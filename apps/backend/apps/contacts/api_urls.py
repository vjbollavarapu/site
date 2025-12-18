from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactSubmissionViewSet, submit_contact_form

router = DefaultRouter()
router.register(r'contacts', ContactSubmissionViewSet, basename='contactsubmission')

urlpatterns = [
    path('contacts/submit/', submit_contact_form, name='contact-submit'),
    path('', include(router.urls)),
]

