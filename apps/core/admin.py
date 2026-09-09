from django.contrib import admin
from .models import SiteSettings, HeroSlide, FAQ

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'tagline', 'contact_email', 'contact_phone')

    def has_add_permission(self, request):
        return False if SiteSettings.objects.exists() else True

@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'subtitle')

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'order', 'is_published')
    list_filter = ('category', 'is_published')
    list_editable = ('order', 'is_published')
    search_fields = ('question', 'answer')
