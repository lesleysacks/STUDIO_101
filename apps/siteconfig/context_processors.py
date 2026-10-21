"""Expose validated navigation and theme CSS to every template."""

import logging

from .services.errors import ConfigError
from .services.loader import get_bundle
from .services.security import is_external_href

logger = logging.getLogger("apps.siteconfig")


def _link(item: dict, path: str) -> dict:
    href = item.get("href", "")
    active = path == href or (href not in {"", "/"} and path.startswith(href))
    return {
        "id": item.get("id", ""),
        "label": item.get("label", ""),
        "href": href,
        "style": item.get("style", "link"),
        "external": is_external_href(href),
        "active": active,
    }


def siteconfig_context(request):
    try:
        bundle = get_bundle()
    except ConfigError:
        logger.exception("Site configuration is unavailable.")
        return {"site_nav": None, "site_theme_css": ""}
    navigation = bundle.navigation
    return {
        "site_nav": {
            "style": navigation.get("style", "fixed-dark"),
            "logo": navigation.get("logo", {}),
            "items": [_link(item, request.path) for item in navigation.get("items", [])],
            "footer": {
                "blurb": navigation.get("footer", {}).get("blurb", ""),
                "legal": navigation.get("footer", {}).get("legal", ""),
                "note": navigation.get("footer", {}).get("note", ""),
                "columns": [
                    {
                        "id": column.get("id", ""),
                        "title": column.get("title", ""),
                        "links": [_link(link, request.path) for link in column.get("links", [])],
                    }
                    for column in navigation.get("footer", {}).get("columns", [])
                ],
            },
        },
        "site_theme_css": bundle.theme_css,
    }
