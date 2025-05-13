from logging import getLogger

from app.database import PgSession
from app.repositories import CrudRepository
from app.services import AppService
from app.models import serial_number
from app.books.models import Book
from app.books.schemas import BookCreate, BookBorrow


logger = getLogger(__name__)


class BookRepository(CrudRepository[Book, BookCreate, BookBorrow]):
    def update_returned_book(self, db_session: PgSession, originator: Book) -> Book:
        originator.reader = None
        originator.borrowing_time = None

        db_session.add(originator)
        db_session.commit()
        db_session.refresh(originator)

        return originator


class BookService(AppService[BookRepository, Book, BookCreate, BookBorrow]):
    def give_back(self, db_session: PgSession, object_id: serial_number) -> Book | None:
        if originator := self.get(db_session, object_id):
            fetched = self.crud.update_returned_book(db_session, originator)
            self.logger.info(f"Returned book with ID: {fetched.id}.")
            return fetched


book_service = BookService(BookRepository, Book, logger)
