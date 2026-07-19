import enum
from datetime import datetime
from typing import Dict, Any
from sqlalchemy import BigInteger, DateTime, Enum as SQLEnum, ForeignKey, Integer, func, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base

JSON_TYPE = JSON().with_variant(JSONB, "postgresql")


class ActionEnum(str, enum.Enum):
    LIKE = "LIKE"
    PASS = "PASS"
    SUPERLIKE = "SUPERLIKE"


class Interaction(Base):
    """Logs all user evaluation actions for recommendation algorithm training."""

    __tablename__ = "interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), index=True, nullable=False)
    target_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), index=True, nullable=False)
    action: Mapped[ActionEnum] = mapped_column(SQLEnum(ActionEnum), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON_TYPE, default=dict, nullable=False)
