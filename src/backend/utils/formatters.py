"""
Utility module providing formatting functions for various data types used 
throughout the loan management system.

This module includes formatting for currency values, dates, phone numbers, SSNs, 
and other data types to ensure consistent presentation across the application.
"""

import datetime
import re
from decimal import Decimal, InvalidOperation
from typing import Union

from utils.constants import (
    DATE_FORMAT,
    DATETIME_FORMAT,
    CURRENCY_FORMAT,
    PERCENTAGE_FORMAT,
    PHONE_FORMAT,
    SSN_FORMAT,
    SSN_DISPLAY_FORMAT,
    US_STATES
)


def format_currency(value: Union[int, float, Decimal, str, None]) -> str:
    """
    Formats a numeric value as currency with dollar sign and commas.
    
    Args:
        value: The numeric value to format as currency
        
    Returns:
        Formatted currency string or empty string if value is None
    
    Examples:
        >>> format_currency(1000)
        '$1,000.00'
        >>> format_currency(1234.56)
        '$1,234.56'
        >>> format_currency(None)
        ''
    """
    if value is None:
        return ""
    
    try:
        # Convert to Decimal for precise formatting
        decimal_value = Decimal(str(value))
        return CURRENCY_FORMAT.format(decimal_value)
    except (ValueError, TypeError, InvalidOperation):
        # Return empty string if conversion fails
        return ""


def format_percentage(value: Union[int, float, Decimal, str, None]) -> str:
    """
    Formats a numeric value as a percentage with specified decimal places.
    
    Args:
        value: The numeric value to format as percentage
        
    Returns:
        Formatted percentage string or empty string if value is None
    
    Examples:
        >>> format_percentage(0.0525)
        '5.25%'
        >>> format_percentage(1)
        '100.00%'
        >>> format_percentage(None)
        ''
    """
    if value is None:
        return ""
    
    try:
        # Convert to float for percentage formatting
        float_value = float(value) * 100 if float(value) < 1 else float(value)
        return PERCENTAGE_FORMAT.format(float_value)
    except (ValueError, TypeError):
        # Return empty string if conversion fails
        return ""


def format_date(date: Union[datetime.date, datetime.datetime, str, None], 
                format: str = DATE_FORMAT) -> str:
    """
    Formats a date object or string as a date string in the standard format.
    
    Args:
        date: The date to format
        format: The format string to use (default: DATE_FORMAT)
        
    Returns:
        Formatted date string or empty string if date is None
    
    Examples:
        >>> format_date(datetime.date(2023, 5, 15))
        '2023-05-15'
        >>> format_date('2023-05-15')
        '2023-05-15'
        >>> format_date(None)
        ''
    """
    if date is None:
        return ""
    
    try:
        if isinstance(date, str):
            # Try to parse the string as a date
            date = datetime.datetime.strptime(date, format).date()
        elif isinstance(date, datetime.datetime):
            # Convert datetime to date if needed
            date = date.date()
        
        # Format the date using the specified format
        return date.strftime(format)
    except (ValueError, TypeError):
        # Return empty string if conversion fails
        return ""


def format_datetime(dt: Union[datetime.datetime, str, None], 
                   format: str = DATETIME_FORMAT) -> str:
    """
    Formats a datetime object or string as a datetime string in the standard format.
    
    Args:
        dt: The datetime to format
        format: The format string to use (default: DATETIME_FORMAT)
        
    Returns:
        Formatted datetime string or empty string if dt is None
    
    Examples:
        >>> format_datetime(datetime.datetime(2023, 5, 15, 14, 30, 0))
        '2023-05-15 14:30:00'
        >>> format_datetime('2023-05-15 14:30:00')
        '2023-05-15 14:30:00'
        >>> format_datetime(None)
        ''
    """
    if dt is None:
        return ""
    
    try:
        if isinstance(dt, str):
            # Try to parse the string as a datetime
            dt = datetime.datetime.strptime(dt, format)
        
        # Format the datetime using the specified format
        return dt.strftime(format)
    except (ValueError, TypeError):
        # Return empty string if conversion fails
        return ""


def format_phone(phone: Union[str, None]) -> str:
    """
    Formats a phone number string into the standard format (XXX) XXX-XXXX.
    
    Args:
        phone: The phone number to format
        
    Returns:
        Formatted phone number string or empty string if phone is None
    
    Examples:
        >>> format_phone('1234567890')
        '(123) 456-7890'
        >>> format_phone('123-456-7890')
        '(123) 456-7890'
        >>> format_phone(None)
        ''
    """
    if phone is None:
        return ""
    
    # Remove any non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Check if we have exactly 10 digits
    if len(digits) == 10:
        return PHONE_FORMAT.format(*digits)
    
    # Return original string if not 10 digits
    return phone


def format_ssn(ssn: Union[str, None]) -> str:
    """
    Formats a Social Security Number into the standard format XXX-XX-XXXX.
    
    Args:
        ssn: The SSN to format
        
    Returns:
        Formatted SSN string or empty string if ssn is None
    
    Examples:
        >>> format_ssn('123456789')
        '123-45-6789'
        >>> format_ssn('123-45-6789')
        '123-45-6789'
        >>> format_ssn(None)
        ''
    """
    if ssn is None:
        return ""
    
    # Remove any non-digit characters
    digits = re.sub(r'\D', '', ssn)
    
    # Check if we have exactly 9 digits
    if len(digits) == 9:
        return SSN_FORMAT.format(*digits)
    
    # Return original string if not 9 digits
    return ssn


def mask_ssn(ssn: Union[str, None]) -> str:
    """
    Masks a Social Security Number showing only the last 4 digits.
    
    Args:
        ssn: The SSN to mask
        
    Returns:
        Masked SSN string (XXX-XX-1234) or empty string if ssn is None
    
    Examples:
        >>> mask_ssn('123456789')
        'XXX-XX-6789'
        >>> mask_ssn('123-45-6789')
        'XXX-XX-6789'
        >>> mask_ssn(None)
        ''
    """
    if ssn is None:
        return ""
    
    # Remove any non-digit characters
    digits = re.sub(r'\D', '', ssn)
    
    # Check if we have exactly 9 digits
    if len(digits) == 9:
        last_four = digits[5:]
        return SSN_DISPLAY_FORMAT.format(*last_four)
    
    # Return original string if not 9 digits
    return ssn


def format_state_name(state_code: Union[str, None]) -> str:
    """
    Converts a state code to its full name.
    
    Args:
        state_code: The two-letter state code
        
    Returns:
        Full state name or empty string if state_code is None or invalid
    
    Examples:
        >>> format_state_name('CA')
        'California'
        >>> format_state_name('ca')
        'California'
        >>> format_state_name(None)
        ''
    """
    if state_code is None:
        return ""
    
    # Convert to uppercase for consistency
    state_code = state_code.upper()
    
    # Look up the state name in US_STATES dictionary
    return US_STATES.get(state_code, state_code)


def format_name(name: Union[str, None]) -> str:
    """
    Formats a person's name with proper capitalization.
    
    Args:
        name: The name to format
        
    Returns:
        Properly formatted name or empty string if name is None
    
    Examples:
        >>> format_name('john smith')
        'John Smith'
        >>> format_name('mary o\'brien')
        'Mary O'Brien'
        >>> format_name(None)
        ''
    """
    if name is None:
        return ""
    
    # Split the name into parts
    parts = name.strip().split()
    formatted_parts = []
    
    for part in parts:
        # Apply title() for basic capitalization
        formatted = part.title()
        
        # Handle special cases
        if "'" in formatted:
            # Handle names like O'Brien
            pos = formatted.find("'")
            if pos + 1 < len(formatted):
                formatted = formatted[:pos+1] + formatted[pos+1].upper() + formatted[pos+2:]
        elif "mc" in formatted.lower() and len(formatted) > 2:
            # Handle Scottish names like McDonald
            if formatted.lower().startswith("mc"):
                formatted = "Mc" + formatted[2:3].upper() + formatted[3:]
        elif "mac" in formatted.lower() and len(formatted) > 3:
            # Handle Scottish names like MacDonald
            if formatted.lower().startswith("mac"):
                formatted = "Mac" + formatted[3:4].upper() + formatted[4:]
                
        formatted_parts.append(formatted)
    
    # Join the parts back together
    return " ".join(formatted_parts)


def format_address(address_line1: Union[str, None], 
                  address_line2: Union[str, None] = None,
                  city: Union[str, None] = None,
                  state: Union[str, None] = None,
                  zip_code: Union[str, None] = None) -> str:
    """
    Formats an address with proper capitalization and formatting.
    
    Args:
        address_line1: The first line of the address
        address_line2: The second line of the address (optional)
        city: The city (optional)
        state: The state code (optional)
        zip_code: The ZIP code (optional)
        
    Returns:
        Formatted address string
    
    Examples:
        >>> format_address("123 main st", None, "anytown", "CA", "12345")
        '123 Main St, Anytown, California 12345'
    """
    if address_line1 is None:
        return ""
    
    # Format address components
    address_parts = []
    
    # Format address line 1 with proper capitalization
    address_parts.append(" ".join(word.capitalize() for word in address_line1.split()))
    
    # Add address line 2 if provided
    if address_line2:
        address_parts.append(" ".join(word.capitalize() for word in address_line2.split()))
    
    # Combine city, state, and zip
    location_parts = []
    
    if city:
        location_parts.append(format_name(city))
    
    if state:
        location_parts.append(format_state_name(state))
    
    if zip_code:
        location_parts.append(zip_code)
    
    # Add the location to the address parts if we have any
    if location_parts:
        address_parts.append(", ".join(location_parts))
    
    # Join all parts with appropriate separators
    return ", ".join(address_parts)


def format_boolean(value: Union[bool, str, int, None]) -> str:
    """
    Formats a boolean value as 'Yes' or 'No'.
    
    Args:
        value: The boolean value to format
        
    Returns:
        'Yes', 'No', or empty string if value is None
    
    Examples:
        >>> format_boolean(True)
        'Yes'
        >>> format_boolean('true')
        'Yes'
        >>> format_boolean(0)
        'No'
        >>> format_boolean(None)
        ''
    """
    if value is None:
        return ""
    
    # Handle string values
    if isinstance(value, str):
        return "Yes" if value.lower() in ('true', 'yes', 'y', '1') else "No"
    
    # Handle numeric values
    if isinstance(value, (int, float)):
        return "Yes" if value else "No"
    
    # Handle boolean values
    return "Yes" if value else "No"


def format_status(status: Union[str, None]) -> str:
    """
    Formats a status code into a human-readable format.
    
    Args:
        status: The status code to format
        
    Returns:
        Human-readable status string or empty string if status is None
    
    Examples:
        >>> format_status('application_submitted')
        'Application Submitted'
        >>> format_status('PENDING_REVIEW')
        'Pending Review'
        >>> format_status(None)
        ''
    """
    if status is None:
        return ""
    
    # Replace underscores with spaces and capitalize
    return status.replace('_', ' ').title()


def truncate_text(text: Union[str, None], max_length: int) -> str:
    """
    Truncates text to a specified length with ellipsis.
    
    Args:
        text: The text to truncate
        max_length: The maximum length of the truncated text
        
    Returns:
        Truncated text string or empty string if text is None
    
    Examples:
        >>> truncate_text("This is a long text that needs to be truncated", 20)
        'This is a long text...'
        >>> truncate_text("Short text", 20)
        'Short text'
        >>> truncate_text(None, 20)
        ''
    """
    if text is None:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."