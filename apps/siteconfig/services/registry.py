"""Explicit component registry. JSON may select these types and nothing else."""

from __future__ import annotations

COMPONENTS: dict[str, dict[str, str]] = {
    "hero": {"template": "siteconfig/components/hero.html", "schema": "hero.schema.json"},
    "rich_text": {"template": "siteconfig/components/rich_text.html", "schema": "rich_text.schema.json"},
    "text_image": {"template": "siteconfig/components/text_image.html", "schema": "text_image.schema.json"},
    "feature_grid": {"template": "siteconfig/components/feature_grid.html", "schema": "feature_grid.schema.json"},
    "service_grid": {"template": "siteconfig/components/service_grid.html", "schema": "service_grid.schema.json"},
    "portfolio_gallery": {
        "template": "siteconfig/components/portfolio_gallery.html",
        "schema": "portfolio_gallery.schema.json",
    },
    "video_embed": {"template": "siteconfig/components/video_embed.html", "schema": "video_embed.schema.json"},
    "pricing": {"template": "siteconfig/components/pricing.html", "schema": "pricing.schema.json"},
    "faq": {"template": "siteconfig/components/faq.html", "schema": "faq.schema.json"},
    "cta": {"template": "siteconfig/components/cta.html", "schema": "cta.schema.json"},
    "contact_enquiry": {"template": "siteconfig/components/contact_enquiry.html", "schema": "contact_enquiry.schema.json"},
    "booking_enquiry": {"template": "siteconfig/components/booking_enquiry.html", "schema": "booking_enquiry.schema.json"},
    "studio_facilities": {
        "template": "siteconfig/components/studio_facilities.html",
        "schema": "studio_facilities.schema.json",
    },
    "live_stream": {"template": "siteconfig/components/live_stream.html", "schema": "live_stream.schema.json"},
    "image_banner": {"template": "siteconfig/components/image_banner.html", "schema": "image_banner.schema.json"},
}

SERVICE_SOURCES = ("featured_services", "published_services")
PROJECT_SOURCES = ("featured_projects", "published_projects")
FAQ_SOURCES = ("published_faqs",)
FACILITY_SOURCES = ("available_spaces",)
STREAM_SOURCES = ("active_stream",)
