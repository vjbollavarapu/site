from rest_framework import serializers
from .models import NewsletterSubscription


class NewsletterSubscribeSerializer(serializers.ModelSerializer):
    """Serializer for public newsletter subscription"""
    interests = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        help_text="List of interest tags"
    )
    
    class Meta:
        model = NewsletterSubscription
        fields = ['email', 'name', 'interests', 'source', 'preference']
        extra_kwargs = {
            'name': {'required': False, 'allow_blank': True},
            'interests': {'required': False},
            'source': {'required': False, 'default': 'website'},
            'preference': {'required': False, 'default': 'weekly'},
        }
    
    def validate_email(self, value):
        """Validate email format"""
        if not value or '@' not in value:
            raise serializers.ValidationError("Invalid email format.")
        return value.lower().strip()
    
    def validate(self, data):
        """Check if already subscribed"""
        email = data.get('email', '').lower().strip()
        if email:
            existing = NewsletterSubscription.objects.filter(email=email).first()
            if existing:
                if existing.subscription_status == 'subscribed':
                    raise serializers.ValidationError({
                        'email': 'This email is already subscribed.'
                    })
                elif existing.subscription_status == 'unsubscribed':
                    # Allow resubscription
                    pass
        return data


class NewsletterVerifySerializer(serializers.Serializer):
    """Serializer for email verification"""
    token = serializers.CharField(required=True, max_length=100)
    
    def validate_token(self, value):
        """Validate verification token"""
        if not NewsletterSubscription.objects.filter(verification_token=value).exists():
            raise serializers.ValidationError("Invalid verification token.")
        return value


class NewsletterUnsubscribeSerializer(serializers.Serializer):
    """Serializer for unsubscribing"""
    email = serializers.EmailField(required=False, allow_blank=True)
    token = serializers.CharField(required=False, allow_blank=True, max_length=100)
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)
    
    def validate(self, data):
        """Ensure either email or token is provided"""
        email = data.get('email', '').strip()
        token = data.get('token', '').strip()
        
        if not email and not token:
            raise serializers.ValidationError(
                "Either email or token must be provided."
            )
        return data


class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for admin newsletter subscription management"""
    
    class Meta:
        model = NewsletterSubscription
        fields = [
            'id', 'email', 'name', 'subscription_status', 'source', 'preference',
            'interests', 'is_verified', 'verified_at', 'verification_token',
            'consent_given', 'consent_timestamp', 'consent_text',
            'unsubscribed_at', 'unsubscribe_reason', 'unsubscribe_token',
            'bounce_count', 'last_bounce_at', 'bounce_reason',
            'complaint_count', 'last_complaint_at',
            'ip_address', 'user_agent', 'referrer',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'verification_token', 'unsubscribe_token',
            'verified_at', 'unsubscribed_at', 'consent_timestamp',
            'last_bounce_at', 'last_complaint_at',
            'created_at', 'updated_at'
        ]

