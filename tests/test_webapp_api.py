import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app
from core.database import get_db_session


@pytest.mark.asyncio
async def test_healthz_endpoint(async_session):
    async def override_get_db_session():
        yield async_session

    app.dependency_overrides[get_db_session] = override_get_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["database"] == "healthy"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_security_headers():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/healthz")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"
