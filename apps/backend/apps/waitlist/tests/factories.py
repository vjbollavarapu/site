"""
Test factories for WaitlistEntry
"""
import factory
from django.utils import timezone
from apps.waitlist.models import WaitlistEntry


class WaitlistEntryFactory(factory.django.DjangoModelFactory):
    """Factory for WaitlistEntry"""
    
    class Meta:
        model = WaitlistEntry
    
    email = factory.Faker('email')
    name = factory.Faker('name')
    company = factory.Faker('company')
    role = factory.Faker('job')
    company_size = '11-50'
    industry = 'technology'
    source = 'website'
    status = 'pending'
    marketing_consent = True
    consent_timestamp = factory.LazyFunction(timezone.now)

