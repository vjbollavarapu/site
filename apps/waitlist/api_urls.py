from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    WaitlistEntryViewSet,
    join_waitlist,
    verify_waitlist_email,
    check_waitlist_status
)

router = DefaultRouter()
router.register(r'entries', WaitlistEntryViewSet, basename='waitlistentry')

urlpatterns = [
    # Public endpoints
    path('waitlist/join/', join_waitlist, name='waitlist-join'),
    path('waitlist/verify/', verify_waitlist_email, name='waitlist-verify'),
    path('waitlist/status/<str:email>/', check_waitlist_status, name='waitlist-status'),
    
    # Admin endpoints (via router) - will be at /api/waitlist/entries/
    path('waitlist/', include(router.urls)),
]

