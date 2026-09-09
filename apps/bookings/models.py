from django.db import models

class BookingRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('contacted', 'Client Contacted'),
        ('confirmed', 'Confirmed & Scheduled'),
        ('declined', 'Declined / Unavailable'),
    ]
    
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    company_or_project = models.CharField(max_length=150, blank=True)
    
    service_requested = models.ForeignKey('services.Service', on_delete=models.SET_NULL, null=True, blank=True)
    studio_space = models.ForeignKey('studio.StudioSpace', on_delete=models.SET_NULL, null=True, blank=True)
    
    preferred_date = models.DateField(null=True, blank=True)
    alternate_date = models.DateField(null=True, blank=True)
    estimated_budget = models.CharField(max_length=100, blank=True, help_text="e.g., R1,300 - R5,000")
    project_details = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, help_text="Internal studio notes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking #{self.id} - {self.full_name} ({self.preferred_date or 'No date'})"
