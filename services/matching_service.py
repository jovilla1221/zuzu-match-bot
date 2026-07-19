from typing import List, Tuple
from datetime import datetime, date, timezone
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.profile import Profile
from models.interaction import Interaction
from core.matching import calculate_compatibility_score


class MatchingService:
    """Service responsible for finding and scoring daily candidate matches."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_valid_candidates(self, user_id: int, user_profile: Profile) -> List[Tuple[User, Profile]]:
        """Helper to fetch and pre-filter candidates by mutual gender preference."""
        interacted_stmt = select(Interaction.target_id).where(Interaction.user_id == user_id)
        interacted_res = await self.session.execute(interacted_stmt)
        interacted_ids = set(interacted_res.scalars().all())
        interacted_ids.add(user_id)

        pref_genders = user_profile.preferences.get("gender_pref", [])

        # SQL Filter: Candidate's gender must match user's preference
        cand_stmt = (
            select(User, Profile)
            .join(Profile, User.telegram_id == Profile.user_id)
            .where(
                and_(
                    User.telegram_id.not_in(list(interacted_ids)),
                    Profile.gender.in_(pref_genders) if pref_genders else True,
                )
            )
        )
        cand_res = await self.session.execute(cand_stmt)
        candidates = cand_res.all()

        valid_candidates = []
        user_gender = user_profile.gender

        for u_row, p_row in candidates:
            # Python Memory Filter: Mutual logic
            if user_gender:
                cand_pref_genders = p_row.preferences.get("gender_pref", [])
                if cand_pref_genders and user_gender not in cand_pref_genders:
                    continue  # Skip because candidate doesn't want user's gender
            
            valid_candidates.append((u_row, p_row))

        return valid_candidates

    async def get_candidate_matches(
        self, user_id: int, limit: int = 5
    ) -> List[Tuple[User, Profile, float]]:
        """Fetches best candidate matches for user_id ranked by compatibility score."""
        user_prof_stmt = select(Profile).where(Profile.user_id == user_id)
        u_prof_res = await self.session.execute(user_prof_stmt)
        user_profile = u_prof_res.scalar_one_or_none()

        if not user_profile:
            return []

        candidates = await self._get_valid_candidates(user_id, user_profile)

        scored_candidates = []
        user_age = user_profile.age or 22

        for user_row, prof_row in candidates:
            cand_age = prof_row.age or 22
            score = calculate_compatibility_score(
                user_tags=user_profile.interests,
                candidate_tags=prof_row.interests,
                user_age=user_age,
                candidate_age=cand_age,
            )
            scored_candidates.append((user_row, prof_row, score))

        import random
        # Langsung acak semua kandidat yang valid
        random.shuffle(scored_candidates)
        
        # Kembalikan sejumlah limit yang diminta
        return scored_candidates[:limit]

    async def search_candidates_by_tag(
        self, user_id: int, tag: str, limit: int = 5
    ) -> List[Tuple[User, Profile, float]]:
        """Find candidates sharing a specific interest tag."""
        user_prof_stmt = select(Profile).where(Profile.user_id == user_id)
        u_prof_res = await self.session.execute(user_prof_stmt)
        user_profile = u_prof_res.scalar_one_or_none()

        if not user_profile:
            return []

        candidates = await self._get_valid_candidates(user_id, user_profile)

        user_tags = user_profile.interests or []
        user_age = user_profile.age or 22
        clean_tag = tag.split()[0].lower()

        matching_results = []
        for u_row, p_row in candidates:
            cand_interests = p_row.interests or []
            if any(clean_tag in (t.lower()) for t in cand_interests):
                score = calculate_compatibility_score(
                    user_tags=user_tags,
                    candidate_tags=cand_interests,
                    user_age=user_age,
                    candidate_age=p_row.age or 22,
                )
                matching_results.append((u_row, p_row, score))

        matching_results.sort(key=lambda x: x[2], reverse=True)
        return matching_results[:limit]

    async def search_candidates_by_keyword(
        self, user_id: int, keyword: str, limit: int = 5
    ) -> List[Tuple[User, Profile, float]]:
        """Search candidates by username, bio text, or interest tags."""
        user_prof_stmt = select(Profile).where(Profile.user_id == user_id)
        u_prof_res = await self.session.execute(user_prof_stmt)
        user_profile = u_prof_res.scalar_one_or_none()

        if not user_profile:
            return []

        candidates = await self._get_valid_candidates(user_id, user_profile)

        user_tags = user_profile.interests or []
        user_age = user_profile.age or 22
        kw = keyword.lower().strip()

        matching_results = []
        for u_row, p_row in candidates:
            username = (u_row.username or "").lower()
            bio = (p_row.bio or "").lower()
            cand_tags = " ".join(p_row.interests or []).lower()

            if kw in username or kw in bio or kw in cand_tags:
                score = calculate_compatibility_score(
                    user_tags=user_tags,
                    candidate_tags=p_row.interests or [],
                    user_age=user_age,
                    candidate_age=p_row.age or 22,
                )
                matching_results.append((u_row, p_row, score))

        matching_results.sort(key=lambda x: x[2], reverse=True)
        return matching_results[:limit]
