"""
Views for handling service package listings and individual service detail views.
"""

from django.shortcuts import render, get_object_or_404
from .models import Service, ServiceCategory


def service_list_view(request):
    """
    Renders the main services directory page listing all active service packages.
    """
    services = Service.objects.all().order_by('order')
    categories = ServiceCategory.objects.all()
    return render(request, 'pages/services_list.html', {
        'services': services,
        'categories': categories,
    })


def service_detail_view(request, slug):
    """
    Renders detailed specifications and features for a single target service package.

    Args:
        slug (str): Unique URL identifier for the target service.
    """
    service = get_object_or_404(Service, slug=slug)
    features = service.features.all().order_by('order')
    return render(request, 'pages/service_detail.html', {
        'service': service,
        'features': features,
    })
