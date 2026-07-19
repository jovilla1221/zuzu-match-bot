from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from core.config import settings
from api.routes.health import router as health_router
from api.routes.webapp import router as webapp_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Zuzu FastAPI Application...")
    yield
    logger.info("Shutting down Zuzu FastAPI Application...")


app = FastAPI(
    title="Zuzu Match Bot API",
    description="Backend API endpoints for Telegram Web App & Health Monitoring",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS Middleware Setup — ALWAYS whitelist exact origins, never "*" with credentials
allowed_origins = [settings.WEBAPP_URL] if settings.WEBAPP_URL else ["http://127.0.0.1:8008"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Inject standard security headers into all API HTTP responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response


from fastapi.staticfiles import StaticFiles

# Include Routers
app.include_router(health_router)
app.include_router(webapp_router)

# Mount WebApp Static Files — html=True removed to prevent directory listing
app.mount("/static", StaticFiles(directory="api/static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
