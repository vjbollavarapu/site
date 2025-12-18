"""
Tests for NewsletterSubscription model
"""
from django.test import TestCase
from apps.newsletter.models import NewsletterSubscription
from apps.newsletter.tests.factories import NewsletterSubscriptionFactory


class NewsletterSubscriptionModelTest(TestCase):
    """Test NewsletterSubscription model"""
    
    def test_create_subscription(self):
        """Test creating a newsletter subscription"""
        subscription = NewsletterSubscriptionFactory()
        self.assertIsNotNone(subscription.id)
        self.assertEqual(subscription.subscription_status, 'subscribed')
        self.assertTrue(subscription.is_verified)
    
    def test_subscribe(self):
        """Test subscribe method"""
        subscription = NewsletterSubscriptionFactory(subscription_status='unsubscribed')
        subscription.subscribe()
        
        self.assertEqual(subscription.subscription_status, 'subscribed')
    
    def test_unsubscribe(self):
        """Test unsubscribe method"""
        subscription = NewsletterSubscriptionFactory(subscription_status='subscribed')
        subscription.unsubscribe(reason='No longer interested')
        
        self.assertEqual(subscription.subscription_status, 'unsubscribed')
        self.assertIsNotNone(subscription.unsubscribed_at)
        self.assertEqual(subscription.unsubscribe_reason, 'No longer interested')
    
    def test_verify(self):
        """Test verify method"""
        subscription = NewsletterSubscriptionFactory(is_verified=False)
        subscription.verify()
        
        self.assertTrue(subscription.is_verified)
        self.assertIsNotNone(subscription.verified_at)
    
    def test_mark_bounced(self):
        """Test mark_bounced method"""
        subscription = NewsletterSubscriptionFactory()
        initial_count = subscription.bounce_count
        
        subscription.mark_bounced()
        
        self.assertEqual(subscription.bounce_count, initial_count + 1)
        self.assertEqual(subscription.subscription_status, 'bounced')
    
    def test_unique_email_constraint(self):
        """Test unique email constraint"""
        NewsletterSubscriptionFactory(email='test@example.com')
        
        with self.assertRaises(Exception):
            NewsletterSubscriptionFactory(email='test@example.com')

