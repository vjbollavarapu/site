"""
Test factories for Lead
"""
import factory
from apps.leads.models import Lead


class LeadFactory(factory.django.DjangoModelFactory):
    """Factory for Lead"""
    
    class Meta:
        model = Lead
    
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    company = factory.Faker('company')
    lead_source = 'website'
    lead_score = 50
    status = 'new'
    lifecycle_stage = 'lead'

