import asyncio
from loguru import logger
from core.database import engine
from models.base import Base
import models  # loads all models into Base.metadata


async def init_db():
    logger.info("Creating database tables if not exist...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
