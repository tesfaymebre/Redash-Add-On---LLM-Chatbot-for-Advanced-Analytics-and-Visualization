"""Tests for POST /api/chat."""

import pytest
from httpx import ASGITransport, AsyncClient

from redash_chatbot.app import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_chat_requires_question():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/chat", json={})

    assert response.status_code == 400
    assert response.json()["error"] == "question is required"


@pytest.mark.anyio
async def test_chat_returns_stub_answer():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/chat",
            json={
                "question": "How many views from mobile?",
                "context": {"type": "query_editor"},
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert "mobile" in body["answer"].lower()
    assert body["route"] == "stub"
    assert body["sql"] is None
    assert "session_id" in body


@pytest.mark.anyio
async def test_chat_cors_headers():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/chat", json={"question": "test"})

    assert response.headers.get("access-control-allow-origin") == "*"
