"""
Models for managing studio production services, pricing tiers, and feature bullet lists.
"""

from django.db import models
from django.utils.text import slugify


class ServiceCategory(models.Model):
    """
    Groups studio offerings into operational domains (e.g. Photography, Podcast, Music & Ads).
    """
    name = models.CharField(max_length=100, help_text="Display name for the category.")
    slug = models.SlugField(unique=True, help_text="URL slug identifier.")
    icon_svg = models.TextField(blank=True, help_text="Optional inline SVG XML icon code.")
    description = models.TextField(blank=True, help_text="Summary of services under this category.")

    class Meta:
        verbose_name_plural = "Service Categories"

    def __str__(self):
        return self.name


class Service(models.Model):
    """
    Represents an individual production service or rental package offered by STUDIO101.

    Fields:
        category (ForeignKey): Associated ServiceCategory.
        title (CharField): Service title.
        slug (SlugField): Unique URL slug.
        summary (TextField): Concise excerpt displayed on service grid cards.
        full_description (TextField): Complete breakdown of equipment and session scope.
        featured_image (ImageField): Service banner card image.
        starting_price (DecimalField): Base monetary rate in ZAR.
        price_unit (CharField): Rate duration descriptor (e.g. 'per project').
        duration_label (CharField): Human-readable session length (e.g. '1 Hour 30 Mins').
        is_featured (BooleanField): Display on homepage showcase.
        order (PositiveIntegerField): Sort order priority.
    """
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, related_name='services')
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    summary = models.TextField(help_text="Short description for grid cards")
    full_description = models.TextField()
    featured_image = models.ImageField(upload_to="services/")
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_unit = models.CharField(max_length=50, default="per project", blank=True)
    duration_label = models.CharField(max_length=50, default="1 Hour 30 Mins", blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'title']

    def save(self, *args, **kwargs):
        """Auto-populates slug field if left blank."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ServiceFeature(models.Model):
    """
    Detailed feature bullet items included within a specific Service package.
    """
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='features')
    title = models.CharField(max_length=150, help_text="Feature bullet title.")
    description = models.CharField(max_length=255, blank=True, help_text="Detailed specification.")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.service.title} - {self.title}"
