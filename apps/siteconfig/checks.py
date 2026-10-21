"""Django system checks for the shipped configuration."""

from django.core.checks import Error, Tags, Warning, register

from .services.errors import ConfigError
from .services.loader import load_bundle


@register(Tags.compatibility)
def check_siteconfig(app_configs, **kwargs):
    try:
        bundle = load_bundle()
    except ConfigError as exc:
        return [Error(str(issue), id="siteconfig.E001") for issue in exc.issues]
    return [Warning(str(issue), id="siteconfig.W001") for issue in bundle.warnings]
