import logging  # version standard library

from django.db.models.signals import post_save, pre_save  # Django 4.2+
from django.dispatch import receiver  # Django 4.2+
from django.db import transaction  # Django 4.2+

from .models import UnderwritingDecision, Stipulation, UnderwritingQueue  # src/backend/apps/underwriting/models.py
from ..applications.models import LoanApplication  # src/backend/apps/applications/models.py
from ..notifications.services import NotificationService  # src/backend/apps/notifications/services.py
from ..documents.services import DocumentService  # src/backend/apps/documents/services.py
from ..workflow.services import WorkflowService  # src/backend/apps/workflow/services.py
from ...utils.constants import UNDERWRITING_DECISION, NOTIFICATION_TYPES  # src/backend/utils/constants.py

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize services
notification_service = NotificationService()
document_service = DocumentService()
workflow_service = WorkflowService()


@receiver(post_save, sender=UnderwritingDecision)
def handle_underwriting_decision_created(sender, instance, created, **kwargs):
    """
    Signal handler for when a new underwriting decision is created.
    """
    if created:
        logger.info(f"New underwriting decision created for application {instance.application.id}")

        # Get the associated loan application
        application = instance.application

        # If decision is APPROVE, create approval notification event
        if instance.decision == UNDERWRITING_DECISION['APPROVE']:
            notification_service.create_event_notification(
                event_type=NOTIFICATION_TYPES['APPLICATION_APPROVED'],
                entity=application,
                triggered_by=instance.underwriter
            )

            # Generate commitment letter document
            document_service.generate_document(
                document_type=NOTIFICATION_TYPES['COMMITMENT_LETTER'],
                application=application,
                generated_by=instance.underwriter
            )

        # If decision is DENY, create denial notification event
        elif instance.decision == UNDERWRITING_DECISION['DENY']:
            notification_service.create_event_notification(
                event_type=NOTIFICATION_TYPES['APPLICATION_DENIED'],
                entity=application,
                triggered_by=instance.underwriter
            )

        # If decision is REVISE, create revision request notification event
        elif instance.decision == UNDERWRITING_DECISION['REVISE']:
            notification_service.create_event_notification(
                event_type=NOTIFICATION_TYPES['APPLICATION_REVISION'],
                entity=application,
                triggered_by=instance.underwriter
            )

        # Update application status based on decision
        instance.update_application_status()

        # Transition application workflow state based on decision
        workflow_service.perform_transition(
            entity=application,
            to_state=UNDERWRITING_DECISION[instance.decision],
            user=instance.underwriter,
            reason=f"Underwriting decision: {instance.decision}"
        )


@receiver(post_save, sender=UnderwritingQueue)
def handle_underwriting_queue_updated(sender, instance, created, **kwargs):
    """
    Signal handler for when an underwriting queue item is updated.
    """
    if created:
        # If new, create notification event for application added to queue
        notification_service.create_event_notification(
            event_type=NOTIFICATION_TYPES['APPLICATION_SUBMITTED'],
            entity=instance.application,
            triggered_by=None  # No specific user triggered this
        )
    else:
        # If not new and status changed to ASSIGNED, create notification for underwriter assignment
        if instance.status == 'assigned':
            notification_service.create_event_notification(
                event_type=NOTIFICATION_TYPES['APPLICATION_ASSIGNED'],
                entity=instance.application,
                triggered_by=instance.assigned_to
            )
        # If not new and status changed to IN_PROGRESS, log that review has started
        elif instance.status == 'in_progress':
            logger.info(f"Underwriter {instance.assigned_to} started reviewing application {instance.application.id}")
        # If not new and status changed to COMPLETED, log that review is complete
        elif instance.status == 'completed':
            logger.info(f"Underwriter {instance.assigned_to} completed review of application {instance.application.id}")


@receiver(post_save, sender=Stipulation)
def handle_stipulation_created(sender, instance, created, **kwargs):
    """
    Signal handler for when a new stipulation is created.
    """
    if created:
        # Create notification event for new stipulation
        notification_service.create_event_notification(
            event_type=NOTIFICATION_TYPES['STIPULATION_REQUESTED'],
            entity=instance.application,
            triggered_by=instance.created_by
        )

        # Get the associated loan application
        application = instance.application

        logger.info(f"New stipulation created for application {application.id}")


@receiver(post_save, sender=Stipulation)
def handle_stipulation_satisfied(sender, instance, created, **kwargs):
    """
    Signal handler for when a stipulation is satisfied.
    """
    if not created and instance.status == 'satisfied':
        # Create notification event for stipulation satisfaction
        notification_service.create_event_notification(
            event_type=NOTIFICATION_TYPES['STIPULATION_SATISFIED'],
            entity=instance.application,
            triggered_by=instance.satisfied_by
        )

        # Get the associated loan application
        application = instance.application

        logger.info(f"Stipulation satisfied for application {application.id}")


def connect_signals():
    """
    Function to connect all signal handlers.
    """
    # This function is automatically called when the module is imported
    # Signal handlers are connected via the @receiver decorator
    pass