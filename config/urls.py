"""
Main URL configuration for the STUDIO101 platform.
Includes domain application routers, admin panel, sitemap XML, and robots.txt.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from apps.core.sitemaps import StaticViewSitemap, ServiceSitemap, ProjectSitemap, StreamSitemap
from apps.core.views import robots_txt_view

sitemaps = {
    'static': StaticViewSitemap,
    'services': ServiceSitemap,
    'portfolio': ProjectSitemap,
    'streams': StreamSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('services/', include('apps.services.urls', namespace='services')),
    path('portfolio/', include('apps.portfolio.urls', namespace='portfolio')),
    path('studio/', include('apps.studio.urls', namespace='studio')),
    path('book/', include('apps.bookings.urls', namespace='bookings')),
    path('streams/', include('apps.streams.urls', namespace='streams')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt_view, name='robots_txt'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom Admin Headers
admin.site.site_header = "STUDIO101 Control Panel"
admin.site.site_title = "STUDIO101 Admin"
admin.site.index_title = "Content Management & Booking Triage"
