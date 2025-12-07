"""
Test factories for GDPR models
"""
import factory
from django.utils import timezone
from apps.gdpr.models import Consent, PrivacyPolicy, DataRetentionPolicy


class PrivacyPolicyFactory(factory.django.DjangoModelFactory):
    """Factory for PrivacyPolicy"""
    
    class Meta:
        model = PrivacyPolicy
    
    version = factory.Sequence(lambda n: f"1.{n}")
    title = factory.Faker('sentence', nb_words=3)
    content = factory.Faker('text', max_nb_chars=1000)
    is_active = True
    effective_date = factory.LazyFunction(timezone.now().date)


class ConsentFactory(factory.django.DjangoModelFactory):
    """Factory for Consent"""
    
    class Meta:
        model = Consent
    
    email = factory.Faker('email')
    consent_type = 'marketing'
    consent_given = True
    consent_timestamp = factory.LazyFunction(timezone.now)
    privacy_policy = factory.SubFactory(PrivacyPolicyFactory)


class DataRetentionPolicyFactory(factory.django.DjangoModelFactory):
    """Factory for DataRetentionPolicy"""
    
    class Meta:
        model = DataRetentionPolicy
    
    data_type = 'contact'
    retention_days = 365
    auto_delete = False
    anonymize_instead = True
    is_active = True

