"""
Analytics utility functions
"""
import hashlib
import re
import logging
from urllib.parse import urlparse, parse_qs
from django.conf import settings

logger = logging.getLogger(__name__)


def anonymize_ip(ip_address):
    """
    Anonymize IP address for GDPR compliance
    IPv4: Remove last octet (e.g., 192.168.1.1 -> 192.168.1.0)
    IPv6: Remove last 64 bits
    """
    if not ip_address:
        return None
    
    # IPv4
    if '.' in ip_address:
        parts = ip_address.split('.')
        if len(parts) == 4:
            return '.'.join(parts[:3]) + '.0'
    
    # IPv6
    if ':' in ip_address:
        parts = ip_address.split(':')
        if len(parts) >= 4:
            return ':'.join(parts[:4]) + '::'
    
    return ip_address


def hash_ip_address(ip_address):
    """
    Hash IP address for GDPR compliance (one-way hash)
    """
    if not ip_address:
        return None
    
    # First anonymize, then hash
    anonymized = anonymize_ip(ip_address)
    return hashlib.sha256(anonymized.encode()).hexdigest()


def parse_user_agent(user_agent_string):
    """
    Parse user agent string to extract browser, OS, and device info
    Returns dict with: browser, browser_version, os, os_version, device_type
    """
    if not user_agent_string:
        return {
            'browser': None,
            'browser_version': None,
            'os': None,
            'os_version': None,
            'device_type': 'other'
        }
    
    ua = user_agent_string.lower()
    
    # Device type detection
    device_type = 'desktop'
    if 'mobile' in ua or 'android' in ua:
        device_type = 'mobile'
    elif 'tablet' in ua or 'ipad' in ua:
        device_type = 'tablet'
    
    # Browser detection
    browser = None
    browser_version = None
    
    if 'chrome' in ua and 'edg' not in ua:
        browser = 'Chrome'
        match = re.search(r'chrome/([\d.]+)', ua)
        if match:
            browser_version = match.group(1)
    elif 'firefox' in ua:
        browser = 'Firefox'
        match = re.search(r'firefox/([\d.]+)', ua)
        if match:
            browser_version = match.group(1)
    elif 'safari' in ua and 'chrome' not in ua:
        browser = 'Safari'
        match = re.search(r'version/([\d.]+)', ua)
        if match:
            browser_version = match.group(1)
    elif 'edg' in ua or 'edge' in ua:
        browser = 'Edge'
        match = re.search(r'edg?e?/([\d.]+)', ua)
        if match:
            browser_version = match.group(1)
    elif 'opera' in ua:
        browser = 'Opera'
        match = re.search(r'opera/([\d.]+)', ua)
        if match:
            browser_version = match.group(1)
    
    # OS detection
    os_name = None
    os_version = None
    
    if 'windows' in ua:
        os_name = 'Windows'
        match = re.search(r'windows nt ([\d.]+)', ua)
        if match:
            os_version = match.group(1)
    elif 'mac' in ua or 'macintosh' in ua:
        os_name = 'macOS'
        match = re.search(r'mac os x ([\d_]+)', ua)
        if match:
            os_version = match.group(1).replace('_', '.')
    elif 'linux' in ua:
        os_name = 'Linux'
    elif 'android' in ua:
        os_name = 'Android'
        match = re.search(r'android ([\d.]+)', ua)
        if match:
            os_version = match.group(1)
    elif 'ios' in ua or 'iphone' in ua or 'ipad' in ua:
        os_name = 'iOS'
        match = re.search(r'os ([\d_]+)', ua)
        if match:
            os_version = match.group(1).replace('_', '.')
    
    return {
        'browser': browser,
        'browser_version': browser_version,
        'os': os_name,
        'os_version': os_version,
        'device_type': device_type
    }


def extract_utm_parameters(request):
    """
    Extract UTM parameters from request
    """
    utm_params = {}
    utm_keys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content']
    
    for key in utm_keys:
        value = request.GET.get(key)
        if value:
            utm_params[key] = value
    
    return utm_params


def extract_campaign_info(request):
    """
    Extract campaign information from request (UTM + referrer)
    """
    utm_params = extract_utm_parameters(request)
    referrer = request.META.get('HTTP_REFERER', '')
    
    campaign_info = {
        'source': utm_params.get('utm_source'),
        'medium': utm_params.get('utm_medium'),
        'campaign': utm_params.get('utm_campaign'),
        'term': utm_params.get('utm_term'),
        'content': utm_params.get('utm_content'),
        'referrer': referrer,
    }
    
    # Parse referrer domain if available
    if referrer:
        try:
            parsed = urlparse(referrer)
            campaign_info['referrer_domain'] = parsed.netloc
        except Exception:
            pass
    
    return campaign_info


def get_client_ip(request):
    """
    Get client IP address from request
    Handles proxies and load balancers
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    
    return ip


def get_geolocation(ip_address):
    """
    Get geolocation from IP address (optional, anonymized)
    Returns dict with country, city (if available)
    
    Note: This is a placeholder. In production, use a service like:
    - MaxMind GeoIP2
    - ipapi.co
    - ip-api.com
    """
    # Placeholder - implement with actual geolocation service
    # For now, return None to indicate geolocation is not available
    return {
        'country': None,
        'city': None,
    }


def check_analytics_consent(request):
    """
    Check if user has given consent for analytics tracking
    Checks cookie or session for consent flag
    """
    # Check cookie
    consent_cookie = request.COOKIES.get('analytics_consent', 'false')
    if consent_cookie.lower() == 'true':
        return True
    
    # Check session
    if hasattr(request, 'session'):
        consent_session = request.session.get('analytics_consent', False)
        if consent_session:
            return True
    
    # Check if opt-out cookie is set
    opt_out = request.COOKIES.get('analytics_opt_out', 'false')
    if opt_out.lower() == 'true':
        return False
    
    # Default: check settings for default consent behavior
    default_consent = getattr(settings, 'ANALYTICS_REQUIRE_CONSENT', True)
    return not default_consent  # If consent required, default is False


def should_track_request(request):
    """
    Determine if request should be tracked
    Checks various conditions:
    - Analytics consent
    - Excluded paths
    - Bot detection
    - Admin/staff users (optional)
    """
    # Check consent
    if not check_analytics_consent(request):
        return False
    
    # Check excluded paths
    excluded_paths = getattr(settings, 'ANALYTICS_EXCLUDED_PATHS', [
        '/admin/',
        '/api/admin/',
        '/static/',
        '/media/',
        '/favicon.ico',
    ])
    
    path = request.path
    for excluded in excluded_paths:
        if path.startswith(excluded):
            return False
    
    # Check if bot (simple detection)
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    bot_keywords = ['bot', 'crawler', 'spider', 'scraper', 'monitor']
    if any(keyword in user_agent for keyword in bot_keywords):
        return False
    
    # Check if admin/staff (optional)
    exclude_staff = getattr(settings, 'ANALYTICS_EXCLUDE_STAFF', True)
    if exclude_staff and hasattr(request, 'user') and request.user.is_authenticated:
        if request.user.is_staff:
            return False
    
    return True

