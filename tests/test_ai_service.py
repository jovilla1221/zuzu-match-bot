import pytest
from core.ai_service import GeminiAIService


def test_gemini_ai_ice_breakers_generation():
    ai = GeminiAIService()
    ice_breakers = ai.generate_ai_ice_breakers("Dinda", "Rangga", ["Coffee ☕", "Gaming 🎮"])
    
    assert isinstance(ice_breakers, list)
    assert len(ice_breakers) == 3
    assert all(isinstance(ib, str) and len(ib) > 5 for ib in ice_breakers)


def test_gemini_ai_bio_generation():
    ai = GeminiAIService()
    bio = ai.generate_ai_bio(["Coffee ☕", "Gaming 🎮"])
    
    assert isinstance(bio, str)
    assert len(bio) > 10
