from functools import singledispatch, wraps
from collections.abc import Callable

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError as SQLAIntegrityError
from psycopg.errors import IntegrityError as PsycopgIntegrityError


class ResourceNotFoundException(Exception):
    def __init__(self, entity_name: str):
        self.entity_name = entity_name
        self.detail = f"{entity_name.capitalize()} not found."


@singledispatch
def handle_exception(exc: Exception, _: str) -> HTTPException:
    raise exc


@handle_exception.register
def _(exc: SQLAIntegrityError | PsycopgIntegrityError, entity: str) -> HTTPException:
    return HTTPException(
        status_code=400,
        detail=f"{entity.capitalize()} with that identifier already exists.",
    )


@handle_exception.register
def _(exc: RequestValidationError, err_msg: str) -> HTTPException:
    if "^[0-9]{6}$" in err_msg:
        err_msg = "Serial number should be 6 digits long."

    return HTTPException(
        status_code=400,
        detail=f"{err_msg}",
    )


@handle_exception.register
def _(exc: ResourceNotFoundException, _: str) -> HTTPException:
    return HTTPException(status_code=404, detail=exc.detail)


@handle_exception.register
def _(exc: AttributeError, entity: str) -> HTTPException:
    return HTTPException(
        status_code=400,
        detail=f"{entity.capitalize()} doesn't have such an attribute.",
    )


def handle_exceptions[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    def async_wrapper(self, *args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return func(self, *args, **kwargs)
        except Exception as exc:
            entity_name = getattr(self, "name", "unknown")
            raise handle_exception(exc, entity_name) from exc

    return async_wrapper
