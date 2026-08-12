from sqlalchemy import text

from app.db.redis import redis_client
from app.db.session import db_session


async def readiness_status() -> dict[str, str]:
    async with db_session() as db:
        await db.execute(text("select 1"))
    async with redis_client() as redis:
        await redis.ping()
    return {"status": "ready", "database": "ok", "redis": "ok"}
