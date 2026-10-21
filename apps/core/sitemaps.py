"""
Sitemap generators for STUDIO101 public views and dynamic database entries.
"""

from types import SimpleNamespace

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.services.models import Service
from apps.portfolio.models import Project
from apps.streams.models import LiveStream
from apps.siteconfig.services.errors import ConfigError
from apps.siteconfig.services.loader import get_bundle


def _json_only(records, existing_slugs):
    extras = []
    for slug, entry in records.items():
        if slug not in existing_slugs and entry.get("published", True):
            extras.append(SimpleNamespace(slug=slug))
    return extras


class StaticViewSitemap(Sitemap):
    """Sitemap for static public pages."""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'core:home',
            'core:about',
            'core:faq',
            'core:contact',
            'services:list',
            'portfolio:list',
            'studio:overview',
            'streams:list',
            'bookings:request',
        ]

    def location(self, item):
        return reverse(item)


class ServiceSitemap(Sitemap):
    """Sitemap for dynamic Service package pages."""
    priority = 0.9
    changefreq = 'monthly'

    def items(self):
        rows = list(Service.objects.all())
        try:
            bundle = get_bundle()
        except ConfigError:
            return rows
        return rows + _json_only(bundle.services, {row.slug for row in rows})

    def location(self, item):
        return reverse('services:detail', kwargs={'slug': item.slug})


class ProjectSitemap(Sitemap):
    """Sitemap for published Portfolio case study projects."""
    priority = 0.7
    changefreq = 'monthly'

    def items(self):
        rows = list(Project.objects.filter(is_published=True))
        try:
            bundle = get_bundle()
        except ConfigError:
            return rows
        return rows + _json_only(bundle.portfolio, {row.slug for row in rows})

    def location(self, item):
        return reverse('portfolio:detail', kwargs={'slug': item.slug})


class StreamSitemap(Sitemap):
    """Sitemap for active Live Stream events."""
    priority = 0.6
    changefreq = 'daily'

    def items(self):
        return LiveStream.objects.filter(is_active=True)

    def location(self, item):
        return reverse('streams:detail', kwargs={'slug': item.slug})
