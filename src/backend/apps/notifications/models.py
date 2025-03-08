"""
Defines the data models for the notification system in the loan management application.

This module implements models for templates, events, mappings, and notification records
to support the email notification system that keeps users informed about application status,
document requirements, and other important events.
"""

from django.db import models  # Django 4.2+
from django.utils import timezone  # Django 4.2+
from django.db.models import JSONField  # Django 4.2+
from django.template.loader import render_to_string  # Django 4.2+

from core.models import (
    CoreModel, UUIDModel, TimeStampedModel, 
    SoftDeleteModel, AuditableModel
)
from apps.users.models import User
from apps.applications.models import LoanApplication
from .constants import (
    NOTIFICATION_TYPES, 
    NOTIFICATION_STATUS,
    NOTIFICATION_DELIVERY_METHODS,
    NOTIFICATION_PRIORITIES,
    NOTIFICATION_CATEGORIES,
    EMAIL_TEMPLATES,
    EVENT_TYPE
)


class NotificationTemplate(CoreModel):
    """
    Model for storing email notification templates.
    
    This model stores templates used for generating email notifications,
    including both the subject and body templates, with support for
    either storing template content directly or referencing template files.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    subject_template = models.CharField(max_length=255)
    body_template = models.TextField()
    notification_type = models.CharField(
        max_length=50,
        choices=[(k, v) for k, v in NOTIFICATION_TYPES.items()],
        unique=True
    )
    is_active = models.BooleanField(default=True)
    template_path = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Optional path to template file. If provided, file template takes precedence over stored template."
    )

    def __str__(self):
        """String representation of template."""
        return f"{self.name} ({self.notification_type})"

    def render(self, context):
        """
        Renders the template with the provided context.
        
        Args:
            context (dict): Context data for rendering the template
            
        Returns:
            tuple: Tuple containing (rendered_subject, rendered_body)
        """
        from django.template import Template, Context
        
        # If template_path is provided, use render_to_string
        if self.template_path:
            rendered_body = render_to_string(self.template_path, context)
            # Still use the subject_template from the model
            subject_template = Template(self.subject_template)
            rendered_subject = subject_template.render(Context(context))
        else:
            # Otherwise use the stored template content
            subject_template = Template(self.subject_template)
            body_template = Template(self.body_template)
            rendered_subject = subject_template.render(Context(context))
            rendered_body = body_template.render(Context(context))
        
        return (rendered_subject, rendered_body)
    
    @classmethod
    def get_template_for_type(cls, notification_type):
        """
        Class method to get the active template for a notification type.
        
        Args:
            notification_type (str): The notification type to get a template for
            
        Returns:
            NotificationTemplate: The active template for the given type or None
        """
        try:
            return cls.objects.get(notification_type=notification_type, is_active=True)
        except cls.DoesNotExist:
            return None


class NotificationEvent(CoreModel):
    """
    Model for storing events that trigger notifications.
    
    This model captures system events that should generate notifications,
    storing event type, related entity information, and context data needed
    for generating notification content.
    """
    event_type = models.CharField(
        max_length=50,
        choices=[(k, v) for k, v in EVENT_TYPE.items()]
    )
    entity_id = models.UUIDField(
        help_text="UUID of the entity related to this event (e.g., application ID, document ID)"
    )
    entity_type = models.CharField(
        max_length=50,
        help_text="Type of entity this event relates to (e.g., 'application', 'document')"
    )
    triggered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="triggered_events"
    )
    context_data = JSONField(
        default=dict,
        blank=True,
        help_text="JSON data with context for notification generation"
    )
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        """String representation of event."""
        return f"{self.get_event_type_display()} - {self.entity_type}:{self.entity_id}"

    def get_context(self):
        """
        Gets the context data for the event.
        
        Returns:
            dict: Context data for the event
        """
        return self.context_data or {}

    def mark_processed(self):
        """
        Marks the event as processed.
        
        Sets the processed flag to True and updates the processed_at timestamp.
        """
        self.processed = True
        self.processed_at = timezone.now()
        self.save(update_fields=['processed', 'processed_at'])

    def get_entity(self):
        """
        Gets the entity associated with this event.
        
        Returns:
            object: The entity object or None if not found
        """
        if self.entity_type == 'application':
            try:
                return LoanApplication.objects.get(id=self.entity_id)
            except LoanApplication.DoesNotExist:
                return None
        # Add other entity types as needed
        return None


class NotificationEventMapping(CoreModel):
    """
    Model for mapping event types to notification templates.
    
    This model defines which notification templates should be used for
    which event types, and which recipient types should receive notifications
    for each event.
    """
    event_type = models.CharField(
        max_length=50,
        choices=[(k, v) for k, v in EVENT_TYPE.items()]
    )
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.PROTECT,
        related_name="event_mappings"
    )
    recipient_type = models.CharField(
        max_length=20,
        choices=[
            ('borrower', 'Borrower'),
            ('co_borrower', 'Co-Borrower'),
            ('school_admin', 'School Administrator'),
            ('underwriter', 'Underwriter'),
            ('system_admin', 'System Administrator')
        ]
    )
    priority = models.CharField(
        max_length=10,
        choices=[(k, v) for k, v in NOTIFICATION_PRIORITIES.items()],
        default=NOTIFICATION_PRIORITIES['MEDIUM']
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('event_type', 'template', 'recipient_type')

    def __str__(self):
        """String representation of mapping."""
        return f"{self.get_event_type_display()} → {self.template.name} → {self.recipient_type}"

    @classmethod
    def get_mappings_for_event(cls, event_type):
        """
        Class method to get all active mappings for an event type.
        
        Args:
            event_type (str): The event type to get mappings for
            
        Returns:
            QuerySet: QuerySet of active mappings for the event type
        """
        return cls.objects.filter(event_type=event_type, is_active=True)


class Notification(CoreModel):
    """
    Model for storing individual notifications.
    
    This model represents a specific notification sent to a recipient,
    tracking its content, delivery status, and retry information.
    """
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.PROTECT,
        related_name="notifications"
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="notifications"
    )
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    event = models.ForeignKey(
        NotificationEvent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications"
    )
    application = models.ForeignKey(
        LoanApplication,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications"
    )
    status = models.CharField(
        max_length=20,
        choices=[(k, v) for k, v in NOTIFICATION_STATUS.items()],
        default=NOTIFICATION_STATUS['PENDING']
    )
    delivery_method = models.CharField(
        max_length=20,
        choices=[(k, v) for k, v in NOTIFICATION_DELIVERY_METHODS.items()],
        default=NOTIFICATION_DELIVERY_METHODS['EMAIL']
    )
    priority = models.CharField(
        max_length=10,
        choices=[(k, v) for k, v in NOTIFICATION_PRIORITIES.items()],
        default=NOTIFICATION_PRIORITIES['MEDIUM']
    )
    category = models.CharField(
        max_length=20,
        choices=[(k, v) for k, v in NOTIFICATION_CATEGORIES.items()],
        default=NOTIFICATION_CATEGORIES['SYSTEM']
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    retry_count = models.IntegerField(default=0)
    last_retry_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        """String representation of notification."""
        return f"Notification to {self.recipient_email} - {self.status}"

    def mark_sent(self):
        """
        Marks the notification as sent.
        
        Updates the status to 'SENT' and sets the sent_at timestamp.
        """
        self.status = NOTIFICATION_STATUS['SENT']
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at'])

    def mark_failed(self, error_message):
        """
        Marks the notification as failed.
        
        Args:
            error_message (str): Error message explaining the failure
        """
        self.status = NOTIFICATION_STATUS['FAILED']
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message'])

    def mark_retry(self):
        """
        Marks the notification for retry.
        
        Increments the retry count and updates the last_retry_at timestamp.
        """
        self.status = NOTIFICATION_STATUS['PENDING']
        self.retry_count += 1
        self.last_retry_at = timezone.now()
        self.save(update_fields=['status', 'retry_count', 'last_retry_at'])

    def can_retry(self, max_retries):
        """
        Checks if the notification can be retried.
        
        Args:
            max_retries (int): Maximum number of retry attempts allowed
            
        Returns:
            bool: True if can be retried, False otherwise
        """
        return self.retry_count < max_retries