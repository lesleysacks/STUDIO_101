"""Resolve validated sections into template context. Templates stay on the registry."""

from __future__ import annotations

import logging

from django.shortcuts import render

from .errors import ConfigError

from apps.bookings.forms import BookingRequestForm
from apps.core.models import FAQ, HeroSlide, SiteSettings
from apps.studio.models import Equipment, StudioSpace

from .catalog import (
    active_stream,
    fallback_cards,
    merged_projects,
    merged_services,
    sanitized_stream,
)
from .loader import SiteBundle, get_bundle
from .registry import COMPONENTS
from .security import css_background_url, public_static_url, safe_embed_url

logger = logging.getLogger("apps.siteconfig")


def _site_settings() -> SiteSettings:
    settings_row, _created = SiteSettings.objects.get_or_create(pk=1)
    return settings_row


def resolve_hero(settings: dict, bundle: SiteBundle) -> dict:
    slide = HeroSlide.objects.filter(is_active=True).order_by("order").first()
    site_settings = _site_settings()
    image_url = ""
    if slide and slide.image:
        image_url = css_background_url(slide.image.url)
    if not image_url:
        image_url = public_static_url(settings.get("image", ""))
    heading = settings.get("heading") or site_settings.hero_title
    description = settings.get("description") or site_settings.hero_description
    primary = dict(settings.get("primary_cta") or {})
    secondary = dict(settings.get("secondary_cta") or {})
    if slide:
        heading = slide.title or heading
        description = slide.subtitle or description
        if slide.cta_primary_text:
            primary["label"] = slide.cta_primary_text
        if slide.cta_primary_link:
            primary["href"] = slide.cta_primary_link
        if slide.cta_secondary_text:
            secondary["label"] = slide.cta_secondary_text
        if slide.cta_secondary_link:
            secondary["href"] = slide.cta_secondary_link
    return {
        "variant": settings.get("variant", "banner"),
        "eyebrow": settings.get("eyebrow", ""),
        "heading": heading,
        "description": description,
        "alignment": settings.get("alignment", "left"),
        "image_url": image_url,
        "image_alt": settings.get("image_alt") or heading,
        "primary_cta": primary,
        "secondary_cta": secondary,
    }


def resolve_rich_text(settings: dict, bundle: SiteBundle) -> dict:
    return {"heading": settings.get("heading", ""), "paragraphs": settings.get("paragraphs", [])}


def resolve_text_image(settings: dict, bundle: SiteBundle) -> dict:
    return {
        "eyebrow": settings.get("eyebrow", ""),
        "heading": settings.get("heading", ""),
        "paragraphs": settings.get("paragraphs", []),
        "image_url": public_static_url(settings.get("image", "")),
        "image_alt": settings.get("image_alt", ""),
        "cta_label": settings.get("cta_label", ""),
        "cta_href": settings.get("cta_href", ""),
        "image_position": settings.get("image_position", "right"),
    }


def resolve_feature_grid(settings: dict, bundle: SiteBundle) -> dict:
    items = []
    for item in settings.get("items", []):
        icon = item.get("icon", "")
        items.append(
            {
                "icon_class": f"fas {icon}" if icon else "",
                "title": item.get("title", ""),
                "text": item.get("text", ""),
            }
        )
    return {
        "eyebrow": settings.get("eyebrow", ""),
        "heading": settings.get("heading", ""),
        "intro": settings.get("intro", ""),
        "items": items,
    }


def resolve_service_grid(settings: dict, bundle: SiteBundle) -> dict:
    featured = settings.get("source") == "featured_services"
    items = merged_services(bundle.services, featured_only=featured, limit=settings.get("limit", 12))
    if not items:
        items = fallback_cards(settings.get("fallback_items", []))
    return {
        "eyebrow": settings.get("eyebrow", ""),
        "heading": settings.get("heading", ""),
        "intro": settings.get("intro", ""),
        "columns": settings.get("columns", 3),
        "items": items,
    }


def resolve_portfolio_gallery(settings: dict, bundle: SiteBundle) -> dict:
    featured = settings.get("source") == "featured_projects"
    items = merged_projects(bundle.portfolio, featured_only=featured, limit=settings.get("limit", 12))
    if not items:
        items = fallback_cards(settings.get("fallback_items", []))
    return {
        "eyebrow": settings.get("eyebrow", ""),
        "heading": settings.get("heading", ""),
        "intro": settings.get("intro", ""),
        "items": items,
    }


def resolve_video_embed(settings: dict, bundle: SiteBundle) -> dict:
    return {
        "heading": settings.get("heading", ""),
        "intro": settings.get("intro", ""),
        "title": settings.get("title") or settings.get("heading", "Video"),
        "embed_url": safe_embed_url(settings.get("url", ""), allow_any_https_host=False),
    }


def resolve_pricing(settings: dict, bundle: SiteBundle) -> dict:
    return {
        "eyebrow": settings.get("eyebrow", ""),
        "heading": settings.get("heading", ""),
        "intro": settings.get("intro", ""),
        "plans": settings.get("plans", []),
    }


def resolve_faq(settings: dict, bundle: SiteBundle) -> dict:
    if settings.get("source") == "published_faqs":
        rows = [
            {"question": faq.question, "answer": faq.answer}
            for faq in FAQ.objects.filter(is_published=True).order_by("order")
        ]
    else:
        rows = []
    if not rows:
        rows = [{"question": item.get("question", ""), "answer": item.get("answer", "")} for item in settings.get("items", [])]
    return {"eyebrow": settings.get("eyebrow", ""), "heading": settings.get("heading", ""), "intro": settings.get("intro", ""), "items": rows}


def resolve_cta(settings: dict, bundle: SiteBundle) -> dict:
    return {
        "eyebrow": settings.get("eyebrow", ""),
        "heading": settings.get("heading", ""),
        "text": settings.get("text", ""),
        "primary_cta": settings.get("primary_cta") or {},
        "secondary_cta": settings.get("secondary_cta") or {},
    }


def resolve_contact_enquiry(settings: dict, bundle: SiteBundle) -> dict:
    site_settings = _site_settings()
    return {
        "eyebrow": settings.get("eyebrow", ""),
        "heading": settings.get("heading", ""),
        "intro": settings.get("intro", ""),
        "hours": settings.get("hours", ""),
        "email": site_settings.contact_email,
        "phone": site_settings.contact_phone,
        "address": site_settings.address,
        "form": BookingRequestForm(),
    }


def resolve_booking_enquiry(settings: dict, bundle: SiteBundle) -> dict:
    return {
        "eyebrow": settings.get("eyebrow", ""),
        "heading": settings.get("heading", ""),
        "intro": settings.get("intro", ""),
        "form": BookingRequestForm(),
    }


def resolve_studio_facilities(settings: dict, bundle: SiteBundle) -> dict:
    spaces = []
    if settings.get("source") == "available_spaces":
        for space in StudioSpace.objects.filter(is_available=True):
            spaces.append(
                {
                    "title": space.name,
                    "text": space.description,
                    "meta": f"{space.square_footage} sq ft · {space.ceiling_height} ft ceiling",
                }
            )
    equipment = [
        {"title": item.name, "text": item.specs, "category": item.get_category_display()}
        for item in Equipment.objects.all()
    ]
    return {
        "eyebrow": settings.get("eyebrow", ""),
        "heading": settings.get("heading", ""),
        "intro": settings.get("intro", ""),
        "spaces": spaces or settings.get("fallback_spaces", []),
        "equipment_heading": settings.get("equipment_heading", ""),
        "equipment": equipment or settings.get("fallback_equipment", []),
    }


def resolve_live_stream(settings: dict, bundle: SiteBundle) -> dict:
    stream = sanitized_stream(active_stream()) if settings.get("source") == "active_stream" else None
    return {
        "eyebrow": settings.get("eyebrow", ""),
        "heading": settings.get("heading", ""),
        "intro": settings.get("intro", ""),
        "stream": stream,
    }


def resolve_image_banner(settings: dict, bundle: SiteBundle) -> dict:
    return {
        "heading": settings.get("heading", ""),
        "image_url": public_static_url(settings.get("image", "")),
        "image_alt": settings.get("image_alt", ""),
        "caption": settings.get("caption", ""),
    }


RESOLVERS = {
    "hero": resolve_hero,
    "rich_text": resolve_rich_text,
    "text_image": resolve_text_image,
    "feature_grid": resolve_feature_grid,
    "service_grid": resolve_service_grid,
    "portfolio_gallery": resolve_portfolio_gallery,
    "video_embed": resolve_video_embed,
    "pricing": resolve_pricing,
    "faq": resolve_faq,
    "cta": resolve_cta,
    "contact_enquiry": resolve_contact_enquiry,
    "booking_enquiry": resolve_booking_enquiry,
    "studio_facilities": resolve_studio_facilities,
    "live_stream": resolve_live_stream,
    "image_banner": resolve_image_banner,
}


def prepare_sections(bundle: SiteBundle, page: dict) -> list[dict]:
    prepared = []
    for section in page.get("sections", []):
        if not section.get("enabled", True):
            continue
        component = COMPONENTS[section["type"]]
        settings = section.get("settings") or {}
        prepared.append(
            {
                "id": section["id"],
                "type": section["type"],
                "template": component["template"],
                "settings": settings,
                "data": RESOLVERS[section["type"]](settings, bundle),
            }
        )
    return prepared


def page_context(slug: str) -> dict | None:
    bundle = get_bundle()
    if not bundle.site.get("use_json_pages", True):
        return None
    page = bundle.pages.get(slug)
    if page is None or not page.get("published", True):
        return None
    seo = page.get("seo") or {}
    return {
        "page": page,
        "sections": prepare_sections(bundle, page),
        "page_title": seo.get("title") or page.get("title", ""),
        "page_description": seo.get("description", ""),
    }


def render_configured_page(request, slug: str, fallback_template: str, fallback_context):
    """Render a validated page, or the existing template when configuration cannot."""
    try:
        context = page_context(slug)
    except ConfigError:
        logger.exception("Configured page %s could not be loaded.", slug)
        context = None
    if context is None:
        return render(request, fallback_template, fallback_context())
    return render(request, "siteconfig/page.html", context)
