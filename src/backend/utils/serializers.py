"""
Utility module providing reusable serializer components, field types, and helper functions
for Django REST Framework serializers across the loan management system.

This module extends the core serializer functionality with domain-specific serialization needs,
data transformation utilities, and custom field types.
"""

from decimal import Decimal, InvalidOperation
from rest_framework import serializers
from rest_framework.fields import CharField, EmailField, DecimalField
from rest_framework.exceptions import ValidationError

from utils.validators import (
    ValidationError as CustomValidationError,
    validate_ssn,
    validate_phone,
    validate_email,
    validate_zip_code,
    validate_currency_amount
)
from utils.formatters import (
    format_ssn,
    format_phone,
    format_currency,
    format_zip_code
)
from utils.encryption import (
    encrypt_ssn,
    decrypt_ssn,
    mask_ssn
)
from core.serializers import SENSITIVE_FIELDS


# Define loan-related fields that need special formatting
LOAN_SERIALIZER_FIELDS = [
    'requested_amount',
    'approved_amount',
    'tuition_amount',
    'deposit_amount',
    'other_funding',
    'interest_rate'
]


def serialize_currency(value, decimal_places=2):
    """
    Formats a currency value for serialization with proper formatting.
    
    Args:
        value (Union[Decimal, float, int, str]): The currency value to format
        decimal_places (int): Number of decimal places to include
        
    Returns:
        str: Formatted currency string
    """
    if value is None:
        return None
    
    try:
        # Convert to Decimal for precise formatting if it's not already
        if not isinstance(value, Decimal):
            value = Decimal(str(value))
        
        # Format the currency value
        return format_currency(value)
    except (ValueError, TypeError, InvalidOperation):
        # Return original value if formatting fails
        return value


def serialize_ssn(value, mask=True):
    """
    Formats and optionally masks an SSN for serialization.
    
    Args:
        value (str): The SSN to format
        mask (bool): Whether to mask the SSN
        
    Returns:
        str: Formatted and optionally masked SSN
    """
    if value is None:
        return None
    
    try:
        # Check if the SSN is encrypted and decrypt it
        try:
            # This will try to decrypt the value if it's encrypted
            value = decrypt_ssn(value)
        except Exception:
            # If it fails, assume the value is not encrypted
            pass
        
        # Format the SSN
        formatted_ssn = format_ssn(value)
        
        # Apply masking if requested
        if mask:
            return mask_ssn(formatted_ssn)
        
        return formatted_ssn
    except Exception:
        # Return masked placeholder if formatting fails
        return "XXX-XX-XXXX" if mask else value


def serialize_phone(value):
    """
    Formats a phone number for serialization with proper formatting.
    
    Args:
        value (str): The phone number to format
        
    Returns:
        str: Formatted phone number
    """
    if value is None:
        return None
    
    try:
        return format_phone(value)
    except Exception:
        # Return original value if formatting fails
        return value


def serialize_zip_code(value):
    """
    Formats a ZIP code for serialization with proper formatting.
    
    Args:
        value (str): The ZIP code to format
        
    Returns:
        str: Formatted ZIP code
    """
    if value is None:
        return None
    
    try:
        return format_zip_code(value)
    except Exception:
        # Return original value if formatting fails
        return value


class SSNField(CharField):
    """
    Custom serializer field for Social Security Numbers with validation and formatting.
    """
    
    def __init__(self, mask=True, **kwargs):
        """
        Initialize the SSN field with masking option.
        
        Args:
            mask (bool): Whether to mask the SSN in the output
        """
        # Set default parameters for SSN field
        kwargs.setdefault('max_length', 11)  # XXX-XX-XXXX format
        kwargs.setdefault('min_length', 9)   # Allow for non-formatted input
        super().__init__(**kwargs)
        self.mask = mask
    
    def to_internal_value(self, value):
        """
        Convert the input value to a validated SSN.
        
        Args:
            value (str): The input SSN
            
        Returns:
            str: Validated and normalized SSN
        """
        # First perform the CharField validation
        value = super().to_internal_value(value)
        
        if not value:
            return ''
        
        # Remove any formatting characters
        ssn = value.replace('-', '')
        
        try:
            # Validate the SSN
            validate_ssn(ssn)
            return ssn
        except CustomValidationError as e:
            # Convert to DRF ValidationError
            raise ValidationError(str(e))
    
    def to_representation(self, value):
        """
        Convert the internal value to a formatted SSN for output.
        
        Args:
            value (str): The SSN to format
            
        Returns:
            str: Formatted and optionally masked SSN
        """
        if not value:
            return ''
        
        return serialize_ssn(value, self.mask)


class PhoneField(CharField):
    """
    Custom serializer field for phone numbers with validation and formatting.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the phone field.
        """
        # Set default parameters for phone field
        kwargs.setdefault('max_length', 14)  # (XXX) XXX-XXXX format
        kwargs.setdefault('min_length', 10)  # Allow for non-formatted input
        super().__init__(**kwargs)
    
    def to_internal_value(self, value):
        """
        Convert the input value to a validated phone number.
        
        Args:
            value (str): The input phone number
            
        Returns:
            str: Validated and normalized phone number
        """
        # First perform the CharField validation
        value = super().to_internal_value(value)
        
        if not value:
            return ''
        
        # Remove any formatting characters
        phone = ''.join(c for c in value if c.isdigit())
        
        try:
            # Validate the phone number
            validate_phone(phone)
            return phone
        except CustomValidationError as e:
            # Convert to DRF ValidationError
            raise ValidationError(str(e))
    
    def to_representation(self, value):
        """
        Convert the internal value to a formatted phone number for output.
        
        Args:
            value (str): The phone number to format
            
        Returns:
            str: Formatted phone number
        """
        if not value:
            return ''
        
        return serialize_phone(value)


class ZipCodeField(CharField):
    """
    Custom serializer field for ZIP codes with validation and formatting.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the ZIP code field.
        """
        # Set default parameters for ZIP code field
        kwargs.setdefault('max_length', 10)  # XXXXX-XXXX format
        kwargs.setdefault('min_length', 5)   # Allow for non-formatted input
        super().__init__(**kwargs)
    
    def to_internal_value(self, value):
        """
        Convert the input value to a validated ZIP code.
        
        Args:
            value (str): The input ZIP code
            
        Returns:
            str: Validated and normalized ZIP code
        """
        # First perform the CharField validation
        value = super().to_internal_value(value)
        
        if not value:
            return ''
        
        # Remove any formatting characters
        zip_code = value.replace('-', '')
        
        try:
            # Validate the ZIP code
            validate_zip_code(zip_code)
            return zip_code
        except CustomValidationError as e:
            # Convert to DRF ValidationError
            raise ValidationError(str(e))
    
    def to_representation(self, value):
        """
        Convert the internal value to a formatted ZIP code for output.
        
        Args:
            value (str): The ZIP code to format
            
        Returns:
            str: Formatted ZIP code
        """
        if not value:
            return ''
        
        return serialize_zip_code(value)


class CurrencyField(DecimalField):
    """
    Custom serializer field for currency values with validation and formatting.
    """
    
    def __init__(self, decimal_places=2, **kwargs):
        """
        Initialize the currency field with decimal places.
        
        Args:
            decimal_places (int): Number of decimal places for the currency value
        """
        # Set default parameters for currency field
        kwargs.setdefault('max_digits', 12)  # Allow large currency values
        super().__init__(decimal_places=decimal_places, **kwargs)
        self.decimal_places = decimal_places
    
    def to_internal_value(self, value):
        """
        Convert the input value to a validated Decimal.
        
        Args:
            value (Union[str, int, float]): The input currency value
            
        Returns:
            Decimal: Validated currency amount as Decimal
        """
        # First perform the DecimalField validation
        value = super().to_internal_value(value)
        
        try:
            # Validate the currency amount
            validate_currency_amount(value)
            return value
        except CustomValidationError as e:
            # Convert to DRF ValidationError
            raise ValidationError(str(e))
    
    def to_representation(self, value):
        """
        Convert the internal value to a formatted currency string for output.
        
        Args:
            value (Decimal): The currency value to format
            
        Returns:
            str: Formatted currency string
        """
        if value is None:
            return None
        
        return serialize_currency(value, self.decimal_places)


class EncryptedSSNField(CharField):
    """
    Custom serializer field for encrypted Social Security Numbers.
    """
    
    def __init__(self, mask=True, **kwargs):
        """
        Initialize the encrypted SSN field with masking option.
        
        Args:
            mask (bool): Whether to mask the SSN in the output
        """
        # Set default parameters for SSN field
        kwargs.setdefault('max_length', 100)  # Allow enough space for encrypted value
        super().__init__(**kwargs)
        self.mask = mask
    
    def to_internal_value(self, value):
        """
        Convert the input value to a validated and encrypted SSN.
        
        Args:
            value (str): The input SSN
            
        Returns:
            str: Encrypted SSN
        """
        # First perform the CharField validation
        value = super().to_internal_value(value)
        
        if not value:
            return ''
        
        # Remove any formatting characters
        ssn = value.replace('-', '')
        
        try:
            # Validate the SSN
            validate_ssn(ssn)
            
            # Encrypt the SSN
            return encrypt_ssn(ssn)
        except CustomValidationError as e:
            # Convert to DRF ValidationError
            raise ValidationError(str(e))
    
    def to_representation(self, value):
        """
        Convert the encrypted value to a formatted SSN for output.
        
        Args:
            value (str): The encrypted SSN
            
        Returns:
            str: Formatted and optionally masked SSN
        """
        if not value:
            return ''
        
        return serialize_ssn(value, self.mask)


class MaskedEmailField(EmailField):
    """
    Custom serializer field for email addresses with masking for privacy.
    """
    
    def to_internal_value(self, value):
        """
        Convert the input value to a validated email.
        
        Args:
            value (str): The input email
            
        Returns:
            str: Validated email
        """
        # First perform the EmailField validation
        value = super().to_internal_value(value)
        
        try:
            # Validate the email
            validate_email(value)
            return value
        except CustomValidationError as e:
            # Convert to DRF ValidationError
            raise ValidationError(str(e))
    
    def to_representation(self, value):
        """
        Convert the internal value to a masked email for output.
        
        Args:
            value (str): The email to mask
            
        Returns:
            str: Masked email address
        """
        if not value:
            return ''
        
        # Split the email into username and domain parts
        parts = value.split('@')
        if len(parts) != 2:
            return value
        
        username, domain = parts
        
        # Mask the username part except for the first character
        if len(username) > 1:
            masked_username = username[0] + '*' * (len(username) - 1)
        else:
            masked_username = username
        
        # Return the masked email
        return f"{masked_username}@{domain}"


class SensitiveDataMixin:
    """
    Mixin for serializers to handle sensitive data fields with masking.
    """
    
    sensitive_fields = None
    
    def to_representation(self, instance):
        """
        Override to_representation to mask sensitive fields.
        
        Args:
            instance (object): The instance being serialized
            
        Returns:
            dict: Serialized data with sensitive fields masked
        """
        # Call parent to_representation method to get initial representation
        representation = super().to_representation(instance)
        
        # Get sensitive fields from self.get_sensitive_fields()
        sensitive_fields = self.get_sensitive_fields()
        
        # For each sensitive field in the representation
        for field in sensitive_fields:
            if field in representation:
                # Apply appropriate masking based on field type
                if field == 'ssn':
                    representation[field] = mask_ssn(representation[field])
                elif field in ['account_number', 'tax_id']:
                    # Show only last 4 characters
                    value = representation[field]
                    if value and len(value) > 4:
                        representation[field] = f"{'X' * (len(value) - 4)}{value[-4:]}"
                elif field == 'credit_score':
                    # Credit score is not masked, just included in sensitive fields for logging purposes
                    pass
                else:
                    # Default masking for other sensitive fields
                    representation[field] = '[REDACTED]'
        
        # Return the representation with sensitive fields masked
        return representation
    
    def get_sensitive_fields(self):
        """
        Get the list of sensitive fields to mask.
        
        Returns:
            list: List of sensitive field names
        """
        # Return self.sensitive_fields if defined
        if self.sensitive_fields is not None:
            return self.sensitive_fields
        
        # Otherwise return SENSITIVE_FIELDS from core.serializers
        return SENSITIVE_FIELDS


class LoanFieldsMixin:
    """
    Mixin for serializers to handle loan-specific fields with proper formatting.
    """
    
    def to_representation(self, instance):
        """
        Override to_representation to format loan fields.
        
        Args:
            instance (object): The instance being serialized
            
        Returns:
            dict: Serialized data with formatted loan fields
        """
        # Call parent to_representation method to get initial representation
        representation = super().to_representation(instance)
        
        # Format loan fields with proper currency formatting
        for field in LOAN_SERIALIZER_FIELDS:
            if field in representation and representation[field] is not None:
                representation[field] = serialize_currency(representation[field])
        
        # Return the representation with formatted loan fields
        return representation