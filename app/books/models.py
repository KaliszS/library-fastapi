from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models import serial_number, datetime_tz, sql_index


class Book(Base):
    id: Mapped[serial_number] = mapped_column(primary_key=True)
    title: Mapped[str]
    author: Mapped[sql_index(str)]
    reader: Mapped[sql_index(serial_number | None)]
    borrowing_time: Mapped[datetime_tz | None]
