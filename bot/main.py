import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from loguru import logger

from core.config import settings
from core.database import async_session_factory
from bot.middlewares.db import DbSessionMiddleware
from bot.middlewares.logging import LoggingMiddleware
from bot.handlers.start import router as start_router
from bot.handlers.profile import router as profile_router
from bot.handlers.quest import router as quest_router
from bot.handlers.chat import router as chat_router
from bot.handlers.admin import router as admin_router
from bot.handlers.leaderboard import router as leaderboard_router
from bot.handlers.search import router as search_router


async def main():
    logger.info("Initializing Zuzu Match Bot...")

    # Set up FSM Storage (Redis with MemoryStorage fallback)
    try:
        from redis.asyncio import Redis
        redis_client = Redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        storage = RedisStorage(redis=redis_client)
        logger.info(f"Connected to Redis at {settings.REDIS_URL}")
    except Exception as e:
        logger.warning(f"Could not connect to Redis ({e}). Falling back to MemoryStorage.")
        storage = MemoryStorage()

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
    dp = Dispatcher(storage=storage)

    # Register Middlewares
    dp.update.outer_middleware(LoggingMiddleware())
    dp.update.middleware(DbSessionMiddleware(async_session_factory))
    
    from bot.middlewares.force_sub import ForceSubMiddleware
    force_sub = ForceSubMiddleware()
    dp.message.outer_middleware(force_sub)
    dp.callback_query.outer_middleware(force_sub)

    # Register Handlers
    dp.include_router(start_router)
    dp.include_router(search_router)
    dp.include_router(profile_router)
    dp.include_router(quest_router)
    dp.include_router(chat_router)
    dp.include_router(admin_router)
    dp.include_router(leaderboard_router)

    # Register Bot Menu Commands in Telegram App UI
    from aiogram.types import BotCommand
    bot_commands = [
        BotCommand(command="start", description="Mulai petualangan & Onboarding"),
        BotCommand(command="search", description="Cari pasangan match berdasarkan minat/kata kunci"),
        BotCommand(command="profile", description="Lihat profil & progress level"),
        BotCommand(command="quest", description="Quest harian & rekomendasi pasangan"),
        BotCommand(command="chat", description="Lihat match & percakapan relay"),
        BotCommand(command="leaderboard", description="Peringkat mingguan regional"),
        BotCommand(command="ai_bio", description="Bantu tulis bio via Gemini AI"),
    ]
    await bot.set_my_commands(bot_commands)
    logger.info("Registered Telegram Bot Menu Commands successfully!")

    logger.info("Starting bot polling loop...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
