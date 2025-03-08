"""
Defines Django signal handlers for funding-related events in the loan management system.
These signals enable event-driven communication between the funding module and other system components,
triggering notifications, application status updates, and audit logging when funding status changes occur.
"""

import logging  # standard library

from django.dispatch import receiver  # django
from django.db.models import signals  # django
from django.db.models.signals import post_save, pre_save  # django

from ...core.signals import model_change_signal, audit_log_signal  # core
from ...utils.logging import get_audit_logger  # utils
from ..notifications.services import NotificationService  # notifications
from ..notifications.constants import EVENT_TYPE  # notifications
from ..workflow.state_machine import FundingStateMachine, ApplicationStateMachine  # workflow
from .models import FundingRequest, Disbursement, EnrollmentVerification, StipulationVerification  # funding
from .constants import (  # funding
    FUNDING_REQUEST_STATUS,
    DISBURSEMENT_STATUS,
    FUNDING_STATUS_REQUIRING_NOTIFICATION,
    FUNDING_STATUS_TRANSITIONS_TO_APPLICATION_STATUS
)

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize audit logger
audit_logger = get_audit_logger()

# Initialize notification service
notification_service = NotificationService()

# Initialize state machines
funding_state_machine = FundingStateMachine()
application_state_machine = ApplicationStateMachine()


@receiver(pre_save, sender=FundingRequest)
def funding_request_pre_save(sender, instance, **kwargs):
    """
    Signal handler that runs before a FundingRequest is saved to capture the previous state.

    Args:
        sender: The model class
        instance: The model instance that is about to be saved
        kwargs: Additional keyword arguments

    Returns:
        None
    """
    if instance.id:  # Existing object
        try:
            # Get the existing object from the database
            existing_instance = FundingRequest.objects.get(id=instance.id)
            # Store the previous status as _previous_status on the instance
            instance._previous_status = existing_instance.status
        except FundingRequest.DoesNotExist:
            # If the object doesn't exist yet, set _previous_status to None
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=FundingRequest)
def funding_request_post_save(sender, instance, created, **kwargs):
    """
    Signal handler that runs after a FundingRequest is saved to handle status changes.

    Args:
        sender: The model class
        instance: The model instance that was saved
        created: Boolean indicating if this is a new instance
        kwargs: Additional keyword arguments

    Returns:
        None
    """
    if created:
        model_change_signal.send(sender=sender, instance=instance, created=True, user=instance.updated_by)
    else:
        # Check if the status has changed
        if hasattr(instance, '_previous_status') and instance._previous_status != instance.status:
            # Log the status change
            logger.info(f"FundingRequest status changed from {instance._previous_status} to {instance.status} for ID {instance.id}")

            # Emit model_change_signal with 'updated' action
            model_change_signal.send(sender=sender, instance=instance, created=False, user=instance.updated_by,
                                     update_fields=['status'])

            # If status is in FUNDING_STATUS_REQUIRING_NOTIFICATION, send notification
            if instance.status in FUNDING_STATUS_REQUIRING_NOTIFICATION:
                send_funding_notification(instance, 'funding_status_changed', instance.updated_by)

            # Update the application status
            if instance.status in FUNDING_STATUS_TRANSITIONS_TO_APPLICATION_STATUS:
                application_state_machine.handle_funding_status_change(
                    instance.application, instance._previous_status, instance.status, instance.updated_by
                )


@receiver(pre_save, sender=Disbursement)
def disbursement_pre_save(sender, instance, **kwargs):
    """
    Signal handler that runs before a Disbursement is saved to capture the previous state.

    Args:
        sender: The model class
        instance: The model instance that is about to be saved
        kwargs: Additional keyword arguments

    Returns:
        None
    """
    if instance.id:  # Existing object
        try:
            # Get the existing object from the database
            existing_instance = Disbursement.objects.get(id=instance.id)
            # Store the previous status as _previous_status on the instance
            instance._previous_status = existing_instance.status
        except Disbursement.DoesNotExist:
            # If the object doesn't exist yet, set _previous_status to None
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=Disbursement)
def disbursement_post_save(sender, instance, created, **kwargs):
    """
    Signal handler that runs after a Disbursement is saved to handle status changes.

    Args:
        sender: The model class
        instance: The model instance that was saved
        created: Boolean indicating if this is a new instance
        kwargs: Additional keyword arguments

    Returns:
        None
    """
    if created:
        model_change_signal.send(sender=sender, instance=instance, created=True, user=instance.updated_by)
    else:
        # Check if the status has changed
        if hasattr(instance, '_previous_status') and instance._previous_status != instance.status:
            # Log the status change
            logger.info(f"Disbursement status changed from {instance._previous_status} to {instance.status} for ID {instance.id}")

            # Emit model_change_signal with 'updated' action
            model_change_signal.send(sender=sender, instance=instance, created=False, user=instance.updated_by,
                                     update_fields=['status'])

            # If status changed to DISBURSEMENT_STATUS['COMPLETED'], call funding_state_machine.process_disbursement
            if instance.status == DISBURSEMENT_STATUS['COMPLETED']:
                funding_state_machine.process_disbursement(instance.funding_request)

            # If status changed to DISBURSEMENT_STATUS['CANCELLED'], update the funding request status accordingly
            if instance.status == DISBURSEMENT_STATUS['CANCELLED']:
                instance.funding_request.status = FUNDING_REQUEST_STATUS['CANCELLED']
                instance.funding_request.save()


@receiver(post_save, sender=EnrollmentVerification)
def enrollment_verification_post_save(sender, instance, created, **kwargs):
    """
    Signal handler that runs after an EnrollmentVerification is saved.

    Args:
        sender: The model class
        instance: The model instance that was saved
        created: Boolean indicating if this is a new instance
        kwargs: Additional keyword arguments

    Returns:
        None
    """
    # Emit model_change_signal with appropriate action ('created' or 'updated')
    model_change_signal.send(sender=sender, instance=instance, created=created, user=instance.updated_by)

    # If this is a new verification (created=True), call funding_state_machine.handle_enrollment_verification
    if created:
        funding_state_machine.handle_enrollment_verification(instance.funding_request)

    # Log the enrollment verification event
    audit_logger.info(f"Enrollment verification {'created' if created else 'updated'} for FundingRequest ID {instance.funding_request.id}")


@receiver(post_save, sender=StipulationVerification)
def stipulation_verification_post_save(sender, instance, created, **kwargs):
    """
    Signal handler that runs after a StipulationVerification is saved.

    Args:
        sender: The model class
        instance: The model instance that was saved
        created: Boolean indicating if this is a new instance
        kwargs: Additional keyword arguments

    Returns:
        None
    """
    # Emit model_change_signal with appropriate action ('created' or 'updated')
    model_change_signal.send(sender=sender, instance=instance, created=created, user=instance.updated_by)

    # Check if all stipulations for the funding request are now verified
    if check_all_stipulations_verified(instance.stipulation.application):
        # If all stipulations are verified, call funding_state_machine.handle_stipulation_verification
        funding_state_machine.handle_stipulation_verification(instance.stipulation.application.get_funding_request())

    # Log the stipulation verification event
    audit_logger.info(f"Stipulation verification {'created' if created else 'updated'} for Stipulation ID {instance.stipulation.id}")


def send_funding_notification(funding_request, event_type, triggered_by):
    """
    Helper function to send notifications for funding-related events.

    Args:
        funding_request (FundingRequest): The FundingRequest instance
        event_type (str): The event type to send
        triggered_by (User): The user who triggered the event

    Returns:
        list: List of created notifications
    """
    # Prepare context data with funding request information
    context = {
        'funding_request_id': str(funding_request.id),
        'funding_status': funding_request.status,
        'application_id': str(funding_request.application.id)
    }

    # Call notification_service.create_event_notification with the event type, funding request, user, and context
    notifications = notification_service.create_event_notification(
        event_type=event_type,
        entity=funding_request,
        triggered_by=triggered_by,
        context_data=context
    )

    # Return the list of created notifications
    return notifications


def check_all_stipulations_verified(application):
    """
    Helper function to check if all stipulations for a funding request are verified.

    Args:
        application (LoanApplication): The LoanApplication instance

    Returns:
        bool: True if all stipulations are verified, False otherwise
    """
    # Get all stipulations for the funding request's application
    stipulations = application.stipulation_set.all()

    # Get all stipulation verifications for the funding request
    funding_request = application.get_funding_request()
    if not funding_request:
        return False

    verifications = funding_request.stipulationverification_set.all()

    # Check if each stipulation has a verification with status 'verified' or 'waived'
    for stipulation in stipulations:
        if not any(verification.stipulation_id == stipulation.id and
                   verification.status in ['verified', 'waived'] for verification in verifications):
            return False

    # Return True if all stipulations are verified or waived
    return True


def connect_funding_signals():
    """
    Function to connect all funding-related signals.

    Returns:
        None
    """
    # Connect funding_request_pre_save to pre_save signal for FundingRequest
    # Connect funding_request_post_save to post_save signal for FundingRequest
    # Connect disbursement_pre_save to pre_save signal for Disbursement
    # Connect disbursement_post_save to post_save signal for Disbursement
    # Connect enrollment_verification_post_save to post_save signal for EnrollmentVerification
    # Connect stipulation_verification_post_save to post_save signal for StipulationVerification

    logger.info("Funding signals connected")