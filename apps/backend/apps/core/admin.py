"""
Admin configuration for core models
"""
from django.contrib import admin
from .models import Site


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'domain', 'display_name', 'base_url', 'is_active', 'is_default', 'created_at']
    list_filter = ['is_active', 'is_default', 'created_at']
    search_fields = ['name', 'domain', 'display_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'display_name', 'domain', 'base_url')
        }),
        ('Configuration', {
            'fields': ('is_active', 'is_default', 'additional_domains')
        }),
        ('Metadata', {
            'fields': ('description', 'id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

