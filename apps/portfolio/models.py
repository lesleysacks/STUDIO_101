"""
Models for managing portfolio case studies, client categories, and project image galleries.
"""

from django.db import models
from django.utils.text import slugify


class ProjectCategory(models.Model):
    """Categorizes portfolio projects (e.g. Commercial, Music Video, Editorial, Podcast)."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Project Categories"

    def __str__(self):
        return self.name


class Project(models.Model):
    """
    Represents a client case study or studio showcase project.

    Fields:
        title (CharField): Project title.
        slug (SlugField): Unique URL slug.
        client_name (CharField): Brand or artist name.
        category (ForeignKey): Associated ProjectCategory.
        cover_image (ImageField): Primary thumbnail asset.
        showcase_video_url (URLField): External video reel URL.
        summary (CharField): Short card excerpt.
        description (TextField): Detailed case study breakdown.
        is_featured (BooleanField): Display on homepage showcase.
        is_published (BooleanField): Visibility toggle.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    client_name = models.CharField(max_length=100, blank=True, help_text="e.g. Nike, Red Bull, Canwill-Smith")
    category = models.ForeignKey(ProjectCategory, on_delete=models.CASCADE, related_name='projects')
    cover_image = models.ImageField(upload_to="portfolio/covers/")
    showcase_video_url = models.URLField(blank=True, help_text="Vimeo or YouTube showreel link")
    summary = models.CharField(max_length=300)
    description = models.TextField()
    completion_date = models.DateField(null=True, blank=True)
    is_featured = models.BooleanField(default=False, help_text="Highlight on homepage showcase")
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def save(self, *args, **kwargs):
        """Auto-populates slug field if left blank."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.client_name})" if self.client_name else self.title


class ProjectImage(models.Model):
    """Gallery image asset associated with a Project case study."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to="portfolio/gallery/")
    caption = models.CharField(max_length=255, blank=True)
    is_full_width = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Gallery Image {self.id} for {self.project.title}"
