"""
Tests for GDPR models
"""
from django.test import TestCase
from apps.gdpr.models import Consent, PrivacyPolicy, DataRetentionPolicy
from apps.gdpr.tests.factories import ConsentFactory, PrivacyPolicyFactory, DataRetentionPolicyFactory


class ConsentModelTest(TestCase):
    """Test Consent model"""
    
    def test_create_consent(self):
        """Test creating consent"""
        consent = ConsentFactory()
        self.assertIsNotNone(consent.id)
        self.assertTrue(consent.consent_given)
    
    def test_withdraw_consent(self):
        """Test withdrawing consent"""
        consent = ConsentFactory()
        consent.withdraw(reason='No longer interested')
        
        self.assertFalse(consent.consent_given)
        self.assertIsNotNone(consent.withdrawal_timestamp)
        self.assertEqual(consent.withdrawal_reason, 'No longer interested')
    
    def test_hash_ip_address(self):
        """Test IP address hashing"""
        hashed = Consent.hash_ip_address('192.168.1.1')
        self.assertIsNotNone(hashed)
        self.assertEqual(len(hashed), 64)


class PrivacyPolicyModelTest(TestCase):
    """Test PrivacyPolicy model"""
    
    def test_create_privacy_policy(self):
        """Test creating privacy policy"""
        policy = PrivacyPolicyFactory()
        self.assertIsNotNone(policy.id)
        self.assertTrue(policy.is_active)
    
    def test_activate_policy_deactivates_others(self):
        """Test activating policy deactivates others"""
        policy1 = PrivacyPolicyFactory(is_active=True)
        policy2 = PrivacyPolicyFactory(is_active=False)
        
        policy2.is_active = True
        policy2.save()
        
        policy1.refresh_from_db()
        self.assertFalse(policy1.is_active)
        self.assertTrue(policy2.is_active)


class DataRetentionPolicyModelTest(TestCase):
    """Test DataRetentionPolicy model"""
    
    def test_create_retention_policy(self):
        """Test creating retention policy"""
        policy = DataRetentionPolicyFactory()
        self.assertIsNotNone(policy.id)
        self.assertEqual(policy.retention_days, 365)
        self.assertTrue(policy.anonymize_instead)

