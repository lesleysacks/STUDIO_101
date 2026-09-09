from django.db import models
from django.utils.text import slugify

class StudioSpace(models.Model):
    name = models.CharField(max_length=150, help_text="e.g. Studio 101 - Infinity Cyclorama Suite")
    slug = models.SlugField(unique=True)
    square_footage = models.PositiveIntegerField(help_text="Size in sq ft")
    ceiling_height = models.DecimalField(max_digits=4, decimal_places=1, help_text="Height in feet")
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=1300.00)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, default=8500.00)
    description = models.TextField()
    hero_image = models.ImageField(upload_to="studio/spaces/")
    is_available = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.square_footage} sq ft)"

class Equipment(models.Model):
    CATEGORY_CHOICES = [
        ('lighting', 'Profoto & RGB Lighting'),
        ('camera', 'Cinema Cameras & Lenses'),
        ('audio', 'Acoustics & Microphones'),
        ('grip', 'Grip & Set Accessories'),
    ]
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    specs = models.CharField(max_length=255, help_text="Specs, e.g. Shure SM7B, Profoto B10X")
    daily_rental_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    included_in_studio_rental = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Equipment"

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
