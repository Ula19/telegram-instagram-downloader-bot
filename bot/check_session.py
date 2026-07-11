"""Проверка Instagram sessionid ЧЕРЕЗ ТОТ ЖЕ прокси, что использует бот.

Важно: запускать на сервере (в контейнере бота), чтобы запрос шёл через
INSTAGRAM_PROXY — sessionid, живой с твоего IP, может давать 403 из-под
серверного прокси из-за скачка гео. Проверяем ровно тот путь, что у бота.

Запуск:
    docker compose exec bot python -m bot.check_session          # все из .env
    docker compose exec bot python -m bot.check_session СЕССИЯ    # конкретную
    docker compose exec bot python -m bot.check_session S1 S2 S3  # несколько
"""
import asyncio
import sys

import aiohttp

from bot.config import settings
from bot.services.session_pool import response_flag
from bot.services.stories import INSTAGRAM_HEADERS, create_session

# auth-gated endpoint, который бот реально использует (работает по HTTP/1.1,
# как aiohttp): валидная сессия → 200, битая/challenge → 403/400 с маркером.
# current_user не годится — отвечает только по HTTP/2, aiohttp на нём виснет.
_CHECK_URL = "https://i.instagram.com/api/v1/users/search?q=instagram"


def _mask(sid: str) -> str:
    """Прячет sessionid в выводе — светить его целиком не нужно"""
    return f"{sid[:6]}…{sid[-4:]}" if len(sid) > 12 else "???"


async def check_one(sid: str) -> tuple[bool, str]:
    """Проверяет один sessionid через прокси. Возвращает (жив, сообщение)"""
    try:
        async with create_session() as session:
            async with session.get(
                _CHECK_URL,
                headers=INSTAGRAM_HEADERS,
                cookies={"sessionid": sid},
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                body = await resp.text()
                if resp.status == 200:
                    return True, "валидна"
                flag = response_flag(resp.status, body)
                reason = f"HTTP {resp.status}"
                if flag and flag != f"HTTP {resp.status}":
                    reason += f" / {flag}"
                return False, reason
    except Exception as e:
        return False, f"ошибка сети/прокси: {type(e).__name__}: {e}"


async def main() -> None:
    proxy = settings.instagram_proxy or "НЕТ (прямое подключение)"
    print(f"Прокси: {proxy}\n")

    sids = sys.argv[1:] or [
        s.strip() for s in (settings.instagram_session_id or "").split(",") if s.strip()
    ]
    if not sids:
        print("Нет sessionid: передай аргументом или заполни INSTAGRAM_SESSION_ID в .env")
        return

    alive = 0
    for i, sid in enumerate(sids, 1):
        ok, msg = await check_one(sid)
        alive += ok
        print(f"#{i} {_mask(sid)} → {'✅' if ok else '❌'} {msg}")

    print(f"\nЖивых: {alive} из {len(sids)}")


if __name__ == "__main__":
    asyncio.run(main())
