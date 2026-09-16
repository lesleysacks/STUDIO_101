"""
Tests for Core application views, SiteSettings model, site_context processor, sitemaps, and robots.txt.
"""

from django.test import TestCase, Client
from django.urls import reverse
from .models import SiteSettings, HeroSlide, FAQ


class CoreModelTests(TestCase):
    def test_site_settings_singleton(self):
        s1 = SiteSettings.objects.create(site_name="Studio Test 1")
        s2 = SiteSettings.objects.create(site_name="Studio Test 2")
        self.assertEqual(s1.pk, 1)
        self.assertEqual(s2.pk, 1)
        self.assertEqual(SiteSettings.objects.count(), 1)
        self.assertEqual(SiteSettings.objects.get(pk=1).site_name, "Studio Test 2")

    def test_hero_slide_str(self):
        slide = HeroSlide.objects.create(title="Cinematic Lighting Suite")
        self.assertEqual(str(slide), "Cinematic Lighting Suite")

    def test_faq_str(self):
        faq = FAQ.objects.create(question="Is gear included?", answer="Yes.")
        self.assertEqual(str(faq), "Is gear included?")


class CoreViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_view_status_code(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/home.html')

    def test_about_view_status_code(self):
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)

    def test_faq_view_status_code(self):
        response = self.client.get(reverse('core:faq'))
        self.assertEqual(response.status_code, 200)

    def test_contact_view_status_code(self):
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)

    def test_sitemap_xml_status_code(self):
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        self.assertIn("xml", response.headers.get("Content-Type", ""))

    def test_robots_txt_status_code(self):
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/plain", response.headers.get("Content-Type", ""))
        self.assertIn("Disallow: /admin/", response.content.decode('utf-8'))
        self.assertIn("Sitemap:", response.content.decode('utf-8'))
