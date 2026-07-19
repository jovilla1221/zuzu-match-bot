from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from core.database import get_db_session

router = APIRouter(tags=["Health"])


@router.get("/healthz")
async def health_check(session: AsyncSession = Depends(get_db_session)):
    """System health check endpoint for monitoring/systemd."""
    try:
        await session.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        raise HTTPException(status_code=500, detail={"status": "error", "db": db_status})

    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
    }
