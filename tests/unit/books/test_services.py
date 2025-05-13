import pytest
from unittest.mock import patch
from freezegun import freeze_time
from fastapi import HTTPException

from app.books.schemas import BookCreate, BookBorrow
from app.books.services import book_service as service
from app.utils.utils import base_to_dict


def test_service_create(db_session, book_new_result):
    new_book = BookCreate(id="000123", title="Silmarillion", author="J.R.R. Tolkien")
    created_book = service.create(db_session, new_book)
    assert created_book
    assert created_book.id == "000123"

    confirmed_book = service.get(db_session, new_book.id)
    assert base_to_dict(confirmed_book) == book_new_result

    new_book_2 = BookCreate(id="000111", title="Beren and Lúthien", author="J.R.R. Tolkien")
    with patch.object(service.logger, "info") as mock_logger:
        service.create(db_session, new_book_2)
    mock_logger.assert_called_once_with("Created book with ID: 000111.")


@pytest.mark.parametrize(
    "book_data, expected_code, expected_msg",
    [
        (  # duplicated ID (id of free_book fixture)
            {"id": "012345", "title": "Silmarillion", "author": "J.R.R. Tolkien"},
            400,
            "Book with that identifier already exists.",
        ),
    ],
)
def test_service_create_errors(
    db_session, free_book, book_data: dict[str, str], expected_code: int, expected_msg: str
):
    with pytest.raises(HTTPException) as err:
        service.create(db_session, BookCreate(**book_data))

    assert err.value.status_code == expected_code
    assert err.value.detail == expected_msg


def test_service_get(db_session, free_book, book_free_result):
    with patch.object(service.logger, "info") as mock_logger:
        book = service.get(db_session, free_book.id)

    assert book
    assert base_to_dict(book) == book_free_result
    mock_logger.assert_called_once_with("Fetched book with ID: 012345.")


@pytest.mark.parametrize(
    "filters, page, limit, sort_by, results",
    [
        ({}, 1, 100, "author", 100),
        ({"author": "J.R.R. Tolkien"}, 1, 100, None, 3),
        ({"author": "C.S. Lewis"}, 1, 100, None, 0),
        ({"author": "J.R.R. Tolkien"}, 1, 2, None, 2),
        ({"author": "J.R.R. Tolkien"}, 2, 2, None, 1),
    ],
)
def test_service_get_all(
    db_session,
    books_100,
    filters: dict[str, str],
    page: int,
    limit: int,
    sort_by: str | None,
    results: int,
):
    with patch.object(service.logger, "info") as mock_logger:
        books = service.get_all(db_session, filters, page, limit, sort_by)

    assert len(books) == results
    mock_logger.assert_called_once_with(f"Fetched {results} books. Filters used: {filters}.")


@freeze_time("1954-07-29", tz_offset=0)
def test_service_update(db_session, free_book, book_free_update_result):
    update = BookBorrow(reader="123456")
    with patch.object(service.logger, "info") as mock_logger:
        updated_book = service.update(db_session, free_book.id, update)
    assert updated_book
    assert base_to_dict(updated_book) == book_free_update_result
    mock_logger.assert_called_with("Updated book with ID: 012345.")


def test_service_update_return(db_session, borrowed_book, book_borrowed_return_result):
    with patch.object(service.logger, "info") as mock_logger:
        updated_book = service.give_back(db_session, borrowed_book.id)
    assert updated_book
    assert base_to_dict(updated_book) == book_borrowed_return_result
    mock_logger.assert_called_with("Returned book with ID: 001234.")


def test_service_delete(db_session, free_book):
    with patch.object(service.logger, "info") as mock_logger:
        deleted_book = service.delete(db_session, free_book.id)
    assert deleted_book
    mock_logger.assert_called_with("Deleted book with ID: 012345.")
    no_book = service.get(db_session, deleted_book.id, False)
    assert not no_book
