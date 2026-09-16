from django.test import TestCase
from django.core import mail
from apps.bookings.models import BookingRequest

class BookingNotificationTests(TestCase):
    def test_booking_creation_sends_emails(self):
        booking = BookingRequest.objects.create(
            client_name="Test Client",
            client_email="client@example.com",
            service="Photography",
            date="2026-09-20"
        )
        self.assertEqual(len(mail.outbox), 2)

    def test_studio_receives_email(self):
        booking = BookingRequest.objects.create(
            client_name="Studio Client",
            client_email="studio@example.com",
            service="Video",
            date="2026-09-21"
        )
        self.assertIn("New Booking Request", mail.outbox[0].subject)

    def test_client_receives_acknowledgement(self):
        booking = BookingRequest.objects.create(
            client_name="Client",
            client_email="client@example.com",
            service="Design",
            date="2026-09-22"
        )
        self.assertIn("Your booking request has been received", mail.outbox[1].subject)

    def test_email_failure_does_not_block(self):
        # Simulate failure by invalid email
        booking = BookingRequest.objects.create(
            client_name="Bad Client",
            client_email="invalid-email",
            service="Editing",
            date="2026-09-23"
        )
        self.assertTrue(BookingRequest.objects.filter(client_name="Bad Client").exists())

    def test_invalid_booking_rejected(self):
        with self.assertRaises(Exception):
            BookingRequest.objects.create(client_name="", client_email="bad@", service="", date="")
