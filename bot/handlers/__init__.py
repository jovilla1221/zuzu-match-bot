from bot.handlers.start import router as start_router
from bot.handlers.profile import router as profile_router
from bot.handlers.quest import router as quest_router
from bot.handlers.chat import router as chat_router
from bot.handlers.admin import router as admin_router
from bot.handlers.leaderboard import router as leaderboard_router
from bot.handlers.search import router as search_router

__all__ = [
    "start_router",
    "profile_router",
    "quest_router",
    "chat_router",
    "admin_router",
    "leaderboard_router",
    "search_router",
]
