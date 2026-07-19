import pytest
from core.matching import compute_cosine_similarity, calculate_compatibility_score
from services.matching_service import MatchingService
from models.user import User
from models.profile import Profile


def test_cosine_similarity():
    tags1 = ["Gaming 🎮", "Coffee ☕", "Music 🎵"]
    tags2 = ["Coffee ☕", "Music 🎵", "Travel ✈️"]
    
    # Common: Coffee, Music (2 items out of 4 unique: Gaming, Coffee, Music, Travel)
    # Cosine = 2 / (sqrt(3) * sqrt(3)) = 2/3 = 0.6667
    sim = compute_cosine_similarity(tags1, tags2)
    assert pytest.approx(sim, 0.01) == 0.667

    # Disjoint tags
    assert compute_cosine_similarity(["Anime 🌸"], ["Hiking 🏔️"]) == 0.0
    
    # Identical tags
    assert compute_cosine_similarity(["Coffee ☕"], ["Coffee ☕"]) == 1.0


def test_compatibility_score():
    tags1 = ["Gaming 🎮", "Coffee ☕"]
    tags2 = ["Gaming 🎮", "Coffee ☕"]
    
    # Identical tags & same age => 100% compatibility
    score = calculate_compatibility_score(
        user_tags=tags1, candidate_tags=tags2, user_age=25, candidate_age=25
    )
    assert score == 100.0


@pytest.mark.asyncio
async def test_candidate_matching_service(async_session):
    # Seed 2 test users
    u1 = User(telegram_id=111, username="u1", level=1)
    p1 = Profile(user_id=111, gender="MALE", age=25, interests=["Gaming 🎮", "Coffee ☕"])

    u2 = User(telegram_id=222, username="u2", level=1)
    p2 = Profile(user_id=222, gender="FEMALE", age=24, interests=["Gaming 🎮", "Music 🎵"])

    async_session.add_all([u1, p1, u2, p2])
    await async_session.commit()

    matching_service = MatchingService(async_session)
    candidates = await matching_service.get_candidate_matches(user_id=111, limit=5)

    assert len(candidates) == 1
    cand_user, cand_prof, score = candidates[0]
    assert cand_user.telegram_id == 222
    assert score > 0.0
