from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from services.quest_service import QuestService
from services.chat_service import ChatService
from services.profile_service import ProfileService
from models.interaction import ActionEnum
from core.exp import get_tier_name

router = Router(name="quest_router")


def get_quest_action_keyboard(target_id: int) -> types.InlineKeyboardMarkup:
    """Build Inline keyboard for daily pasangan decision."""
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Pass", callback_data=f"quest_act:pass:{target_id}")
    builder.button(text="❤️ Like", callback_data=f"quest_act:like:{target_id}")
    builder.button(text="⭐ Superlike (1⚡)", callback_data=f"quest_act:superlike:{target_id}")
    builder.adjust(2, 1)
    return builder.as_markup()


@router.message(Command("quest"))
@router.message(F.text == "🎯 Quest Harian")
async def quest_handler(message: types.Message, session: AsyncSession):
    """Render daily quest pasangan card."""
    quest_service = QuestService(session)
    quest, scored_candidates = await quest_service.get_or_create_daily_quest(message.from_user.id)

    evaluated_count = quest.details.get("evaluated_count", 0)

    if evaluated_count >= len(scored_candidates) or not scored_candidates:
        await message.answer(
            "🎉 **QUEST HARIAN SELESAI!** 🎉\n\n"
            "Kamu sudah mengevaluasi semua pasangan hari ini! "
            "Kamu mendapat **+30 EXP** dan streak login kamu bertambah! 🔥\n\n"
            "Kembali lagi besok untuk pasangan quest harian baru!"
        )
        return

    # Render current pasangan card
    candidate_user, candidate_prof, score = scored_candidates[evaluated_count]
    tier = get_tier_name(candidate_user.level)

    bio_snippet = candidate_prof.bio or "Belum ada bio."
    interests_str = ", ".join(candidate_prof.interests) if candidate_prof.interests else "Belum diisi"
    display_name = candidate_prof.display_name or f"User_{candidate_user.telegram_id % 10000}"

    card_text = (
        f"🎯 **Pasangan Quest #{evaluated_count + 1}** (Kecocokan: **{score}%**)\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📛 **{display_name}** ({candidate_prof.age or 22} tahun) — {tier}\n"
        f"📝 **Bio:** _{bio_snippet}_\n\n"
        f"🏷️ **Minat:** {interests_str}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"Pilih tindakan kamu:"
    )

    keyboard = get_quest_action_keyboard(candidate_user.telegram_id)

    if candidate_prof.photo_file_ids and len(candidate_prof.photo_file_ids) > 0:
        try:
            await message.answer_photo(
                photo=candidate_prof.photo_file_ids[0], caption=card_text, reply_markup=keyboard
            )
        except Exception:
            await message.answer(card_text, reply_markup=keyboard)
    else:
        await message.answer(card_text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("quest_act:"))
async def process_quest_action(callback: types.CallbackQuery, session: AsyncSession):
    """Process user evaluation action (like, pass, superlike)."""
    parts = callback.data.split(":")
    action_type = parts[1]
    target_id = int(parts[2])

    chat_service = ChatService(session)
    quest_service = QuestService(session)

    action_enum = ActionEnum.PASS
    if action_type == "like":
        action_enum = ActionEnum.LIKE
    elif action_type == "superlike":
        action_enum = ActionEnum.SUPERLIKE

    try:
        is_mutual, match_obj, ice_breakers = await chat_service.record_interaction(
            user_id=callback.from_user.id,
            target_id=target_id,
            action=action_enum,
        )
    except ValueError as e:
        # Spark insufficient for SUPERLIKE
        await callback.answer(str(e), show_alert=True)
        return

    completed = await quest_service.record_evaluation(callback.from_user.id)

    if is_mutual:
        ice_text = "\n".join([f"• {ib}" for ib in ice_breakers])
        await callback.message.answer(
            f"💖 **IT'S A MATCH!** 💖\n\n"
            f"Selamat! Kamu dan pasangan saling menyukai! 🎉 (+15 EXP!)\n\n"
            f"💡 **Ice-Breaker Starters:**\n{ice_text}\n\n"
            f"Gunakan command `/chat` untuk mulai mengobrol!"
        )
    else:
        # Show spark cost confirmation for SUPERLIKE
        if action_type == "superlike":
            await callback.answer(f"⭐ Superlike terkirim! (-1⚡)", show_alert=True)
        else:
            await callback.answer(f"Tindakan {action_type.upper()} tersimpan!")

    # Prompt next pasangan or complete message
    if completed:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            "🎉 **QUEST HARIAN SELESAI!** 🎉\n"
            "Semua pasangan hari ini telah dinilai! Bonus **+30 EXP** dan Streak +1 telah ditambahkan! 🔥"
        )
    else:
        # Re-trigger quest handler to show next pasangan
        await quest_handler(callback.message, session)