from uuid import UUID
from logging import Logger

from pydantic import BaseModel

from app.database import Base, PgSession
from app.repositories import CrudRepository
from app.utils.exceptions import ResourceNotFoundException, handle_exceptions


class AppService[
    CrudModelType: CrudRepository,
    ModelType: Base,
    CreateSchemaType: BaseModel,
    UpdateSchemaType: BaseModel,
]:
    """Class to prepare CrudRepository to being used by API views."""

    def __init__(
        self,
        crud_model: type[CrudModelType],
        model: type[ModelType],
        log: Logger,
    ):
        self.crud = crud_model(model)
        self.name = self.crud.model.__name__.lower()
        self.logger = log

    @handle_exceptions
    def create(self, db_session: PgSession, creator: CreateSchemaType) -> ModelType:
        creation = self.crud.create(db_session, creator)
        self.logger.info(f"Created {self.name} with ID: {creation.id}.")
        return creation

    @handle_exceptions
    def get(
        self, db_session: PgSession, object_id: UUID | int, raise_404: bool = True
    ) -> ModelType:
        if not (fetched := self.crud.get(db_session, object_id)) and raise_404:
            raise ResourceNotFoundException(self.name)
        if raise_404:
            self.logger.info(f"Fetched {self.name} with ID: {fetched.id}.")
        return fetched

    @handle_exceptions
    def get_all(
        self,
        db_session: PgSession,
        filters: dict[str, str],
        page: int,
        limit: int,
        sort_by: str | None,
        raise_404: bool = False,
    ) -> list[ModelType]:
        offset = max((page - 1), 0) * limit
        fetched = self.crud.get_all(db_session, filters, offset, limit, sort_by)

        if not fetched and raise_404:
            raise ResourceNotFoundException(self.name)

        self.logger.info(f"Fetched {len(fetched)} {self.name}s. Filters used: {filters}.")

        return fetched

    def update(
        self,
        db_session: PgSession,
        object_id: UUID | int,
        updater: UpdateSchemaType,
    ) -> ModelType:
        if originator := self.get(db_session, object_id):
            fetched = self.crud.update(db_session, originator, updater)
            self.logger.info(f"Updated {self.name} with ID: {fetched.id}.")
            return fetched

    def delete(self, db_session: PgSession, object_id: UUID | int) -> ModelType:
        if originator := self.get(db_session, object_id):
            deleted = self.crud.delete(db_session, originator)
            self.logger.info(f"Deleted {self.name} with ID: {deleted.id}.")
            return deleted
