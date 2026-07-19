import pytest
from core.exp import get_level_for_exp, get_tier_name, exp_progress_info, LEVEL_THRESHOLDS


def test_level_thresholds():
    assert get_level_for_exp(0) == 0
    assert get_level_for_exp(49) == 0
    assert get_level_for_exp(50) == 1
    assert get_level_for_exp(120) == 2
    assert get_level_for_exp(2720) == 15
    assert get_level_for_exp(9920) == 30


def test_level_thresholds_above_30():
    # L30 = 9920. Each level above 30 requires +700 EXP
    assert get_level_for_exp(9920 + 700) == 31
    assert get_level_for_exp(9920 + 1400) == 32


def test_tier_names():
    assert get_tier_name(1) == "Newbie 🌱"
    assert get_tier_name(5) == "Newbie 🌱"
    assert get_tier_name(6) == "Explorer 🚀"
    assert get_tier_name(15) == "Explorer 🚀"
    assert get_tier_name(16) == "Charmer ✨"
    assert get_tier_name(30) == "Charmer ✨"
    assert get_tier_name(31) == "Icon ⭐"


def test_exp_progress_info():
    current_level, exp_in_lvl, req_in_lvl, percentage = exp_progress_info(80)
    assert current_level == 1
    assert exp_in_lvl == 30  # 80 - 50 = 30
    assert req_in_lvl == 70  # L2(120) - L1(50) = 70
    assert pytest.approx(percentage, 0.01) == (30 / 70)
