from rest_framework import serializers
from .models import WaitlistEntry
from django.contrib.auth.models import User


class WaitlistJoinSerializer(serializers.ModelSerializer):
    """Serializer for public waitlist join"""
    
    class Meta:
        model = WaitlistEntry
        fields = ['email', 'name', 'company', 'role', 'company_size', 'industry', 'use_case', 'source', 'referral_code', 'ab_test_name']
        extra_kwargs = {
            'name': {'required': False, 'allow_blank': True},
            'company': {'required': False, 'allow_blank': True},
            'role': {'required': False, 'allow_blank': True},
            'company_size': {'required': False, 'allow_blank': True},
            'industry': {'required': False, 'allow_blank': True},
            'use_case': {'required': False, 'allow_blank': True},
            'source': {'required': False},
            'referral_code': {'required': False, 'allow_blank': True},
        }
    
    def validate_email(self, value):
        """Validate email format and uniqueness"""
        if not value or '@' not in value:
            raise serializers.ValidationError("Invalid email format.")
        email = value.lower().strip()
        
        # Check if email already exists
        if WaitlistEntry.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email is already on the waitlist.")
        
        return email


class WaitlistVerifySerializer(serializers.Serializer):
    """Serializer for email verification"""
    token = serializers.CharField(required=True, max_length=100)
    
    def validate_token(self, value):
        """Validate verification token"""
        if not WaitlistEntry.objects.filter(verification_token=value).exists():
            raise serializers.ValidationError("Invalid verification token.")
        return value


class WaitlistEntrySerializer(serializers.ModelSerializer):
    """Serializer for admin waitlist entry management"""
    invited_by_username = serializers.CharField(source='invited_by.username', read_only=True)
    invited_by_full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = WaitlistEntry
        fields = [
            'id', 'email', 'name', 'company', 'role', 'company_size', 'industry',
            'use_case', 'source', 'referral_code', 'priority_score', 'status',
            'invited_at', 'invited_by', 'invited_by_username', 'invited_by_full_name',
            'invite_code', 'expected_start_date', 'notes',
            'is_verified', 'verified_at', 'verification_token',
            'marketing_consent', 'consent_timestamp',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'priority_score', 'invited_at', 'invited_by',
            'invite_code', 'verification_token', 'verified_at',
            'consent_timestamp', 'created_at', 'updated_at'
        ]
    
    def get_invited_by_full_name(self, obj):
        """Get full name of user who sent invitation"""
        if obj.invited_by:
            return obj.invited_by.get_full_name() or obj.invited_by.username
        return None


class WaitlistEntryUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating waitlist entry (admin only)"""
    
    class Meta:
        model = WaitlistEntry
        fields = ['status', 'notes', 'expected_start_date']
        extra_kwargs = {
            'notes': {'required': False, 'allow_blank': True},
            'expected_start_date': {'required': False},
        }


class WaitlistStatusSerializer(serializers.Serializer):
    """Serializer for waitlist status check"""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Validate email format"""
        return value.lower().strip()

