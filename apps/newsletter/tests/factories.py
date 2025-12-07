"""
Test factories for NewsletterSubscription
"""
import factory
import secrets
from django.utils import timezone
from apps.newsletter.models import NewsletterSubscription


class NewsletterSubscriptionFactory(factory.django.DjangoModelFactory):
    """Factory for NewsletterSubscription"""
    
    class Meta:
        model = NewsletterSubscription
    
    email = factory.Faker('email')
    name = factory.Faker('name')
    subscription_status = 'subscribed'
    source = 'website'
    preference = 'weekly'
    is_verified = True
    verified_at = factory.LazyFunction(timezone.now)
    consent_given = True
    consent_timestamp = factory.LazyFunction(timezone.now)

