"""
GDPR serializers
"""
from rest_framework import serializers
from .models import Consent, PrivacyPolicy, DataRetentionPolicy, DataDeletionAudit


class ConsentSerializer(serializers.ModelSerializer):
    """Serializer for consent records"""
    
    class Meta:
        model = Consent
        fields = [
            'id', 'email', 'consent_type', 'consent_given',
            'consent_timestamp', 'consent_text', 'withdrawal_timestamp',
            'withdrawal_reason', 'privacy_policy', 'source', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ConsentCreateSerializer(serializers.Serializer):
    """Serializer for creating consent"""
    email = serializers.EmailField(required=True)
    consent_type = serializers.ChoiceField(choices=Consent.CONSENT_TYPE_CHOICES, required=True)
    consent_given = serializers.BooleanField(required=True)
    consent_text = serializers.CharField(required=False, allow_blank=True)
    privacy_policy_version = serializers.CharField(required=False, allow_blank=True)
    source = serializers.CharField(required=False, allow_blank=True)


class PrivacyPolicySerializer(serializers.ModelSerializer):
    """Serializer for privacy policy"""
    
    class Meta:
        model = PrivacyPolicy
        fields = [
            'id', 'version', 'title', 'content', 'is_active',
            'effective_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DataExportSerializer(serializers.Serializer):
    """Serializer for data export request"""
    email = serializers.EmailField(required=True)


class DataDeletionSerializer(serializers.Serializer):
    """Serializer for data deletion request"""
    email = serializers.EmailField(required=True)
    anonymize = serializers.BooleanField(default=False)
    confirmation = serializers.BooleanField(required=True, help_text="Must be True to confirm deletion")
    confirmation_token = serializers.CharField(required=False, allow_blank=True)


class DataRetentionPolicySerializer(serializers.ModelSerializer):
    """Serializer for data retention policy"""
    
    class Meta:
        model = DataRetentionPolicy
        fields = [
            'id', 'data_type', 'retention_days', 'auto_delete',
            'anonymize_instead', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

