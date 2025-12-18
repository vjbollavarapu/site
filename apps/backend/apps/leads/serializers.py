from rest_framework import serializers
from .models import Lead
from django.contrib.auth.models import User
from apps.analytics.models import Event, Conversion


class LeadCaptureSerializer(serializers.ModelSerializer):
    """Serializer for public lead capture"""
    
    class Meta:
        model = Lead
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'company',
            'lead_source', 'industry', 'job_title', 'company_size', 'ab_test_name'
        ]
        extra_kwargs = {
            'phone': {'required': False, 'allow_blank': True},
            'company': {'required': False, 'allow_blank': True},
            'industry': {'required': False, 'allow_blank': True},
            'job_title': {'required': False, 'allow_blank': True},
            'company_size': {'required': False, 'allow_blank': True},
            'lead_source': {'required': False, 'default': 'website'},
        }
    
    def validate_email(self, value):
        """Validate email format"""
        if not value or '@' not in value:
            raise serializers.ValidationError("Invalid email format.")
        return value.lower().strip()


class LeadTrackEventSerializer(serializers.Serializer):
    """Serializer for tracking lead engagement events"""
    event_name = serializers.CharField(required=True, max_length=200)
    event_properties = serializers.JSONField(required=False, default=dict)
    page_url = serializers.URLField(required=False, allow_blank=True)
    session_id = serializers.CharField(required=False, allow_blank=True)


class LeadSerializer(serializers.ModelSerializer):
    """Serializer for admin lead management"""
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)
    assigned_to_full_name = serializers.SerializerMethodField()
    engagement_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Lead
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 'company',
            'lead_source', 'lead_score', 'industry', 'job_title', 'company_size',
            'status', 'lifecycle_stage', 'assigned_to', 'assigned_to_username',
            'assigned_to_full_name', 'custom_data', 'engagement_count',
            'created_at', 'updated_at', 'last_contacted_at', 'converted_at'
        ]
        read_only_fields = [
            'id', 'lead_score', 'created_at', 'updated_at',
            'last_contacted_at', 'converted_at'
        ]
    
    def get_assigned_to_full_name(self, obj):
        """Get full name of assigned user"""
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.username
        return None
    
    def get_engagement_count(self, obj):
        """Get count of engagement events for this lead"""
        return Event.objects.filter(
            user_identifier=obj.email
        ).count()


class LeadUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating lead (admin only)"""
    
    class Meta:
        model = Lead
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'company',
            'lead_source', 'industry', 'job_title', 'company_size',
            'status', 'lifecycle_stage', 'assigned_to'
        ]


class LeadDetailSerializer(LeadSerializer):
    """Extended serializer with engagement history"""
    engagement_events = serializers.SerializerMethodField()
    conversions = serializers.SerializerMethodField()
    
    class Meta(LeadSerializer.Meta):
        fields = LeadSerializer.Meta.fields + ['engagement_events', 'conversions']
    
    def get_engagement_events(self, obj):
        """Get recent engagement events"""
        events = Event.objects.filter(
            user_identifier=obj.email
        ).order_by('-timestamp')[:20]
        
        return [{
            'event_name': e.event_name,
            'event_category': e.event_category,
            'page_url': e.page_url,
            'timestamp': e.timestamp,
            'event_properties': e.event_properties
        } for e in events]
    
    def get_conversions(self, obj):
        """Get conversions for this lead"""
        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(Lead)
        conversions = Conversion.objects.filter(
            content_type=ct,
            object_id=obj.id
        ).order_by('-timestamp')
        
        return [{
            'conversion_type': c.conversion_type,
            'value': str(c.value) if c.value else None,
            'timestamp': c.timestamp,
            'campaign_info': c.campaign_info
        } for c in conversions]

