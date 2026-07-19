from typing import Tuple, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.profile import Profile
from core.photo_verify import compute_photo_similarity_score, evaluate_nsfw_score
from services.gamification_service import GamificationService


class VerificationService:
    """Business logic for photo verification pipeline and admin review routing."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def verify_user_photos(
        self, user_id: int, profile_photo_id: str, selfie_photo_id: str
    ) -> Dict[str, Any]:
        """
        Runs NSFW filter and face matching pipeline.
        Returns dict containing status ("AUTO_VERIFIED", "PENDING_ADMIN_REVIEW", "REJECTED"),
        similarity_score, and nsfw_score.
        """
        nsfw_score = evaluate_nsfw_score(profile_photo_id)
        if nsfw_score > 0.7:
            return {
                "status": "REJECTED",
                "reason": "Foto tidak memenuhi standar komunitas (NSFW filter).",
                "similarity_score": 0.0,
                "nsfw_score": nsfw_score,
            }

        score = compute_photo_similarity_score(profile_photo_id, selfie_photo_id)
        
        stmt = select(User).where(User.telegram_id == user_id)
        res = await self.session.execute(stmt)
        user = res.scalar_one_or_none()

        profile_stmt = select(Profile).where(Profile.user_id == user_id)
        prof_res = await self.session.execute(profile_stmt)
        profile = prof_res.scalar_one_or_none()

        if profile:
            profile.selfie_file_id = selfie_photo_id

        if score >= 70.0:
            if user:
                user.photo_verified = True
            if profile and "Verified ✨" not in profile.badges:
                profile.badges = list(profile.badges) + ["Verified ✨"]
            
            gamification = GamificationService(self.session)
            await gamification.add_exp(user_id, 50)
            await self.session.commit()
            
            return {
                "status": "AUTO_VERIFIED",
                "similarity_score": score,
                "nsfw_score": nsfw_score,
            }
        elif score >= 50.0:
            await self.session.commit()
            return {
                "status": "PENDING_ADMIN_REVIEW",
                "similarity_score": score,
                "nsfw_score": nsfw_score,
            }
        else:
            await self.session.commit()
            return {
                "status": "REJECTED",
                "reason": "Foto selfie dan foto profil kurang cocok. Coba di tempat yang lebih terang ya!",
                "similarity_score": score,
                "nsfw_score": nsfw_score,
            }

    async def admin_approve(self, user_id: int) -> User:
        """Manually approve photo verification by admin."""
        stmt = select(User).where(User.telegram_id == user_id)
        res = await self.session.execute(stmt)
        user = res.scalar_one_or_none()
        
        profile_stmt = select(Profile).where(Profile.user_id == user_id)
        prof_res = await self.session.execute(profile_stmt)
        profile = prof_res.scalar_one_or_none()

        if user:
            user.photo_verified = True
        if profile and "Verified ✨" not in profile.badges:
            profile.badges = list(profile.badges) + ["Verified ✨"]
            
        gamification = GamificationService(self.session)
        await gamification.add_exp(user_id, 50)
        await self.session.commit()
        return user
