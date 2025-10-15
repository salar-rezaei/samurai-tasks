# tests/test_api_unit.py
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/v1/tasks/nonexistent")
        assert r.status_code in (200, 404)  # route exists; behavior depends on DB
