from .models import SiteSettings

def site_context(request):
    """Global context processor providing site configuration to all templates."""
    try:
        settings = SiteSettings.objects.get(pk=1)
    except SiteSettings.DoesNotExist:
        settings = SiteSettings.objects.create()

    return {
        'site_settings': settings
    }
