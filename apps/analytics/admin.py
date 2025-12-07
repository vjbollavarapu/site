"""
Enhanced Django admin for Analytics models
"""
from django.contrib import admin
from django.utils.html import format_html
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django_admin_listfilter_dropdown.filters import DropdownFilter
from .models import PageView, Event, Conversion


class PageViewResource(resources.ModelResource):
    """Resource for import/export"""
    class Meta:
        model = PageView
        fields = ('id', 'session_id', 'page_url', 'page_title', 'device_type',
                  'browser', 'country', 'timestamp')
        export_order = fields


class EventResource(resources.ModelResource):
    """Resource for import/export"""
    class Meta:
        model = Event
        fields = ('id', 'event_name', 'event_category', 'session_id', 'page_url',
                  'timestamp')
        export_order = fields


class ConversionResource(resources.ModelResource):
    """Resource for import/export"""
    class Meta:
        model = Conversion
        fields = ('id', 'conversion_type', 'value', 'timestamp')
        export_order = fields


@admin.register(PageView)
class PageViewAdmin(ImportExportModelAdmin):
    """Enhanced admin for PageView"""
    resource_class = PageViewResource
    
    list_display = ['page_url_short', 'page_title_short', 'device_badge', 'browser',
                    'country', 'session_id_short', 'timestamp']
    list_filter = [
        ('device_type', DropdownFilter),
        ('browser', DropdownFilter),
        ('country', DropdownFilter),
        'timestamp',
    ]
    search_fields = ['page_url', 'page_title', 'session_id', 'ip_address_hash']
    readonly_fields = ['id', 'timestamp', 'ip_address_hash']
    date_hierarchy = 'timestamp'
    list_per_page = 100
    
    fieldsets = (
        ('Page Information', {
            'fields': ('page_url', 'page_title', 'referrer_url')
        }),
        ('Session', {
            'fields': ('session_id',)
        }),
        ('Device & Browser', {
            'fields': ('device_type', 'browser', 'operating_system', 'user_agent')
        }),
        ('Location', {
            'fields': ('country', 'city')
        }),
        ('Analytics', {
            'fields': ('duration', 'is_exit_page')
        }),
        ('Privacy', {
            'fields': ('ip_address_hash',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('timestamp',)
        }),
    )
    
    def page_url_short(self, obj):
        """Display shortened URL"""
        if len(obj.page_url) > 50:
            return obj.page_url[:47] + '...'
        return obj.page_url
    page_url_short.short_description = 'Page URL'
    
    def page_title_short(self, obj):
        """Display shortened title"""
        if obj.page_title and len(obj.page_title) > 40:
            return obj.page_title[:37] + '...'
        return obj.page_title or '-'
    page_title_short.short_description = 'Title'
    
    def device_badge(self, obj):
        """Display device type with badge"""
        colors = {
            'desktop': 'blue',
            'mobile': 'green',
            'tablet': 'orange',
            'other': 'gray',
        }
        color = colors.get(obj.device_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_device_type_display() if obj.device_type else 'Unknown'
        )
    device_badge.short_description = 'Device'
    
    def session_id_short(self, obj):
        """Display shortened session ID"""
        return obj.session_id[:8] + '...' if len(obj.session_id) > 8 else obj.session_id
    session_id_short.short_description = 'Session'


@admin.register(Event)
class EventAdmin(ImportExportModelAdmin):
    """Enhanced admin for Event"""
    resource_class = EventResource
    
    list_display = ['event_name', 'event_category_badge', 'session_id_short',
                    'page_url_short', 'event_value', 'timestamp']
    list_filter = [
        ('event_category', DropdownFilter),
        ('event_name', DropdownFilter),
        'timestamp',
    ]
    search_fields = ['event_name', 'session_id', 'page_url', 'user_identifier']
    readonly_fields = ['id', 'timestamp']
    date_hierarchy = 'timestamp'
    list_per_page = 100
    
    fieldsets = (
        ('Event Information', {
            'fields': ('event_name', 'event_category', 'event_value')
        }),
        ('Context', {
            'fields': ('session_id', 'page_url', 'user_identifier')
        }),
        ('Data', {
            'fields': ('event_properties', 'metadata')
        }),
        ('Timestamps', {
            'fields': ('timestamp',)
        }),
    )
    
    def event_category_badge(self, obj):
        """Display event category with badge"""
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            obj.get_event_category_display()
        )
    event_category_badge.short_description = 'Category'
    
    def page_url_short(self, obj):
        """Display shortened URL"""
        if obj.page_url and len(obj.page_url) > 40:
            return obj.page_url[:37] + '...'
        return obj.page_url or '-'
    page_url_short.short_description = 'Page URL'
    
    def session_id_short(self, obj):
        """Display shortened session ID"""
        return obj.session_id[:8] + '...' if len(obj.session_id) > 8 else obj.session_id
    session_id_short.short_description = 'Session'


@admin.register(Conversion)
class ConversionAdmin(ImportExportModelAdmin):
    """Enhanced admin for Conversion"""
    resource_class = ConversionResource
    
    list_display = ['conversion_type_badge', 'value', 'content_object_link',
                    'timestamp']
    list_filter = [
        ('conversion_type', DropdownFilter),
        'timestamp',
    ]
    search_fields = ['conversion_type']
    readonly_fields = ['id', 'timestamp']
    date_hierarchy = 'timestamp'
    list_per_page = 50
    
    fieldsets = (
        ('Conversion Information', {
            'fields': ('conversion_type', 'value')
        }),
        ('Related Object', {
            'fields': ('content_type', 'object_id')
        }),
        ('Attribution', {
            'fields': ('attribution_data', 'campaign_info')
        }),
        ('Timestamps', {
            'fields': ('timestamp',)
        }),
    )
    
    def conversion_type_badge(self, obj):
        """Display conversion type with badge"""
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            obj.get_conversion_type_display()
        )
    conversion_type_badge.short_description = 'Type'
    
    def content_object_link(self, obj):
        """Display link to related object"""
        if obj.content_object:
            return format_html('<a href="#">{}</a>', str(obj.content_object))
        return '-'
    content_object_link.short_description = 'Related Object'
