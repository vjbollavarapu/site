"""
Core models for multi-site support
"""
import uuid
from django.db import models
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


class Site(models.Model):
    """
    Model to manage multiple websites/domains
    Each site can have its own configuration and tracking
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True, help_text="Internal name for the site")
    domain = models.CharField(
        max_length=255,
        unique=True,
        help_text="Primary domain (e.g., oasys360.com)"
    )
    display_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Display name for the site"
    )
    
    # URLs
    base_url = models.URLField(
        help_text="Full base URL (e.g., https://oasys360.com)"
    )
    
    # Configuration
    is_active = models.BooleanField(default=True, help_text="Whether this site is active")
    is_default = models.BooleanField(
        default=False,
        help_text="Default site for requests without site identifier"
    )
    
    # Additional domains (for www, subdomains, etc.)
    additional_domains = models.JSONField(
        default=list,
        blank=True,
        help_text="List of additional domains (e.g., ['www.oasys360.com'])"
    )
    
    # Metadata
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Site'
        verbose_name_plural = 'Sites'
    
    def __str__(self):
        return f"{self.display_name or self.name} ({self.domain})"
    
    def clean(self):
        """Validate domain and URL"""
        # Ensure domain doesn't include protocol
        if '://' in self.domain:
            raise ValidationError({'domain': 'Domain should not include protocol (http:// or https://)'})
        
        # Ensure base_url includes protocol
        if not self.base_url.startswith(('http://', 'https://')):
            raise ValidationError({'base_url': 'Base URL must include protocol (http:// or https://)'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_all_domains(self):
        """Get all domains associated with this site"""
        domains = [self.domain]
        if self.additional_domains:
            domains.extend(self.additional_domains)
        return domains
    
    @classmethod
    def get_site_from_domain(cls, domain):
        """
        Get site from domain name
        Checks both primary domain and additional domains
        """
        # Remove protocol if present
        if '://' in domain:
            from urllib.parse import urlparse
            domain = urlparse(domain).netloc
        
        # Remove www. prefix for matching
        domain_clean = domain.replace('www.', '')
        
        # Try to find by primary domain
        site = cls.objects.filter(
            models.Q(domain=domain) | 
            models.Q(domain=domain_clean) |
            models.Q(domain__icontains=domain_clean)
        ).first()
        
        if site:
            return site
        
        # Try to find by additional domains
        site = cls.objects.filter(
            additional_domains__contains=[domain]
        ).first()
        
        if site:
            return site
        
        # Return default site if exists
        return cls.objects.filter(is_default=True, is_active=True).first()
    
    @classmethod
    def get_site_from_request(cls, request):
        """
        Get site from request headers
        Checks Origin, Referer, and custom X-Site-Identifier header
        """
        # Check custom header first (for API calls)
        site_identifier = request.headers.get('X-Site-Identifier')
        if site_identifier:
            try:
                return cls.objects.get(id=site_identifier, is_active=True)
            except (cls.DoesNotExist, ValueError):
                pass
        
        # Check Origin header
        origin = request.headers.get('Origin')
        if origin:
            site = cls.get_site_from_domain(origin)
            if site:
                return site
        
        # Check Referer header
        referer = request.META.get('HTTP_REFERER', '')
        if referer:
            site = cls.get_site_from_domain(referer)
            if site:
                return site
        
        # Check Host header
        host = request.get_host()
        if host:
            site = cls.get_site_from_domain(host)
            if site:
                return site
        
        # Return default site
        return cls.objects.filter(is_default=True, is_active=True).first()

