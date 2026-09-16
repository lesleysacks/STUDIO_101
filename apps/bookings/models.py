"""
Models for managing client booking inquiries, session preferences, and operational triage status.
"""

from django.contrib import admin
from django.db import models


class BookingRequest(models.Model):
    id = models.AutoField(primary_key=True)
    STATUS_CHOICES = [
        ("NEW", "New"),
        ("CONTACTED", "Contacted"),
        ("QUOTED", "Quoted"),
        ("CONFIRMED", "Confirmed"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="NEW",
        help_text="Operational triage state."
    )

    # other fields like client_full_name, client_email, service_type, booking_date, created_at...





    full_name = models.CharField(max_length=150, help_text="Client full name.")
    email = models.EmailField(help_text="Client contact email address.")
    phone = models.CharField(max_length=30, help_text="Client contact phone number.")
    company_or_project = models.CharField(max_length=150, blank=True, help_text="Company or project title.")

    service_requested = models.ForeignKey(
        'services.Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Target service package selected by client."
    )
    studio_space = models.ForeignKey(
        'studio.StudioSpace',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Target studio space requested."
    )

    preferred_date = models.DateField(null=True, blank=True, help_text="Primary preferred session date.")
    alternate_date = models.DateField(null=True, blank=True, help_text="Backup session date.")
    estimated_budget = models.CharField(max_length=100, blank=True, help_text="Estimated client budget range.")
    project_details = models.TextField(help_text="Detailed description of visual concept and production scope.")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', help_text="Operational triage state.")
    admin_notes = models.TextField(blank=True, help_text="Internal studio notes.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Booking Request"
        verbose_name_plural = "Booking Requests"

    def __str__(self):
        """String representation of booking request with ID, client name, and date."""
        return f"Booking #{self.id} - {self.full_name} ({self.preferred_date or 'No date'})"
