import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from models.base import Base


@pytest_asyncio.fixture
async def async_session() -> AsyncSession:
    """Provides isolated SQLite in-memory session for async service unit tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    
    async with session_factory() as session:
        yield session
        await session.rollback()
        
    await engine.dispose()
