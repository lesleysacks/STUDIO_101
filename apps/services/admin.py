"""
Admin configurations for managing service categories, packages, and inline features.
"""

from django.contrib import admin
from .models import ServiceCategory, Service, ServiceFeature


class ServiceFeatureInline(admin.TabularInline):
    """Inline manager allowing direct editing of features on a Service admin page."""
    model = ServiceFeature
    extra = 3


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    """Admin manager for ServiceCategory objects."""
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Admin manager for Service objects with inline feature configuration."""
    list_display = ('title', 'category', 'starting_price', 'is_featured', 'order')
    list_editable = ('is_featured', 'order')
    list_filter = ('category', 'is_featured')
    search_fields = ('title', 'summary', 'full_description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ServiceFeatureInline]
