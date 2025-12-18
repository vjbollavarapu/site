"""
Enhanced Django admin for ContactSubmission
"""
import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.urls import reverse
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django_admin_listfilter_dropdown.filters import DropdownFilter
from .models import ContactSubmission
from apps.integrations.email_service import EmailService


class ContactSubmissionResource(resources.ModelResource):
    """Resource for import/export"""
    class Meta:
        model = ContactSubmission
        fields = ('id', 'name', 'email', 'phone', 'company', 'subject', 'message', 
                  'status', 'priority', 'is_spam', 'spam_score', 'created_at')
        export_order = fields


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(ImportExportModelAdmin):
    """Enhanced admin for ContactSubmission"""
    resource_class = ContactSubmissionResource
    
    list_display = ['name', 'email', 'subject', 'status_badge', 'priority_badge', 
                    'spam_indicator', 'created_at', 'actions_column']
    list_filter = [
        ('status', DropdownFilter),
        ('priority', DropdownFilter),
        ('is_spam', DropdownFilter),
        ('source', DropdownFilter),
        'created_at',
        'contacted_at',
    ]
    search_fields = ['name', 'email', 'subject', 'message', 'company', 'phone']
    readonly_fields = ['id', 'created_at', 'updated_at', 'contacted_at', 'resolved_at', 
                      'spam_score', 'ip_address', 'user_agent']
    date_hierarchy = 'created_at'
    list_per_page = 50
    list_select_related = ['assigned_to']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'company')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'assigned_to')
        }),
        ('Metadata', {
            'fields': ('source', 'referrer', 'user_agent', 'ip_address'),
            'classes': ('collapse',)
        }),
        ('Spam Detection', {
            'fields': ('is_spam', 'spam_score'),
            'classes': ('collapse',)
        }),
        ('GDPR', {
            'fields': ('consent_given', 'consent_timestamp'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'contacted_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
        ('Additional', {
            'fields': ('custom_data',),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'mark_as_contacted',
        'mark_as_resolved',
        'mark_as_spam',
        'mark_as_not_spam',
        'export_to_csv',
        'send_confirmation_emails',
        'bulk_assign',
    ]
    
    def status_badge(self, obj):
        """Display status with badge"""
        colors = {
            'new': 'blue',
            'contacted': 'orange',
            'resolved': 'green',
            'archived': 'gray',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def priority_badge(self, obj):
        """Display priority with badge"""
        colors = {
            'low': 'green',
            'medium': 'orange',
            'high': 'red',
            'urgent': 'darkred',
        }
        color = colors.get(obj.priority, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def spam_indicator(self, obj):
        """Display spam indicator"""
        if obj.is_spam:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠ SPAM</span>'
            )
        elif obj.spam_score and obj.spam_score > 0.5:
            return format_html(
                '<span style="color: orange;">⚠ Score: {}</span>',
                obj.spam_score
            )
        return format_html('<span style="color: green;">✓</span>')
    spam_indicator.short_description = 'Spam'
    
    def actions_column(self, obj):
        """Quick action links"""
        return format_html(
            '<a href="{}" class="button">View</a>',
            reverse('admin:contacts_contactsubmission_change', args=[obj.pk])
        )
    actions_column.short_description = 'Actions'
    
    # Custom Actions
    def mark_as_contacted(self, request, queryset):
        """Mark selected submissions as contacted"""
        count = 0
        for submission in queryset:
            submission.mark_as_contacted()
            count += 1
        self.message_user(request, f'{count} submissions marked as contacted.')
    mark_as_contacted.short_description = "Mark as contacted"
    
    def mark_as_resolved(self, request, queryset):
        """Mark selected submissions as resolved"""
        count = 0
        for submission in queryset:
            submission.mark_as_resolved()
            count += 1
        self.message_user(request, f'{count} submissions marked as resolved.')
    mark_as_resolved.short_description = "Mark as resolved"
    
    def mark_as_spam(self, request, queryset):
        """Mark selected submissions as spam"""
        count = queryset.update(is_spam=True)
        self.message_user(request, f'{count} submissions marked as spam.')
    mark_as_spam.short_description = "Mark as spam"
    
    def mark_as_not_spam(self, request, queryset):
        """Mark selected submissions as not spam"""
        count = queryset.update(is_spam=False)
        self.message_user(request, f'{count} submissions marked as not spam.')
    mark_as_not_spam.short_description = "Mark as not spam"
    
    def export_to_csv(self, request, queryset):
        """Export selected submissions to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="contact_submissions.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'Phone', 'Company', 'Subject', 'Message', 
                        'Status', 'Priority', 'Created At'])
        
        for submission in queryset:
            writer.writerow([
                submission.name,
                submission.email,
                submission.phone or '',
                submission.company or '',
                submission.subject,
                submission.message[:200],  # Truncate long messages
                submission.get_status_display(),
                submission.get_priority_display(),
                submission.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        
        return response
    export_to_csv.short_description = "Export to CSV"
    
    def send_confirmation_emails(self, request, queryset):
        """Send confirmation emails to selected submissions"""
        count = 0
        email_service = EmailService()
        for submission in queryset:
            if not submission.is_spam:
                try:
                    email_service.send_contact_confirmation(submission)
                    count += 1
                except Exception as e:
                    self.message_user(request, f'Error sending email to {submission.email}: {str(e)}', level='error')
        self.message_user(request, f'Confirmation emails sent to {count} submissions.')
    send_confirmation_emails.short_description = "Send confirmation emails"
    
    def bulk_assign(self, request, queryset):
        """Bulk assign submissions to current user"""
        count = queryset.update(assigned_to=request.user)
        self.message_user(request, f'{count} submissions assigned to you.')
    bulk_assign.short_description = "Assign to me"
