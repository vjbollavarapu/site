"""
Enhanced Django admin for WaitlistEntry
"""
import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.urls import reverse
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django_admin_listfilter_dropdown.filters import DropdownFilter
from .models import WaitlistEntry
from apps.integrations.email_service import EmailService


class WaitlistEntryResource(resources.ModelResource):
    """Resource for import/export"""
    class Meta:
        model = WaitlistEntry
        fields = ('id', 'email', 'name', 'company', 'role', 'company_size', 'industry',
                  'status', 'priority_score', 'source', 'is_verified', 'created_at')
        export_order = fields


@admin.register(WaitlistEntry)
class WaitlistEntryAdmin(ImportExportModelAdmin):
    """Enhanced admin for WaitlistEntry"""
    resource_class = WaitlistEntryResource
    
    list_display = ['email', 'name', 'company', 'status_badge', 'priority_score', 
                    'company_size', 'industry', 'verified_badge', 'created_at', 'actions_column']
    list_filter = [
        ('status', DropdownFilter),
        ('company_size', DropdownFilter),
        ('industry', DropdownFilter),
        ('source', DropdownFilter),
        ('is_verified', DropdownFilter),
        ('marketing_consent', DropdownFilter),
        'created_at',
    ]
    search_fields = ['email', 'name', 'company', 'role', 'referral_code', 'invite_code']
    readonly_fields = ['id', 'created_at', 'updated_at', 'verification_token', 
                      'priority_score', 'invited_at']
    date_hierarchy = 'created_at'
    list_per_page = 50
    list_select_related = ['invited_by']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('email', 'name', 'company', 'role')
        }),
        ('Company Details', {
            'fields': ('company_size', 'industry', 'use_case')
        }),
        ('Source & Referral', {
            'fields': ('source', 'referral_code')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority_score')
        }),
        ('Invitation', {
            'fields': ('invited_at', 'invited_by', 'invite_code', 'expected_start_date'),
            'classes': ('collapse',)
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_at', 'verification_token'),
            'classes': ('collapse',)
        }),
        ('Consent', {
            'fields': ('marketing_consent', 'consent_timestamp'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Internal Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'approve_entries',
        'reject_entries',
        'send_invitations',
        'mark_onboarded',
        'export_to_csv',
        'send_verification_emails',
    ]
    
    def status_badge(self, obj):
        """Display status with badge"""
        colors = {
            'pending': 'gray',
            'approved': 'blue',
            'invited': 'orange',
            'onboarded': 'green',
            'rejected': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def verified_badge(self, obj):
        """Display verification status"""
        if obj.is_verified:
            return format_html('<span style="color: green;">✓ Verified</span>')
        return format_html('<span style="color: orange;">⚠ Not Verified</span>')
    verified_badge.short_description = 'Verified'
    
    def actions_column(self, obj):
        """Quick action links"""
        return format_html(
            '<a href="{}" class="button">View</a>',
            reverse('admin:waitlist_waitlistentry_change', args=[obj.pk])
        )
    actions_column.short_description = 'Actions'
    
    # Custom Actions
    def approve_entries(self, request, queryset):
        """Approve selected entries"""
        count = 0
        for entry in queryset:
            entry.approve()
            count += 1
        self.message_user(request, f'{count} entries approved.')
    approve_entries.short_description = "Approve selected entries"
    
    def reject_entries(self, request, queryset):
        """Reject selected entries"""
        count = queryset.update(status='rejected')
        self.message_user(request, f'{count} entries rejected.')
    reject_entries.short_description = "Reject selected entries"
    
    def send_invitations(self, request, queryset):
        """Send invitations to selected entries"""
        count = 0
        email_service = EmailService()
        for entry in queryset:
            if entry.status in ['pending', 'approved']:
                try:
                    entry.send_invitation(user=request.user)
                    count += 1
                except Exception as e:
                    self.message_user(request, f'Error sending invitation to {entry.email}: {str(e)}', level='error')
        self.message_user(request, f'Invitations sent to {count} entries.')
    send_invitations.short_description = "Send invitations to selected entries"
    
    def mark_onboarded(self, request, queryset):
        """Mark selected entries as onboarded"""
        count = 0
        for entry in queryset:
            entry.mark_onboarded()
            count += 1
        self.message_user(request, f'{count} entries marked as onboarded.')
    mark_onboarded.short_description = "Mark selected entries as onboarded"
    
    def export_to_csv(self, request, queryset):
        """Export selected entries to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="waitlist_entries.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Email', 'Name', 'Company', 'Role', 'Company Size', 'Industry',
                        'Status', 'Priority Score', 'Source', 'Verified', 'Created At'])
        
        for entry in queryset:
            writer.writerow([
                entry.email,
                entry.name or '',
                entry.company or '',
                entry.role or '',
                entry.get_company_size_display() if entry.company_size else '',
                entry.get_industry_display() if entry.industry else '',
                entry.get_status_display(),
                entry.priority_score,
                entry.get_source_display(),
                'Yes' if entry.is_verified else 'No',
                entry.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        
        return response
    export_to_csv.short_description = "Export to CSV"
    
    def send_verification_emails(self, request, queryset):
        """Send verification emails to selected entries"""
        count = 0
        email_service = EmailService()
        for entry in queryset:
            if not entry.is_verified:
                try:
                    email_service.send_waitlist_verification(entry)
                    count += 1
                except Exception as e:
                    self.message_user(request, f'Error sending verification to {entry.email}: {str(e)}', level='error')
        self.message_user(request, f'Verification emails sent to {count} entries.')
    send_verification_emails.short_description = "Send verification emails"
