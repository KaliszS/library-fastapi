from fastapi import status

create_payload = {"id": "012345", "title": "The Lord of the Rings", "author": "J.R.R. Tolkien"}


def test_endpoint_create(client, book_api_response_create):
    response = client.post(
        "/api/v1/books/",
        json=create_payload,
    )
    assert response.status_code == status.HTTP_201_CREATED

    book_json = response.json()
    assert book_json == book_api_response_create


def test_endpoint_create_duplicate(client, free_book):
    response = client.post(
        "/api/v1/books/",
        json=create_payload,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Book with that identifier already exists."}


def test_endpoint_create_wrong_id(client):
    response = client.post(
        "/api/v1/books/",
        json={"id": "a12345", "title": "The Lord of the Rings", "author": "J.R.R. Tolkien"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Serial number should be 6 digits long."}


def test_endpoint_get(client, free_book, book_api_response_get):
    response = client.get("/api/v1/books/012345")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == book_api_response_get


def test_endpoint_borrow(client, free_book, book_api_response_borrow):
    response = client.patch(
        "/api/v1/books/012345/borrow",
        json={"reader": "123456", "borrowing_time": "1954-07-29 12:00:00.100000"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == book_api_response_borrow


def test_endpoint_return(client, borrowed_book_2, book_api_response_return):
    response = client.post("/api/v1/books/012345/return")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == book_api_response_return


def test_endpoint_delete(client, free_book, book_api_response_get):
    response = client.delete("/api/v1/books/012345")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == book_api_response_get
