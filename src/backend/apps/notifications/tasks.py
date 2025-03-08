"""
Defines Celery tasks for asynchronous notification processing in the loan management system.

This module includes tasks for sending individual notifications, processing notification batches,
handling notification events, scheduling reminders, and cleaning up old notification records.
"""

import logging
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from django.conf import settings

from ../../config.celery import app
from .models import Notification, NotificationEvent
from .email import send_notification_email, process_notification_batch
from .services import process_pending_events
from .constants import (
    NOTIFICATION_STATUS,
    BATCH_SIZE,
    MAX_RETRY_ATTEMPTS,
    RETRY_DELAY_SECONDS,
    NOTIFICATION_RETENTION_DAYS
)
from ../../utils.logging import get_audit_logger

# Set up loggers
logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()

@app.task
def send_notification(notification_id):
    """
    Celery task to send a single notification asynchronously.
    
    Args:
        notification_id (UUID): The ID of the notification to send
        
    Returns:
        bool: True if notification was sent successfully, False otherwise
    """
    try:
        # Retrieve the notification by ID
        notification = Notification.objects.get(id=notification_id)
        
        # Log the notification sending attempt
        logger.info(f"Sending notification {notification_id}")
        
        # Send the notification
        result = send_notification_email(notification)
        
        # Log the result
        if result:
            logger.info(f"Successfully sent notification {notification_id}")
            audit_logger.info(
                "Notification sent successfully",
                extra={
                    'notification_id': str(notification_id),
                    'recipient_type': notification.recipient.user_type,
                    'template_type': notification.template.notification_type
                }
            )
        else:
            logger.error(f"Failed to send notification {notification_id}")
        
        return result
    except Notification.DoesNotExist:
        logger.error(f"Notification with ID {notification_id} not found")
        return False
    except Exception as e:
        logger.exception(f"Error sending notification {notification_id}: {str(e)}")
        return False

@app.task
def process_notification_queue():
    """
    Celery task to process pending notifications in batches.
    
    Returns:
        dict: Statistics about processed notifications
    """
    try:
        # Query for pending notifications
        pending_notifications = Notification.objects.filter(
            status=NOTIFICATION_STATUS['PENDING']
        ).order_by('created_at')
        
        total_count = pending_notifications.count()
        logger.info(f"Processing {total_count} pending notifications")
        
        if total_count == 0:
            return {'sent': 0, 'failed': 0, 'total': 0}
        
        # Initialize counters for tracking progress
        processed_count = 0
        sent_count = 0
        failed_count = 0
        
        # Process in batches to avoid memory issues
        while processed_count < total_count:
            # Get the next batch
            batch = pending_notifications[processed_count:processed_count+BATCH_SIZE]
            
            # Process the batch
            result = process_notification_batch(batch)
            
            # Update counters
            sent_count += result['sent']
            failed_count += result['failed']
            processed_count += BATCH_SIZE if processed_count + BATCH_SIZE < total_count else total_count
            
            logger.info(f"Processed batch: {result['sent']} sent, {result['failed']} failed")
        
        # Log overall statistics
        logger.info(f"Notification queue processing completed: {sent_count} sent, {failed_count} failed, {total_count} total")
        audit_logger.info(
            "Notification queue processed",
            extra={
                'sent_count': sent_count,
                'failed_count': failed_count,
                'total_count': total_count
            }
        )
        
        # Return statistics
        return {
            'sent': sent_count,
            'failed': failed_count,
            'total': total_count
        }
    except Exception as e:
        logger.exception(f"Error processing notification queue: {str(e)}")
        return {
            'sent': 0,
            'failed': 0,
            'total': 0,
            'error': str(e)
        }

@app.task
def retry_failed_notifications():
    """
    Celery task to retry failed notifications.
    
    Returns:
        dict: Statistics about retry attempts
    """
    try:
        # Query for failed notifications that can be retried
        failed_notifications = Notification.objects.filter(
            status=NOTIFICATION_STATUS['FAILED'],
            retry_count__lt=MAX_RETRY_ATTEMPTS
        )
        
        total_count = failed_notifications.count()
        logger.info(f"Attempting to retry {total_count} failed notifications")
        
        retried_count = 0
        
        # Process in a transaction to ensure consistency
        with transaction.atomic():
            for notification in failed_notifications:
                # Check if notification can be retried
                if notification.can_retry(MAX_RETRY_ATTEMPTS):
                    # Mark for retry
                    notification.mark_retry()
                    
                    # Queue for sending
                    send_notification.delay(notification.id)
                    
                    retried_count += 1
        
        # Log statistics
        logger.info(f"Queued {retried_count} of {total_count} failed notifications for retry")
        audit_logger.info(
            "Failed notifications retry attempt",
            extra={
                'retried_count': retried_count,
                'total_count': total_count
            }
        )
        
        # Return statistics
        return {
            'retried': retried_count,
            'total': total_count
        }
    except Exception as e:
        logger.exception(f"Error retrying failed notifications: {str(e)}")
        return {
            'retried': 0,
            'total': 0,
            'error': str(e)
        }

@app.task
def process_notification_events():
    """
    Celery task to process pending notification events.
    
    Returns:
        dict: Statistics about processed events and created notifications
    """
    try:
        # Call the service function to process pending events
        result = process_pending_events()
        
        # Log statistics
        logger.info(f"Processed {result.get('events_processed', 0)} events, created {result.get('notifications_created', 0)} notifications")
        audit_logger.info(
            "Notification events processed",
            extra={
                'events_processed': result.get('events_processed', 0),
                'notifications_created': result.get('notifications_created', 0)
            }
        )
        
        return result
    except Exception as e:
        logger.exception(f"Error processing notification events: {str(e)}")
        return {
            'events_processed': 0,
            'notifications_created': 0,
            'error': str(e)
        }

@app.task
def schedule_signature_reminders():
    """
    Celery task to schedule reminder notifications for pending signatures.
    
    This task identifies document packages with pending signatures that are approaching
    their expiration date and creates reminder notifications for the signers.
    
    Returns:
        int: Number of reminders scheduled
    """
    try:
        # Import document-related models here to avoid circular imports
        from ..documents.models import DocumentPackage, SignatureRequest
        from .constants import REMINDER_SCHEDULE_DAYS
        from .services import send_immediate_notification
        
        # Find document packages with pending signatures
        pending_packages = DocumentPackage.objects.filter(
            status__in=['sent', 'partially_executed']
        )
        
        reminder_count = 0
        today = timezone.now().date()
        
        # Process each package
        for package in pending_packages:
            # Skip packages without expiration date
            if not package.expiration_date:
                continue
                
            # Calculate days until expiration
            days_until_expiration = (package.expiration_date - today).days
            
            # Skip if not in reminder schedule
            if days_until_expiration not in REMINDER_SCHEDULE_DAYS:
                continue
                
            # Get pending signatures for this package
            pending_signatures = SignatureRequest.objects.filter(
                document__package=package,
                status='pending'
            )
            
            # For each pending signature, create a reminder notification
            for signature in pending_signatures:
                # Skip if signer is None
                if not signature.signer:
                    continue
                    
                # Get application from package
                application = package.application
                
                # Prepare context data
                context = {
                    'recipient_name': f"{signature.signer.first_name} {signature.signer.last_name}",
                    'days_remaining': days_until_expiration,
                    'expiration_date': package.expiration_date.strftime('%B %d, %Y'),
                    'document_type': signature.document.document_type,
                    'package_id': str(package.id),
                    'application_id': str(application.id) if application else None,
                    'signature_url': signature.get_signing_url() if hasattr(signature, 'get_signing_url') else None
                }
                
                # Create and send reminder notification
                success = send_immediate_notification(
                    notification_type='signature_reminder',
                    recipient=signature.signer,
                    context=context,
                    application=application
                )
                
                if success:
                    reminder_count += 1
        
        # Log statistics
        logger.info(f"Scheduled {reminder_count} signature reminder notifications")
        audit_logger.info(
            "Signature reminders scheduled",
            extra={
                'reminder_count': reminder_count
            }
        )
        
        return reminder_count
    except Exception as e:
        logger.exception(f"Error scheduling signature reminders: {str(e)}")
        return 0

@app.task
def cleanup_old_notifications():
    """
    Celery task to delete old notification records.
    
    This task identifies and deletes notifications that are older than the retention
    period defined in NOTIFICATION_RETENTION_DAYS.
    
    Returns:
        int: Number of notifications deleted
    """
    try:
        # Calculate cutoff date
        cutoff_date = timezone.now() - timedelta(days=NOTIFICATION_RETENTION_DAYS)
        
        # Query for old notifications
        old_notifications = Notification.objects.filter(
            created_at__lt=cutoff_date
        )
        
        # Count how many we're going to delete
        total_count = old_notifications.count()
        logger.info(f"Found {total_count} notifications older than {NOTIFICATION_RETENTION_DAYS} days to delete")
        
        if total_count == 0:
            return 0
        
        # Delete in batches to avoid performance issues
        batch_size = 1000
        deleted_count = 0
        
        while deleted_count < total_count:
            # Get batch IDs to delete
            batch_ids = list(old_notifications.values_list('id', flat=True)[deleted_count:deleted_count+batch_size])
            
            # Delete this batch
            batch_deleted, _ = Notification.objects.filter(id__in=batch_ids).delete()
            deleted_count += batch_deleted
            
            logger.info(f"Deleted batch of {batch_deleted} old notifications")
        
        # Log final count
        logger.info(f"Deleted {deleted_count} old notifications")
        audit_logger.info(
            "Old notifications cleanup",
            extra={
                'deleted_count': deleted_count,
                'retention_days': NOTIFICATION_RETENTION_DAYS
            }
        )
        
        return deleted_count
    except Exception as e:
        logger.exception(f"Error cleaning up old notifications: {str(e)}")
        return 0