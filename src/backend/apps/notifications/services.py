"""
Provides service functions for creating, managing, and processing notifications in the loan management system.

This module implements the business logic for notification generation based on system events, 
recipient determination, and notification delivery orchestration.
"""

import logging
from datetime import datetime
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from django.conf import settings

from .models import (
    NotificationTemplate, NotificationEvent, 
    NotificationEventMapping, Notification
)
from .email import send_notification_email, EmailDeliveryService
from .constants import (
    NOTIFICATION_TYPES, NOTIFICATION_STATUS, 
    NOTIFICATION_DELIVERY_METHODS, NOTIFICATION_PRIORITIES, 
    NOTIFICATION_CATEGORIES, EMAIL_SUBJECTS,
    NOTIFICATION_EVENT_MAPPINGS, EVENT_TYPE
)
from ..users.models import User
from ..applications.models import LoanApplication
from ...utils.logging import get_audit_logger, mask_pii

# Set up loggers
logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()


def create_notification(template, recipient, context, application=None, event=None, 
                       delivery_method=NOTIFICATION_DELIVERY_METHODS['EMAIL'], 
                       priority=NOTIFICATION_PRIORITIES['MEDIUM'],
                       category=NOTIFICATION_CATEGORIES['SYSTEM']):
    """
    Creates a notification record based on template and recipient information.
    
    Args:
        template (NotificationTemplate): Template for the notification
        recipient (User): User who should receive the notification
        context (dict): Context data for rendering the template
        application (LoanApplication, optional): Associated loan application
        event (NotificationEvent, optional): Triggering event
        delivery_method (str, optional): Method of delivery
        priority (str, optional): Priority level
        category (str, optional): Notification category
        
    Returns:
        Notification: Created notification object
    """
    try:
        # Render the template with context
        subject, body = template.render(context)
        
        # Create notification object
        notification = Notification.objects.create(
            template=template,
            recipient=recipient,
            recipient_email=recipient.email,
            subject=subject,
            body=body,
            event=event,
            application=application,
            status=NOTIFICATION_STATUS['PENDING'],
            delivery_method=delivery_method,
            priority=priority,
            category=category
        )
        
        logger.info(f"Created notification ID {notification.id} for {mask_pii(recipient.email)}")
        audit_logger.info(
            "Notification created",
            extra={
                'notification_id': str(notification.id),
                'template_type': template.notification_type,
                'recipient_type': recipient.user_type,
                'email_masked': mask_pii(recipient.email)
            }
        )
        
        return notification
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        raise


def create_notification_from_event(event):
    """
    Creates notifications based on a notification event and its mappings.
    
    Args:
        event (NotificationEvent): The triggering event
        
    Returns:
        list: List of created notification objects
    """
    created_notifications = []
    try:
        # Get event context data
        context = event.get_context()
        
        # Get associated entity (e.g., application)
        entity = event.get_entity()
        
        # Get mappings for this event type
        mappings = NotificationEventMapping.get_mappings_for_event(event.event_type)
        
        # Process each mapping to create appropriate notifications
        for mapping in mappings:
            template = mapping.template
            
            # Determine recipients based on mapping
            recipients = get_recipients_for_mapping(mapping, entity, context)
            
            # Create a notification for each recipient
            for recipient in recipients:
                application = entity if isinstance(entity, LoanApplication) else None
                notification = create_notification(
                    template=template,
                    recipient=recipient,
                    context=context,
                    application=application,
                    event=event,
                    priority=mapping.priority,
                    category=template.notification_type.split('_')[0].upper() 
                          if '_' in template.notification_type else NOTIFICATION_CATEGORIES['SYSTEM']
                )
                created_notifications.append(notification)
        
        # Mark the event as processed
        event.mark_processed()
        
        return created_notifications
    except Exception as e:
        logger.error(f"Error creating notifications from event {event.id}: {str(e)}")
        raise


def create_event(event_type, entity, triggered_by=None, context_data=None):
    """
    Creates a notification event based on an entity and event type.
    
    Args:
        event_type (str): Type of the event
        entity (object): The entity associated with the event
        triggered_by (User, optional): User who triggered the event
        context_data (dict, optional): Additional context data
        
    Returns:
        NotificationEvent: Created event object
    """
    try:
        # Validate event type
        if event_type not in EVENT_TYPE.values():
            raise ValueError(f"Invalid event type: {event_type}")
        
        # Determine entity type and ID
        entity_id = getattr(entity, 'id', None)
        entity_type = entity.__class__.__name__.lower()
        
        # Create the event
        event = NotificationEvent.objects.create(
            event_type=event_type,
            entity_id=entity_id,
            entity_type=entity_type,
            triggered_by=triggered_by,
            context_data=context_data or {}
        )
        
        logger.info(f"Created notification event ID {event.id} of type {event_type}")
        
        return event
    except Exception as e:
        logger.error(f"Error creating notification event: {str(e)}")
        raise


def get_recipients_for_mapping(mapping, entity, context):
    """
    Determines the recipients for a notification based on mapping and entity.
    
    Args:
        mapping (NotificationEventMapping): The mapping configuration
        entity (object): The entity associated with the event
        context (dict): Context data for additional information
        
    Returns:
        list: List of User objects who should receive the notification
    """
    recipients = []
    
    try:
        recipient_type = mapping.recipient_type
        
        # Handle application-related recipients
        if isinstance(entity, LoanApplication):
            application = entity
            
            # Borrower
            if recipient_type == 'borrower':
                recipients.append(application.borrower)
            
            # Co-borrower
            elif recipient_type == 'co_borrower' and application.co_borrower:
                recipients.append(application.co_borrower)
            
            # School administrator
            elif recipient_type == 'school_admin':
                # Get school administrators from the school
                from ..users.models import SchoolAdminProfile
                school_admins = SchoolAdminProfile.objects.filter(
                    school=application.school, 
                    user__is_active=True
                )
                recipients.extend([admin.user for admin in school_admins])
            
            # Underwriter
            elif recipient_type == 'underwriter':
                # Try to get the assigned underwriter if available
                try:
                    from ..underwriting.models import UnderwritingQueue
                    queue_item = UnderwritingQueue.objects.filter(
                        application=application, 
                        assigned_to__isnull=False
                    ).first()
                    if queue_item and queue_item.assigned_to:
                        recipients.append(queue_item.assigned_to)
                except (ImportError, Exception):
                    pass
            
            # System administrators
            elif recipient_type == 'system_admin':
                system_admins = User.objects.filter(
                    user_type='system_admin',
                    is_active=True
                )
                recipients.extend(system_admins)
        
        # Handle other entity types as needed
        # Add more cases based on your entity types as the system grows
        
    except Exception as e:
        logger.error(f"Error determining recipients: {str(e)}")
    
    # Return unique recipients
    return list(set(recipients))


def process_pending_events():
    """
    Processes all pending notification events.
    
    Returns:
        dict: Statistics about processed events and created notifications
    """
    events_processed = 0
    notifications_created = 0
    
    try:
        # Find all unprocessed events
        unprocessed_events = NotificationEvent.objects.filter(processed=False)
        
        with transaction.atomic():
            # Process each event
            for event in unprocessed_events:
                notifications = create_notification_from_event(event)
                events_processed += 1
                notifications_created += len(notifications)
        
        logger.info(f"Processed {events_processed} events, created {notifications_created} notifications")
        
        return {
            'events_processed': events_processed,
            'notifications_created': notifications_created
        }
    except Exception as e:
        logger.error(f"Error processing notification events: {str(e)}")
        return {
            'events_processed': events_processed,
            'notifications_created': notifications_created,
            'error': str(e)
        }


def send_immediate_notification(notification_type, recipient, context, application=None):
    """
    Creates and immediately sends a notification.
    
    Args:
        notification_type (str): Type of notification to send
        recipient (User): User who should receive the notification
        context (dict): Context data for rendering the template
        application (LoanApplication, optional): Associated loan application
        
    Returns:
        bool: True if notification was sent successfully, False otherwise
    """
    try:
        # Get the template for this notification type
        template = NotificationTemplate.get_template_for_type(notification_type)
        if not template:
            logger.error(f"No active template found for notification type: {notification_type}")
            return False
        
        # Create notification
        notification = create_notification(
            template=template,
            recipient=recipient,
            context=context,
            application=application
        )
        
        # Send notification immediately
        success = send_notification_email(notification)
        
        logger.info(f"Immediate notification {notification.id} send result: {'success' if success else 'failed'}")
        
        return success
    except Exception as e:
        logger.error(f"Error sending immediate notification: {str(e)}")
        return False


def get_notification_context(entity, additional_context=None):
    """
    Builds a context dictionary for notification templates based on entity type.
    
    Args:
        entity (object): The entity to extract context data from
        additional_context (dict, optional): Additional context to include
        
    Returns:
        dict: Context dictionary for notification templates
    """
    context = {}
    
    # Base context data common to all notifications
    context['current_date'] = datetime.now().strftime('%B %d, %Y')
    context['app_name'] = getattr(settings, 'APP_NAME', 'Loan Management System')
    context['support_email'] = getattr(settings, 'SUPPORT_EMAIL', 'support@example.com')
    context['base_url'] = getattr(settings, 'BASE_URL', 'https://example.com')
    
    try:
        # Build context based on entity type
        if isinstance(entity, LoanApplication):
            # Application context
            application = entity
            context['application_id'] = str(application.id)
            context['application_status'] = application.status
            
            # Borrower information
            if application.borrower:
                context['borrower_name'] = f"{application.borrower.first_name} {application.borrower.last_name}"
                context['borrower_email'] = application.borrower.email
            
            # Co-borrower information if available
            if application.co_borrower:
                context['co_borrower_name'] = f"{application.co_borrower.first_name} {application.co_borrower.last_name}"
                context['co_borrower_email'] = application.co_borrower.email
            
            # School and program information
            if application.school:
                context['school_name'] = application.school.name
            
            if application.program:
                context['program_name'] = application.program.name
            
            # Loan details
            try:
                loan_details = application.get_loan_details()
                if loan_details:
                    context['requested_amount'] = f"${loan_details.requested_amount:,.2f}"
                    context['start_date'] = loan_details.start_date.strftime('%B %d, %Y')
            except Exception as e:
                logger.error(f"Error getting loan details for context: {str(e)}")
            
            # Underwriting decision if available
            try:
                decision = application.get_underwriting_decision()
                if decision:
                    context['approved_amount'] = f"${decision.approved_amount:,.2f}"
                    context['interest_rate'] = f"{decision.interest_rate:.2f}%"
                    context['term_months'] = decision.term_months
            except Exception as e:
                logger.error(f"Error getting underwriting decision for context: {str(e)}")
        
        # Add more entity types as needed for documents, signatures, etc.
        
        # Merge with additional context if provided
        if additional_context:
            context.update(additional_context)
        
        return context
    except Exception as e:
        logger.error(f"Error building notification context: {str(e)}")
        # Return at least the additional context or an empty dict
        return additional_context or {}


def schedule_reminder(notification_type, recipient, context, application=None, reminder_date=None):
    """
    Schedules a reminder notification for a future date.
    
    Args:
        notification_type (str): Type of notification to schedule
        recipient (User): User who should receive the notification
        context (dict): Context data for rendering the template
        application (LoanApplication, optional): Associated loan application
        reminder_date (datetime.date): Date when the reminder should be sent
        
    Returns:
        Notification: Created notification object with scheduled status
    """
    try:
        # Get the template for this notification type
        template = NotificationTemplate.get_template_for_type(notification_type)
        if not template:
            logger.error(f"No active template found for notification type: {notification_type}")
            return None
        
        # Create notification
        notification = create_notification(
            template=template,
            recipient=recipient,
            context=context,
            application=application,
            priority=NOTIFICATION_PRIORITIES['HIGH']  # Reminders usually high priority
        )
        
        # Set status to scheduled with reminder date
        notification.status = NOTIFICATION_STATUS.get('SCHEDULED', 'scheduled')
        if reminder_date:
            notification.scheduled_for = reminder_date
        notification.save()
        
        logger.info(f"Scheduled reminder notification {notification.id} for {reminder_date}")
        
        return notification
    except Exception as e:
        logger.error(f"Error scheduling reminder notification: {str(e)}")
        return None


class NotificationService:
    """
    Service class for managing notifications throughout the system.
    """
    
    def __init__(self):
        """
        Initializes the notification service.
        """
        self.email_service = EmailDeliveryService()
        logger.info("NotificationService initialized")
    
    def create_notification(self, notification_type, recipient, context, application=None):
        """
        Creates a notification record.
        
        Args:
            notification_type (str): Type of notification to create
            recipient (User): User who should receive the notification
            context (dict): Context data for rendering the template
            application (LoanApplication, optional): Associated loan application
            
        Returns:
            Notification: Created notification object
        """
        template = NotificationTemplate.get_template_for_type(notification_type)
        if not template:
            logger.error(f"No active template found for notification type: {notification_type}")
            return None
        
        return create_notification(
            template=template,
            recipient=recipient,
            context=context,
            application=application
        )
    
    def send_notification(self, notification):
        """
        Sends an existing notification.
        
        Args:
            notification (Notification): The notification to send
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        return self.email_service.send_notification(notification)
    
    def create_and_send(self, notification_type, recipient, context, application=None):
        """
        Creates and immediately sends a notification.
        
        Args:
            notification_type (str): Type of notification to send
            recipient (User): User who should receive the notification
            context (dict): Context data for rendering the template
            application (LoanApplication, optional): Associated loan application
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        notification = self.create_notification(
            notification_type=notification_type,
            recipient=recipient,
            context=context,
            application=application
        )
        
        if notification:
            return self.send_notification(notification)
        
        return False
    
    def create_event_notification(self, event_type, entity, triggered_by=None, context_data=None):
        """
        Creates a notification event and processes it immediately.
        
        Args:
            event_type (str): Type of the event
            entity (object): The entity associated with the event
            triggered_by (User, optional): User who triggered the event
            context_data (dict, optional): Additional context data
            
        Returns:
            list: List of created notifications
        """
        event = create_event(
            event_type=event_type,
            entity=entity,
            triggered_by=triggered_by,
            context_data=context_data
        )
        
        return create_notification_from_event(event)
    
    def schedule_reminder(self, notification_type, recipient, context, application=None, reminder_date=None):
        """
        Schedules a reminder notification.
        
        Args:
            notification_type (str): Type of notification to schedule
            recipient (User): User who should receive the notification
            context (dict): Context data for rendering the template
            application (LoanApplication, optional): Associated loan application
            reminder_date (date): Date when the reminder should be sent
            
        Returns:
            Notification: Created notification with scheduled status
        """
        return schedule_reminder(
            notification_type=notification_type,
            recipient=recipient,
            context=context,
            application=application,
            reminder_date=reminder_date
        )
    
    def process_pending_events(self):
        """
        Processes all pending notification events.
        
        Args:
            None
            
        Returns:
            dict: Statistics about processed events
        """
        return process_pending_events()


class EventNotificationManager:
    """
    Manager class for handling event-based notifications.
    """
    
    def __init__(self):
        """
        Initializes the event notification manager.
        """
        self.notification_service = NotificationService()
        logger.info("EventNotificationManager initialized")
    
    def register_event_handlers(self):
        """
        Registers event handlers for different entity types.
        
        This method would connect to model signals or other event sources in a Django application.
        
        Returns:
            None
        """
        # This would typically connect to Django signals
        # Example:
        # from django.db.models.signals import post_save
        # from django.dispatch import receiver
        # 
        # @receiver(post_save, sender=LoanApplication)
        # def application_changed(sender, instance, created, **kwargs):
        #     if not created and hasattr(instance, '_original_status'):
        #         self.handle_application_status_change(
        #             instance, instance._original_status, instance.status
        #         )
        
        logger.info("Event handlers registered")
    
    def handle_application_status_change(self, application, old_status, new_status, triggered_by=None):
        """
        Handles notification events for application status changes.
        
        Args:
            application (LoanApplication): The application that changed status
            old_status (str): Previous status
            new_status (str): New status
            triggered_by (User, optional): User who triggered the change
            
        Returns:
            list: List of created notifications
        """
        # Determine the appropriate event type based on status transition
        event_type = None
        context_data = {
            'old_status': old_status,
            'new_status': new_status
        }
        
        # Map status transitions to event types
        if new_status == 'submitted':
            event_type = EVENT_TYPE['APPLICATION_STATUS_CHANGE']
            context_data['notification_type'] = NOTIFICATION_TYPES['APPLICATION_SUBMITTED']
        elif new_status == 'approved':
            event_type = EVENT_TYPE['APPLICATION_STATUS_CHANGE']
            context_data['notification_type'] = NOTIFICATION_TYPES['APPLICATION_APPROVED']
        elif new_status == 'denied':
            event_type = EVENT_TYPE['APPLICATION_STATUS_CHANGE']
            context_data['notification_type'] = NOTIFICATION_TYPES['APPLICATION_DENIED']
        elif new_status == 'revision_requested':
            event_type = EVENT_TYPE['APPLICATION_STATUS_CHANGE']
            context_data['notification_type'] = NOTIFICATION_TYPES['APPLICATION_REVISION']
        elif new_status == 'funded':
            event_type = EVENT_TYPE['APPLICATION_STATUS_CHANGE']
            context_data['notification_type'] = NOTIFICATION_TYPES['FUNDING_COMPLETED']
        
        # Create event notification if we have a valid event type
        if event_type:
            return self.notification_service.create_event_notification(
                event_type=event_type,
                entity=application,
                triggered_by=triggered_by,
                context_data=context_data
            )
        
        return []
    
    def handle_document_status_change(self, document, old_status, new_status, triggered_by=None):
        """
        Handles notification events for document status changes.
        
        Args:
            document (Document): The document that changed status
            old_status (str): Previous status
            new_status (str): New status
            triggered_by (User, optional): User who triggered the change
            
        Returns:
            list: List of created notifications
        """
        # Determine the appropriate event type based on status transition
        event_type = None
        context_data = {
            'old_status': old_status,
            'new_status': new_status,
            'document_type': getattr(document, 'document_type', None)
        }
        
        # Get the application associated with the document
        application = getattr(document, 'application', None)
        
        # Map status transitions to event types
        if new_status == 'generated':
            event_type = EVENT_TYPE['DOCUMENT_STATUS_CHANGE']
            context_data['notification_type'] = NOTIFICATION_TYPES['DOCUMENT_READY']
        
        # Create event notification if we have a valid event type and application
        if event_type and application:
            return self.notification_service.create_event_notification(
                event_type=event_type,
                entity=application,  # Use application as the entity for better context
                triggered_by=triggered_by,
                context_data=context_data
            )
        
        return []
    
    def handle_signature_status_change(self, signature_request, old_status, new_status, triggered_by=None):
        """
        Handles notification events for signature status changes.
        
        Args:
            signature_request (SignatureRequest): The signature request that changed status
            old_status (str): Previous status
            new_status (str): New status
            triggered_by (User, optional): User who triggered the change
            
        Returns:
            list: List of created notifications
        """
        # Determine the appropriate event type based on status transition
        event_type = None
        context_data = {
            'old_status': old_status,
            'new_status': new_status
        }
        
        # Get the document and application associated with the signature request
        document = getattr(signature_request, 'document', None)
        application = getattr(document, 'application', None) if document else None
        
        # Map status transitions to event types
        if new_status == 'signed':
            event_type = EVENT_TYPE['SIGNATURE_STATUS_CHANGE']
            context_data['notification_type'] = NOTIFICATION_TYPES['SIGNATURE_COMPLETED']
        
        # Create event notification if we have a valid event type and application
        if event_type and application:
            return self.notification_service.create_event_notification(
                event_type=event_type,
                entity=application,  # Use application as the entity for better context
                triggered_by=triggered_by,
                context_data=context_data
            )
        
        return []
    
    def handle_funding_status_change(self, funding_request, old_status, new_status, triggered_by=None):
        """
        Handles notification events for funding status changes.
        
        Args:
            funding_request (FundingRequest): The funding request that changed status
            old_status (str): Previous status
            new_status (str): New status
            triggered_by (User, optional): User who triggered the change
            
        Returns:
            list: List of created notifications
        """
        # Determine the appropriate event type based on status transition
        event_type = None
        context_data = {
            'old_status': old_status,
            'new_status': new_status
        }
        
        # Get the application associated with the funding request
        application = getattr(funding_request, 'application', None)
        
        # Map status transitions to event types
        if new_status == 'disbursed':
            event_type = EVENT_TYPE['FUNDING_STATUS_CHANGE']
            context_data['notification_type'] = NOTIFICATION_TYPES['FUNDING_COMPLETED']
        
        # Create event notification if we have a valid event type and application
        if event_type and application:
            return self.notification_service.create_event_notification(
                event_type=event_type,
                entity=application,  # Use application as the entity for better context
                triggered_by=triggered_by,
                context_data=context_data
            )
        
        return []