"""
Django admin configuration for the notification system.

This module registers notification-related models with the Django admin interface,
providing custom admin classes with appropriate display, filtering, and search
capabilities for managing notification templates, events, mappings, and records.
"""

from django.contrib import admin  # Django 4.2+
from django.utils.html import format_html  # Django 4.2+

from .models import (
    NotificationTemplate,
    NotificationEvent,
    NotificationEventMapping,
    Notification
)
from .constants import (
    NOTIFICATION_TYPES,
    NOTIFICATION_STATUS,
    NOTIFICATION_DELIVERY_METHODS,
    NOTIFICATION_PRIORITIES,
    NOTIFICATION_CATEGORIES,
    EVENT_TYPE,
    MAX_RETRY_ATTEMPTS
)


class NotificationTemplateAdmin(admin.ModelAdmin):
    """Admin configuration for NotificationTemplate model."""
    list_display = ('name', 'notification_type', 'template_preview', 'is_active')
    list_filter = ('notification_type', 'is_active')
    search_fields = ('name', 'description', 'notification_type')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'notification_type', 'is_active')
        }),
        ('Template Content', {
            'fields': ('subject_template', 'body_template', 'template_path'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('template_preview',)

    def template_preview(self, obj):
        """
        Generates a preview link for the template.
        
        Args:
            obj: NotificationTemplate instance
            
        Returns:
            str: HTML link for template preview
        """
        return format_html(
            '<a href="{}?template_id={}" target="_blank">Preview</a>',
            '/admin/notifications/preview/',
            obj.pk
        )
    template_preview.short_description = 'Preview'
    template_preview.allow_tags = True


class NotificationEventAdmin(admin.ModelAdmin):
    """Admin configuration for NotificationEvent model."""
    list_display = ('event_type', 'entity_details', 'processing_status', 
                    'triggered_by', 'created_at')
    list_filter = ('event_type', 'processed', 'entity_type')
    search_fields = ('entity_id', 'entity_type')
    raw_id_fields = ('triggered_by',)

    def entity_details(self, obj):
        """
        Display formatted entity details.
        
        Args:
            obj: NotificationEvent instance
            
        Returns:
            str: Entity type and ID
        """
        return f"{obj.entity_type}: {obj.entity_id}"
    entity_details.short_description = 'Entity'

    def processing_status(self, obj):
        """
        Display the processing status.
        
        Args:
            obj: NotificationEvent instance
            
        Returns:
            str: Processing status as 'Processed' or 'Pending'
        """
        return 'Processed' if obj.processed else 'Pending'
    processing_status.short_description = 'Status'


class NotificationEventMappingAdmin(admin.ModelAdmin):
    """Admin configuration for NotificationEventMapping model."""
    list_display = ('event_type', 'template_name', 'recipient_type', 'priority', 'is_active')
    list_filter = ('event_type', 'recipient_type', 'priority', 'is_active')
    search_fields = ('event_type', 'recipient_type', 'template__name')
    raw_id_fields = ('template',)

    def template_name(self, obj):
        """
        Display the template name.
        
        Args:
            obj: NotificationEventMapping instance
            
        Returns:
            str: Template name
        """
        return obj.template.name
    template_name.short_description = 'Template'


class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for Notification model."""
    list_display = ('recipient_name', 'recipient_email', 'template_type',
                   'delivery_status', 'can_be_retried', 'created_at')
    list_filter = ('status', 'delivery_method', 'priority', 'category')
    search_fields = ('recipient_email', 'subject')
    raw_id_fields = ('recipient', 'event', 'application', 'template')

    def recipient_name(self, obj):
        """
        Display recipient's name.
        
        Args:
            obj: Notification instance
            
        Returns:
            str: Recipient's full name
        """
        if obj.recipient and hasattr(obj.recipient, 'get_full_name'):
            return obj.recipient.get_full_name()
        return obj.recipient_email
    recipient_name.short_description = 'Recipient'

    def template_type(self, obj):
        """
        Display the template type.
        
        Args:
            obj: Notification instance
            
        Returns:
            str: Template notification type
        """
        return obj.template.notification_type
    template_type.short_description = 'Type'

    def delivery_status(self, obj):
        """
        Display the delivery status with timestamp.
        
        Args:
            obj: Notification instance
            
        Returns:
            str: Formatted delivery status with timestamp
        """
        if obj.status == NOTIFICATION_STATUS['SENT'] and obj.sent_at:
            return f"{obj.status} at {obj.sent_at.strftime('%Y-%m-%d %H:%M:%S')}"
        return obj.status
    delivery_status.short_description = 'Delivery Status'

    def can_be_retried(self, obj):
        """
        Display if the notification can be retried.
        
        Args:
            obj: Notification instance
            
        Returns:
            str: 'Yes' if can be retried, 'No' otherwise
        """
        return 'Yes' if obj.can_retry(MAX_RETRY_ATTEMPTS) else 'No'
    can_be_retried.short_description = 'Can Retry'


# Register models with the admin site
admin.site.register(NotificationTemplate, NotificationTemplateAdmin)
admin.site.register(NotificationEvent, NotificationEventAdmin)
admin.site.register(NotificationEventMapping, NotificationEventMappingAdmin)
admin.site.register(Notification, NotificationAdmin)