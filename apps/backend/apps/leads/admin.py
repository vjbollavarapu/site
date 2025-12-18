"""
Enhanced Django admin for Lead
"""
import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.urls import reverse
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django_admin_listfilter_dropdown.filters import DropdownFilter
from .models import Lead


class LeadResource(resources.ModelResource):
    """Resource for import/export"""
    class Meta:
        model = Lead
        fields = ('id', 'first_name', 'last_name', 'email', 'phone', 'company',
                  'lead_source', 'lead_score', 'status', 'lifecycle_stage', 'created_at')
        export_order = fields


@admin.register(Lead)
class LeadAdmin(ImportExportModelAdmin):
    """Enhanced admin for Lead"""
    resource_class = LeadResource
    
    list_display = ['full_name', 'email', 'company', 'lead_source_badge', 'status_badge',
                    'lead_score', 'lifecycle_stage', 'created_at', 'actions_column']
    list_filter = [
        ('status', DropdownFilter),
        ('lifecycle_stage', DropdownFilter),
        ('lead_source', DropdownFilter),
        ('industry', DropdownFilter),
        ('company_size', DropdownFilter),
        'created_at',
    ]
    search_fields = ['first_name', 'last_name', 'email', 'company', 'job_title', 'phone']
    readonly_fields = ['id', 'created_at', 'updated_at', 'lead_score', 'last_contacted_at', 'converted_at']
    date_hierarchy = 'created_at'
    list_per_page = 50
    list_select_related = ['assigned_to']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'company')
        }),
        ('Lead Details', {
            'fields': ('lead_source', 'lead_score', 'industry', 'job_title', 'company_size')
        }),
        ('Status & Assignment', {
            'fields': ('status', 'lifecycle_stage', 'assigned_to', 'assigned_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_contacted_at', 'converted_at'),
            'classes': ('collapse',)
        }),
        ('Additional', {
            'fields': ('custom_data', 'tags'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'qualify_leads',
        'convert_leads',
        'export_to_csv',
        'bulk_assign',
    ]
    
    def full_name(self, obj):
        """Display full name"""
        return f"{obj.first_name} {obj.last_name}".strip()
    full_name.short_description = 'Name'
    
    def lead_source_badge(self, obj):
        """Display lead source with badge"""
        return format_html(
            '<span style="background-color: #007bff; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            obj.get_lead_source_display() if obj.lead_source else 'Unknown'
        )
    lead_source_badge.short_description = 'Source'
    
    def status_badge(self, obj):
        """Display status with badge"""
        colors = {
            'new': 'blue',
            'contacted': 'orange',
            'qualified': 'green',
            'converted': 'darkgreen',
            'lost': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def actions_column(self, obj):
        """Quick action links"""
        return format_html(
            '<a href="{}" class="button">View</a>',
            reverse('admin:leads_lead_change', args=[obj.pk])
        )
    actions_column.short_description = 'Actions'
    
    # Custom Actions
    def qualify_leads(self, request, queryset):
        """Qualify selected leads"""
        count = 0
        for lead in queryset:
            lead.qualify()
            count += 1
        self.message_user(request, f'{count} leads qualified.')
    qualify_leads.short_description = "Qualify selected leads"
    
    def convert_leads(self, request, queryset):
        """Convert selected leads"""
        count = 0
        for lead in queryset:
            lead.convert()
            count += 1
        self.message_user(request, f'{count} leads converted.')
    convert_leads.short_description = "Convert selected leads"
    
    def export_to_csv(self, request, queryset):
        """Export selected leads to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="leads.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['First Name', 'Last Name', 'Email', 'Phone', 'Company',
                        'Lead Source', 'Lead Score', 'Status', 'Lifecycle Stage', 'Created At'])
        
        for lead in queryset:
            writer.writerow([
                lead.first_name,
                lead.last_name,
                lead.email,
                lead.phone or '',
                lead.company or '',
                lead.get_lead_source_display() if lead.lead_source else '',
                lead.lead_score,
                lead.get_status_display(),
                lead.get_lifecycle_stage_display() if lead.lifecycle_stage else '',
                lead.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        
        return response
    export_to_csv.short_description = "Export to CSV"
    
    def bulk_assign(self, request, queryset):
        """Bulk assign leads to current user"""
        count = queryset.update(assigned_to=request.user)
        self.message_user(request, f'{count} leads assigned to you.')
    bulk_assign.short_description = "Assign to me"
