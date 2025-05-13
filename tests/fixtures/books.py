import pytest


@pytest.fixture
def book_new_result() -> dict[str, str | None]:
    return {
        "id": "000123",
        "title": "Silmarillion",
        "author": "J.R.R. Tolkien",
        "reader": None,
        "borrowing_time": None,
    }


@pytest.fixture
def book_free_result() -> dict[str, str | None]:
    return {
        "id": "012345",
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "reader": None,
        "borrowing_time": None,
    }


@pytest.fixture
def book_free_update_result() -> dict[str, str]:
    return {
        "id": "012345",
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "reader": "123456",
        "borrowing_time": "1954-07-29T00:00:00+00:00",
    }


@pytest.fixture
def book_borrowed_return_result() -> dict[str, str | None]:
    return {
        "id": "001234",
        "title": "Hobbit",
        "author": "J.R.R. Tolkien",
        "reader": None,
        "borrowing_time": None,
    }


def book_api_response(
    reader: str | None = None,
    borr_time: str | None = None,
    id: str | None = "",
    endpoint: str | None = "",
    post: bool = False,
) -> dict:
    return {
        "id": "012345",
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "reader": reader,
        "borrowing_time": borr_time,
        "_links": [
            {
                "rel": "self",
                "href": f"http://testserver/api/v1/books{'' if post else '/'}{'' if post else id}{endpoint}",
            },
            {
                "rel": "delete",
                "href": f"http://testserver/api/v1/books/{id}",
                "method": "DELETE",
            },
            {
                "rel": "borrow",
                "href": f"http://testserver/api/v1/books/{id}/borrow",
                "method": "PATCH",
            },
            {
                "rel": "return",
                "href": f"http://testserver/api/v1/books/{id}/return",
                "method": "POST",
            },
        ],
    }


@pytest.fixture
def book_api_response_create() -> dict:
    return book_api_response(id="012345", post=True)


@pytest.fixture
def book_api_response_get() -> dict:
    return book_api_response(id="012345")


@pytest.fixture
def book_api_response_borrow() -> dict:
    return book_api_response(
        id="012345",
        endpoint="/borrow",
        reader="123456",
        borr_time="1954-07-29T12:00:00.100000+00:00",
    )


@pytest.fixture
def book_api_response_return() -> dict:
    return book_api_response(
        id="012345",
        endpoint="/return",
    )
