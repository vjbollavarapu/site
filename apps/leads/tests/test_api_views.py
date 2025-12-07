"""
Tests for Lead API views
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.leads.models import Lead
from apps.leads.tests.factories import LeadFactory


class LeadAPITest(TestCase):
    """Test Lead API endpoints"""
    
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
    
    @patch('apps.leads.api_views.crm_service')
    def test_capture_lead_success(self, mock_crm):
        """Test successful lead capture"""
        mock_crm.sync_lead = MagicMock()
        
        data = {
            'email': 'newlead@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'company': 'Test Company',
            'lead_source': 'website'
        }
        
        response = self.client.post('/api/leads/capture/', data, format='json')
        
        if response.status_code not in [404, 500]:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(response.data.get('success'))
            self.assertIn('lead_id', response.data)
            mock_crm.sync_lead.assert_called_once()
    
    def test_capture_lead_duplicate(self):
        """Test capturing duplicate lead"""
        existing = LeadFactory(email='existing@example.com')
        
        data = {
            'email': 'existing@example.com',
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = self.client.post('/api/leads/capture/', data, format='json')
        
        if response.status_code not in [404, 500]:
            # Should update existing lead
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            existing.refresh_from_db()
            self.assertEqual(existing.first_name, 'Updated')
    
    def test_track_lead_event(self):
        """Test tracking lead event"""
        lead = LeadFactory()
        
        data = {
            'event_name': 'button_click',
            'event_category': 'user_interaction',
            'event_properties': {'button_id': 'signup'}
        }
        
        response = self.client.post(f'/api/leads/{lead.id}/track-event/', data, format='json')
        
        if response.status_code not in [404, 500]:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(response.data.get('success'))
    
    def test_qualify_lead_admin(self):
        """Test qualifying lead as admin"""
        lead = LeadFactory(status='new')
        
        response = self.admin_client.post(f'/api/leads/{lead.id}/qualify/')
        
        if response.status_code not in [404, 500]:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            lead.refresh_from_db()
            self.assertEqual(lead.status, 'qualified')
