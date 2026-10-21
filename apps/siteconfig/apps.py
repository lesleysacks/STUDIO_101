from django.apps import AppConfig


class SiteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.siteconfig"
    verbose_name = "Site configuration"

    def ready(self) -> None:
        from . import checks  # noqa: F401
