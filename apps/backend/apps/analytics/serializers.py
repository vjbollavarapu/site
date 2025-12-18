from rest_framework import serializers
from .models import PageView, Event, Conversion


class PageViewSerializer(serializers.ModelSerializer):
    """Serializer for tracking page views"""
    
    class Meta:
        model = PageView
        fields = ['page_url', 'page_title', 'referrer_url', 'session_id', 'duration']
        extra_kwargs = {
            'page_title': {'required': False, 'allow_blank': True},
            'referrer_url': {'required': False, 'allow_blank': True},
            'session_id': {'required': False, 'allow_blank': True},
            'duration': {'required': False},
        }


class EventSerializer(serializers.ModelSerializer):
    """Serializer for tracking events"""
    
    class Meta:
        model = Event
        fields = ['event_name', 'event_category', 'event_value', 'event_properties', 'session_id', 'page_url', 'user_identifier']
        extra_kwargs = {
            'event_category': {'required': False, 'default': 'other'},
            'event_value': {'required': False},
            'event_properties': {'required': False, 'default': dict},
            'session_id': {'required': False, 'allow_blank': True},
            'page_url': {'required': False, 'allow_blank': True},
            'user_identifier': {'required': False, 'allow_blank': True},
        }


class PageViewListSerializer(serializers.ModelSerializer):
    """Serializer for listing page views (admin)"""
    
    class Meta:
        model = PageView
        fields = [
            'id', 'session_id', 'page_url', 'page_title', 'referrer_url',
            'device_type', 'browser', 'operating_system', 'country', 'city',
            'timestamp', 'duration', 'is_exit_page'
        ]


class EventListSerializer(serializers.ModelSerializer):
    """Serializer for listing events (admin)"""
    
    class Meta:
        model = Event
        fields = [
            'id', 'event_name', 'event_category', 'event_value',
            'event_properties', 'session_id', 'page_url', 'user_identifier',
            'timestamp'
        ]


class ConversionListSerializer(serializers.ModelSerializer):
    """Serializer for listing conversions (admin)"""
    related_object_str = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversion
        fields = [
            'id', 'conversion_type', 'value', 'related_object_str',
            'attribution_data', 'campaign_info', 'timestamp'
        ]
    
    def get_related_object_str(self, obj):
        """Get string representation of related object"""
        related = obj.related_object
        if related:
            return str(related)
        return None

