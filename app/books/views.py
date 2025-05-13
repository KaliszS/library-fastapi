from fastapi import APIRouter, Request, Depends, status

from app.database import PgSession
from app.models import serial_number
from app.utils.api_utils import pagination_params, format_response
from app.books.schemas import (
    BookCreate,
    BookRead,
    BookReadList,
    BookBorrow,
)
from app.books.services import book_service


router = APIRouter()
book_rels = [
    {"rel": "borrow", "method": "PATCH", "overwrite": "update", "endpoint": "/borrow"},
    {"rel": "return", "method": "POST", "endpoint": "/return"},
]


@router.post("", response_model=BookRead)
@format_response(extra_rels=book_rels, status_code=status.HTTP_201_CREATED)
async def create_book(request: Request, db: PgSession, book: BookCreate):
    return book_service.create(db, book)


@router.get("/{book_id}", response_model=BookRead)
@format_response(extra_rels=book_rels, status_code=status.HTTP_200_OK)
async def read_book(request: Request, db: PgSession, book_id: serial_number):
    return book_service.get(db, book_id)


@router.get("", response_model=BookReadList)
@format_response(is_collection=True, status_code=status.HTTP_200_OK)
async def read_books(
    request: Request,
    db: PgSession,
    author: str | None = None,
    pagination: dict = Depends(pagination_params),
):
    filters: dict[str, str] = {}
    if author:
        filters["author"] = author

    return book_service.get_all(db, filters=filters, **pagination)


@router.patch("/{book_id}/borrow", response_model=BookRead)
@format_response(extra_rels=book_rels, status_code=status.HTTP_200_OK)
async def borrow_book(
    request: Request, db: PgSession, book_id: serial_number, settlement: BookBorrow
):
    return book_service.update(db, book_id, settlement)


@router.post("/{book_id}/return", response_model=BookRead)
@format_response(extra_rels=book_rels, status_code=status.HTTP_200_OK)
async def return_book(request: Request, db: PgSession, book_id: serial_number):
    return book_service.give_back(db, book_id)


@router.delete("/{book_id}", response_model=BookRead)
@format_response(extra_rels=book_rels, status_code=status.HTTP_200_OK)
async def delete_book(request: Request, db: PgSession, book_id: serial_number):
    return book_service.delete(db, book_id)
