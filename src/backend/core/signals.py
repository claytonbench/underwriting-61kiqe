"""
Defines core Django signals and signal-related utilities for the loan management system.

These signals provide a centralized event system for tracking model changes, user actions,
and audit events across the application, enabling loose coupling between components
while maintaining data consistency and audit trails.
"""

import logging
from django.dispatch import Signal, receiver
from django.utils import timezone
from django.contrib.auth import get_user_model

from utils.logging import get_audit_logger, mask_pii

# Set up loggers
logger = logging.getLogger('core.signals')
audit_logger = get_audit_logger()

# Define custom signals
model_change_signal = Signal(providing_args=['instance', 'created', 'user'])
audit_log_signal = Signal(providing_args=['instance', 'action', 'user', 'details'])


def log_user_action(user, action, resource, details):
    """
    Log a user action for audit purposes.

    Args:
        user: The user performing the action
        action: The action being performed (e.g., 'create', 'read', 'update', 'delete')
        resource: The resource being acted upon (e.g., 'application', 'document')
        details: Additional details about the action

    Returns:
        None
    """
    try:
        # Mask any PII in the details
        masked_details = mask_pii(details) if details else {}
        
        # Get user ID for logging, use 'system' if no user provided
        user_id = getattr(user, 'id', 'system') if user else 'system'
        
        # Prepare the audit log entry
        log_entry = {
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'details': masked_details,
            'timestamp': timezone.now().isoformat()
        }
        
        # Log the action using the audit logger
        audit_logger.info(f"User {user_id} performed {action} on {resource}", extra=log_entry)
        
        # Emit the audit log signal
        audit_log_signal.send(
            sender=__name__,
            instance=None,
            action=action,
            user=user,
            details=details
        )
    except Exception as e:
        logger.error(f"Error logging user action: {str(e)}")


@receiver(model_change_signal)
def handle_model_change(sender, instance, created=False, user=None, **kwargs):
    """
    Signal handler for model changes that logs the change and emits audit events.

    Args:
        sender: The model class
        instance: The model instance that was changed
        created: Boolean indicating if this is a new instance
        user: The user who made the change
        **kwargs: Additional arguments

    Returns:
        None
    """
    try:
        # Determine the action type
        if 'deleted' in kwargs and kwargs['deleted']:
            action = 'delete'
        elif created:
            action = 'create'
        else:
            action = 'update'
        
        # Get model information
        model_name = sender.__name__
        model_id = getattr(instance, 'id', None)
        
        # Prepare the details dictionary
        details = {
            'model': model_name,
            'id': model_id,
        }
        
        # For updates, include the changed fields if available
        if action == 'update' and 'update_fields' in kwargs:
            details['changed_fields'] = kwargs['update_fields']
        
        # Log the action
        log_user_action(user, action, f"{model_name.lower()}", details)
        
        # Log additional debug information
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                f"Model change: {action} on {model_name} (id={model_id}) by user {getattr(user, 'id', 'system')}"
            )
    except Exception as e:
        logger.error(f"Error handling model change: {str(e)}")


def connect_core_signals():
    """
    Connect core signal handlers to their respective signals.

    This function is called during application initialization to ensure
    all signal handlers are properly connected.

    Returns:
        None
    """
    # The handle_model_change is already connected via decorator
    # Connect any additional signal handlers here as needed
    
    logger.info("Core signals connected")