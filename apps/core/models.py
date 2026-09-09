from django.db import models

class SiteSettings(models.Model):
    """Singleton configuration model for studio settings, SEO defaults, and branding."""
    site_name = models.CharField(max_length=100, default="STUDIO 101")
    tagline = models.CharField(max_length=255, default="Luxury Creative Production Studio")
    subbrand_text = models.CharField(max_length=255, default="Canwill-Smith Photography Presents")
    hero_title = models.CharField(max_length=255, default="The New Face of Creative Space")
    hero_description = models.TextField(
        default="An ultra-premium luxury facility engineered for high-end photography, dynamic music video sets, soundproof podcast recordings, and corporate advertisement productions."
    )
    contact_email = models.EmailField(default="info@studio101.co.za")
    contact_phone = models.CharField(max_length=50, default="+27 (0) 82 101 9900")
    address = models.TextField(default="Studio 101, Creative Quarter")
    instagram_url = models.URLField(blank=True, default="https://instagram.com")
    vimeo_url = models.URLField(blank=True, default="https://vimeo.com")
    youtube_url = models.URLField(blank=True, default="https://youtube.com")

    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"

    def save(self, *args, **kwargs):
        self.pk = 1  # Force singleton
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.site_name} Configuration"

class HeroSlide(models.Model):
    """Carousel / video items for main hero displays."""
    title = models.CharField(max_length=150)
    subtitle = models.CharField(max_length=255, blank=True)
    video_url = models.URLField(blank=True, help_text="Direct link to MP4 or Vimeo video stream")
    image = models.ImageField(upload_to="hero/", help_text="Background hero image asset")
    cta_primary_text = models.CharField(max_length=50, default="Explore Facilities")
    cta_primary_link = models.CharField(max_length=200, default="/services/")
    cta_secondary_text = models.CharField(max_length=50, default="Reserve Session")
    cta_secondary_link = models.CharField(max_length=200, default="/book/")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General Info'),
        ('booking', 'Bookings & Packages'),
        ('technical', 'Technical Specs & Gear'),
    ]
    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question
