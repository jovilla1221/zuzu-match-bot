import pytest
from services.user_service import UserService
from services.profile_service import ProfileService
from services.matching_service import MatchingService


@pytest.mark.asyncio
async def test_search_candidates_by_tag(async_session):
    user_service = UserService(async_session)
    profile_service = ProfileService(async_session)
    matching_service = MatchingService(async_session)

    # User 1
    u1 = await user_service.get_or_create_user(telegram_id=501, username="seeker")
    p1 = await profile_service.get_profile(501)
    await profile_service.update_interests(501, ["Coffee ☕", "Gaming 🎮"])

    # Candidate 1 (matches Coffee)
    u2 = await user_service.get_or_create_user(telegram_id=502, username="coffee_lover")
    p2 = await profile_service.get_profile(502)
    p2.gender = "FEMALE"
    await profile_service.update_interests(502, ["Coffee ☕", "Art 🎨"])

    # Candidate 2 (matches Gaming)
    u3 = await user_service.get_or_create_user(telegram_id=503, username="gamer_girl")
    p3 = await profile_service.get_profile(503)
    p3.gender = "FEMALE"
    await profile_service.update_interests(503, ["Gaming 🎮", "Music 🎵"])

    await async_session.commit()

    # Search by Coffee
    coffee_matches = await matching_service.search_candidates_by_tag(501, "Coffee ☕")
    assert len(coffee_matches) == 1
    assert coffee_matches[0][0].telegram_id == 502


@pytest.mark.asyncio
async def test_search_candidates_by_keyword(async_session):
    user_service = UserService(async_session)
    profile_service = ProfileService(async_session)
    matching_service = MatchingService(async_session)

    u1 = await user_service.get_or_create_user(telegram_id=601, username="searcher")
    
    u2 = await user_service.get_or_create_user(telegram_id=602, username="indie_musician")
    p2 = await profile_service.get_profile(602)
    await profile_service.update_bio(602, "Guitarist in an indie rock band")
    await profile_service.update_interests(602, ["Music 🎵"])

    await async_session.commit()

    # Keyword match in bio or username
    kw_matches = await matching_service.search_candidates_by_keyword(601, "indie")
    assert len(kw_matches) == 1
    assert kw_matches[0][0].telegram_id == 602
