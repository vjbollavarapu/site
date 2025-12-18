"""
Tests for Anonymization Service
"""
from django.test import TestCase
from apps.integrations.anonymization_service import AnonymizationService
from apps.contacts.tests.factories import ContactSubmissionFactory


class AnonymizationServiceTest(TestCase):
    """Test Anonymization Service"""
    
    def test_anonymize_email_hash(self):
        """Test email anonymization with hash method"""
        original = 'user@example.com'
        anonymized = AnonymizationService.anonymize_email(original, method='hash')
        
        self.assertNotEqual(anonymized, original)
        self.assertIn('@anonymous.com', anonymized)
        self.assertIn('user_', anonymized)
    
    def test_anonymize_email_replace(self):
        """Test email anonymization with replace method"""
        original = 'user@example.com'
        anonymized = AnonymizationService.anonymize_email(original, method='replace')
        
        self.assertEqual(anonymized, 'user@anonymous.com')
    
    def test_anonymize_name_replace(self):
        """Test name anonymization"""
        original = 'John Doe'
        anonymized = AnonymizationService.anonymize_name(original, method='replace')
        
        self.assertEqual(anonymized, 'Anonymous User')
    
    def test_anonymize_phone_remove(self):
        """Test phone anonymization"""
        original = '+1234567890'
        anonymized = AnonymizationService.anonymize_phone(original, method='remove')
        
        self.assertEqual(anonymized, '')
    
    def test_anonymize_ip_truncate(self):
        """Test IP anonymization with truncate"""
        original = '192.168.1.100'
        anonymized = AnonymizationService.anonymize_ip(original, method='truncate')
        
        self.assertEqual(anonymized, '192.168.1.0')
    
    def test_remove_pii_from_text(self):
        """Test removing PII from text"""
        text = 'Contact me at user@example.com or call 123-456-7890'
        cleaned = AnonymizationService.remove_pii_from_text(text)
        
        self.assertNotIn('user@example.com', cleaned)
        self.assertNotIn('123-456-7890', cleaned)
        self.assertIn('[EMAIL_REMOVED]', cleaned)
        self.assertIn('[PHONE_REMOVED]', cleaned)
    
    def test_anonymize_contact_submission(self):
        """Test anonymizing contact submission"""
        contact = ContactSubmissionFactory()
        original_email = contact.email
        original_name = contact.name
        
        AnonymizationService.anonymize_contact_submission(contact, reason='Test')
        
        contact.refresh_from_db()
        self.assertNotEqual(contact.email, original_email)
        self.assertNotEqual(contact.name, original_name)
        self.assertIn('anonymous', contact.email.lower())

