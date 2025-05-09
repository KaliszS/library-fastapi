from sqlalchemy.inspection import inspect

from app.database import Base
from app.config import settings


def base_to_dict(instance: Base) -> dict[str, str]:
    """Function to convert SQLALchemy Base model into dict."""
    return {
        c.key: getattr(instance, c.key) for c in inspect(instance).mapper.column_attrs
    }


def build_query(base_url: str, name: str, inst_id: str | None = "") -> str:
    return f"{base_url}{settings.api_latest}/{name}s/{inst_id}"


def generate_item_links(
    built_url: str,
    url: str,
    extra_rels: list[dict] | None = None,
) -> list[dict]:
    links = [
        {"rel": "self", "href": url},
        {"rel": "update", "href": built_url, "method": "PUT"},
        {"rel": "delete", "href": built_url, "method": "DELETE"},
    ]
    if extra_rels:
        for relation in extra_rels:
            link = {}
            link["rel"] = relation.get("rel")
            link["href"] = built_url + relation.get("endpoint", "")
            link["method"] = relation.get("method")
            links.append(link)
            if overwrite := relation.get("overwrite"):
                links = [lnk for lnk in links if lnk.get("rel") != overwrite]
    return links


def generate_collection_links(
    page: int,
    limit: int,
    base_url: str,
) -> list[dict]:
    links = [
        {"rel": "self", "href": f"{base_url}?page={page}&limit={limit}"},
        {"rel": "next", "href": f"{base_url}?page={page + 1}&limit={limit}"},
    ]
    if page > 1:
        links.append(
            {"rel": "prev", "href": f"{base_url}?page={page - 1}&limit={limit}"}
        )
    return links


def get_hateoas_item(
    instance: Base, base_url: str, url: str, extra_rels: dict | None = None
) -> dict:
    item = base_to_dict(instance)
    name = instance.__tablename__
    inst_id = instance.id_str
    built_url = build_query(base_url, name, inst_id)
    item["_links"] = generate_item_links(built_url, url, extra_rels)
    return item


def get_hateoas_list(
    items: list[Base],
    page: int,
    limit: int,
    base_url: str,
) -> dict:
    name = items[0].__tablename__ if len(items) else ""
    built_url = build_query(base_url, name)
    return {
        "items": [base_to_dict(item) for item in items],
        "_links": generate_collection_links(page, limit, built_url),
    }
