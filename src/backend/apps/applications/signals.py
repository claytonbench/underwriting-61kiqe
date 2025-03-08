from django.db.models.signals import post_save, pre_save  # Django 4.2+
from django.dispatch import receiver  # Django 4.2+
from django.db import transaction  # Django 4.2+
from django.utils import timezone  # Django 4.2+

from .models import LoanApplication, ApplicationStatusHistory  # ./models.py
from utils.constants import APPLICATION_STATUS, NOTIFICATION_TYPES  # ../../../utils/constants.py
from .constants import APPLICATION_REVIEWABLE_STATUSES  # ./constants.py
from apps.underwriting.models import UnderwritingQueue  # ../../apps/underwriting/models.py
from apps.underwriting.constants import UNDERWRITING_QUEUE_PRIORITY, UNDERWRITING_QUEUE_STATUS  # ../../apps/underwriting/constants.py
from apps.notifications.models import NotificationEvent  # ../../apps/notifications/models.py
from apps.workflow.models import WorkflowEntity  # ../../apps/workflow/models.py
from apps.workflow.constants import WORKFLOW_TYPES  # ../../apps/workflow/constants.py


@receiver(pre_save, sender=LoanApplication)
def application_pre_save(sender, instance, **kwargs):
    """
    Signal handler that runs before a LoanApplication is saved.

    Args:
        sender: The model class
        instance: The actual instance being saved
        kwargs: Additional keyword arguments
    """
    # Store the original status if instance already exists in database
    try:
        instance._original_status = LoanApplication.objects.get(pk=instance.pk).status
    except LoanApplication.DoesNotExist:
        # If this is a new instance (no ID), set the original status to None
        instance._original_status = None


@receiver(post_save, sender=LoanApplication)
def application_post_save(sender, instance, created, **kwargs):
    """
    Signal handler that runs after a LoanApplication is saved.

    Args:
        sender: The model class
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        kwargs: Additional keyword arguments
    """
    old_status = getattr(instance, '_original_status', None)

    # If status has changed, handle the status transition
    if not created and old_status != instance.status:
        handle_status_transition(instance, old_status, instance.status)


def handle_status_transition(application, old_status, new_status):
    """
    Handles actions needed when an application status changes.

    Args:
        application: The LoanApplication instance
        old_status: The previous status
        new_status: The new status
    """
    # If new_status is in APPLICATION_REVIEWABLE_STATUSES, ensure application is in underwriting queue
    if new_status in APPLICATION_REVIEWABLE_STATUSES:
        create_underwriting_queue_entry(application)

    # If new_status is SUBMITTED, add to underwriting queue and create notification
    if new_status == APPLICATION_STATUS['SUBMITTED']:
        create_notification_event(application, NOTIFICATION_TYPES['APPLICATION_SUBMITTED'], {})

    # If new_status is APPROVED, create approval notification
    if new_status == APPLICATION_STATUS['APPROVED']:
        create_notification_event(application, NOTIFICATION_TYPES['APPLICATION_APPROVED'], {})

    # If new_status is DENIED, create denial notification
    if new_status == APPLICATION_STATUS['DENIED']:
        create_notification_event(application, NOTIFICATION_TYPES['APPLICATION_DENIED'], {})

    # If new_status is REVISION_REQUESTED, create revision notification
    if new_status == APPLICATION_STATUS['REVISION_REQUESTED']:
        create_notification_event(application, NOTIFICATION_TYPES['APPLICATION_REVISION'], {})

    # If application is a WorkflowEntity, update workflow state to match application status
    if isinstance(application, WorkflowEntity):
        application.transition_to(new_status)


def create_underwriting_queue_entry(application):
    """
    Creates an entry in the underwriting queue for a submitted application.

    Args:
        application: The LoanApplication instance

    Returns:
        UnderwritingQueue: The created queue entry
    """
    # Check if application already has a queue entry
    existing_queue_entry = UnderwritingQueue.objects.filter(application=application).first()
    if existing_queue_entry:
        return existing_queue_entry

    # Create new UnderwritingQueue entry with application, priority NORMAL, and status PENDING
    queue_entry = UnderwritingQueue(
        application=application,
        priority=UNDERWRITING_QUEUE_PRIORITY['MEDIUM'],
        status=UNDERWRITING_QUEUE_STATUS['PENDING']
    )

    # Save the queue entry
    queue_entry.save()

    # Return the queue entry
    return queue_entry


def create_notification_event(application, event_type, context):
    """
    Creates a notification event for an application status change.

    Args:
        application: The LoanApplication instance
        event_type: The type of notification event
        context: Additional context data for the notification

    Returns:
        NotificationEvent: The created notification event
    """
    # Create a new NotificationEvent with the specified event_type
    notification_event = NotificationEvent(
        event_type=event_type,
        entity_id=application.id,
        entity_type='application',
        context_data=context
    )

    # Set triggered_by to application.modified_by if available
    if hasattr(application, 'updated_by') and application.updated_by:
        notification_event.triggered_by = application.updated_by

    # Save the notification event
    notification_event.save()

    # Return the notification event
    return notification_event