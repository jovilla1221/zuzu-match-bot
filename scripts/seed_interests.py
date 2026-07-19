import asyncio
from loguru import logger
from core.database import async_session_factory
from models.user import User
from models.profile import Profile
from models.base import Base
from core.database import engine

SAMPLE_USERS = [
    {
        "telegram_id": 1001,
        "username": "dinda_art",
        "display_name": "Dinda Kusuma 🎨",
        "bio": "Content creator & coffee lover ☕ Suka keliling museum dan dengerin indie music 🎨",
        "gender": "FEMALE",
        "age": 23,
        "interests": ["Coffee ☕", "Art 🎨", "Music 🎵", "Photography 📷"],
        "photo_file_id": "sample_photo_dinda_1",
    },
    {
        "telegram_id": 1002,
        "username": "rangga_tech",
        "display_name": "Rangga Dev 💻",
        "bio": "Software dev yang hobi outdoor & gaming 🎮 Cari temen ngopi dan diskusi Web3/AI 🚀",
        "gender": "MALE",
        "age": 26,
        "interests": ["Gaming 🎮", "Tech 💻", "Coffee ☕", "Hiking 🏔️"],
        "photo_file_id": "sample_photo_rangga_1",
    },
    {
        "telegram_id": 1003,
        "username": "sarah_books",
        "display_name": "Sarah Amalia 📚",
        "bio": "Bookworm 📚 & cat person 🐱 Suka cerita tentang film sci-fi dan jalan-jalan santai.",
        "gender": "FEMALE",
        "age": 20,
        "interests": ["Books 📚", "Pets 🐶", "Movies 🍿", "Anime 🌸"],
        "photo_file_id": "sample_photo_sarah_1",
    },
]


async def seed_data():
    logger.info("Seeding initial sample candidates into DB...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        for u_data in SAMPLE_USERS:
            existing = await session.get(User, u_data["telegram_id"])
            if not existing:
                user = User(
                    telegram_id=u_data["telegram_id"],
                    username=u_data["username"],
                    level=1,
                    exp=50,
                    onboarding_step="COMPLETE",
                )
                session.add(user)
                await session.flush()

                profile = Profile(
                    user_id=u_data["telegram_id"],
                    display_name=u_data["display_name"],
                    bio=u_data["bio"],
                    age=u_data["age"],
                    gender=u_data["gender"],
                    interests=u_data["interests"],
                    photo_file_ids=[u_data["photo_file_id"]],
                    completeness_score=100,
                    badges=["Verified Newbie 🌱"],
                )
                session.add(profile)

        await session.commit()
    logger.info("Seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_data())
