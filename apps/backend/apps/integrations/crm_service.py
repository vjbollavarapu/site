"""
CRM integration service supporting multiple providers
"""
from abc import ABC, abstractmethod
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class CRMProvider(ABC):
    """
    Abstract base class for CRM providers
    """
    
    @abstractmethod
    def create_contact(self, contact_data):
        """Create a new contact in CRM"""
        pass
    
    @abstractmethod
    def update_contact(self, contact_id, contact_data):
        """Update existing contact in CRM"""
        pass
    
    @abstractmethod
    def create_lead(self, lead_data):
        """Create a new lead in CRM"""
        pass
    
    @abstractmethod
    def create_deal(self, deal_data):
        """Create a new deal/opportunity in CRM"""
        pass
    
    @abstractmethod
    def create_note(self, entity_id, note_content):
        """Create a note/activity for an entity"""
        pass
    
    @abstractmethod
    def search_contact(self, email):
        """Search for contact by email"""
        pass


class HubSpotCRMProvider(CRMProvider):
    """
    HubSpot CRM integration using enhanced HubSpot service
    """
    
    def __init__(self):
        from .hubspot_service import hubspot_service
        self.service = hubspot_service
    
    def create_contact(self, contact_data):
        """Create contact in HubSpot"""
        return self.service.create_contact(contact_data)
    
    def update_contact(self, contact_id, contact_data):
        """Update contact in HubSpot"""
        return self.service.update_contact(contact_id, contact_data)
    
    def create_lead(self, lead_data):
        """Create lead in HubSpot (as contact with lead status)"""
        # Add lead status property
        lead_data_with_status = lead_data.copy()
        lead_data_with_status['hs_lead_status'] = 'NEW'
        return self.service.create_contact(lead_data_with_status)
    
    def create_deal(self, deal_data):
        """Create deal in HubSpot"""
        associated_contact_id = deal_data.pop('associated_contact_id', None)
        return self.service.create_deal(deal_data, associated_contact_id)
    
    def create_note(self, entity_id, note_content):
        """Create timeline note in HubSpot"""
        return self.service.add_timeline_note(entity_id, note_content)
    
    def search_contact(self, email):
        """Search contact by email in HubSpot"""
        result = self.service.search_contact_by_email(email)
        return [result] if result else []


class SalesforceCRMProvider(CRMProvider):
    """
    Salesforce CRM integration
    """
    
    def __init__(self):
        self.username = getattr(settings, 'SALESFORCE_USERNAME', '')
        self.password = getattr(settings, 'SALESFORCE_PASSWORD', '')
        self.security_token = getattr(settings, 'SALESFORCE_SECURITY_TOKEN', '')
        self.sandbox = getattr(settings, 'SALESFORCE_SANDBOX', False)
        if not all([self.username, self.password]):
            logger.warning("Salesforce credentials not configured")
    
    def _get_connection(self):
        """Get Salesforce connection"""
        try:
            from simple_salesforce import Salesforce
            return Salesforce(
                username=self.username,
                password=self.password,
                security_token=self.security_token,
                sandbox=self.sandbox
            )
        except Exception as e:
            logger.error(f"Salesforce connection error: {str(e)}")
            return None
    
    def create_contact(self, contact_data):
        """Create contact in Salesforce"""
        try:
            sf = self._get_connection()
            if not sf:
                return None
            
            contact = {
                'FirstName': contact_data.get('first_name', ''),
                'LastName': contact_data.get('last_name', ''),
                'Email': contact_data.get('email', ''),
                'Phone': contact_data.get('phone', ''),
                'Company__c': contact_data.get('company', ''),
            }
            
            result = sf.Contact.create(contact)
            return result
        except Exception as e:
            logger.error(f"Salesforce create_contact error: {str(e)}")
            return None
    
    def update_contact(self, contact_id, contact_data):
        """Update contact in Salesforce"""
        try:
            sf = self._get_connection()
            if not sf:
                return None
            
            contact = {
                'FirstName': contact_data.get('first_name', ''),
                'LastName': contact_data.get('last_name', ''),
                'Email': contact_data.get('email', ''),
            }
            
            result = sf.Contact.update(contact_id, contact)
            return result
        except Exception as e:
            logger.error(f"Salesforce update_contact error: {str(e)}")
            return None
    
    def create_lead(self, lead_data):
        """Create lead in Salesforce"""
        try:
            sf = self._get_connection()
            if not sf:
                return None
            
            lead = {
                'FirstName': lead_data.get('first_name', ''),
                'LastName': lead_data.get('last_name', ''),
                'Email': lead_data.get('email', ''),
                'Company': lead_data.get('company', ''),
                'Status': 'Open - Not Contacted',
            }
            
            result = sf.Lead.create(lead)
            return result
        except Exception as e:
            logger.error(f"Salesforce create_lead error: {str(e)}")
            return None
    
    def create_deal(self, deal_data):
        """Create opportunity in Salesforce"""
        try:
            sf = self._get_connection()
            if not sf:
                return None
            
            opportunity = {
                'Name': deal_data.get('name', ''),
                'Amount': deal_data.get('value', ''),
                'StageName': 'Prospecting',
                'CloseDate': deal_data.get('close_date', ''),
            }
            
            result = sf.Opportunity.create(opportunity)
            return result
        except Exception as e:
            logger.error(f"Salesforce create_deal error: {str(e)}")
            return None
    
    def create_note(self, entity_id, note_content):
        """Create note in Salesforce"""
        try:
            sf = self._get_connection()
            if not sf:
                return None
            
            note = {
                'Body': note_content,
                'ParentId': entity_id,
            }
            
            result = sf.Note.create(note)
            return result
        except Exception as e:
            logger.error(f"Salesforce create_note error: {str(e)}")
            return None
    
    def search_contact(self, email):
        """Search contact by email in Salesforce"""
        try:
            sf = self._get_connection()
            if not sf:
                return []
            
            query = f"SELECT Id, Name, Email FROM Contact WHERE Email = '{email}'"
            result = sf.query(query)
            return result.get('records', [])
        except Exception as e:
            logger.error(f"Salesforce search_contact error: {str(e)}")
            return []


class PipedriveCRMProvider(CRMProvider):
    """
    Pipedrive CRM integration
    """
    
    def __init__(self):
        self.api_token = getattr(settings, 'PIPEDRIVE_API_TOKEN', '')
        self.base_url = getattr(settings, 'PIPEDRIVE_BASE_URL', 'https://api.pipedrive.com/v1')
        if not self.api_token:
            logger.warning("Pipedrive API token not configured")
    
    def _make_request(self, method, endpoint, data=None):
        """Make API request to Pipedrive"""
        try:
            import requests
            url = f"{self.base_url}/{endpoint}"
            params = {'api_token': self.api_token}
            
            if method == 'GET':
                response = requests.get(url, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, params=params, json=data, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, params=params, json=data, timeout=10)
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Pipedrive API error: {str(e)}")
            return None
    
    def create_contact(self, contact_data):
        """Create person in Pipedrive"""
        data = {
            'name': f"{contact_data.get('first_name', '')} {contact_data.get('last_name', '')}".strip(),
            'email': [{'value': contact_data.get('email', ''), 'primary': True}],
            'phone': [{'value': contact_data.get('phone', ''), 'primary': True}] if contact_data.get('phone') else [],
        }
        return self._make_request('POST', 'persons', data)
    
    def update_contact(self, contact_id, contact_data):
        """Update person in Pipedrive"""
        data = {
            'name': f"{contact_data.get('first_name', '')} {contact_data.get('last_name', '')}".strip(),
            'email': [{'value': contact_data.get('email', ''), 'primary': True}],
        }
        return self._make_request('PUT', f'persons/{contact_id}', data)
    
    def create_lead(self, lead_data):
        """Create person as lead in Pipedrive"""
        return self.create_contact(lead_data)
    
    def create_deal(self, deal_data):
        """Create deal in Pipedrive"""
        data = {
            'title': deal_data.get('name', ''),
            'value': deal_data.get('value', ''),
            'currency': deal_data.get('currency', 'USD'),
            'stage_id': deal_data.get('stage_id', 1),
        }
        return self._make_request('POST', 'deals', data)
    
    def create_note(self, entity_id, note_content):
        """Create note in Pipedrive"""
        data = {
            'content': note_content,
            'deal_id': entity_id,  # Assuming deal, can be person_id or org_id
        }
        return self._make_request('POST', 'notes', data)
    
    def search_contact(self, email):
        """Search person by email in Pipedrive"""
        result = self._make_request('GET', f'persons/search', {'term': email})
        if result and result.get('data'):
            return result['data'].get('items', [])
        return []


class CRMService:
    """
    Unified CRM service that routes to the configured provider
    """
    
    def __init__(self):
        self.provider_name = getattr(settings, 'CRM_PROVIDER', '').lower()
        self.provider = self._get_provider()
        self.field_mapping = getattr(settings, 'CRM_FIELD_MAPPING', {})
    
    def _get_provider(self):
        """Get the configured CRM provider instance"""
        if self.provider_name == 'hubspot':
            return HubSpotCRMProvider()
        elif self.provider_name == 'salesforce':
            return SalesforceCRMProvider()
        elif self.provider_name == 'pipedrive':
            return PipedriveCRMProvider()
        else:
            logger.warning(f"Unknown CRM provider: {self.provider_name}")
            return None
    
    def _map_fields(self, data):
        """Map fields according to configuration"""
        if not self.field_mapping:
            return data
        
        mapped_data = {}
        for key, value in data.items():
            mapped_key = self.field_mapping.get(key, key)
            mapped_data[mapped_key] = value
        
        return mapped_data
    
    def sync_contact_submission(self, contact_submission, immediate=True):
        """
        Auto-sync contact submission to CRM
        immediate: If True, sync immediately; if False, queue for batch sync
        """
        if not self.provider:
            return False
        
        if not immediate:
            # Queue for batch sync via Celery
            try:
                from .tasks import sync_to_crm_task
                sync_to_crm_task.delay('contact', str(contact_submission.id))
                return True
            except Exception as e:
                logger.error(f"Failed to queue CRM sync: {str(e)}")
                # Fall back to immediate sync
                immediate = True
        
        if immediate:
            try:
                contact_data = {
                    'name': contact_submission.name,
                    'email': contact_submission.email,
                    'phone': contact_submission.phone or '',
                    'company': contact_submission.company or '',
                }
                
                mapped_data = self._map_fields(contact_data)
                result = self.provider.create_contact(mapped_data)
                
                if result:
                    # Extract contact ID
                    if isinstance(result, dict):
                        contact_id = result.get('id')
                    else:
                        contact_id = result
                    
                    if contact_id:
                        # Create note with message
                        note = f"Subject: {contact_submission.subject}\n\n{contact_submission.message}"
                        self.provider.create_note(contact_id, note)
                        
                        # Tag contact based on source
                        if self.provider_name == 'hubspot' and contact_submission.source:
                            from .hubspot_service import hubspot_service
                            source_tag = f"source_{contact_submission.source.replace(' ', '_').lower()}"
                            hubspot_service.tag_contact(contact_id, [source_tag])
                    
                    logger.info(f"Contact synced to CRM: {contact_submission.email}")
                    return True
            except Exception as e:
                logger.error(f"CRM sync error for contact: {str(e)}")
        return False
    
    def sync_waitlist_entry(self, waitlist_entry, immediate=True):
        """
        Auto-sync waitlist entry to CRM
        immediate: If True, sync immediately; if False, queue for batch sync
        """
        if not self.provider:
            return False
        
        if not immediate:
            # Queue for batch sync via Celery
            try:
                from .tasks import sync_to_crm_task
                sync_to_crm_task.delay('waitlist', str(waitlist_entry.id))
                return True
            except Exception as e:
                logger.error(f"Failed to queue CRM sync: {str(e)}")
                immediate = True
        
        if immediate:
            try:
                lead_data = {
                    'name': waitlist_entry.name or '',
                    'email': waitlist_entry.email,
                    'company': waitlist_entry.company or '',
                }
                
                mapped_data = self._map_fields(lead_data)
                result = self.provider.create_lead(mapped_data)
                
                if result:
                    # Extract contact ID
                    if isinstance(result, dict):
                        contact_id = result.get('id')
                    else:
                        contact_id = result
                    
                    # Tag based on source
                    if self.provider_name == 'hubspot' and waitlist_entry.source:
                        from .hubspot_service import hubspot_service
                        source_tag = f"source_{waitlist_entry.source.replace(' ', '_').lower()}"
                        hubspot_service.tag_contact(contact_id, [source_tag])
                    
                    logger.info(f"Waitlist entry synced to CRM: {waitlist_entry.email}")
                    return True
            except Exception as e:
                logger.error(f"CRM sync error for waitlist: {str(e)}")
        return False
    
    def sync_lead(self, lead, immediate=True):
        """
        Auto-sync lead to CRM
        immediate: If True, sync immediately; if False, queue for batch sync
        """
        if not self.provider:
            return False
        
        if not immediate:
            # Queue for batch sync via Celery
            try:
                from .tasks import sync_to_crm_task
                sync_to_crm_task.delay('lead', str(lead.id))
                return True
            except Exception as e:
                logger.error(f"Failed to queue CRM sync: {str(e)}")
                immediate = True
        
        if immediate:
            try:
                lead_data = {
                    'first_name': lead.first_name,
                    'last_name': lead.last_name,
                    'email': lead.email,
                    'phone': lead.phone or '',
                    'company': lead.company or '',
                }
                
                mapped_data = self._map_fields(lead_data)
                result = self.provider.create_lead(mapped_data)
                
                if result:
                    # Extract contact ID
                    if isinstance(result, dict):
                        contact_id = result.get('id')
                    else:
                        contact_id = result
                    
                    # Create deal for qualified leads
                    if lead.status == 'qualified' and self.provider_name == 'hubspot':
                        from .hubspot_service import hubspot_service
                        deal_data = {
                            'name': f"Deal for {lead.first_name} {lead.last_name}",
                            'value': None,  # Can be set if available
                            'stage': 'qualifiedtobuy',
                        }
                        hubspot_service.create_deal(deal_data, associated_contact_id=contact_id)
                    
                    # Tag based on source
                    if self.provider_name == 'hubspot' and lead.lead_source:
                        from .hubspot_service import hubspot_service
                        source_tag = f"source_{lead.lead_source.replace(' ', '_').lower()}"
                        hubspot_service.tag_contact(contact_id, [source_tag])
                    
                    logger.info(f"Lead synced to CRM: {lead.email}")
                    return True
            except Exception as e:
                logger.error(f"CRM sync error for lead: {str(e)}")
        return False
    
    def sync_status_change(self, entity_type, entity_id, new_status, immediate=True):
        """
        Sync status change to CRM
        Creates timeline note and updates properties if needed
        """
        if not self.provider:
            return False
        
        try:
            note = f"Status changed to: {new_status}"
            result = self.provider.create_note(entity_id, note)
            
            # For qualified leads, create deal in HubSpot
            if new_status == 'qualified' and entity_type == 'lead' and self.provider_name == 'hubspot':
                from .hubspot_service import hubspot_service
                # Get lead data (would need to fetch from database)
                # This is a simplified version
                deal_data = {
                    'name': f"Qualified Lead Deal",
                    'stage': 'qualifiedtobuy',
                }
                hubspot_service.create_deal(deal_data, associated_contact_id=entity_id)
            
            logger.info(f"Status change synced to CRM: {entity_type} {entity_id}")
            return True
        except Exception as e:
            logger.error(f"CRM sync error for status change: {str(e)}")
        return False


# Global CRM service instance
crm_service = CRMService()

