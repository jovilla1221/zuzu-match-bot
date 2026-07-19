from typing import Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from core.exp import get_level_for_exp, get_tier_name, EXP_PROFILE_STEP


class GamificationService:
    """Business logic for awarding EXP, triggering level ups, and Spark management."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_exp(self, user_id: int, amount: int) -> Tuple[User, bool, int]:
        """
        Awards EXP to user.
        Returns: (user, leveled_up: bool, new_level: int)
        """
        stmt = select(User).where(User.telegram_id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"User with telegram_id {user_id} not found.")

        old_level = user.level
        user.exp += amount
        new_level = get_level_for_exp(user.exp)
        
        leveled_up = new_level > old_level
        if leveled_up:
            user.level = new_level
            # Award bonus Sparks for level up (+5 per level)
            level_diff = new_level - old_level
            user.spark += level_diff * 5

        await self.session.commit()
        return user, leveled_up, new_level

    async def award_profile_step_exp(self, user_id: int) -> Tuple[User, bool, int]:
        """Reward EXP for completing a profile onboarding step."""
        return await self.add_exp(user_id, EXP_PROFILE_STEP)

    async def add_sparks(self, user_id: int, amount: int) -> User:
        """Add virtual currency Sparks to user balance."""
        stmt = select(User).where(User.telegram_id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            user.spark += amount
            await self.session.commit()
        return user
