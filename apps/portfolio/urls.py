from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.portfolio_list_view, name='list'),
    path('<slug:slug>/', views.project_detail_view, name='detail'),
]
