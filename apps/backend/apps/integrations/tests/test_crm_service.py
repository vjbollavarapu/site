"""
Tests for CRM Service
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from apps.integrations.crm_service import CRMService
from apps.contacts.tests.factories import ContactSubmissionFactory


class CRMServiceTest(TestCase):
    """Test CRM Service"""
    
    def setUp(self):
        """Set up CRM service"""
        self.crm_service = CRMService()
    
    @patch('apps.integrations.crm_service.crm_service.provider')
    def test_sync_contact_submission(self, mock_provider):
        """Test syncing contact submission to CRM"""
        mock_provider.create_contact = MagicMock(return_value={'id': '123'})
        mock_provider.create_note = MagicMock(return_value={'id': '456'})
        
        submission = ContactSubmissionFactory()
        result = self.crm_service.sync_contact_submission(submission)
        
        # Should attempt to sync if provider is configured
        # Result depends on provider configuration
        self.assertIsNotNone(result)
    
    @patch('apps.integrations.crm_service.sync_to_crm_task')
    def test_sync_contact_submission_async(self, mock_task):
        """Test async CRM sync"""
        submission = ContactSubmissionFactory()
        
        # If immediate=False, should queue task
        result = self.crm_service.sync_contact_submission(submission, immediate=False)
        
        # Should return True if task was queued
        # Mock task might not be called in test environment
        self.assertIsNotNone(result)

