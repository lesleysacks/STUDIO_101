"""
Views for handling service package listings and individual service detail views.
"""

from django.http import Http404
from django.shortcuts import render

from apps.siteconfig.services.catalog import json_service_namespace
from apps.siteconfig.services.errors import ConfigError
from apps.siteconfig.services.loader import get_bundle
from apps.siteconfig.services.rendering import render_configured_page

from .models import Service, ServiceCategory


def _services_context():
    return {
        "services": Service.objects.all().order_by("order"),
        "categories": ServiceCategory.objects.all(),
    }


def service_list_view(request):
    """
    Renders the main services directory page listing all active service packages.
    """
    return render_configured_page(request, "services", "pages/services_list.html", _services_context)


def service_detail_view(request, slug):
    """
    Renders detailed specifications and features for a single target service package.

    Database rows win when a slug exists. Otherwise a published JSON catalog entry is used.

    Args:
        slug (str): Unique URL identifier for the target service.
    """
    service = Service.objects.filter(slug=slug).first()
    if service is not None:
        features = service.features.all().order_by("order")
        return render(request, "pages/service_detail.html", {
            "service": service,
            "features": features,
        })
    try:
        bundle = get_bundle()
    except ConfigError as exc:
        raise Http404("Service not found") from exc
    entry = bundle.services.get(slug)
    if entry is None or not entry.get("published", True):
        raise Http404("Service not found")
    service, features = json_service_namespace(entry)
    seo = entry.get("seo") or {}
    return render(request, "pages/service_detail.html", {
        "service": service,
        "features": features,
        "page_title": seo.get("title") or service.title,
        "page_description": seo.get("description") or service.summary,
    })
