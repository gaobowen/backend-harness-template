from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from redis.asyncio import Redis

from app.core.config import settings

_pool = Redis.from_url(settings.redis_url, decode_responses=True)


@asynccontextmanager
async def redis_client() -> AsyncIterator[Redis]:
    yield _pool


async def close_redis_pool() -> None:
    await _pool.aclose()
