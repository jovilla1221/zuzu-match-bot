import pytest
from services.user_service import UserService
from services.profile_service import ProfileService
from services.gamification_service import GamificationService


@pytest.mark.asyncio
async def test_user_creation_and_retrieval(async_session):
    user_service = UserService(async_session)
    user = await user_service.get_or_create_user(telegram_id=999111, username="testuser")

    assert user.telegram_id == 999111
    assert user.username == "testuser"
    assert user.onboarding_step == "START"
    assert user.level == 0
    assert user.exp == 0
    assert user.spark == 10


@pytest.mark.asyncio
async def test_profile_completeness_and_updates(async_session):
    user_service = UserService(async_session)
    profile_service = ProfileService(async_session)

    await user_service.get_or_create_user(telegram_id=888222, username="profileuser")
    
    # Update bio
    profile = await profile_service.update_bio(888222, "Bio baru dengan lebih dari sepuluh karakter!")
    assert profile.bio == "Bio baru dengan lebih dari sepuluh karakter!"
    assert profile.completeness_score >= 25

    # Update interests
    profile = await profile_service.update_interests(888222, ["Gaming 🎮", "Music 🎵", "Coffee ☕"])
    assert len(profile.interests) == 3
    assert profile.completeness_score >= 50


@pytest.mark.asyncio
async def test_gamification_exp_and_level_up(async_session):
    user_service = UserService(async_session)
    gamification_service = GamificationService(async_session)

    await user_service.get_or_create_user(telegram_id=777333, username="gamer")

    # Award 60 EXP (enough to trigger level 1, threshold = 50)
    user, leveled_up, new_level = await gamification_service.add_exp(777333, 60)
    
    assert user.exp == 60
    assert leveled_up is True
    assert new_level == 1
    assert user.level == 1
    assert user.spark == 15  # 10 default + 5 bonus for level up
