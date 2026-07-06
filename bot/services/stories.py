"""Сервис скачивания Instagram Stories — через private API + sessionid"""
import asyncio
import logging
import os
import re

import aiohttp
from aiohttp_socks import ProxyConnector

from bot.config import settings

logger = logging.getLogger(__name__)


class SessionExpiredError(RuntimeError):
    """INSTAGRAM_SESSION_ID устарела или невалидна — нужно обновить"""

# Instagram private API — мобильные заголовки
INSTAGRAM_HEADERS = {
    "User-Agent": "Instagram 275.0.0.27.98 Android (33/13; 420dpi; 1080x2400; samsung; SM-G991B; o1s; exynos2100)",
    "X-IG-App-ID": "936619743392459",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
}


def parse_story_url(url: str) -> tuple[str, str]:
    """Извлекает username и story_id из URL истории
    URL формат: https://www.instagram.com/stories/username/story_id/
    """
    match = re.search(r"stories/([^/]+)/(\d+)", url)
    if not match:
        raise ValueError(f"Не удалось распарсить URL истории: {url}")
    return match.group(1), match.group(2)


def is_story_url(url: str) -> bool:
    """Проверяет, является ли URL ссылкой на историю"""
    return bool(re.search(r"instagram\.com/stories/[^/]+/\d+", url))


# кэш user_id чтобы не запрашивать повторно
_user_id_cache: dict[str, str] = {}


def create_session() -> aiohttp.ClientSession:
    """Создаёт ClientSession с поддержкой прокси (HTTP/HTTPS/SOCKS4/SOCKS5).
    Прокси берётся из settings.instagram_proxy. ProxyConnector работает с любым
    протоколом, включая user:pass в URL — парсить вручную не нужно.
    """
    proxy_url = settings.instagram_proxy or None
    if not proxy_url:
        return aiohttp.ClientSession()
    connector = ProxyConnector.from_url(proxy_url)
    return aiohttp.ClientSession(connector=connector)


def _proxy_kind() -> str:
    """Возвращает тип прокси для логов: socks5, http или нет"""
    proxy_url = settings.instagram_proxy or None
    if not proxy_url:
        return "нет"
    if proxy_url.startswith("socks"):
        return proxy_url.split("://")[0]
    return "http"


async def _fetch_profile_once(
    session: aiohttp.ClientSession, username: str, cookies: dict
) -> tuple[int, dict | None]:
    """Один запрос профиля. Возвращает (http_status, json или None)"""
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
    async with session.get(
        url, headers=INSTAGRAM_HEADERS, cookies=cookies,
        timeout=aiohttp.ClientTimeout(total=10),
    ) as resp:
        if resp.status != 200:
            return resp.status, None
        return 200, await resp.json()


async def fetch_profile_info(session: aiohttp.ClientSession, username: str) -> dict:
    """Получает данные профиля через private API (с ретраем при 429).
    Возвращает dict юзера: id, profile_pic_url_hd, is_private и т.д.
    """
    cookies = {"sessionid": settings.instagram_session_id}

    # ретрай при 429
    for attempt in range(3):
        status, data = await _fetch_profile_once(session, username, cookies)

        # 429 с sessionid — лимит висит на аккаунте, пробуем анонимно.
        # Анонимный ответ берём только если 200, иначе ошибки не искажаем
        if status == 429:
            anon_status, anon_data = await _fetch_profile_once(session, username, {})
            if anon_status == 200:
                logger.info(f"429 с sessionid, анонимный запрос прошёл (@{username})")
                status, data = 200, anon_data

        if status == 429:
            delay = 5 * (attempt + 1)
            logger.warning(f"429 от Instagram, ждём {delay}с (попытка {attempt + 1}/3)")
            await asyncio.sleep(delay)
            continue
        if status in (401, 403):
            raise SessionExpiredError(
                f"INSTAGRAM_SESSION_ID устарела или заблокирована (HTTP {status})"
            )
        if status != 200:
            raise RuntimeError(f"Не удалось получить профиль @{username}: HTTP {status}")
        break
    else:
        raise RuntimeError("Instagram блокирует запросы (429)")

    user = data.get("data", {}).get("user")
    if not user or not user.get("id"):
        raise RuntimeError(f"Пользователь @{username} не найден")

    return user


async def get_user_id(session: aiohttp.ClientSession, username: str) -> str:
    """Получает user_id по username (с кэшем в памяти)"""
    if username in _user_id_cache:
        logger.info(f"@{username} → user_id={_user_id_cache[username]} (кэш)")
        return _user_id_cache[username]

    user = await fetch_profile_info(session, username)
    user_id = user["id"]

    _user_id_cache[username] = user_id
    logger.info(f"@{username} → user_id={user_id}")
    return user_id


async def get_story_media(
    session: aiohttp.ClientSession, user_id: str, story_id: str
) -> dict:
    """Получает медиа конкретной истории"""
    url = f"https://i.instagram.com/api/v1/feed/reels_media/?reel_ids={user_id}"
    cookies = {"sessionid": settings.instagram_session_id}

    async with session.get(
        url, headers=INSTAGRAM_HEADERS, cookies=cookies,
        timeout=aiohttp.ClientTimeout(total=10),
    ) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Не удалось получить истории: HTTP {resp.status}")
        data = await resp.json()

    reels = data.get("reels", {})
    reel = reels.get(user_id, {})
    items = reel.get("items", [])

    if not items:
        raise RuntimeError("Истории не найдены или уже истекли (24 часа)")

    # ищем конкретную историю по story_id
    for item in items:
        if str(item.get("pk")) == story_id or str(item.get("id", "")).startswith(story_id):
            return item

    # фоллбэк — последняя история
    logger.warning(f"Story {story_id} не найден, отправляем последнюю")
    return items[-1]


async def download_story(url: str, download_dir: str) -> dict:
    """Скачивает историю и возвращает {file_path, media_type, title}"""
    if not settings.instagram_session_id:
        raise RuntimeError(
            "Для скачивания Stories нужна авторизация.\n"
            "Добавь INSTAGRAM_SESSION_ID в .env"
        )

    username, story_id = parse_story_url(url)
    logger.info(f"Stories: user=@{username}, proxy={_proxy_kind()}")

    async with create_session() as session:
        # получаем user_id
        user_id = await get_user_id(session, username)

        # получаем медиа истории
        item = await get_story_media(session, user_id, story_id)

        # определяем тип и URL медиа
        media_type = "video" if item.get("video_versions") else "photo"

        if media_type == "video":
            versions = item["video_versions"]
            media_url = versions[0]["url"]
            ext = ".mp4"
        else:
            candidates = item.get("image_versions2", {}).get("candidates", [])
            if not candidates:
                raise RuntimeError("Не удалось найти фото в истории")
            media_url = candidates[0]["url"]
            ext = ".jpg"

        # скачиваем файл
        file_path = os.path.join(download_dir, f"story_{username}_{story_id}{ext}")

        async with session.get(
            media_url, timeout=aiohttp.ClientTimeout(total=30)
        ) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Не удалось скачать медиа: HTTP {resp.status}")
            content = await resp.read()

            if len(content) > 2000 * 1024 * 1024:
                raise RuntimeError("Файл больше 2 ГБ) — лимит локального Telegram API")

            with open(file_path, "wb") as f:
                f.write(content)

        size_mb = len(content) / (1024 * 1024)
        logger.info(f"Story скачана: {file_path} ({size_mb:.1f} МБ, {media_type})")

        return {
            "file_path": file_path,
            "media_type": media_type,
            "title": f"Story @{username}",
        }
