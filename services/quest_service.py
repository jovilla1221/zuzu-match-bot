from datetime import date, timezone, datetime
from typing import Optional, List, Tuple
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.quest import Quest
from models.user import User
from models.profile import Profile
from services.matching_service import MatchingService
from services.gamification_service import GamificationService


class QuestService:
    """Manages daily candidate quests and quest completion reward pipeline."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_daily_quest(self, user_id: int) -> Tuple[Quest, List[Tuple[User, Profile, float]]]:
        """Fetch today's quest for user or generate a new candidate list."""
        today = date.today()
        stmt = select(Quest).where(and_(Quest.user_id == user_id, Quest.quest_date == today))
        res = await self.session.execute(stmt)
        quest = res.scalar_one_or_none()

        matching_service = MatchingService(self.session)
        scored_candidates = await matching_service.get_candidate_matches(user_id=user_id, limit=5)

        if not quest:
            cand_ids = [c[0].telegram_id for c in scored_candidates]
            quest = Quest(
                user_id=user_id,
                quest_date=today,
                candidates=cand_ids,
                completed=False,
                details={"evaluated_count": 0, "total_candidates": len(cand_ids)},
            )
            self.session.add(quest)
            await self.session.commit()

        return quest, scored_candidates

    async def record_evaluation(self, user_id: int) -> bool:
        """
        Increment evaluated candidate counter for today's quest.
        Returns True if quest was completed by this evaluation action.
        """
        today = date.today()
        stmt = select(Quest).where(and_(Quest.user_id == user_id, Quest.quest_date == today))
        res = await self.session.execute(stmt)
        quest = res.scalar_one_or_none()

        if quest and not quest.completed:
            evaluated = quest.details.get("evaluated_count", 0) + 1
            total = quest.details.get("total_candidates", 5)
            
            quest.details = {**quest.details, "evaluated_count": evaluated}
            
            if evaluated >= total:
                quest.completed = True
                
                # Award +30 EXP and increment streak for completing quest
                gamification = GamificationService(self.session)
                await gamification.add_exp(user_id, 30)

                user_stmt = select(User).where(User.telegram_id == user_id)
                u_res = await self.session.execute(user_stmt)
                user = u_res.scalar_one_or_none()
                if user:
                    user.streak += 1
                    
                await self.session.commit()
                return True

            await self.session.commit()

        return False
