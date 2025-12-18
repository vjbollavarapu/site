"""
Test factories for Analytics models
"""
import factory
from django.utils import timezone
from apps.analytics.models import PageView, Event, Conversion


class PageViewFactory(factory.django.DjangoModelFactory):
    """Factory for PageView"""
    
    class Meta:
        model = PageView
    
    session_id = factory.Faker('uuid4')
    page_url = factory.Faker('url')
    page_title = factory.Faker('sentence', nb_words=4)
    device_type = 'desktop'
    browser = 'Chrome'
    operating_system = 'Windows'
    timestamp = factory.LazyFunction(timezone.now)


class EventFactory(factory.django.DjangoModelFactory):
    """Factory for Event"""
    
    class Meta:
        model = Event
    
    event_name = factory.Faker('word')
    event_category = 'user_interaction'
    session_id = factory.Faker('uuid4')
    page_url = factory.Faker('url')
    timestamp = factory.LazyFunction(timezone.now)


class ConversionFactory(factory.django.DjangoModelFactory):
    """Factory for Conversion"""
    
    class Meta:
        model = Conversion
    
    conversion_type = 'form_submission'
    value = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    timestamp = factory.LazyFunction(timezone.now)

