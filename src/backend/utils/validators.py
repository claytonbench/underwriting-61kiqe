"""
Utility module providing validation functions for various data types used throughout the loan management system.

This module includes validation for personal information, financial data, and application-specific requirements
to ensure data integrity and compliance with business rules.
"""

import re
import os
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Any, Union, List

from utils.constants import (
    EMAIL_REGEX, PHONE_REGEX, ZIP_CODE_REGEX, SSN_REGEX, US_STATES,
    MINIMUM_LOAN_AMOUNT, MAXIMUM_LOAN_AMOUNT, PASSWORD_COMPLEXITY_REGEX,
    PASSWORD_MIN_LENGTH
)


class ValidationError(Exception):
    """Custom exception class for validation errors."""
    def __init__(self, message: str):
        """Initialize the ValidationError with a message."""
        super().__init__(message)


def validate_email(email: str) -> bool:
    """
    Validates that an email address matches the required format.
    
    Args:
        email: The email address to validate.
        
    Returns:
        True if the email is valid.
        
    Raises:
        ValidationError: If the email is invalid.
    """
    if email is None or not email.strip():
        raise ValidationError("Email address is required")
    
    if not re.match(EMAIL_REGEX, email):
        raise ValidationError("Email address is not in a valid format")
    
    return True


def validate_phone(phone: str) -> bool:
    """
    Validates that a phone number matches the required format.
    
    Args:
        phone: The phone number to validate.
        
    Returns:
        True if the phone number is valid.
        
    Raises:
        ValidationError: If the phone number is invalid.
    """
    if phone is None or not phone.strip():
        raise ValidationError("Phone number is required")
    
    if not re.match(PHONE_REGEX, phone):
        raise ValidationError("Phone number is not in a valid format. Expected: (XXX) XXX-XXXX")
    
    return True


def validate_ssn(ssn: str) -> bool:
    """
    Validates that a Social Security Number matches the required format.
    
    Args:
        ssn: The SSN to validate.
        
    Returns:
        True if the SSN is valid.
        
    Raises:
        ValidationError: If the SSN is invalid.
    """
    if ssn is None or not ssn.strip():
        raise ValidationError("Social Security Number is required")
    
    if not re.match(SSN_REGEX, ssn):
        raise ValidationError("Social Security Number is not in a valid format. Expected: XXX-XX-XXXX")
    
    return True


def validate_zip_code(zip_code: str) -> bool:
    """
    Validates that a ZIP code matches the required format.
    
    Args:
        zip_code: The ZIP code to validate.
        
    Returns:
        True if the ZIP code is valid.
        
    Raises:
        ValidationError: If the ZIP code is invalid.
    """
    if zip_code is None or not zip_code.strip():
        raise ValidationError("ZIP code is required")
    
    if not re.match(ZIP_CODE_REGEX, zip_code):
        raise ValidationError("ZIP code is not in a valid format. Expected: XXXXX or XXXXX-XXXX")
    
    return True


def validate_state_code(state_code: str) -> bool:
    """
    Validates that a state code is a valid US state abbreviation.
    
    Args:
        state_code: The state code to validate.
        
    Returns:
        True if the state code is valid.
        
    Raises:
        ValidationError: If the state code is invalid.
    """
    if state_code is None or not state_code.strip():
        raise ValidationError("State code is required")
    
    state_code = state_code.strip().upper()
    
    if state_code not in US_STATES:
        raise ValidationError(f"Invalid state code: {state_code}")
    
    return True


def validate_date(date_str: str, format: str = "%Y-%m-%d") -> date:
    """
    Validates that a date string can be parsed into a valid date.
    
    Args:
        date_str: The date string to validate.
        format: The expected date format, defaults to "%Y-%m-%d".
        
    Returns:
        The parsed date object if valid.
        
    Raises:
        ValidationError: If the date string cannot be parsed.
    """
    if date_str is None or not date_str.strip():
        raise ValidationError("Date is required")
    
    try:
        parsed_date = datetime.strptime(date_str, format).date()
        return parsed_date
    except ValueError:
        raise ValidationError(f"Date is not in a valid format. Expected: {format}")


def validate_future_date(date_obj: date) -> bool:
    """
    Validates that a date is in the future.
    
    Args:
        date_obj: The date to validate.
        
    Returns:
        True if the date is in the future.
        
    Raises:
        ValidationError: If the date is not in the future.
    """
    if date_obj is None:
        raise ValidationError("Date is required")
    
    today = date.today()
    
    if date_obj <= today:
        raise ValidationError("Date must be in the future")
    
    return True


def validate_positive_number(value: Union[int, float, Decimal]) -> bool:
    """
    Validates that a number is positive (greater than zero).
    
    Args:
        value: The number to validate.
        
    Returns:
        True if the value is positive.
        
    Raises:
        ValidationError: If the value is not positive.
    """
    if value is None:
        raise ValidationError("Value is required")
    
    try:
        decimal_value = Decimal(str(value))
        
        if decimal_value <= Decimal('0'):
            raise ValidationError("Value must be positive (greater than zero)")
        
        return True
    except (ValueError, TypeError, InvalidOperation):
        raise ValidationError("Value must be a valid number")


def validate_non_negative_number(value: Union[int, float, Decimal]) -> bool:
    """
    Validates that a number is non-negative (greater than or equal to zero).
    
    Args:
        value: The number to validate.
        
    Returns:
        True if the value is non-negative.
        
    Raises:
        ValidationError: If the value is negative.
    """
    if value is None:
        raise ValidationError("Value is required")
    
    try:
        decimal_value = Decimal(str(value))
        
        if decimal_value < Decimal('0'):
            raise ValidationError("Value must be non-negative (greater than or equal to zero)")
        
        return True
    except (ValueError, TypeError, InvalidOperation):
        raise ValidationError("Value must be a valid number")


def validate_loan_amount(amount: Union[int, float, Decimal]) -> bool:
    """
    Validates that a loan amount is within the allowed range.
    
    Args:
        amount: The loan amount to validate.
        
    Returns:
        True if the amount is valid.
        
    Raises:
        ValidationError: If the amount is outside the allowed range.
    """
    if amount is None:
        raise ValidationError("Loan amount is required")
    
    try:
        decimal_amount = Decimal(str(amount))
        
        if decimal_amount < MINIMUM_LOAN_AMOUNT:
            raise ValidationError(f"Loan amount must be at least {MINIMUM_LOAN_AMOUNT}")
        
        if decimal_amount > MAXIMUM_LOAN_AMOUNT:
            raise ValidationError(f"Loan amount cannot exceed {MAXIMUM_LOAN_AMOUNT}")
        
        return True
    except (ValueError, TypeError, InvalidOperation):
        raise ValidationError("Loan amount must be a valid number")


def validate_password(password: str) -> bool:
    """
    Validates that a password meets the required complexity and length requirements.
    
    Args:
        password: The password to validate.
        
    Returns:
        True if the password is valid.
        
    Raises:
        ValidationError: If the password does not meet the requirements.
    """
    if password is None or not password:
        raise ValidationError("Password is required")
    
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValidationError(f"Password must be at least {PASSWORD_MIN_LENGTH} characters long")
    
    if not re.match(PASSWORD_COMPLEXITY_REGEX, password):
        raise ValidationError(
            "Password must contain at least one uppercase letter, one lowercase letter, "
            "one digit, and one special character"
        )
    
    return True


def validate_boolean(value: Any) -> bool:
    """
    Validates that a value is a boolean or can be converted to a boolean.
    
    Args:
        value: The value to validate.
        
    Returns:
        The converted boolean value if valid.
        
    Raises:
        ValidationError: If the value cannot be converted to a boolean.
    """
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        value = value.lower().strip()
        if value in ('true', 't', 'yes', 'y', '1'):
            return True
        if value in ('false', 'f', 'no', 'n', '0'):
            return False
    
    if isinstance(value, (int, float)):
        return bool(value)
    
    raise ValidationError("Value cannot be converted to a boolean")


def validate_in_choices(value: Any, choices: list) -> bool:
    """
    Validates that a value is one of the allowed choices.
    
    Args:
        value: The value to validate.
        choices: The list of allowed choices.
        
    Returns:
        True if the value is in choices.
        
    Raises:
        ValidationError: If the value is not in choices.
    """
    if value is None:
        raise ValidationError("Value is required")
    
    if value not in choices:
        raise ValidationError(f"Value must be one of: {', '.join(str(c) for c in choices)}")
    
    return True


def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """
    Validates that a file has an allowed extension.
    
    Args:
        filename: The filename to validate.
        allowed_extensions: The list of allowed file extensions.
        
    Returns:
        True if the file extension is allowed.
        
    Raises:
        ValidationError: If the file extension is not allowed.
    """
    if filename is None or not filename.strip():
        raise ValidationError("Filename is required")
    
    # Get the file extension (including the dot)
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    
    if ext not in allowed_extensions:
        raise ValidationError(
            f"File extension '{ext}' is not allowed. Allowed extensions: "
            f"{', '.join(allowed_extensions)}"
        )
    
    return True


def validate_file_size(file_size: int, max_size_mb: int) -> bool:
    """
    Validates that a file size is within the allowed limit.
    
    Args:
        file_size: The file size in bytes.
        max_size_mb: The maximum allowed size in megabytes.
        
    Returns:
        True if the file size is within the limit.
        
    Raises:
        ValidationError: If the file size exceeds the limit.
    """
    if file_size is None:
        raise ValidationError("File size is required")
    
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file_size > max_size_bytes:
        raise ValidationError(f"File size exceeds the maximum allowed size of {max_size_mb} MB")
    
    return True