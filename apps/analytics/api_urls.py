from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    PageViewViewSet,
    EventViewSet,
    ConversionViewSet,
    track_pageview,
    track_event,
    analytics_dashboard
)

router = DefaultRouter()
router.register(r'analytics/pageviews', PageViewViewSet, basename='pageview')
router.register(r'analytics/events', EventViewSet, basename='event')
router.register(r'analytics/conversions', ConversionViewSet, basename='conversion')

urlpatterns = [
    # Public tracking endpoints
    path('analytics/pageview/', track_pageview, name='analytics-pageview'),
    path('analytics/event/', track_event, name='analytics-event'),
    
    # Admin dashboard
    path('analytics/dashboard/', analytics_dashboard, name='analytics-dashboard'),
    
    # Admin endpoints (via router)
    path('', include(router.urls)),
]

