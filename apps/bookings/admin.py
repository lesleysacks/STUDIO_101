from django.contrib import admin
from .models import BookingRequest

@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'service_requested', 'preferred_date', 'status', 'created_at')
    list_filter = ('status', 'service_requested', 'created_at')
    search_fields = ('full_name', 'email', 'company_or_project', 'project_details')
    list_editable = ('status',)
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Contact Information', {
            'fields': ('full_name', 'email', 'phone', 'company_or_project')
        }),
        ('Booking Specifications', {
            'fields': ('service_requested', 'studio_space', 'preferred_date', 'alternate_date', 'estimated_budget', 'project_details')
        }),
        ('Status & Admin Notes', {
            'fields': ('status', 'admin_notes', 'created_at')
        }),
    )
