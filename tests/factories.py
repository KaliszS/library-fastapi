import datetime
from random import randint

from factory import LazyFunction, Faker
from factory.alchemy import SQLAlchemyModelFactory

from app.books.models import Book
from .utils import Session as SessionScoped


class BookFactory(SQLAlchemyModelFactory):
    id = LazyFunction(lambda: f"{randint(0, 999999):06d}")
    title = Faker("sentence", nb_words=3)
    author = Faker("name")

    class Meta:
        model = Book
        sqlalchemy_session = SessionScoped
        sqlalchemy_session_persistence = "flush"


class BookBorrowed(BookFactory):
    reader = LazyFunction(lambda: f"{randint(0, 999999):06d}")
    borrowing_time = LazyFunction(lambda: datetime.now())


class BookFree(BookFactory):
    reader = None
    borrowing_time = None
