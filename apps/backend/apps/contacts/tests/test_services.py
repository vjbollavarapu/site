"""
Tests for ContactSubmission services
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from apps.contacts.models import ContactSubmission
from apps.contacts.services import CheckSubmissionSpam
from apps.contacts.tests.factories import ContactSubmissionFactory


class SpamDetectionServiceTest(TestCase):
    """Test spam detection service"""
    
    def setUp(self):
        """Set up test request"""
        from django.test import RequestFactory
        self.factory = RequestFactory()
        self.request = self.factory.post('/api/contacts/submit/', {
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'Test message'
        })
        self.request.META['REMOTE_ADDR'] = '192.168.1.1'
    
    def test_check_honeypot_empty(self):
        """Test honeypot check with empty value"""
        data = {'name': 'Test', 'email': 'test@example.com', 'message': 'Test'}
        checker = CheckSubmissionSpam(data, self.request)
        is_spam = checker.check_honeypot('')
        self.assertFalse(is_spam)
    
    def test_check_honeypot_filled(self):
        """Test honeypot check with filled value (spam)"""
        data = {'name': 'Test', 'email': 'test@example.com', 'message': 'Test'}
        checker = CheckSubmissionSpam(data, self.request)
        is_spam = checker.check_honeypot('filled')
        self.assertTrue(is_spam)
    
    @patch('apps.contacts.services.verify_recaptcha')
    def test_check_recaptcha_valid(self, mock_verify):
        """Test reCAPTCHA check with valid token"""
        mock_verify.return_value = True
        data = {'name': 'Test', 'email': 'test@example.com', 'message': 'Test'}
        checker = CheckSubmissionSpam(data, self.request)
        is_valid = checker.check_recaptcha('valid_token')
        self.assertTrue(is_valid)
        mock_verify.assert_called_once()
    
    @patch('apps.contacts.services.verify_recaptcha')
    def test_check_recaptcha_invalid(self, mock_verify):
        """Test reCAPTCHA check with invalid token"""
        mock_verify.return_value = False
        data = {'name': 'Test', 'email': 'test@example.com', 'message': 'Test'}
        checker = CheckSubmissionSpam(data, self.request)
        is_valid = checker.check_recaptcha('invalid_token')
        self.assertFalse(is_valid)
    
    def test_check_content_spam_keywords(self):
        """Test content check with spam keywords"""
        data = {
            'name': 'Test',
            'email': 'test@example.com',
            'message': 'BUY NOW CLICK HERE FREE MONEY!!!'
        }
        checker = CheckSubmissionSpam(data, self.request)
        is_spam, score = checker.check_content()
        self.assertTrue(is_spam)
        self.assertGreater(score, 0.5)
    
    def test_check_content_too_many_links(self):
        """Test content check with too many links"""
        data = {
            'name': 'Test',
            'email': 'test@example.com',
            'message': 'Check this: http://link1.com and http://link2.com and http://link3.com and http://link4.com'
        }
        checker = CheckSubmissionSpam(data, self.request)
        is_spam, score = checker.check_content()
        self.assertTrue(is_spam)
    
    def test_check_content_all_caps(self):
        """Test content check with all caps"""
        data = {
            'name': 'Test',
            'email': 'test@example.com',
            'message': 'THIS IS ALL IN CAPS WHICH IS SUSPICIOUS BEHAVIOR FOR SPAM'
        }
        checker = CheckSubmissionSpam(data, self.request)
        is_spam, score = checker.check_content()
        self.assertTrue(is_spam)
        self.assertGreater(score, 0.5)
    
    def test_calculate_spam_score_low(self):
        """Test spam score calculation for legitimate submission"""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Hello, I am interested in your product. Can you provide more information?'
        }
        checker = CheckSubmissionSpam(data, self.request)
        is_spam, score, reasons, logs = checker.calculate_spam_score()
        self.assertFalse(is_spam)
        self.assertLess(score, 0.5)
    
    def test_calculate_spam_score_high(self):
        """Test spam score calculation for spam submission"""
        data = {
            'name': 'Spam Bot',
            'email': 'spam@spam.com',
            'message': 'BUY NOW CLICK HERE FREE MONEY!!! http://spam.com http://spam2.com http://spam3.com'
        }
        checker = CheckSubmissionSpam(data, self.request)
        is_spam, score, reasons, logs = checker.calculate_spam_score()
        self.assertTrue(is_spam)
        self.assertGreater(score, 0.7)

