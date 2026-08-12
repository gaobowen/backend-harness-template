from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

pytestmark = pytest.mark.integration


async def test_example_item_round_trip() -> None:
    unique_name = f"integration-{uuid4()}"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        ready = await client.get("/api/health/ready")
        assert ready.status_code == 200

        created = await client.post(
            "/api/examples/create",
            json={"name": unique_name, "description": "integration fixture"},
        )
        assert created.status_code == 200
        item_id = created.json()["data"]["id"]

        fetched = await client.post("/api/examples/get", json={"id": item_id})
        assert fetched.status_code == 200
        assert fetched.json()["data"]["name"] == unique_name

        searched = await client.post(
            "/api/examples/search",
            json={"keyword": unique_name, "page": 1, "page_size": 10},
        )
        assert searched.status_code == 200
        assert searched.json()["data"]["total"] == 1
