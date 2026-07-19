from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Build persistent main menu reply keyboard with rich emoticon buttons."""
    keyboard = [
        [
            KeyboardButton(text="🎯 Quest Harian"),
            KeyboardButton(text="🔍 Cari Pasangan"),
        ],
        [
            KeyboardButton(text="👤 Profil Saya"),
            KeyboardButton(text="✨ AI Bio Assistant"),
        ],
        [
            KeyboardButton(text="💬 Match & Chat"),
            KeyboardButton(text="🏆 Leaderboard"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
