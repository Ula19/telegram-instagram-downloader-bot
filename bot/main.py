"""Точка входа — запуск бота"""
import asyncio
import glob
import logging
import os
import time

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.enums import ParseMode
from sqlalchemy import text

from bot.config import settings
from bot.database import engine
from bot.database.models import Base
from bot.emojis import E
from bot.handlers import admin, download, inline, start
from bot.i18n import get_bot_commands
from bot.middlewares.rate_limit import RateLimitMiddleware
from bot.middlewares.subscription import SubscriptionMiddleware

# настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# файл-флаг для определения crash recovery
_CRASH_FLAG = "/tmp/insta_bot_running.flag"

# паттерны для фоновой очистки
_TMP_GLOB = "/tmp/insta_*/**/*"
_BOT_API_GLOB = "/var/lib/telegram-bot-api/**/*"


async def _background_cleanup() -> None:
    """Фоновая очистка /tmp и Local Bot API каждые 5 минут.
    /tmp/insta_* — старше 30 мин, Local Bot API — старше 1 часа.
    """
    while True:
        await asyncio.sleep(300)
        now = time.time()
        tmp_cutoff = now - 30 * 60
        api_cutoff = now - 60 * 60

        cleaned_tmp = 0
        for f in glob.glob(_TMP_GLOB, recursive=True):
            try:
                if os.path.isfile(f) and os.path.getmtime(f) < tmp_cutoff:
                    os.remove(f)
                    cleaned_tmp += 1
            except OSError:
                pass

        cleaned_api = 0
        for f in glob.glob(_BOT_API_GLOB, recursive=True):
            try:
                if os.path.isfile(f) and os.path.getmtime(f) < api_cutoff:
                    os.remove(f)
                    cleaned_api += 1
            except OSError:
                pass

        if cleaned_tmp or cleaned_api:
            logger.info(
                "Фоновая очистка: /tmp=%d, Local Bot API=%d",
                cleaned_tmp, cleaned_api,
            )


async def on_startup(bot: Bot) -> None:
    """Действия при запуске бота"""
    # создаём таблицы если их нет
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        try:
            await conn.execute(text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS language VARCHAR(5) DEFAULT 'ru'"
            ))
        except Exception:
            pass

    logger.info("Таблицы БД созданы/проверены")

    bot_info = await bot.get_me()
    logger.info(f"Бот запущен: @{bot_info.username}")

    # устанавливаем дефолтное меню команд (Английский для всех остальных)
    await bot.set_my_commands(get_bot_commands("en"))

    # Русский — для тех, у кого Telegram на русском
    await bot.set_my_commands(get_bot_commands("ru"), language_code="ru")

    # Узбекский — для тех, у кого Telegram на узбекском
    await bot.set_my_commands(get_bot_commands("uz"), language_code="uz")

    # health-check: если флаг существует — значит прошлый запуск упал
    if os.path.exists(_CRASH_FLAG):
        for admin_id in settings.admin_id_list:
            try:
                await bot.send_message(
                    admin_id,
                    f"{E['warning']} <b>Бот перезапущен после падения!</b>\n\n"
                    f"{E['bot']} @{bot_info.username}\n"
                    "Проверь логи: <code>journalctl -u insta-bot -n 50</code>",
                )
            except Exception as e:
                logger.warning(f"Не удалось уведомить админа {admin_id}: {e}")

    # ставим флаг — бот работает
    with open(_CRASH_FLAG, "w") as f:
        f.write("running")

    # запускаем фоновую очистку /tmp и Local Bot API
    asyncio.create_task(_background_cleanup())
    logger.info("Фоновая очистка запущена (каждые 5 мин)")


async def on_shutdown(bot: Bot) -> None:
    """Действия при штатной остановке бота"""
    # убираем флаг — остановка штатная, не crash
    if os.path.exists(_CRASH_FLAG):
        os.remove(_CRASH_FLAG)

    await engine.dispose()
    logger.info("Бот остановлен, соединение с БД закрыто")


async def main() -> None:
    """Главная функция запуска"""
    # локальный Bot API или стандартный
    bot_kwargs = {
        "token": settings.bot_token,
        "default": DefaultBotProperties(parse_mode=ParseMode.HTML),
    }
    if settings.local_bot_api_url:
        bot_kwargs["base_url"] = f"{settings.local_bot_api_url}/bot"
        bot_kwargs["base_file_url"] = f"{settings.local_bot_api_url}/file/bot"
        logger.info(f"Используем Local Bot API: {settings.local_bot_api_url}")

    bot = Bot(**bot_kwargs)

    # диспетчер для обработки событий
    dp = Dispatcher()

    # регистрируем хэндлеры (порядок важен!)
    dp.include_router(start.router)      # /start и меню — первый
    dp.include_router(admin.router)      # /admin — второй
    dp.include_router(inline.router)     # inline-режим (@бот ссылка в чатах)
    dp.include_router(download.router)   # ссылки Instagram — последний

    # мидлвари (порядок: rate limit → подписка)
    dp.message.middleware(RateLimitMiddleware())
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())

    # хуки запуска/остановки
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logger.info("Запускаем бота...")

    # запуск polling (получение обновлений)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
