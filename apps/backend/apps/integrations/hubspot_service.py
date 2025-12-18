"""
Enhanced HubSpot integration service
"""
import time
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Try to import HubSpot client
try:
    from hubspot import HubSpot
    from hubspot.crm.contacts import ApiException as ContactsApiException
    from hubspot.crm.deals import ApiException as DealsApiException
    try:
        from hubspot.crm.timeline import ApiException as TimelineApiException
    except ImportError:
        # Timeline API might not be available in all versions
        TimelineApiException = Exception
    HUBSPOT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"HubSpot API client not available: {str(e)}")
    HubSpot = None
    ContactsApiException = Exception
    DealsApiException = Exception
    TimelineApiException = Exception
    HUBSPOT_AVAILABLE = False


class HubSpotService:
    """
    Enhanced HubSpot integration with rate limiting, batching, and retry logic
    """
    
    def __init__(self):
        if not HUBSPOT_AVAILABLE:
            logger.warning("HubSpot API client not installed")
            self.client = None
            return
        
        self.api_key = getattr(settings, 'HUBSPOT_API_KEY', '') or getattr(settings, 'HUBSPOT_ACCESS_TOKEN', '')
        self.portal_id = getattr(settings, 'HUBSPOT_PORTAL_ID', '')
        self.field_mapping = getattr(settings, 'HUBSPOT_FIELD_MAPPING', {})
        
        if not self.api_key:
            logger.warning("HubSpot API key not configured")
            self.client = None
        else:
            try:
                self.client = HubSpot(access_token=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize HubSpot client: {str(e)}")
                self.client = None
        
        # Rate limit handling
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests (10 requests/second)
        self.batch_size = 100
    
    def _handle_rate_limit(self):
        """Handle rate limiting by adding delays between requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _map_fields(self, data, field_type='contact'):
        """
        Map fields according to configuration
        field_type: 'contact', 'deal', 'note'
        """
        if not self.field_mapping:
            return data
        
        mapping_key = f"{field_type}_mapping"
        mapping = self.field_mapping.get(mapping_key, {})
        
        mapped_data = {}
        for key, value in data.items():
            mapped_key = mapping.get(key, key)
            mapped_data[mapped_key] = value
        
        return mapped_data
    
    def _split_name(self, name):
        """Split full name into first_name and last_name"""
        if not name:
            return '', ''
        
        parts = name.strip().split()
        if len(parts) == 1:
            return parts[0], ''
        elif len(parts) >= 2:
            return parts[0], ' '.join(parts[1:])
        return '', ''
    
    def create_contact(self, contact_data, retry_count=3):
        """
        Create contact in HubSpot with retry logic
        Maps name → first_name/last_name
        """
        if not self.client:
            return None
        
        self._handle_rate_limit()
        
        try:
            # Split name into first_name and last_name
            name = contact_data.get('name', '') or f"{contact_data.get('first_name', '')} {contact_data.get('last_name', '')}".strip()
            if name and not contact_data.get('first_name'):
                first_name, last_name = self._split_name(name)
                contact_data['first_name'] = first_name
                contact_data['last_name'] = last_name
            
            # Map fields
            properties = {
                'email': contact_data.get('email', ''),
                'firstname': contact_data.get('first_name', ''),
                'lastname': contact_data.get('last_name', ''),
                'phone': contact_data.get('phone', ''),
                'company': contact_data.get('company', ''),
            }
            
            # Apply custom field mapping
            mapped_properties = self._map_fields(properties, 'contact')
            
            # Remove empty values
            properties = {k: v for k, v in mapped_properties.items() if v}
            
            # Create contact
            api_response = self.client.crm.contacts.basic_api.create(
                simple_public_object_input={'properties': properties}
            )
            
            logger.info(f"HubSpot contact created: {api_response.id}")
            return {'id': api_response.id, 'properties': api_response.properties}
        
        except ContactsApiException as e:
            if e.status == 409:  # Contact already exists
                # Try to find existing contact
                return self.search_contact_by_email(contact_data.get('email', ''))
            elif retry_count > 0:
                logger.warning(f"HubSpot API error, retrying: {str(e)}")
                time.sleep(1)
                return self.create_contact(contact_data, retry_count - 1)
            else:
                logger.error(f"HubSpot create_contact error: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"HubSpot create_contact error: {str(e)}")
            return None
    
    def update_contact(self, contact_id, contact_data, retry_count=3):
        """Update contact in HubSpot"""
        if not self.client:
            return None
        
        self._handle_rate_limit()
        
        try:
            properties = {}
            if 'first_name' in contact_data:
                properties['firstname'] = contact_data['first_name']
            if 'last_name' in contact_data:
                properties['lastname'] = contact_data['last_name']
            if 'email' in contact_data:
                properties['email'] = contact_data['email']
            if 'phone' in contact_data:
                properties['phone'] = contact_data['phone']
            if 'company' in contact_data:
                properties['company'] = contact_data['company']
            
            mapped_properties = self._map_fields(properties, 'contact')
            properties = {k: v for k, v in mapped_properties.items() if v}
            
            api_response = self.client.crm.contacts.basic_api.update(
                contact_id=contact_id,
                simple_public_object_input={'properties': properties}
            )
            
            logger.info(f"HubSpot contact updated: {contact_id}")
            return {'id': api_response.id, 'properties': api_response.properties}
        
        except ContactsApiException as e:
            if retry_count > 0:
                logger.warning(f"HubSpot API error, retrying: {str(e)}")
                time.sleep(1)
                return self.update_contact(contact_id, contact_data, retry_count - 1)
            else:
                logger.error(f"HubSpot update_contact error: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"HubSpot update_contact error: {str(e)}")
            return None
    
    def create_deal(self, deal_data, associated_contact_id=None, retry_count=3):
        """
        Create deal in HubSpot for qualified leads
        """
        if not self.client:
            return None
        
        self._handle_rate_limit()
        
        try:
            properties = {
                'dealname': deal_data.get('name', 'Deal'),
                'amount': str(deal_data.get('value', '')) if deal_data.get('value') else '',
                'dealstage': deal_data.get('stage', 'appointmentscheduled'),
                'pipeline': deal_data.get('pipeline', 'default'),
            }
            
            mapped_properties = self._map_fields(properties, 'deal')
            properties = {k: v for k, v in mapped_properties.items() if v}
            
            # Create deal
            api_response = self.client.crm.deals.basic_api.create(
                simple_public_object_input={'properties': properties}
            )
            
            deal_id = api_response.id
            
            # Associate with contact if provided
            if associated_contact_id:
                self.associate_deal_with_contact(deal_id, associated_contact_id)
            
            logger.info(f"HubSpot deal created: {deal_id}")
            return {'id': deal_id, 'properties': api_response.properties}
        
        except DealsApiException as e:
            if retry_count > 0:
                logger.warning(f"HubSpot API error, retrying: {str(e)}")
                time.sleep(1)
                return self.create_deal(deal_data, associated_contact_id, retry_count - 1)
            else:
                logger.error(f"HubSpot create_deal error: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"HubSpot create_deal error: {str(e)}")
            return None
    
    def add_timeline_note(self, contact_id, note_content, note_type='NOTE', retry_count=3):
        """
        Add timeline note/activity to contact
        """
        if not self.client:
            return None
        
        self._handle_rate_limit()
        
        try:
            # Use notes API for better compatibility
            notes_api = self.client.crm.notes.basic_api
            
            # Create note
            note_properties = {
                'hs_note_body': note_content,
            }
            
            api_response = notes_api.create(
                simple_public_object_input={'properties': note_properties}
            )
            
            note_id = api_response.id
            
            # Associate note with contact
            try:
                associations_api = self.client.crm.notes.associations_api
                associations_api.create(
                    note_id=note_id,
                    to_object_type='contacts',
                    to_object_id=contact_id,
                    association_type='note_to_contact'
                )
            except Exception as assoc_error:
                logger.warning(f"Failed to associate note with contact: {str(assoc_error)}")
            
            logger.info(f"HubSpot note added to contact: {contact_id}")
            return {'id': note_id}
        
        except Exception as e:
            if retry_count > 0:
                logger.warning(f"HubSpot API error, retrying: {str(e)}")
                time.sleep(1)
                return self.add_timeline_note(contact_id, note_content, note_type, retry_count - 1)
            else:
                logger.error(f"HubSpot add_timeline_note error: {str(e)}")
                return None
    
    def tag_contact(self, contact_id, tags, retry_count=3):
        """
        Tag contact based on source or other criteria
        """
        if not self.client:
            return None
        
        self._handle_rate_limit()
        
        try:
            # Get current contact
            contact = self.client.crm.contacts.basic_api.get_by_id(contact_id)
            current_tags = contact.properties.get('tags', '').split(';') if contact.properties.get('tags') else []
            
            # Add new tags
            new_tags = list(set(current_tags + tags))
            tags_string = ';'.join(new_tags)
            
            # Update contact with tags
            api_response = self.client.crm.contacts.basic_api.update(
                contact_id=contact_id,
                simple_public_object_input={'properties': {'tags': tags_string}}
            )
            
            logger.info(f"HubSpot contact tagged: {contact_id} with {tags}")
            return {'id': api_response.id}
        
        except ContactsApiException as e:
            if retry_count > 0:
                logger.warning(f"HubSpot API error, retrying: {str(e)}")
                time.sleep(1)
                return self.tag_contact(contact_id, tags, retry_count - 1)
            else:
                logger.error(f"HubSpot tag_contact error: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"HubSpot tag_contact error: {str(e)}")
            return None
    
    def search_contact_by_email(self, email):
        """Search for contact by email"""
        if not self.client:
            return None
        
        self._handle_rate_limit()
        
        try:
            search_request = {
                'filterGroups': [{
                    'filters': [{
                        'propertyName': 'email',
                        'operator': 'EQ',
                        'value': email
                    }]
                }],
                'limit': 1
            }
            
            api_response = self.client.crm.contacts.search_api.do_search(
                public_object_search_request=search_request
            )
            
            if api_response.results:
                result = api_response.results[0]
                return {'id': result.id, 'properties': result.properties}
            return None
        
        except Exception as e:
            logger.error(f"HubSpot search_contact_by_email error: {str(e)}")
            return None
    
    def associate_deal_with_contact(self, deal_id, contact_id):
        """Associate deal with contact"""
        if not self.client:
            return None
        
        self._handle_rate_limit()
        
        try:
            # Associate deal with contact
            self.client.crm.deals.associations_api.create(
                deal_id=deal_id,
                to_object_type='contacts',
                to_object_id=contact_id,
                association_type='deal_to_contact'
            )
            
            logger.info(f"HubSpot deal {deal_id} associated with contact {contact_id}")
            return True
        
        except Exception as e:
            logger.error(f"HubSpot associate_deal_with_contact error: {str(e)}")
            return False
    
    def batch_create_contacts(self, contacts_data):
        """
        Batch create contacts (up to batch_size)
        """
        if not self.client:
            return []
        
        results = []
        for i in range(0, len(contacts_data), self.batch_size):
            batch = contacts_data[i:i + self.batch_size]
            batch_results = []
            
            for contact_data in batch:
                result = self.create_contact(contact_data)
                if result:
                    batch_results.append(result)
            
            results.extend(batch_results)
        
        return results


# Global HubSpot service instance
hubspot_service = HubSpotService()

