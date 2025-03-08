"""
Core serializers for the loan management system.

Defines base serializer classes that provide common functionality for all serializers
in the loan management system. These base serializers implement consistent handling of
sensitive data, audit fields, validation, and error formatting across the application's API endpoints.
"""

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model

from ..core.exceptions import ValidationException
from ..utils.encryption import mask_ssn
from ..utils.logging import get_request_logger

# List of fields that should be treated as sensitive
SENSITIVE_FIELDS = ['ssn', 'tax_id', 'account_number', 'routing_number', 'credit_score']


def handle_validation_error(exc):
    """
    Converts DRF ValidationError to custom ValidationException.
    
    Args:
        exc (ValidationError): The DRF validation error
        
    Raises:
        ValidationException: Custom validation exception with error details
    """
    # Extract error details from ValidationError
    error_detail = exc.detail
    
    # Create a ValidationException with the error message and details
    if hasattr(exc, 'get_full_details'):
        details = exc.get_full_details()
    else:
        details = error_detail
    
    # Raise the ValidationException
    raise ValidationException(str(error_detail), details)


class BaseSerializer(serializers.Serializer):
    """
    Base serializer class that provides common functionality for all serializers.
    
    This serializer implements consistent error handling and sensitive data masking
    to ensure security and compliance across the application.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the base serializer with logging.
        """
        super().__init__(*args, **kwargs)
        # Set up logger using get_request_logger
        self.logger = get_request_logger(
            request_id=self.context.get('request_id', 'unknown') 
            if hasattr(self, 'context') and self.context else 'unknown',
            user_id=self.context.get('user_id', None) 
            if hasattr(self, 'context') and self.context else None
        )
    
    def is_valid(self, raise_exception=False):
        """
        Override is_valid to use custom validation error handling.
        
        Args:
            raise_exception (bool): Whether to raise an exception on validation error
            
        Returns:
            bool: True if validation passed, False otherwise
        """
        try:
            # Call parent is_valid method
            return super().is_valid(raise_exception=raise_exception)
        except ValidationError as exc:
            # If ValidationError is raised and raise_exception is True, handle with handle_validation_error
            if raise_exception:
                handle_validation_error(exc)
            # Return False for validation failure
            return False
    
    def handle_sensitive_data(self, data, fields_to_mask=None):
        """
        Masks sensitive data in serialized output.
        
        Args:
            data (dict): The data to process
            fields_to_mask (list): List of field names to mask
            
        Returns:
            dict: Data with sensitive fields masked
        """
        # If fields_to_mask is not provided, use SENSITIVE_FIELDS
        if fields_to_mask is None:
            fields_to_mask = SENSITIVE_FIELDS
        
        # For each sensitive field in the data
        for field in fields_to_mask:
            if field in data:
                # Apply appropriate masking based on field type
                if field == 'ssn':
                    data[field] = mask_ssn(data[field])
                elif field in ['account_number', 'tax_id']:
                    # Show only last 4 characters
                    value = data[field]
                    if value and len(value) > 4:
                        data[field] = f"{'X' * (len(value) - 4)}{value[-4:]}"
                elif field == 'credit_score':
                    # Credit score is not masked, just included in sensitive fields for logging purposes
                    pass
                else:
                    # Default masking for other sensitive fields
                    data[field] = '[REDACTED]'
        
        # Return the data with sensitive fields masked
        return data


class BaseModelSerializer(BaseSerializer, serializers.ModelSerializer):
    """
    Base model serializer that extends BaseSerializer with model-specific functionality.
    
    This serializer adds support for handling audit fields and sensitive data in model instances.
    """
    sensitive_fields = None
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the base model serializer.
        """
        super().__init__(*args, **kwargs)
    
    def to_representation(self, instance):
        """
        Override to_representation to handle sensitive data.
        
        Args:
            instance (object): The model instance
            
        Returns:
            dict: Serialized data with sensitive fields masked
        """
        # Call parent to_representation method to get initial representation
        representation = super().to_representation(instance)
        
        # Get sensitive fields from self.sensitive_fields or default to SENSITIVE_FIELDS
        sensitive_fields = self.sensitive_fields or SENSITIVE_FIELDS
        
        # Call handle_sensitive_data to mask sensitive fields
        representation = self.handle_sensitive_data(representation, sensitive_fields)
        
        # Return the representation with sensitive fields masked
        return representation
    
    def create(self, validated_data):
        """
        Override create to handle audit fields.
        
        Args:
            validated_data (dict): The validated data for creating the instance
            
        Returns:
            object: Created model instance
        """
        # Get the current user from the request context
        request = self.context.get('request') if hasattr(self, 'context') else None
        user = getattr(request, 'user', None) if request else None
        
        # Add created_by field to validated_data if model has this field
        if user and not user.is_anonymous and hasattr(self.Meta.model, 'created_by'):
            validated_data['created_by'] = user
        
        # Add updated_by field to validated_data if model has this field
        if user and not user.is_anonymous and hasattr(self.Meta.model, 'updated_by'):
            validated_data['updated_by'] = user
        
        # Call parent create method with updated validated_data
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Override update to handle audit fields.
        
        Args:
            instance (object): The model instance to update
            validated_data (dict): The validated data for updating the instance
            
        Returns:
            object: Updated model instance
        """
        # Get the current user from the request context
        request = self.context.get('request') if hasattr(self, 'context') else None
        user = getattr(request, 'user', None) if request else None
        
        # Add updated_by field to validated_data if model has this field
        if user and not user.is_anonymous and hasattr(self.Meta.model, 'updated_by'):
            validated_data['updated_by'] = user
        
        # Call parent update method with instance and updated validated_data
        return super().update(instance, validated_data)
    
    def get_fields(self):
        """
        Override get_fields to handle read-only audit fields.
        
        Returns:
            dict: Dictionary of serializer fields
        """
        # Call parent get_fields method to get initial fields
        fields = super().get_fields()
        
        # Make audit fields (created_at, updated_at, created_by, updated_by) read-only
        audit_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
        for field_name in audit_fields:
            if field_name in fields:
                fields[field_name].read_only = True
        
        # Return the updated fields dictionary
        return fields


class ReadOnlyModelSerializer(BaseModelSerializer):
    """
    Model serializer that enforces read-only access to all fields.
    
    This serializer is useful for endpoints that only need to display data
    without allowing modifications.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the read-only model serializer.
        """
        super().__init__(*args, **kwargs)
    
    def get_fields(self):
        """
        Override get_fields to make all fields read-only.
        
        Returns:
            dict: Dictionary of read-only serializer fields
        """
        # Call parent get_fields method to get initial fields
        fields = super().get_fields()
        
        # Set read_only=True for all fields
        for field_name, field in fields.items():
            field.read_only = True
        
        # Return the updated fields dictionary
        return fields


class AuditFieldsMixin:
    """
    Mixin that adds audit fields to a serializer.
    
    This mixin adds created_at, updated_at, created_by, and updated_by fields
    to track when and by whom records were created and modified.
    """
    
    def get_fields(self):
        """
        Override get_fields to add audit fields.
        
        Returns:
            dict: Dictionary of serializer fields with audit fields added
        """
        # Call parent get_fields method to get initial fields
        fields = super().get_fields()
        
        # Add created_at, updated_at fields as read-only DateTimeFields
        if 'created_at' not in fields:
            fields['created_at'] = serializers.DateTimeField(read_only=True)
        
        if 'updated_at' not in fields:
            fields['updated_at'] = serializers.DateTimeField(read_only=True)
        
        # Get the user model
        User = get_user_model()
        
        # Add created_by, updated_by fields as read-only related fields
        if 'created_by' not in fields:
            fields['created_by'] = serializers.PrimaryKeyRelatedField(
                queryset=User.objects.all(),
                read_only=True
            )
        
        if 'updated_by' not in fields:
            fields['updated_by'] = serializers.PrimaryKeyRelatedField(
                queryset=User.objects.all(),
                read_only=True
            )
        
        # Return the updated fields dictionary
        return fields


class SensitiveDataMixin:
    """
    Mixin that handles sensitive data in serializers.
    
    This mixin provides functionality to mask sensitive fields in serialized data
    to ensure security and privacy compliance.
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
        
        # Otherwise return SENSITIVE_FIELDS global variable
        return SENSITIVE_FIELDS