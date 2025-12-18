"""
GDPR admin configuration
"""
from django.contrib import admin
from django.utils.html import format_html
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django_admin_listfilter_dropdown.filters import DropdownFilter
from .models import Consent, PrivacyPolicy, DataRetentionPolicy, DataDeletionAudit


class ConsentResource(resources.ModelResource):
    """Resource for import/export"""
    class Meta:
        model = Consent
        fields = ('id', 'email', 'consent_type', 'consent_given', 'consent_timestamp',
                  'withdrawal_timestamp', 'privacy_policy', 'created_at')
        export_order = fields


class PrivacyPolicyResource(resources.ModelResource):
    """Resource for import/export"""
    class Meta:
        model = PrivacyPolicy
        fields = ('id', 'version', 'title', 'is_active', 'effective_date', 'created_at')
        export_order = fields


@admin.register(Consent)
class ConsentAdmin(ImportExportModelAdmin):
    """Enhanced admin for Consent"""
    resource_class = ConsentResource
    
    list_display = ['email', 'consent_type_badge', 'consent_status', 'consent_timestamp',
                    'privacy_policy_version', 'created_at']
    list_filter = [
        ('consent_type', DropdownFilter),
        ('consent_given', DropdownFilter),
        ('privacy_policy', DropdownFilter),
        'consent_timestamp',
        'created_at',
    ]
    search_fields = ['email', 'consent_text', 'withdrawal_reason']
    readonly_fields = ['id', 'created_at', 'updated_at', 'ip_address_hash']
    date_hierarchy = 'consent_timestamp'
    list_per_page = 50
    
    fieldsets = (
        ('User Information', {
            'fields': ('email', 'ip_address_hash', 'user_agent', 'source')
        }),
        ('Consent Details', {
            'fields': ('consent_type', 'consent_given', 'consent_timestamp', 'consent_text')
        }),
        ('Withdrawal', {
            'fields': ('withdrawal_timestamp', 'withdrawal_reason')
        }),
        ('Privacy Policy', {
            'fields': ('privacy_policy',)
        }),
        ('Metadata', {
            'fields': ('metadata',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def consent_type_badge(self, obj):
        """Display consent type with badge"""
        colors = {
            'marketing': 'blue',
            'analytics': 'green',
            'necessary': 'gray',
            'functional': 'orange',
            'advertising': 'purple',
        }
        color = colors.get(obj.consent_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_consent_type_display()
        )
    consent_type_badge.short_description = 'Type'
    
    def consent_status(self, obj):
        """Display consent status"""
        if obj.consent_given:
            return format_html('<span style="color: green;">✓ Given</span>')
        elif obj.withdrawal_timestamp:
            return format_html('<span style="color: red;">✗ Withdrawn</span>')
        return format_html('<span style="color: gray;">—</span>')
    consent_status.short_description = 'Status'
    
    def privacy_policy_version(self, obj):
        """Display privacy policy version"""
        if obj.privacy_policy:
            return obj.privacy_policy.version
        return '-'
    privacy_policy_version.short_description = 'Policy Version'


@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(ImportExportModelAdmin):
    """Enhanced admin for PrivacyPolicy"""
    resource_class = PrivacyPolicyResource
    
    list_display = ['version', 'title', 'active_badge', 'effective_date', 'created_at']
    list_filter = [
        ('is_active', DropdownFilter),
        'effective_date',
        'created_at',
    ]
    search_fields = ['version', 'title', 'content']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'effective_date'
    
    fieldsets = (
        ('Policy Information', {
            'fields': ('version', 'title', 'content')
        }),
        ('Status', {
            'fields': ('is_active', 'effective_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def active_badge(self, obj):
        """Display active status"""
        if obj.is_active:
            return format_html('<span style="color: green; font-weight: bold;">✓ Active</span>')
        return format_html('<span style="color: gray;">Inactive</span>')
    active_badge.short_description = 'Status'


@admin.register(DataRetentionPolicy)
class DataRetentionPolicyAdmin(ImportExportModelAdmin):
    """Enhanced admin for DataRetentionPolicy"""
    
    list_display = ['data_type', 'retention_days', 'action_badge', 'active_badge', 'created_at']
    list_filter = [
        ('data_type', DropdownFilter),
        ('is_active', DropdownFilter),
        ('auto_delete', DropdownFilter),
        ('anonymize_instead', DropdownFilter),
    ]
    search_fields = ['data_type']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Policy Configuration', {
            'fields': ('data_type', 'retention_days', 'is_active')
        }),
        ('Action Settings', {
            'fields': ('auto_delete', 'anonymize_instead')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def action_badge(self, obj):
        """Display action type"""
        if obj.anonymize_instead:
            return format_html('<span style="background-color: orange; color: white; padding: 3px 8px; border-radius: 3px;">Anonymize</span>')
        elif obj.auto_delete:
            return format_html('<span style="background-color: red; color: white; padding: 3px 8px; border-radius: 3px;">Delete</span>')
        return format_html('<span style="color: gray;">Manual</span>')
    action_badge.short_description = 'Action'
    
    def active_badge(self, obj):
        """Display active status"""
        if obj.is_active:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: gray;">✗</span>')
    active_badge.short_description = 'Active'


@admin.register(DataDeletionAudit)
class DataDeletionAuditAdmin(admin.ModelAdmin):
    """Enhanced admin for DataDeletionAudit"""
    
    list_display = ['email', 'deletion_type_badge', 'data_types_count', 'deleted_by',
                    'deletion_timestamp', 'confirmed_badge']
    list_filter = [
        ('deletion_type', DropdownFilter),
        'deletion_timestamp',
    ]
    search_fields = ['email', 'deleted_by']
    readonly_fields = ['id', 'deletion_timestamp']
    date_hierarchy = 'deletion_timestamp'
    
    fieldsets = (
        ('Deletion Information', {
            'fields': ('email', 'deletion_type', 'data_types_deleted')
        }),
        ('Audit Details', {
            'fields': ('deleted_by', 'ip_address_hash', 'deletion_timestamp')
        }),
        ('Confirmation', {
            'fields': ('confirmation_token', 'confirmed_at')
        }),
        ('Metadata', {
            'fields': ('metadata',)
        }),
    )
    
    def deletion_type_badge(self, obj):
        """Display deletion type"""
        colors = {
            'full': 'red',
            'anonymize': 'orange',
            'partial': 'yellow',
        }
        color = colors.get(obj.deletion_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_deletion_type_display()
        )
    deletion_type_badge.short_description = 'Type'
    
    def data_types_count(self, obj):
        """Display count of data types deleted"""
        count = len(obj.data_types_deleted) if obj.data_types_deleted else 0
        return count
    data_types_count.short_description = 'Data Types'
    
    def confirmed_badge(self, obj):
        """Display confirmation status"""
        if obj.confirmed_at:
            return format_html('<span style="color: green;">✓ Confirmed</span>')
        return format_html('<span style="color: orange;">⚠ Pending</span>')
    confirmed_badge.short_description = 'Confirmed'
