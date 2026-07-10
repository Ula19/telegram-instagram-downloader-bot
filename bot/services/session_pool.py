"""Пул Instagram-сессий: ротация аккаунтов + кулдаун.

INSTAGRAM_SESSION_ID может содержать несколько sessionid через запятую.
Активный аккаунт используется, пока не словит challenge/feedback/401/403 —
тогда он уходит в кулдаун, а пул переключается на следующий живой.
Один sessionid без запятых работает как раньше.
"""
import asyncio
import logging
import time
from typing import Awaitable, Callable, TypeVar

from bot.config import settings

logger = logging.getLogger(__name__)

# на сколько аккаунт уходит в кулдаун после флага
_COOLDOWN_SECONDS = 60 * 60  # 1 час

# маркеры в теле ответа Instagram — аккаунт под ограничением
_FLAGGED_MARKERS = ("challenge_required", "feedback_required", "login_required")

T = TypeVar("T")


class SessionExpiredError(RuntimeError):
    """Активный sessionid устарел/заблокирован — уведён в кулдаун"""


class AllSessionsExpiredError(SessionExpiredError):
    """Все sessionid выгорели (в кулдауне) — нужно обновить аккаунты"""


# {sessionid: timestamp когда кулдаун закончится}
_cooldown: dict[str, float] = {}


def _accounts() -> list[str]:
    """Парсит sessionid из настроек (через запятую), убирая дубликаты"""
    raw = settings.instagram_session_id or ""
    # dict.fromkeys сохраняет порядок и выкидывает повторы
    return list(dict.fromkeys(s.strip() for s in raw.split(",") if s.strip()))


def has_any_session() -> bool:
    """Есть ли вообще хоть один sessionid в конфиге"""
    return bool(_accounts())


def _alive_accounts() -> list[str]:
    """Аккаунты не в кулдауне"""
    now = time.time()
    return [sid for sid in _accounts() if _cooldown.get(sid, 0) <= now]


def get_sessionid() -> str:
    """Возвращает активный (не в кулдауне) sessionid.
    Бросает AllSessionsExpiredError если все выгорели или ни один не задан.
    """
    if not _accounts():
        raise AllSessionsExpiredError("INSTAGRAM_SESSION_ID не задан")

    alive = _alive_accounts()
    if not alive:
        raise AllSessionsExpiredError("Все Instagram-аккаунты в кулдауне")

    # sticky: всегда первый живой, чтобы не размазывать нагрузку по всем сразу
    return alive[0]


def report_bad(sessionid: str, reason: str) -> None:
    """Помечает аккаунт как выгоревший — уводит в кулдаун"""
    _cooldown[sessionid] = time.time() + _COOLDOWN_SECONDS
    accounts = _accounts()
    num = accounts.index(sessionid) + 1 if sessionid in accounts else "?"
    logger.warning(
        f"Аккаунт #{num} в кулдаун на {_COOLDOWN_SECONDS // 60} мин: {reason}. "
        f"Живых аккаунтов осталось: {len(_alive_accounts())}"
    )


def response_flag(status: int, body: str) -> str | None:
    """Если ответ говорит, что аккаунт под ограничением — возвращает причину, иначе None.
    Вызывать на НЕуспешных ответах (status != 200).
    """
    if status in (401, 403):
        return f"HTTP {status}"
    for marker in _FLAGGED_MARKERS:
        if marker in body:
            return marker
    return None


def check_flagged(sessionid: str, status: int, body: str) -> None:
    """На НЕуспешном ответе: если аккаунт под ограничением — уводит его в кулдаун
    и бросает SessionExpiredError. Иначе логирует тело (чтобы заметить новые
    формы бана) и возвращает управление — вызывающий бросит свою ошибку.
    """
    flag = response_flag(status, body)
    if flag:
        report_bad(sessionid, flag)
        raise SessionExpiredError(f"INSTAGRAM_SESSION_ID заблокирована ({flag})")
    logger.warning("Instagram HTTP %s без маркера бана: %s", status, body[:200])


# сериализует запросы к private API: один аккаунт на всех — параллельный
# долбёж выглядит для Instagram как бот и ускоряет бан. К тому же не даёт
# наплыву запросов пройти по уже выгорающему аккаунту до выставления кулдауна.
_rotation_lock = asyncio.Lock()


async def with_rotation(op: Callable[[], Awaitable[T]]) -> T:
    """Выполняет операцию, при выгорании активного аккаунта переключается на
    следующий и повторяет. op — функция без аргументов, читающая sessionid
    через get_sessionid() внутри (report_bad вызывается на месте детекта).
    Запросы сериализованы — одновременно идёт только одна операция.
    """
    attempts = max(1, len(_accounts()))
    last_err: SessionExpiredError | None = None

    async with _rotation_lock:
        for _ in range(attempts):
            try:
                return await op()
            except AllSessionsExpiredError:
                raise  # живых аккаунтов нет — повторять нечем
            except SessionExpiredError as e:
                last_err = e
                # аккаунт уже уведён в кулдаун внутри op; пробуем следующий
                if not _alive_accounts():
                    break

    # попытки исчерпаны — все аккаунты выгорели
    raise last_err or AllSessionsExpiredError("Все Instagram-аккаунты выгорели")
