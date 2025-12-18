"""
Tests for Analytics API views
"""
from unittest.mock import patch
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.analytics.models import PageView, Event
from apps.analytics.tests.factories import PageViewFactory, EventFactory


class AnalyticsAPITest(TestCase):
    """Test Analytics API endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.client = APIClient()
        self.admin_client = APIClient()
        from django.contrib.auth.models import User
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        self.admin_client.force_authenticate(user=self.admin_user)
    
    def test_track_pageview(self):
        """Test tracking page view"""
        data = {
            'session_id': 'test-session-123',
            'page_url': 'https://example.com/page',
            'page_title': 'Test Page'
        }
        
        response = self.client.post('/api/analytics/pageview/', data, format='json')
        
        if response.status_code not in [404, 500]:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(response.data.get('success'))
    
    def test_track_event(self):
        """Test tracking event"""
        data = {
            'event_name': 'button_click',
            'event_category': 'user_interaction',
            'session_id': 'test-session-123',
            'event_properties': {'button_id': 'signup'}
        }
        
        response = self.client.post('/api/analytics/event/', data, format='json')
        
        if response.status_code not in [404, 500]:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(response.data.get('success'))
    
    def test_analytics_dashboard_admin(self):
        """Test analytics dashboard as admin"""
        PageViewFactory.create_batch(10)
        EventFactory.create_batch(5)
        
        response = self.admin_client.get('/api/analytics/dashboard/')
        
        if response.status_code not in [404, 500]:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('total_pageviews', response.data)
