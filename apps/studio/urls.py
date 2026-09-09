from django.urls import path
from . import views

app_name = 'studio'

urlpatterns = [
    path('', views.studio_overview_view, name='overview'),
]
