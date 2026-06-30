"""Smoke tests — verify the app boots and responds."""

import pytest
from httpx import ASGITransport, AsyncClient

from redash_chatbot.app import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_health_returns_ok():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "redash-chatbot-backend"
