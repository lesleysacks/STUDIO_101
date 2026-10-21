import json

from django.core.management.base import BaseCommand, CommandError

from apps.siteconfig.services.errors import ConfigError
from apps.siteconfig.services.importer import apply_portfolio, apply_services, plan_portfolio, plan_services


class Command(BaseCommand):
    help = "Import JSON service or portfolio catalogs. Dry-run unless --apply is given. Never deletes records."

    def add_arguments(self, parser):
        parser.add_argument("--kind", choices=["services", "portfolio"], required=True)
        parser.add_argument("--apply", action="store_true", help="Write validated records. Existing slugs are skipped unless --update is set.")
        parser.add_argument("--update", action="store_true", help="Update text fields of existing slugs. Does not replace an uploaded image.")

    def handle(self, *args, **options):
        planners = {"services": (plan_services, apply_services), "portfolio": (plan_portfolio, apply_portfolio)}
        plan_func, apply_func = planners[options["kind"]]
        try:
            plan = apply_func(update=options["update"]) if options["apply"] else plan_func()
        except ConfigError as exc:
            for issue in exc.issues:
                self.stderr.write(str(issue))
            raise CommandError("Configuration failed validation.") from exc
        payload = {
            "kind": options["kind"],
            "applied": bool(options["apply"]),
            "update": bool(options["update"]),
            "creates": plan.creates,
            "updates": plan.updates,
            "unchanged": plan.unchanged,
            "conflicts": plan.conflicts,
            "errors": plan.errors,
        }
        self.stdout.write(json.dumps(payload, indent=2))
        if plan.errors or (options["apply"] and plan.conflicts and not options["update"]):
            raise CommandError("Import did not complete. Re-run with --update to change existing slugs, or fix the errors above.")
        if not options["apply"]:
            self.stdout.write("Dry run only. Pass --apply to write records.")
