import time
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from loguru import logger


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging incoming Telegram updates and handler execution time."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        start_time = time.time()
        user_id = "unknown"

        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
            logger.info(f"[Update Message] user_id={user_id} text='{event.text}'")
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id
            logger.info(f"[Update Callback] user_id={user_id} data='{event.data}'")

        try:
            result = await handler(event, data)
            duration = (time.time() - start_time) * 1000
            logger.info(f"[Update Done] user_id={user_id} duration={duration:.2f}ms")
            return result
        except Exception as exc:
            duration = (time.time() - start_time) * 1000
            logger.error(f"[Update Error] user_id={user_id} duration={duration:.2f}ms error={exc}")
            raise
