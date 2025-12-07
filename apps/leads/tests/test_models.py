"""
Tests for Lead model
"""
from django.test import TestCase
from apps.leads.models import Lead
from apps.leads.tests.factories import LeadFactory


class LeadModelTest(TestCase):
    """Test Lead model"""
    
    def test_create_lead(self):
        """Test creating a lead"""
        lead = LeadFactory()
        self.assertIsNotNone(lead.id)
        self.assertEqual(lead.status, 'new')
        self.assertEqual(lead.lead_score, 50)
    
    def test_qualify_lead(self):
        """Test qualifying a lead"""
        lead = LeadFactory()
        lead.qualify()
        
        self.assertEqual(lead.status, 'qualified')
        self.assertEqual(lead.lifecycle_stage, 'sales_qualified')
    
    def test_convert_lead(self):
        """Test converting a lead"""
        lead = LeadFactory(status='qualified')
        lead.convert()
        
        self.assertEqual(lead.status, 'converted')
        self.assertEqual(lead.lifecycle_stage, 'customer')
        self.assertIsNotNone(lead.converted_at)
    
    def test_calculate_lead_score(self):
        """Test lead score calculation"""
        lead = LeadFactory(
            company='Large Corp',
            lead_source='referral'
        )
        score = lead.calculate_lead_score()
        
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        self.assertEqual(lead.lead_score, score)
    
    def test_update_engagement(self):
        """Test updating engagement"""
        lead = LeadFactory()
        initial_engagement = lead.engagement_score or 0
        
        lead.update_engagement('page_view')
        lead.refresh_from_db()
        
        # Engagement should increase
        self.assertGreaterEqual(lead.engagement_score or 0, initial_engagement)

