"""
Tests for Live Streaming app models and views.
"""

from django.test import TestCase, Client
from django.urls import reverse
from .models import LiveStream


class LiveStreamModelTests(TestCase):
    def setUp(self):
        self.stream = LiveStream.objects.create(
            title="Live Summer Showcase 2026",
            platform="youtube",
            embed_url="https://www.youtube.com/embed/dQw4w9WgXcQ",
            description="Live studio session stream.",
            is_live=True,
            is_active=True
        )

    def test_live_stream_str_and_slug(self):
        self.assertEqual(self.stream.slug, "live-summer-showcase-2026")
        self.assertIn("[LIVE]", str(self.stream))

    def test_stream_list_view(self):
        client = Client()
        response = client.get(reverse('streams:list'))
        self.assertEqual(response.status_code, 200)

    def test_stream_detail_view(self):
        client = Client()
        response = client.get(reverse('streams:detail', kwargs={'slug': self.stream.slug}))
        self.assertEqual(response.status_code, 200)
