from typing import Set
from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.states.onboarding import OnboardingFSM
from bot.utils.messages import (
    WELCOME_NEW,
    WELCOME_BACK,
    ONBOARD_PHOTO_PROMPT,
    ONBOARD_GENDER_PROMPT,
    ONBOARD_BIO_PROMPT,
    ONBOARD_INTERESTS_PROMPT,
    ONBOARD_PREFERENCES_PROMPT,
    ONBOARD_COMPLETE,
    LEVEL_UP,
)
from bot.keyboards.inline import get_interests_keyboard, get_gender_pref_keyboard, get_user_gender_keyboard
from bot.keyboards.reply import get_main_menu_keyboard
from services.user_service import UserService
from services.profile_service import ProfileService
from services.gamification_service import GamificationService
from core.exp import get_tier_name

router = Router(name="start_router")


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext, session: AsyncSession):
    """Entry point for /start command."""
    # --- Subscribe check ---
    target_channel = "@botunlverse"  # channel username
    try:
        chat_member = await message.bot.get_chat_member(chat_id=target_channel, user_id=message.from_user.id)
        is_member = chat_member.status in ("member", "administrator", "creator")
    except Exception:
        # Jika error (misal: bot tidak punya akses), anggap tidak subscribe
        is_member = False

    if not is_member:
        join_btn = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Join @botunlverse", url=f"https://t.me/{target_channel.lstrip('@')}")]
        ])
        await message.answer(
            "⚠️ Hey! Kamu harus subscribe ke @botunlverse dulu ya, sebelum bisa mulai pakai bot ini! 📢",
            reply_markup=join_btn,
        )
        return

    # --- Continue with existing logic ---
    user_service = UserService(session)
    profile_service = ProfileService(session)
    
    user = await user_service.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username or message.from_user.first_name,
    )

    if user.onboarding_step == "COMPLETE":
        tier = get_tier_name(user.level)
        name = message.from_user.first_name or "Adventurer"
        text = WELCOME_BACK.format(
            name=name,
            level=user.level,
            tier=tier,
            exp=user.exp,
            streak=user.streak,
            spark=user.spark,
        )
        await message.answer(text, reply_markup=get_main_menu_keyboard())
    else:
        await message.answer(WELCOME_NEW)
        await state.set_state(OnboardingFSM.NAME)
        await user_service.update_onboarding_step(user.telegram_id, "NAME")
        await message.answer(
            "📛 **Siapa nama panggilan (nickname) favorit kamu yang ingin ditampilkan ke pasangan match?**\n\n"
            "_(Nama ini yang akan terlihat oleh pengguna lain di profil, quest, & leaderboard, bukan username Telegram kamu!)_"
        )


@router.message(OnboardingFSM.NAME, F.text)
async def process_onboarding_name(message: types.Message, state: FSMContext, session: AsyncSession):
    """Process custom display name input in FSM."""
    display_name = message.text.strip()
    if len(display_name) < 2 or len(display_name) > 30:
        await message.answer("⚠️ Nama panggilan harus antara 2 hingga 30 karakter ya!")
        return

    profile_service = ProfileService(session)
    gamification_service = GamificationService(session)
    user_service = UserService(session)

    await profile_service.update_display_name(message.from_user.id, display_name)
    await gamification_service.award_profile_step_exp(message.from_user.id)
    await user_service.update_onboarding_step(message.from_user.id, "GENDER")

    await state.set_state(OnboardingFSM.GENDER)
    keyboard = get_user_gender_keyboard()
    await message.answer(ONBOARD_GENDER_PROMPT, reply_markup=keyboard)


@router.callback_query(OnboardingFSM.GENDER, F.data.startswith("my_gender:"))
async def process_onboarding_gender(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    """Process user's own gender selection."""
    gender = callback.data.split(":", 1)[1]
    
    profile_service = ProfileService(session)
    gamification_service = GamificationService(session)
    user_service = UserService(session)

    await profile_service.update_gender(callback.from_user.id, gender)
    await gamification_service.award_profile_step_exp(callback.from_user.id)
    await user_service.update_onboarding_step(callback.from_user.id, "PHOTO")

    await state.set_state(OnboardingFSM.PHOTO)
    await callback.message.edit_text(ONBOARD_PHOTO_PROMPT)
    await callback.answer()


@router.message(OnboardingFSM.PHOTO, F.photo)
async def process_onboarding_photo(message: types.Message, state: FSMContext, session: AsyncSession):
    """Process uploaded profile photo in FSM."""
    photo_file_id = message.photo[-1].file_id  # largest resolution photo
    profile_service = ProfileService(session)
    gamification_service = GamificationService(session)
    user_service = UserService(session)

    await profile_service.add_photo(message.from_user.id, photo_file_id)
    await gamification_service.award_profile_step_exp(message.from_user.id)
    await user_service.update_onboarding_step(message.from_user.id, "BIO")

    await state.set_state(OnboardingFSM.BIO)
    await message.answer(ONBOARD_BIO_PROMPT)


@router.message(OnboardingFSM.BIO, F.text)
async def process_onboarding_bio(message: types.Message, state: FSMContext, session: AsyncSession):
    """Process user bio text in FSM."""
    bio_text = message.text.strip()
    if len(bio_text) < 10:
        await message.answer("⚠️ Bio kamu terlalu singkat! Tulis minimal 10 karakter ya, biar pasangan lain makin kenal.")
        return

    profile_service = ProfileService(session)
    gamification_service = GamificationService(session)
    user_service = UserService(session)

    await profile_service.update_bio(message.from_user.id, bio_text)
    await gamification_service.award_profile_step_exp(message.from_user.id)
    await user_service.update_onboarding_step(message.from_user.id, "INTERESTS")

    # Initialize empty set in state data for multi-select
    await state.update_data(selected_interests=set())
    await state.set_state(OnboardingFSM.INTERESTS)
    
    keyboard = get_interests_keyboard(set())
    await message.answer(ONBOARD_INTERESTS_PROMPT, reply_markup=keyboard)


@router.callback_query(OnboardingFSM.INTERESTS, F.data.startswith("interest_toggle:"))
async def toggle_interest_tag(callback: types.CallbackQuery, state: FSMContext):
    """Toggle selection of an interest tag in inline keyboard."""
    tag = callback.data.split(":", 1)[1]
    data = await state.get_data()
    selected: Set[str] = data.get("selected_interests", set())

    if tag in selected:
        selected.remove(tag)
    else:
        selected.add(tag)

    await state.update_data(selected_interests=selected)
    keyboard = get_interests_keyboard(selected)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(OnboardingFSM.INTERESTS, F.data == "interest_save")
async def save_interests(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    """Confirm & save interest tags selection."""
    data = await state.get_data()
    selected: Set[str] = data.get("selected_interests", set())

    if len(selected) < 3:
        await callback.answer("⚠️ Pilih minimal 3 minat/hobi ya!", show_alert=True)
        return

    profile_service = ProfileService(session)
    gamification_service = GamificationService(session)
    user_service = UserService(session)

    await profile_service.update_interests(callback.from_user.id, list(selected))
    await gamification_service.award_profile_step_exp(callback.from_user.id)
    await user_service.update_onboarding_step(callback.from_user.id, "PREFERENCES")

    await state.set_state(OnboardingFSM.PREFERENCES)
    keyboard = get_gender_pref_keyboard()
    await callback.message.edit_text(ONBOARD_PREFERENCES_PROMPT, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(OnboardingFSM.PREFERENCES, F.data.startswith("pref_gender:"))
async def save_gender_preference(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    """Save gender search preferences & complete onboarding."""
    gender_choice = callback.data.split(":", 1)[1]
    if gender_choice == "ALL":
        pref_genders = ["MALE", "FEMALE", "NON_BINARY"]
    else:
        pref_genders = [gender_choice]

    profile_service = ProfileService(session)
    gamification_service = GamificationService(session)
    user_service = UserService(session)

    await profile_service.update_preferences(
        user_id=callback.from_user.id,
        age_min=18,
        age_max=35,
        gender_pref=pref_genders,
    )

    # Award final onboarding step EXP and complete status
    user, leveled_up, new_level = await gamification_service.award_profile_step_exp(callback.from_user.id)
    await user_service.update_onboarding_step(callback.from_user.id, "COMPLETE")

    await state.clear()
    tier = get_tier_name(user.level)

    await callback.message.edit_text(ONBOARD_COMPLETE.format(tier=tier))
    if leveled_up:
        await callback.message.answer(LEVEL_UP.format(level=new_level, tier=tier))
    await callback.message.answer("Gunakan menu utama di bawah untuk menjelajah:", reply_markup=get_main_menu_keyboard())
    await callback.answer()