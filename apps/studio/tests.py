"""
Tests for Studio facilities and equipment models/views.
"""

from django.test import TestCase, Client
from django.urls import reverse
from .models import StudioSpace, Equipment


class StudioModelTests(TestCase):
    def setUp(self):
        self.space = StudioSpace.objects.create(
            name="Studio 101 Cyclorama Suite",
            square_footage=1200,
            ceiling_height=16.5,
            hourly_rate=1300.00,
            daily_rate=8500.00,
            description="Full white infinity cyclorama curve."
        )

    def test_studio_space(self):
        self.assertEqual(self.space.slug, "studio-101-cyclorama-suite")
        self.assertIn("1200 sq ft", str(self.space))

    def test_equipment(self):
        gear = Equipment.objects.create(name="Profoto B10X", category="lighting", specs="500Ws Flash")
        self.assertIn("Profoto", str(gear))

    def test_studio_overview_view(self):
        client = Client()
        response = client.get(reverse('studio:overview'))
        self.assertEqual(response.status_code, 200)
