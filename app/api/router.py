from fastapi import APIRouter

from app.api.routes import example_items, health

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(example_items.router, prefix="/examples", tags=["examples"])
