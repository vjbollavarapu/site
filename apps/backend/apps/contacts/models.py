import uuid
from django.db import models
from django.contrib.auth.models import User
from apps.core.models import Site


class ContactSubmission(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('resolved', 'Resolved'),
        ('archived', 'Archived'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=200, blank=True, null=True)
    
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Site tracking
    site = models.ForeignKey(
        Site,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contact_submissions',
        help_text="Site/domain where this submission came from"
    )
    
    source = models.URLField(blank=True, null=True, help_text="Website URL where form was submitted")
    referrer = models.URLField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_contacts')
    
    custom_data = models.JSONField(default=dict, blank=True)
    
    # A/B Testing
    ab_test_variant = models.CharField(max_length=1, blank=True, null=True, help_text="A/B test variant (A or B)")
    ab_test_name = models.CharField(max_length=200, blank=True, null=True, help_text="Name of A/B test")
    
    is_spam = models.BooleanField(default=False)
    spam_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    consent_given = models.BooleanField(default=False)
    consent_timestamp = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    contacted_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Submission'
        verbose_name_plural = 'Contact Submissions'
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
    
    def mark_as_contacted(self):
        """Mark submission as contacted"""
        from django.utils import timezone
        self.status = 'contacted'
        self.contacted_at = timezone.now()
        self.save()
    
    def mark_as_resolved(self):
        """Mark submission as resolved"""
        from django.utils import timezone
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()
    
    def mark_as_spam(self):
        """Mark submission as spam"""
        self.is_spam = True
        self.status = 'archived'
        self.save()

