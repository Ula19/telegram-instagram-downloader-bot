"""Сервис скачивания постов Instagram через private API + sessionid.
Fallback на случай когда Cobalt не смог (error.api.fetch.empty и т.д.).
Поддерживает: фото, видео, карусели.
"""
import asyncio
import logging
import os
import re
import uuid

import aiohttp

from bot.config import settings
from bot.services.stories import (
    INSTAGRAM_HEADERS,
    SessionExpiredError,
    create_session,
    pick_inline_video_url,
)

logger = logging.getLogger(__name__)

# алфавит shortcode Instagram (base64url)
_SHORTCODE_ALPHABET = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
)


def is_post_url(url: str) -> bool:
    """Проверяет, является ли URL ссылкой на пост/Reels"""
    return bool(re.search(r"instagram\.com/(p|reel|reels|tv)/[\w\-]+", url))


def parse_post_shortcode(url: str) -> str:
    """Извлекает shortcode из URL поста
    URL формат: https://www.instagram.com/p/DaUZM67CK8c/
    """
    match = re.search(r"instagram\.com/(?:p|reel|reels|tv)/([\w\-]+)", url)
    if not match:
        raise ValueError(f"Не удалось распарсить URL поста: {url}")
    return match.group(1)


def shortcode_to_media_pk(shortcode: str) -> int:
    """Конвертирует shortcode в media_pk (число для private API)"""
    pk = 0
    for ch in shortcode:
        pk = pk * 64 + _SHORTCODE_ALPHABET.index(ch)
    return pk


async def get_media_info(session: aiohttp.ClientSession, media_pk: int) -> dict:
    """Получает инфо о посте через private API (с ретраем при 429)"""
    url = f"https://i.instagram.com/api/v1/media/{media_pk}/info/"
    cookies = {"sessionid": settings.instagram_session_id}

    # ретрай при 429
    for attempt in range(3):
        async with session.get(
            url, headers=INSTAGRAM_HEADERS, cookies=cookies,
            timeout=aiohttp.ClientTimeout(total=10),
        ) as resp:
            if resp.status == 429:
                delay = 5 * (attempt + 1)
                logger.warning(f"429 от Instagram, ждём {delay}с (попытка {attempt + 1}/3)")
                await asyncio.sleep(delay)
                continue
            if resp.status in (401, 403):
                raise SessionExpiredError(
                    f"INSTAGRAM_SESSION_ID устарела или заблокирована (HTTP {resp.status})"
                )
            if resp.status == 404:
                raise RuntimeError("Пост не найден (404) — удалён или ссылка неправильная")
            if resp.status != 200:
                raise RuntimeError(f"Не удалось получить пост: HTTP {resp.status}")
            data = await resp.json()
            break
    else:
        raise RuntimeError("Instagram блокирует запросы (429)")

    items = data.get("items", [])
    if not items:
        raise RuntimeError("Пост не найден — Instagram вернул пустой ответ")

    return items[0]


def _pick_media_url(item: dict) -> tuple[str, str]:
    """Достаёт из элемента поста URL медиа и тип: (url, media_type)"""
    if item.get("video_versions"):
        return item["video_versions"][0]["url"], "video"

    candidates = item.get("image_versions2", {}).get("candidates", [])
    if not candidates:
        raise RuntimeError("Не удалось найти медиа в посте")
    return candidates[0]["url"], "photo"


async def _download_file(
    session: aiohttp.ClientSession, media_url: str, file_path: str
) -> None:
    """Скачивает файл по URL на диск"""
    async with session.get(
        media_url, timeout=aiohttp.ClientTimeout(total=60)
    ) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Не удалось скачать медиа: HTTP {resp.status}")
        content = await resp.read()

        if len(content) > 2000 * 1024 * 1024:
            raise RuntimeError("Файл больше 2 ГБ — лимит локального Telegram API")

        with open(file_path, "wb") as f:
            f.write(content)

    size_mb = len(content) / (1024 * 1024)
    logger.info(f"Скачано: {file_path} ({size_mb:.1f} МБ)")


async def get_post_media_urls(url: str) -> list[dict]:
    """Возвращает прямые CDN-ссылки медиа поста БЕЗ скачивания (для inline-режима).
    Каждый элемент: {url, media_type, thumb}
    """
    if not settings.instagram_session_id:
        raise RuntimeError(
            "Для inline-режима нужна авторизация.\n"
            "Добавь INSTAGRAM_SESSION_ID в .env"
        )

    shortcode = parse_post_shortcode(url)
    media_pk = shortcode_to_media_pk(shortcode)

    async with create_session() as session:
        post = await get_media_info(session, media_pk)
        medias = post.get("carousel_media") or [post]

        results = []
        for item in medias:
            # превью всегда есть в image_versions2 (у видео это обложка)
            candidates = item.get("image_versions2", {}).get("candidates", [])
            thumb = candidates[-1]["url"] if candidates else None

            if item.get("video_versions"):
                media_url = await pick_inline_video_url(session, item)
                media_type = "video"
            else:
                if not candidates:
                    continue  # нет ни видео, ни фото — пропускаем элемент
                media_url = candidates[0]["url"]
                media_type = "photo"

            results.append({
                "url": media_url,
                "media_type": media_type,
                "thumb": thumb,
            })

    if not results:
        raise RuntimeError("Не удалось найти медиа в посте")

    return results


async def download_post(url: str, download_dir: str) -> list[dict]:
    """Скачивает пост (фото/видео/карусель) через private API.
    Возвращает список {file_path, media_type, title} — как download_story.
    """
    if not settings.instagram_session_id:
        raise RuntimeError(
            "Для скачивания через private API нужна авторизация.\n"
            "Добавь INSTAGRAM_SESSION_ID в .env"
        )

    shortcode = parse_post_shortcode(url)
    media_pk = shortcode_to_media_pk(shortcode)
    logger.info(f"Post fallback: shortcode={shortcode}, pk={media_pk}")

    async with create_session() as session:
        post = await get_media_info(session, media_pk)

        # карусель — несколько элементов, иначе один
        medias = post.get("carousel_media") or [post]

        # уникальный суффикс — чтобы параллельные запросы не затирали файлы друг друга
        uid = uuid.uuid4().hex[:8]

        results = []
        try:
            for i, item in enumerate(medias):
                media_url, media_type = _pick_media_url(item)
                ext = ".mp4" if media_type == "video" else ".jpg"
                file_path = os.path.join(
                    download_dir, f"post_{shortcode}_{uid}_{i}{ext}"
                )
                await _download_file(session, media_url, file_path)

                title = "Instagram Reels" if media_type == "video" else "Instagram Фото"
                results.append({
                    "file_path": file_path,
                    "media_type": media_type,
                    "title": title,
                })
        except Exception:
            # не бросаем недокачанную карусель на диске — чистим за собой
            for r in results:
                try:
                    os.remove(r["file_path"])
                except OSError:
                    pass
            raise

        return results
