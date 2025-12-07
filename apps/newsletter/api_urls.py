from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    NewsletterSubscriptionViewSet,
    subscribe_newsletter,
    verify_newsletter_subscription,
    unsubscribe_newsletter
)

router = DefaultRouter()
router.register(r'newsletter/subscribers', NewsletterSubscriptionViewSet, basename='newslettersubscription')

urlpatterns = [
    # Public endpoints
    path('newsletter/subscribe/', subscribe_newsletter, name='newsletter-subscribe'),
    path('newsletter/verify/', verify_newsletter_subscription, name='newsletter-verify'),
    path('newsletter/unsubscribe/', unsubscribe_newsletter, name='newsletter-unsubscribe'),
    
    # Admin endpoints (via router)
    path('', include(router.urls)),
]

