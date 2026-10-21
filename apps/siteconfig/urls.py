from django.urls import path

from . import views

app_name = "siteconfig"

urlpatterns = [
    path("site-config/diagnostics/", views.diagnostics_view, name="diagnostics"),
]
