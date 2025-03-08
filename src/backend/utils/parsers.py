"""
Utility module providing parsing functions for converting and transforming data between different formats.

This includes parsing form data, query parameters, file content, and API responses to ensure
consistent data handling throughout the loan management system.
"""

import datetime
import decimal
import json
import csv
import io
import re

from utils.validators import ValidationError
from utils.formatters import FormatError
from utils.constants import (
    DATE_FORMAT,
    DATETIME_FORMAT,
    ISO_DATE_FORMAT,
    ISO_DATETIME_FORMAT,
)


class ParseError(Exception):
    """Custom exception class for parsing errors."""
    
    def __init__(self, message):
        """Initialize the ParseError with a message."""
        super().__init__(message)


def parse_date(date_str, format=DATE_FORMAT):
    """
    Parses a string into a date object using the specified format.
    
    Args:
        date_str (str): The date string to parse
        format (str): The format of the date string
        
    Returns:
        datetime.date: A date object parsed from the string
        
    Raises:
        ParseError: If the date string cannot be parsed
    """
    if date_str is None or not date_str.strip():
        return None
    
    try:
        return datetime.datetime.strptime(date_str, format).date()
    except ValueError as e:
        raise ParseError(f"Invalid date format: {e}")


def parse_datetime(datetime_str, format=DATETIME_FORMAT):
    """
    Parses a string into a datetime object using the specified format.
    
    Args:
        datetime_str (str): The datetime string to parse
        format (str): The format of the datetime string
        
    Returns:
        datetime.datetime: A datetime object parsed from the string
        
    Raises:
        ParseError: If the datetime string cannot be parsed
    """
    if datetime_str is None or not datetime_str.strip():
        return None
    
    try:
        return datetime.datetime.strptime(datetime_str, format)
    except ValueError as e:
        raise ParseError(f"Invalid datetime format: {e}")


def parse_standard_date(date_str):
    """
    Parses a string into a date object using the standard application date format.
    
    Args:
        date_str (str): The date string to parse
        
    Returns:
        datetime.date: A date object parsed from the string using standard format
    """
    return parse_date(date_str, DATE_FORMAT)


def parse_standard_datetime(datetime_str):
    """
    Parses a string into a datetime object using the standard application datetime format.
    
    Args:
        datetime_str (str): The datetime string to parse
        
    Returns:
        datetime.datetime: A datetime object parsed from the string using standard format
    """
    return parse_datetime(datetime_str, DATETIME_FORMAT)


def parse_iso_date(date_str):
    """
    Parses an ISO 8601 formatted date string (YYYY-MM-DD) into a date object.
    
    Args:
        date_str (str): The ISO formatted date string to parse
        
    Returns:
        datetime.date: A date object parsed from the ISO formatted string
    """
    return parse_date(date_str, ISO_DATE_FORMAT)


def parse_iso_datetime(datetime_str):
    """
    Parses an ISO 8601 formatted datetime string into a datetime object.
    
    Args:
        datetime_str (str): The ISO formatted datetime string to parse
        
    Returns:
        datetime.datetime: A datetime object parsed from the ISO formatted string
    """
    return parse_datetime(datetime_str, ISO_DATETIME_FORMAT)


def parse_decimal(value):
    """
    Parses a string into a Decimal object for precise financial calculations.
    
    Args:
        value (str): The string value to parse
        
    Returns:
        decimal.Decimal: A Decimal object parsed from the string
        
    Raises:
        ParseError: If the string cannot be parsed into a Decimal
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    
    try:
        # If the value is already a Decimal, return it
        if isinstance(value, decimal.Decimal):
            return value
        
        # If it's a string, clean it before parsing
        if isinstance(value, str):
            # Remove currency symbols, commas, and whitespace
            value = re.sub(r'[$,\s]', '', value)
        
        return decimal.Decimal(str(value))
    except (ValueError, decimal.InvalidOperation) as e:
        raise ParseError(f"Cannot parse value '{value}' as Decimal: {e}")


def parse_currency(currency_str):
    """
    Parses a currency string into a Decimal object.
    
    Args:
        currency_str (str): The currency string to parse
        
    Returns:
        decimal.Decimal: A Decimal object representing the currency amount
    """
    if currency_str is None or not currency_str.strip():
        return None
    
    # Remove currency symbol, commas, and whitespace
    cleaned_str = re.sub(r'[$,\s]', '', currency_str)
    
    return parse_decimal(cleaned_str)


def parse_percentage(percentage_str):
    """
    Parses a percentage string into a Decimal object (as a decimal fraction).
    
    Args:
        percentage_str (str): The percentage string to parse
        
    Returns:
        decimal.Decimal: A Decimal object representing the percentage as a decimal fraction
        
    Raises:
        ParseError: If the percentage string cannot be parsed
    """
    if percentage_str is None or not percentage_str.strip():
        return None
    
    try:
        # Remove percentage symbol and whitespace
        cleaned_str = re.sub(r'[%\s]', '', percentage_str)
        
        # Parse as Decimal
        value = decimal.Decimal(cleaned_str)
        
        # Convert from percentage to decimal fraction (e.g., 5.25% -> 0.0525)
        return value / decimal.Decimal('100')
    except (ValueError, decimal.InvalidOperation) as e:
        raise ParseError(f"Cannot parse value '{percentage_str}' as percentage: {e}")


def parse_boolean(value):
    """
    Parses various string representations into a boolean value.
    
    Args:
        value: The value to parse into a boolean
        
    Returns:
        bool: A boolean value parsed from the input
        
    Raises:
        ParseError: If the value cannot be parsed into a boolean
    """
    if value is None:
        return None
    
    # If it's already a boolean, return it
    if isinstance(value, bool):
        return value
    
    # If it's a string, check common boolean representations
    if isinstance(value, str):
        value = value.lower().strip()
        if value in ('true', 't', 'yes', 'y', '1'):
            return True
        if value in ('false', 'f', 'no', 'n', '0'):
            return False
        
        raise ParseError(f"Cannot parse string '{value}' as boolean")
    
    # If it's a number, treat 0 as False and anything else as True
    if isinstance(value, (int, float)):
        return bool(value)
    
    raise ParseError(f"Cannot parse value of type {type(value)} as boolean")


def parse_int(value):
    """
    Parses a string into an integer value.
    
    Args:
        value (str): The string value to parse
        
    Returns:
        int: An integer value parsed from the string
        
    Raises:
        ParseError: If the string cannot be parsed into an integer
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    
    try:
        # If it's already an int, return it
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        
        # If it's a string, clean it before parsing
        if isinstance(value, str):
            # Remove commas and whitespace
            value = re.sub(r'[,\s]', '', value)
        
        return int(value)
    except ValueError as e:
        raise ParseError(f"Cannot parse value '{value}' as integer: {e}")


def parse_float(value):
    """
    Parses a string into a float value.
    
    Args:
        value (str): The string value to parse
        
    Returns:
        float: A float value parsed from the string
        
    Raises:
        ParseError: If the string cannot be parsed into a float
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    
    try:
        # If it's already a float, return it
        if isinstance(value, float):
            return value
        
        # If it's a string, clean it before parsing
        if isinstance(value, str):
            # Remove commas and whitespace
            value = re.sub(r'[,\s]', '', value)
        
        return float(value)
    except ValueError as e:
        raise ParseError(f"Cannot parse value '{value}' as float: {e}")


def parse_ssn(ssn):
    """
    Parses and normalizes a Social Security Number string.
    
    Args:
        ssn (str): The SSN string to parse
        
    Returns:
        str: A normalized SSN string in XXX-XX-XXXX format
        
    Raises:
        ParseError: If the SSN is invalid
    """
    if ssn is None or not ssn.strip():
        return None
    
    # Remove any non-digit characters
    digits = re.sub(r'\D', '', ssn)
    
    # Check if we have exactly 9 digits
    if len(digits) != 9:
        raise ParseError("SSN must contain exactly 9 digits")
    
    # Format as XXX-XX-XXXX
    return f"{digits[:3]}-{digits[3:5]}-{digits[5:]}"


def parse_phone(phone):
    """
    Parses and normalizes a phone number string.
    
    Args:
        phone (str): The phone number string to parse
        
    Returns:
        str: A normalized phone number string in (XXX) XXX-XXXX format
        
    Raises:
        ParseError: If the phone number is invalid
    """
    if phone is None or not phone.strip():
        return None
    
    # Remove any non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Check if we have exactly 10 digits (or 11 if it starts with 1)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    else:
        raise ParseError("Phone number must contain exactly 10 digits or 11 digits starting with '1'")


def parse_zip_code(zip_code):
    """
    Parses and normalizes a ZIP code string.
    
    Args:
        zip_code (str): The ZIP code string to parse
        
    Returns:
        str: A normalized ZIP code string (either 5 digits or ZIP+4 format)
        
    Raises:
        ParseError: If the ZIP code is invalid
    """
    if zip_code is None or not zip_code.strip():
        return None
    
    # Remove spaces and other non-alphanumeric characters (except hyphen)
    zip_code = re.sub(r'[^\w\-]', '', zip_code)
    
    # Check if it's a 5-digit ZIP
    if re.match(r'^\d{5}$', zip_code):
        return zip_code
    
    # Check if it's a 9-digit ZIP with no hyphen
    if re.match(r'^\d{9}$', zip_code):
        return f"{zip_code[:5]}-{zip_code[5:]}"
    
    # Check if it's already in ZIP+4 format
    if re.match(r'^\d{5}-\d{4}$', zip_code):
        return zip_code
    
    raise ParseError("ZIP code must be in either 5-digit format (12345) or ZIP+4 format (12345-6789)")


def parse_json(json_str):
    """
    Parses a JSON string into a Python object.
    
    Args:
        json_str (str): The JSON string to parse
        
    Returns:
        dict or list: A Python object (dict or list) parsed from the JSON string
        
    Raises:
        ParseError: If the JSON string cannot be parsed
    """
    if json_str is None or (isinstance(json_str, str) and not json_str.strip()):
        return None
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ParseError(f"Invalid JSON: {e}")


def parse_csv(csv_content, field_mapping=None, has_header=True):
    """
    Parses CSV content into a list of dictionaries.
    
    Args:
        csv_content (str or file-like object): The CSV content to parse
        field_mapping (dict): Optional mapping from CSV column names to dictionary keys
        has_header (bool): Whether the CSV has a header row
        
    Returns:
        list: A list of dictionaries representing the CSV rows
        
    Raises:
        ParseError: If the CSV content cannot be parsed
    """
    if csv_content is None:
        return []
    
    try:
        # If csv_content is a string, convert to file-like object
        if isinstance(csv_content, str):
            csv_content = io.StringIO(csv_content)
        
        # Create a CSV reader
        reader = csv.reader(csv_content)
        
        # Get the header row if has_header is True
        header = next(reader) if has_header else None
        
        # Initialize the result list
        results = []
        
        # Process each row
        for row_num, row in enumerate(reader, start=1 if has_header else 0):
            # Skip empty rows
            if not row or all(not cell.strip() for cell in row):
                continue
            
            # Create a dictionary for the row
            if header and not field_mapping:
                # Use header as keys if no field_mapping is provided
                row_dict = {header[i]: value for i, value in enumerate(row) if i < len(header)}
            elif field_mapping:
                # Use field_mapping to create dictionary
                if header:
                    # Map from header names to new names
                    row_dict = {}
                    for i, column in enumerate(header):
                        if i < len(row) and column in field_mapping:
                            row_dict[field_mapping[column]] = row[i]
                else:
                    # Map from column indices to names
                    row_dict = {}
                    for i, value in enumerate(row):
                        if str(i) in field_mapping:
                            row_dict[field_mapping[str(i)]] = value
            else:
                # No header and no field_mapping, use column indices as keys
                row_dict = {i: value for i, value in enumerate(row)}
            
            results.append(row_dict)
        
        return results
    except csv.Error as e:
        raise ParseError(f"Error parsing CSV: {e}")


def parse_query_params(query_params, param_types=None):
    """
    Parses and transforms query parameters based on expected types.
    
    Args:
        query_params (dict): The query parameters to parse
        param_types (dict): A dictionary mapping parameter names to expected types
        
    Returns:
        dict: A dictionary of parsed query parameters with appropriate types
    """
    if query_params is None:
        return {}
    
    if param_types is None:
        # If no types specified, return the original params
        return query_params
    
    result = {}
    
    # Process each parameter according to its expected type
    for param, value in query_params.items():
        if param in param_types:
            param_type = param_types[param]
            
            # Parse according to the specified type
            if param_type == 'int':
                result[param] = parse_int(value)
            elif param_type == 'float':
                result[param] = parse_float(value)
            elif param_type == 'decimal':
                result[param] = parse_decimal(value)
            elif param_type == 'boolean':
                result[param] = parse_boolean(value)
            elif param_type == 'date':
                result[param] = parse_standard_date(value)
            elif param_type == 'datetime':
                result[param] = parse_standard_datetime(value)
            elif param_type == 'iso_date':
                result[param] = parse_iso_date(value)
            elif param_type == 'iso_datetime':
                result[param] = parse_iso_datetime(value)
            else:
                # If the type is not recognized, keep the original value
                result[param] = value
        else:
            # If the parameter doesn't have a specified type, keep the original value
            result[param] = value
    
    return result


def parse_form_data(form_data, field_types=None):
    """
    Parses and transforms form data based on expected types.
    
    Args:
        form_data (dict): The form data to parse
        field_types (dict): A dictionary mapping field names to expected types
        
    Returns:
        dict: A dictionary of parsed form data with appropriate types
    """
    if form_data is None:
        return {}
    
    if field_types is None:
        # If no types specified, return the original data
        return form_data
    
    result = {}
    
    # Process each field according to its expected type
    for field, value in form_data.items():
        if field in field_types:
            field_type = field_types[field]
            
            # Parse according to the specified type
            if field_type == 'int':
                result[field] = parse_int(value)
            elif field_type == 'float':
                result[field] = parse_float(value)
            elif field_type == 'decimal':
                result[field] = parse_decimal(value)
            elif field_type == 'currency':
                result[field] = parse_currency(value)
            elif field_type == 'percentage':
                result[field] = parse_percentage(value)
            elif field_type == 'boolean':
                result[field] = parse_boolean(value)
            elif field_type == 'date':
                result[field] = parse_standard_date(value)
            elif field_type == 'datetime':
                result[field] = parse_standard_datetime(value)
            elif field_type == 'ssn':
                result[field] = parse_ssn(value)
            elif field_type == 'phone':
                result[field] = parse_phone(value)
            elif field_type == 'zip_code':
                result[field] = parse_zip_code(value)
            elif field_type == 'json':
                result[field] = parse_json(value)
            else:
                # If the type is not recognized, keep the original value
                result[field] = value
        else:
            # If the field doesn't have a specified type, keep the original value
            result[field] = value
    
    return result