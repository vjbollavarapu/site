import uuid
import secrets
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.core.models import Site


class WaitlistEntry(models.Model):
    COMPANY_SIZE_CHOICES = [
        ('1-10', '1-10'),
        ('11-50', '11-50'),
        ('51-200', '51-200'),
        ('201-1000', '201-1000'),
        ('1000+', '1000+'),
    ]
    
    INDUSTRY_CHOICES = [
        ('technology', 'Technology'),
        ('finance', 'Finance'),
        ('healthcare', 'Healthcare'),
        ('retail', 'Retail'),
        ('education', 'Education'),
        ('manufacturing', 'Manufacturing'),
        ('consulting', 'Consulting'),
        ('real_estate', 'Real Estate'),
        ('hospitality', 'Hospitality'),
        ('other', 'Other'),
    ]
    
    SOURCE_CHOICES = [
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('ad_campaign', 'Ad Campaign'),
        ('social_media', 'Social Media'),
        ('email_campaign', 'Email Campaign'),
        ('event', 'Event'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('invited', 'Invited'),
        ('onboarded', 'Onboarded'),
        ('declined', 'Declined'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    company = models.CharField(max_length=200, blank=True, null=True)
    role = models.CharField(max_length=200, blank=True, null=True, help_text="Job title/Role")
    
    company_size = models.CharField(max_length=20, choices=COMPANY_SIZE_CHOICES, blank=True, null=True)
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, blank=True, null=True)
    use_case = models.TextField(blank=True, null=True, help_text="Use case/Interest description")
    
    # Site tracking
    site = models.ForeignKey(
        Site,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='waitlist_entries',
        help_text="Site/domain where this entry came from"
    )
    
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='website')
    referral_code = models.CharField(max_length=100, blank=True, null=True)
    
    priority_score = models.IntegerField(default=0, help_text="Calculated priority score")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    invited_at = models.DateTimeField(null=True, blank=True)
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='invited_waitlist_entries')
    invite_code = models.CharField(max_length=100, blank=True, null=True, unique=True)
    
    expected_start_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True, help_text="Internal notes")
    
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_token = models.CharField(max_length=100, blank=True, null=True, unique=True)
    
    # A/B Testing
    ab_test_variant = models.CharField(max_length=1, blank=True, null=True, help_text="A/B test variant (A or B)")
    ab_test_name = models.CharField(max_length=200, blank=True, null=True, help_text="Name of A/B test")
    
    marketing_consent = models.BooleanField(default=False)
    consent_timestamp = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority_score', '-created_at']
        verbose_name = 'Waitlist Entry'
        verbose_name_plural = 'Waitlist Entries'
    
    def __str__(self):
        return f"{self.email} ({self.get_status_display()})"
    
    def calculate_priority_score(self):
        """Calculate priority score based on company size, role, industry, etc."""
        score = 0
        
        # Company size scoring
        if self.company_size == '1000+':
            score += 30
        elif self.company_size == '201-1000':
            score += 25
        elif self.company_size == '51-200':
            score += 20
        elif self.company_size == '11-50':
            score += 15
        elif self.company_size == '1-10':
            score += 10
        
        # Role/Title scoring (higher level roles get more points)
        if self.role:
            role_lower = self.role.lower()
            if any(title in role_lower for title in ['ceo', 'founder', 'president', 'owner', 'director', 'vp', 'vice president']):
                score += 25
            elif any(title in role_lower for title in ['manager', 'head', 'lead', 'senior']):
                score += 15
            elif any(title in role_lower for title in ['engineer', 'developer', 'analyst', 'specialist']):
                score += 10
        
        # Industry scoring
        if self.industry in ['technology', 'finance', 'healthcare']:
            score += 10
        elif self.industry:
            score += 5
        
        # Company name presence
        if self.company:
            score += 5
        
        # Use case description
        if self.use_case and len(self.use_case) > 50:
            score += 5
        
        # Email verification
        if self.is_verified:
            score += 5
        
        self.priority_score = min(100, score)  # Cap at 100
        return self.priority_score
    
    def approve(self):
        """Approve the waitlist entry"""
        self.status = 'approved'
        self.save()
    
    def send_invitation(self, user=None):
        """Send invitation and generate invite code"""
        if not self.invite_code:
            self.invite_code = secrets.token_urlsafe(32)
        
        self.status = 'invited'
        self.invited_at = timezone.now()
        if user:
            self.invited_by = user
        self.save()
        return self.invite_code
    
    def mark_onboarded(self):
        """Mark entry as onboarded"""
        self.status = 'onboarded'
        self.save()
    
    def verify(self):
        """Verify the email address"""
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save()
        # Recalculate priority score since verification affects it
        self.calculate_priority_score()
        self.save()
    
    def save(self, *args, **kwargs):
        """Override save to auto-calculate priority score"""
        # Only calculate if not already set or if relevant fields changed
        if not self.priority_score or any(field in ['company_size', 'role', 'industry', 'company', 'use_case', 'is_verified'] 
                                         for field in kwargs.get('update_fields', [])):
            self.calculate_priority_score()
        super().save(*args, **kwargs)

