from collections.abc import Generator

import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import api
from app.database import Base, engine, get_db

from .factories import BookFree, BookBorrowed
from .utils import Session as SessionScoped
from tests.output_fixtures.books import (  # noqa: F401
    book_new_result,
    book_free_result,
    book_free_update_result,
    book_borrowed_return_result,
    book_api_response_create,
    book_api_response_get,
    book_api_response_borrow,
    book_api_response_return,
)


def reset_db() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


@pytest.fixture(autouse=True)
def db_session() -> Generator[Session, None, None]:
    with SessionScoped() as session:
        reset_db()
        yield session


@pytest.fixture
def client(db_session) -> Generator[TestClient, None, None]:
    api.dependency_overrides[get_db] = lambda: db_session
    with TestClient(api) as client:
        yield client


@pytest.fixture
def free_book() -> BookFree:
    return BookFree(id="012345", title="The Lord of the Rings", author="J.R.R. Tolkien")


@pytest.fixture
def free_book_2() -> BookFree:
    return BookFree(id="000012", title="The Children of Húrin", author="J.R.R. Tolkien")


@pytest.fixture
def borrowed_book() -> BookBorrowed:
    return BookBorrowed(
        id="001234",
        title="Hobbit",
        author="J.R.R. Tolkien",
        reader="123456",
        borrowing_time="1937-09-21 12:00:00.100000",
    )


@pytest.fixture
def borrowed_book_2() -> BookBorrowed:
    return BookBorrowed(
        id="012345",
        title="The Lord of the Rings",
        author="J.R.R. Tolkien",
        reader="123456",
        borrowing_time="1954-07-29 12:00:00.100000",
    )


@pytest.fixture
def books_100(free_book, free_book_2, borrowed_book) -> list[BookBorrowed | BookFree]:
    return [free_book, free_book_2, borrowed_book] + [BookFree() for _ in range(97)]
