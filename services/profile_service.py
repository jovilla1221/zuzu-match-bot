from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.profile import Profile
from models.user import User


class ProfileService:
    """Business logic for Profile creation, completeness rating, and edits."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_profile(self, user_id: int) -> Optional[Profile]:
        """Fetch profile for given user_id."""
        stmt = select(Profile).where(Profile.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    def calculate_completeness(self, profile: Profile) -> int:
        """
        Calculates profile completeness percentage (0-100%).
        - Photos (>=1 photo): 30%
        - Bio (>=10 chars): 25%
        - Interests (>=3 tags): 25%
        - Preferences configured: 20%
        """
        score = 0
        if profile.photo_file_ids and len(profile.photo_file_ids) > 0:
            score += 30
        if profile.bio and len(profile.bio.strip()) >= 10:
            score += 25
        if profile.interests and len(profile.interests) >= 3:
            score += 25
        if profile.preferences and "age_min" in profile.preferences:
            score += 20
        return min(100, score)

    async def update_bio(self, user_id: int, bio: str) -> Profile:
        """Update bio and recalculate completeness."""
        profile = await self.get_profile(user_id)
        if profile:
            profile.bio = bio.strip()
            profile.completeness_score = self.calculate_completeness(profile)
            
            # Badge unlock check
            if len(profile.bio) >= 100 and "Storyteller 📖" not in profile.badges:
                profile.badges = list(profile.badges) + ["Storyteller 📖"]
                
            await self.session.commit()
        return profile

    async def update_display_name(self, user_id: int, display_name: str) -> Profile:
        """Update user custom display name."""
        profile = await self.get_profile(user_id)
        if profile:
            profile.display_name = display_name.strip()
            await self.session.commit()
        return profile

    async def update_gender(self, user_id: int, gender: str) -> Profile:
        """Update user gender."""
        profile = await self.get_profile(user_id)
        if profile:
            profile.gender = gender
            await self.session.commit()
        return profile

    async def update_interests(self, user_id: int, interests: List[str]) -> Profile:
        """Update interest tags and recalculate completeness."""
        profile = await self.get_profile(user_id)
        if profile:
            profile.interests = interests
            profile.completeness_score = self.calculate_completeness(profile)
            await self.session.commit()
        return profile

    async def add_photo(self, user_id: int, photo_file_id: str) -> Profile:
        """Add photo file_id to profile."""
        profile = await self.get_profile(user_id)
        if profile:
            photos = list(profile.photo_file_ids)
            if photo_file_id not in photos:
                photos.append(photo_file_id)
                profile.photo_file_ids = photos
                profile.completeness_score = self.calculate_completeness(profile)
                await self.session.commit()
        return profile

    async def update_preferences(
        self, user_id: int, age_min: int, age_max: int, gender_pref: List[str], radius_km: int = 50
    ) -> Profile:
        """Update search preferences."""
        profile = await self.get_profile(user_id)
        if profile:
            profile.preferences = {
                "age_min": age_min,
                "age_max": age_max,
                "gender_pref": gender_pref,
                "radius_km": radius_km,
            }
            profile.completeness_score = self.calculate_completeness(profile)
            await self.session.commit()
        return profile
