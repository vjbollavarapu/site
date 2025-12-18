"""
Admin configuration for webhooks
"""
from django.contrib import admin
from .models import WebhookConfig, WebhookEvent


@admin.register(WebhookConfig)
class WebhookConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'event_type', 'url', 'is_active', 'retry_attempts', 'created_at']
    list_filter = ['event_type', 'is_active', 'created_at']
    search_fields = ['name', 'url']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'event_type', 'url', 'is_active')
        }),
        ('Configuration', {
            'fields': ('secret_key', 'retry_attempts', 'retry_delay', 'timeout', 'headers')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at')
        }),
    )


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ['webhook_config', 'event_type', 'status', 'attempt_count', 'created_at', 'sent_at']
    list_filter = ['status', 'event_type', 'created_at', 'webhook_config']
    search_fields = ['webhook_config__name', 'event_type', 'error_message']
    readonly_fields = ['id', 'created_at', 'sent_at', 'last_attempt_at', 'next_retry_at']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Event Information', {
            'fields': ('webhook_config', 'event_type', 'payload', 'signature')
        }),
        ('Status', {
            'fields': ('status', 'attempt_count', 'last_attempt_at', 'next_retry_at')
        }),
        ('Response', {
            'fields': ('response_status', 'response_body', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'sent_at')
        }),
    )

