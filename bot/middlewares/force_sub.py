from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from loguru import logger

class ForceSubMiddleware(BaseMiddleware):
    def __init__(self, channel_username: str = "@botunlverse"):
        self.channel_username = channel_username
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        bot = data.get("bot")
        if not bot:
            return await handler(event, data)

        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        try:
            member = await bot.get_chat_member(chat_id=self.channel_username, user_id=user.id)
            if member.status in ["left", "kicked"]:
                msg_text = (
                    f"⚠️ **AKSES DITOLAK**\n\n"
                    f"Untuk menggunakan bot ini, kamu WAJIB berlangganan ke channel "
                    f"**{self.channel_username}** terlebih dahulu."
                )
                
                from aiogram.utils.keyboard import InlineKeyboardBuilder
                builder = InlineKeyboardBuilder()
                builder.button(text="📢 Gabung Channel", url="https://t.me/botunlverse")
                markup = builder.as_markup()
                
                if isinstance(event, Message):
                    await event.answer(msg_text, reply_markup=markup)
                elif isinstance(event, CallbackQuery):
                    await event.message.answer(msg_text, reply_markup=markup)
                    await event.answer()
                
                # Stop propagation
                return
        except Exception as e:
            logger.warning(f"Error checking channel membership for {user.id}: {e}")
            # If bot can't check, we might want to let them pass or block. 
            # Usually, we let them pass if it's an API error, but if the bot must strictly enforce it,
            # it implies the bot must be an admin in that channel.
            # Assuming bot is admin. We'll let it pass on exception to avoid breaking the bot 
            # if the channel API is temporarily down, but log the error.

        return await handler(event, data)
