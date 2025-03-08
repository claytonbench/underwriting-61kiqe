# src/backend/apps/qc/signals.py
from django.db.models.signals import post_save, pre_save  # Django 4.2+
from django.dispatch import receiver  # Django 4.2+
from django.db import transaction  # Django 4.2+
from django.utils import timezone  # Django 4.2+

from .models import QCReview, DocumentVerification, QCStipulationVerification  # Importing QCReview model
from .constants import QC_STATUS, QC_STATUS_TO_APPLICATION_STATUS, QC_APPROVAL_TO_FUNDING_STATUS  # Importing QC status constants
from ..funding.models import FundingRequest  # Importing FundingRequest model
from ..funding.constants import FUNDING_REQUEST_STATUS  # Importing funding request status constants
from ..notifications.models import NotificationEvent  # Importing NotificationEvent model
from ..notifications.constants import EVENT_TYPE  # Importing notification event type constants
from ..applications.models import LoanApplication  # Importing LoanApplication model


@receiver(pre_save, sender=QCReview)
def handle_qc_review_pre_save(sender, instance, **kwargs):
    """
    Signal handler that runs before a QCReview is saved to store the original status for comparison
    """
    if not instance.pk:
        return

    try:
        original_instance = QCReview.objects.get(pk=instance.pk)
        instance._original_status = original_instance.status
    except QCReview.DoesNotExist:
        pass


@receiver(post_save, sender=QCReview)
def handle_qc_review_post_save(sender, instance, created, **kwargs):
    """
    Signal handler that runs after a QCReview is saved to handle status changes
    """
    if created:
        create_qc_notification_event(
            event_type=EVENT_TYPE['APPLICATION_STATUS_CHANGE'],
            qc_review=instance,
            context_data={'status': instance.status}
        )
    else:
        if hasattr(instance, '_original_status') and instance._original_status != instance.status:
            LoanApplication.objects.filter(pk=instance.application.pk).update(status=QC_STATUS_TO_APPLICATION_STATUS[instance.status])
            create_qc_notification_event(
                event_type=EVENT_TYPE['APPLICATION_STATUS_CHANGE'],
                qc_review=instance,
                context_data={'status': instance.status}
            )

            if instance.status == QC_STATUS['APPROVED']:
                with transaction.atomic():
                    if not FundingRequest.objects.filter(application=instance.application).exists():
                        funding_request = FundingRequest.objects.create(
                            application=instance.application,
                            status=QC_APPROVAL_TO_FUNDING_STATUS[instance.status],
                            requested_amount=instance.application.loan_details.requested_amount,
                            requested_by=instance.assigned_to
                        )
                        create_qc_notification_event(
                            event_type=EVENT_TYPE['FUNDING_STATUS_CHANGE'],
                            qc_review=instance,
                            context_data={'status': funding_request.status}
                        )


@receiver(post_save, sender=DocumentVerification)
def handle_document_verification_post_save(sender, instance, created, **kwargs):
    """
    Signal handler that runs after a DocumentVerification is saved
    """
    if created:
        return

    qc_review = instance.qc_review

    if qc_review.status == QC_STATUS['IN_REVIEW'] and qc_review.is_complete():
        qc_review.save()


@receiver(post_save, sender=QCStipulationVerification)
def handle_stipulation_verification_post_save(sender, instance, created, **kwargs):
    """
    Signal handler that runs after a QCStipulationVerification is saved
    """
    if created:
        return

    qc_review = instance.qc_review

    if qc_review.status == QC_STATUS['IN_REVIEW'] and qc_review.is_complete():
        qc_review.save()


def create_qc_notification_event(event_type, qc_review, context_data=None):
    """
    Helper function to create notification events for QC-related actions
    """
    context = {
        'application_id': qc_review.application.id,
        'qc_review_id': qc_review.id,
        'qc_status': qc_review.status
    }

    if context_data:
        context.update(context_data)

    notification_event = NotificationEvent.objects.create(
        event_type=event_type,
        entity_id=qc_review.application.id,
        entity_type='application',
        triggered_by=qc_review.assigned_to,
        context_data=context
    )

    return notification_event