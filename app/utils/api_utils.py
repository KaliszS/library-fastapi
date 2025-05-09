from functools import wraps

from fastapi import Query, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.utils.hateoas import get_hateoas_item, get_hateoas_list


def pagination_params(
    page: int = Query(1, ge=1),
    limit: int = Query(settings.paging_limit, ge=1),
    sort_by: str | None = None,
) -> dict[str, str]:
    return {"page": page, "limit": limit, "sort_by": sort_by}


def format_response(extra_rels: dict = {}, is_collection: bool = False):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            base_url = str(request.base_url).rstrip("/")
            full_url = str(request.url)
            result = await func(request, *args, **kwargs)
            if is_collection:
                pagination = kwargs["pagination"]
                page = int(pagination.get("page", 1))
                limit = int(pagination.get("limit", settings.paging_limit))
                formatted = get_hateoas_list(result, page, limit, base_url)
            else:
                formatted = get_hateoas_item(result, base_url, full_url, extra_rels)
            return JSONResponse(content=formatted)

        return wrapper

    return decorator


# def format_single_resource(
#     instance: BaseModel,
#     base_url: str,
#     extra_actions: dict[str, dict] | None = None,
# ) -> dict:
#     item = instance.model_dump()
#     item["_links"] = generate_item_links(item["id"], base_url, extra_actions)
#     return item


# def format_collection_response(
#     items: list[BaseModel],
#     page: int,
#     limit: int,
#     base_url: str,
#     extra_actions: dict[str, dict] | None = None,
# ) -> dict:
#     return {
#         "items": [item.model_dump() for item in items],
#         "_links": generate_collection_links(page, limit, base_url, extra_actions),
#     }
