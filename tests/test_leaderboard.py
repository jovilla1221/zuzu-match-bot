import pytest
from services.user_service import UserService
from services.leaderboard_service import LeaderboardService
from services.shop_service import ShopService


@pytest.mark.asyncio
async def test_leaderboard_rankings(async_session):
    user_service = UserService(async_session)
    lb_service = LeaderboardService(async_session)

    u1 = await user_service.get_or_create_user(telegram_id=801, username="top_user")
    u2 = await user_service.get_or_create_user(telegram_id=802, username="mid_user")

    u1.exp = 500
    u1.level = 5
    u1.streak = 7

    u2.exp = 200
    u2.level = 3
    u2.streak = 2

    await async_session.commit()

    active_lb = await lb_service.get_most_active_leaderboard(limit=5)
    assert len(active_lb) == 2
    assert active_lb[0][0].telegram_id == 801  # Top user first


@pytest.mark.asyncio
async def test_shop_streak_freeze_purchase(async_session):
    user_service = UserService(async_session)
    shop_service = ShopService(async_session)

    user = await user_service.get_or_create_user(telegram_id=901, username="rich_user")
    user.spark = 10
    await async_session.commit()

    success, msg = await shop_service.buy_streak_freeze(901)
    assert success is True
    assert user.spark == 5

    # Insufficient sparks check
    user.spark = 2
    await async_session.commit()
    fail_success, fail_msg = await shop_service.buy_streak_freeze(901)
    assert fail_success is False
    assert "tidak cukup" in fail_msg
