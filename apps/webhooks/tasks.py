"""
Celery tasks for webhooks
"""
from celery import shared_task
import logging
from .services import WebhookService

logger = logging.getLogger(__name__)


@shared_task
def send_webhook_task(event_type, payload, entity_id=None):
    """Celery task to send webhook"""
    try:
        WebhookService.send_webhook(event_type, payload, entity_id)
        return True
    except Exception as e:
        logger.error(f"Webhook task failed: {str(e)}")
        raise


@shared_task
def retry_failed_webhooks_task():
    """Celery task to retry failed webhooks"""
    try:
        WebhookService.retry_failed_webhooks()
        return True
    except Exception as e:
        logger.error(f"Retry webhooks task failed: {str(e)}")
        raise

