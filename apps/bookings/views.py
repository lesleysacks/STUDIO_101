"""
Views for handling client session reservation requests and submission processing.
"""

from django.shortcuts import render
from django.http import JsonResponse
from .forms import BookingRequestForm
from .utils import send_booking_notifications


def booking_view(request):
    """
    Renders and processes the studio reservation form.

    POST Handling:
        1. Validates form data against BookingRequestForm rules.
        2. Saves BookingRequest record to PostgreSQL/SQLite database.
        3. Triggers asynchronous/safe email notifications to studio team and client.
        4. Returns JSON response for AJAX calls or renders success state template for standard POST.
    """
    if request.method == 'POST':
        form = BookingRequestForm(request.POST)
        if form.is_valid():
            booking = form.save()
            
            # Send Studio alert & Client acknowledgement emails
            send_booking_notifications(booking)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': f'Thank you {booking.full_name}, your booking request #{booking.id} has been submitted!',
                    'booking_id': booking.id
                })
            return render(request, 'pages/book.html', {
                'form': BookingRequestForm(),
                'success_message': f'Thank you {booking.full_name}, your booking request #{booking.id} has been received.'
            })
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    else:
        form = BookingRequestForm()

    return render(request, 'pages/book.html', {'form': form})
