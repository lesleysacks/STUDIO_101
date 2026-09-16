from django.contrib import admin
from .models import BookingRequest

@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "service_requested", "preferred_date", "status", "created_at")
    list_filter = ("status", "service_requested", "preferred_date")
    search_fields = ("full_name", "email", "phone")
