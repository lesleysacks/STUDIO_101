"""
Tests for Bookings application models, forms, email notification pipeline, and view handlers.
"""

from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from .models import BookingRequest
from .forms import BookingRequestForm


class BookingNotificationAndModelTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.valid_post_data = {
            'full_name': "Alex Taylor",
            'email': "alex@example.com",
            'phone': "+27 82 000 1111",
            'project_details': "Music video shoot concept."
        }

    def test_1_valid_booking_creates_database_record(self):
        """Test 1: Valid booking submission creates a database record."""
        response = self.client.post(reverse('bookings:request'), self.valid_post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(BookingRequest.objects.filter(full_name="Alex Taylor").exists())
        booking = BookingRequest.objects.get(full_name="Alex Taylor")
        self.assertEqual(booking.status, 'new')

    def test_2_studio_notification_email_generated(self):
        """Test 2: Studio notification email is generated upon valid booking."""
        self.client.post(reverse('bookings:request'), self.valid_post_data)
        self.assertGreaterEqual(len(mail.outbox), 1)
        studio_email = mail.outbox[0]
        self.assertIn("New Booking Request", studio_email.subject)
        self.assertIn("Alex Taylor", studio_email.body)

    def test_3_client_acknowledgement_email_generated(self):
        """Test 3: Client acknowledgement email is generated upon valid booking."""
        self.client.post(reverse('bookings:request'), self.valid_post_data)
        self.assertEqual(len(mail.outbox), 2)
        client_email = mail.outbox[1]
        self.assertIn("Booking Request Acknowledgement", client_email.subject)
        self.assertIn("alex@example.com", client_email.to)

    @patch('apps.bookings.utils.send_mail')
    def test_4_email_failure_does_not_prevent_booking_save(self, mock_send_mail):
        """Test 4: Email failure does not prevent the booking from being saved in database."""
        mock_send_mail.side_effect = Exception("SMTP Server Unreachable")
        response = self.client.post(reverse('bookings:request'), self.valid_post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(BookingRequest.objects.filter(full_name="Alex Taylor").exists())

    def test_5_invalid_booking_does_not_trigger_notification(self):
        """Test 5: Invalid booking form submission does not trigger notifications."""
        invalid_data = {
            'full_name': "",
            'email': "not-an-email",
            'phone': "",
            'project_details': ""
        }
        response = self.client.post(reverse('bookings:request'), invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertFalse(BookingRequest.objects.filter(email="not-an-email").exists())
