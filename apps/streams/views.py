"""
Views for handling live stream broadcast rendering and event listings.

Views:
    stream_list_view: Renders a list of all active and upcoming live stream broadcasts.
    stream_detail_view: Renders a dedicated page for a single live stream broadcast event.
"""

from django.shortcuts import render, get_object_or_404
from .models import LiveStream


def stream_list_view(request):
    """
    Queries all active live stream events and renders the stream directory template.

    Query Logic:
        Filter `is_active=True`, ordered with live broadcasts first (`-is_live`),
        followed by closest upcoming scheduled broadcasts.
    """
    streams = LiveStream.objects.filter(is_active=True)
    active_live = streams.filter(is_live=True).first()
    
    return render(request, 'pages/stream_list.html', {
        'streams': streams,
        'active_live': active_live,
    })


def stream_detail_view(request, slug):
    """
    Retrieves a single live stream broadcast by slug and renders its detail template.

    Args:
        slug (str): Unique URL identifier for the target broadcast event.
    """
    stream = get_object_or_404(LiveStream, slug=slug, is_active=True)
    return render(request, 'pages/stream_detail.html', {
        'stream': stream,
    })
