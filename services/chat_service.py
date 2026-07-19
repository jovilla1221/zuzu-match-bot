import random
from typing import Tuple, Optional, List
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from models.interaction import Interaction, ActionEnum
from models.match import Match, MatchStatusEnum
from models.profile import Profile
from models.user import User
from services.gamification_service import GamificationService

ICE_BREAKER_TEMPLATES = [
    "Kalian sama-sama suka {interest}! Apa rekomendasi terbaikmu buat pemula? ☕",
    "Sama-sama tertarik dengan {interest}! Kalau punya kesempatan ke sana besok, mau ngapain? ✨",
    "Topik seru: {interest}! Dari 1 sampai 10, seberapa obsesif kamu sama ini? 🍿",
]

SUPERLIKE_SPARK_COST = 1


class ChatService:
    """Business logic for interactions, mutual match creation, and chat relay messaging."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def record_interaction(
        self, user_id: int, target_id: int, action: ActionEnum, metadata: dict = None
    ) -> Tuple[bool, Optional[Match], List[str]]:
        """
        Record user decision (LIKE, PASS, SUPERLIKE).
        Returns (is_mutual_match, match_object, ice_breakers).
        Raises ValueError if user lacks Sparks for SUPERLIKE.
        """
        # ─── Spark deduction for SUPERLIKE ───
        if action == ActionEnum.SUPERLIKE:
            user_stmt = select(User).where(User.telegram_id == user_id)
            u_res = await self.session.execute(user_stmt)
            user = u_res.scalar_one_or_none()

            if not user:
                raise ValueError("User not found.")

            if user.spark < SUPERLIKE_SPARK_COST:
                raise ValueError(
                    f"Spark tidak cukup (butuh {SUPERLIKE_SPARK_COST} ⚡, "
                    f"saldo: {user.spark} ⚡)."
                )

            user.spark -= SUPERLIKE_SPARK_COST

        # ─── Record interaction ───
        interaction = Interaction(
            user_id=user_id,
            target_id=target_id,
            action=action,
            metadata_json=metadata or {},
        )
        self.session.add(interaction)
        await self.session.flush()

        if action in (ActionEnum.LIKE, ActionEnum.SUPERLIKE):
            # Check if target user previously liked source user
            check_stmt = select(Interaction).where(
                and_(
                    Interaction.user_id == target_id,
                    Interaction.target_id == user_id,
                    Interaction.action.in_([ActionEnum.LIKE, ActionEnum.SUPERLIKE]),
                )
            )
            res = await self.session.execute(check_stmt)
            opposite_like = res.scalar_one_or_none()

            if opposite_like:
                # Mutual Match Event!
                user_a = min(user_id, target_id)
                user_b = max(user_id, target_id)

                match = Match(user_a=user_a, user_b=user_b, status=MatchStatusEnum.ACTIVE)
                self.session.add(match)

                # Award +15 EXP to both users
                gamification = GamificationService(self.session)
                await gamification.add_exp(user_id, 15)
                await gamification.add_exp(target_id, 15)

                # Fetch user profiles and common interests for Gemini AI ice-breaker prompts
                u1_user = (await self.session.execute(select(User).where(User.telegram_id == user_id))).scalar_one_or_none()
                u2_user = (await self.session.execute(select(User).where(User.telegram_id == target_id))).scalar_one_or_none()

                u1_prof = (await self.session.execute(select(Profile).where(Profile.user_id == user_id))).scalar_one_or_none()
                u2_prof = (await self.session.execute(select(Profile).where(Profile.user_id == target_id))).scalar_one_or_none()

                common_interests = []
                if u1_prof and u2_prof and u1_prof.interests and u2_prof.interests:
                    common_interests = list(set(u1_prof.interests).intersection(set(u2_prof.interests)))

                from core.ai_service import GeminiAIService
                ai_service = GeminiAIService()

                user1_name = (u1_user.username or "Adventurer") if u1_user else "Adventurer"
                user2_name = (u2_user.username or "Adventurer") if u2_user else "Adventurer"

                ice_breakers = ai_service.generate_ai_ice_breakers(user1_name, user2_name, common_interests)

                await self.session.commit()
                return True, match, ice_breakers

        await self.session.commit()
        return False, None, []

    async def get_active_matches(self, user_id: int) -> List[Tuple[Match, User, Profile]]:
        """Fetch all active matches for a user."""
        stmt = (
            select(Match, User, Profile)
            .join(User, (User.telegram_id == Match.user_a) | (User.telegram_id == Match.user_b))
            .join(Profile, User.telegram_id == Profile.user_id)
            .where(
                and_(
                    Match.status == MatchStatusEnum.ACTIVE,
                    User.telegram_id != user_id,
                    (Match.user_a == user_id) | (Match.user_b == user_id),
                )
            )
        )
        res = await self.session.execute(stmt)
        return res.all()

    async def increment_message_counter(self, match_id: int) -> int:
        """Increment match message counter and return new count."""
        stmt = select(Match).where(Match.id == match_id)
        res = await self.session.execute(stmt)
        match = res.scalar_one_or_none()
        if match:
            match.message_count += 1
            await self.session.commit()
            return match.message_count
        return 0
