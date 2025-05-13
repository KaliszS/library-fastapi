from typing import Annotated
from collections.abc import Iterator

from fastapi import Depends

from sqlalchemy import create_engine, DateTime, String, Engine, inspect
from sqlalchemy.orm import DeclarativeBase, declared_attr, Session, sessionmaker

from app.config import settings
from app.models import serial_number, datetime_tz


engine = create_engine(settings.db_uri, pool_pre_ping=True)


def prepare_sessionmaker(engine: Engine) -> sessionmaker:
    return sessionmaker(autocommit=False, bind=engine)


class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(self) -> str:
        return self.__name__.lower()

    @property
    def id_str(self) -> str:
        return f"{inspect(self).identity[0]}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id_str})>"

    type_annotation_map = {
        str: String,
        serial_number: String(6),
        datetime_tz: DateTime(timezone=True),
    }


def get_db() -> Iterator[Session]:
    db = prepare_sessionmaker(engine)()
    with db:
        yield db


PgSession = Annotated[Session, Depends(get_db)]
