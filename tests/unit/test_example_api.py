from datetime import UTC, datetime
from uuid import UUID, uuid4

from httpx import ASGITransport, AsyncClient

from app.api.routes import example_items
from app.db.crud.example_items import DuplicateExampleNameError
from app.main import app


def item_data(item_id: UUID | None = None, *, name: str = "example") -> dict:
    now = datetime.now(UTC)
    return {
        "id": item_id or uuid4(),
        "name": name,
        "description": "description",
        "created_at": now,
        "updated_at": now,
    }


async def test_create_example_item(monkeypatch) -> None:
    expected = item_data()

    async def fake_create(*args, **kwargs) -> dict:
        return expected

    monkeypatch.setattr(example_items, "create_example_item", fake_create)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/examples/create", json={"name": " example ", "description": " description "})

    assert response.status_code == 200
    assert response.json()["data"]["name"] == "example"


async def test_create_example_item_maps_duplicate_error(monkeypatch) -> None:
    async def fake_create(*args, **kwargs) -> dict:
        raise DuplicateExampleNameError("example")

    monkeypatch.setattr(example_items, "create_example_item", fake_create)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/examples/create", json={"name": "example"})

    assert response.status_code == 409
    assert response.json()["data"]["error_code"] == "EXAMPLE_NAME_EXISTS"


async def test_get_missing_example_item(monkeypatch) -> None:
    async def fake_get(*args, **kwargs) -> None:
        return None

    monkeypatch.setattr(example_items, "get_example_item", fake_get)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/examples/get", json={"id": str(uuid4())})

    assert response.status_code == 404
    assert response.json()["data"]["error_code"] == "EXAMPLE_NOT_FOUND"


async def test_get_example_item(monkeypatch) -> None:
    expected = item_data()

    async def fake_get(*args, **kwargs) -> dict:
        return expected

    monkeypatch.setattr(example_items, "get_example_item", fake_get)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/examples/get", json={"id": str(expected["id"])})

    assert response.status_code == 200
    assert response.json()["data"]["id"] == str(expected["id"])


async def test_search_example_items(monkeypatch) -> None:
    expected = item_data(name="search-result")

    async def fake_list(*args, **kwargs) -> tuple[list[dict], int]:
        return [expected], 1

    monkeypatch.setattr(example_items, "list_example_items", fake_list)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/examples/search", json={"keyword": "search", "page": 1, "page_size": 20})

    assert response.status_code == 200
    assert response.json()["data"]["total"] == 1
    assert response.json()["data"]["items"][0]["name"] == "search-result"


async def test_unknown_request_fields_are_rejected() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/examples/search", json={"unexpected": True})

    assert response.status_code == 422
    assert response.json()["data"]["error_code"] == "VALIDATION_ERROR"
