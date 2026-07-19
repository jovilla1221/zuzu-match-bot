from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from services.leaderboard_service import LeaderboardService

router = Router(name="leaderboard_router")


def get_leaderboard_category_keyboard() -> types.InlineKeyboardMarkup:
    """Build inline category switcher buttons for leaderboard views."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔥 Most Active", callback_data="lb_cat:active")
    builder.button(text="💬 Conversationalist", callback_data="lb_cat:chat")
    builder.button(text="🚀 Rising Star", callback_data="lb_cat:rising")
    builder.adjust(3)
    return builder.as_markup()


@router.message(Command("leaderboard"))
@router.message(F.text == "🏆 Leaderboard")
async def leaderboard_handler(message: types.Message, session: AsyncSession):
    """Render Most Active default leaderboard."""
    await render_leaderboard_category(message, "active", session)


@router.callback_query(F.data.startswith("lb_cat:"))
async def process_leaderboard_category_switch(callback: types.CallbackQuery, session: AsyncSession):
    """Switch category tab on inline button click."""
    cat = callback.data.split(":")[1]
    await render_leaderboard_category(callback.message, cat, session, is_callback=True)
    await callback.answer()


async def render_leaderboard_category(
    message: types.Message, category: str, session: AsyncSession, is_callback: bool = False
):
    lb_service = LeaderboardService(session)

    if category == "chat":
        title = "💬 **Leaderboard: Best Conversationalist**"
        results = await lb_service.get_best_conversationalists(limit=10)
    elif category == "rising":
        title = "🚀 **Leaderboard: Rising Star**"
        results = await lb_service.get_rising_stars(limit=10)
    else:
        title = "🔥 **Leaderboard: Most Active**"
        results = await lb_service.get_most_active_leaderboard(limit=10)

    rows = []
    medals = ["🥇", "🥈", "🥉"]

    for idx, (user, profile, tier) in enumerate(results, start=1):
        prefix = medals[idx - 1] if idx <= 3 else f"#{idx}"
        name = profile.display_name or f"User_{user.telegram_id % 10000}"
        rows.append(f"{prefix} **{name}** — {tier} ({user.exp} EXP | 🔥 {user.streak}d)")

    if not rows:
        content_text = f"{title}\n\nBelum ada data leaderboard minggu ini."
    else:
        content_text = f"{title}\n━━━━━━━━━━━━━━━━━━━\n" + "\n".join(rows)

    keyboard = get_leaderboard_category_keyboard()

    if is_callback:
        await message.edit_text(content_text, reply_markup=keyboard)
    else:
        await message.answer(content_text, reply_markup=keyboard)
