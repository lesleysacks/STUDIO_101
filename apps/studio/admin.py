from django.contrib import admin
from .models import StudioSpace, Equipment

@admin.register(StudioSpace)
class StudioSpaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'square_footage', 'hourly_rate', 'daily_rate', 'is_available')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_available',)

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'specs', 'included_in_studio_rental', 'daily_rental_fee')
    list_filter = ('category', 'included_in_studio_rental')
    search_fields = ('name', 'specs')
