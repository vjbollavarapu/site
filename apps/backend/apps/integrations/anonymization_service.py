"""
Data anonymization service for GDPR compliance
"""
import re
import hashlib
import logging
from datetime import datetime
from django.utils import timezone
from django.db import models
from django.conf import settings

logger = logging.getLogger(__name__)


class AnonymizationService:
    """
    Service for anonymizing personal data
    """
    
    # PII patterns for detection in free text
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
    SSN_PATTERN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
    CREDIT_CARD_PATTERN = re.compile(r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b')
    IP_PATTERN = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    
    @staticmethod
    def anonymize_email(email, method='hash'):
        """
        Anonymize email address
        
        Args:
            email: Email address to anonymize
            method: 'hash' (hash with prefix) or 'replace' (generic replacement)
        
        Returns:
            Anonymized email
        """
        if not email:
            return None
        
        email_lower = email.lower().strip()
        
        if method == 'hash':
            # Hash email and use as local part
            email_hash = hashlib.sha256(email_lower.encode()).hexdigest()[:16]
            return f"user_{email_hash}@anonymous.com"
        elif method == 'replace':
            return "user@anonymous.com"
        else:
            # Default: hash method
            email_hash = hashlib.sha256(email_lower.encode()).hexdigest()[:16]
            return f"user_{email_hash}@anonymous.com"
    
    @staticmethod
    def anonymize_name(name, method='replace'):
        """
        Anonymize name
        
        Args:
            name: Name to anonymize
            method: 'replace' (generic) or 'hash' (hashed identifier)
        
        Returns:
            Anonymized name
        """
        if not name:
            return None
        
        if method == 'replace':
            return "Anonymous User"
        elif method == 'hash':
            name_hash = hashlib.sha256(name.encode()).hexdigest()[:8]
            return f"User_{name_hash}"
        else:
            return "Anonymous User"
    
    @staticmethod
    def anonymize_phone(phone, method='remove'):
        """
        Anonymize phone number
        
        Args:
            phone: Phone number to anonymize
            method: 'remove' (empty string) or 'hash' (hashed value)
        
        Returns:
            Anonymized phone (empty string or hashed)
        """
        if not phone:
            return ""
        
        if method == 'remove':
            return ""
        elif method == 'hash':
            phone_hash = hashlib.sha256(phone.encode()).hexdigest()[:12]
            return f"***-***-{phone_hash[:4]}"
        else:
            return ""
    
    @staticmethod
    def anonymize_ip(ip_address, method='hash'):
        """
        Anonymize IP address
        
        Args:
            ip_address: IP address to anonymize
            method: 'hash' (full hash) or 'truncate' (remove last octet)
        
        Returns:
            Anonymized IP
        """
        if not ip_address:
            return None
        
        if method == 'truncate':
            # Remove last octet for IPv4
            if '.' in ip_address:
                parts = ip_address.split('.')
                if len(parts) == 4:
                    return '.'.join(parts[:3]) + '.0'
            # For IPv6, remove last 64 bits
            elif ':' in ip_address:
                parts = ip_address.split(':')
                if len(parts) >= 4:
                    return ':'.join(parts[:4]) + '::'
            return ip_address
        elif method == 'hash':
            # Full hash
            return hashlib.sha256(ip_address.encode()).hexdigest()
        else:
            # Default: truncate
            if '.' in ip_address:
                parts = ip_address.split('.')
                if len(parts) == 4:
                    return '.'.join(parts[:3]) + '.0'
            return ip_address
    
    @staticmethod
    def remove_pii_from_text(text):
        """
        Remove PII patterns from free text
        
        Args:
            text: Text to clean
        
        Returns:
            Text with PII patterns removed/replaced
        """
        if not text:
            return ""
        
        # Replace email addresses
        text = AnonymizationService.EMAIL_PATTERN.sub('[EMAIL_REMOVED]', text)
        
        # Replace phone numbers
        text = AnonymizationService.PHONE_PATTERN.sub('[PHONE_REMOVED]', text)
        
        # Replace SSN
        text = AnonymizationService.SSN_PATTERN.sub('[SSN_REMOVED]', text)
        
        # Replace credit card numbers
        text = AnonymizationService.CREDIT_CARD_PATTERN.sub('[CARD_REMOVED]', text)
        
        # Replace IP addresses
        text = AnonymizationService.IP_PATTERN.sub('[IP_REMOVED]', text)
        
        return text
    
    @staticmethod
    def anonymize_contact_submission(contact, reason='GDPR deletion', keep_audit=True):
        """
        Anonymize a ContactSubmission instance
        
        Args:
            contact: ContactSubmission instance
            reason: Reason for anonymization
            keep_audit: Whether to keep audit trail
        
        Returns:
            Anonymized contact instance
        """
        from apps.contacts.models import ContactSubmission
        
        # Anonymize fields
        contact.email = AnonymizationService.anonymize_email(contact.email, method='hash')
        contact.name = AnonymizationService.anonymize_name(contact.name, method='replace')
        contact.phone = AnonymizationService.anonymize_phone(contact.phone, method='remove')
        contact.message = AnonymizationService.remove_pii_from_text(contact.message)
        contact.message = "[Data anonymized per GDPR request]" if not contact.message else contact.message
        
        # Anonymize IP if exists
        if contact.ip_address:
            contact.ip_address = AnonymizationService.anonymize_ip(str(contact.ip_address), method='truncate')
        
        contact.save()
        
        # Log anonymization
        if keep_audit:
            AnonymizationAudit.log_anonymization(
                model_name='ContactSubmission',
                instance_id=str(contact.id),
                reason=reason,
                fields_anonymized=['email', 'name', 'phone', 'message', 'ip_address']
            )
        
        return contact
    
    @staticmethod
    def anonymize_waitlist_entry(entry, reason='GDPR deletion', keep_audit=True):
        """
        Anonymize a WaitlistEntry instance
        """
        from apps.waitlist.models import WaitlistEntry
        
        entry.email = AnonymizationService.anonymize_email(entry.email, method='hash')
        entry.name = AnonymizationService.anonymize_name(entry.name, method='replace') if entry.name else None
        
        entry.save()
        
        if keep_audit:
            AnonymizationAudit.log_anonymization(
                model_name='WaitlistEntry',
                instance_id=str(entry.id),
                reason=reason,
                fields_anonymized=['email', 'name']
            )
        
        return entry
    
    @staticmethod
    def anonymize_lead(lead, reason='GDPR deletion', keep_audit=True):
        """
        Anonymize a Lead instance
        """
        from apps.leads.models import Lead
        
        lead.email = AnonymizationService.anonymize_email(lead.email, method='hash')
        lead.first_name = AnonymizationService.anonymize_name(lead.first_name, method='replace') if lead.first_name else None
        lead.last_name = AnonymizationService.anonymize_name(lead.last_name, method='replace') if lead.last_name else None
        lead.phone = AnonymizationService.anonymize_phone(lead.phone, method='remove') if lead.phone else None
        
        lead.save()
        
        if keep_audit:
            AnonymizationAudit.log_anonymization(
                model_name='Lead',
                instance_id=str(lead.id),
                reason=reason,
                fields_anonymized=['email', 'first_name', 'last_name', 'phone']
            )
        
        return lead
    
    @staticmethod
    def anonymize_newsletter_subscription(subscription, reason='GDPR deletion', keep_audit=True):
        """
        Anonymize a NewsletterSubscription instance
        """
        from apps.newsletter.models import NewsletterSubscription
        
        subscription.email = AnonymizationService.anonymize_email(subscription.email, method='hash')
        subscription.name = AnonymizationService.anonymize_name(subscription.name, method='replace') if subscription.name else None
        
        subscription.save()
        
        if keep_audit:
            AnonymizationAudit.log_anonymization(
                model_name='NewsletterSubscription',
                instance_id=str(subscription.id),
                reason=reason,
                fields_anonymized=['email', 'name']
            )
        
        return subscription
    
    @staticmethod
    def anonymize_by_email(email, reason='GDPR deletion', keep_audit=True):
        """
        Anonymize all records associated with an email address
        
        Args:
            email: Email address to anonymize
            reason: Reason for anonymization
            keep_audit: Whether to keep audit trail
        
        Returns:
            Dict with anonymization summary
        """
        email_lower = email.lower().strip()
        summary = {
            'email': email_lower,
            'anonymized_at': timezone.now().isoformat(),
            'reason': reason,
            'records_anonymized': {}
        }
        
        # Anonymize contact submissions
        try:
            from apps.contacts.models import ContactSubmission
            contacts = ContactSubmission.objects.filter(email__iexact=email_lower)
            count = contacts.count()
            for contact in contacts:
                AnonymizationService.anonymize_contact_submission(contact, reason, keep_audit)
            summary['records_anonymized']['contacts'] = count
        except Exception as e:
            logger.error(f"Error anonymizing contacts: {str(e)}")
            summary['records_anonymized']['contacts'] = 0
        
        # Anonymize waitlist entries
        try:
            from apps.waitlist.models import WaitlistEntry
            entries = WaitlistEntry.objects.filter(email__iexact=email_lower)
            count = entries.count()
            for entry in entries:
                AnonymizationService.anonymize_waitlist_entry(entry, reason, keep_audit)
            summary['records_anonymized']['waitlist'] = count
        except Exception as e:
            logger.error(f"Error anonymizing waitlist: {str(e)}")
            summary['records_anonymized']['waitlist'] = 0
        
        # Anonymize leads
        try:
            from apps.leads.models import Lead
            leads = Lead.objects.filter(email__iexact=email_lower)
            count = leads.count()
            for lead in leads:
                AnonymizationService.anonymize_lead(lead, reason, keep_audit)
            summary['records_anonymized']['leads'] = count
        except Exception as e:
            logger.error(f"Error anonymizing leads: {str(e)}")
            summary['records_anonymized']['leads'] = 0
        
        # Anonymize newsletter subscriptions
        try:
            from apps.newsletter.models import NewsletterSubscription
            subscriptions = NewsletterSubscription.objects.filter(email__iexact=email_lower)
            count = subscriptions.count()
            for subscription in subscriptions:
                AnonymizationService.anonymize_newsletter_subscription(subscription, reason, keep_audit)
            summary['records_anonymized']['newsletter'] = count
        except Exception as e:
            logger.error(f"Error anonymizing newsletter: {str(e)}")
            summary['records_anonymized']['newsletter'] = 0
        
        return summary


class AnonymizationAudit:
    """
    Audit trail for anonymization operations
    """
    
    @staticmethod
    def log_anonymization(model_name, instance_id, reason, fields_anonymized, 
                         anonymized_by=None, ip_address=None):
        """
        Log anonymization operation
        
        Args:
            model_name: Name of the model
            instance_id: ID of the anonymized instance
            reason: Reason for anonymization
            fields_anonymized: List of field names that were anonymized
            anonymized_by: Who initiated anonymization
            ip_address: IP address (will be hashed)
        """
        try:
            from apps.gdpr.models import DataDeletionAudit
            
            # Hash IP if provided
            ip_hash = None
            if ip_address:
                ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()
            
            # Create audit record
            audit = DataDeletionAudit.objects.create(
                email=f"anonymized_{instance_id}@audit.local",  # Placeholder
                deletion_type='anonymize',
                data_types_deleted=[model_name],
                deleted_by=anonymized_by or 'system',
                ip_address_hash=ip_hash,
                metadata={
                    'model_name': model_name,
                    'instance_id': instance_id,
                    'reason': reason,
                    'fields_anonymized': fields_anonymized,
                    'anonymization_timestamp': timezone.now().isoformat(),
                }
            )
            
            logger.info(f"Anonymization logged: {model_name} {instance_id} - {reason}")
            return audit
        except Exception as e:
            logger.error(f"Error logging anonymization: {str(e)}")
            return None
    
    @staticmethod
    def get_anonymization_history(model_name=None, instance_id=None):
        """
        Get anonymization history
        
        Args:
            model_name: Filter by model name
            instance_id: Filter by instance ID
        
        Returns:
            QuerySet of audit records
        """
        from apps.gdpr.models import DataDeletionAudit
        
        queryset = DataDeletionAudit.objects.filter(deletion_type='anonymize')
        
        if model_name:
            queryset = queryset.filter(metadata__model_name=model_name)
        
        if instance_id:
            queryset = queryset.filter(metadata__instance_id=instance_id)
        
        return queryset.order_by('-deletion_timestamp')


# Global service instance
anonymization_service = AnonymizationService()

