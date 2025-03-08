"""
Notification system constants for the loan management application.

This module defines constants used throughout the notification system including
notification types, templates, delivery methods, priorities, and configuration
values.
"""

import os  # standard library

from ../../utils.constants import (  # Note: In actual Python code, this would be replaced with a valid import like 'from src.backend.utils.constants import' or an appropriate relative import
    APPLICATION_STATUS,
    DOCUMENT_TYPES,
    DOCUMENT_STATUS,
    SIGNATURE_STATUS,
    FUNDING_STATUS
)

# Notification Type Constants
NOTIFICATION_TYPES = {
    "APPLICATION_SUBMITTED": "application_submitted",
    "APPLICATION_APPROVED": "application_approved",
    "APPLICATION_DENIED": "application_denied",
    "APPLICATION_REVISION": "application_revision",
    "DOCUMENT_READY": "document_ready",
    "SIGNATURE_COMPLETED": "signature_completed",
    "SIGNATURE_REMINDER": "signature_reminder",
    "FUNDING_COMPLETED": "funding_completed",
    "STIPULATION_REQUESTED": "stipulation_requested",
    "COMMITMENT_LETTER": "commitment_letter"
}

# Notification Status Constants
NOTIFICATION_STATUS = {
    "PENDING": "pending",
    "SENT": "sent",
    "FAILED": "failed",
    "CANCELLED": "cancelled"
}

# Notification Delivery Method Constants
NOTIFICATION_DELIVERY_METHODS = {
    "EMAIL": "email",
    "SMS": "sms",
    "PUSH": "push"
}

# Notification Priority Constants
NOTIFICATION_PRIORITIES = {
    "HIGH": "high",
    "MEDIUM": "medium",
    "LOW": "low"
}

# Notification Category Constants
NOTIFICATION_CATEGORIES = {
    "APPLICATION": "application",
    "DOCUMENT": "document",
    "FUNDING": "funding",
    "SYSTEM": "system"
}

# Email Template Mapping
EMAIL_TEMPLATES = {
    "application_submitted": "application_confirmation.html",
    "application_approved": "application_approval.html",
    "application_denied": "application_denial.html",
    "application_revision": "application_revision.html",
    "document_ready": "document_signature_request.html",
    "signature_completed": "signature_completed.html",
    "signature_reminder": "signature_reminder.html",
    "funding_completed": "funding_confirmation.html",
    "stipulation_requested": "stipulation_requested.html",
    "commitment_letter": "commitment_letter.html"
}

# Email Subject Lines
EMAIL_SUBJECTS = {
    "application_submitted": "Your loan application has been submitted",
    "application_approved": "Your loan application has been approved",
    "application_denied": "Important information about your loan application",
    "application_revision": "Action required: Revisions needed for your loan application",
    "document_ready": "Action required: Documents ready for signature",
    "signature_completed": "Document signing completed",
    "signature_reminder": "Reminder: Documents pending signature",
    "funding_completed": "Your loan has been funded",
    "stipulation_requested": "Action required: Additional documentation needed",
    "commitment_letter": "Your loan commitment letter is ready for review"
}

# Email Sender Configuration
EMAIL_SENDER = "noreply@loanmanagementsystem.com"
EMAIL_SENDER_NAME = "Loan Management System"
EMAIL_REPLY_TO = "support@loanmanagementsystem.com"

# Notification Event Mappings
NOTIFICATION_EVENT_MAPPINGS = {
    "application_submitted": {
        "template": "application_submitted",
        "recipients": ["borrower", "school_admin"],
        "priority": "medium",
        "category": "application"
    },
    "application_approved": {
        "template": "application_approved",
        "recipients": ["borrower", "school_admin"],
        "priority": "high",
        "category": "application"
    },
    "application_denied": {
        "template": "application_denied",
        "recipients": ["borrower", "school_admin"],
        "priority": "high",
        "category": "application"
    },
    "application_revision": {
        "template": "application_revision",
        "recipients": ["borrower", "school_admin"],
        "priority": "high",
        "category": "application"
    },
    "document_ready": {
        "template": "document_ready",
        "recipients": ["borrower", "co_borrower", "school_admin"],
        "priority": "high",
        "category": "document"
    },
    "signature_completed": {
        "template": "signature_completed",
        "recipients": ["borrower", "school_admin"],
        "priority": "medium",
        "category": "document"
    },
    "signature_reminder": {
        "template": "signature_reminder",
        "recipients": ["borrower", "co_borrower", "school_admin"],
        "priority": "high",
        "category": "document"
    },
    "funding_completed": {
        "template": "funding_completed",
        "recipients": ["borrower", "school_admin"],
        "priority": "high",
        "category": "funding"
    },
    "stipulation_requested": {
        "template": "stipulation_requested",
        "recipients": ["borrower", "school_admin"],
        "priority": "high",
        "category": "application"
    },
    "commitment_letter": {
        "template": "commitment_letter",
        "recipients": ["school_admin"],
        "priority": "high",
        "category": "document"
    }
}

# Event Types that trigger notifications
EVENT_TYPE = {
    "APPLICATION_STATUS_CHANGE": "application_status_change",
    "DOCUMENT_STATUS_CHANGE": "document_status_change",
    "SIGNATURE_STATUS_CHANGE": "signature_status_change",
    "FUNDING_STATUS_CHANGE": "funding_status_change",
    "STIPULATION_REQUESTED": "stipulation_requested",
    "STIPULATION_SATISFIED": "stipulation_satisfied",
    "DOCUMENT_EXPIRATION_APPROACHING": "document_expiration_approaching"
}

# Notification Processing Configuration
BATCH_SIZE = 50  # Number of notifications to process in one batch
MAX_RETRY_ATTEMPTS = 3  # Maximum number of retry attempts for failed notifications
RETRY_DELAY_SECONDS = 300  # Delay between retry attempts (5 minutes)
REMINDER_SCHEDULE_DAYS = [30, 15, 7, 3, 1]  # Days before deadline to send reminders
NOTIFICATION_RETENTION_DAYS = 90  # Days to retain notification records before cleanup

# Template Directory Configuration
TEMPLATE_DIR = os.path.join('notifications', 'templates')