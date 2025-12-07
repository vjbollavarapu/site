"""
Admin configuration for A/B testing
"""
from django.contrib import admin
from .models import ABTest, VariantAssignment, ConversionByVariant, ABTestStats


@admin.register(ABTest)
class ABTestAdmin(admin.ModelAdmin):
    list_display = ['name', 'test_type', 'status', 'traffic_split', 'start_date', 'end_date', 'created_at']
    list_filter = ['status', 'test_type', 'created_at']
    search_fields = ['name', 'description', 'test_type']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Test Information', {
            'fields': ('name', 'description', 'test_type', 'status')
        }),
        ('Variants', {
            'fields': ('variant_a_name', 'variant_b_name', 'traffic_split')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at')
        }),
    )
    
    actions = ['activate_tests', 'pause_tests', 'calculate_stats']
    
    def activate_tests(self, request, queryset):
        """Activate selected tests"""
        queryset.update(status='active')
        self.message_user(request, f"{queryset.count()} test(s) activated.")
    activate_tests.short_description = "Activate selected tests"
    
    def pause_tests(self, request, queryset):
        """Pause selected tests"""
        queryset.update(status='paused')
        self.message_user(request, f"{queryset.count()} test(s) paused.")
    pause_tests.short_description = "Pause selected tests"
    
    def calculate_stats(self, request, queryset):
        """Calculate statistics for selected tests"""
        from .services import ABTestingService
        for test in queryset:
            ABTestingService.update_test_stats(test)
        self.message_user(request, f"Statistics calculated for {queryset.count()} test(s).")
    calculate_stats.short_description = "Calculate statistics"


@admin.register(VariantAssignment)
class VariantAssignmentAdmin(admin.ModelAdmin):
    list_display = ['ab_test', 'user_identifier', 'variant', 'assigned_at']
    list_filter = ['ab_test', 'variant', 'assigned_at']
    search_fields = ['user_identifier', 'ab_test__name']
    readonly_fields = ['id', 'assigned_at']
    date_hierarchy = 'assigned_at'


@admin.register(ConversionByVariant)
class ConversionByVariantAdmin(admin.ModelAdmin):
    list_display = ['ab_test', 'variant', 'conversion_type', 'user_identifier', 'converted_at']
    list_filter = ['ab_test', 'variant', 'conversion_type', 'converted_at']
    search_fields = ['user_identifier', 'ab_test__name', 'conversion_type']
    readonly_fields = ['id', 'converted_at']
    date_hierarchy = 'converted_at'


@admin.register(ABTestStats)
class ABTestStatsAdmin(admin.ModelAdmin):
    list_display = ['ab_test', 'variant_a_conversion_rate', 'variant_b_conversion_rate', 'winner', 'confidence_level', 'last_calculated_at']
    list_filter = ['winner', 'last_calculated_at']
    search_fields = ['ab_test__name']
    readonly_fields = ['id', 'last_calculated_at']
    
    def has_add_permission(self, request):
        return False  # Stats are auto-created

