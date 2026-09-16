"""
Tests for Services application models and views.
"""

from django.test import TestCase, Client
from django.urls import reverse
from .models import ServiceCategory, Service, ServiceFeature


class ServicesModelAndCategoryTests(TestCase):
    def setUp(self):
        self.category = ServiceCategory.objects.create(name="Photography", slug="photography")
        self.service = Service.objects.create(
            category=self.category,
            title="Studio Photography Hire",
            summary="Profoto strobe infinity cyclorama suite.",
            full_description="Complete equipment access.",
            starting_price=1300.00
        )

    def test_service_creation_and_slug(self):
        self.assertEqual(self.service.slug, "studio-photography-hire")
        self.assertEqual(str(self.service), "Studio Photography Hire")
        self.assertEqual(str(self.category), "Photography")

    def test_service_feature(self):
        feature = ServiceFeature.objects.create(service=self.service, title="Profoto B10X Strobes")
        self.assertIn("Profoto", str(feature))

    def test_service_list_view(self):
        client = Client()
        response = client.get(reverse('services:list'))
        self.assertEqual(response.status_code, 200)

    def test_service_detail_view(self):
        client = Client()
        response = client.get(reverse('services:detail', kwargs={'slug': self.service.slug}))
        self.assertEqual(response.status_code, 200)
