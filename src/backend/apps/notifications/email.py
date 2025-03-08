"""
Email delivery functionality for the loan management system's notification component.

This module integrates with SendGrid for reliable email delivery, providing template rendering,
batch processing, and delivery status tracking for the notification system.
"""

import logging  # standard library
from sendgrid import SendGridAPIClient  # sendgrid 6.9.0+
from sendgrid.helpers.mail import Mail  # sendgrid 6.9.0+
from django.conf import settings  # Django 4.2+
from django.db import transaction  # Django 4.2+

from .models import Notification, NotificationTemplate
from .constants import (
    EMAIL_SENDER, 
    EMAIL_SENDER_NAME, 
    EMAIL_REPLY_TO,
    NOTIFICATION_STATUS,
    MAX_RETRY_ATTEMPTS
)
from ../../utils.logging import get_audit_logger, mask_pii

# Set up loggers
logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()

def send_notification_email(notification):
    """
    Sends an email notification using SendGrid.
    
    Args:
        notification (Notification): The notification object to send
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Extract recipient email from notification
    recipient_email = notification.recipient_email
    
    # Extract subject and body from notification
    subject = notification.subject
    html_content = notification.body
    
    # Create a SendGrid Mail object
    message = Mail(
        from_email=(EMAIL_SENDER, EMAIL_SENDER_NAME),
        to_emails=recipient_email,
        subject=subject,
        html_content=html_content
    )
    
    # Set reply-to address
    message.reply_to = EMAIL_REPLY_TO
    
    try:
        # Initialize SendGrid client with API key from settings
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        
        # Send the email
        response = sg.send(message)
        
        # Check if the email was sent successfully (status code 2xx)
        if 200 <= response.status_code < 300:
            # Mark notification as sent
            notification.mark_sent()
            
            # Log success
            logger.info(f"Email sent successfully to {mask_pii(recipient_email)}, notification ID: {notification.id}")
            audit_logger.info(
                f"Email notification sent",
                extra={
                    'notification_id': str(notification.id),
                    'recipient_type': notification.recipient.user_type if notification.recipient else 'unknown',
                    'email_masked': mask_pii(recipient_email),
                    'template_type': notification.template.notification_type if notification.template else 'unknown'
                }
            )
            
            return True
        else:
            # Log the error
            error_message = f"SendGrid API returned status code {response.status_code}"
            logger.error(f"Failed to send email: {error_message}")
            
            # Mark notification as failed
            notification.mark_failed(error_message)
            return False
            
    except Exception as e:
        # Handle exceptions
        error_message = f"Error sending email: {str(e)}"
        logger.exception(error_message)
        
        # Mark notification as failed
        notification.mark_failed(error_message)
        return False

def process_notification_batch(queryset):
    """
    Processes a batch of notifications for delivery.
    
    Args:
        queryset: QuerySet of Notification objects to process
        
    Returns:
        dict: Statistics about the processed batch (sent, failed, total)
    """
    sent_count = 0
    failed_count = 0
    total_count = queryset.count()
    
    for notification in queryset:
        success = send_notification_email(notification)
        if success:
            sent_count += 1
        else:
            failed_count += 1
    
    logger.info(f"Batch processing completed: {sent_count} sent, {failed_count} failed, {total_count} total")
    
    return {
        'sent': sent_count,
        'failed': failed_count,
        'total': total_count
    }

class EmailDeliveryService:
    """
    Service class for handling email delivery operations.
    """
    
    def __init__(self):
        """
        Initializes the email delivery service with SendGrid credentials.
        """
        self.api_key = settings.SENDGRID_API_KEY
        self.client = SendGridAPIClient(self.api_key)
        logger.info("EmailDeliveryService initialized")
    
    def send_email(self, to_email, subject, html_content, from_email=None, from_name=None, reply_to=None):
        """
        Sends an individual email using SendGrid.
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            html_content (str): Email body in HTML format
            from_email (str, optional): Sender email address
            from_name (str, optional): Sender name
            reply_to (str, optional): Reply-to email address
            
        Returns:
            tuple: (bool, str) - Success status and error message if any
        """
        # Set default values if not provided
        from_email = from_email or EMAIL_SENDER
        from_name = from_name or EMAIL_SENDER_NAME
        reply_to = reply_to or EMAIL_REPLY_TO
        
        # Create a SendGrid Mail object
        message = Mail(
            from_email=(from_email, from_name),
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        # Set reply-to address
        message.reply_to = reply_to
        
        try:
            # Send the email
            response = self.client.send(message)
            
            # Log the delivery attempt with masked PII
            logger.info(f"Email sent to {mask_pii(to_email)}, status code: {response.status_code}")
            audit_logger.info(
                "Email sent",
                extra={
                    'recipient': mask_pii(to_email),
                    'status_code': response.status_code
                }
            )
            
            # Check if the email was sent successfully (status code 2xx)
            if 200 <= response.status_code < 300:
                return True, ""
            else:
                error_message = f"SendGrid API returned status code {response.status_code}"
                return False, error_message
                
        except Exception as e:
            error_message = f"Error sending email: {str(e)}"
            logger.exception(error_message)
            return False, error_message
    
    def send_notification(self, notification):
        """
        Sends an email for a notification record.
        
        Args:
            notification (Notification): The notification object to send
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        # Extract recipient email, subject, and body from notification
        recipient_email = notification.recipient_email
        subject = notification.subject
        html_content = notification.body
        
        # Send the email
        success, error_message = self.send_email(
            to_email=recipient_email,
            subject=subject,
            html_content=html_content
        )
        
        # Update notification status based on result
        if success:
            notification.mark_sent()
            return True
        else:
            notification.mark_failed(error_message)
            return False
    
    def process_batch(self, queryset):
        """
        Processes a batch of notifications for delivery.
        
        Args:
            queryset: QuerySet of Notification objects to process
            
        Returns:
            dict: Statistics about the processed batch (sent, failed, total)
        """
        sent_count = 0
        failed_count = 0
        total_count = queryset.count()
        
        # Use transaction to ensure consistency
        with transaction.atomic():
            for notification in queryset:
                success = self.send_notification(notification)
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
        
        # Log batch processing statistics
        logger.info(f"Batch processing completed: {sent_count} sent, {failed_count} failed, {total_count} total")
        
        return {
            'sent': sent_count,
            'failed': failed_count,
            'total': total_count
        }
    
    def get_delivery_status(self, message_id):
        """
        Retrieves delivery status for a sent email.
        
        Args:
            message_id (str): The SendGrid message ID
            
        Returns:
            dict: Delivery status information from SendGrid
        """
        try:
            # Call SendGrid API to get message status
            # Note: This is a placeholder for the actual implementation
            # SendGrid's v3 API doesn't directly support message status queries
            # This would require a custom implementation or use of SendGrid's Event Webhook
            
            # For now, return a placeholder response
            return {
                'message_id': message_id,
                'status': 'unknown',
                'reason': 'Status tracking requires SendGrid Event Webhook configuration'
            }
        except Exception as e:
            logger.exception(f"Error retrieving delivery status: {str(e)}")
            return {
                'message_id': message_id,
                'status': 'error',
                'reason': str(e)
            }

class SendGridEmailBackend:
    """
    Email backend implementation using SendGrid.
    """
    
    def __init__(self, **kwargs):
        """
        Initializes the SendGrid email backend.
        
        Args:
            **kwargs: Additional configuration options
        """
        self.delivery_service = EmailDeliveryService()
    
    def send_messages(self, email_messages):
        """
        Sends a list of email messages.
        
        Args:
            email_messages (list): List of EmailMessage objects
            
        Returns:
            int: Number of successfully sent messages
        """
        if not email_messages:
            return 0
        
        sent_count = 0
        
        for message in email_messages:
            # Convert Django EmailMessage to SendGrid format
            to_email = message.to[0] if message.to else None
            if not to_email:
                continue
                
            subject = message.subject
            html_content = message.body
            
            # Get from_email and reply_to from Django EmailMessage
            from_email = message.from_email
            reply_to = message.extra_headers.get('Reply-To') if message.extra_headers else None
            
            # Send using the delivery service
            success, _ = self.delivery_service.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                from_email=from_email,
                reply_to=reply_to
            )
            
            if success:
                sent_count += 1
        
        return sent_count