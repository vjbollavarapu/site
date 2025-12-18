"""
Webhook service for sending webhook notifications
"""
import json
import logging
import requests
from django.utils import timezone
from django.conf import settings
from .models import WebhookConfig, WebhookEvent

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for sending webhooks"""
    
    @staticmethod
    def send_webhook(event_type, payload, entity_id=None):
        """
        Send webhook for a given event type
        
        Args:
            event_type: Type of event (contact_submission, waitlist_join, etc.)
            payload: Data to send in webhook
            entity_id: Optional entity ID for tracking
        """
        # Get active webhook configs for this event type
        webhook_configs = WebhookConfig.objects.filter(
            event_type=event_type,
            is_active=True
        )
        
        if not webhook_configs.exists():
            logger.debug(f"No webhook configs found for event type: {event_type}")
            return
        
        for config in webhook_configs:
            try:
                WebhookService._send_webhook_request(config, payload, entity_id)
            except Exception as e:
                logger.error(f"Error sending webhook {config.name}: {str(e)}")
                # Create failed event record
                WebhookService._create_webhook_event(
                    config, event_type, payload, 'failed', error_message=str(e)
                )
    
    @staticmethod
    def _send_webhook_request(config, payload, entity_id=None):
        """Send webhook request to configured URL"""
        import hmac
        import hashlib
        
        # Prepare payload
        payload_str = json.dumps(payload, sort_keys=True)
        
        # Generate signature
        secret = config.secret_key.encode('utf-8')
        signature = hmac.new(secret, payload_str.encode('utf-8'), hashlib.sha256).hexdigest()
        
        # Create webhook event record
        webhook_event = WebhookEvent.objects.create(
            webhook_config=config,
            event_type=config.event_type,
            payload=payload,
            signature=signature,
            status='pending'
        )
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': f'sha256={signature}',
            'X-Webhook-Event': config.event_type,
            'X-Webhook-Id': str(webhook_event.id),
        }
        
        # Add custom headers
        if config.headers:
            headers.update(config.headers)
        
        # Send request
        try:
            response = requests.post(
                config.url,
                json=payload,
                headers=headers,
                timeout=config.timeout
            )
            
            if response.status_code >= 200 and response.status_code < 300:
                # Success
                webhook_event.mark_as_sent(
                    response.status_code,
                    response.text[:1000]
                )
                logger.info(f"Webhook {config.name} sent successfully")
            else:
                # Failed
                webhook_event.mark_as_failed(
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response.status_code,
                    response.text[:1000]
                )
                logger.warning(f"Webhook {config.name} failed with status {response.status_code}")
        
        except requests.exceptions.Timeout:
            webhook_event.mark_as_failed("Request timeout", error_message="Request timed out")
            logger.error(f"Webhook {config.name} timed out")
        
        except requests.exceptions.RequestException as e:
            webhook_event.mark_as_failed(str(e), error_message=str(e))
            logger.error(f"Webhook {config.name} request failed: {str(e)}")
    
    @staticmethod
    def _create_webhook_event(config, event_type, payload, status, error_message=''):
        """Create webhook event record"""
        WebhookEvent.objects.create(
            webhook_config=config,
            event_type=event_type,
            payload=payload,
            status=status,
            error_message=error_message
        )
    
    @staticmethod
    def retry_failed_webhooks():
        """Retry failed webhooks that are due for retry"""
        from django.utils import timezone
        
        retry_events = WebhookEvent.objects.filter(
            status='retrying',
            next_retry_at__lte=timezone.now()
        )
        
        for event in retry_events:
            try:
                WebhookService._send_webhook_request(
                    event.webhook_config,
                    event.payload
                )
            except Exception as e:
                logger.error(f"Error retrying webhook {event.id}: {str(e)}")
    
    @staticmethod
    def verify_signature(payload_str, signature, secret_key):
        """
        Verify webhook signature
        
        Args:
            payload_str: Webhook payload as string
            signature: Signature from X-Webhook-Signature header
            secret_key: Secret key for verification
        
        Returns:
            bool: True if signature is valid
        """
        import hmac
        import hashlib
        
        # Remove 'sha256=' prefix if present
        if signature.startswith('sha256='):
            signature = signature[7:]
        
        # Generate expected signature
        secret = secret_key.encode('utf-8')
        expected_signature = hmac.new(secret, payload_str.encode('utf-8'), hashlib.sha256).hexdigest()
        
        # Compare signatures (constant-time comparison)
        return hmac.compare_digest(signature, expected_signature)


# Global webhook service instance
webhook_service = WebhookService()

