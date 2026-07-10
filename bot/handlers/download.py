"""Хэндлер скачивания — обрабатывает ссылки Instagram"""
import logging
import os
import re
import time

from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
)

from bot.database import async_session
from bot.database.crud import (
    get_cached_download,
    get_or_create_user,
    get_user_language,
    save_download,
)
from bot.emojis import E
from bot.i18n import t
from bot.keyboards.inline import get_back_keyboard
from bot.services.instagram import DownloadResult, downloader
from bot.services.posts import download_post, is_post_url
from bot.services.profile import download_profile_photo
from bot.services.stories import SessionExpiredError, download_story, is_story_url
from bot.utils.helpers import (
    clean_instagram_url,
    extract_profile_username,
    is_instagram_url,
    is_profile_url,
)
from bot.utils.notify_admin import notify_admins
from bot.utils.video_meta import get_video_meta

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text)
async def handle_instagram_link(message: Message) -> None:
    """Обработка текстовых сообщений — ищем ссылки Instagram"""
    text = message.text.strip()

    # получаем язык юзера
    async with async_session() as session:
        lang = await get_user_language(session, message.from_user.id)

    # ссылка на пост/Reels/Story — скачиваем медиа
    if is_instagram_url(text):
        await _process_download(message, text, lang)
        return

    # ссылка на профиль — скачиваем аватарку
    if is_profile_url(text):
        await _process_profile(message, text, lang)
        return

    await message.answer(
        t("download.not_instagram", lang),
        parse_mode="HTML",
    )


async def _process_download(
    message: Message, raw_url: str, lang: str = "ru"
) -> None:
    """Скачивает и отправляет медиа — вызывается из хэндлера и после подписки"""
    clean_url = clean_instagram_url(raw_url)

    # обновляем юзера в БД + проверяем кэш
    async with async_session() as session:
        user = await get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )
        cached = await get_cached_download(session, clean_url)

    if cached:
        logger.info(f"Кэш найден для {clean_url}, отправляем file_id")
        await _send_cached(message, cached.file_id, cached.media_type, clean_url, lang)
        return

    # кэша нет — скачиваем
    status_msg = await message.answer(t("download.processing", lang))

    results: list[DownloadResult] = []
    try:
        # сначала пробуем через Cobalt (работает для всех типов)
        try:
            results = await downloader.download(clean_url)
        except Exception as cobalt_err:
            # Cobalt не смог — пробуем private API
            if is_story_url(clean_url):
                logger.warning(f"Cobalt не смог скачать Story, пробуем private API: {cobalt_err}")
                story_data = await download_story(clean_url, downloader.download_dir)
                results = [DownloadResult(
                    file_path=story_data["file_path"],
                    media_type=story_data["media_type"],
                    title=story_data["title"],
                )]
            elif is_post_url(clean_url):
                logger.warning(f"Cobalt не смог скачать пост, пробуем private API: {cobalt_err}")
                post_items = await download_post(clean_url, downloader.download_dir)
                results = [DownloadResult(
                    file_path=item["file_path"],
                    media_type=item["media_type"],
                    title=item["title"],
                ) for item in post_items]
            else:
                raise

        # проверяем размер каждого файла
        for r in results:
            file_size = os.path.getsize(r.file_path)
            if file_size > 2000 * 1024 * 1024:
                await status_msg.edit_text(t("error.too_large", lang))
                return

        if len(results) == 1:
            # одиночный файл — отправляем как раньше + кэшируем
            file_id = await _send_media(message, results[0], lang)
            if file_id:
                async with async_session() as session:
                    await save_download(
                        session=session,
                        instagram_url=clean_url,
                        file_id=file_id,
                        media_type=results[0].media_type,
                    )
                await _bump_download_count(message)
        else:
            # карусель — отправляем альбомом
            await _send_media_group(message, results, lang)
            await _bump_download_count(message)

        await status_msg.delete()

    except SessionExpiredError as e:
        # Все аккаунты выгорели — сообщаем юзеру и уведомляем админов
        logger.error(f"Сессия Instagram недоступна: {e}")
        await status_msg.edit_text(t("error.session_flagged", lang))
        await _alert_session_dead(message.bot)

    except Exception as e:
        logger.error(f"Ошибка скачивания {clean_url}: {e}")
        error_text = _get_error_text(str(e), lang)
        await status_msg.edit_text(error_text)

    finally:
        if results:
            downloader.cleanup(results)


async def _process_profile(
    message: Message, raw_url: str, lang: str = "ru"
) -> None:
    """Скачивает и отправляет HD-аватарку профиля"""
    username = extract_profile_username(raw_url)

    status_msg = await message.answer(t("download.processing", lang))

    results: list[DownloadResult] = []
    try:
        avatar = await download_profile_photo(username, downloader.download_dir)
        results = [DownloadResult(
            file_path=avatar["file_path"],
            media_type=avatar["media_type"],
            title=avatar["title"],
        )]

        await message.answer_photo(
            photo=FSInputFile(avatar["file_path"]),
            caption=t("download.profile_photo", lang, username=username) + _promo(lang),
        )
        await status_msg.delete()
        await _bump_download_count(message)

    except SessionExpiredError as e:
        logger.error(f"Сессия Instagram недоступна: {e}")
        await status_msg.edit_text(t("error.session_flagged", lang))
        await _alert_session_dead(message.bot)

    except Exception as e:
        logger.error(f"Ошибка скачивания аватарки @{username}: {e}")
        await status_msg.edit_text(t("error.profile_failed", lang, username=username))

    finally:
        if results:
            downloader.cleanup(results)


# троттлинг алерта админам — чтобы при потоке запросов не спамило
_last_session_alert = 0.0
_SESSION_ALERT_COOLDOWN = 30 * 60  # 30 мин


async def _alert_session_dead(bot) -> None:
    """Уведомляет админов что все Instagram-аккаунты выгорели (не чаще раза в 30 мин)"""
    global _last_session_alert
    now = time.monotonic()
    if now - _last_session_alert < _SESSION_ALERT_COOLDOWN:
        return
    _last_session_alert = now

    await notify_admins(
        bot,
        f"{E['warning']} <b>Instagram-аккаунты заблокированы!</b>\n\n"
        "Все INSTAGRAM_SESSION_ID под ограничением (challenge/feedback). "
        "Не работают: посты (fallback), Stories, аватарки, inline-режим.\n\n"
        "Действие: зайди в аккаунт(ы) через браузер, пройди проверку «это вы», "
        "обнови INSTAGRAM_SESSION_ID в .env и перезапусти "
        "(<code>docker compose restart bot</code>)",
    )


async def _bump_download_count(message: Message) -> None:
    """Увеличивает счётчик скачиваний юзера на 1"""
    async with async_session() as session:
        user_obj = await get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )
        user_obj.download_count += 1
        await session.commit()


def _promo(lang: str) -> str:
    """Рекламная подпись под каждым медиа — чтобы получатель узнал про бота"""
    from bot.config import settings
    return t("download.promo", lang, bot_username=settings.bot_username)


async def _send_media(message: Message, result: DownloadResult, lang: str) -> str | None:
    """Отправляет медиа юзеру и возвращает file_id"""
    file = FSInputFile(result.file_path)

    if result.media_type == "video":
        icon = E["video"] if "Story" in result.title else E["video"]
        meta = await get_video_meta(result.file_path)
        sent = await message.answer_video(
            video=file,
            caption=f"{icon} {result.title}{_promo(lang)}",
            width=meta.get("width"),
            height=meta.get("height"),
            duration=meta.get("duration"),
        )
        return sent.video.file_id

    elif result.media_type == "photo":
        sent = await message.answer_photo(
            photo=file,
            caption=f"{E['camera']} {result.title}{_promo(lang)}",
        )
        return sent.photo[-1].file_id

    return None


async def _send_media_group(
    message: Message, results: list[DownloadResult], lang: str
) -> None:
    """Отправляет карусель альбомом через media_group (макс 10 элементов на альбом)"""
    media = []
    for i, r in enumerate(results):
        file = FSInputFile(r.file_path)
        # caption только на первом элементе, добавляем рекламу
        caption = f"{E['camera']} Instagram Карусель ({len(results)} фото/видео){_promo(lang)}" if i == 0 else None
        if r.media_type == "video":
            meta = await get_video_meta(r.file_path)
            media.append(InputMediaVideo(
                media=file, caption=caption,
                width=meta.get("width"), height=meta.get("height"),
                duration=meta.get("duration"),
            ))
        else:
            media.append(InputMediaPhoto(media=file, caption=caption))

    # Telegram разрешает максимум 10 элементов в одном альбоме
    for chunk_start in range(0, len(media), 10):
        chunk = media[chunk_start:chunk_start + 10]
        await message.answer_media_group(media=chunk)

    logger.info(f"Карусель отправлена: {len(results)} элементов")


async def _send_cached(
    message: Message, file_id: str, media_type: str, url: str, lang: str
) -> None:
    """Отправляет из кэша по file_id с тем же caption"""
    caption = _make_caption(media_type, url, lang)
    try:
        if media_type == "video":
            await message.answer_video(video=file_id, caption=caption)
        elif media_type == "photo":
            await message.answer_photo(photo=file_id, caption=caption)
    except Exception as e:
        logger.error(f"Ошибка отправки из кэша: {e}")
        await message.answer(f"{E['warning']} Кэш устарел. Отправь ссылку ещё раз.")


def _make_caption(media_type: str, url: str, lang: str) -> str:
    """Генерит caption по типу медиа и URL (для кэшированных медиа)"""
    promo = _promo(lang)
    if is_story_url(url):
        match = re.search(r"stories/([^/]+)", url)
        username = match.group(1) if match else "unknown"
        icon = E["video"] if media_type == "video" else E["camera"]
        return f"{icon} Story @{username}{promo}"
    elif media_type == "photo":
        return f"{E['camera']} Instagram Фото{promo}"
    else:
        return f"{E['video']} Instagram Reels{promo}"


def _get_error_text(error: str, lang: str = "ru") -> str:
    """Человеко-понятное сообщение об ошибке"""
    error_lower = error.lower()

    if "session" in error_lower and "авторизация" in error_lower:
        return t("error.session", lang)
    elif "истории не найдены" in error_lower or "истекли" in error_lower:
        return t("error.story_expired", lang)
    elif "private" in error_lower or "login" in error_lower:
        return t("error.private", lang)
    elif "not found" in error_lower or "404" in error_lower:
        return t("error.not_found", lang)
    elif "unsupported" in error_lower:
        return t("error.unsupported", lang)
    elif "too large" in error_lower or "2 гб" in error_lower:
        return t("error.too_large", lang)
    elif "timeout" in error_lower:
        return t("error.timeout", lang)
    else:
        return t("error.generic", lang)
