"""
Utility functions for site detection and management
"""
from .models import Site


def get_site_from_request(request):
    """
    Get site from request headers
    This is a convenience function that wraps Site.get_site_from_request
    """
    return Site.get_site_from_request(request)


def get_site_from_domain(domain):
    """
    Get site from domain name
    This is a convenience function that wraps Site.get_site_from_domain
    """
    return Site.get_site_from_domain(domain)

