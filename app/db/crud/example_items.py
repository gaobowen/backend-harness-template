from typing import Any
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.example_item import ExampleItem


class DuplicateExampleNameError(ValueError):
    pass


async def create_example_item(db: AsyncSession, *, name: str, description: str) -> dict[str, Any]:
    item = ExampleItem(name=name, description=description)
    db.add(item)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise DuplicateExampleNameError(name) from exc
    await db.refresh(item)
    return item.to_dict()


async def get_example_item(db: AsyncSession, item_id: UUID) -> dict[str, Any] | None:
    item = await db.get(ExampleItem, item_id)
    return item.to_dict() if item else None


async def list_example_items(
    db: AsyncSession,
    *,
    keyword: str | None,
    offset: int,
    limit: int,
) -> tuple[list[dict[str, Any]], int]:
    filters = []
    if keyword:
        pattern = f"%{keyword.strip()}%"
        filters.append(or_(ExampleItem.name.ilike(pattern), ExampleItem.description.ilike(pattern)))

    count_stmt = select(func.count()).select_from(ExampleItem).where(*filters)
    items_stmt = (
        select(ExampleItem)
        .where(*filters)
        .order_by(ExampleItem.created_at.desc(), ExampleItem.id.desc())
        .offset(offset)
        .limit(limit)
    )
    total = int(await db.scalar(count_stmt) or 0)
    items = await db.scalars(items_stmt)
    return [item.to_dict() for item in items.all()], total
