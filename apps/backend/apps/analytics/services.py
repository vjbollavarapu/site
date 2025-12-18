"""
Event tracking service for analytics
"""
import uuid
import hashlib
import time
import logging
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Count, Avg, Sum, Max, Min, Q
from django.db.models.functions import TruncDate, TruncHour
from django.conf import settings

from .models import PageView, Event, Conversion
from .utils import (
    hash_ip_address,
    parse_user_agent,
    get_client_ip,
    get_geolocation,
    extract_campaign_info,
    extract_utm_parameters,
)
from .session_manager import SessionManager
from .batch_processor import batch_processor
from .external_analytics import external_analytics

logger = logging.getLogger(__name__)

# Cache keys
CACHE_KEY_SESSION = 'analytics_session_{}'
CACHE_KEY_STATS = 'analytics_stats_{}'  # {date}
CACHE_KEY_DASHBOARD = 'analytics_dashboard'
CACHE_TIMEOUT = 3600  # 1 hour


class TrackEvents:
    """
    Service class for tracking analytics events
    """
    
    def __init__(self, request=None):
        self.request = request
        self.use_batch = getattr(settings, 'ANALYTICS_USE_BATCH', True)
        self.track_external = getattr(settings, 'ANALYTICS_EXTERNAL_ENABLED', False)
    
    def get_session(self, session_id=None):
        """
        Get or create session
        Returns session_id and session data
        """
        if not session_id and self.request:
            session_id = SessionManager.get_or_create_session(self.request)
        elif not session_id:
            # Create new session without request
            session_id = str(uuid.uuid4())
            session_data = {
                'session_id': session_id,
                'created_at': time.time(),
                'last_activity': time.time(),
                'page_views': 0,
                'events': 0,
            }
            try:
                cache.set(CACHE_KEY_SESSION.format(session_id), session_data, 
                         getattr(settings, 'ANALYTICS_SESSION_TIMEOUT', 1800))
            except Exception as e:
                logger.warning(f"Cache set error (Redis may be unavailable): {str(e)}")
        
        session_data = SessionManager.get_session_data(session_id)
        if not session_data:
            # Create new session
            session_id = str(uuid.uuid4())
            session_data = {
                'session_id': session_id,
                'created_at': time.time(),
                'last_activity': time.time(),
                'page_views': 0,
                'events': 0,
            }
            try:
                cache.set(CACHE_KEY_SESSION.format(session_id), session_data,
                         getattr(settings, 'ANALYTICS_SESSION_TIMEOUT', 1800))
            except Exception as e:
                logger.warning(f"Cache set error (Redis may be unavailable): {str(e)}")
        
        return session_id, session_data
    
    def update_session(self, session_id, **kwargs):
        """
        Update session data
        """
        try:
            session_data = SessionManager.get_session_data(session_id)
        except Exception as e:
            logger.warning(f"Session data retrieval error (Redis may be unavailable): {str(e)}")
            session_data = None
        
        if session_data:
            session_data.update(kwargs)
            session_data['last_activity'] = time.time()
            try:
                cache.set(CACHE_KEY_SESSION.format(session_id), session_data,
                         getattr(settings, 'ANALYTICS_SESSION_TIMEOUT', 1800))
            except Exception as e:
                logger.warning(f"Cache set error (Redis may be unavailable): {str(e)}")
            return session_data
        return None
    
    def track_page_view(self, page_url, page_title=None, referrer_url=None, 
                       duration=None, is_exit_page=False, session_id=None,
                       user_id=None, custom_properties=None, **kwargs):
        """
        Track a page view
        
        Args:
            page_url: URL of the page
            page_title: Title of the page
            referrer_url: Referrer URL
            duration: Time spent on page (seconds)
            is_exit_page: Whether this is an exit page
            session_id: Session ID (optional, will be created if not provided)
            user_id: User ID (optional, will be hashed for privacy)
            custom_properties: Dict of custom properties
            **kwargs: Additional properties
        """
        # Get or create session
        session_id, session_data = self.get_session(session_id)
        
        # Extract request data if available
        ip_address = None
        user_agent = None
        geo_data = {}
        campaign_info = {}
        
        if self.request:
            ip_address = get_client_ip(self.request)
            user_agent = self.request.META.get('HTTP_USER_AGENT', '')
            referrer_url = referrer_url or self.request.META.get('HTTP_REFERER', '')
            campaign_info = extract_campaign_info(self.request)
            
            if getattr(settings, 'ANALYTICS_ENABLE_GEOLOCATION', False):
                geo_data = get_geolocation(ip_address)
        
        # Parse user agent
        ua_data = parse_user_agent(user_agent) if user_agent else {}
        
        # Hash IP for GDPR
        ip_hash = hash_ip_address(ip_address) if ip_address else None
        
        # Hash user ID for privacy
        user_identifier = None
        if user_id:
            user_identifier = hashlib.sha256(str(user_id).encode()).hexdigest()
        
        # Prepare page view data
        page_view_data = {
            'session_id': session_id,
            'page_url': page_url,
            'page_title': page_title,
            'referrer_url': referrer_url,
            'user_agent': user_agent,
            'ip_address_hash': ip_hash,
            'device_type': ua_data.get('device_type', 'other'),
            'browser': ua_data.get('browser'),
            'operating_system': ua_data.get('os'),
            'country': geo_data.get('country'),
            'city': geo_data.get('city'),
            'duration': duration,
            'is_exit_page': is_exit_page,
            'timestamp': timezone.now(),
        }
        
        # Add custom properties to metadata if needed
        if custom_properties or kwargs:
            # Store in a metadata field if model supports it
            # For now, we'll add to page_view_data if model has JSONField
            pass
        
        # Store page view
        if self.use_batch:
            batch_processor.add_page_view(page_view_data)
        else:
            try:
                pageview = PageView.objects.create(**page_view_data)
                logger.info(f"Page view tracked: {page_url}")
            except Exception as e:
                logger.error(f"Error tracking page view: {str(e)}")
        
        # Update session
        SessionManager.update_session_activity(session_id)
        self.update_session(session_id, page_views=session_data.get('page_views', 0) + 1)
        
        # Send to external analytics
        if self.track_external:
            try:
                external_analytics.track_pageview(
                    page_url, page_title, session_id, user_id
                )
            except Exception as e:
                logger.error(f"Error sending to external analytics: {str(e)}")
        
        return session_id
    
    def track_event(self, event_name, event_category='other', event_value=None,
                   page_url=None, session_id=None, user_id=None,
                   event_properties=None, metadata=None, **kwargs):
        """
        Track a custom event
        
        Args:
            event_name: Name of the event
            event_category: Category of the event
            event_value: Numeric value associated with event
            page_url: URL where event occurred
            session_id: Session ID
            user_id: User ID (optional, will be hashed)
            event_properties: Dict of event properties (flexible JSONField)
            metadata: Additional metadata
            **kwargs: Additional properties
        """
        # Get or create session
        session_id, session_data = self.get_session(session_id)
        
        # Extract request data if available
        if self.request:
            page_url = page_url or self.request.build_absolute_uri()
            ip_address = get_client_ip(self.request)
            user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        else:
            ip_address = None
            user_agent = None
        
        # Hash user ID for privacy
        user_identifier = None
        if user_id:
            user_identifier = hashlib.sha256(str(user_id).encode()).hexdigest()
        
        # Prepare event data
        event_data = {
            'event_name': event_name,
            'event_category': event_category,
            'event_value': event_value,
            'event_properties': event_properties or {},
            'session_id': session_id,
            'page_url': page_url,
            'user_identifier': user_identifier,
            'timestamp': timezone.now(),
            'metadata': metadata or {},
        }
        
        # Add any additional kwargs to event_properties
        if kwargs:
            event_data['event_properties'].update(kwargs)
        
        # Add standard properties
        if page_url:
            event_data['event_properties']['page_url'] = page_url
        if user_agent:
            event_data['metadata']['user_agent'] = user_agent
        if ip_address:
            event_data['metadata']['ip_address_hash'] = hash_ip_address(ip_address)
        
        # Store event
        if self.use_batch:
            batch_processor.add_event(event_data)
        else:
            try:
                event = Event.objects.create(**event_data)
                logger.info(f"Event tracked: {event_name}")
            except Exception as e:
                logger.error(f"Error tracking event: {str(e)}")
        
        # Update session
        SessionManager.increment_event_count(session_id)
        self.update_session(session_id, events=session_data.get('events', 0) + 1)
        
        # Send to external analytics
        if self.track_external:
            try:
                external_analytics.track_event(
                    event_name, event_data['event_properties'], session_id, user_id
                )
            except Exception as e:
                logger.error(f"Error sending to external analytics: {str(e)}")
        
        return session_id
    
    def track_conversion(self, conversion_type, value=None, content_object=None,
                        attribution_data=None, campaign_info=None, session_id=None,
                        user_id=None, **kwargs):
        """
        Track a conversion
        
        Args:
            conversion_type: Type of conversion
            value: Conversion value (monetary)
            content_object: Related object (Lead, ContactSubmission, etc.)
            attribution_data: Attribution data (UTM params, referrer)
            campaign_info: Campaign information
            session_id: Session ID
            user_id: User ID
            **kwargs: Additional data
        """
        # Get or create session
        session_id, _ = self.get_session(session_id)
        
        # Extract request data if available
        if self.request:
            if not attribution_data:
                attribution_data = extract_utm_parameters(self.request)
            if not campaign_info:
                campaign_info = extract_campaign_info(self.request)
        
        # Prepare conversion data
        conversion_data = {
            'conversion_type': conversion_type,
            'value': value,
            'attribution_data': attribution_data or {},
            'campaign_info': campaign_info or {},
            'timestamp': timezone.now(),
        }
        
        # Link to content object if provided
        if content_object:
            from django.contrib.contenttypes.models import ContentType
            conversion_data['content_type'] = ContentType.objects.get_for_model(content_object)
            conversion_data['object_id'] = content_object.id
        
        # Add any additional kwargs to attribution_data
        if kwargs:
            conversion_data['attribution_data'].update(kwargs)
        
        # Store conversion
        try:
            conversion = Conversion.objects.create(**conversion_data)
            logger.info(f"Conversion tracked: {conversion_type}")
            
            # Track as event as well
            self.track_event(
                event_name=f'conversion_{conversion_type}',
                event_category='conversion',
                event_value=value,
                session_id=session_id,
                user_id=user_id,
                event_properties={
                    'conversion_id': str(conversion.id),
                    'conversion_type': conversion_type,
                    **conversion_data['attribution_data']
                }
            )
            
            return conversion
        except Exception as e:
            logger.error(f"Error tracking conversion: {str(e)}")
            return None
    
    def get_session_duration(self, session_id):
        """
        Calculate session duration
        Returns duration in seconds
        """
        session_data = SessionManager.get_session_data(session_id)
        if not session_data:
            return None
        
        created_at = session_data.get('created_at')
        last_activity = session_data.get('last_activity')
        
        if created_at and last_activity:
            return last_activity - created_at
        
        # Fallback: calculate from page views
        page_views = PageView.objects.filter(session_id=session_id).order_by('timestamp')
        if page_views.count() >= 2:
            first_view = page_views.first()
            last_view = page_views.last()
            duration = (last_view.timestamp - first_view.timestamp).total_seconds()
            return duration
        
        return None
    
    def get_session_summary(self, session_id):
        """
        Get comprehensive session summary
        """
        session_data = SessionManager.get_session_data(session_id)
        if not session_data:
            return None
        
        # Get page views for session
        page_views = PageView.objects.filter(session_id=session_id).order_by('timestamp')
        events = Event.objects.filter(session_id=session_id).order_by('timestamp')
        
        # Calculate duration
        duration = self.get_session_duration(session_id)
        
        # Get first and last page
        first_page = page_views.first()
        last_page = page_views.last()
        
        return {
            'session_id': session_id,
            'created_at': session_data.get('created_at'),
            'last_activity': session_data.get('last_activity'),
            'duration': duration,
            'page_views_count': page_views.count(),
            'events_count': events.count(),
            'first_page': {
                'url': first_page.page_url if first_page else None,
                'title': first_page.page_title if first_page else None,
                'timestamp': first_page.timestamp if first_page else None,
            },
            'last_page': {
                'url': last_page.page_url if last_page else None,
                'title': last_page.page_title if last_page else None,
                'timestamp': last_page.timestamp if last_page else None,
            },
            'device_type': first_page.device_type if first_page else None,
            'browser': first_page.browser if first_page else None,
            'country': first_page.country if first_page else None,
        }




def calculate_aggregated_stats(date=None):
    """
    Pre-calculate common metrics for a given date
    Caches results for dashboard performance
    """
    if not date:
        date = timezone.now().date()
    
    cache_key = CACHE_KEY_STATS.format(date.isoformat())
    
    # Check cache first
    cached_stats = cache.get(cache_key)
    if cached_stats:
        return cached_stats
    
    # Calculate stats
    pageviews_qs = PageView.objects.filter(timestamp__date=date)
    events_qs = Event.objects.filter(timestamp__date=date)
    conversions_qs = Conversion.objects.filter(timestamp__date=date)
    
    stats = {
        'date': date.isoformat(),
        'total_pageviews': pageviews_qs.count(),
        'unique_visitors': pageviews_qs.values('session_id').distinct().count(),
        'total_events': events_qs.count(),
        'total_conversions': conversions_qs.count(),
        'conversion_value': conversions_qs.aggregate(
            total=Sum('value')
        )['total'] or 0,
        'avg_session_duration': pageviews_qs.exclude(duration__isnull=True).aggregate(
            avg=Avg('duration')
        )['avg'] or 0,
        'bounce_rate': 0,  # Calculate separately
        'top_pages': list(
            pageviews_qs.values('page_url', 'page_title')
            .annotate(views=Count('id'))
            .order_by('-views')[:10]
        ),
        'top_events': list(
            events_qs.values('event_name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        ),
    }
    
    # Calculate bounce rate
    total_sessions = pageviews_qs.values('session_id').distinct().count()
    if total_sessions > 0:
        single_page_sessions = pageviews_qs.values('session_id').annotate(
            page_count=Count('id')
        ).filter(page_count=1).count()
        stats['bounce_rate'] = (single_page_sessions / total_sessions) * 100
    
    # Cache for 1 hour
    try:
        cache.set(cache_key, stats, CACHE_TIMEOUT)
    except Exception as e:
        logger.warning(f"Cache set error (Redis may be unavailable): {str(e)}")
    
    return stats


def get_dashboard_stats(date_from=None, date_to=None):
    """
    Get aggregated dashboard statistics
    Uses cache for performance
    """
    if not date_from:
        date_from = (timezone.now() - timedelta(days=30)).date()
    if not date_to:
        date_to = timezone.now().date()
    
    cache_key = f"{CACHE_KEY_DASHBOARD}_{date_from}_{date_to}"
    
    # Check cache
    cached_stats = cache.get(cache_key)
    if cached_stats:
        return cached_stats
    
    # Calculate stats
    pageviews_qs = PageView.objects.filter(
        timestamp__date__gte=date_from,
        timestamp__date__lte=date_to
    )
    events_qs = Event.objects.filter(
        timestamp__date__gte=date_from,
        timestamp__date__lte=date_to
    )
    conversions_qs = Conversion.objects.filter(
        timestamp__date__gte=date_from,
        timestamp__date__lte=date_to
    )
    
    stats = {
        'date_from': date_from.isoformat(),
        'date_to': date_to.isoformat(),
        'total_pageviews': pageviews_qs.count(),
        'unique_visitors': pageviews_qs.values('session_id').distinct().count(),
        'total_events': events_qs.count(),
        'total_conversions': conversions_qs.count(),
        'conversion_value': conversions_qs.aggregate(
            total=Sum('value')
        )['total'] or 0,
        'avg_session_duration': pageviews_qs.exclude(duration__isnull=True).aggregate(
            avg=Avg('duration')
        )['avg'] or 0,
        'bounce_rate': 0,
        'top_pages': list(
            pageviews_qs.values('page_url', 'page_title')
            .annotate(views=Count('id'), unique_visitors=Count('session_id', distinct=True))
            .order_by('-views')[:10]
        ),
        'top_events': list(
            events_qs.values('event_name', 'event_category')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        ),
        'conversions_by_type': list(
            conversions_qs.values('conversion_type')
            .annotate(count=Count('id'), total_value=Sum('value'))
            .order_by('-count')
        ),
        'daily_stats': list(
            pageviews_qs.annotate(date=TruncDate('timestamp'))
            .values('date')
            .annotate(
                pageviews=Count('id'),
                visitors=Count('session_id', distinct=True),
                events=Count('event', distinct=True)
            )
            .order_by('date')
        ),
    }
    
    # Calculate bounce rate
    total_sessions = pageviews_qs.values('session_id').distinct().count()
    if total_sessions > 0:
        single_page_sessions = pageviews_qs.values('session_id').annotate(
            page_count=Count('id')
        ).filter(page_count=1).count()
        stats['bounce_rate'] = (single_page_sessions / total_sessions) * 100
    
    # Cache for 1 hour
    try:
        cache.set(cache_key, stats, CACHE_TIMEOUT)
    except Exception as e:
        logger.warning(f"Cache set error (Redis may be unavailable): {str(e)}")
    
    return stats

