"""
A/B Testing API URLs
"""
from django.urls import path
from .api_views import get_variant, get_test_results

urlpatterns = [
    path('ab-testing/variant/<str:test_name>/', get_variant, name='ab-test-variant'),
    path('ab-testing/results/<str:test_name>/', get_test_results, name='ab-test-results'),
]

