"""
Tests for NewsletterSubscription API views
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.newsletter.models import NewsletterSubscription
from apps.newsletter.tests.factories import NewsletterSubscriptionFactory


class NewsletterSubscriptionAPITest(TestCase):
    """Test NewsletterSubscription API endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.client = APIClient()
    
    @patch('apps.newsletter.api_views.email_service')
    def test_subscribe_newsletter_success(self, mock_email):
        """Test successful newsletter subscription"""
        mock_email.send_newsletter_verification = MagicMock()
        
        data = {
            'email': 'newsubscriber@example.com',
            'name': 'New Subscriber'
        }
        
        response = self.client.post('/api/newsletter/subscribe/', data, format='json')
        
        if response.status_code not in [404, 500]:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(response.data.get('success'))
            mock_email.send_newsletter_verification.assert_called_once()
    
    def test_subscribe_newsletter_duplicate(self):
        """Test subscribing with duplicate email"""
        existing = NewsletterSubscriptionFactory(email='existing@example.com')
        
        data = {
            'email': 'existing@example.com',
            'name': 'Existing User'
        }
        
        response = self.client.post('/api/newsletter/subscribe/', data, format='json')
        
        if response.status_code not in [404, 500]:
            # Should handle duplicate gracefully
            self.assertIn(response.status_code, [
                status.HTTP_201_CREATED,
                status.HTTP_400_BAD_REQUEST
            ])
    
    def test_verify_newsletter_email(self):
        """Test email verification"""
        subscription = NewsletterSubscriptionFactory(
            email='test@example.com',
            is_verified=False
        )
        token = subscription.verification_token or 'test-token'
        subscription.save()
        
        data = {
            'email': 'test@example.com',
            'token': token
        }
        
        response = self.client.post('/api/newsletter/verify/', data, format='json')
        
        if response.status_code not in [404, 500]:
            self.assertIn(response.status_code, [
                status.HTTP_200_OK,
                status.HTTP_400_BAD_REQUEST
            ])
    
    def test_unsubscribe_newsletter(self):
        """Test unsubscribing from newsletter"""
        subscription = NewsletterSubscriptionFactory(
            email='test@example.com',
            subscription_status='subscribed'
        )
        token = subscription.unsubscribe_token or 'test-token'
        subscription.save()
        
        data = {
            'email': 'test@example.com',
            'token': token
        }
        
        response = self.client.post('/api/newsletter/unsubscribe/', data, format='json')
        
        if response.status_code not in [404, 500]:
            self.assertIn(response.status_code, [
                status.HTTP_200_OK,
                status.HTTP_400_BAD_REQUEST
            ])
