from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from services.chat_service import ChatService
from services.gamification_service import GamificationService

router = Router(name="chat_router")


def get_matches_keyboard(matches) -> types.InlineKeyboardMarkup:
    """Build inline buttons for selecting active match conversation."""
    builder = InlineKeyboardBuilder()
    for match, user_target, prof_target in matches:
        name = prof_target.display_name or f"Match_{user_target.telegram_id % 10000}"
        builder.button(
            text=f"💬 Chat dengan {name}",
            callback_data=f"chat_select:{match.id}:{user_target.telegram_id}",
        )
    builder.adjust(1)
    return builder.as_markup()


@router.message(Command("chat"))
@router.message(F.text == "💬 Match & Chat")
async def chat_list_handler(message: types.Message, session: AsyncSession):
    """Render list of active mutual matches."""
    chat_service = ChatService(session)
    matches = await chat_service.get_active_matches(message.from_user.id)

    if not matches:
        await message.answer(
            "💬 **Belum Ada Match Active**\n\n"
            "Kamu belum punya match aktif. Selesaikan `/quest` harianmu "
            "dan berikan Like pada pasangan favoritmu untuk mendapatkan match! ✨"
        )
        return

    text = f"💬 **Daftar Match Aktif Kamu ({len(matches)} Match):**\n\nPilih match di bawah untuk melihat percakapan:"
    keyboard = get_matches_keyboard(matches)
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("chat_select:"))
async def select_chat_match(callback: types.CallbackQuery, session: AsyncSession):
    """Handle match selection for chat relay."""
    parts = callback.data.split(":")
    match_id = int(parts[1])
    target_id = int(parts[2])

    await callback.message.edit_text(
        f"💬 **Relay Chat Aktif!**\n\n"
        f"Ketik pesan balasanmu di bot ini. Bot akan menyampaikan pesanmu secara aman dan anonim ke pasangan match ID `{target_id}`!\n\n"
        f"*(Setiap 10/25/50 pesan kamu bakal dapet bonus EXP! 🚀)*"
    )
    await callback.answer()
