from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    ReportConfiguration, SavedReport, ReportSchedule,
    ReportDelivery, ReportPermission, REPORT_TYPES,
    REPORT_STATUS, SCHEDULE_FREQUENCY, DELIVERY_METHOD,
    DELIVERY_STATUS, EXPORT_FORMATS
)


class ReportConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_type_display', 'is_active', 'school_name', 'created_at')
    list_filter = ('report_type', 'is_active', 'school')
    search_fields = ('name', 'description', 'school__name')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'report_type', 'is_active', 'school')
        }),
        ('Parameters', {
            'fields': ('parameters',),
            'classes': ('collapse',),
        }),
    )
    
    def report_type_display(self, obj):
        """Custom admin display method for showing the report type display name"""
        return obj.get_display_name()
    
    def school_name(self, obj):
        """Custom admin display method for showing the school name if associated"""
        return obj.school.name if obj.school else 'N/A'


class SavedReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'report_type_display', 'configuration_name', 'status', 
                    'generated_at', 'expiration_status', 'download_link')
    list_filter = ('report_type', 'status', 'generated_at', 'expires_at')
    search_fields = ('configuration__name', 'id')
    readonly_fields = ('generated_at', 'expires_at', 'file_path', 'created_at', 'updated_at')
    raw_id_fields = ('configuration', 'created_by')
    
    def report_type_display(self, obj):
        """Custom admin display method for showing the report type display name"""
        return REPORT_TYPES.get(obj.report_type, obj.report_type)
    
    def configuration_name(self, obj):
        """Custom admin display method for showing the configuration name"""
        return obj.configuration.name if obj.configuration else 'N/A'
    
    def download_link(self, obj):
        """Custom admin display method for showing a download link for the report"""
        if obj.file_path:
            try:
                url = obj.get_download_url()
                return format_html('<a href="{}" target="_blank">Download</a>', url)
            except Exception as e:
                return f'Error: {str(e)}'
        return 'No file'
    
    def expiration_status(self, obj):
        """Custom admin display method for showing the report expiration status"""
        return 'Expired' if obj.is_expired() else 'Active'


class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'configuration_name', 'report_type', 'frequency', 
                    'next_run', 'due_status', 'is_active', 'execute_link')
    list_filter = ('frequency', 'is_active', 'next_run', 'last_run')
    search_fields = ('name', 'configuration__name')
    raw_id_fields = ('configuration', 'created_by')
    
    def configuration_name(self, obj):
        """Custom admin display method for showing the configuration name"""
        return obj.configuration.name
    
    def report_type(self, obj):
        """Custom admin display method for showing the report type"""
        return REPORT_TYPES.get(obj.configuration.report_type, obj.configuration.report_type)
    
    def due_status(self, obj):
        """Custom admin display method for showing if the schedule is due"""
        return 'Due' if obj.is_due() else 'Not Due'
    
    def execute_link(self, obj):
        """Custom admin display method for showing an execute link for the schedule"""
        url = f"/admin/reporting/reportschedule/{obj.id}/execute/"
        return format_html('<a href="{}">Execute Now</a>', url)


class ReportDeliveryAdmin(admin.ModelAdmin):
    list_display = ('report_id', 'report_type', 'delivery_method', 'status', 
                    'delivered_at', 'retry_count', 'retry_link')
    list_filter = ('delivery_method', 'status', 'delivered_at', 'retry_count')
    search_fields = ('report__id', 'error_message')
    raw_id_fields = ('report', 'created_by')
    
    def report_id(self, obj):
        """Custom admin display method for showing the report ID"""
        return str(obj.report.id)
    
    def report_type(self, obj):
        """Custom admin display method for showing the report type"""
        return REPORT_TYPES.get(obj.report.report_type, obj.report.report_type)
    
    def retry_link(self, obj):
        """Custom admin display method for showing a retry link for failed deliveries"""
        if obj.status == DELIVERY_STATUS['FAILED']:
            url = f"/admin/reporting/reportdelivery/{obj.id}/retry/"
            return format_html('<a href="{}">Retry</a>', url)
        return ''


class ReportPermissionAdmin(admin.ModelAdmin):
    list_display = ('configuration_name', 'user_name', 'can_view', 'can_generate', 
                    'can_schedule', 'can_export', 'granted_by_name', 'granted_at')
    list_filter = ('can_view', 'can_generate', 'can_schedule', 'can_export', 'granted_at')
    search_fields = ('configuration__name', 'user__email', 'user__first_name', 'user__last_name')
    raw_id_fields = ('configuration', 'user', 'granted_by')
    
    def configuration_name(self, obj):
        """Custom admin display method for showing the configuration name"""
        return obj.configuration.name
    
    def user_name(self, obj):
        """Custom admin display method for showing the user's full name"""
        return obj.user.get_full_name() or obj.user.email
    
    def granted_by_name(self, obj):
        """Custom admin display method for showing the granter's full name"""
        if not obj.granted_by:
            return 'N/A'
        return obj.granted_by.get_full_name() or obj.granted_by.email


# Register models with admin site
admin.site.register(ReportConfiguration, ReportConfigurationAdmin)
admin.site.register(SavedReport, SavedReportAdmin)
admin.site.register(ReportSchedule, ReportScheduleAdmin)
admin.site.register(ReportDelivery, ReportDeliveryAdmin)
admin.site.register(ReportPermission, ReportPermissionAdmin)