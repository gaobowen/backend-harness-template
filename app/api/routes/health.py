from fastapi import APIRouter

from app.core.errors import ApiError
from app.schemas.common import ApiResponse, ok
from app.services.readiness import readiness_status

router = APIRouter()


@router.get("/live", response_model=ApiResponse[dict[str, str]])
async def live() -> ApiResponse[dict[str, str]]:
    return ok({"status": "alive"})


@router.get("/ready", response_model=ApiResponse[dict[str, str]])
async def ready() -> ApiResponse[dict[str, str]]:
    try:
        status = await readiness_status()
    except Exception as exc:
        raise ApiError(status_code=503, error_code="DEPENDENCY_UNAVAILABLE", message="Service is not ready") from exc
    return ok(status)
