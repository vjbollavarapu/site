"""
Tests for ContactSubmission model
"""
from django.test import TestCase
from django.utils import timezone
from apps.contacts.models import ContactSubmission
from apps.contacts.tests.factories import ContactSubmissionFactory


class ContactSubmissionModelTest(TestCase):
    """Test ContactSubmission model"""
    
    def test_create_contact_submission(self):
        """Test creating a contact submission"""
        submission = ContactSubmissionFactory()
        self.assertIsNotNone(submission.id)
        self.assertEqual(submission.status, 'new')
        self.assertEqual(submission.priority, 'medium')
        self.assertFalse(submission.is_spam)
    
    def test_mark_as_contacted(self):
        """Test marking submission as contacted"""
        submission = ContactSubmissionFactory()
        submission.mark_as_contacted()
        
        self.assertEqual(submission.status, 'contacted')
        self.assertIsNotNone(submission.contacted_at)
    
    def test_mark_as_resolved(self):
        """Test marking submission as resolved"""
        submission = ContactSubmissionFactory()
        submission.mark_as_resolved()
        
        self.assertEqual(submission.status, 'resolved')
        self.assertIsNotNone(submission.resolved_at)
    
    def test_mark_as_spam(self):
        """Test marking submission as spam"""
        submission = ContactSubmissionFactory()
        submission.mark_as_spam()
        
        self.assertTrue(submission.is_spam)
        self.assertEqual(submission.status, 'archived')
    
    def test_string_representation(self):
        """Test string representation"""
        submission = ContactSubmissionFactory(name="John Doe", email="john@example.com")
        self.assertIn("John Doe", str(submission))
        self.assertIn("john@example.com", str(submission))
    
    def test_default_values(self):
        """Test default values"""
        submission = ContactSubmission.objects.create(
            name="Test User",
            email="test@example.com",
            subject="Test Subject",
            message="Test message"
        )
        self.assertEqual(submission.status, 'new')
        self.assertEqual(submission.priority, 'medium')
        self.assertFalse(submission.is_spam)
        self.assertEqual(submission.spam_score, 0.0)

