"""
Webhook models for event notifications
"""
import uuid
import hmac
import hashlib
import json
from django.db import models
from django.utils import timezone
from django.conf import settings


class WebhookConfig(models.Model):
    """Configuration for webhook endpoints"""
    
    EVENT_TYPE_CHOICES = [
        ('contact_submission', 'Contact Submission'),
        ('waitlist_join', 'Waitlist Join'),
        ('lead_created', 'Lead Created'),
        ('lead_qualified', 'Lead Qualified'),
        ('lead_converted', 'Lead Converted'),
        ('newsletter_subscribe', 'Newsletter Subscribe'),
        ('conversion', 'Conversion'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    url = models.URLField(max_length=500)
    secret_key = models.CharField(max_length=200, help_text="Secret key for signature verification")
    is_active = models.BooleanField(default=True)
    retry_attempts = models.IntegerField(default=3, help_text="Number of retry attempts on failure")
    retry_delay = models.IntegerField(default=60, help_text="Delay between retries in seconds")
    timeout = models.IntegerField(default=30, help_text="Request timeout in seconds")
    
    headers = models.JSONField(default=dict, blank=True, help_text="Additional headers to include")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Webhook Configuration'
        verbose_name_plural = 'Webhook Configurations'
    
    def __str__(self):
        return f"{self.name} - {self.get_event_type_display()}"


class WebhookEvent(models.Model):
    """History of webhook events"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    webhook_config = models.ForeignKey(WebhookConfig, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=50)
    payload = models.JSONField()
    signature = models.CharField(max_length=200, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    attempt_count = models.IntegerField(default=0)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    
    response_status = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'next_retry_at']),
            models.Index(fields=['webhook_config', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.webhook_config.name} - {self.event_type} - {self.status}"
    
    def generate_signature(self, payload_str):
        """Generate HMAC signature for webhook payload"""
        secret = self.webhook_config.secret_key.encode('utf-8')
        signature = hmac.new(secret, payload_str.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature
    
    def mark_as_sent(self, response_status, response_body=''):
        """Mark webhook event as successfully sent"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.response_status = response_status
        self.response_body = response_body[:1000]  # Limit response body length
        self.save()
    
    def mark_as_failed(self, error_message, response_status=None, response_body=''):
        """Mark webhook event as failed"""
        self.attempt_count += 1
        self.last_attempt_at = timezone.now()
        self.error_message = error_message[:1000]  # Limit error message length
        
        if response_status:
            self.response_status = response_status
        if response_body:
            self.response_body = response_body[:1000]
        
        # Check if should retry
        if self.attempt_count < self.webhook_config.retry_attempts:
            self.status = 'retrying'
            from datetime import timedelta
            self.next_retry_at = timezone.now() + timedelta(seconds=self.webhook_config.retry_delay)
        else:
            self.status = 'failed'
        
        self.save()

