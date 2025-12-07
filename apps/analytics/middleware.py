"""
Analytics middleware for automatic tracking
"""
import time
import logging
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

from .utils import (
    hash_ip_address,
    parse_user_agent,
    extract_campaign_info,
    get_client_ip,
    get_geolocation,
    should_track_request,
)
from .session_manager import SessionManager
from .batch_processor import batch_processor
from .external_analytics import external_analytics

logger = logging.getLogger(__name__)


class AnalyticsMiddleware(MiddlewareMixin):
    """
    Middleware to automatically track page views, sessions, and user journey
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.use_batch_processing = getattr(settings, 'ANALYTICS_USE_BATCH', True)
        self.track_external = getattr(settings, 'ANALYTICS_EXTERNAL_ENABLED', False)
        super().__init__(get_response)
    
    def process_request(self, request):
        """Process request before view"""
        # Store start time for duration calculation
        request._analytics_start_time = time.time()
        
        # Check if should track
        if not should_track_request(request):
            return None
        
        # Get or create session
        session_id = SessionManager.get_or_create_session(request)
        request._analytics_session_id = session_id
        
        # Extract analytics data
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referrer = request.META.get('HTTP_REFERER', '')
        page_url = request.build_absolute_uri()
        page_title = None  # Will be set from response if available
        
        # Parse user agent
        ua_data = parse_user_agent(user_agent)
        
        # Get geolocation (optional)
        geo_data = {}
        if getattr(settings, 'ANALYTICS_ENABLE_GEOLOCATION', False):
            geo_data = get_geolocation(ip_address)
        
        # Extract campaign info
        campaign_info = extract_campaign_info(request)
        
        # Hash IP for GDPR
        ip_hash = hash_ip_address(ip_address)
        
        # Prepare page view data
        page_view_data = {
            'session_id': session_id,
            'page_url': page_url,
            'page_title': page_title,
            'referrer_url': referrer or None,
            'user_agent': user_agent,
            'ip_address_hash': ip_hash,
            'device_type': ua_data.get('device_type'),
            'browser': ua_data.get('browser'),
            'operating_system': ua_data.get('os'),
            'country': geo_data.get('country'),
            'city': geo_data.get('city'),
            'timestamp': timezone.now(),
        }
        
        # Store in request for later use
        request._analytics_page_view_data = page_view_data
        request._analytics_campaign_info = campaign_info
        
        return None
    
    def process_response(self, request, response):
        """Process response after view"""
        # Check if should track
        if not should_track_request(request):
            return response
        
        # Get session ID
        session_id = getattr(request, '_analytics_session_id', None)
        if not session_id:
            return response
        
        # Update session activity
        SessionManager.update_session_activity(session_id)
        
        # Get page view data
        page_view_data = getattr(request, '_analytics_page_view_data', None)
        if not page_view_data:
            return response
        
        # Calculate duration
        start_time = getattr(request, '_analytics_start_time', None)
        if start_time:
            duration = time.time() - start_time
            page_view_data['duration'] = duration
        
        # Try to extract page title from response (if HTML)
        if hasattr(response, 'content'):
            try:
                content = response.content.decode('utf-8', errors='ignore')
                if '<title>' in content:
                    import re
                    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
                    if title_match:
                        page_view_data['page_title'] = title_match.group(1).strip()[:500]
            except Exception:
                pass
        
        # Store page view
        if self.use_batch_processing:
            batch_processor.add_page_view(page_view_data)
        else:
            # Immediate save
            try:
                from .models import PageView
                PageView.objects.create(**page_view_data)
            except Exception as e:
                logger.error(f"Error saving page view: {str(e)}")
        
        # Send to external analytics
        if self.track_external:
            try:
                user_id = None
                if hasattr(request, 'user') and request.user.is_authenticated:
                    user_id = str(request.user.id)
                
                external_analytics.track_pageview(
                    page_view_data['page_url'],
                    page_view_data.get('page_title'),
                    session_id,
                    user_id
                )
            except Exception as e:
                logger.error(f"Error sending to external analytics: {str(e)}")
        
        # Set session cookie
        if not request.COOKIES.get('analytics_session_id'):
            response.set_cookie(
                'analytics_session_id',
                session_id,
                max_age=86400 * 30,  # 30 days
                httponly=True,
                samesite='Lax'
            )
        
        return response
    
    def process_exception(self, request, exception):
        """Handle exceptions"""
        # Log error event if needed
        logger.error(f"Analytics middleware exception: {str(exception)}")
        return None

