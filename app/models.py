from datetime import datetime
from typing import Annotated, Literal, Any

from sqlalchemy.orm import MappedColumn, mapped_column


serial_number = Annotated[str, Literal["length=6", "digits-only"]]
datetime_tz = Annotated[datetime, Literal["timezone-aware"]]


def sql_primary_key[T](col_type: T) -> Annotated[T, MappedColumn[Any]]:
    """Function to set primary key using SQlAlchemy ORM"""
    return Annotated[col_type, mapped_column(primary_key=True)]


def sql_index[T](col_type: T) -> Annotated[T, MappedColumn[Any]]:
    """Function to set index using SQLAlchemy ORM"""
    return Annotated[col_type, mapped_column(index=True)]
