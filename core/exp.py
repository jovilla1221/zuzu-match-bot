from typing import Tuple, Dict

# EXP Constants (from PRD §6.1)
EXP_PROFILE_STEP = 30
EXP_DAILY_QUEST_COMPLETE = 30
EXP_MUTUAL_MATCH = 15
EXP_QUICK_REPLY = 5
EXP_CHAT_MILESTONE_10 = 25
EXP_CHAT_MILESTONE_25 = 50
EXP_CHAT_MILESTONE_50 = 100
EXP_STREAK_7_DAYS_BONUS = 100

# Base cumulative EXP thresholds for levels 0..30
LEVEL_THRESHOLDS: Dict[int, int] = {
    0: 0,
    1: 50,
    2: 120,
    3: 200,
    4: 300,
    5: 420,
    6: 560,
    7: 720,
    8: 900,
    9: 1100,
    10: 1320,
    11: 1560,
    12: 1820,
    13: 2100,
    14: 2400,
    15: 2720,
    16: 3060,
    17: 3420,
    18: 3800,
    19: 4200,
    20: 4620,
    21: 5060,
    22: 5520,
    23: 6000,
    24: 6500,
    25: 7020,
    26: 7560,
    27: 8120,
    28: 8700,
    29: 9300,
    30: 9920,
}


def get_level_for_exp(exp: int) -> int:
    """Calculate current level based on total cumulative EXP."""
    if exp < 0:
        return 0
    
    current_level = 0
    for level in range(0, 31):
        if exp >= LEVEL_THRESHOLDS[level]:
            current_level = level
        else:
            break
            
    # For levels above 30, each level requires +700 EXP
    if exp > LEVEL_THRESHOLDS[30]:
        extra_exp = exp - LEVEL_THRESHOLDS[30]
        extra_levels = extra_exp // 700
        current_level = 30 + extra_levels
        
    return current_level


def get_tier_name(level: int) -> str:
    """Return tier name based on level (PRD §6.1)."""
    if level <= 5:
        return "Newbie 🌱"
    elif level <= 15:
        return "Explorer 🚀"
    elif level <= 30:
        return "Charmer ✨"
    else:
        return "Icon ⭐"


def exp_progress_info(exp: int) -> Tuple[int, int, int, float]:
    """
    Returns (current_level, exp_in_level, required_in_level, percentage)
    for rendering profile progress bar.
    """
    current_level = get_level_for_exp(exp)
    
    if current_level < 30:
        base_exp = LEVEL_THRESHOLDS[current_level]
        next_exp = LEVEL_THRESHOLDS[current_level + 1]
    else:
        extra_levels = current_level - 30
        base_exp = LEVEL_THRESHOLDS[30] + (extra_levels * 700)
        next_exp = base_exp + 700

    exp_in_level = exp - base_exp
    required_in_level = next_exp - base_exp
    percentage = min(1.0, max(0.0, exp_in_level / required_in_level)) if required_in_level > 0 else 1.0

    return current_level, exp_in_level, required_in_level, percentage
