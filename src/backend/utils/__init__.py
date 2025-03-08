"""
Utility package for the loan management system.

This package provides centralized access to common utilities used throughout the
loan management system, including constants, encryption, validation, logging,
storage, and formatting functions.

Importing from this package allows easy access to frequently used utility
functions without having to know which specific module they are defined in,
promoting code reusability and maintainability.
"""

# Version of the utils package
__version__ = "1.0.0"

# Import all constants
from utils.constants import *

# Import encryption functions for sensitive data
from utils.encryption import encrypt, decrypt, encrypt_ssn, decrypt_ssn, mask_ssn, EncryptedField

# Import validation utilities
from utils.validators import (
    ValidationError, validate_ssn, validate_email, validate_phone,
    validate_zip_code, validate_loan_amount
)

# Import logging utilities
from utils.logging import setup_logger, get_request_logger, get_audit_logger, mask_pii

# Import storage utilities
from utils.storage import S3Storage, generate_presigned_url, StorageError

# Import formatting utilities
from utils.formatters import format_currency, format_ssn, format_phone, format_date, format_percentage

# Define additional constants and functions
VERSION = __version__
API_VERSION = "v1.0"

# Rename US_STATES to STATES for export
STATES = US_STATES

# Define validation function for currency amounts
def validate_currency_amount(amount):
    """
    Validate that a currency amount is a positive number.
    
    Args:
        amount: The currency amount to validate
        
    Returns:
        bool: True if the amount is valid
        
    Raises:
        ValidationError: If the amount is invalid
    """
    from utils.validators import validate_positive_number
    return validate_positive_number(amount)

# Notification types and statuses
NOTIFICATION_TYPES = {
    "APPLICATION_SUBMITTED": "application_submitted",
    "APPLICATION_APPROVED": "application_approved",
    "APPLICATION_DENIED": "application_denied",
    "DOCUMENT_READY": "document_ready",
    "SIGNATURE_REQUESTED": "signature_requested",
    "SIGNATURE_COMPLETED": "signature_completed",
    "FUNDING_COMPLETED": "funding_completed"
}

NOTIFICATION_STATUS = {
    "PENDING": "pending",
    "SENT": "sent",
    "DELIVERED": "delivered",
    "FAILED": "failed"
}

# Standard error messages
ERROR_MESSAGES = {
    "INVALID_INPUT": "Invalid input provided",
    "UNAUTHORIZED": "Unauthorized access",
    "FORBIDDEN": "Forbidden action",
    "NOT_FOUND": "Resource not found",
    "SERVER_ERROR": "Internal server error"
}

# Custom error for formatting
class FormatError(Exception):
    """Custom exception for formatting errors."""
    pass

# Define wrapper functions for formatting
def format_loan_amount(amount):
    """
    Format loan amount with appropriate currency formatting.
    
    Args:
        amount: The loan amount to format
        
    Returns:
        str: Formatted loan amount as currency string
    """
    return format_currency(amount)

def format_interest_rate(rate):
    """
    Format interest rate as percentage string.
    
    Args:
        rate: The interest rate to format (e.g., 0.0525 for 5.25%)
        
    Returns:
        str: Formatted interest rate as percentage string (e.g., "5.25%")
    """
    return format_percentage(rate)

# Define what symbols are exported
__all__ = [
    # Constants
    'VERSION', 'API_VERSION', 'APPLICATION_STATUS', 'DOCUMENT_TYPES', 'DOCUMENT_STATUS',
    'SIGNATURE_STATUS', 'UNDERWRITING_DECISION', 'QC_DECISION', 'FUNDING_STATUS',
    'STIPULATION_STATUS', 'STIPULATION_TYPES', 'USER_TYPES', 'EMPLOYMENT_TYPES',
    'HOUSING_STATUS', 'CITIZENSHIP_STATUS', 'NOTIFICATION_TYPES', 'NOTIFICATION_STATUS',
    'ERROR_MESSAGES', 'STATES',
    # Encryption
    'encrypt', 'decrypt', 'encrypt_ssn', 'decrypt_ssn', 'mask_ssn', 'EncryptedField',
    # Validation
    'ValidationError', 'validate_ssn', 'validate_email', 'validate_phone',
    'validate_zip_code', 'validate_currency_amount', 'validate_loan_amount',
    # Logging
    'setup_logger', 'get_request_logger', 'get_audit_logger', 'mask_pii',
    # Storage
    'S3Storage', 'generate_presigned_url', 'StorageError',
    # Formatting
    'FormatError', 'format_currency', 'format_ssn', 'format_phone', 'format_date',
    'format_loan_amount', 'format_interest_rate'
]