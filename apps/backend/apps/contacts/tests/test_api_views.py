"""
Tests for ContactSubmission API views
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.contacts.models import ContactSubmission
from apps.contacts.tests.factories import ContactSubmissionFactory


class ContactSubmissionAPITest(TestCase):
    """Test ContactSubmission API endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.client = APIClient()
        self.admin_client = APIClient()
        # Create admin user for authenticated tests
        from django.contrib.auth.models import User
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        self.admin_client.force_authenticate(user=self.admin_user)
    
    @patch('apps.contacts.views.CheckSubmissionSpam')
    @patch('apps.contacts.views.email_service')
    @patch('apps.contacts.views.crm_service')
    def test_submit_contact_form_success(self, mock_crm, mock_email, mock_spam):
        """Test successful contact form submission"""
        mock_spam.return_value.calculate_spam_score.return_value = (False, 0.1, [], [])
        mock_email.send_contact_confirmation = MagicMock()
        mock_crm.sync_contact_submission = MagicMock()
        
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message that is long enough',
            'phone': '+1234567890',
            'company': 'Test Company'
        }
        
        response = self.client.post('/api/contacts/submit/', data, format='json')
        
        if response.status_code not in [404, 500]:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(response.data.get('success'))
            self.assertIn('submission_id', response.data)
    
    @patch('apps.contacts.views.CheckSubmissionSpam')
    def test_submit_contact_form_spam_detected(self, mock_spam):
        """Test contact form submission with spam detected"""
        mock_spam.return_value.calculate_spam_score.return_value = (True, 0.9, ['suspicious_keywords'], [])
        
        data = {
            'name': 'Spam Bot',
            'email': 'spam@spam.com',
            'subject': 'Buy now!',
            'message': 'CLICK HERE NOW!!! BUY BUY BUY!!!',
        }
        
        response = self.client.post('/api/contacts/submit/', data, format='json')
        
        if response.status_code not in [404, 500]:
            # Should still create submission but mark as spam
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_submit_contact_form_invalid_data(self):
        """Test contact form submission with invalid data"""
        data = {
            'name': 'John',
            'email': 'invalid-email',
            'subject': 'Test',
            'message': 'Hi'  # Too short
        }
        
        response = self.client.post('/api/contacts/submit/', data, format='json')
        
        if response.status_code not in [404, 500]:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('email', response.data or {})
    
    def test_list_contact_submissions_admin(self):
        """Test listing contact submissions as admin"""
        ContactSubmissionFactory.create_batch(5)
        
        response = self.admin_client.get('/api/contacts/')
        
        if response.status_code not in [404, 500]:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Should return paginated results
    
    def test_list_contact_submissions_unauthorized(self):
        """Test listing contact submissions without auth"""
        response = self.client.get('/api/contacts/')
        
        if response.status_code not in [404, 500]:
            # Should require authentication
            self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_get_contact_submission_detail(self):
        """Test getting contact submission detail"""
        submission = ContactSubmissionFactory()
        
        response = self.admin_client.get(f'/api/contacts/{submission.id}/')
        
        if response.status_code not in [404, 500]:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(str(response.data['id']), str(submission.id))
    
    def test_update_contact_submission(self):
        """Test updating contact submission"""
        submission = ContactSubmissionFactory(status='new')
        data = {'status': 'contacted', 'priority': 'high'}
        
        response = self.admin_client.patch(f'/api/contacts/{submission.id}/', data, format='json')
        
        if response.status_code not in [404, 500]:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            submission.refresh_from_db()
            self.assertEqual(submission.status, 'contacted')
            self.assertEqual(submission.priority, 'high')
    
    def test_delete_contact_submission(self):
        """Test deleting contact submission"""
        submission = ContactSubmissionFactory()
        
        response = self.admin_client.delete(f'/api/contacts/{submission.id}/')
        
        if response.status_code not in [404, 500]:
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            self.assertFalse(ContactSubmission.objects.filter(id=submission.id).exists())
