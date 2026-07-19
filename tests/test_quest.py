import pytest
from services.quest_service import QuestService
from services.user_service import UserService


@pytest.mark.asyncio
async def test_quest_creation_and_completion(async_session):
    user_service = UserService(async_session)
    user = await user_service.get_or_create_user(telegram_id=555444, username="quest_user")

    quest_service = QuestService(async_session)
    quest, candidates = await quest_service.get_or_create_daily_quest(555444)

    assert quest.user_id == 555444
    assert quest.completed is False
    initial_exp = user.exp
    initial_streak = user.streak

    # Record evaluation until total candidates
    total = len(quest.candidates) or 1
    completed = False
    for _ in range(total):
        completed = await quest_service.record_evaluation(555444)

    assert completed is True
    assert user.exp == initial_exp + 30
    assert user.streak == initial_streak + 1
