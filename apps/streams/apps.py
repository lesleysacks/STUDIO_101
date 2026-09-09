"""
Application configuration module for the STUDIO101 Live Streaming app.
"""

from django.apps import AppConfig


class StreamsConfig(AppConfig):
    """
    Configures the Live Streaming app settings and display label in Django Admin.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.streams'
    verbose_name = 'Live Broadcasts & Streaming'
