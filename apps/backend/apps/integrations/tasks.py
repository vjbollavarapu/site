"""
Celery tasks for async email sending
"""
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_email_task(self, subject, to_email, html_content, text_content):
    """
    Celery task for sending emails asynchronously
    """
    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
        
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[to_email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def sync_to_crm_task(self, entity_type, entity_id):
    """
    Celery task for syncing entities to CRM with retry logic
    """
    from .crm_service import crm_service
    
    try:
        if entity_type == 'contact':
            from apps.contacts.models import ContactSubmission
            entity = ContactSubmission.objects.get(pk=entity_id)
            return crm_service.sync_contact_submission(entity, immediate=True)
        elif entity_type == 'waitlist':
            from apps.waitlist.models import WaitlistEntry
            entity = WaitlistEntry.objects.get(pk=entity_id)
            return crm_service.sync_waitlist_entry(entity, immediate=True)
        elif entity_type == 'lead':
            from apps.leads.models import Lead
            entity = Lead.objects.get(pk=entity_id)
            return crm_service.sync_lead(entity, immediate=True)
    except Exception as e:
        logger.error(f"CRM sync task error: {str(e)}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task
def retry_failed_webhooks():
    """Celery task to retry failed webhooks"""
    from apps.webhooks.services import WebhookService
    WebhookService.retry_failed_webhooks()
    logger.info("Failed webhooks retry completed")


@shared_task
def update_ab_test_stats():
    """Celery task to update A/B test statistics"""
    from apps.ab_testing.models import ABTest
    from apps.ab_testing.services import ABTestingService
    
    active_tests = ABTest.objects.filter(status='active')
    for test in active_tests:
        ABTestingService.update_test_stats(test)
    logger.info(f"Updated statistics for {active_tests.count()} A/B tests")

