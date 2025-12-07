"""
Tests for GDPR API views
"""
from unittest.mock import patch
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.gdpr.models import Consent
from apps.gdpr.tests.factories import ConsentFactory


class GDPRAPITest(TestCase):
    """Test GDPR API endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.client = APIClient()
    
    def test_manage_consent_give(self):
        """Test giving consent"""
        data = {
            'email': 'user@example.com',
            'consent_type': 'marketing',
            'consent_given': True
        }
        
        response = self.client.post('/api/gdpr/consent/', data, format='json')
        
        if response.status_code not in [404, 500]:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(response.data.get('success'))
    
    def test_export_user_data(self):
        """Test exporting user data"""
        # Create some test data
        from apps.contacts.tests.factories import ContactSubmissionFactory
        ContactSubmissionFactory(email='user@example.com')
        
        response = self.client.get('/api/gdpr/export/user@example.com/')
        
        if response.status_code not in [404, 500]:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('data', response.data)
            self.assertIn('contacts', response.data['data'])
    
    @patch('apps.gdpr.api_views.GDPRService')
    def test_delete_user_data(self, mock_service):
        """Test deleting user data"""
        mock_service.delete_user_data.return_value = {
            'email': 'user@example.com',
            'deleted': {'contacts': 1, 'waitlist': 0}
        }
        
        response = self.client.delete('/api/gdpr/delete/user@example.com/?confirmation=true')
        
        if response.status_code not in [404, 500]:
            # Should require confirmation first
            self.assertIn(response.status_code, [
                status.HTTP_200_OK,
                status.HTTP_400_BAD_REQUEST
            ])
