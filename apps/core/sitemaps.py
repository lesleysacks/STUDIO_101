"""
Sitemap generators for STUDIO101 public views and dynamic database entries.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.services.models import Service
from apps.portfolio.models import Project
from apps.streams.models import LiveStream


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
        return Service.objects.all()

    def location(self, item):
        return reverse('services:detail', kwargs={'slug': item.slug})


class ProjectSitemap(Sitemap):
    """Sitemap for published Portfolio case study projects."""
    priority = 0.7
    changefreq = 'monthly'

    def items(self):
        return Project.objects.filter(is_published=True)

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
