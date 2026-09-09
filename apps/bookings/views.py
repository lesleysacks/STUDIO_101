from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import BookingRequestForm

def booking_view(request):
    if request.method == 'POST':
        form = BookingRequestForm(request.POST)
        if form.is_valid():
            booking = form.save()
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
