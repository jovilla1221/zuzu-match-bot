from datetime import date
from typing import List, Dict, Any
from sqlalchemy import BigInteger, Boolean, Date, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin

JSON_TYPE = JSON().with_variant(JSONB, "postgresql")


class Quest(Base, TimestampMixin):
    """Daily quest log tracking candidates presented to a user per day."""

    __tablename__ = "quests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), index=True, nullable=False)
    quest_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    candidates: Mapped[List[int]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON_TYPE, default=dict, nullable=False)
