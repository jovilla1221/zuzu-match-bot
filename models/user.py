from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from models.profile import Profile


class User(Base, TimestampMixin):
    """Core user identity and gamification record."""

    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    photo_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    exp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    spark: Mapped[int] = mapped_column(Integer, default=10, nullable=False)  # default 10 sparks
    streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    onboarding_step: Mapped[str] = mapped_column(String(32), default="START", nullable=False)

    # Relationship to detailed profile
    profile: Mapped[Optional["Profile"]] = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
