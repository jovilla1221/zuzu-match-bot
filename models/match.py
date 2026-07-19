import enum
from sqlalchemy import BigInteger, Enum as SQLEnum, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin


class MatchStatusEnum(str, enum.Enum):
    ACTIVE = "ACTIVE"
    UNMATCHED = "UNMATCHED"


class Match(Base, TimestampMixin):
    """Mutual match record between two users."""

    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_a: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), index=True, nullable=False)
    user_b: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), index=True, nullable=False)
    status: Mapped[MatchStatusEnum] = mapped_column(
        SQLEnum(MatchStatusEnum), default=MatchStatusEnum.ACTIVE, nullable=False
    )
    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    compatibility_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
