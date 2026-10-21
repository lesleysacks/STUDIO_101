"""Staff-only configuration diagnostics. This view does not edit files."""

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseNotAllowed
from django.shortcuts import render

from .services.errors import ConfigError
from .services.loader import load_bundle


@staff_member_required
def diagnostics_view(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    errors = []
    warnings = []
    try:
        bundle = load_bundle()
        warnings = bundle.warnings
        page_count = len(bundle.pages)
        service_count = len(bundle.services)
    except ConfigError as exc:
        errors = exc.issues
        page_count = 0
        service_count = 0
    return render(
        request,
        "siteconfig/diagnostics.html",
        {
            "config_errors": errors,
            "config_warnings": warnings,
            "page_count": page_count,
            "service_count": service_count,
        },
    )
