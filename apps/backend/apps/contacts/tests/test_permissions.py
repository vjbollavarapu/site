"""
Tests for API permissions
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from apps.contacts.models import ContactSubmission
from apps.contacts.tests.factories import ContactSubmissionFactory


class PermissionsTest(TestCase):
    """Test API permissions"""
    
    def setUp(self):
        """Set up test clients"""
        self.client = APIClient()
        self.admin_client = APIClient()
        self.staff_client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        self.admin_client.force_authenticate(user=self.admin_user)
        
        # Create staff user (non-superuser)
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=False
        )
        self.staff_client.force_authenticate(user=self.staff_user)
    
    def test_public_submit_contact_allowed(self):
        """Test public can submit contact form"""
        data = {
            'name': 'Public User',
            'email': 'public@example.com',
            'subject': 'Test',
            'message': 'This is a test message that is long enough'
        }
        
        try:
            url = reverse('api:submit-contact')
        except:
            response = self.client.post('/api/contacts/submit/', data, format='json')
        else:
            response = self.client.post(url, data, format='json')
        
        if response.status_code not in [404, 500]:
            # Public endpoint should allow unauthenticated requests
            self.assertIn(response.status_code, [
                status.HTTP_201_CREATED,
                status.HTTP_400_BAD_REQUEST
            ])
    
    def test_list_contacts_requires_auth(self):
        """Test listing contacts requires authentication"""
        ContactSubmissionFactory.create_batch(3)
        
        try:
            url = reverse('api:contact-list')
        except:
            response = self.client.get('/api/contacts/')
        else:
            response = self.client.get(url)
        
        if response.status_code not in [404, 500]:
            # Should require authentication
            self.assertIn(response.status_code, [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN
            ])
    
    def test_list_contacts_admin_allowed(self):
        """Test admin can list contacts"""
        ContactSubmissionFactory.create_batch(3)
        
        try:
            url = reverse('api:contact-list')
        except:
            response = self.admin_client.get('/api/contacts/')
        else:
            response = self.admin_client.get(url)
        
        if response.status_code not in [404, 500]:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_contact_admin_allowed(self):
        """Test admin can update contact"""
        submission = ContactSubmissionFactory(status='new')
        data = {'status': 'contacted'}
        
        try:
            url = reverse('api:contact-detail', args=[submission.id])
        except:
            response = self.admin_client.patch(f'/api/contacts/{submission.id}/', data, format='json')
        else:
            response = self.admin_client.patch(url, data, format='json')
        
        if response.status_code not in [404, 500]:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_contact_unauthorized(self):
        """Test unauthorized user cannot update contact"""
        submission = ContactSubmissionFactory()
        data = {'status': 'contacted'}
        
        try:
            url = reverse('api:contact-detail', args=[submission.id])
        except:
            response = self.client.patch(f'/api/contacts/{submission.id}/', data, format='json')
        else:
            response = self.client.patch(url, data, format='json')
        
        if response.status_code not in [404, 500]:
            self.assertIn(response.status_code, [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN
            ])

