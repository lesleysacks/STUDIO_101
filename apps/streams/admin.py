"""
Django Admin interface configuration for the STUDIO101 Live Streaming app.
Provides quick toggles for live broadcast status, platform filtering, and search options.
"""

from django.contrib import admin
from .models import LiveStream


@admin.register(LiveStream)
class LiveStreamAdmin(admin.ModelAdmin):
    """
    Admin control panel customization for managing LiveStream events.

    List Display:
        Displays broadcast title, platform, live toggle state, active visibility, and schedule date.

    List Editable:
        Allows direct toggling of `is_live` and `is_active` status directly from list view.
    """

    list_display = ('title', 'platform', 'is_live', 'is_active', 'scheduled_at', 'created_at')
    list_filter = ('is_live', 'is_active', 'platform', 'scheduled_at')
    search_fields = ('title', 'description', 'embed_url')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_live', 'is_active')
    ordering = ('-is_live', '-scheduled_at')

    fieldsets = (
        ('Event Specifications', {
            'fields': ('title', 'slug', 'platform', 'scheduled_at', 'description')
        }),
        ('Iframe Configuration', {
            'fields': ('embed_url',),
            'description': 'Enter direct player embed URLs (e.g. https://www.youtube.com/embed/VIDEO_ID).'
        }),
        ('Broadcast State & Visibility', {
            'fields': ('is_live', 'is_active')
        }),
    )
