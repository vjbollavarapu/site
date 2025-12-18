"""
Celery tasks for GDPR compliance
"""
from celery import shared_task
import logging
from .services import GDPRService

logger = logging.getLogger(__name__)


@shared_task
def apply_data_retention_policies():
    """
    Background job to apply data retention policies
    Should be run daily via Celery Beat
    """
    try:
        summary = GDPRService.apply_retention_policies()
        logger.info(f"Applied data retention policies: {summary}")
        return summary
    except Exception as e:
        logger.error(f"Error applying retention policies: {str(e)}")
        return None
