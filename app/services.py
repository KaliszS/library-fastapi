from uuid import UUID
from logging import Logger

from pydantic import BaseModel
from sqlalchemy.orm import Query

from app.database import Base, PgSession
from app.config import settings
from app.utils.exceptions import ResourceNotFoundException, handle_exceptions


type ModelType[model: Base] = model
type CreateSchemaType[schema: BaseModel] = schema
type UpdateSchemaType[schema: BaseModel] = schema


class CrudServices[ModelType, CreateSchemaType, UpdateSchemaType]:
    """Class to manage database operations."""

    def __init__(self, model: type[ModelType]):
        self.model = model

    def create(self, db_session: PgSession, creator: CreateSchemaType) -> ModelType:
        creation_data = creator.model_dump()
        creation = self.model(**creation_data)
        db_session.add(creation)
        db_session.commit()
        db_session.refresh(creation)
        return creation

    def get(self, db_session: PgSession, object_id: UUID | int) -> ModelType | None:
        return (
            db_session.query(self.model)
            .filter(self.model.id == object_id)
            .one_or_none()
        )

    def get_all(
        self,
        db_session: PgSession,
        filters: dict[str, str] = {},
        offset: int = 0,
        limit: int = settings.paging_limit,
        sort_by: str | None = None,
    ) -> list[ModelType]:
        query: Query = db_session.query(self.model)

        for field, value in filters.items():
            query = query.filter(getattr(self.model, field) == value)

        if sort_by:
            query = query.order_by(getattr(self.model, sort_by))

        return query.offset(offset).limit(limit).all()

    def update(
        self,
        db_session: PgSession,
        originator: ModelType,
        updater: UpdateSchemaType,
    ) -> ModelType:
        updater_data = updater.model_dump(exclude_none=True)
        for field_name, field_value in updater_data.items():
            setattr(originator, field_name, field_value)
        db_session.add(originator)
        db_session.commit()
        db_session.refresh(originator)
        return originator

    def delete(self, db_session: PgSession, originator: ModelType) -> None:
        db_session.delete(originator)
        db_session.commit()
        return originator


class AppServices[
    CrudModelType: CrudServices,
    ModelType,
    CreateSchemaType,
    UpdateSchemaType,
]:
    """Class to prepare CrudServices to being used by API views."""

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
    async def create(
        self, db_session: PgSession, creator: CreateSchemaType
    ) -> ModelType:
        creation = self.crud.create(db_session, creator)
        self.logger.info(f"Created {self.name} with ID: {creation.id}.")
        return creation

    @handle_exceptions
    async def get(
        self, db_session: PgSession, object_id: UUID | int, raise_404: bool = True
    ) -> ModelType:
        if not (fetched := self.crud.get(db_session, object_id)) and raise_404:
            raise ResourceNotFoundException(self.name)
        self.logger.info(f"Fetched {self.name} with ID: {fetched.id}.")
        return fetched

    @handle_exceptions
    async def get_all(
        self,
        db_session: PgSession,
        filters: dict[str, str] = {},
        page: int = 1,
        limit: int = settings.paging_limit,
        sort_by: str | None = None,
        raise_404: bool = False,
    ) -> list[ModelType]:
        offset = max((page - 1), 0) * limit
        fetched = self.crud.get_all(db_session, filters, offset, limit, sort_by)

        if not fetched and raise_404:
            raise ResourceNotFoundException(self.name)

        self.logger.info(
            f"Fetched {len(fetched)} {self.name}s. Filters used: {filters}."
        )

        return fetched

    async def update(
        self,
        db_session: PgSession,
        object_id: UUID | int,
        updater: UpdateSchemaType,
    ) -> ModelType:
        if originator := await self.get(db_session, object_id):
            fetched = self.crud.update(db_session, originator, updater)
            self.logger.info(f"Updated {self.name} with ID: {fetched.id}.")
            return fetched

    async def delete(self, db_session: PgSession, object_id: UUID | int) -> ModelType:
        if originator := await self.get(db_session, object_id):
            deleted = self.crud.delete(db_session, originator)
            self.logger.info(f"Deleted {self.name} with ID: {deleted.id}.")
            return deleted
