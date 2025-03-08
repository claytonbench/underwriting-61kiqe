import logging  # Import logging utilities for error and activity logging
from django.dispatch import receiver  # Decorator to register signal handlers
from django.db.models.signals import post_save, pre_save, post_delete  # Signals sent after model instance is saved
from django.db import transaction  # Database transaction management for signal handlers
from django.utils import timezone  # Timezone utilities for handling datetime fields

from .models import Document  # Import Document model for signal handlers
from .models import DocumentPackage  # Import DocumentPackage model for signal handlers
from .models import SignatureRequest  # Import SignatureRequest model for signal handlers
from core.signals import model_change_signal  # Import core signal for model changes
from core.signals import audit_log_signal  # Import core signal for audit logging
from .constants import DOCUMENT_STATUS  # Import document status constants
from .constants import SIGNATURE_STATUS  # Import signature status constants
from .constants import DOCUMENT_PACKAGE_TYPES  # Import document package type constants
from apps.notifications.services import create_notification_event  # Import function to create notification events
from utils.constants import NOTIFICATION_TYPES  # Import notification type constants
from utils.constants import APPLICATION_STATUS  # Import application status constants
from apps.applications.services import update_application_status  # Import function to update application status
from apps.workflow.services import schedule_automatic_transition  # Import function to schedule automatic workflow transitions

# Initialize logger
logger = logging.getLogger('document_signals')

# Define custom signals
document_status_signal = post_save  # Signal emitted when a document's status changes
signature_status_signal = post_save  # Signal emitted when a signature request's status changes
document_package_status_signal = post_save  # Signal emitted when a document package's status changes


@receiver(pre_save, sender=Document)
def handle_document_pre_save(sender, instance, **kwargs):
    """
    Signal handler that runs before a Document is saved to track status changes
    """
    # If this is a new document (no ID), return early as there's no status change
    if not instance.pk:
        return

    try:
        # Try to get the existing document from the database
        existing_document = Document.objects.get(pk=instance.pk)
        # If existing document is found, store its status as instance._previous_status
        instance._previous_status = existing_document.status
    except Document.DoesNotExist:
        # If no existing document is found, set instance._previous_status to None
        instance._previous_status = None
    except Exception as e:
        logger.error(f"Error getting existing document: {e}")

    # Log the status change if there is one
    if hasattr(instance, '_previous_status') and instance._previous_status != instance.status:
        logger.info(f"Document {instance.pk} status changing from {instance._previous_status} to {instance.status}")


@receiver(post_save, sender=Document)
def handle_document_post_save(sender, instance, created, **kwargs):
    """
    Signal handler that runs after a Document is saved to handle status change effects
    """
    # If this is a new document (created=True), emit model_change_signal and return
    if created:
        model_change_signal.send(sender=sender, instance=instance, created=created, **kwargs)
        return

    # Get the previous status from instance._previous_status if it exists
    previous_status = getattr(instance, '_previous_status', None)

    # If status hasn't changed, emit model_change_signal and return
    if previous_status == instance.status:
        model_change_signal.send(sender=sender, instance=instance, created=created, **kwargs)
        return

    # Emit document_status_signal with document, previous_status, new_status, and user
    document_status_signal.send(sender=sender, instance=instance, previous_status=previous_status, new_status=instance.status, **kwargs)

    # Emit model_change_signal for audit logging
    model_change_signal.send(sender=sender, instance=instance, created=created, **kwargs)

    # If status changed to SIGNED, trigger document processing
    if instance.status == DOCUMENT_STATUS['SIGNED']:
        logger.info(f"Document {instance.pk} signed, triggering document processing")
        # TODO: Implement document processing logic here

    # If status changed to COMPLETED, update package status and trigger notifications
    if instance.status == DOCUMENT_STATUS['COMPLETED']:
        logger.info(f"Document {instance.pk} completed, updating package status and triggering notifications")
        instance.package.update_status()
        # TODO: Implement notification logic here

    # If status changed to EXPIRED, update package status and trigger notifications
    if instance.status == DOCUMENT_STATUS['EXPIRED']:
        logger.info(f"Document {instance.pk} expired, updating package status and triggering notifications")
        instance.package.update_status()
        # TODO: Implement notification logic here

    # Update the package status to reflect the document status change
    instance.package.update_status()


@receiver(pre_save, sender=SignatureRequest)
def handle_signature_request_pre_save(sender, instance, **kwargs):
    """
    Signal handler that runs before a SignatureRequest is saved to track status changes
    """
    # If this is a new signature request (no ID), return early as there's no status change
    if not instance.pk:
        return

    try:
        # Try to get the existing signature request from the database
        existing_signature_request = SignatureRequest.objects.get(pk=instance.pk)
        # If existing signature request is found, store its status as instance._previous_status
        instance._previous_status = existing_signature_request.status
    except SignatureRequest.DoesNotExist:
        # If no existing signature request is found, set instance._previous_status to None
        instance._previous_status = None
    except Exception as e:
        logger.error(f"Error getting existing signature request: {e}")

    # Log the status change if there is one
    if hasattr(instance, '_previous_status') and instance._previous_status != instance.status:
        logger.info(f"SignatureRequest {instance.pk} status changing from {instance._previous_status} to {instance.status}")


@receiver(post_save, sender=SignatureRequest)
def handle_signature_request_post_save(sender, instance, created, **kwargs):
    """
    Signal handler that runs after a SignatureRequest is saved to handle status change effects
    """
    # If this is a new signature request (created=True), emit model_change_signal and return
    if created:
        model_change_signal.send(sender=sender, instance=instance, created=created, **kwargs)
        return

    # Get the previous status from instance._previous_status if it exists
    previous_status = getattr(instance, '_previous_status', None)

    # If status hasn't changed, emit model_change_signal and return
    if previous_status == instance.status:
        model_change_signal.send(sender=sender, instance=instance, created=created, **kwargs)
        return

    # Emit signature_status_signal with signature_request, previous_status, new_status, and user
    signature_status_signal.send(sender=sender, instance=instance, previous_status=previous_status, new_status=instance.status, **kwargs)

    # Emit model_change_signal for audit logging
    model_change_signal.send(sender=sender, instance=instance, created=created, **kwargs)

    # If status changed to COMPLETED, check if all signatures for the document are complete
    if instance.status == SIGNATURE_STATUS['COMPLETED']:
        logger.info(f"SignatureRequest {instance.pk} completed, checking if all signatures are complete")
        if check_document_signatures_complete(instance.document):
            instance.document.update_status(DOCUMENT_STATUS['COMPLETED'])

    # If status changed to DECLINED, handle signature declination
    if instance.status == SIGNATURE_STATUS['DECLINED']:
        logger.info(f"SignatureRequest {instance.pk} declined, handling signature declination")
        # TODO: Implement signature declination logic here

    # If status changed to EXPIRED, update document status accordingly
    if instance.status == SIGNATURE_STATUS['EXPIRED']:
        logger.info(f"SignatureRequest {instance.pk} expired, updating document status")
        # TODO: Implement document expiration logic here


@receiver(pre_save, sender=DocumentPackage)
def handle_document_package_pre_save(sender, instance, **kwargs):
    """
    Signal handler that runs before a DocumentPackage is saved to track status changes
    """
    # If this is a new package (no ID), return early as there's no status change
    if not instance.pk:
        return

    try:
        # Try to get the existing package from the database
        existing_package = DocumentPackage.objects.get(pk=instance.pk)
        # If existing package is found, store its status as instance._previous_status
        instance._previous_status = existing_package.status
    except DocumentPackage.DoesNotExist:
        # If no existing package is found, set instance._previous_status to None
        instance._previous_status = None
    except Exception as e:
        logger.error(f"Error getting existing document package: {e}")

    # Log the status change if there is one
    if hasattr(instance, '_previous_status') and instance._previous_status != instance.status:
        logger.info(f"DocumentPackage {instance.pk} status changing from {instance._previous_status} to {instance.status}")


@receiver(post_save, sender=DocumentPackage)
def handle_document_package_post_save(sender, instance, created, **kwargs):
    """
    Signal handler that runs after a DocumentPackage is saved to handle status change effects
    """
    # If this is a new package (created=True), emit model_change_signal and return
    if created:
        model_change_signal.send(sender=sender, instance=instance, created=created, **kwargs)
        return

    # Get the previous status from instance._previous_status if it exists
    previous_status = getattr(instance, '_previous_status', None)

    # If status hasn't changed, emit model_change_signal and return
    if previous_status == instance.status:
        model_change_signal.send(sender=sender, instance=instance, created=created, **kwargs)
        return

    # Emit document_package_status_signal with package, previous_status, new_status, and user
    document_package_status_signal.send(sender=sender, instance=instance, previous_status=previous_status, new_status=instance.status, **kwargs)

    # Emit model_change_signal for audit logging
    model_change_signal.send(sender=sender, instance=instance, created=created, **kwargs)

    # If status changed to COMPLETED, update application status and trigger notifications
    if instance.status == DOCUMENT_STATUS['COMPLETED']:
        logger.info(f"DocumentPackage {instance.pk} completed, updating application status and triggering notifications")
        # TODO: Implement application status update logic here
        # TODO: Implement notification logic here

    # If status changed to EXPIRED, update application status and trigger notifications
    if instance.status == DOCUMENT_STATUS['EXPIRED']:
        logger.info(f"DocumentPackage {instance.pk} expired, updating application status and triggering notifications")
        # TODO: Implement application status update logic here
        # TODO: Implement notification logic here

    # If status changed to SENT, schedule reminder notifications
    if instance.status == DOCUMENT_STATUS['SENT']:
        logger.info(f"DocumentPackage {instance.pk} sent, scheduling reminder notifications")
        # TODO: Implement reminder notification scheduling logic here


@receiver(document_status_signal)
def handle_document_status_change(sender, instance, previous_status, new_status, **kwargs):
    """
    Signal handler for document status changes that triggers appropriate actions
    """
    logger.info(f"Document {instance.pk} status changed from {previous_status} to {new_status}")

    # If status changed to SENT, create notification event for document signature request
    if new_status == DOCUMENT_STATUS['SENT']:
        logger.info(f"Creating notification event for document signature request")
        create_notification_event(
            event_type=NOTIFICATION_TYPES['SIGNATURE_REMINDER'],
            entity=instance,
            triggered_by=None,  # TODO: Determine the appropriate user
            context_data={'document_id': str(instance.id)}
        )

    # If status changed to SIGNED, create notification event for document signing completion
    if new_status == DOCUMENT_STATUS['SIGNED']:
        logger.info(f"Creating notification event for document signing completion")
        create_notification_event(
            event_type=NOTIFICATION_TYPES['SIGNATURE_COMPLETED'],
            entity=instance,
            triggered_by=None,  # TODO: Determine the appropriate user
            context_data={'document_id': str(instance.id)}
        )

    # If status changed to COMPLETED, create notification event for document completion
    if new_status == DOCUMENT_STATUS['COMPLETED']:
        logger.info(f"Creating notification event for document completion")
        create_notification_event(
            event_type=NOTIFICATION_TYPES['DOCUMENT_READY'],
            entity=instance,
            triggered_by=None,  # TODO: Determine the appropriate user
            context_data={'document_id': str(instance.id)}
        )

    # If status changed to EXPIRED, create notification event for document expiration
    if new_status == DOCUMENT_STATUS['EXPIRED']:
        logger.info(f"Creating notification event for document expiration")
        create_notification_event(
            event_type=NOTIFICATION_TYPES['SIGNATURE_REMINDER'],
            entity=instance,
            triggered_by=None,  # TODO: Determine the appropriate user
            context_data={'document_id': str(instance.id)}
        )

    # If status changed to VOIDED, create notification event for document voiding
    if new_status == DOCUMENT_STATUS['VOIDED']:
        logger.info(f"Creating notification event for document voiding")
        # TODO: Implement notification event creation for document voiding


@receiver(signature_status_signal)
def handle_signature_status_change(sender, instance, previous_status, new_status, **kwargs):
    """
    Signal handler for signature request status changes that triggers appropriate actions
    """
    logger.info(f"SignatureRequest {instance.pk} status changed from {previous_status} to {new_status}")

    # If status changed to COMPLETED, create notification event for signature completion
    if new_status == SIGNATURE_STATUS['COMPLETED']:
        logger.info(f"Creating notification event for signature completion")
        create_notification_event(
            event_type=NOTIFICATION_TYPES['SIGNATURE_COMPLETED'],
            entity=instance,
            triggered_by=None,  # TODO: Determine the appropriate user
            context_data={'signature_request_id': str(instance.id)}
        )

    # If status changed to DECLINED, create notification event for signature declination
    if new_status == SIGNATURE_STATUS['DECLINED']:
        logger.info(f"Creating notification event for signature declination")
        # TODO: Implement notification event creation for signature declination

    # If status changed to EXPIRED, create notification event for signature expiration
    if new_status == SIGNATURE_STATUS['EXPIRED']:
        logger.info(f"Creating notification event for signature expiration")
        # TODO: Implement notification event creation for signature expiration


@receiver(document_package_status_signal)
def handle_document_package_status_change(sender, instance, previous_status, new_status, **kwargs):
    """
    Signal handler for document package status changes that triggers appropriate actions
    """
    logger.info(f"DocumentPackage {instance.pk} status changed from {previous_status} to {new_status}")

    # Get the application associated with the package
    application = instance.application

    # If status changed to COMPLETED and package type is COMMITMENT_LETTER, update application status to COMMITMENT_ACCEPTED
    if instance.status == DOCUMENT_STATUS['COMPLETED'] and instance.package_type == DOCUMENT_PACKAGE_TYPES['APPROVAL']:
        logger.info(f"Updating application status to COMMITMENT_ACCEPTED")
        update_application_status(application, APPLICATION_STATUS['COMMITMENT_ACCEPTED'], None, "Commitment letter signed")

    # If status changed to COMPLETED and package type is LOAN_DOCUMENTS, update application status to FULLY_EXECUTED
    if instance.status == DOCUMENT_STATUS['COMPLETED'] and instance.package_type == DOCUMENT_PACKAGE_TYPES['LOAN_AGREEMENT']:
        logger.info(f"Updating application status to FULLY_EXECUTED")
        update_application_status(application, APPLICATION_STATUS['FULLY_EXECUTED'], None, "Loan documents fully executed")

    # If status changed to EXPIRED, update application status to DOCUMENTS_EXPIRED
    if instance.status == DOCUMENT_STATUS['EXPIRED']:
        logger.info(f"Updating application status to DOCUMENTS_EXPIRED")
        update_application_status(application, APPLICATION_STATUS['DOCUMENTS_EXPIRED'], None, "Document package expired")

    # If status changed to VOIDED, update application status appropriately based on package type
    if instance.status == DOCUMENT_STATUS['VOIDED']:
        logger.info(f"Updating application status due to package being voided")
        # TODO: Implement application status update logic based on package type

    # Create appropriate notification events based on the status change and package type
    # TODO: Implement notification event creation based on status change and package type


def update_document_package_status(package):
    """
    Updates the status of a document package based on its documents' statuses
    """
    # Get all documents in the package
    documents = package.get_documents()

    # If no documents, return False
    if not documents.exists():
        return False

    # Check if all documents are in COMPLETED status
    if all(doc.status == DOCUMENT_STATUS['COMPLETED'] for doc in documents):
        package.status = DOCUMENT_STATUS['COMPLETED']
    # Check if any documents are in EXPIRED status
    elif any(doc.status == DOCUMENT_STATUS['EXPIRED'] for doc in documents):
        package.status = DOCUMENT_STATUS['EXPIRED']
    # Check if any documents are in VOIDED status
    elif any(doc.status == DOCUMENT_STATUS['VOIDED'] for doc in documents):
        package.status = DOCUMENT_STATUS['VOIDED']
    else:
        return False

    package.save()
    return True


def check_document_signatures_complete(document):
    """
    Checks if all signature requests for a document are complete
    """
    # Get all signature requests for the document
    signature_requests = document.signature_requests.all()

    # If no signature requests, return False
    if not signature_requests.exists():
        return False

    # Check if all signature requests have status COMPLETED
    return all(sig.status == SIGNATURE_STATUS['COMPLETED'] for sig in signature_requests)


def schedule_signature_reminders(package):
    """
    Schedules reminder notifications for pending signatures
    """
    # Get all documents in the package
    documents = package.get_documents()

    # For each document, get all signature requests with status SENT
    for document in documents:
        signature_requests = document.signature_requests.filter(status=SIGNATURE_STATUS['SENT'])

        # For each pending signature request, schedule a reminder notification
        for signature_request in signature_requests:
            # TODO: Implement reminder notification scheduling logic here
            pass

    logger.info(f"Scheduled signature reminders for document package {package.id}")


def connect_document_signals():
    """
    Connects all document-related signal handlers
    """
    # Connect document_status_signal to handle_document_status_change
    # Connect signature_status_signal to handle_signature_status_change
    # Connect document_package_status_signal to handle_document_package_status_change
    logger.info("Document signals connected")