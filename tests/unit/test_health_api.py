from httpx import ASGITransport, AsyncClient

from app.api.routes import health
from app.main import app


async def test_live_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/health/live")

    assert response.status_code == 200
    assert response.json() == {"code": 200, "data": {"status": "alive"}, "msg": ""}


async def test_ready_endpoint_reports_dependencies(monkeypatch) -> None:
    async def fake_readiness() -> dict[str, str]:
        return {"status": "ready", "database": "ok", "redis": "ok"}

    monkeypatch.setattr(health, "readiness_status", fake_readiness)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/health/ready")

    assert response.status_code == 200
    assert response.json()["data"]["database"] == "ok"


async def test_ready_endpoint_uses_stable_error(monkeypatch) -> None:
    async def failing_readiness() -> dict[str, str]:
        raise RuntimeError("database password must not leak")

    monkeypatch.setattr(health, "readiness_status", failing_readiness)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "code": 503,
        "data": {"error_code": "DEPENDENCY_UNAVAILABLE"},
        "msg": "Service is not ready",
    }
