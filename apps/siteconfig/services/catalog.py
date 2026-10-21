"""Merge JSON catalogs with database records. Database rows win on the same slug."""

from __future__ import annotations

from types import SimpleNamespace

from apps.portfolio.models import Project
from apps.services.models import Service
from apps.streams.models import LiveStream

from .security import css_background_url, public_static_url, safe_embed_url


def _image_url(image_field, static_path: str = "") -> str:
    if image_field:
        try:
            return css_background_url(image_field.url)
        except ValueError:
            return ""
    return public_static_url(static_path)


def service_card(entry: dict) -> dict:
    image = public_static_url(entry.get("featured_image", ""))
    return {
        "slug": entry["slug"],
        "title": entry.get("name") or entry.get("title", ""),
        "summary": entry.get("summary", ""),
        "category": (entry.get("category") or {}).get("name", ""),
        "image_url": image,
        "alt": entry.get("image_alt") or entry.get("name") or entry.get("title", ""),
        "href": f"/services/{entry['slug']}/",
        "order": entry.get("order", 0),
        "price_label": entry.get("price_label", ""),
    }


def service_card_from_model(service: Service) -> dict:
    category = service.category.name if service.category_id else ""
    return {
        "slug": service.slug,
        "title": service.title,
        "summary": service.summary,
        "category": category,
        "image_url": _image_url(service.featured_image),
        "alt": service.title,
        "href": f"/services/{service.slug}/",
        "order": service.order,
        "price_label": f"From R{service.starting_price}" if service.starting_price is not None else "",
    }


def merged_services(catalog: dict[str, dict], *, featured_only: bool, limit: int) -> list[dict]:
    items: dict[str, dict] = {}
    for slug, entry in catalog.items():
        if not entry.get("published", True):
            continue
        if featured_only and not entry.get("is_featured", False):
            continue
        items[slug] = service_card(entry)
    queryset = Service.objects.select_related("category").all()
    if featured_only:
        queryset = queryset.filter(is_featured=True)
    for service in queryset:
        items[service.slug] = service_card_from_model(service)
    ordered = sorted(items.values(), key=lambda item: (item["order"], item["title"].lower()))
    return ordered[:limit]


def project_card(entry: dict) -> dict:
    image = public_static_url(entry.get("image", ""))
    slug = entry.get("slug", "")
    return {
        "slug": slug,
        "title": entry.get("title", ""),
        "summary": entry.get("summary") or entry.get("caption", ""),
        "category": (entry.get("category") or {}).get("name", ""),
        "image_url": image,
        "alt": entry.get("image_alt") or entry.get("title", ""),
        "href": f"/portfolio/{slug}/" if slug else "",
        "order": entry.get("order", 0),
    }


def project_card_from_model(project: Project) -> dict:
    return {
        "slug": project.slug,
        "title": project.title,
        "summary": project.summary,
        "category": project.category.name if project.category_id else "",
        "image_url": _image_url(project.cover_image),
        "alt": project.title,
        "href": f"/portfolio/{project.slug}/",
        "order": project.order,
    }


def merged_projects(catalog: dict[str, dict], *, featured_only: bool, limit: int) -> list[dict]:
    items: dict[str, dict] = {}
    for slug, entry in catalog.items():
        if not entry.get("published", True):
            continue
        if featured_only and not entry.get("is_featured", False):
            continue
        items[slug] = project_card(entry)
    queryset = Project.objects.select_related("category").filter(is_published=True)
    if featured_only:
        queryset = queryset.filter(is_featured=True)
    for project in queryset:
        items[project.slug] = project_card_from_model(project)
    ordered = sorted(items.values(), key=lambda item: (item["order"], item["title"].lower()))
    return ordered[:limit]


def fallback_cards(items: list[dict]) -> list[dict]:
    cards = []
    for item in items:
        image = public_static_url(item.get("image", ""))
        cards.append(
            {
                "title": item.get("title", ""),
                "summary": item.get("summary", ""),
                "category": item.get("category", ""),
                "image_url": image,
                "alt": item.get("alt") or item.get("title", ""),
                "href": item.get("href", "") if item.get("href") else "",
                "caption": item.get("caption", ""),
            }
        )
    return cards


def json_service_namespace(entry: dict):
    image = public_static_url(entry.get("featured_image", ""))
    category_name = (entry.get("category") or {}).get("name", "")
    features = [
        SimpleNamespace(title=feature.get("title", ""), description=feature.get("description", ""))
        for feature in entry.get("features", [])
    ]
    service = SimpleNamespace(
        title=entry.get("name", ""),
        slug=entry.get("slug", ""),
        summary=entry.get("summary", ""),
        full_description=entry.get("description", ""),
        starting_price=entry.get("starting_price"),
        duration_label=entry.get("duration_label", ""),
        price_unit=entry.get("price_unit", ""),
        category=SimpleNamespace(name=category_name),
        featured_image=SimpleNamespace(url=image) if image else None,
        cta_label=entry.get("cta_label") or "Book This Service",
        cta_href=entry.get("cta_href") or "",
    )
    return service, features


def json_project_namespace(entry: dict):
    image = public_static_url(entry.get("image", ""))
    category_name = (entry.get("category") or {}).get("name", "")
    gallery = []
    for item in entry.get("gallery", []):
        url = public_static_url(item.get("image", ""))
        if not url:
            continue
        gallery.append(SimpleNamespace(image=SimpleNamespace(url=url), caption=item.get("alt") or item.get("caption", "")))
    project = SimpleNamespace(
        title=entry.get("title", ""),
        slug=entry.get("slug", ""),
        client_name=entry.get("client_name", ""),
        summary=entry.get("summary", ""),
        description=entry.get("description", ""),
        category=SimpleNamespace(name=category_name),
        cover_image=SimpleNamespace(url=image) if image else None,
    )
    return project, gallery


def active_stream():
    live = LiveStream.objects.filter(is_active=True, is_live=True).first()
    if live:
        return live
    return LiveStream.objects.filter(is_active=True).order_by("-scheduled_at").first()


def sanitized_stream(stream):
    if stream is None:
        return None
    return SimpleNamespace(
        title=stream.title,
        description=stream.description,
        is_live=stream.is_live,
        scheduled_at=stream.scheduled_at,
        embed_url=safe_embed_url(stream.embed_url, allow_any_https_host=True),
        platform=stream.platform,
    )
