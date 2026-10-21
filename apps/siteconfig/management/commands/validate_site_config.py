from django.core.management.base import BaseCommand, CommandError

from apps.siteconfig.services.errors import ConfigError
from apps.siteconfig.services.loader import load_bundle, reset_cache


class Command(BaseCommand):
    help = "Validate STUDIO101 JSON configuration. Exits nonzero when validation fails."

    def add_arguments(self, parser):
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Treat warnings, including missing media files, as failures.",
        )

    def handle(self, *args, **options):
        reset_cache()
        try:
            bundle = load_bundle()
        except ConfigError as exc:
            for issue in exc.issues:
                self.stderr.write(str(issue))
            raise CommandError(f"{len(exc.issues)} configuration error(s).") from exc
        for warning in bundle.warnings:
            self.stdout.write(self.style.WARNING(str(warning)))
        if options["strict"] and bundle.warnings:
            raise CommandError(f"{len(bundle.warnings)} configuration warning(s) in strict mode.")
        self.stdout.write(self.style.SUCCESS(f"Site configuration is valid ({len(bundle.warnings)} warning(s))."))
