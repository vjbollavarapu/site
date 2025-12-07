import uuid
from django.db import models
from django.contrib.auth.models import User


class Lead(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('unqualified', 'Unqualified'),
        ('converted', 'Converted'),
        ('lost', 'Lost'),
    ]
    
    LIFECYCLE_STAGE_CHOICES = [
        ('visitor', 'Visitor'),
        ('lead', 'Lead'),
        ('marketing_qualified', 'Marketing Qualified'),
        ('sales_qualified', 'Sales Qualified'),
        ('customer', 'Customer'),
    ]
    
    SOURCE_CHOICES = [
        ('organic', 'Organic'),
        ('paid_ad', 'Paid Ad'),
        ('referral', 'Referral'),
        ('social_media', 'Social Media'),
        ('email_campaign', 'Email Campaign'),
        ('website', 'Website'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=200, blank=True, null=True)
    
    lead_source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='website')
    lead_score = models.IntegerField(default=0, help_text="Score from 0-100")
    
    industry = models.CharField(max_length=100, blank=True, null=True)
    job_title = models.CharField(max_length=200, blank=True, null=True)
    company_size = models.CharField(max_length=50, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    lifecycle_stage = models.CharField(max_length=30, choices=LIFECYCLE_STAGE_CHOICES, default='lead')
    
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_leads')
    assigned_at = models.DateTimeField(null=True, blank=True)
    
    custom_data = models.JSONField(default=dict, blank=True)
    
    # A/B Testing
    ab_test_variant = models.CharField(max_length=1, blank=True, null=True, help_text="A/B test variant (A or B)")
    ab_test_name = models.CharField(max_length=200, blank=True, null=True, help_text="Name of A/B test")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_contacted_at = models.DateTimeField(null=True, blank=True)
    converted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def calculate_lead_score(self):
        """Calculate lead score based on various factors"""
        score = 0
        if self.company:
            score += 10
        if self.job_title:
            score += 10
        if self.phone:
            score += 5
        if self.industry:
            score += 5
        # Add more scoring logic as needed
        self.lead_score = min(100, score)
        return self.lead_score
    
    def qualify(self):
        """Mark lead as qualified"""
        self.status = 'qualified'
        self.lifecycle_stage = 'sales_qualified'
        self.save()
    
    def convert(self):
        """Convert lead to customer"""
        from django.utils import timezone
        self.status = 'converted'
        self.lifecycle_stage = 'customer'
        self.converted_at = timezone.now()
        self.save()

