import uuid
import secrets
from django.db import models
from django.utils import timezone
from apps.core.models import Site


class NewsletterSubscription(models.Model):
    STATUS_CHOICES = [
        ('subscribed', 'Subscribed'),
        ('unsubscribed', 'Unsubscribed'),
        ('bounced', 'Bounced'),
        ('complained', 'Complained'),
    ]
    
    SOURCE_CHOICES = [
        ('website', 'Website'),
        ('popup', 'Popup'),
        ('footer', 'Footer'),
        ('checkout', 'Checkout'),
        ('landing_page', 'Landing Page'),
        ('social_media', 'Social Media'),
        ('referral', 'Referral'),
        ('other', 'Other'),
    ]
    
    PREFERENCE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    
    # Site tracking
    site = models.ForeignKey(
        Site,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='newsletter_subscriptions',
        help_text="Site/domain where this subscription came from"
    )
    
    subscription_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='subscribed')
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='website')
    
    interests = models.JSONField(default=list, blank=True, help_text="List of interest tags")
    preference = models.CharField(max_length=20, choices=PREFERENCE_CHOICES, default='weekly')
    
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_token = models.CharField(max_length=100, blank=True, null=True, unique=True)
    
    consent_given = models.BooleanField(default=False)
    consent_timestamp = models.DateTimeField(null=True, blank=True)
    consent_text = models.TextField(blank=True, null=True, help_text="Text of consent agreement")
    
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    unsubscribe_reason = models.TextField(blank=True, null=True)
    unsubscribe_token = models.CharField(max_length=100, blank=True, null=True, unique=True)
    
    bounce_count = models.IntegerField(default=0)
    last_bounce_at = models.DateTimeField(null=True, blank=True)
    bounce_reason = models.TextField(blank=True, null=True)
    
    complaint_count = models.IntegerField(default=0)
    last_complaint_at = models.DateTimeField(null=True, blank=True)
    
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Newsletter Subscription'
        verbose_name_plural = 'Newsletter Subscriptions'
    
    def __str__(self):
        return f"{self.email} ({self.get_subscription_status_display()})"
    
    def subscribe(self):
        """Subscribe to newsletter"""
        self.subscription_status = 'subscribed'
        if not self.consent_given:
            self.consent_given = True
            self.consent_timestamp = timezone.now()
        self.save()
    
    def unsubscribe(self, reason=None, token=None):
        """Unsubscribe from newsletter"""
        self.subscription_status = 'unsubscribed'
        self.unsubscribed_at = timezone.now()
        if reason:
            self.unsubscribe_reason = reason
        if token:
            self.unsubscribe_token = token
        elif not self.unsubscribe_token:
            # Generate unsubscribe token if not provided
            self.unsubscribe_token = secrets.token_urlsafe(32)
        self.save()
    
    def verify(self):
        """Verify email address"""
        self.is_verified = True
        self.verified_at = timezone.now()
        if not self.verification_token:
            self.verification_token = secrets.token_urlsafe(32)
        self.save()
    
    def mark_bounced(self, reason=None):
        """Mark email as bounced"""
        self.subscription_status = 'bounced'
        self.bounce_count += 1
        self.last_bounce_at = timezone.now()
        if reason:
            self.bounce_reason = reason
        self.save()
    
    def mark_complained(self):
        """Mark as complained (spam complaint)"""
        self.subscription_status = 'complained'
        self.complaint_count += 1
        self.last_complaint_at = timezone.now()
        # Auto-unsubscribe on complaint
        if self.subscription_status != 'unsubscribed':
            self.unsubscribed_at = timezone.now()
        self.save()
    
    def save(self, *args, **kwargs):
        """Override save to generate tokens if needed"""
        # Generate verification token on first save if not set
        if not self.verification_token and not self.pk:
            self.verification_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

