from logging import basicConfig, INFO

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.api import api_router
from app.utils.exceptions import handle_exception


basicConfig(level=INFO, format="[%(asctime)s - %(name)s] (%(levelname)s) %(message)s")

api = FastAPI(title="Library API")


@api.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    raise handle_exception(exc, err_msg=exc.args[0][0]["msg"])


@api.get("/")
async def root():
    return {"message": "Library server is running!"}


api.include_router(api_router, prefix=settings.api_latest)
