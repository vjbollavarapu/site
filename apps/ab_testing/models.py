"""
A/B Testing models
"""
import uuid
import hashlib
from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class ABTest(models.Model):
    """A/B test configuration"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    test_type = models.CharField(max_length=50, help_text="Type of test (e.g., 'landing_page', 'form_variant')")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    variant_a_name = models.CharField(max_length=100, default='Control')
    variant_b_name = models.CharField(max_length=100, default='Variant')
    
    traffic_split = models.IntegerField(default=50, help_text="Percentage of traffic to variant B (0-100)")
    
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'A/B Test'
        verbose_name_plural = 'A/B Tests'
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    def is_active(self):
        """Check if test is currently active"""
        if self.status != 'active':
            return False
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True
    
    def assign_variant(self, user_identifier):
        """
        Assign a variant to a user based on consistent hashing
        
        Args:
            user_identifier: Unique identifier for user (email, session_id, etc.)
        
        Returns:
            str: 'A' or 'B'
        """
        # Create consistent hash
        hash_input = f"{self.id}_{user_identifier}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        # Assign based on traffic split
        threshold = (self.traffic_split / 100) * 100
        if (hash_value % 100) < threshold:
            return 'B'
        else:
            return 'A'


class VariantAssignment(models.Model):
    """Track variant assignments to users"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ab_test = models.ForeignKey(ABTest, on_delete=models.CASCADE, related_name='assignments')
    user_identifier = models.CharField(max_length=200, db_index=True, help_text="Email, session_id, or other unique identifier")
    variant = models.CharField(max_length=1, choices=[('A', 'Variant A'), ('B', 'Variant B')])
    
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['ab_test', 'user_identifier']
        indexes = [
            models.Index(fields=['ab_test', 'variant']),
            models.Index(fields=['user_identifier']),
        ]
    
    def __str__(self):
        return f"{self.ab_test.name} - {self.user_identifier} - {self.variant}"


class ConversionByVariant(models.Model):
    """Track conversions by variant"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ab_test = models.ForeignKey(ABTest, on_delete=models.CASCADE, related_name='conversions')
    variant = models.CharField(max_length=1, choices=[('A', 'Variant A'), ('B', 'Variant B')])
    
    # Link to conversion
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    conversion_object = GenericForeignKey('content_type', 'object_id')
    
    conversion_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    conversion_type = models.CharField(max_length=50, default='form_submission')
    
    user_identifier = models.CharField(max_length=200, db_index=True)
    
    converted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-converted_at']
        indexes = [
            models.Index(fields=['ab_test', 'variant']),
            models.Index(fields=['user_identifier']),
        ]
    
    def __str__(self):
        return f"{self.ab_test.name} - {self.variant} - {self.conversion_type}"


class ABTestStats(models.Model):
    """Pre-calculated statistics for A/B tests"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ab_test = models.OneToOneField(ABTest, on_delete=models.CASCADE, related_name='stats')
    
    variant_a_visitors = models.IntegerField(default=0)
    variant_b_visitors = models.IntegerField(default=0)
    
    variant_a_conversions = models.IntegerField(default=0)
    variant_b_conversions = models.IntegerField(default=0)
    
    variant_a_conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    variant_b_conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    statistical_significance = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="P-value")
    confidence_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Confidence level percentage")
    
    winner = models.CharField(max_length=1, choices=[('A', 'Variant A'), ('B', 'Variant B'), ('N', 'No winner')], null=True, blank=True)
    
    last_calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'A/B Test Statistics'
        verbose_name_plural = 'A/B Test Statistics'
    
    def __str__(self):
        return f"Stats for {self.ab_test.name}"
    
    def calculate_stats(self):
        """Calculate and update statistics"""
        
        # Get visitor counts
        self.variant_a_visitors = VariantAssignment.objects.filter(
            ab_test=self.ab_test,
            variant='A'
        ).count()
        
        self.variant_b_visitors = VariantAssignment.objects.filter(
            ab_test=self.ab_test,
            variant='B'
        ).count()
        
        # Get conversion counts
        self.variant_a_conversions = ConversionByVariant.objects.filter(
            ab_test=self.ab_test,
            variant='A'
        ).count()
        
        self.variant_b_conversions = ConversionByVariant.objects.filter(
            ab_test=self.ab_test,
            variant='B'
        ).count()
        
        # Calculate conversion rates
        if self.variant_a_visitors > 0:
            self.variant_a_conversion_rate = (self.variant_a_conversions / self.variant_a_visitors) * 100
        if self.variant_b_visitors > 0:
            self.variant_b_conversion_rate = (self.variant_b_conversions / self.variant_b_visitors) * 100
        
        # Calculate statistical significance (chi-square test)
        if self.variant_a_visitors > 0 and self.variant_b_visitors > 0:
            try:
                from scipy import stats
                
                # Create contingency table
                # [conversions_A, non_conversions_A]
                # [conversions_B, non_conversions_B]
                contingency = [
                    [self.variant_a_conversions, self.variant_a_visitors - self.variant_a_conversions],
                    [self.variant_b_conversions, self.variant_b_visitors - self.variant_b_conversions]
                ]
                
                chi2, p_value = stats.chi2_contingency(contingency)[:2]
                self.statistical_significance = float(p_value)
                self.confidence_level = (1 - float(p_value)) * 100
                
                # Determine winner (if significant)
                if p_value < 0.05:  # 95% confidence
                    if self.variant_b_conversion_rate > self.variant_a_conversion_rate:
                        self.winner = 'B'
                    elif self.variant_a_conversion_rate > self.variant_b_conversion_rate:
                        self.winner = 'A'
                    else:
                        self.winner = 'N'
                else:
                    self.winner = 'N'
            except ImportError:
                logger.warning("scipy not installed, using simple calculation")
                # Fallback: simple winner determination
                if self.variant_b_conversion_rate > self.variant_a_conversion_rate:
                    self.winner = 'B'
                elif self.variant_a_conversion_rate > self.variant_b_conversion_rate:
                    self.winner = 'A'
                else:
                    self.winner = 'N'
                self.statistical_significance = None
                self.confidence_level = None
            except Exception as e:
                logger.error(f"Error calculating statistical significance: {e}")
                # If calculation fails, set to None
                self.statistical_significance = None
                self.confidence_level = None
                self.winner = 'N'
        
        self.save()
    
    def _calculate_stats_simple(self):
        """Simple statistics calculation without scipy"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Get visitor counts
        self.variant_a_visitors = VariantAssignment.objects.filter(
            ab_test=self.ab_test,
            variant='A'
        ).count()
        
        self.variant_b_visitors = VariantAssignment.objects.filter(
            ab_test=self.ab_test,
            variant='B'
        ).count()
        
        # Get conversion counts
        self.variant_a_conversions = ConversionByVariant.objects.filter(
            ab_test=self.ab_test,
            variant='A'
        ).count()
        
        self.variant_b_conversions = ConversionByVariant.objects.filter(
            ab_test=self.ab_test,
            variant='B'
        ).count()
        
        # Calculate conversion rates
        if self.variant_a_visitors > 0:
            self.variant_a_conversion_rate = (self.variant_a_conversions / self.variant_a_visitors) * 100
        if self.variant_b_visitors > 0:
            self.variant_b_conversion_rate = (self.variant_b_conversions / self.variant_b_visitors) * 100
        
        # Simple winner determination (without statistical significance)
        if self.variant_b_conversion_rate > self.variant_a_conversion_rate:
            self.winner = 'B'
        elif self.variant_a_conversion_rate > self.variant_b_conversion_rate:
            self.winner = 'A'
        else:
            self.winner = 'N'
        
        self.statistical_significance = None
        self.confidence_level = None
        
        self.save()

