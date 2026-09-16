"""
Core application views for handling global site pages such as Home, About, FAQ, Contact, and Robots.txt.

Views:
    home_view: Compiles hero slides, live streams, featured services, portfolio showcase, and FAQs for homepage.
    about_view: Displays studio heritage, facilities overview, and brand philosophy.
    faq_view: Lists frequently asked questions grouped by categories.
    contact_view: Renders contact details and direct inquiry booking form.
    robots_txt_view: Renders dynamic robots.txt file with sitemap reference.
"""

from django.shortcuts import render
from django.http import HttpResponse
from .models import HeroSlide, FAQ
from apps.services.models import Service
from apps.portfolio.models import Project
from apps.studio.models import StudioSpace
from apps.bookings.forms import BookingRequestForm
from apps.streams.models import LiveStream


def home_view(request):
    """
    Renders the homepage assembling active hero slides, live streams, featured services,
    portfolio showreels, studio space highlights, FAQs, and reservation forms.

    Live Stream Resolution:
        1. Checks for currently active live broadcast (`is_live=True`, `is_active=True`).
        2. Falls back to nearest scheduled upcoming broadcast if no active stream is live.
    """
    hero_slides = HeroSlide.objects.filter(is_active=True).order_by('order')
    featured_services = Service.objects.filter(is_featured=True).order_by('order')[:3]
    featured_projects = Project.objects.filter(is_featured=True, is_published=True).order_by('order')[:6]
    studio_spaces = StudioSpace.objects.filter(is_available=True)
    faqs = FAQ.objects.filter(is_published=True).order_by('order')
    booking_form = BookingRequestForm()
    
    # Live stream active or upcoming query
    live_stream = LiveStream.objects.filter(is_active=True, is_live=True).first()
    if not live_stream:
        live_stream = LiveStream.objects.filter(is_active=True).order_by('-scheduled_at').first()

    context = {
        'hero_slides': hero_slides,
        'featured_services': featured_services,
        'featured_projects': featured_projects,
        'studio_spaces': studio_spaces,
        'faqs': faqs,
        'booking_form': booking_form,
        'live_stream': live_stream,
    }
    return render(request, 'pages/home.html', context)


def about_view(request):
    """
    Renders the About Studio 101 page highlighting company legacy and studio specs.
    """
    studio_spaces = StudioSpace.objects.filter(is_available=True)
    return render(request, 'pages/about.html', {'studio_spaces': studio_spaces})


def faq_view(request):
    """
    Renders the FAQ directory listing published questions and answers.
    """
    faqs = FAQ.objects.filter(is_published=True).order_by('order')
    return render(request, 'pages/faq.html', {'faqs': faqs})


def contact_view(request):
    """
    Renders the Contact & Location view with direct inquiry form.
    """
    booking_form = BookingRequestForm()
    return render(request, 'pages/contact.html', {'booking_form': booking_form})


def robots_txt_view(request):
    """
    Renders plain-text robots.txt file allowing public search engine indexation
    while disallowing access to administrative panels and pointing to sitemap.xml.
    """
    host = request.get_host()
    scheme = request.scheme
    content = (
        "User-agent: *\n"
        "Disallow: /admin/\n\n"
        f"Sitemap: {scheme}://{host}/sitemap.xml\n"
    )
    return HttpResponse(content, content_type="text/plain")
