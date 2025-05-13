import pytest
from freezegun import freeze_time

from app.books.models import Book
from app.books.schemas import BookCreate, BookBorrow
from app.books.services import BookRepository
from app.utils.utils import base_to_dict


repository = BookRepository(Book)


def test_repository_create(db_session, book_new_result):
    new_book = BookCreate(id="000123", title="Silmarillion", author="J.R.R. Tolkien")
    created_book = repository.create(db_session, new_book)
    assert created_book
    assert created_book.id == "000123"

    confirmed_book = repository.get(db_session, new_book.id)
    assert base_to_dict(confirmed_book) == book_new_result


def test_repository_get(db_session, free_book, book_free_result):
    book = repository.get(db_session, free_book.id)
    assert book
    assert base_to_dict(book) == book_free_result


@pytest.mark.parametrize(
    "filters, offset, limit, sort_by, results",
    [
        ({}, 0, 100, "author", 100),
        ({}, 1, 100, None, 99),
        ({"author": "J.R.R. Tolkien"}, 0, 100, None, 3),
        ({"author": "C.S. Lewis"}, 0, 100, None, 0),
        ({"author": "J.R.R. Tolkien"}, 0, 2, None, 2),
        ({"author": "J.R.R. Tolkien"}, 1, 2, None, 2),
    ],
)
def test_repository_get_all(
    db_session,
    books_100,
    filters: dict[str, str],
    offset: int,
    limit: int,
    sort_by: str | None,
    results: int,
):
    books = repository.get_all(db_session, filters, offset, limit, sort_by)
    assert len(books) == results


@freeze_time("1954-07-29", tz_offset=0)
def test_repository_update(db_session, free_book, book_free_update_result):
    update = BookBorrow(reader="123456")
    updated_book = repository.update(db_session, free_book, update)
    assert updated_book
    assert base_to_dict(updated_book) == book_free_update_result


def test_repository_update_return(db_session, borrowed_book, book_borrowed_return_result):
    updated_book = repository.update_returned_book(db_session, borrowed_book)
    assert updated_book
    assert base_to_dict(updated_book) == book_borrowed_return_result


def test_repository_delete(db_session, free_book):
    deleted_book = repository.delete(db_session, free_book)
    assert deleted_book

    no_book = repository.get(db_session, deleted_book.id)
    assert not no_book
