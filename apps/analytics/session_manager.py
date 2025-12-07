"""
Session management for analytics tracking
"""
import uuid
import time
from django.core.cache import cache
from django.conf import settings

SESSION_TIMEOUT = getattr(settings, 'ANALYTICS_SESSION_TIMEOUT', 1800)  # 30 minutes


class SessionManager:
    """
    Manages analytics sessions
    """
    
    @staticmethod
    def get_or_create_session(request):
        """
        Get existing session ID or create new one
        Returns session_id
        """
        # Check cookie first
        session_id = request.COOKIES.get('analytics_session_id')
        
        if session_id:
            # Verify session still exists in cache
            session_data = cache.get(f'analytics_session_{session_id}')
            if session_data:
                # Update last activity
                session_data['last_activity'] = time.time()
                cache.set(f'analytics_session_{session_id}', session_data, SESSION_TIMEOUT)
                return session_id
        
        # Create new session
        session_id = str(uuid.uuid4())
        session_data = {
            'session_id': session_id,
            'created_at': time.time(),
            'last_activity': time.time(),
            'page_views': 0,
            'events': 0,
        }
        
        cache.set(f'analytics_session_{session_id}', session_data, SESSION_TIMEOUT)
        return session_id
    
    @staticmethod
    def update_session_activity(session_id):
        """Update last activity time for session"""
        session_data = cache.get(f'analytics_session_{session_id}')
        if session_data:
            session_data['last_activity'] = time.time()
            session_data['page_views'] = session_data.get('page_views', 0) + 1
            cache.set(f'analytics_session_{session_id}', session_data, SESSION_TIMEOUT)
    
    @staticmethod
    def get_session_data(session_id):
        """Get session data"""
        return cache.get(f'analytics_session_{session_id}')
    
    @staticmethod
    def increment_event_count(session_id):
        """Increment event count for session"""
        session_data = cache.get(f'analytics_session_{session_id}')
        if session_data:
            session_data['events'] = session_data.get('events', 0) + 1
            session_data['last_activity'] = time.time()
            cache.set(f'analytics_session_{session_id}', session_data, SESSION_TIMEOUT)
    
    @staticmethod
    def get_user_journey(session_id):
        """
        Get user journey for session
        Returns list of page views and events in chronological order
        """
        # This would query the database for all page views and events for this session
        # For now, return session metadata
        session_data = cache.get(f'analytics_session_{session_id}')
        if session_data:
            return {
                'session_id': session_id,
                'created_at': session_data.get('created_at'),
                'last_activity': session_data.get('last_activity'),
                'page_views': session_data.get('page_views', 0),
                'events': session_data.get('events', 0),
            }
        return None

