"""
Tests for Analytics models
"""
from django.test import TestCase
from apps.analytics.models import PageView, Event, Conversion
from apps.analytics.tests.factories import PageViewFactory, EventFactory, ConversionFactory


class PageViewModelTest(TestCase):
    """Test PageView model"""
    
    def test_create_page_view(self):
        """Test creating a page view"""
        pageview = PageViewFactory()
        self.assertIsNotNone(pageview.id)
        self.assertIsNotNone(pageview.session_id)
    
    def test_hash_ip_address(self):
        """Test IP address hashing"""
        hashed = PageView.hash_ip_address('192.168.1.1')
        self.assertIsNotNone(hashed)
        self.assertEqual(len(hashed), 64)  # SHA256 hex length
    
    def test_hash_ip_address_none(self):
        """Test IP address hashing with None"""
        hashed = PageView.hash_ip_address(None)
        self.assertIsNone(hashed)


class EventModelTest(TestCase):
    """Test Event model"""
    
    def test_create_event(self):
        """Test creating an event"""
        event = EventFactory()
        self.assertIsNotNone(event.id)
        self.assertIsNotNone(event.event_name)
    
    def test_event_properties_json(self):
        """Test event properties as JSON"""
        event = EventFactory(event_properties={'key': 'value'})
        self.assertEqual(event.event_properties['key'], 'value')


class ConversionModelTest(TestCase):
    """Test Conversion model"""
    
    def test_create_conversion(self):
        """Test creating a conversion"""
        conversion = ConversionFactory()
        self.assertIsNotNone(conversion.id)
        self.assertIsNotNone(conversion.conversion_type)
    
    def test_conversion_with_related_object(self):
        """Test conversion with related object"""
        from apps.contacts.models import ContactSubmission
        from apps.contacts.tests.factories import ContactSubmissionFactory
        from django.contrib.contenttypes.models import ContentType
        
        contact = ContactSubmissionFactory()
        content_type = ContentType.objects.get_for_model(ContactSubmission)
        
        conversion = ConversionFactory(
            content_type=content_type,
            object_id=contact.id
        )
        
        self.assertEqual(conversion.related_object, contact)

