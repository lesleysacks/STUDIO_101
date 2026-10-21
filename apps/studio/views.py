from apps.siteconfig.services.rendering import render_configured_page

from .models import StudioSpace, Equipment


def studio_overview_view(request):
    return render_configured_page(
        request,
        "studio",
        "pages/studio.html",
        lambda: {
            "spaces": StudioSpace.objects.filter(is_available=True),
            "equipment": Equipment.objects.all(),
        },
    )
