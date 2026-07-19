import pytest
from services.chat_service import ChatService
from services.user_service import UserService
from services.profile_service import ProfileService
from models.interaction import ActionEnum


@pytest.mark.asyncio
async def test_mutual_match_and_ice_breakers(async_session):
    user_service = UserService(async_session)
    profile_service = ProfileService(async_session)
    chat_service = ChatService(async_session)

    # Create 2 users with matching interest
    u1 = await user_service.get_or_create_user(telegram_id=301, username="user1")
    u2 = await user_service.get_or_create_user(telegram_id=302, username="user2")

    await profile_service.update_interests(301, ["Coffee ☕", "Gaming 🎮"])
    await profile_service.update_interests(302, ["Coffee ☕", "Music 🎵"])

    # User 1 likes User 2
    is_mutual1, match1, ib1 = await chat_service.record_interaction(301, 302, ActionEnum.LIKE)
    assert is_mutual1 is False
    assert match1 is None

    # User 2 likes User 1 (Mutual Match Event!)
    is_mutual2, match2, ib2 = await chat_service.record_interaction(302, 301, ActionEnum.LIKE)
    assert is_mutual2 is True
    assert match2 is not None
    assert len(ib2) == 3
    assert isinstance(ib2[0], str) and len(ib2[0]) > 5

    # Verify both received +15 EXP
    assert u1.exp > 0
    assert u2.exp > 0
