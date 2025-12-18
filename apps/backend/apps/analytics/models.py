import uuid
import hashlib
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from apps.core.models import Site


class PageView(models.Model):
    DEVICE_TYPE_CHOICES = [
        ('desktop', 'Desktop'),
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Site tracking
    site = models.ForeignKey(
        Site,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='page_views',
        help_text="Site/domain where this page view came from"
    )
    
    session_id = models.CharField(max_length=100, db_index=True)
    page_url = models.URLField()
    page_title = models.CharField(max_length=500, blank=True, null=True)
    referrer_url = models.URLField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # IP address hashed for GDPR compliance
    ip_address_hash = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPE_CHOICES, blank=True, null=True)
    browser = models.CharField(max_length=100, blank=True, null=True)
    operating_system = models.CharField(max_length=100, blank=True, null=True)
    
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    duration = models.FloatField(null=True, blank=True, help_text="Time on page in seconds")
    is_exit_page = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Page View'
        verbose_name_plural = 'Page Views'
        indexes = [
            models.Index(fields=['session_id', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.page_url} - {self.timestamp}"
    
    @staticmethod
    def hash_ip_address(ip_address):
        """Hash IP address for GDPR compliance"""
        if not ip_address:
            return None
        return hashlib.sha256(ip_address.encode()).hexdigest()
    
    def save(self, *args, **kwargs):
        # If IP address is provided but not hashed, hash it
        # Note: In practice, you'd hash the IP before saving
        super().save(*args, **kwargs)


class Event(models.Model):
    EVENT_CATEGORY_CHOICES = [
        ('user_interaction', 'User Interaction'),
        ('form', 'Form'),
        ('navigation', 'Navigation'),
        ('media', 'Media'),
        ('download', 'Download'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Site tracking
    site = models.ForeignKey(
        Site,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
        help_text="Site/domain where this event came from"
    )
    
    event_name = models.CharField(max_length=200, db_index=True)
    event_category = models.CharField(max_length=50, choices=EVENT_CATEGORY_CHOICES, default='other')
    event_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    event_properties = models.JSONField(default=dict, blank=True)
    
    session_id = models.CharField(max_length=100, db_index=True)
    page_url = models.URLField(blank=True, null=True)
    user_identifier = models.CharField(max_length=200, blank=True, null=True, db_index=True)
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        indexes = [
            models.Index(fields=['event_name', '-timestamp']),
            models.Index(fields=['session_id', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.event_name} - {self.timestamp}"


class Conversion(models.Model):
    CONVERSION_TYPE_CHOICES = [
        ('form_submission', 'Form Submission'),
        ('signup', 'Signup'),
        ('purchase', 'Purchase'),
        ('download', 'Download'),
        ('newsletter_subscription', 'Newsletter Subscription'),
        ('waitlist_signup', 'Waitlist Signup'),
        ('contact_submission', 'Contact Submission'),
        ('lead_capture', 'Lead Capture'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Site tracking
    site = models.ForeignKey(
        Site,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversions',
        help_text="Site/domain where this conversion came from"
    )
    
    conversion_type = models.CharField(max_length=50, choices=CONVERSION_TYPE_CHOICES, db_index=True)
    value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Generic foreign key to reference Lead, ContactSubmission, WaitlistEntry, etc.
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.UUIDField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    attribution_data = models.JSONField(default=dict, blank=True, help_text="UTM parameters, referrer, etc.")
    campaign_info = models.JSONField(default=dict, blank=True, help_text="Campaign name, source, medium, etc.")
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Conversion'
        verbose_name_plural = 'Conversions'
        indexes = [
            models.Index(fields=['conversion_type', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_conversion_type_display()} - {self.timestamp}"
    
    @property
    def related_object(self):
        """Get the related object (Lead, ContactSubmission, etc.)"""
        if self.content_type and self.object_id:
            try:
                return self.content_type.get_object_for_this_type(pk=self.object_id)
            except:
                return None
        return None

