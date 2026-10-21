"""Configuration loading, rendering, security, and import behaviour."""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, TestCase, override_settings

from apps.bookings.models import BookingRequest
from apps.services.models import Service, ServiceCategory
from apps.siteconfig.services import loader
from apps.siteconfig.services.errors import ConfigError
from apps.siteconfig.services.importer import apply_services, plan_services
from apps.siteconfig.services.loader import get_bundle, load_bundle, reset_cache
from apps.siteconfig.services.rendering import page_context
from apps.siteconfig.services.security import is_safe_href, is_safe_media_ref


class ConfigCopy:
    def __init__(self, source: Path):
        self._directory = tempfile.TemporaryDirectory()
        self.root = Path(self._directory.name) / "content"
        shutil.copytree(source, self.root)

    def cleanup(self):
        self._directory.cleanup()

    def write(self, relative: str, payload) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(payload, str):
            path.write_text(payload, encoding="utf-8")
        else:
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def read(self, relative: str):
        return json.loads((self.root / relative).read_text(encoding="utf-8"))


class SiteConfigTests(TestCase):
    def setUp(self):
        self.copy = ConfigCopy(Path(loader.config_root()))
        self.addCleanup(self.copy.cleanup)
        self.addCleanup(reset_cache)
        reset_cache()

    def _settings(self):
        return override_settings(SITECONFIG_ROOT=self.copy.root)

    def test_valid_configuration_loads(self):
        with self._settings():
            bundle = load_bundle()
        self.assertIn("home", bundle.pages)
        self.assertIn("photography", bundle.services)
        self.assertIn("--primary: #800020;", bundle.theme_css)

    def test_invalid_json_names_the_file(self):
        self.copy.write("site.json", "{")
        with self._settings():
            with self.assertRaises(ConfigError) as caught:
                load_bundle()
        self.assertIn("site.json", str(caught.exception))
        self.assertIn("Invalid JSON", str(caught.exception))

    def test_schema_violation_reports_path(self):
        theme = self.copy.read("theme.json")
        theme["colors"]["primary"] = "burgundy"
        self.copy.write("theme.json", theme)
        with self._settings():
            with self.assertRaises(ConfigError) as caught:
                load_bundle()
        self.assertIn("theme.json", str(caught.exception))
        self.assertIn("$.colors.primary", str(caught.exception))

    def test_unknown_component_type_is_rejected(self):
        with self._settings():
            with patch.dict(loader.COMPONENTS, {"hero": None}):
                with self.assertRaises(ConfigError) as caught:
                    load_bundle()
        self.assertIn("Unknown component type 'hero'", str(caught.exception))

    def test_missing_required_field_is_reported(self):
        page = self.copy.read("pages/about.json")
        del page["title"]
        self.copy.write("pages/about.json", page)
        with self._settings():
            with self.assertRaises(ConfigError) as caught:
                load_bundle()
        self.assertIn("pages/about.json", str(caught.exception))
        self.assertIn("$.title", str(caught.exception))
        self.assertIn("required", str(caught.exception))

    def test_defaults_and_page_overrides(self):
        page = self.copy.read("pages/services.json")
        grid = next(section for section in page["sections"] if section["id"] == "services-grid")
        del grid["settings"]["columns"]
        del grid["settings"]["limit"]
        self.copy.write("pages/services.json", page)
        with self._settings():
            bundle = load_bundle()
        services = next(section for section in bundle.pages["services"]["sections"] if section["id"] == "services-grid")
        home = next(section for section in bundle.pages["home"]["sections"] if section["id"] == "home-services")
        self.assertEqual(services["settings"]["columns"], 3)
        self.assertEqual(services["settings"]["limit"], 12)
        self.assertEqual(services["settings"]["source"], "published_services")
        self.assertEqual(home["settings"]["source"], "featured_services")
        self.assertEqual(home["settings"]["limit"], 3)

    def test_section_order_and_disabled_sections(self):
        page = self.copy.read("pages/home.json")
        page["sections"][2]["enabled"] = False
        disabled_heading = page["sections"][2]["settings"]["heading"]
        self.copy.write("pages/home.json", page)
        with self._settings():
            context = page_context("home")
        ids = [section["id"] for section in context["sections"]]
        self.assertEqual(ids, ["home-hero", "home-stream", "home-services", "home-portfolio", "booking-cta"])
        self.assertNotIn(disabled_heading, " ".join(section["data"].get("heading", "") for section in context["sections"]))

    def test_theme_css_uses_validated_tokens(self):
        theme = self.copy.read("theme.json")
        theme["colors"]["primary"] = "#112233"
        theme["layout"]["content_width"] = "960px"
        self.copy.write("theme.json", theme)
        with self._settings():
            bundle = load_bundle()
        self.assertIn("--primary: #112233;", bundle.theme_css)
        self.assertIn("--site-content-width: 960px;", bundle.theme_css)
        self.assertNotIn("expression", bundle.theme_css)

    def test_missing_media_is_a_warning_until_strict(self):
        page = self.copy.read("pages/home.json")
        page["sections"][0]["settings"]["image"] = "ASSETS/IMAGES/does-not-exist.png"
        self.copy.write("pages/home.json", page)
        with self._settings():
            bundle = load_bundle()
            self.assertTrue(any("does-not-exist.png" in issue.message or "not found" in issue.message for issue in bundle.warnings))
            with self.assertRaises(CommandError):
                call_command("validate_site_config", "--strict")

    def test_unsafe_media_and_urls_fail(self):
        self.assertFalse(is_safe_media_ref("../secret.png"))
        self.assertFalse(is_safe_href("javascript:alert(1)"))
        page = self.copy.read("pages/home.json")
        page["sections"][0]["settings"]["image"] = "../secret.png"
        page["sections"][0]["settings"]["primary_cta"]["href"] = "javascript:alert(1)"
        self.copy.write("pages/home.json", page)
        with self._settings():
            with self.assertRaises(ConfigError) as caught:
                load_bundle()
        message = str(caught.exception)
        self.assertIn("Media path", message)
        self.assertIn("URL must be", message)

    def test_cache_invalidation_and_last_valid_bundle(self):
        with self._settings():
            first = get_bundle()
            self.assertEqual(first.pages["home"]["title"], "Studio 101")
            page = self.copy.read("pages/home.json")
            page["title"] = "Studio Updated"
            self.copy.write("pages/home.json", page)
            second = get_bundle()
            self.assertEqual(second.pages["home"]["title"], "Studio Updated")
            self.copy.write("site.json", "{")
            retained = get_bundle()
            self.assertEqual(retained.pages["home"]["title"], "Studio Updated")
            with self.assertRaises(ConfigError):
                load_bundle()

    def test_malicious_content_is_escaped_and_not_executed(self):
        page = self.copy.read("pages/about.json")
        page["sections"][0]["settings"]["heading"] = "<script>alert(1)</script>"
        page["sections"][0]["settings"]["paragraphs"] = ["__EVAL__{{ 7|add:7 }}"]
        self.copy.write("pages/about.json", page)
        with self._settings():
            response = Client().get("/about/")
        self.assertContains(response, "&lt;script&gt;alert(1)&lt;/script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertContains(response, "__EVAL__{{ 7|add:7 }}")

    def test_extra_template_field_is_rejected(self):
        page = self.copy.read("pages/about.json")
        page["sections"][0]["template"] = "pages/home.html"
        self.copy.write("pages/about.json", page)
        with self._settings():
            with self.assertRaises(ConfigError) as caught:
                load_bundle()
        self.assertIn("Unknown field", str(caught.exception))

    def test_unpublished_page_uses_legacy_template(self):
        page = self.copy.read("pages/faq.json")
        page["published"] = False
        self.copy.write("pages/faq.json", page)
        with self._settings():
            response = Client().get("/faq/")
        self.assertTemplateUsed(response, "pages/faq.html")

    def test_diagnostics_require_staff_and_reject_writes(self):
        anonymous = Client()
        self.assertEqual(anonymous.get("/site-config/diagnostics/").status_code, 302)
        user = get_user_model().objects.create_user("editor", "editor@example.com", "correct-horse")
        user.is_staff = True
        user.save()
        staff = Client()
        staff.force_login(user)
        self.assertEqual(staff.get("/site-config/diagnostics/").status_code, 200)
        self.assertEqual(staff.post("/site-config/diagnostics/").status_code, 405)

    def test_validate_command_succeeds_for_shipped_config(self):
        reset_cache()
        call_command("validate_site_config", "--strict")

    def test_json_service_detail_and_database_precedence(self):
        response = Client().get("/services/photography/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Studio Photography")
        self.assertContains(response, "Profoto strobe lighting")
        category = ServiceCategory.objects.create(name="Photography", slug="photography-db")
        Service.objects.create(
            category=category,
            title="Database Wins",
            slug="photography",
            summary="From the database.",
            full_description="Database copy.",
        )
        response = Client().get("/services/photography/")
        self.assertContains(response, "Database Wins")
        self.assertNotContains(response, "Profoto strobe lighting")

    def test_import_is_dry_run_until_apply_and_does_not_clobber(self):
        reset_cache()
        plan = plan_services()
        self.assertIn("photography", plan.creates)
        self.assertEqual(Service.objects.filter(slug="photography").count(), 0)
        apply_services(update=False)
        service = Service.objects.get(slug="photography")
        self.assertEqual(service.title, "Studio Photography")
        self.assertTrue(service.features.filter(title="Profoto strobe lighting").exists())
        again = plan_services()
        self.assertIn("photography", again.unchanged)
        service.title = "Custom admin title"
        service.save()
        conflicted = plan_services()
        self.assertIn("photography", conflicted.conflicts)
        apply_services(update=False)
        service.refresh_from_db()
        self.assertEqual(service.title, "Custom admin title")
        kept = Service.objects.create(
            title="Manual Only",
            slug="manual-only",
            summary="Kept.",
            full_description="Kept.",
        )
        apply_services(update=True)
        service.refresh_from_db()
        self.assertEqual(service.title, "Studio Photography")
        self.assertTrue(Service.objects.filter(pk=kept.pk).exists())

    def test_sitemap_omits_private_bookings(self):
        BookingRequest.objects.create(
            full_name="Private Client",
            email="private@example.com",
            phone="123",
            project_details="Confidential shoot",
        )
        response = Client().get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "private@example.com")
        self.assertContains(response, "/services/photography/")

    def test_honeypot_rejects_spam(self):
        response = Client().post(
            "/book/",
            {
                "full_name": "Spam Bot",
                "email": "spam@example.com",
                "phone": "000",
                "project_details": "Buy now",
                "honeypot": "filled",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(BookingRequest.objects.filter(email="spam@example.com").exists())

    def test_public_pages_still_render(self):
        client = Client()
        for path in ("/", "/about/", "/services/", "/portfolio/", "/studio/", "/contact/", "/faq/", "/book/", "/streams/"):
            response = client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertContains(response, "STUDIO")
            self.assertContains(response, 'id="site-theme"')
