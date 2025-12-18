"""
Custom Django admin configuration with enhanced dashboard
"""
from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate, TruncDay
from django.utils import timezone
from django.utils.html import format_html
from datetime import timedelta
import json


class CustomAdminSite(admin.AdminSite):
    """Custom admin site with dashboard"""
    site_header = "Site Backend Administration"
    site_title = "Site Backend Admin"
    index_title = "Dashboard"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard), name='admin_dashboard'),
        ]
        return custom_urls + urls
    
    def dashboard(self, request):
        """Custom admin dashboard with statistics and charts"""
        # Get date ranges
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Import models
        from apps.contacts.models import ContactSubmission
        from apps.waitlist.models import WaitlistEntry
        from apps.leads.models import Lead
        from apps.newsletter.models import NewsletterSubscription
        from apps.analytics.models import PageView, Event, Conversion
        
        # Today's submissions
        todays_submissions = {
            'contacts': ContactSubmission.objects.filter(created_at__date=today).count(),
            'waitlist': WaitlistEntry.objects.filter(created_at__date=today).count(),
            'leads': Lead.objects.filter(created_at__date=today).count(),
            'newsletter': NewsletterSubscription.objects.filter(created_at__date=today).count(),
        }
        
        # Pending items count
        pending_items = {
            'contacts': ContactSubmission.objects.filter(status='new').count(),
            'waitlist': WaitlistEntry.objects.filter(status='pending').count(),
            'leads': Lead.objects.filter(status='new').count(),
            'total': (
                ContactSubmission.objects.filter(status='new').count() +
                WaitlistEntry.objects.filter(status='pending').count() +
                Lead.objects.filter(status='new').count()
            ),
        }
        
        # Conversion statistics
        conversion_stats = {
            'total_conversions': Conversion.objects.count(),
            'conversions_today': Conversion.objects.filter(timestamp__date=today).count(),
            'conversions_week': Conversion.objects.filter(timestamp__date__gte=week_ago).count(),
            'conversion_value_today': Conversion.objects.filter(timestamp__date=today).aggregate(
                total=Sum('value')
            )['total'] or 0,
            'conversion_value_week': Conversion.objects.filter(timestamp__date__gte=week_ago).aggregate(
                total=Sum('value')
            )['total'] or 0,
            'lead_conversion_rate': 0,
        }
        
        # Calculate lead conversion rate
        total_leads = Lead.objects.count()
        converted_leads = Lead.objects.filter(status='converted').count()
        if total_leads > 0:
            conversion_stats['lead_conversion_rate'] = round((converted_leads / total_leads) * 100, 2)
        
        # Top sources
        top_sources = {
            'contacts': list(
                ContactSubmission.objects.exclude(source__isnull=True)
                .values('source')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
            ),
            'waitlist': list(
                WaitlistEntry.objects.values('source')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
            ),
            'leads': list(
                Lead.objects.values('lead_source')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
            ),
            'newsletter': list(
                NewsletterSubscription.objects.values('source')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
            ),
        }
        
        # Recent activity feed (last 20 items)
        recent_activities = []
        
        # Recent contacts
        for contact in ContactSubmission.objects.order_by('-created_at')[:5]:
            recent_activities.append({
                'type': 'contact',
                'title': f"New contact: {contact.name}",
                'subtitle': contact.email,
                'status': contact.status,
                'timestamp': contact.created_at,
                'url': reverse('admin:contacts_contactsubmission_change', args=[contact.pk]),
            })
        
        # Recent waitlist entries
        for entry in WaitlistEntry.objects.order_by('-created_at')[:5]:
            recent_activities.append({
                'type': 'waitlist',
                'title': f"New waitlist entry: {entry.email}",
                'subtitle': entry.name or entry.company or '',
                'status': entry.status,
                'timestamp': entry.created_at,
                'url': reverse('admin:waitlist_waitlistentry_change', args=[entry.pk]),
            })
        
        # Recent leads
        for lead in Lead.objects.order_by('-created_at')[:5]:
            recent_activities.append({
                'type': 'lead',
                'title': f"New lead: {lead.first_name} {lead.last_name}",
                'subtitle': lead.email,
                'status': lead.status,
                'timestamp': lead.created_at,
                'url': reverse('admin:leads_lead_change', args=[lead.pk]),
            })
        
        # Recent conversions
        for conversion in Conversion.objects.order_by('-timestamp')[:5]:
            recent_activities.append({
                'type': 'conversion',
                'title': f"Conversion: {conversion.get_conversion_type_display()}",
                'subtitle': f"Value: ${conversion.value or 0}",
                'status': 'converted',
                'timestamp': conversion.timestamp,
                'url': reverse('admin:analytics_conversion_change', args=[conversion.pk]),
            })
        
        # Sort by timestamp and take most recent 20
        recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
        recent_activities = recent_activities[:20]
        
        # Submission trends (last 30 days) - for line chart
        submission_trends = []
        for i in range(30):
            date = today - timedelta(days=29-i)
            submission_trends.append({
                'date': date.strftime('%Y-%m-%d'),
                'contacts': ContactSubmission.objects.filter(created_at__date=date).count(),
                'waitlist': WaitlistEntry.objects.filter(created_at__date=date).count(),
                'leads': Lead.objects.filter(created_at__date=date).count(),
            })
        
        # Source distribution - for pie chart
        source_distribution = {}
        all_sources = []
        
        # Aggregate all sources
        for source_data in top_sources['waitlist']:
            source = source_data['source']
            count = source_data['count']
            if source not in source_distribution:
                source_distribution[source] = 0
            source_distribution[source] += count
        
        for source_data in top_sources['leads']:
            source = source_data['lead_source']
            count = source_data['count']
            if source not in source_distribution:
                source_distribution[source] = 0
            source_distribution[source] += count
        
        for source_data in top_sources['newsletter']:
            source = source_data['source']
            count = source_data['count']
            if source not in source_distribution:
                source_distribution[source] = 0
            source_distribution[source] += count
        
        # Status breakdown - for bar chart
        contact_statuses = {
            item['status']: item['count']
            for item in ContactSubmission.objects.values('status').annotate(count=Count('id'))
        }
        waitlist_statuses = {
            item['status']: item['count']
            for item in WaitlistEntry.objects.values('status').annotate(count=Count('id'))
        }
        lead_statuses = {
            item['status']: item['count']
            for item in Lead.objects.values('status').annotate(count=Count('id'))
        }
        
        status_breakdown = {
            'contacts': contact_statuses,
            'waitlist': waitlist_statuses,
            'leads': lead_statuses,
        }
        
        # Growth metrics (week over week)
        this_week_count = (
            ContactSubmission.objects.filter(created_at__date__gte=week_ago).count() +
            WaitlistEntry.objects.filter(created_at__date__gte=week_ago).count() +
            Lead.objects.filter(created_at__date__gte=week_ago).count()
        )
        last_week_count = (
            ContactSubmission.objects.filter(
                created_at__date__gte=week_ago - timedelta(days=7),
                created_at__date__lt=week_ago
            ).count() +
            WaitlistEntry.objects.filter(
                created_at__date__gte=week_ago - timedelta(days=7),
                created_at__date__lt=week_ago
            ).count() +
            Lead.objects.filter(
                created_at__date__gte=week_ago - timedelta(days=7),
                created_at__date__lt=week_ago
            ).count()
        )
        
        growth_rate = 0
        if last_week_count > 0:
            growth_rate = round(((this_week_count - last_week_count) / last_week_count) * 100, 2)
        
        # Overall stats
        contact_stats = {
            'total': ContactSubmission.objects.count(),
            'new': ContactSubmission.objects.filter(status='new').count(),
            'this_week': ContactSubmission.objects.filter(created_at__date__gte=week_ago).count(),
            'this_month': ContactSubmission.objects.filter(created_at__date__gte=month_ago).count(),
            'spam': ContactSubmission.objects.filter(is_spam=True).count(),
        }
        
        waitlist_stats = {
            'total': WaitlistEntry.objects.count(),
            'pending': WaitlistEntry.objects.filter(status='pending').count(),
            'approved': WaitlistEntry.objects.filter(status='approved').count(),
            'onboarded': WaitlistEntry.objects.filter(status='onboarded').count(),
            'this_week': WaitlistEntry.objects.filter(created_at__date__gte=week_ago).count(),
        }
        
        lead_stats = {
            'total': Lead.objects.count(),
            'new': Lead.objects.filter(status='new').count(),
            'qualified': Lead.objects.filter(status='qualified').count(),
            'converted': Lead.objects.filter(status='converted').count(),
            'this_week': Lead.objects.filter(created_at__date__gte=week_ago).count(),
        }
        
        newsletter_stats = {
            'total': NewsletterSubscription.objects.count(),
            'subscribed': NewsletterSubscription.objects.filter(subscription_status='subscribed').count(),
            'unsubscribed': NewsletterSubscription.objects.filter(subscription_status='unsubscribed').count(),
            'this_week': NewsletterSubscription.objects.filter(created_at__date__gte=week_ago).count(),
        }
        
        analytics_stats = {
            'pageviews_today': PageView.objects.filter(timestamp__date=today).count(),
            'pageviews_week': PageView.objects.filter(timestamp__date__gte=week_ago).count(),
            'events_today': Event.objects.filter(timestamp__date=today).count(),
            'conversions_today': Conversion.objects.filter(timestamp__date=today).count(),
            'unique_sessions_week': PageView.objects.filter(timestamp__date__gte=week_ago).values('session_id').distinct().count(),
        }
        
        context = {
            **self.each_context(request),
            'contact_stats': contact_stats,
            'waitlist_stats': waitlist_stats,
            'lead_stats': lead_stats,
            'newsletter_stats': newsletter_stats,
            'analytics_stats': analytics_stats,
            'todays_submissions': todays_submissions,
            'pending_items': pending_items,
            'conversion_stats': conversion_stats,
            'top_sources': top_sources,
            'recent_activities': recent_activities,
            'submission_trends': json.dumps(submission_trends),
            'source_distribution': json.dumps(source_distribution),
            'status_breakdown': json.dumps(status_breakdown),
            'growth_rate': growth_rate,
            'this_week_count': this_week_count,
            'last_week_count': last_week_count,
        }
        
        # Add admin context
        from django.contrib.admin import AdminSite
        context.update(AdminSite().each_context(request))
        return render(request, 'admin/dashboard.html', context)


# Override default admin site index
def admin_index_override(request):
    """Override admin index to show custom dashboard"""
    custom_site = CustomAdminSite(name='admin')
    return custom_site.dashboard(request)

# Monkey patch admin.site.index to use our dashboard
admin.site.index = admin_index_override
