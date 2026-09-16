"""
Tests for Portfolio application models and views.
"""

from django.test import TestCase, Client
from django.urls import reverse
from .models import ProjectCategory, Project, ProjectImage


class PortfolioModelAndCategoryTests(TestCase):
    def setUp(self):
        self.category = ProjectCategory.objects.create(name="Commercial", slug="commercial")
        self.project = Project.objects.create(
            title="Red Bull Campaign",
            client_name="Red Bull",
            category=self.category,
            summary="High energy action shoot.",
            description="Complete commercial production breakdown.",
            is_published=True
        )

    def test_project_slug_and_str(self):
        self.assertEqual(self.project.slug, "red-bull-campaign")
        self.assertEqual(str(self.project), "Red Bull Campaign (Red Bull)")

    def test_portfolio_list_view(self):
        client = Client()
        response = client.get(reverse('portfolio:list'))
        self.assertEqual(response.status_code, 200)

    def test_portfolio_detail_view(self):
        client = Client()
        response = client.get(reverse('portfolio:detail', kwargs={'slug': self.project.slug}))
        self.assertEqual(response.status_code, 200)
