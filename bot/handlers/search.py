from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from bot.states.onboarding import SearchFSM
from bot.keyboards.inline import get_search_filter_keyboard
from services.matching_service import MatchingService
from services.chat_service import ChatService
from models.interaction import ActionEnum
from core.exp import get_tier_name

router = Router(name="search_router")


def get_search_action_keyboard(target_id: int, current_index: int = 0, total: int = 1) -> types.InlineKeyboardMarkup:
    """Build action buttons for search result card."""
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Pass", callback_data=f"search_act:pass:{target_id}:{current_index}")
    builder.button(text="❤️ Like", callback_data=f"search_act:like:{target_id}:{current_index}")
    builder.button(text="⭐ Superlike (1⚡)", callback_data=f"search_act:superlike:{target_id}:{current_index}")

    if current_index + 1 < total:
        builder.button(text="➡️ Pasangan Berikutnya", callback_data=f"search_act:next:{target_id}:{current_index}")

    builder.button(text="🔍 Cari Ulang", callback_data="search_reset")
    builder.adjust(2, 1, 1, 1)
    return builder.as_markup()


@router.message(Command("search"))
@router.message(F.text == "🔍 Cari Pasangan")
async def search_menu_handler(event: types.TelegramObject, state: FSMContext, session: AsyncSession):
    """Directly fetch random candidates bypassing the filter menu."""
    await state.clear()
    
    if isinstance(event, types.CallbackQuery):
        user_id = event.from_user.id
        message = event.message
    else:
        user_id = event.from_user.id
        message = event

    matching_service = MatchingService(session)
    results = await matching_service.get_candidate_matches(
        user_id=user_id,
        limit=5,
    )

    if not results:
        msg = "🎉 Semua pasangan saat ini sudah dievaluasi!"
        if isinstance(event, types.CallbackQuery):
            await message.answer(msg)
            await event.answer()
        else:
            await message.answer(msg)
        return

    await render_search_candidate_card(message, results, index=0, filter_label="Pasangan Acak")
    if isinstance(event, types.CallbackQuery):
        await event.answer()


@router.callback_query(F.data == "search_reset")
async def search_reset_handler(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    """Reset search and directly show candidates again."""
    await search_menu_handler(callback, state, session)


@router.callback_query(F.data == "search_mode:query")
async def search_prompt_query_handler(callback: types.CallbackQuery, state: FSMContext):
    """Prompt user to type search keyword/username."""
    await state.set_state(SearchFSM.QUERY)
    await callback.message.answer(
        "🔎 **Ketik Kata Kunci Pencarian:**\n\n"
        "Misalnya: `username`, `anime`, `kopi`, `sci-fi`, `bandung`\n\n"
        "Kirim /cancel jika ingin membatalkan."
    )
    await callback.answer()


@router.message(SearchFSM.QUERY, Command("cancel"))
async def search_query_cancel(message: types.Message, state: FSMContext):
    """Cancel search keyword input."""
    await state.clear()
    await message.answer("❌ Pencarian dibatalkan. Ketik /search atau gunakan menu di bawah.")


@router.message(SearchFSM.QUERY)
async def process_search_query_text(message: types.Message, state: FSMContext, session: AsyncSession):
    """Perform keyword search in database."""
    keyword = (message.text or "").strip()
    if not keyword:
        await message.answer("⚠️ Masukkan kata kunci pencarian yang valid.")
        return

    await state.clear()
    matching_service = MatchingService(session)
    results = await matching_service.search_candidates_by_keyword(
        user_id=message.from_user.id,
        keyword=keyword,
        limit=5,
    )

    if not results:
        await message.answer(
            f"🔍 Tidak ditemukan pasangan yang cocok dengan kata kunci `'{keyword}'`.\n"
            f"Coba cari dengan kata kunci lain atau gunakan kategori populer!",
            reply_markup=get_search_filter_keyboard(),
        )
        return

    # Render first pasangan
    await render_search_candidate_card(message, results, index=0, filter_label=f"Kata kunci: '{keyword}'")


@router.callback_query(F.data.startswith("search_tag:"))
async def process_search_tag_callback(callback: types.CallbackQuery, session: AsyncSession):
    """Perform tag category search."""
    tag = callback.data.split(":", 1)[1]
    matching_service = MatchingService(session)

    results = await matching_service.search_candidates_by_tag(
        user_id=callback.from_user.id,
        tag=tag,
        limit=5,
    )

    if not results:
        await callback.message.answer(
            f"🔍 Belum ada pasangan baru dengan tag **{tag}**.\nCoba pilih kategori minat lainnya!",
            reply_markup=get_search_filter_keyboard(),
        )
        await callback.answer()
        return

    await render_search_candidate_card(callback.message, results, index=0, filter_label=f"Kategori {tag}")
    await callback.answer()


@router.callback_query(F.data == "search_mode:random")
async def process_search_random_callback(callback: types.CallbackQuery, session: AsyncSession):
    """Get random best pasangan recommendations."""
    matching_service = MatchingService(session)
    results = await matching_service.get_candidate_matches(
        user_id=callback.from_user.id,
        limit=5,
    )

    if not results:
        await callback.message.answer("🎉 Semua pasangan terdekat saat ini sudah dievaluasi!")
        await callback.answer()
        return

    await render_search_candidate_card(callback.message, results, index=0, filter_label="Pasangan Acak")
    await callback.answer()


async def render_search_candidate_card(
    message: types.Message, results: list, index: int = 0, filter_label: str = ""
):
    """Helper to render pasangan card from search result pool."""
    if index >= len(results):
        await message.answer(
            "🎉 Semua hasil pencarian untuk kategori ini telah kamu lihat!",
            reply_markup=get_search_filter_keyboard(),
        )
        return

    candidate_user, candidate_prof, score = results[index]
    tier = get_tier_name(candidate_user.level)
    display_name = candidate_prof.display_name or f"User_{candidate_user.telegram_id % 10000}"
    bio_snippet = candidate_prof.bio or "Belum ada bio."
    interests_str = ", ".join(candidate_prof.interests) if candidate_prof.interests else "Belum diisi"

    card_text = (
        f"🔎 **Hasil Pencarian ({filter_label}) #{index + 1}/{len(results)}**\n"
        f"Kecocokan: **{score}%**\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📛 **{display_name}** ({candidate_prof.age or 22} tahun) — {tier}\n"
        f"📝 **Bio:** _{bio_snippet}_\n\n"
        f"🏷️ **Minat:** {interests_str}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"Pilih tindakan kamu:"
    )

    keyboard = get_search_action_keyboard(candidate_user.telegram_id, current_index=index, total=len(results))

    if candidate_prof.photo_file_ids and len(candidate_prof.photo_file_ids) > 0:
        try:
            await message.answer_photo(
                photo=candidate_prof.photo_file_ids[0], caption=card_text, reply_markup=keyboard
            )
        except Exception as e:
            # Fallback if photo_file_id is invalid (e.g. sample mock data)
            await message.answer(card_text, reply_markup=keyboard)
    else:
        await message.answer(card_text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("search_act:"))
async def process_search_action_callback(callback: types.CallbackQuery, session: AsyncSession):
    """Process evaluation action on search pasangan card."""
    parts = callback.data.split(":")
    action_type = parts[1]
    target_id = int(parts[2])
    current_index = int(parts[3])

    if action_type == "next":
        matching_service = MatchingService(session)
        results = await matching_service.get_candidate_matches(user_id=callback.from_user.id, limit=5)
        await render_search_candidate_card(callback.message, results, index=current_index + 1, filter_label="Hasil")
        await callback.answer()
        return

    chat_service = ChatService(session)
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
        await callback.answer(str(e), show_alert=True)
        return

    if is_mutual:
        ice_text = "\n".join([f"• {ib}" for ib in ice_breakers])
        await callback.message.answer(
            f"💖 **IT'S A MATCH!** 💖\n\n"
            f"Selamat! Kamu dan pasangan saling menyukai! 🎉 (+15 EXP!)\n\n"
            f"💡 **Ice-Breaker Starters:**\n{ice_text}\n\n"
            f"Gunakan command `/chat` atau menu **💬 Match & Chat** untuk mulai mengobrol!"
        )
    else:
        if action_type == "superlike":
            await callback.answer("⭐ Superlike terkirim! (-1⚡)", show_alert=True)
        else:
            await callback.answer(f"Tindakan {action_type.upper()} tersimpan!")

    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 Cari Lagi", callback_data="search_reset")
    
    await callback.message.answer(
        "Tindakan tersimpan! Mau cari pasangan lain?",
        reply_markup=builder.as_markup(),
    )
