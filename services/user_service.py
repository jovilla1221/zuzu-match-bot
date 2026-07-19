from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.profile import Profile


class UserService:
    """Business logic for User identity & account management."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Fetch user by Telegram ID."""
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create_user(self, telegram_id: int, username: Optional[str] = None) -> User:
        """Get existing user or create a new one with initial profile."""
        user = await self.get_by_telegram_id(telegram_id)
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                onboarding_step="START",
                last_active_at=datetime.now(timezone.utc),
            )
            self.session.add(user)
            await self.session.flush()

            # Initialize empty profile linked to user
            profile = Profile(
                user_id=telegram_id,
                interests=[],
                photo_file_ids=[],
                badges=["Verified Newbie 🌱"],
            )
            self.session.add(profile)
            await self.session.commit()
        else:
            # Update username and last active timestamp
            if username and user.username != username:
                user.username = username
            user.last_active_at = datetime.now(timezone.utc)
            await self.session.commit()

        return user

    async def update_onboarding_step(self, telegram_id: int, step: str) -> None:
        """Update user's onboarding progress step."""
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            user.onboarding_step = step
            await self.session.commit()
