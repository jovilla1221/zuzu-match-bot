from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from services.verification_service import VerificationService

router = Router(name="admin_router")


def get_admin_review_keyboard(target_user_id: int) -> types.InlineKeyboardMarkup:
    """Build inline buttons for admin photo verification decision."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Approve", callback_data=f"admin_verify:approve:{target_user_id}")
    builder.button(text="Reject", callback_data=f"admin_verify:reject:{target_user_id}")
    builder.adjust(2)
    return builder.as_markup()


@router.callback_query(F.data.startswith("admin_verify:"))
async def process_admin_verification_decision(callback: types.CallbackQuery, session: AsyncSession):
    """Handle admin decision on photo review queue. Requires admin auth."""
    # FIX: Enforce admin ownership — reject if caller is not the admin
    if callback.from_user.id != settings.ADMIN_CHAT_ID:
        await callback.answer("Unauthorized — admin only.", show_alert=True)
        return

    parts = callback.data.split(":")
    action = parts[1]
    target_user_id = int(parts[2])

    verification_service = VerificationService(session)

    if action == "approve":
        await verification_service.admin_approve(target_user_id)
        await callback.message.edit_text(
            f"User ID `{target_user_id}` approved by admin."
        )
    else:
        await callback.message.edit_text(
            f"User ID `{target_user_id}` rejected by admin."
        )

    await callback.answer()
