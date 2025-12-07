from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import LeadViewSet, capture_lead, track_lead_event

router = DefaultRouter()
router.register(r'leads', LeadViewSet, basename='lead')

urlpatterns = [
    # Public endpoints
    path('leads/capture/', capture_lead, name='lead-capture'),
    path('leads/<uuid:pk>/track-event/', track_lead_event, name='lead-track-event'),
    
    # Admin endpoints (via router)
    path('', include(router.urls)),
]

