from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import connection
from django.utils import timezone
from apps.leads.models import Lead
from apps.contacts.models import ContactSubmission
from apps.waitlist.models import WaitlistEntry
from apps.newsletter.models import NewsletterSubscription


@login_required
def dashboard(request):
    """Dashboard view showing overview statistics"""
    total_leads = Lead.objects.count()
    new_leads = Lead.objects.filter(status='new').count()
    qualified_leads = Lead.objects.filter(status='qualified').count()
    converted_leads = Lead.objects.filter(status='converted').count()
    
    total_contacts = ContactSubmission.objects.filter(is_spam=False).count()
    new_contacts = ContactSubmission.objects.filter(status='new', is_spam=False).count()
    resolved_contacts = ContactSubmission.objects.filter(status='resolved', is_spam=False).count()
    
    total_waitlist = WaitlistEntry.objects.count()
    pending_waitlist = WaitlistEntry.objects.filter(status='pending').count()
    approved_waitlist = WaitlistEntry.objects.filter(status='approved').count()
    onboarded_waitlist = WaitlistEntry.objects.filter(status='onboarded').count()
    
    total_newsletter = NewsletterSubscription.objects.count()
    subscribed_newsletter = NewsletterSubscription.objects.filter(subscription_status='subscribed').count()
    unsubscribed_newsletter = NewsletterSubscription.objects.filter(subscription_status='unsubscribed').count()
    bounced_newsletter = NewsletterSubscription.objects.filter(subscription_status='bounced').count()
    
    recent_leads = Lead.objects.all()[:5]
    recent_contacts = ContactSubmission.objects.filter(is_spam=False)[:5]
    recent_waitlist = WaitlistEntry.objects.all()[:5]
    recent_newsletter = NewsletterSubscription.objects.filter(subscription_status='subscribed')[:5]
    
    context = {
        'total_leads': total_leads,
        'new_leads': new_leads,
        'qualified_leads': qualified_leads,
        'converted_leads': converted_leads,
        'total_contacts': total_contacts,
        'new_contacts': new_contacts,
        'resolved_contacts': resolved_contacts,
        'total_waitlist': total_waitlist,
        'pending_waitlist': pending_waitlist,
        'approved_waitlist': approved_waitlist,
        'onboarded_waitlist': onboarded_waitlist,
        'total_newsletter': total_newsletter,
        'subscribed_newsletter': subscribed_newsletter,
        'unsubscribed_newsletter': unsubscribed_newsletter,
        'bounced_newsletter': bounced_newsletter,
        'recent_leads': recent_leads,
        'recent_contacts': recent_contacts,
        'recent_waitlist': recent_waitlist,
        'recent_newsletter': recent_newsletter,
    }
    
    return render(request, 'dashboard.html', context)


def health_check(request):
    """
    Health check endpoint for monitoring and load balancers.
    Returns 200 OK if the application is healthy.
    """
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': timezone.now().isoformat()
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=503)


def early_access_alias(request):
    """
    API v1 alias for waitlist join endpoint.
    Redirects to the waitlist join endpoint for backward compatibility.
    """
    from apps.waitlist.api_views import join_waitlist
    return join_waitlist(request)


def early_access_alias(request):
    """
    API v1 alias for waitlist join endpoint.
    Redirects to the waitlist join endpoint for backward compatibility.
    """
    from apps.waitlist.api_views import join_waitlist
    return join_waitlist(request)

