"""
Tests for ContactSubmission serializers
"""
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from apps.contacts.serializers import (
    ContactSubmissionCreateSerializer,
    ContactSubmissionSerializer,
    ContactSubmissionUpdateSerializer
)
from apps.contacts.tests.factories import ContactSubmissionFactory


class ContactSubmissionSerializerTest(TestCase):
    """Test ContactSubmission serializers"""
    
    def test_create_serializer_valid(self):
        """Test valid data for create serializer"""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message',
            'phone': '+1234567890',
            'company': 'Test Company'
        }
        serializer = ContactSubmissionCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_create_serializer_missing_required_fields(self):
        """Test serializer with missing required fields"""
        data = {
            'name': 'John Doe',
            # Missing email, subject, message
        }
        serializer = ContactSubmissionCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        self.assertIn('subject', serializer.errors)
        self.assertIn('message', serializer.errors)
    
    def test_create_serializer_invalid_email(self):
        """Test serializer with invalid email"""
        data = {
            'name': 'John Doe',
            'email': 'invalid-email',
            'subject': 'Test Subject',
            'message': 'Test message'
        }
        serializer = ContactSubmissionCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_create_serializer_message_too_short(self):
        """Test serializer with message too short"""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'Hi'  # Too short
        }
        serializer = ContactSubmissionCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('message', serializer.errors)
    
    def test_create_serializer_message_too_long(self):
        """Test serializer with message too long"""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'x' * 10001  # Too long
        }
        serializer = ContactSubmissionCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('message', serializer.errors)
    
    def test_serializer_output(self):
        """Test serializer output"""
        submission = ContactSubmissionFactory()
        serializer = ContactSubmissionSerializer(submission)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('name', data)
        self.assertIn('email', data)
        self.assertIn('status', data)
        self.assertIn('created_at', data)
    
    def test_update_serializer(self):
        """Test update serializer"""
        submission = ContactSubmissionFactory(status='new')
        data = {
            'status': 'contacted',
            'priority': 'high'
        }
        serializer = ContactSubmissionUpdateSerializer(submission, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated = serializer.save()
        self.assertEqual(updated.status, 'contacted')
        self.assertEqual(updated.priority, 'high')

