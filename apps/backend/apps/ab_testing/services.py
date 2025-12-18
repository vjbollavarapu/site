"""
A/B Testing service
"""
import logging
from django.contrib.contenttypes.models import ContentType
from .models import ABTest, VariantAssignment, ConversionByVariant, ABTestStats

logger = logging.getLogger(__name__)


class ABTestingService:
    """Service for A/B testing functionality"""
    
    @staticmethod
    def get_variant(test_name, user_identifier):
        """
        Get or assign variant for a user in an A/B test
        
        Args:
            test_name: Name of the A/B test
            user_identifier: Unique identifier for user (email, session_id, etc.)
        
        Returns:
            str: 'A' or 'B', or None if test not found/active
        """
        try:
            test = ABTest.objects.get(name=test_name, status='active')
            
            if not test.is_active():
                return None
            
            # Check if user already has assignment
            assignment = VariantAssignment.objects.filter(
                ab_test=test,
                user_identifier=user_identifier
            ).first()
            
            if assignment:
                return assignment.variant
            
            # Assign new variant
            variant = test.assign_variant(user_identifier)
            
            # Create assignment record
            VariantAssignment.objects.create(
                ab_test=test,
                user_identifier=user_identifier,
                variant=variant
            )
            
            return variant
        
        except ABTest.DoesNotExist:
            logger.debug(f"A/B test '{test_name}' not found or not active")
            return None
    
    @staticmethod
    def track_conversion(test_name, user_identifier, conversion_object, conversion_type='form_submission', conversion_value=None):
        """
        Track a conversion for an A/B test
        
        Args:
            test_name: Name of the A/B test
            user_identifier: User identifier
            conversion_object: The object that was converted (ContactSubmission, Lead, etc.)
            conversion_type: Type of conversion
            conversion_value: Optional monetary value
        """
        try:
            test = ABTest.objects.get(name=test_name)
            
            # Get user's variant assignment
            assignment = VariantAssignment.objects.filter(
                ab_test=test,
                user_identifier=user_identifier
            ).first()
            
            if not assignment:
                logger.warning(f"No variant assignment found for user {user_identifier} in test {test_name}")
                return
            
            # Create conversion record
            content_type = ContentType.objects.get_for_model(conversion_object)
            ConversionByVariant.objects.create(
                ab_test=test,
                variant=assignment.variant,
                content_type=content_type,
                object_id=conversion_object.id,
                conversion_type=conversion_type,
                conversion_value=conversion_value,
                user_identifier=user_identifier
            )
            
            # Update test statistics
            ABTestingService.update_test_stats(test)
        
        except ABTest.DoesNotExist:
            logger.error(f"A/B test '{test_name}' not found")
        except Exception as e:
            logger.error(f"Error tracking conversion: {str(e)}")
    
    @staticmethod
    def update_test_stats(test):
        """Update statistics for an A/B test"""
        try:
            stats, created = ABTestStats.objects.get_or_create(ab_test=test)
            stats.calculate_stats()
        except Exception as e:
            logger.error(f"Error updating test stats: {str(e)}")
    
    @staticmethod
    def get_test_results(test_name):
        """
        Get results for an A/B test
        
        Returns:
            dict: Test statistics and results
        """
        try:
            test = ABTest.objects.get(name=test_name)
            stats, created = ABTestStats.objects.get_or_create(ab_test=test)
            
            if not created:
                stats.calculate_stats()
            
            return {
                'test_name': test.name,
                'status': test.status,
                'variant_a': {
                    'name': test.variant_a_name,
                    'visitors': stats.variant_a_visitors,
                    'conversions': stats.variant_a_conversions,
                    'conversion_rate': float(stats.variant_a_conversion_rate),
                },
                'variant_b': {
                    'name': test.variant_b_name,
                    'visitors': stats.variant_b_visitors,
                    'conversions': stats.variant_b_conversions,
                    'conversion_rate': float(stats.variant_b_conversion_rate),
                },
                'statistical_significance': float(stats.statistical_significance) if stats.statistical_significance else None,
                'confidence_level': float(stats.confidence_level) if stats.confidence_level else None,
                'winner': stats.winner,
            }
        except ABTest.DoesNotExist:
            return None


# Global service instance
ab_testing_service = ABTestingService()

