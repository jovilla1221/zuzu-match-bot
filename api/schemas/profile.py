from typing import List, Optional
from pydantic import BaseModel, Field


class ProfileResponse(BaseModel):
    user_id: int
    display_name: Optional[str] = None
    username: Optional[str] = None
    level: int
    exp: int
    tier: str
    spark: int
    streak: int
    bio: Optional[str] = None
    interests: List[str] = Field(default_factory=list)
    completeness_score: int
    badges: List[str] = Field(default_factory=list)
    photo_file_ids: List[str] = Field(default_factory=list)


class UpdateBioRequest(BaseModel):
    init_data: str = Field(..., description="Telegram WebApp initData string for authentication")
    bio: str = Field(..., min_length=10, max_length=500, description="User bio text")


class UpdateInterestsRequest(BaseModel):
    init_data: str = Field(..., description="Telegram WebApp initData string for authentication")
    interests: List[str] = Field(..., min_length=3, max_length=15, description="List of interest tags")


class UpdatePreferencesRequest(BaseModel):
    init_data: str = Field(..., description="Telegram WebApp initData string for authentication")
    age_min: int = Field(default=18, ge=18, le=100)
    age_max: int = Field(default=35, ge=18, le=100)
    radius_km: int = Field(default=50, ge=1, le=500)
    gender_pref: List[str] = Field(default=["MALE", "FEMALE"])
