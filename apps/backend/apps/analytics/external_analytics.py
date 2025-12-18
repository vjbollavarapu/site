"""
External analytics integration (Google Analytics, Mixpanel, etc.)
"""
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class GoogleAnalytics:
    """
    Google Analytics 4 integration
    """
    
    def __init__(self):
        self.measurement_id = getattr(settings, 'GA4_MEASUREMENT_ID', '')
        self.api_secret = getattr(settings, 'GA4_API_SECRET', '')
        self.enabled = bool(self.measurement_id)
    
    def track_pageview(self, page_url, page_title=None, session_id=None, user_id=None):
        """Send pageview to Google Analytics"""
        if not self.enabled:
            return
        
        try:
            url = f"https://www.google-analytics.com/mp/collect"
            params = {
                'measurement_id': self.measurement_id,
                'api_secret': self.api_secret,
            }
            
            payload = {
                'client_id': session_id or 'anonymous',
                'events': [{
                    'name': 'page_view',
                    'params': {
                        'page_location': page_url,
                        'page_title': page_title or '',
                    }
                }]
            }
            
            if user_id:
                payload['user_id'] = user_id
            
            response = requests.post(url, params=params, json=payload, timeout=2)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Google Analytics tracking error: {str(e)}")
    
    def track_event(self, event_name, event_params=None, session_id=None, user_id=None):
        """Send event to Google Analytics"""
        if not self.enabled:
            return
        
        try:
            url = f"https://www.google-analytics.com/mp/collect"
            params = {
                'measurement_id': self.measurement_id,
                'api_secret': self.api_secret,
            }
            
            payload = {
                'client_id': session_id or 'anonymous',
                'events': [{
                    'name': event_name,
                    'params': event_params or {}
                }]
            }
            
            if user_id:
                payload['user_id'] = user_id
            
            response = requests.post(url, params=params, json=payload, timeout=2)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Google Analytics event tracking error: {str(e)}")


class Mixpanel:
    """
    Mixpanel integration
    """
    
    def __init__(self):
        self.token = getattr(settings, 'MIXPANEL_TOKEN', '')
        self.enabled = bool(self.token)
    
    def track(self, event_name, properties=None, distinct_id=None):
        """Send event to Mixpanel"""
        if not self.enabled:
            return
        
        try:
            url = "https://api.mixpanel.com/track"
            
            data = {
                'event': event_name,
                'properties': {
                    'token': self.token,
                    'distinct_id': distinct_id or 'anonymous',
                    **(properties or {})
                }
            }
            
            response = requests.post(url, json=[data], timeout=2)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Mixpanel tracking error: {str(e)}")


class ExternalAnalyticsService:
    """
    Service to send analytics data to external providers
    """
    
    def __init__(self):
        self.ga = GoogleAnalytics()
        self.mixpanel = Mixpanel()
        self.enabled = getattr(settings, 'ANALYTICS_EXTERNAL_ENABLED', False)
    
    def track_pageview(self, page_url, page_title=None, session_id=None, user_id=None):
        """Track pageview in external analytics"""
        if not self.enabled:
            return
        
        try:
            self.ga.track_pageview(page_url, page_title, session_id, user_id)
            self.mixpanel.track('Page View', {
                'page_url': page_url,
                'page_title': page_title,
            }, distinct_id=session_id)
        except Exception as e:
            logger.error(f"External analytics tracking error: {str(e)}")
    
    def track_event(self, event_name, event_params=None, session_id=None, user_id=None):
        """Track event in external analytics"""
        if not self.enabled:
            return
        
        try:
            self.ga.track_event(event_name, event_params, session_id, user_id)
            self.mixpanel.track(event_name, event_params or {}, distinct_id=session_id)
        except Exception as e:
            logger.error(f"External analytics event tracking error: {str(e)}")


# Global external analytics service
external_analytics = ExternalAnalyticsService()

