"""
Utility functions for the Bookings application, handling studio email notifications and client acknowledgements.
"""

import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


def send_booking_notifications(booking):
    """
    Sends email notifications upon successful creation of a BookingRequest:
        1. Studio Notification Email: Sent to configured studio email (STUDIO_NOTIFICATION_EMAIL).
        2. Client Acknowledgement Email: Sent to client email acknowledging submission.

    Failure Safety:
        All email attempts are wrapped in try/except blocks. If an email fails (e.g. network/SMTP outage),
        the error is logged, and execution continues cleanly so database persistence is NEVER broken.

    Args:
        booking (BookingRequest): Saved booking model instance.
    """
    studio_email = getattr(settings, 'STUDIO_NOTIFICATION_EMAIL', 'info@studio101.co.za')
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@studio101.co.za')

    # 1. Studio Notification Email
    try:
        service_name = booking.service_requested.title if booking.service_requested else 'General Studio Hire'
        studio_name = booking.studio_space.name if booking.studio_space else 'N/A'
        
        subject_studio = f"[STUDIO101] New Booking Request #{booking.id} - {booking.full_name}"
        message_studio = (
            f"New booking inquiry received for STUDIO101:\n\n"
            f"Booking ID: #{booking.id}\n"
            f"Client Name: {booking.full_name}\n"
            f"Email: {booking.email}\n"
            f"Phone: {booking.phone}\n"
            f"Company/Brand: {booking.company_or_project or 'N/A'}\n"
            f"Requested Service: {service_name}\n"
            f"Studio Space: {studio_name}\n"
            f"Preferred Date: {booking.preferred_date or 'Not specified'}\n"
            f"Estimated Budget: {booking.estimated_budget or 'Not specified'}\n"
            f"Status: {booking.get_status_display()}\n\n"
            f"Project Concept & Details:\n{booking.project_details}\n"
        )

        send_mail(
            subject=subject_studio,
            message=message_studio,
            from_email=from_email,
            recipient_list=[studio_email],
            fail_silently=False,
        )
    except Exception as exc:
        logger.error(f"Failed to send studio notification email for Booking #{booking.id}: {exc}")

    # 2. Client Acknowledgement Email
    try:
        subject_client = f"Booking Request Acknowledgement #{booking.id} - STUDIO101"
        message_client = (
            f"Hello {booking.full_name},\n\n"
            f"Thank you for reaching out to STUDIO101.\n\n"
            f"We have received your booking request for '{booking.service_requested.title if booking.service_requested else 'Studio Hire'}' "
            f"and our production team is currently reviewing your project specifications.\n\n"
            f"PLEASE NOTE: This email is an official acknowledgement of your request submission, "
            f"not a final booking confirmation. A studio representative will contact you directly to confirm schedule and details.\n\n"
            f"Best regards,\n"
            f"STUDIO101 Production Team\n"
            f"info@studio101.co.za\n"
        )

        send_mail(
            subject=subject_client,
            message=message_client,
            from_email=from_email,
            recipient_list=[booking.email],
            fail_silently=False,
        )
    except Exception as exc:
        logger.error(f"Failed to send client acknowledgement email for Booking #{booking.id}: {exc}")
