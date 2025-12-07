"""
GDPR compliance services
"""
import hashlib
import json
import logging
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from django.conf import settings

from .models import Consent, PrivacyPolicy, DataRetentionPolicy, DataDeletionAudit
from apps.integrations.anonymization_service import AnonymizationService

logger = logging.getLogger(__name__)


class GDPRService:
    """
    Service for GDPR compliance operations
    """
    
    @staticmethod
    def hash_email(email):
        """Hash email for anonymization"""
        if not email:
            return None
        return hashlib.sha256(email.lower().strip().encode()).hexdigest()
    
    @staticmethod
    def anonymize_email(email):
        """Anonymize email address"""
        if not email:
            return None
        parts = email.split('@')
        if len(parts) == 2:
            # Keep first letter and domain, hash the rest
            local = parts[0]
            domain = parts[1]
            if len(local) > 1:
                anonymized_local = local[0] + '*' * (len(local) - 1)
            else:
                anonymized_local = '*'
            return f"{anonymized_local}@{domain}"
        return "***@***"
    
    @staticmethod
    def export_user_data(email):
        """
        Export all user data in JSON format
        Includes: contacts, waitlist, leads, newsletter, analytics, consent
        """
        email_lower = email.lower().strip()
        data = {
            'email': email_lower,
            'export_timestamp': timezone.now().isoformat(),
            'data': {}
        }
        
        # Contact submissions
        try:
            from apps.contacts.models import ContactSubmission
            contacts = ContactSubmission.objects.filter(email__iexact=email_lower)
            data['data']['contacts'] = [
                {
                    'id': str(c.id),
                    'name': c.name,
                    'email': c.email,
                    'phone': c.phone,
                    'company': c.company,
                    'subject': c.subject,
                    'message': c.message,
                    'status': c.status,
                    'created_at': c.created_at.isoformat(),
                    'consent_given': c.consent_given,
                    'consent_timestamp': c.consent_timestamp.isoformat() if c.consent_timestamp else None,
                }
                for c in contacts
            ]
        except Exception as e:
            logger.error(f"Error exporting contacts: {str(e)}")
            data['data']['contacts'] = []
        
        # Waitlist entries
        try:
            from apps.waitlist.models import WaitlistEntry
            waitlist = WaitlistEntry.objects.filter(email__iexact=email_lower)
            data['data']['waitlist'] = [
                {
                    'id': str(w.id),
                    'email': w.email,
                    'name': w.name,
                    'company': w.company,
                    'role': w.role,
                    'status': w.status,
                    'created_at': w.created_at.isoformat(),
                    'marketing_consent': w.marketing_consent,
                    'consent_timestamp': w.consent_timestamp.isoformat() if w.consent_timestamp else None,
                }
                for w in waitlist
            ]
        except Exception as e:
            logger.error(f"Error exporting waitlist: {str(e)}")
            data['data']['waitlist'] = []
        
        # Leads
        try:
            from apps.leads.models import Lead
            leads = Lead.objects.filter(email__iexact=email_lower)
            data['data']['leads'] = [
                {
                    'id': str(l.id),
                    'email': l.email,
                    'first_name': l.first_name,
                    'last_name': l.last_name,
                    'phone': l.phone,
                    'company': l.company,
                    'lead_source': l.lead_source,
                    'status': l.status,
                    'created_at': l.created_at.isoformat(),
                }
                for l in leads
            ]
        except Exception as e:
            logger.error(f"Error exporting leads: {str(e)}")
            data['data']['leads'] = []
        
        # Newsletter subscriptions
        try:
            from apps.newsletter.models import NewsletterSubscription
            newsletter = NewsletterSubscription.objects.filter(email__iexact=email_lower)
            data['data']['newsletter'] = [
                {
                    'id': str(n.id),
                    'email': n.email,
                    'name': n.name,
                    'subscription_status': n.subscription_status,
                    'subscribed_at': n.created_at.isoformat(),
                    'consent_given': n.consent_given,
                    'consent_timestamp': n.consent_timestamp.isoformat() if n.consent_timestamp else None,
                }
                for n in newsletter
            ]
        except Exception as e:
            logger.error(f"Error exporting newsletter: {str(e)}")
            data['data']['newsletter'] = []
        
        # Analytics (anonymized - only session-based data)
        try:
            from apps.analytics.models import PageView, Event, Conversion
            # Get sessions associated with this email (if tracked)
            # Note: Analytics data is typically session-based, not email-based
            # This is a simplified version
            data['data']['analytics'] = {
                'note': 'Analytics data is session-based and may not be directly linked to email',
                'page_views': 0,  # Would need to query by user_identifier hash
                'events': 0,
                'conversions': 0,
            }
        except Exception as e:
            logger.error(f"Error exporting analytics: {str(e)}")
            data['data']['analytics'] = {}
        
        # Consent records
        try:
            consents = Consent.objects.filter(email__iexact=email_lower)
            data['data']['consents'] = [
                {
                    'id': str(c.id),
                    'consent_type': c.consent_type,
                    'consent_given': c.consent_given,
                    'consent_timestamp': c.consent_timestamp.isoformat() if c.consent_timestamp else None,
                    'withdrawal_timestamp': c.withdrawal_timestamp.isoformat() if c.withdrawal_timestamp else None,
                    'privacy_policy_version': c.privacy_policy.version if c.privacy_policy else None,
                }
                for c in consents
            ]
        except Exception as e:
            logger.error(f"Error exporting consents: {str(e)}")
            data['data']['consents'] = []
        
        return data
    
    @staticmethod
    def delete_user_data(email, anonymize=False, keep_audit=True, deleted_by=None, ip_address=None):
        """
        Delete or anonymize all user data
        Returns dict with deletion summary
        """
        email_lower = email.lower().strip()
        deletion_summary = {
            'email': email_lower,
            'anonymized': anonymize,
            'timestamp': timezone.now().isoformat(),
            'deleted': {}
        }
        
        # Hash IP for audit
        ip_hash = None
        if ip_address:
            ip_hash = Consent.hash_ip_address(ip_address)
        
        # Contact submissions
        try:
            from apps.contacts.models import ContactSubmission
            contacts = ContactSubmission.objects.filter(email__iexact=email_lower)
            count = contacts.count()
            if anonymize:
                # Use anonymization service
                for contact in contacts:
                    AnonymizationService.anonymize_contact_submission(
                        contact,
                        reason='GDPR deletion request',
                        keep_audit=keep_audit
                    )
            else:
                contacts.delete()
            deletion_summary['deleted']['contacts'] = count
        except Exception as e:
            logger.error(f"Error deleting contacts: {str(e)}")
            deletion_summary['deleted']['contacts'] = 0
        
        # Waitlist entries
        try:
            from apps.waitlist.models import WaitlistEntry
            waitlist = WaitlistEntry.objects.filter(email__iexact=email_lower)
            count = waitlist.count()
            if anonymize:
                # Use anonymization service
                for entry in waitlist:
                    AnonymizationService.anonymize_waitlist_entry(
                        entry,
                        reason='GDPR deletion request',
                        keep_audit=keep_audit
                    )
            else:
                waitlist.delete()
            deletion_summary['deleted']['waitlist'] = count
        except Exception as e:
            logger.error(f"Error deleting waitlist: {str(e)}")
            deletion_summary['deleted']['waitlist'] = 0
        
        # Leads
        try:
            from apps.leads.models import Lead
            leads = Lead.objects.filter(email__iexact=email_lower)
            count = leads.count()
            if anonymize:
                # Use anonymization service
                for lead in leads:
                    AnonymizationService.anonymize_lead(
                        lead,
                        reason='GDPR deletion request',
                        keep_audit=keep_audit
                    )
            else:
                leads.delete()
            deletion_summary['deleted']['leads'] = count
        except Exception as e:
            logger.error(f"Error deleting leads: {str(e)}")
            deletion_summary['deleted']['leads'] = 0
        
        # Newsletter subscriptions
        try:
            from apps.newsletter.models import NewsletterSubscription
            newsletter = NewsletterSubscription.objects.filter(email__iexact=email_lower)
            count = newsletter.count()
            if anonymize:
                # Use anonymization service
                for subscription in newsletter:
                    AnonymizationService.anonymize_newsletter_subscription(
                        subscription,
                        reason='GDPR deletion request',
                        keep_audit=keep_audit
                    )
            else:
                newsletter.delete()
            deletion_summary['deleted']['newsletter'] = count
        except Exception as e:
            logger.error(f"Error deleting newsletter: {str(e)}")
            deletion_summary['deleted']['newsletter'] = 0
        
        # Consent records (keep for audit, but mark as withdrawn)
        try:
            consents = Consent.objects.filter(email__iexact=email_lower, consent_given=True)
            for consent in consents:
                consent.withdraw(reason="GDPR deletion request")
            deletion_summary['deleted']['consents_withdrawn'] = consents.count()
        except Exception as e:
            logger.error(f"Error withdrawing consents: {str(e)}")
            deletion_summary['deleted']['consents_withdrawn'] = 0
        
        # Create audit trail
        if keep_audit:
            try:
                import secrets
                DataDeletionAudit.objects.create(
                    email=email_lower,
                    deletion_type='anonymize' if anonymize else 'full',
                    data_types_deleted=list(deletion_summary['deleted'].keys()),
                    deleted_by=deleted_by,
                    ip_address_hash=ip_hash,
                    confirmation_token=secrets.token_urlsafe(32),
                )
            except Exception as e:
                logger.error(f"Error creating audit trail: {str(e)}")
        
        return deletion_summary
    
    @staticmethod
    def get_user_data(email):
        """
        Get all data associated with email (Right to Access)
        Similar to export but returns Python objects
        """
        return GDPRService.export_user_data(email)
    
    @staticmethod
    def apply_retention_policies():
        """
        Apply data retention policies
        Auto-delete or anonymize old data based on policies
        """
        policies = DataRetentionPolicy.objects.filter(is_active=True)
        summary = {}
        
        for policy in policies:
            cutoff_date = timezone.now() - timedelta(days=policy.retention_days)
            
            if policy.data_type == 'contact':
                from apps.contacts.models import ContactSubmission
                queryset = ContactSubmission.objects.filter(created_at__lt=cutoff_date)
                count = queryset.count()
                if policy.anonymize_instead:
                    # Use anonymization service
                    for contact in queryset:
                        AnonymizationService.anonymize_contact_submission(
                            contact,
                            reason='Retention policy',
                            keep_audit=True
                        )
                elif policy.auto_delete:
                    queryset.delete()
                summary[policy.data_type] = count
            
            elif policy.data_type == 'waitlist':
                from apps.waitlist.models import WaitlistEntry
                queryset = WaitlistEntry.objects.filter(created_at__lt=cutoff_date)
                count = queryset.count()
                if policy.anonymize_instead:
                    # Use anonymization service
                    for entry in queryset:
                        AnonymizationService.anonymize_waitlist_entry(
                            entry,
                            reason='Retention policy',
                            keep_audit=True
                        )
                elif policy.auto_delete:
                    queryset.delete()
                summary[policy.data_type] = count
            
            elif policy.data_type == 'lead':
                from apps.leads.models import Lead
                queryset = Lead.objects.filter(created_at__lt=cutoff_date)
                count = queryset.count()
                if policy.anonymize_instead:
                    # Use anonymization service
                    for lead in queryset:
                        AnonymizationService.anonymize_lead(
                            lead,
                            reason='Retention policy',
                            keep_audit=True
                        )
                elif policy.auto_delete:
                    queryset.delete()
                summary[policy.data_type] = count
            
            elif policy.data_type == 'analytics_pageview':
                from apps.analytics.models import PageView
                queryset = PageView.objects.filter(timestamp__lt=cutoff_date)
                count = queryset.count()
                if policy.auto_delete:
                    queryset.delete()
                summary[policy.data_type] = count
            
            elif policy.data_type == 'analytics_event':
                from apps.analytics.models import Event
                queryset = Event.objects.filter(timestamp__lt=cutoff_date)
                count = queryset.count()
                if policy.auto_delete:
                    queryset.delete()
                summary[policy.data_type] = count
        
        logger.info(f"Applied retention policies: {summary}")
        return summary

