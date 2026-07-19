from typing import List, Tuple
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.profile import Profile
from core.exp import get_tier_name


class LeaderboardService:
    """Service for computing multi-category weekly rankings."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_most_active_leaderboard(self, limit: int = 10) -> List[Tuple[User, Profile, str]]:
        """Rank users by highest total EXP."""
        stmt = (
            select(User, Profile)
            .join(Profile, User.telegram_id == Profile.user_id)
            .order_by(desc(User.exp))
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        results = res.all()
        return [(u, p, get_tier_name(u.level)) for u, p in results]

    async def get_best_conversationalists(self, limit: int = 10) -> List[Tuple[User, Profile, str]]:
        """Rank users by streak count and chat activity."""
        stmt = (
            select(User, Profile)
            .join(Profile, User.telegram_id == Profile.user_id)
            .order_by(desc(User.streak), desc(User.exp))
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        results = res.all()
        return [(u, p, get_tier_name(u.level)) for u, p in results]

    async def get_rising_stars(self, limit: int = 10) -> List[Tuple[User, Profile, str]]:
        """Rank newer users by progress level."""
        stmt = (
            select(User, Profile)
            .join(Profile, User.telegram_id == Profile.user_id)
            .where(User.level >= 1)
            .order_by(desc(User.level), desc(User.exp))
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        results = res.all()
        return [(u, p, get_tier_name(u.level)) for u, p in results]
