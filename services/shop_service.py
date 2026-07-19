from typing import Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.profile import Profile


class ShopService:
    """Business logic for spending Sparks on streak freezes and profile boosts."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def buy_streak_freeze(self, user_id: int) -> Tuple[bool, str]:
        """
        Deducts 5 Sparks to purchase a Streak Freeze item and add badge.
        Returns (success: bool, message: str)
        """
        user_stmt = select(User).where(User.telegram_id == user_id)
        u_res = await self.session.execute(user_stmt)
        user = u_res.scalar_one_or_none()

        prof_stmt = select(Profile).where(Profile.user_id == user_id)
        p_res = await self.session.execute(prof_stmt)
        profile = p_res.scalar_one_or_none()

        if not user or not profile:
            return False, "Pengguna tidak ditemukan."

        if user.spark < 5:
            return False, f"Spark kamu tidak cukup (Butuh 5 ⚡, saldo kamu: {user.spark} ⚡)."

        user.spark -= 5
        if "Streak Freeze ❄️" not in profile.badges:
            profile.badges = list(profile.badges) + ["Streak Freeze ❄️"]

        await self.session.commit()
        return True, "Berhasil membeli **Streak Freeze ❄️**! Streak harian kamu aman saat absen 1 hari."

    async def spend_spark(self, user_id: int, amount: int) -> Tuple[bool, str]:
        """Deducts Spark balance for superlikes or boosts."""
        user_stmt = select(User).where(User.telegram_id == user_id)
        u_res = await self.session.execute(user_stmt)
        user = u_res.scalar_one_or_none()

        if not user:
            return False, "Pengguna tidak ditemukan."

        if user.spark < amount:
            return False, f"Saldo Spark kurang (Butuh {amount} ⚡, saldo: {user.spark} ⚡)."

        user.spark -= amount
        await self.session.commit()
        return True, "Berhasil menggunakan Spark!"
