"""
GDPR compliance models
"""
import uuid
import hashlib
from django.db import models
from django.utils import timezone


class PrivacyPolicy(models.Model):
    """
    Store privacy policy versions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = models.CharField(max_length=50, unique=True, help_text="Version identifier (e.g., '1.0', '2024-01-01')")
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Full privacy policy text")
    
    is_active = models.BooleanField(default=True, help_text="Currently active policy")
    effective_date = models.DateField(help_text="Date when this policy becomes effective")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-effective_date', '-created_at']
        verbose_name = 'Privacy Policy'
        verbose_name_plural = 'Privacy Policies'
    
    def __str__(self):
        return f"Privacy Policy {self.version} ({'Active' if self.is_active else 'Inactive'})"
    
    def save(self, *args, **kwargs):
        # Deactivate other policies when activating a new one
        if self.is_active:
            PrivacyPolicy.objects.exclude(id=self.id).update(is_active=False)
        super().save(*args, **kwargs)


class Consent(models.Model):
    """
    Track user consent for GDPR compliance
    """
    CONSENT_TYPE_CHOICES = [
        ('marketing', 'Marketing'),
        ('analytics', 'Analytics'),
        ('necessary', 'Necessary'),
        ('functional', 'Functional'),
        ('advertising', 'Advertising'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(db_index=True, help_text="User email address")
    
    consent_type = models.CharField(max_length=20, choices=CONSENT_TYPE_CHOICES, db_index=True)
    consent_given = models.BooleanField(default=False, help_text="Whether consent was given")
    
    consent_timestamp = models.DateTimeField(null=True, blank=True, help_text="When consent was given")
    consent_text = models.TextField(blank=True, null=True, help_text="Text of what they consented to")
    
    withdrawal_timestamp = models.DateTimeField(null=True, blank=True, help_text="When consent was withdrawn")
    withdrawal_reason = models.TextField(blank=True, null=True, help_text="Reason for withdrawal")
    
    # Link to privacy policy version
    privacy_policy = models.ForeignKey(
        PrivacyPolicy,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consents',
        help_text="Privacy policy version at time of consent"
    )
    
    # IP address (hashed for GDPR)
    ip_address_hash = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    
    # Additional metadata
    user_agent = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=200, blank=True, null=True, help_text="Where consent was given")
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-consent_timestamp', '-created_at']
        verbose_name = 'Consent'
        verbose_name_plural = 'Consents'
        indexes = [
            models.Index(fields=['email', 'consent_type']),
            models.Index(fields=['email', '-consent_timestamp']),
        ]
        # Note: unique_together removed - allow multiple consent records for same email/type
        # This enables tracking consent history
    
    def __str__(self):
        status = "Given" if self.consent_given else "Withdrawn"
        return f"{self.email} - {self.get_consent_type_display()} - {status}"
    
    @staticmethod
    def hash_ip_address(ip_address):
        """Hash IP address for GDPR compliance"""
        if not ip_address:
            return None
        return hashlib.sha256(ip_address.encode()).hexdigest()
    
    def withdraw(self, reason=None):
        """Withdraw consent"""
        self.consent_given = False
        self.withdrawal_timestamp = timezone.now()
        if reason:
            self.withdrawal_reason = reason
        self.save()


class DataRetentionPolicy(models.Model):
    """
    Configure data retention policies per data type
    """
    DATA_TYPE_CHOICES = [
        ('contact', 'Contact Submissions'),
        ('waitlist', 'Waitlist Entries'),
        ('lead', 'Leads'),
        ('newsletter', 'Newsletter Subscriptions'),
        ('analytics_pageview', 'Analytics Page Views'),
        ('analytics_event', 'Analytics Events'),
        ('analytics_conversion', 'Analytics Conversions'),
        ('consent', 'Consent Records'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data_type = models.CharField(max_length=50, choices=DATA_TYPE_CHOICES, unique=True)
    
    retention_days = models.IntegerField(help_text="Number of days to retain data (0 = keep forever)")
    auto_delete = models.BooleanField(default=False, help_text="Automatically delete after retention period")
    anonymize_instead = models.BooleanField(default=False, help_text="Anonymize instead of deleting")
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['data_type']
        verbose_name = 'Data Retention Policy'
        verbose_name_plural = 'Data Retention Policies'
    
    def __str__(self):
        action = "Anonymize" if self.anonymize_instead else "Delete"
        return f"{self.get_data_type_display()} - {self.retention_days} days ({action})"


class DataDeletionAudit(models.Model):
    """
    Audit trail for data deletions (optional)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(db_index=True)
    
    deletion_type = models.CharField(
        max_length=20,
        choices=[
            ('full', 'Full Deletion'),
            ('anonymize', 'Anonymization'),
            ('partial', 'Partial Deletion'),
        ]
    )
    
    data_types_deleted = models.JSONField(
        default=list,
        help_text="List of data types that were deleted/anonymized"
    )
    
    deletion_timestamp = models.DateTimeField(auto_now_add=True)
    deleted_by = models.CharField(max_length=200, blank=True, null=True, help_text="Who initiated deletion")
    ip_address_hash = models.CharField(max_length=64, blank=True, null=True)
    
    confirmation_token = models.CharField(max_length=100, unique=True, blank=True, null=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-deletion_timestamp']
        verbose_name = 'Data Deletion Audit'
        verbose_name_plural = 'Data Deletion Audits'
    
    def __str__(self):
        return f"{self.email} - {self.get_deletion_type_display()} - {self.deletion_timestamp}"

