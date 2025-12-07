"""
Enhanced Django admin for NewsletterSubscription
"""
import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.urls import reverse
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django_admin_listfilter_dropdown.filters import DropdownFilter
from .models import NewsletterSubscription
from apps.integrations.email_service import EmailService


class NewsletterSubscriptionResource(resources.ModelResource):
    """Resource for import/export"""
    class Meta:
        model = NewsletterSubscription
        fields = ('id', 'email', 'name', 'subscription_status', 'source', 'preference',
                  'is_verified', 'consent_given', 'created_at')
        export_order = fields


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(ImportExportModelAdmin):
    """Enhanced admin for NewsletterSubscription"""
    resource_class = NewsletterSubscriptionResource
    
    list_display = ['email', 'name', 'status_badge', 'source', 'verified_badge',
                    'preference', 'created_at', 'actions_column']
    list_filter = [
        ('subscription_status', DropdownFilter),
        ('source', DropdownFilter),
        ('preference', DropdownFilter),
        ('is_verified', DropdownFilter),
        ('consent_given', DropdownFilter),
        'created_at',
    ]
    search_fields = ['email', 'name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'verification_token', 
                      'unsubscribe_token', 'bounce_count', 'complaint_count']
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    fieldsets = (
        ('Subscriber Information', {
            'fields': ('email', 'name')
        }),
        ('Subscription Details', {
            'fields': ('subscription_status', 'source', 'preference', 'interests')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_at', 'verification_token'),
            'classes': ('collapse',)
        }),
        ('Consent', {
            'fields': ('consent_given', 'consent_timestamp', 'consent_text'),
            'classes': ('collapse',)
        }),
        ('Unsubscribe', {
            'fields': ('unsubscribed_at', 'unsubscribe_reason', 'unsubscribe_token'),
            'classes': ('collapse',)
        }),
        ('Bounce & Complaints', {
            'fields': ('bounce_count', 'last_bounce_at', 'complaint_count', 'last_complaint_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'verify_subscriptions',
        'unsubscribe_selected',
        'resubscribe_selected',
        'export_to_csv',
        'send_welcome_emails',
    ]
    
    def status_badge(self, obj):
        """Display status with badge"""
        colors = {
            'subscribed': 'green',
            'unsubscribed': 'red',
            'bounced': 'orange',
            'complained': 'darkred',
        }
        color = colors.get(obj.subscription_status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_subscription_status_display()
        )
    status_badge.short_description = 'Status'
    
    def verified_badge(self, obj):
        """Display verification status"""
        if obj.is_verified:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: orange;">⚠</span>')
    verified_badge.short_description = 'Verified'
    
    def actions_column(self, obj):
        """Quick action links"""
        return format_html(
            '<a href="{}" class="button">View</a>',
            reverse('admin:newsletter_newslettersubscription_change', args=[obj.pk])
        )
    actions_column.short_description = 'Actions'
    
    # Custom Actions
    def verify_subscriptions(self, request, queryset):
        """Verify selected subscriptions"""
        count = 0
        for subscription in queryset:
            subscription.verify()
            count += 1
        self.message_user(request, f'{count} subscriptions verified.')
    verify_subscriptions.short_description = "Verify selected subscriptions"
    
    def unsubscribe_selected(self, request, queryset):
        """Unsubscribe selected subscriptions"""
        count = 0
        for subscription in queryset:
            subscription.unsubscribe()
            count += 1
        self.message_user(request, f'{count} subscriptions unsubscribed.')
    unsubscribe_selected.short_description = "Unsubscribe selected"
    
    def resubscribe_selected(self, request, queryset):
        """Resubscribe selected subscriptions"""
        count = 0
        for subscription in queryset:
            subscription.subscribe()
            count += 1
        self.message_user(request, f'{count} subscriptions resubscribed.')
    resubscribe_selected.short_description = "Resubscribe selected"
    
    def export_to_csv(self, request, queryset):
        """Export selected subscriptions to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="newsletter_subscriptions.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Email', 'Name', 'Status', 'Source', 'Preference', 
                        'Verified', 'Consent Given', 'Created At'])
        
        for subscription in queryset:
            writer.writerow([
                subscription.email,
                subscription.name or '',
                subscription.get_subscription_status_display(),
                subscription.get_source_display(),
                subscription.get_preference_display(),
                'Yes' if subscription.is_verified else 'No',
                'Yes' if subscription.consent_given else 'No',
                subscription.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        
        return response
    export_to_csv.short_description = "Export to CSV"
    
    def send_welcome_emails(self, request, queryset):
        """Send welcome emails to selected subscriptions"""
        count = 0
        email_service = EmailService()
        for subscription in queryset:
            if subscription.subscription_status == 'subscribed' and subscription.is_verified:
                try:
                    email_service.send_newsletter_welcome(subscription)
                    count += 1
                except Exception as e:
                    self.message_user(request, f'Error sending email to {subscription.email}: {str(e)}', level='error')
        self.message_user(request, f'Welcome emails sent to {count} subscriptions.')
    send_welcome_emails.short_description = "Send welcome emails"
