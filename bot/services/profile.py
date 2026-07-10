"""Сервис скачивания фото профиля (аватарки) Instagram.
Основной путь: users/search + users/{pk}/info — отдаёт HD-аватарку.
Fallback: web_profile_info (тот же что у Stories, но чаще ловит 429).
"""
import logging
import os
import uuid

import aiohttp

from bot.services.session_pool import (
    SessionExpiredError,
    check_flagged,
    get_sessionid,
    has_any_session,
    with_rotation,
)
from bot.services.stories import (
    INSTAGRAM_HEADERS,
    create_session,
    fetch_profile_info,
)

logger = logging.getLogger(__name__)


async def _fetch_user_pk(session: aiohttp.ClientSession, username: str) -> str:
    """Ищет юзера по username через private API search, возвращает pk"""
    url = f"https://i.instagram.com/api/v1/users/search?q={username}"
    sid = get_sessionid()
    cookies = {"sessionid": sid}

    async with session.get(
        url, headers=INSTAGRAM_HEADERS, cookies=cookies,
        timeout=aiohttp.ClientTimeout(total=10),
    ) as resp:
        if resp.status != 200:
            check_flagged(sid, resp.status, await resp.text())
            raise RuntimeError(f"Поиск юзера не сработал: HTTP {resp.status}")
        data = await resp.json()

    # ищем точное совпадение username в результатах
    for user in data.get("users", []):
        if user.get("username", "").lower() == username.lower():
            return str(user["pk"])

    raise RuntimeError(f"Пользователь @{username} не найден")


async def _fetch_hd_avatar_url(session: aiohttp.ClientSession, pk: str) -> str:
    """Получает URL HD-аватарки через users/{pk}/info"""
    url = f"https://i.instagram.com/api/v1/users/{pk}/info/"
    sid = get_sessionid()
    cookies = {"sessionid": sid}

    async with session.get(
        url, headers=INSTAGRAM_HEADERS, cookies=cookies,
        # этот endpoint бывает медленным — таймаут больше
        timeout=aiohttp.ClientTimeout(total=25),
    ) as resp:
        if resp.status != 200:
            check_flagged(sid, resp.status, await resp.text())
            raise RuntimeError(f"Не удалось получить инфо юзера: HTTP {resp.status}")
        data = await resp.json()

    user = data.get("user", {})
    pic_url = (
        user.get("hd_profile_pic_url_info", {}).get("url")
        or user.get("profile_pic_url")
    )
    if not pic_url:
        raise RuntimeError("У профиля нет фото")
    return pic_url


async def _get_avatar_url(session: aiohttp.ClientSession, username: str) -> str:
    """Достаёт URL аватарки: сначала search+info, потом web_profile_info"""
    try:
        pk = await _fetch_user_pk(session, username)
        return await _fetch_hd_avatar_url(session, pk)
    except SessionExpiredError:
        raise  # сессия протухла — fallback не поможет
    except Exception as e:
        logger.warning(f"search+info не сработал для @{username}, пробуем web_profile_info: {e}")

    # fallback — web_profile_info (со своим ретраем на 429)
    user = await fetch_profile_info(session, username)
    pic_url = user.get("profile_pic_url_hd") or user.get("profile_pic_url")
    if not pic_url:
        raise RuntimeError(f"У профиля @{username} нет фото")
    return pic_url


async def get_avatar_url(username: str) -> str:
    """Возвращает прямую ссылку на HD-аватарку БЕЗ скачивания (для inline-режима)"""
    if not has_any_session():
        raise RuntimeError(
            "Для скачивания фото профиля нужна авторизация.\n"
            "Добавь INSTAGRAM_SESSION_ID в .env"
        )

    async def _impl():
        async with create_session() as session:
            return await _get_avatar_url(session, username)

    return await with_rotation(_impl)


async def download_profile_photo(username: str, download_dir: str) -> dict:
    """Скачивает HD-аватарку профиля.
    Возвращает {file_path, media_type, title} — как download_story.
    """
    if not has_any_session():
        raise RuntimeError(
            "Для скачивания фото профиля нужна авторизация.\n"
            "Добавь INSTAGRAM_SESSION_ID в .env"
        )
    return await with_rotation(lambda: _download_profile_photo_impl(username, download_dir))


async def _download_profile_photo_impl(username: str, download_dir: str) -> dict:
    async with create_session() as session:
        pic_url = await _get_avatar_url(session, username)

        # уникальный суффикс — чтобы параллельные запросы не затирали файлы друг друга
        uid = uuid.uuid4().hex[:8]
        file_path = os.path.join(download_dir, f"avatar_{username}_{uid}.jpg")

        async with session.get(
            pic_url, timeout=aiohttp.ClientTimeout(total=30)
        ) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Не удалось скачать аватарку: HTTP {resp.status}")
            content = await resp.read()

            with open(file_path, "wb") as f:
                f.write(content)

    size_kb = len(content) / 1024
    logger.info(f"Аватарка скачана: {file_path} ({size_kb:.0f} КБ)")

    return {
        "file_path": file_path,
        "media_type": "photo",
        "title": f"@{username}",
    }
