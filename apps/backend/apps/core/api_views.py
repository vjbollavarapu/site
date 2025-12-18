"""
API views for core dashboard functionality
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import timedelta

from apps.contacts.models import ContactSubmission
from apps.waitlist.models import WaitlistEntry
from apps.leads.models import Lead
from apps.newsletter.models import NewsletterSubscription


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def dashboard_stats(request):
    """
    Get dashboard statistics aggregating data from all apps
    Returns counts and trends for contacts, waitlist, leads, and newsletter
    
    Query Parameters:
    - site: Filter by site name or ID (optional)
    """
    from apps.core.models import Site
    from apps.core.utils import get_site_from_request
    
    # Get site filter from query params or request
    site_filter = request.query_params.get('site', None)
    site = None
    
    if site_filter:
        # Try to get site by name or ID
        try:
            # Try UUID first
            site = Site.objects.get(id=site_filter, is_active=True)
        except (Site.DoesNotExist, ValueError):
            # Try by name
            try:
                site = Site.objects.get(name=site_filter, is_active=True)
            except Site.DoesNotExist:
                pass
    
    # Base queryset filter
    site_filter_q = Q()
    if site:
        site_filter_q = Q(site=site)
    
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    last_month_start = month_ago - timedelta(days=30)
    
    # Contacts stats
    total_contacts = ContactSubmission.objects.filter(is_spam=False).filter(site_filter_q).count()
    new_contacts = ContactSubmission.objects.filter(
        is_spam=False,
        created_at__date__gte=week_ago.date()
    ).filter(site_filter_q).count()
    pending_contacts = ContactSubmission.objects.filter(
        is_spam=False,
        status='new'
    ).filter(site_filter_q).count()
    
    # Calculate contacts trend (this month vs last month)
    this_month_contacts = ContactSubmission.objects.filter(
        is_spam=False,
        created_at__date__gte=month_ago.date()
    ).filter(site_filter_q).count()
    last_month_contacts = ContactSubmission.objects.filter(
        is_spam=False,
        created_at__date__gte=last_month_start.date(),
        created_at__date__lt=month_ago.date()
    ).filter(site_filter_q).count()
    contacts_trend = 0
    if last_month_contacts > 0:
        contacts_trend = round(((this_month_contacts - last_month_contacts) / last_month_contacts) * 100, 1)
    
    # Waitlist stats
    total_waitlist = WaitlistEntry.objects.filter(site_filter_q).count()
    pending_waitlist = WaitlistEntry.objects.filter(status='pending').filter(site_filter_q).count()
    avg_score = WaitlistEntry.objects.filter(site_filter_q).aggregate(avg=Avg('priority_score'))['avg'] or 0
    
    # Calculate waitlist trend
    this_month_waitlist = WaitlistEntry.objects.filter(
        created_at__date__gte=month_ago.date()
    ).filter(site_filter_q).count()
    last_month_waitlist = WaitlistEntry.objects.filter(
        created_at__date__gte=last_month_start.date(),
        created_at__date__lt=month_ago.date()
    ).filter(site_filter_q).count()
    waitlist_trend = 0
    if last_month_waitlist > 0:
        waitlist_trend = round(((this_month_waitlist - last_month_waitlist) / last_month_waitlist) * 100, 1)
    
    # Leads stats
    total_leads = Lead.objects.filter(site_filter_q).count()
    qualified_leads = Lead.objects.filter(status='qualified').filter(site_filter_q).count()
    converted_leads = Lead.objects.filter(status='converted').filter(site_filter_q).count()
    conversion_rate = 0
    if total_leads > 0:
        conversion_rate = round((converted_leads / total_leads) * 100, 1)
    
    # Calculate leads trend
    this_month_leads = Lead.objects.filter(
        created_at__date__gte=month_ago.date()
    ).filter(site_filter_q).count()
    last_month_leads = Lead.objects.filter(
        created_at__date__gte=last_month_start.date(),
        created_at__date__lt=month_ago.date()
    ).filter(site_filter_q).count()
    leads_trend = 0
    if last_month_leads > 0:
        leads_trend = round(((this_month_leads - last_month_leads) / last_month_leads) * 100, 1)
    
    # Newsletter stats
    total_newsletter = NewsletterSubscription.objects.filter(site_filter_q).count()
    active_newsletter = NewsletterSubscription.objects.filter(
        subscription_status='subscribed'
    ).filter(site_filter_q).count()
    unsubscribed_newsletter = NewsletterSubscription.objects.filter(
        subscription_status='unsubscribed'
    ).filter(site_filter_q).count()
    
    # Calculate newsletter growth rate
    this_month_newsletter = NewsletterSubscription.objects.filter(
        subscription_status='subscribed',
        created_at__date__gte=month_ago.date()
    ).filter(site_filter_q).count()
    last_month_newsletter = NewsletterSubscription.objects.filter(
        subscription_status='subscribed',
        created_at__date__gte=last_month_start.date(),
        created_at__date__lt=month_ago.date()
    ).filter(site_filter_q).count()
    newsletter_growth_rate = 0
    if last_month_newsletter > 0:
        newsletter_growth_rate = round(((this_month_newsletter - last_month_newsletter) / last_month_newsletter) * 100, 1)
    
    response_data = {
        'contacts': {
            'total': total_contacts,
            'new': new_contacts,
            'pending': pending_contacts,
            'trend': contacts_trend,
        },
        'waitlist': {
            'total': total_waitlist,
            'pending': pending_waitlist,
            'avgScore': round(avg_score, 1),
            'trend': waitlist_trend,
        },
        'leads': {
            'total': total_leads,
            'qualified': qualified_leads,
            'conversionRate': conversion_rate,
            'trend': leads_trend,
        },
        'newsletter': {
            'total': total_newsletter,
            'active': active_newsletter,
            'unsubscribes': unsubscribed_newsletter,
            'growthRate': newsletter_growth_rate,
        },
    }
    
    # Include site info if filtered
    if site:
        response_data['site'] = {
            'id': str(site.id),
            'name': site.name,
            'domain': site.domain,
            'display_name': site.display_name,
        }
    
    return Response(response_data, status=200)

