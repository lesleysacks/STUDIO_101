"""
Models for managing live stream broadcasts, iframe embed URLs, and scheduled events.

Developers & Admins:
    To add a new stream provider (e.g., YouTube, Facebook Live, Twitch, or Custom RTMP):
    1. Select the platform in Django Admin.
    2. Input the direct iframe embed URL in the `embed_url` field:
       - YouTube: https://www.youtube.com/embed/VIDEO_ID
       - Facebook: https://www.facebook.com/plugins/video.php?href=VIDEO_URL
       - Twitch: https://player.twitch.tv/?channel=CHANNEL_NAME&parent=YOUR_DOMAIN
       - Custom Embed: Direct HTTP/S player endpoint.
    3. Toggle `is_live` to True to display the stream live on the homepage hero or broadcast component.
"""

from django.db import models
from django.utils.text import slugify


class LiveStream(models.Model):
    """
    Stores live stream metadata and embedded iframe configurations for dynamic rendering.
    Supports platforms such as YouTube Live, Facebook Live, Twitch, and custom RTMP providers.

    Fields:
        title (CharField): Title of the live broadcast event.
        slug (SlugField): URL-safe slug for deep-linking (auto-populated if blank).
        platform (CharField): Selected broadcast provider platform.
        embed_url (URLField): Direct HTTP/HTTPS iframe source URL.
        description (TextField): Detailed event summary or broadcast itinerary.
        scheduled_at (DateTimeField): Expected broadcast start date and time.
        is_live (BooleanField): Toggle to mark stream as actively broadcasting live on frontend.
        is_active (BooleanField): Global visibility toggle to enable or hide the event listing.
        created_at (DateTimeField): Auto timestamp of record creation.
    """

    PLATFORM_CHOICES = [
        ('youtube', 'YouTube Live'),
        ('facebook', 'Facebook Live'),
        ('custom', 'Custom Embed / Other'),
    ]

    title = models.CharField(
        max_length=200, 
        help_text="Title of the live broadcast event."
    )
    slug = models.SlugField(
        unique=True, 
        help_text="URL-friendly identifier (e.g., 'summer-session-2026')."
    )
    platform = models.CharField(
        max_length=20, 
        choices=PLATFORM_CHOICES, 
        default='youtube'
    )
    embed_url = models.URLField(
        help_text="The direct embed URL for the iframe (e.g., 'https://www.youtube.com/embed/VIDEO_ID')."
    )
    description = models.TextField(
        blank=True, 
        help_text="Brief summary or description of the stream content."
    )
    scheduled_at = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Scheduled broadcast date and time."
    )
    is_live = models.BooleanField(
        default=False, 
        help_text="Toggle to display as currently live on the frontend."
    )
    is_active = models.BooleanField(
        default=True, 
        help_text="Toggle visibility on the website."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_live', '-scheduled_at']
        verbose_name = "Live Stream"
        verbose_name_plural = "Live Streams"

    def save(self, *args, **kwargs):
        """Auto-populates slug field if left blank prior to saving."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        """String representation showing current live broadcast status and title."""
        status = "LIVE" if self.is_live else "Scheduled/Archived"
        return f"[{status}] {self.title}"
