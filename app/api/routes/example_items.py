from fastapi import APIRouter

from app.core.errors import ApiError
from app.db.crud.example_items import (
    DuplicateExampleNameError,
    create_example_item,
    get_example_item,
    list_example_items,
)
from app.db.session import DbSession
from app.schemas.common import ApiResponse, ok
from app.schemas.example_item import (
    ExampleItemCreateRequest,
    ExampleItemData,
    ExampleItemIdRequest,
    ExampleItemSearchData,
    ExampleItemSearchRequest,
)

router = APIRouter()


@router.post("/create", response_model=ApiResponse[ExampleItemData])
async def create(payload: ExampleItemCreateRequest, db: DbSession) -> ApiResponse[ExampleItemData]:
    try:
        item = await create_example_item(
            db,
            name=payload.name.strip(),
            description=payload.description.strip(),
        )
    except DuplicateExampleNameError as exc:
        raise ApiError(
            status_code=409, error_code="EXAMPLE_NAME_EXISTS", message="Example name already exists"
        ) from exc
    return ok(ExampleItemData.model_validate(item))


@router.post("/get", response_model=ApiResponse[ExampleItemData])
async def get(payload: ExampleItemIdRequest, db: DbSession) -> ApiResponse[ExampleItemData]:
    item = await get_example_item(db, payload.id)
    if item is None:
        raise ApiError(status_code=404, error_code="EXAMPLE_NOT_FOUND", message="Example item not found")
    return ok(ExampleItemData.model_validate(item))


@router.post("/search", response_model=ApiResponse[ExampleItemSearchData])
async def search(payload: ExampleItemSearchRequest, db: DbSession) -> ApiResponse[ExampleItemSearchData]:
    items, total = await list_example_items(
        db,
        keyword=payload.keyword,
        offset=(payload.page - 1) * payload.page_size,
        limit=payload.page_size,
    )
    return ok(
        ExampleItemSearchData(
            items=[ExampleItemData.model_validate(item) for item in items],
            total=total,
        )
    )
