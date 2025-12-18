from rest_framework import serializers
from .models import ContactSubmission
from django.contrib.auth.models import User
from .security import sanitize_input, validate_honeypot


class ContactSubmissionCreateSerializer(serializers.ModelSerializer):
    """Serializer for public contact form submission"""
    website = serializers.CharField(required=False, allow_blank=True, write_only=True, help_text="Honeypot field - leave empty")
    recaptcha_token = serializers.CharField(required=False, allow_blank=True, write_only=True, help_text="reCAPTCHA v3 token")
    
    class Meta:
        model = ContactSubmission
        fields = ['name', 'email', 'phone', 'company', 'subject', 'message', 'source', 'custom_data', 'website', 'recaptcha_token', 'ab_test_name']
        extra_kwargs = {
            'phone': {'required': False, 'allow_blank': True},
            'company': {'required': False, 'allow_blank': True},
            'source': {'required': False, 'allow_blank': True},
            'custom_data': {'required': False},
        }
    
    def validate_email(self, value):
        """Validate email format"""
        if not value or '@' not in value:
            raise serializers.ValidationError("Invalid email format.")
        return value.lower().strip()
    
    def validate_website(self, value):
        """Validate honeypot field - should be empty"""
        if value and value.strip():
            raise serializers.ValidationError("Spam detected.")
        return value
    
    def validate_message(self, value):
        """Validate message length and sanitize"""
        if len(value) > 5000:
            raise serializers.ValidationError("Message cannot exceed 5000 characters.")
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters.")
        # Sanitize input
        return sanitize_input(value)
    
    def validate_name(self, value):
        """Validate name and sanitize"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters.")
        return sanitize_input(value.strip())
    
    def validate_subject(self, value):
        """Validate subject and sanitize"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Subject must be at least 3 characters.")
        return sanitize_input(value.strip())
    
    def validate_email(self, value):
        """Validate email and sanitize"""
        if not value or '@' not in value:
            raise serializers.ValidationError("Invalid email format.")
        return sanitize_input(value.lower().strip())


class ContactSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for admin contact submission management"""
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)
    assigned_to_full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ContactSubmission
        fields = [
            'id', 'name', 'email', 'phone', 'company', 'subject', 'message',
            'source', 'referrer', 'user_agent', 'ip_address',
            'status', 'priority', 'assigned_to', 'assigned_to_username', 'assigned_to_full_name',
            'custom_data', 'is_spam', 'spam_score',
            'consent_given', 'consent_timestamp',
            'created_at', 'updated_at', 'contacted_at', 'resolved_at'
        ]
        read_only_fields = [
            'id', 'referrer', 'user_agent', 'ip_address',
            'spam_score', 'consent_timestamp',
            'created_at', 'updated_at', 'contacted_at', 'resolved_at'
        ]
    
    def get_assigned_to_full_name(self, obj):
        """Get full name of assigned user"""
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.username
        return None


class ContactSubmissionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating contact submission (admin only)"""
    
    class Meta:
        model = ContactSubmission
        fields = ['status', 'priority', 'assigned_to', 'custom_data']
        extra_kwargs = {
            'custom_data': {'required': False},
        }
    
    def validate_status(self, value):
        """Validate status transitions"""
        if self.instance:
            # Allow any status transition for now
            # Can add business logic here if needed
            pass
        return value

