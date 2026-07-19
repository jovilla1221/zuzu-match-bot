from typing import List, Dict, Any, Optional, TYPE_CHECKING
from sqlalchemy import BigInteger, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from models.user import User

# Cross-dialect JSON type: PostgreSQL JSONB in prod, JSON in SQLite/dev
JSON_TYPE = JSON().with_variant(JSONB, "postgresql")


class Profile(Base, TimestampMixin):
    """Detailed user dating profile and preferences."""

    __tablename__ = "profiles"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), primary_key=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo_file_ids: Mapped[List[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    selfie_file_id: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    location_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    interests: Mapped[List[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    preferences: Mapped[Dict[str, Any]] = mapped_column(
        JSON_TYPE,
        default=lambda: {"age_min": 18, "age_max": 35, "radius_km": 50, "gender_pref": ["MALE", "FEMALE"]},
        nullable=False,
    )
    completeness_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    badges: Mapped[List[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)

    # Back relationship to User
    user: Mapped["User"] = relationship("User", back_populates="profile")
