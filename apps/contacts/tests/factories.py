"""
Test factories for ContactSubmission
"""
import factory
from django.utils import timezone
from apps.contacts.models import ContactSubmission


class ContactSubmissionFactory(factory.django.DjangoModelFactory):
    """Factory for ContactSubmission"""
    
    class Meta:
        model = ContactSubmission
    
    name = factory.Faker('name')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    company = factory.Faker('company')
    subject = factory.Faker('sentence', nb_words=4)
    message = factory.Faker('text', max_nb_chars=500)
    source = factory.Faker('url')
    referrer = factory.Faker('url')
    status = 'new'
    priority = 'medium'
    is_spam = False
    spam_score = 0.0
    consent_given = True
    consent_timestamp = factory.LazyFunction(timezone.now)

