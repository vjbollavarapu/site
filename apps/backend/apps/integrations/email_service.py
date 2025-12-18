"""
Email service supporting multiple providers
"""
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Unified email service supporting multiple providers
    """
    
    def __init__(self):
        self.backend = getattr(settings, 'EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
        self.frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
    
    def send_email(self, subject, to_email, template_name, context, use_celery=True):
        """
        Send email using template
        
        Args:
            subject: Email subject
            to_email: Recipient email address
            template_name: Template name (without .html/.txt extension)
            context: Template context dictionary
            use_celery: Whether to use Celery for async sending (if available)
        
        Returns:
            bool: Success status
        """
        try:
            # Render HTML template
            html_content = render_to_string(f'emails/{template_name}.html', context)
            
            # Render plain text template
            try:
                text_content = render_to_string(f'emails/{template_name}.txt', context)
            except:
                # Fallback: convert HTML to text
                text_content = strip_tags(html_content)
            
            # Send email
            if use_celery and self._is_celery_available():
                # Use Celery task for async sending
                from .tasks import send_email_task
                send_email_task.delay(subject, to_email, html_content, text_content)
                return True
            else:
                # Send synchronously
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=self.from_email,
                    to=[to_email]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                return True
        
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_contact_confirmation(self, contact_submission):
        """Send contact form confirmation email"""
        context = {
            'name': contact_submission.name,
            'subject': contact_submission.subject,
            'submission_id': str(contact_submission.id),
            'expected_response_time': '24-48 hours',
            'frontend_url': self.frontend_url
        }
        
        return self.send_email(
            subject='Thank you for contacting us',
            to_email=contact_submission.email,
            template_name='contact_confirmation',
            context=context
        )
    
    def send_waitlist_verification(self, waitlist_entry, use_celery=None):
        """Send waitlist verification email"""
        verification_url = f"{self.frontend_url}/waitlist/verify/{waitlist_entry.verification_token}/"
        
        context = {
            'name': waitlist_entry.name or 'there',
            'email': waitlist_entry.email,
            'verification_url': verification_url,
            'verification_token': waitlist_entry.verification_token,
            'expires_hours': 24,
            'frontend_url': self.frontend_url
        }
        
        # Default to synchronous if Celery not explicitly requested
        # This ensures emails are sent even if Celery worker is not running
        if use_celery is None:
            use_celery = False
        
        return self.send_email(
            subject='Verify your email - Waitlist',
            to_email=waitlist_entry.email,
            template_name='waitlist_verification',
            context=context,
            use_celery=use_celery
        )
    
    def send_waitlist_invitation(self, waitlist_entry):
        """Send waitlist invitation email"""
        invite_url = f"{self.frontend_url}/invite/{waitlist_entry.invite_code}/"
        
        context = {
            'name': waitlist_entry.name or 'there',
            'email': waitlist_entry.email,
            'invite_code': waitlist_entry.invite_code,
            'invite_url': invite_url,
            'frontend_url': self.frontend_url
        }
        
        return self.send_email(
            subject="You're in! Welcome to our platform",
            to_email=waitlist_entry.email,
            template_name='waitlist_invitation',
            context=context
        )
    
    def send_newsletter_verification(self, subscription):
        """Send newsletter verification email (double opt-in)"""
        verification_url = f"{self.frontend_url}/newsletter/verify/{subscription.verification_token}/"
        unsubscribe_url = f"{self.frontend_url}/newsletter/unsubscribe/{subscription.unsubscribe_token}/"
        
        context = {
            'name': subscription.name or 'there',
            'email': subscription.email,
            'verification_url': verification_url,
            'unsubscribe_url': unsubscribe_url,
            'frontend_url': self.frontend_url
        }
        
        return self.send_email(
            subject='Confirm your subscription',
            to_email=subscription.email,
            template_name='newsletter_verification',
            context=context
        )
    
    def send_newsletter_welcome(self, subscription):
        """Send newsletter welcome email"""
        manage_url = f"{self.frontend_url}/newsletter/preferences/{subscription.unsubscribe_token}/"
        
        context = {
            'name': subscription.name or 'there',
            'email': subscription.email,
            'preference': subscription.get_preference_display(),
            'manage_url': manage_url,
            'frontend_url': self.frontend_url
        }
        
        return self.send_email(
            subject='Welcome to our newsletter!',
            to_email=subscription.email,
            template_name='newsletter_welcome',
            context=context
        )
    
    def send_newsletter_unsubscribe_confirmation(self, subscription):
        """Send unsubscribe confirmation email"""
        context = {
            'name': subscription.name or 'there',
            'email': subscription.email,
            'frontend_url': self.frontend_url
        }
        
        return self.send_email(
            subject='You have been unsubscribed',
            to_email=subscription.email,
            template_name='newsletter_unsubscribe',
            context=context
        )
    
    def _is_celery_available(self):
        """Check if Celery is available"""
        try:
            from celery import current_app
            return current_app.conf.task_always_eager is False
        except:
            return False


# Global email service instance
email_service = EmailService()

