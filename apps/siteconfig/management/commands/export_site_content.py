from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.siteconfig.services.importer import export_portfolio, export_services, write_output


class Command(BaseCommand):
    help = "Export database services or portfolio items as JSON. Writes atomically when --output is set."

    def add_arguments(self, parser):
        parser.add_argument("--kind", choices=["services", "portfolio"], required=True)
        parser.add_argument("--output", help="Destination file. Omit to print JSON to stdout.")

    def handle(self, *args, **options):
        payload = export_services() if options["kind"] == "services" else export_portfolio()
        output = Path(options["output"]) if options["output"] else None
        if output and output.exists() and not options.get("force", False):
            # Export never overwrites an existing file unless the operator removes it first.
            raise CommandError(f"{output} already exists. Remove it or choose another path. Export does not overwrite.")
        text = write_output(payload, output)
        if output is None:
            self.stdout.write(text)
        else:
            self.stdout.write(f"Exported {len(payload)} record(s) to {output}.")
