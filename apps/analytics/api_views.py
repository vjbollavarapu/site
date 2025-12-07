from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.utils import timezone
from django.db.models import Count, Q, Avg, Sum, Max, Min, F
from django.db.models.functions import TruncDate
from django.utils.dateparse import parse_date
from django_ratelimit.core import is_ratelimited
from datetime import timedelta
import secrets
import re
from .models import PageView, Event, Conversion
from .serializers import (
    PageViewSerializer,
    EventSerializer,
    PageViewListSerializer,
    EventListSerializer,
    ConversionListSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def track_pageview(request):
    """
    Public endpoint to track page views
    Extracts device/browser info and geolocation
    Rate limited: 10 requests per IP per hour
    """
    # Rate limiting check
    if is_ratelimited(request, group='analytics-pageview', key='ip', rate='10/h', method='POST', increment=True):
        return Response(
            {'error': 'Too many requests. Please try again later.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    serializer = PageViewSerializer(data=request.data)
    
    if serializer.is_valid():
        # Extract metadata
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referrer = serializer.validated_data.get('referrer_url') or request.META.get('HTTP_REFERER', '')
        session_id = serializer.validated_data.get('session_id') or get_or_create_session_id(request)
        
        # Extract device/browser info from user agent
        device_info = parse_user_agent(user_agent)
        
        # Hash IP address for GDPR compliance
        ip_hash = hash_ip_address(ip_address) if ip_address else None
        
        # Get geolocation (simplified - in production use a geolocation service)
        geo_info = get_geolocation(ip_address) if ip_address else {}
        
        # Create page view
        pageview = PageView.objects.create(
            session_id=session_id,
            page_url=serializer.validated_data['page_url'],
            page_title=serializer.validated_data.get('page_title', ''),
            referrer_url=referrer,
            user_agent=user_agent,
            ip_address_hash=ip_hash,
            device_type=device_info.get('device_type', 'other'),
            browser=device_info.get('browser', ''),
            operating_system=device_info.get('os', ''),
            country=geo_info.get('country', ''),
            city=geo_info.get('city', ''),
            duration=serializer.validated_data.get('duration'),
            is_exit_page=serializer.validated_data.get('is_exit_page', False)
        )
        
        return Response({
            'success': True,
            'session_id': session_id,
            'pageview_id': str(pageview.id)
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def track_event(request):
    """
    Public endpoint to track custom events
    Rate limited: 10 requests per IP per hour
    """
    # Rate limiting check
    if is_ratelimited(request, group='analytics-event', key='ip', rate='10/h', method='POST', increment=True):
        return Response(
            {'error': 'Too many requests. Please try again later.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    serializer = EventSerializer(data=request.data)
    
    if serializer.is_valid():
        # Extract metadata
        session_id = serializer.validated_data.get('session_id') or get_or_create_session_id(request)
        page_url = serializer.validated_data.get('page_url') or request.META.get('HTTP_REFERER', '')
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Create event
        event = Event.objects.create(
            event_name=serializer.validated_data['event_name'],
            event_category=serializer.validated_data.get('event_category', 'other'),
            event_value=serializer.validated_data.get('event_value'),
            event_properties=serializer.validated_data.get('event_properties', {}),
            session_id=session_id,
            page_url=page_url,
            user_identifier=serializer.validated_data.get('user_identifier', ''),
            metadata={
                'ip_address': hash_ip_address(ip_address) if ip_address else None,
                'user_agent': user_agent
            }
        )
        
        return Response({
            'success': True,
            'event_id': str(event.id),
            'session_id': session_id
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PageViewViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing page views (admin only)
    """
    queryset = PageView.objects.all()
    serializer_class = PageViewListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['page_url', 'page_title', 'session_id']
    ordering_fields = ['timestamp', 'duration']
    ordering = ['-timestamp']


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing events (admin only)
    """
    queryset = Event.objects.all()
    serializer_class = EventListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['event_name', 'session_id', 'user_identifier', 'page_url']
    ordering_fields = ['timestamp', 'event_value']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = Event.objects.all()
        
        # Filter by event name
        event_name = self.request.query_params.get('event_name', None)
        if event_name:
            queryset = queryset.filter(event_name=event_name)
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(event_category=category)
        
        # Group by event name
        group_by = self.request.query_params.get('group_by', None)
        if group_by == 'event_name':
            # This would be handled in a custom action
            pass
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def grouped(self, request):
        """Get events grouped by event name with aggregations"""
        queryset = self.get_queryset()
        
        # Group by event name
        grouped = queryset.values('event_name', 'event_category').annotate(
            count=Count('id'),
            total_value=Sum('event_value'),
            avg_value=Avg('event_value'),
            max_value=Max('event_value'),
            min_value=Min('event_value')
        ).order_by('-count')
        
        return Response(list(grouped), status=status.HTTP_200_OK)


class ConversionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing conversions (admin only)
    """
    queryset = Conversion.objects.all()
    serializer_class = ConversionListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['conversion_type']
    ordering_fields = ['timestamp', 'value']
    ordering = ['-timestamp']


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def analytics_dashboard(request):
    """
    Admin endpoint for analytics dashboard
    Provides aggregate statistics
    """
    # Get date range from query params
    date_from = request.query_params.get('date_from', None)
    date_to = request.query_params.get('date_to', None)
    
    # Default to last 30 days if no date range specified
    if not date_from:
        date_from = (timezone.now() - timedelta(days=30)).date()
    else:
        date_from = parse_date(date_from)
    
    if not date_to:
        date_to = timezone.now().date()
    else:
        date_to = parse_date(date_to)
    
    # Base querysets with date filtering
    pageviews_qs = PageView.objects.filter(timestamp__date__gte=date_from, timestamp__date__lte=date_to)
    events_qs = Event.objects.filter(timestamp__date__gte=date_from, timestamp__date__lte=date_to)
    conversions_qs = Conversion.objects.filter(timestamp__date__gte=date_from, timestamp__date__lte=date_to)
    
    # Total page views
    total_pageviews = pageviews_qs.count()
    
    # Unique visitors (unique session IDs)
    unique_visitors = pageviews_qs.values('session_id').distinct().count()
    
    # Average session duration
    sessions_with_duration = pageviews_qs.exclude(duration__isnull=True)
    avg_session_duration = sessions_with_duration.aggregate(
        avg_duration=Avg('duration')
    )['avg_duration'] or 0
    
    # Bounce rate (sessions with only 1 pageview)
    total_sessions = pageviews_qs.values('session_id').distinct().count()
    single_page_sessions = pageviews_qs.values('session_id').annotate(
        page_count=Count('id')
    ).filter(page_count=1).count()
    bounce_rate = (single_page_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
    # Top pages
    top_pages = pageviews_qs.values('page_url', 'page_title').annotate(
        views=Count('id'),
        unique_visitors=Count('session_id', distinct=True)
    ).order_by('-views')[:10]
    
    # Traffic sources (referrers)
    traffic_sources = pageviews_qs.exclude(referrer_url__isnull=True).exclude(referrer_url='').values(
        'referrer_url'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Device breakdown
    device_breakdown = pageviews_qs.values('device_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Browser breakdown
    browser_breakdown = pageviews_qs.exclude(browser='').values('browser').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Operating system breakdown
    os_breakdown = pageviews_qs.exclude(operating_system='').values('operating_system').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Geographic data
    geographic_data = pageviews_qs.exclude(country='').values('country', 'city').annotate(
        count=Count('id')
    ).order_by('-count')[:20]
    
    # Daily page views (for chart)
    daily_pageviews = pageviews_qs.annotate(
        date=TruncDate('timestamp')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Conversion funnel
    conversion_funnel = conversions_qs.values('conversion_type').annotate(
        count=Count('id'),
        total_value=Sum('value')
    ).order_by('-count')
    
    # Conversion rate by source
    conversion_by_source = conversions_qs.exclude(
        campaign_info__source__isnull=True
    ).values('campaign_info__source').annotate(
        count=Count('id'),
        total_value=Sum('value')
    ).order_by('-count')
    
    # Revenue attribution
    revenue_attribution = conversions_qs.exclude(value__isnull=True).aggregate(
        total_revenue=Sum('value'),
        avg_revenue=Avg('value'),
        max_revenue=Max('value')
    )
    
    return Response({
        'date_range': {
            'from': date_from.isoformat() if date_from else None,
            'to': date_to.isoformat() if date_to else None
        },
        'overview': {
            'total_pageviews': total_pageviews,
            'unique_visitors': unique_visitors,
            'avg_session_duration': round(avg_session_duration, 2),
            'bounce_rate': round(bounce_rate, 2)
        },
        'top_pages': list(top_pages),
        'traffic_sources': list(traffic_sources),
        'device_breakdown': list(device_breakdown),
        'browser_breakdown': list(browser_breakdown),
        'os_breakdown': list(os_breakdown),
        'geographic_data': list(geographic_data),
        'daily_pageviews': list(daily_pageviews),
        'conversion_funnel': list(conversion_funnel),
        'conversion_by_source': list(conversion_by_source),
        'revenue_attribution': revenue_attribution
    }, status=status.HTTP_200_OK)


def get_or_create_session_id(request):
    """Get or create session ID for tracking"""
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key or secrets.token_urlsafe(16)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def hash_ip_address(ip_address):
    """Hash IP address for GDPR compliance"""
    import hashlib
    if not ip_address:
        return None
    return hashlib.sha256(ip_address.encode()).hexdigest()


def parse_user_agent(user_agent):
    """
    Parse user agent string to extract device, browser, and OS info
    Simplified parser - in production use a library like user-agents
    """
    if not user_agent:
        return {'device_type': 'other', 'browser': '', 'os': ''}
    
    ua_lower = user_agent.lower()
    
    # Device type detection
    device_type = 'desktop'
    if 'mobile' in ua_lower or 'android' in ua_lower:
        device_type = 'mobile'
    elif 'tablet' in ua_lower or 'ipad' in ua_lower:
        device_type = 'tablet'
    
    # Browser detection
    browser = ''
    if 'chrome' in ua_lower and 'edg' not in ua_lower:
        browser = 'Chrome'
    elif 'firefox' in ua_lower:
        browser = 'Firefox'
    elif 'safari' in ua_lower and 'chrome' not in ua_lower:
        browser = 'Safari'
    elif 'edg' in ua_lower:
        browser = 'Edge'
    elif 'opera' in ua_lower:
        browser = 'Opera'
    
    # OS detection
    os = ''
    if 'windows' in ua_lower:
        os = 'Windows'
    elif 'mac' in ua_lower or 'macintosh' in ua_lower:
        os = 'macOS'
    elif 'linux' in ua_lower:
        os = 'Linux'
    elif 'android' in ua_lower:
        os = 'Android'
    elif 'ios' in ua_lower or 'iphone' in ua_lower or 'ipad' in ua_lower:
        os = 'iOS'
    
    return {
        'device_type': device_type,
        'browser': browser,
        'os': os
    }


def get_geolocation(ip_address):
    """
    Get geolocation from IP address
    Simplified - in production use a service like MaxMind GeoIP2 or ipapi.co
    """
    # This is a placeholder - in production, use a proper geolocation service
    # For now, return empty dict
    return {
        'country': '',
        'city': ''
    }
    # Example with a service:
    # try:
    #     response = requests.get(f'https://ipapi.co/{ip_address}/json/')
    #     data = response.json()
    #     return {
    #         'country': data.get('country_name', ''),
    #         'city': data.get('city', '')
    #     }
    # except:
    #     return {'country': '', 'city': ''}

