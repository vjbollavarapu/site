"""
Webhook API URLs
"""
from django.urls import path
from .api_views import test_webhook, verify_webhook_signature

urlpatterns = [
    path('webhooks/test/', test_webhook, name='webhook-test'),
    path('webhooks/verify/', verify_webhook_signature, name='webhook-verify'),
]

