from typing import Annotated
from datetime import datetime, timezone

from pydantic import BaseModel, StringConstraints, Field


class BookCreate(BaseModel):
    id: Annotated[str, StringConstraints(pattern=r"^[0-9]{6}$")]
    title: str
    author: str


class BookRead(BaseModel):
    id: str
    title: str
    author: str
    reader: str | None
    borrowing_time: datetime | None

    _links: dict[str, dict]


class BookReadList(BaseModel):
    items: list[BookRead]
    _links: dict[str, dict]


class BookBorrow(BaseModel):
    reader: Annotated[str, StringConstraints(pattern=r"^[0-9]{6}$")]
    borrowing_time: datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc))
