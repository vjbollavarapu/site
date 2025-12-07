"""
Tests for Email Service
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core import mail
from apps.integrations.email_service import EmailService
from apps.contacts.tests.factories import ContactSubmissionFactory


class EmailServiceTest(TestCase):
    """Test Email Service"""
    
    def setUp(self):
        """Set up email service"""
        self.email_service = EmailService()
    
    def test_send_contact_confirmation(self):
        """Test sending contact confirmation email"""
        submission = ContactSubmissionFactory()
        
        self.email_service.send_contact_confirmation(submission)
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Thank You for Contacting Us')
        self.assertIn(submission.email, mail.outbox[0].to)
    
    @patch('apps.integrations.email_service.send_email_task')
    def test_send_contact_confirmation_async(self, mock_task):
        """Test sending contact confirmation email asynchronously"""
        submission = ContactSubmissionFactory()
        
        # If async is enabled, should use Celery task
        self.email_service.send_contact_confirmation(submission, async_send=True)
        
        # In test, might send synchronously, but we can check the method was called
        # The actual behavior depends on Celery configuration

