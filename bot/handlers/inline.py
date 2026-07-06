"""Inline-режим — @бот <ссылка> в любом чате.
Медиа отдаётся без скачивания: по file_id из кэша или по прямой CDN-ссылке
(Telegram сам забирает файл при отправке в чат).
"""
import asyncio
import logging

from aiogram import Router
from aiogram.types import (
    InlineQuery,
    InlineQueryResultCachedPhoto,
    InlineQueryResultCachedVideo,
    InlineQueryResultPhoto,
    InlineQueryResultVideo,
    InlineQueryResultsButton,
)

from bot.config import settings
from bot.database import async_session
from bot.database.crud import get_active_channels, get_cached_download
from bot.handlers.download import _make_caption, _promo
from bot.i18n import detect_language, t
from bot.middlewares.rate_limit import hit_rate_limit
from bot.middlewares.subscription import is_subscribed
from bot.services.posts import get_post_media_urls
from bot.services.profile import get_avatar_url
from bot.services.stories import get_story_media_urls, is_story_url
from bot.utils.helpers import (
    clean_instagram_url,
    extract_profile_username,
    is_instagram_url,
    is_profile_url,
)

logger = logging.getLogger(__name__)
router = Router()

# дебаунс: inline_query прилетает на каждый символ,
# обрабатываем только последний ввод юзера
_DEBOUNCE_SECONDS = 1.0
_last_query_id: dict[int, str] = {}


def _button(text: str, start_parameter: str) -> InlineQueryResultsButton:
    """Кнопка над inline-результатами — ведёт в ЛС бота"""
    return InlineQueryResultsButton(text=text, start_parameter=start_parameter)


async def _answer(
    query: InlineQuery, results: list, cache_time: int = 5, **kwargs
) -> bool:
    """Отвечает на inline-запрос. Возвращает True если Telegram принял ответ"""
    try:
        await query.answer(
            results, cache_time=cache_time, is_personal=True, **kwargs
        )
        return True
    except Exception as e:
        logger.warning(f"Не удалось ответить на inline-запрос: {e}")
        return False


async def _check_subscription(query: InlineQuery) -> bool:
    """Проверяет подписку юзера на обязательные каналы (админы — без проверки)"""
    if query.from_user.id in settings.admin_id_list:
        return True

    async with async_session() as session:
        channels = await get_active_channels(session)

    if not channels:
        return True

    for channel in channels:
        if not await is_subscribed(query.bot, channel.channel_id, query.from_user.id):
            return False
    return True


def _cached_result(cached, url: str, lang: str) -> list:
    """Результат из кэша — по file_id, мгновенно и без лимита 20 МБ"""
    caption = _make_caption(cached.media_type, url, lang)
    if cached.media_type == "video":
        return [InlineQueryResultCachedVideo(
            id="cached",
            video_file_id=cached.file_id,
            title=t("inline.title_video", lang),
            caption=caption,
        )]
    if cached.media_type == "photo":
        return [InlineQueryResultCachedPhoto(
            id="cached",
            photo_file_id=cached.file_id,
            title=t("inline.title_photo", lang),
            caption=caption,
        )]
    return []


def _url_result(i: int, item: dict, caption: str, title: str) -> object | None:
    """Inline-результат по прямой CDN-ссылке"""
    if item["media_type"] == "video":
        # для видео превью обязательно должно быть картинкой
        if not item.get("thumb"):
            return None
        return InlineQueryResultVideo(
            id=f"r{i}",
            video_url=item["url"],
            mime_type="video/mp4",
            thumbnail_url=item["thumb"],
            title=title,
            caption=caption,
        )
    if item["media_type"] == "photo":
        return InlineQueryResultPhoto(
            id=f"r{i}",
            photo_url=item["url"],
            thumbnail_url=item.get("thumb") or item["url"],
            title=title,
            caption=caption,
        )
    return None


@router.inline_query()
async def inline_download(query: InlineQuery) -> None:
    """Обработка @бот <ссылка> — отдаём медиа прямо в чат"""
    text = (query.query or "").strip()
    lang = detect_language(query.from_user.language_code)

    # не ссылка — показываем подсказку (без запросов к БД/API)
    if not (is_instagram_url(text) or is_profile_url(text)):
        await _answer(query, [], button=_button(t("inline.hint", lang), "inline_help"))
        return

    # дебаунс: ждём паузу в наборе, обрабатываем только последний запрос
    user_id = query.from_user.id
    _last_query_id[user_id] = query.id
    await asyncio.sleep(_DEBOUNCE_SECONDS)
    if _last_query_id.get(user_id) != query.id:
        return  # юзер уже ввёл что-то новее — этот запрос устарел

    # rate limit — общий с обычным режимом (после дебаунса, чтобы
    # промежуточный набор символов не съедал лимит)
    if hit_rate_limit(user_id) is not None:
        await _answer(query, [], button=_button(t("inline.rate_limit", lang), "inline_help"))
        return

    # обязательная подписка действует и в inline
    if not await _check_subscription(query):
        await _answer(query, [], button=_button(t("inline.need_sub", lang), "subscribe"))
        return

    clean_url = clean_instagram_url(text)

    try:
        # сначала кэш — мгновенно и без лимита размера
        async with async_session() as session:
            cached = await get_cached_download(session, clean_url)

        if cached:
            results = _cached_result(cached, clean_url, lang)
            if results and await _answer(query, results, cache_time=300):
                return

        # кэша нет — берём прямые CDN-ссылки через private API
        if is_profile_url(text):
            username = extract_profile_username(text)
            items = [{
                "url": await get_avatar_url(username),
                "media_type": "photo",
                "thumb": None,
            }]
            caption = t("download.profile_photo", lang, username=username) + _promo(lang)
        elif is_story_url(clean_url):
            items = [await get_story_media_urls(clean_url)]
            caption = None  # сгенерим по типу ниже
        else:
            items = await get_post_media_urls(clean_url)
            caption = None

        results = []
        for i, item in enumerate(items):
            item_caption = caption or _make_caption(item["media_type"], clean_url, lang)
            title = (
                t("inline.title_video", lang)
                if item["media_type"] == "video"
                else t("inline.title_photo", lang)
            )
            if len(items) > 1:
                title = f"{title} {i + 1}/{len(items)}"
            result = _url_result(i, item, item_caption, title)
            if result:
                results.append(result)

        if not results:
            raise RuntimeError("Нет подходящих медиа для inline")

        if not await _answer(query, results, cache_time=300):
            # Telegram отверг результаты — отдаём хотя бы кнопку ошибки
            await _answer(query, [], button=_button(t("inline.error", lang), "inline_help"))

    except Exception as e:
        logger.error(f"Inline: не удалось обработать {clean_url}: {e}")
        await _answer(query, [], button=_button(t("inline.error", lang), "inline_help"))
