"""
URL routing patterns for the Live Streaming app.
"""

from django.urls import path
from . import views

app_name = 'streams'

urlpatterns = [
    path('', views.stream_list_view, name='list'),
    path('<slug:slug>/', views.stream_detail_view, name='detail'),
]
