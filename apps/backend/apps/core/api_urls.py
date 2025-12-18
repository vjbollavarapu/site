"""
URL configuration for core API endpoints
"""
from django.urls import path
from .api_views import dashboard_stats

urlpatterns = [
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),
]

