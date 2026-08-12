from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExampleItemCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=1000)


class ExampleItemIdRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID


class ExampleItemSearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    keyword: str | None = Field(default=None, max_length=120)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class ExampleItemData(BaseModel):
    id: UUID
    name: str
    description: str
    created_at: datetime
    updated_at: datetime


class ExampleItemSearchData(BaseModel):
    items: list[ExampleItemData]
    total: int
