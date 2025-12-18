"""
GDPR API URLs
"""
from django.urls import path
from .api_views import (
    manage_consent,
    export_user_data,
    access_user_data,
    delete_user_data,
    list_consents,
    manage_privacy_policy,
    manage_retention_policies,
    apply_retention_policies,
)

urlpatterns = [
    # Public GDPR endpoints
    path('gdpr/consent/', manage_consent, name='gdpr-consent'),
    path('gdpr/export/<str:email>/', export_user_data, name='gdpr-export'),
    path('gdpr/access/<str:email>/', access_user_data, name='gdpr-access'),
    path('gdpr/delete/<str:email>/', delete_user_data, name='gdpr-delete'),
    
    # Admin endpoints
    path('gdpr/admin/consents/', list_consents, name='gdpr-admin-consents'),
    path('gdpr/admin/privacy-policy/', manage_privacy_policy, name='gdpr-admin-privacy-policy'),
    path('gdpr/admin/retention-policies/', manage_retention_policies, name='gdpr-admin-retention-policies'),
    path('gdpr/admin/apply-retention/', apply_retention_policies, name='gdpr-admin-apply-retention'),
]

