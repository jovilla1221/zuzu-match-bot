from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.utils.messages import PROFILE_VIEW
from bot.states.onboarding import AIBioFSM, SetNameFSM, SetPhotoFSM, SetBioFSM, SetGenderFSM, SetInterestsFSM
from services.user_service import UserService
from services.profile_service import ProfileService
from core.exp import get_tier_name, exp_progress_info

router = Router(name="profile_router")


@router.message(Command("profile"))
@router.message(F.text == "👤 Profil Saya")
async def profile_handler(message: types.Message, session: AsyncSession):
    """Render user profile with level, tier, exp progress, badges, and completeness."""
    user_service = UserService(session)
    profile_service = ProfileService(session)

    user = await user_service.get_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("⚠️ Profil tidak ditemukan. Silakan jalankan /start dulu ya!")
        return

    profile = await profile_service.get_profile(message.from_user.id)
    if not profile:
        await message.answer("⚠️ Profil belum diisi. Silakan jalankan /start!")
        return

    tier = get_tier_name(user.level)
    curr_lvl, exp_in_lvl, req_in_lvl, percentage = exp_progress_info(user.exp)

    # Render visual progress bar (10 blocks)
    filled_blocks = int(percentage * 10)
    progress_bar = "🟩" * filled_blocks + "⬜" * (10 - filled_blocks)

    interests_str = ", ".join(profile.interests) if profile.interests else "Belum diisi"
    badges_str = " | ".join(profile.badges) if profile.badges else "Belum ada badge"
    bio_str = profile.bio if profile.bio else "Belum ada bio."
    display_name = profile.display_name or message.from_user.first_name or f"User_{user.telegram_id % 10000}"

    text = PROFILE_VIEW.format(
        username=display_name,
        tier=tier,
        level=user.level,
        progress_bar=progress_bar,
        exp_in_level=exp_in_lvl,
        required=req_in_lvl,
        streak=user.streak,
        spark=user.spark,
        completeness=profile.completeness_score,
        bio=bio_str,
        interests=interests_str,
        badges=badges_str,
    )

    keyboard_builder = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="✏️ Ubah Nama Panggilan", callback_data="profile_set_name"),
                types.InlineKeyboardButton(text="🖼️ Ganti Foto", callback_data="profile_set_photo"),
            ],
            [
                types.InlineKeyboardButton(text="✨ Tulis Bio via AI", callback_data="profile_ai_bio"),
                types.InlineKeyboardButton(text="📝 Ubah Bio Manual", callback_data="profile_set_bio"),
            ],
            [
                types.InlineKeyboardButton(text="🏷️ Ubah Minat", callback_data="profile_set_interests"),
                types.InlineKeyboardButton(text="🚻 Ubah Gender", callback_data="profile_set_gender"),
            ]
        ]
    )

    if profile.photo_file_ids and len(profile.photo_file_ids) > 0:
        try:
            await message.answer_photo(photo=profile.photo_file_ids[0], caption=text, reply_markup=keyboard_builder)
        except Exception:
            await message.answer(text, reply_markup=keyboard_builder)
    else:
        await message.answer(text, reply_markup=keyboard_builder)


# ─── Custom Display Name Handler Flow ───

@router.message(Command("setname"))
@router.callback_query(F.data == "profile_set_name")
async def set_name_start(event: types.TelegramObject, state: FSMContext):
    """Prompt user to type new custom display name."""
    await state.set_state(SetNameFSM.NAME)
    prompt_text = (
        "✏️ **Ubah Nama Panggilan Kamu:**\n\n"
        "Ketik nama panggilan baru yang ingin kamu tampilkan di profil, quest, dan leaderboard.\n\n"
        "Kirim /cancel untuk membatalkan."
    )
    if isinstance(event, types.CallbackQuery):
        await event.message.answer(prompt_text)
        await event.answer()
    else:
        await event.answer(prompt_text)


@router.message(SetNameFSM.NAME, Command("cancel"))
async def set_name_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Perubahan nama dibatalkan. Ketik /profile untuk lihat profil.")


@router.message(SetNameFSM.NAME, F.text)
async def set_name_process(message: types.Message, state: FSMContext, session: AsyncSession):
    new_name = message.text.strip()
    if len(new_name) < 2 or len(new_name) > 30:
        await message.answer("⚠️ Nama panggilan harus antara 2 hingga 30 karakter ya!")
        return

    profile_service = ProfileService(session)
    await profile_service.update_display_name(message.from_user.id, new_name)
    await state.clear()

    await message.answer(
        f"✅ Nama panggilan berhasil diubah menjadi **{new_name}**! 🎉\nKetik /profile untuk melihat profilmu."
    )


# ─── Photo Handler Flow ───

@router.callback_query(F.data == "profile_set_photo")
async def set_photo_start(callback: types.CallbackQuery, state: FSMContext):
    """Prompt user to upload a new photo."""
    await state.set_state(SetPhotoFSM.PHOTO)
    prompt_text = (
        "📸 **Kirimkan Foto Profil Baru Kamu:**\n\n"
        "Pastikan wajahmu terlihat jelas agar lebih mudah dikenali! "
        "(Kirim sebagai foto biasa, bukan dokumen).\n\n"
        "Kirim /cancel untuk membatalkan."
    )
    await callback.message.answer(prompt_text)
    await callback.answer()


@router.message(SetPhotoFSM.PHOTO, Command("cancel"))
async def set_photo_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Perubahan foto dibatalkan. Ketik /profile untuk lihat profil.")


@router.message(SetPhotoFSM.PHOTO, F.photo)
async def set_photo_process(message: types.Message, state: FSMContext, session: AsyncSession):
    photo_file_id = message.photo[-1].file_id
    profile_service = ProfileService(session)
    await profile_service.add_photo(message.from_user.id, photo_file_id)
    await state.clear()

    await message.answer(
        "✅ Foto profil berhasil diubah! 🎉\nKetik /profile untuk melihat profil barumu."
    )


@router.message(SetPhotoFSM.PHOTO)
async def set_photo_invalid(message: types.Message):
    await message.answer("⚠️ Tolong kirim sebuah **foto** (bukan file/dokumen/teks). Atau kirim /cancel untuk batal.")


# ─── AI Bio Flow: prompt → generate → preview → confirm ───

@router.message(Command("ai_bio"))
@router.message(F.text == "✨ AI Bio Assistant")
@router.callback_query(F.data == "profile_ai_bio")
async def ai_bio_start(event: types.TelegramObject, state: FSMContext, session: AsyncSession):
    """Step 1: Ask user what kind of bio they want."""
    user_id = event.from_user.id
    profile_service = ProfileService(session)
    profile = await profile_service.get_profile(user_id)

    if not profile:
        msg = "⚠️ Profil belum ditemukan. Silakan jalankan /start!"
        if isinstance(event, types.CallbackQuery):
            await event.answer(msg, show_alert=True)
        else:
            await event.answer(msg)
        return

    # Store interests for later prompt construction
    await state.update_data(
        interests=profile.interests or [],
        current_bio=profile.bio or "",
    )
    await state.set_state(AIBioFSM.PROMPT)

    prompt_text = (
        "🤖 **Bantu Tulis Bio via Gemini AI**\n\n"
        "Ceritakan gaya bio yang kamu mau! Misalnya:\n"
        "• _\"Santai, suka ngopi dan jalan-jalan\"_\n"
        "• _\"Lucu, sedikit sarcasm, gemar gaming\"_\n"
        "• _\"Minimalis, mysterious vibes\"_\n\n"
        "Ketik deskripsi gaya bio kamu (wajib). Setiap generate akan mengikuti prompt kamu.\n\n"
        "Kirim /cancel untuk batal."
    )

    if isinstance(event, types.CallbackQuery):
        await event.message.answer(prompt_text)
        await event.answer()
    else:
        await event.answer(prompt_text)


@router.message(AIBioFSM.PROMPT, Command("cancel"))
async def ai_bio_cancel(message: types.Message, state: FSMContext):
    """Cancel AI bio generation."""
    await state.clear()
    await message.answer("❌ Generasi bio dibatalkan. Ketik /profile untuk lihat profil.")


@router.message(AIBioFSM.PROMPT)
async def ai_bio_generate(message: types.Message, state: FSMContext, session: AsyncSession):
    """Step 2: User sent prompt → generate bio via Gemini → show preview."""
    user_text = (message.text or "").strip()

    if not user_text:
        await message.answer("⚠️ Ketik deskripsi gaya bio yang kamu mau. /cancel untuk batal.")
        return

    data = await state.get_data()
    interests = data.get("interests", [])
    current_bio = data.get("current_bio", "")

    # Always use explicit user prompt — no "skip" auto-generate
    user_prompt = user_text

    await message.answer("🤖 Gemini sedang menulis bio kamu... tunggu sebentar ya!")

    from core.ai_service import GeminiAIService

    ai_service = GeminiAIService()
    suggested_bio = ai_service.generate_ai_bio(
        interests=interests,
        current_bio=current_bio,
        user_prompt=user_prompt,
    )

    # Store generated bio in FSM for confirm/regenerate
    await state.update_data(
        generated_bio=suggested_bio,
        user_prompt=user_prompt,
    )
    await state.set_state(AIBioFSM.PREVIEW)

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="✅ Simpan Bio", callback_data="ai_bio_save"),
                types.InlineKeyboardButton(text="🔄 Regenerate", callback_data="ai_bio_regen"),
            ],
            [types.InlineKeyboardButton(text="❌ Batal", callback_data="ai_bio_cancel")],
        ]
    )

    await message.answer(
        f"🤖 **Saran Bio dari Gemini:**\n\n"
        f"_{suggested_bio}_\n\n"
        f"Pilih aksi di bawah:",
        reply_markup=keyboard,
    )


@router.callback_query(AIBioFSM.PREVIEW, F.data == "ai_bio_save")
async def ai_bio_save(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    """Step 3a: User confirms → save bio + award EXP."""
    data = await state.get_data()
    suggested_bio = data.get("generated_bio", "")

    if not suggested_bio:
        await callback.answer("⚠️ Sesi kedaluwarsa. Coba lagi dengan /ai_bio", show_alert=True)
        await state.clear()
        return

    profile_service = ProfileService(session)
    await profile_service.update_bio(callback.from_user.id, suggested_bio)

    from services.gamification_service import GamificationService
    gamification = GamificationService(session)
    await gamification.award_profile_step_exp(callback.from_user.id)

    await state.clear()
    await callback.message.edit_text(
        f"✅ **Bio berhasil disimpan!**\n\n"
        f"_{suggested_bio}_\n\n"
        f"🎉 +30 EXP awarded! Ketik /profile untuk lihat profilmu."
    )
    await callback.answer("Bio disimpan!")


@router.callback_query(AIBioFSM.PREVIEW, F.data == "ai_bio_regen")
async def ai_bio_regenerate(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    """Step 3b: User wants regenerate → call Gemini again with same prompt."""
    data = await state.get_data()
    interests = data.get("interests", [])
    current_bio = data.get("current_bio", "")
    user_prompt = data.get("user_prompt", "")

    await callback.answer("Regenerating...")

    from core.ai_service import GeminiAIService
    ai_service = GeminiAIService()
    suggested_bio = ai_service.generate_ai_bio(
        interests=interests,
        current_bio=current_bio,
        user_prompt=user_prompt,
    )

    await state.update_data(generated_bio=suggested_bio)

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="✅ Simpan Bio", callback_data="ai_bio_save"),
                types.InlineKeyboardButton(text="🔄 Regenerate", callback_data="ai_bio_regen"),
            ],
            [types.InlineKeyboardButton(text="❌ Batal", callback_data="ai_bio_cancel")],
        ]
    )

    await callback.message.edit_text(
        f"🤖 **Saran Bio dari Gemini (regenerated):**\n\n"
        f"_{suggested_bio}_\n\n"
        f"Pilih aksi di bawah:",
        reply_markup=keyboard,
    )


@router.callback_query(AIBioFSM.PREVIEW, F.data == "ai_bio_cancel")
async def ai_bio_cancel_callback(callback: types.CallbackQuery, state: FSMContext):
    """Step 3c: User cancels from preview."""
    await state.clear()
    await callback.message.edit_text("❌ Generasi bio dibatalkan. Ketik /profile untuk lihat profil.")
    await callback.answer()


# ─── Manual Bio Edit Flow ───

@router.callback_query(F.data == "profile_set_bio")
async def set_manual_bio_start(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(SetBioFSM.BIO)
    prompt = (
        "📝 **Ubah Bio Manual:**\n\n"
        "Ketik bio baru kamu (minimal 10 karakter).\n\n"
        "Kirim /cancel untuk membatalkan."
    )
    await callback.message.answer(prompt)
    await callback.answer()

@router.message(SetBioFSM.BIO, Command("cancel"))
async def set_manual_bio_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Perubahan bio dibatalkan. Ketik /profile untuk lihat profil.")

@router.message(SetBioFSM.BIO, F.text)
async def set_manual_bio_process(message: types.Message, state: FSMContext, session: AsyncSession):
    bio_text = message.text.strip()
    if len(bio_text) < 10:
        await message.answer("⚠️ Bio kamu terlalu singkat! Tulis minimal 10 karakter ya.")
        return

    profile_service = ProfileService(session)
    await profile_service.update_bio(message.from_user.id, bio_text)
    await state.clear()

    await message.answer("✅ Bio berhasil diubah! 🎉\nKetik /profile untuk melihat profilmu.")


# ─── Edit Gender Flow ───

@router.callback_query(F.data == "profile_set_gender")
async def set_gender_start(callback: types.CallbackQuery, state: FSMContext):
    from bot.keyboards.inline import get_user_gender_keyboard
    await state.set_state(SetGenderFSM.GENDER)
    keyboard = get_user_gender_keyboard()
    await callback.message.answer("🚻 **Ubah Gender Kamu:**", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(SetGenderFSM.GENDER, F.data.startswith("my_gender:"))
async def process_edit_gender(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    gender = callback.data.split(":", 1)[1]
    profile_service = ProfileService(session)
    await profile_service.update_gender(callback.from_user.id, gender)
    await state.clear()
    await callback.message.edit_text(f"✅ Gender berhasil diubah!\nKetik /profile untuk melihat profilmu.")
    await callback.answer()


# ─── Edit Interests Flow ───

@router.callback_query(F.data == "profile_set_interests")
async def set_interests_start(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    from bot.keyboards.inline import get_interests_keyboard
    profile_service = ProfileService(session)
    profile = await profile_service.get_profile(callback.from_user.id)
    
    selected = set(profile.interests) if profile and profile.interests else set()
    await state.update_data(selected_interests=selected)
    await state.set_state(SetInterestsFSM.INTERESTS)
    
    keyboard = get_interests_keyboard(selected)
    await callback.message.answer("🏷️ **Ubah Minat & Hobi:**\nPilih minimal 3 tag:", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(SetInterestsFSM.INTERESTS, F.data.startswith("interest_toggle:"))
async def edit_interest_toggle(callback: types.CallbackQuery, state: FSMContext):
    from bot.keyboards.inline import get_interests_keyboard
    tag = callback.data.split(":", 1)[1]
    data = await state.get_data()
    selected: set = data.get("selected_interests", set())

    if tag in selected:
        selected.remove(tag)
    else:
        selected.add(tag)

    await state.update_data(selected_interests=selected)
    keyboard = get_interests_keyboard(selected)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()

@router.callback_query(SetInterestsFSM.INTERESTS, F.data == "interest_save")
async def edit_interest_save(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    selected: set = data.get("selected_interests", set())

    if len(selected) < 3:
        await callback.answer("⚠️ Pilih minimal 3 minat/hobi ya!", show_alert=True)
        return

    profile_service = ProfileService(session)
    await profile_service.update_interests(callback.from_user.id, list(selected))
    await state.clear()

    await callback.message.edit_text("✅ Minat berhasil diperbarui! 🎉\nKetik /profile untuk melihat profilmu.")
    await callback.answer()