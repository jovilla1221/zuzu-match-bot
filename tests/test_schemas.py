import pytest
from pydantic import ValidationError
from core.security import verify_telegram_init_data
from api.schemas.profile import UpdateBioRequest, UpdateInterestsRequest


def test_telegram_init_data_verification():
    # Invalid token or empty hash should fail
    assert verify_telegram_init_data("", "token") is False
    assert verify_telegram_init_data("user=%7B%22id%22%3A12345%7D&hash=invalidhash", "token") is False


def test_update_bio_schema_validation():
    # Valid payload
    req = UpdateBioRequest(init_data="dummy_init_data", bio="Halo! Saya dev yang suka gaming dan ngopi ☕")
    assert req.bio == "Halo! Saya dev yang suka gaming dan ngopi ☕"

    # Too short bio (<10 chars) should raise ValidationError
    with pytest.raises(ValidationError):
        UpdateBioRequest(init_data="dummy", bio="Pendek")


def test_update_interests_schema_validation():
    # Valid payload (>=3 items)
    req = UpdateInterestsRequest(init_data="dummy", interests=["Gaming 🎮", "Music 🎵", "Coffee ☕"])
    assert len(req.interests) == 3

    # Less than 3 items should fail
    with pytest.raises(ValidationError):
        UpdateInterestsRequest(init_data="dummy", interests=["Gaming 🎮"])
