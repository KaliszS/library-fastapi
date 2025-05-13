from functools import wraps

from fastapi import Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.config import settings
from app.utils.hateoas import get_hateoas_item, get_hateoas_list


def pagination_params(
    page: int = Query(1, ge=1),
    limit: int = Query(settings.paging_limit, ge=1),
    sort_by: str | None = None,
) -> dict[str, str]:
    return {"page": page, "limit": limit, "sort_by": sort_by}


def format_response(extra_rels: dict = {}, is_collection: bool = False, status_code: int = 200):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            base_url = str(kwargs.get("request").base_url).rstrip("/")
            full_url = str(kwargs.get("request").url)
            result = await func(*args, **kwargs)
            if is_collection:
                pagination = kwargs["pagination"]
                page = int(pagination.get("page", 1))
                limit = int(pagination.get("limit", settings.paging_limit))
                formatted = get_hateoas_list(result, page, limit, base_url)
            else:
                formatted = get_hateoas_item(result, base_url, full_url, extra_rels)
            return JSONResponse(content=jsonable_encoder(formatted), status_code=status_code)

        return wrapper

    return decorator
