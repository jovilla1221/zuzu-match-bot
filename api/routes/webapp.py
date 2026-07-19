from urllib.parse import parse_qsl, unquote
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import get_db_session
from core.security import verify_telegram_init_data
from core.exp import get_tier_name
from services.user_service import UserService
from services.profile_service import ProfileService
from services.gamification_service import GamificationService
from api.schemas.profile import (
    ProfileResponse,
    UpdateBioRequest,
    UpdateInterestsRequest,
    UpdatePreferencesRequest,
)

router = APIRouter(prefix="/webapp", tags=["Telegram Web App"])


def extract_user_id_from_init_data(init_data: str) -> int:
    """Validate Telegram WebApp initData HMAC signature and parse user ID.
    ALWAYS enforces signature validation — no DEBUG bypass.
    """
    if not verify_telegram_init_data(init_data, settings.BOT_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram initData authentication signature.",
        )

    try:
        parsed = dict(parse_qsl(init_data, keep_blank_values=True))
        user_json_str = unquote(parsed.get("user", "{}"))
        user_dict = json.loads(user_json_str)
        user_id = user_dict.get("id")
        if not user_id:
            raise ValueError("user id missing in initData payload")
        return int(user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not parse user information from initData.",
        )


@router.get("/profile/me", response_model=ProfileResponse)
async def get_my_profile(init_data: str, session: AsyncSession = Depends(get_db_session)):
    """Fetch current authenticated user profile for Mini App rendering."""
    user_id = extract_user_id_from_init_data(init_data)
    
    user_service = UserService(session)
    profile_service = ProfileService(session)

    user = await user_service.get_by_telegram_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found. Run /start in bot.")

    profile = await profile_service.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile details missing.")

    tier = get_tier_name(user.level)

    return ProfileResponse(
        user_id=user.telegram_id,
        display_name=profile.display_name or f"User_{user.telegram_id % 10000}",
        username=user.username,
        level=user.level,
        exp=user.exp,
        tier=tier,
        spark=user.spark,
        streak=user.streak,
        bio=profile.bio,
        interests=profile.interests,
        completeness_score=profile.completeness_score,
        badges=profile.badges,
        photo_file_ids=profile.photo_file_ids,
    )


@router.post("/profile/bio", response_model=ProfileResponse)
async def update_profile_bio(payload: UpdateBioRequest, session: AsyncSession = Depends(get_db_session)):
    """Save user bio from Mini App and award EXP."""
    user_id = extract_user_id_from_init_data(payload.init_data)
    
    profile_service = ProfileService(session)
    gamification_service = GamificationService(session)
    user_service = UserService(session)

    await profile_service.update_bio(user_id, payload.bio)
    await gamification_service.award_profile_step_exp(user_id)

    return await get_my_profile(init_data=payload.init_data, session=session)


@router.post("/profile/interests", response_model=ProfileResponse)
async def update_profile_interests(
    payload: UpdateInterestsRequest, session: AsyncSession = Depends(get_db_session)
):
    """Save user interest tags from Mini App and award EXP."""
    user_id = extract_user_id_from_init_data(payload.init_data)

    profile_service = ProfileService(session)
    gamification_service = GamificationService(session)

    await profile_service.update_interests(user_id, payload.interests)
    await gamification_service.award_profile_step_exp(user_id)

    return await get_my_profile(init_data=payload.init_data, session=session)


@router.post("/profile/preferences", response_model=ProfileResponse)
async def update_profile_preferences(
    payload: UpdatePreferencesRequest, session: AsyncSession = Depends(get_db_session)
):
    """Save search preferences from Mini App and award EXP."""
    user_id = extract_user_id_from_init_data(payload.init_data)

    profile_service = ProfileService(session)
    gamification_service = GamificationService(session)

    await profile_service.update_preferences(
        user_id=user_id,
        age_min=payload.age_min,
        age_max=payload.age_max,
        radius_km=payload.radius_km,
        gender_pref=payload.gender_pref,
    )
    await gamification_service.award_profile_step_exp(user_id)

    return await get_my_profile(init_data=payload.init_data, session=session)
