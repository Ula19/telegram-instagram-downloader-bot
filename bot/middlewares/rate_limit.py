"""Rate limiting — ограничение частоты запросов на скачивание
Лимит: 5 запросов в минуту на юзера (настраиваемо через RATE_LIMIT_*)
Хранение в памяти — без Redis/БД, сбрасывается при перезапуске
"""
import time
import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from bot.i18n import detect_language, t

logger = logging.getLogger(__name__)

# лимит — сколько скачиваний в минуту
MAX_REQUESTS = 5
WINDOW_SECONDS = 60

# {user_id: [timestamp1, timestamp2, ...]}
_user_requests: dict[int, list[float]] = {}


def hit_rate_limit(user_id: int) -> int | None:
    """Регистрирует запрос юзера. Если лимит превышен — возвращает
    сколько секунд подождать, иначе None (запрос засчитан).
    Используется и мидлварью, и inline-режимом.
    """
    now = time.time()

    # чистим старые записи
    requests = [
        ts for ts in _user_requests.get(user_id, [])
        if now - ts < WINDOW_SECONDS
    ]

    if len(requests) >= MAX_REQUESTS:
        _user_requests[user_id] = requests
        oldest = requests[0]
        return int(WINDOW_SECONDS - (now - oldest)) + 1

    requests.append(now)
    _user_requests[user_id] = requests
    return None


class RateLimitMiddleware(BaseMiddleware):
    """Ограничивает частоту скачиваний — только для текстовых сообщений"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # ограничиваем только текстовые сообщения (ссылки)
        if not isinstance(event, Message) or not event.text:
            return await handler(event, data)

        # проверяем что текст похож на ссылку Instagram (пост или профиль)
        from bot.utils.helpers import is_instagram_url, is_profile_url
        text = event.text.strip()
        if not (is_instagram_url(text) or is_profile_url(text)):
            return await handler(event, data)

        wait_sec = hit_rate_limit(event.from_user.id)
        if wait_sec is not None:
            lang = detect_language(event.from_user.language_code)
            await event.answer(
                t("error.rate_limit", lang, seconds=wait_sec),
            )
            logger.info(f"Rate limit для {event.from_user.id}: подождать {wait_sec} сек")
            return None  # блокируем

        return await handler(event, data)
