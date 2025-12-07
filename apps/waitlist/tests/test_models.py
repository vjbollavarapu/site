"""
Tests for WaitlistEntry model
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from apps.waitlist.models import WaitlistEntry
from apps.waitlist.tests.factories import WaitlistEntryFactory


class WaitlistEntryModelTest(TestCase):
    """Test WaitlistEntry model"""
    
    def test_create_waitlist_entry(self):
        """Test creating a waitlist entry"""
        entry = WaitlistEntryFactory()
        self.assertIsNotNone(entry.id)
        self.assertEqual(entry.status, 'pending')
        self.assertFalse(entry.is_verified)
    
    def test_approve_entry(self):
        """Test approving waitlist entry"""
        entry = WaitlistEntryFactory()
        entry.approve()
        
        self.assertEqual(entry.status, 'approved')
    
    def test_send_invitation(self):
        """Test sending invitation"""
        from unittest.mock import patch, MagicMock
        entry = WaitlistEntryFactory(status='approved')
        from django.contrib.auth.models import User
        user = User.objects.create_user('testuser', 'test@example.com', 'pass')
        
        with patch('apps.waitlist.models.email_service') as mock_email:
            mock_email.send_waitlist_invitation = MagicMock()
            entry.send_invitation(user=user)
            
            self.assertEqual(entry.status, 'invited')
            self.assertIsNotNone(entry.invited_at)
            self.assertIsNotNone(entry.invite_code)
            mock_email.send_waitlist_invitation.assert_called_once()
    
    def test_mark_onboarded(self):
        """Test marking entry as onboarded"""
        entry = WaitlistEntryFactory(status='invited')
        entry.mark_onboarded()
        
        self.assertEqual(entry.status, 'onboarded')
    
    def test_calculate_priority_score(self):
        """Test priority score calculation"""
        entry = WaitlistEntryFactory(
            company_size='201-1000',
            industry='technology'
        )
        entry.calculate_priority_score()
        
        self.assertGreater(entry.priority_score, 0)
    
    def test_unique_email_constraint(self):
        """Test unique email constraint"""
        WaitlistEntryFactory(email='test@example.com')
        
        with self.assertRaises(Exception):  # IntegrityError or ValidationError
            WaitlistEntryFactory(email='test@example.com')

