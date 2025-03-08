"""
Defines custom exception classes and exception handling utilities for the loan management system.

These exceptions provide a standardized way to handle various error scenarios across the application, 
including validation errors, permission issues, resource not found errors, and API-specific exceptions.
"""

from rest_framework import status
from rest_framework.exceptions import APIException as DRFAPIException
from rest_framework.exceptions import ValidationError

from ..utils.logging import log_exception

# Standard error response template
ERROR_RESPONSE_TEMPLATE = {
    'status': 'error',
    'error': {
        'code': None,
        'message': None,
        'details': None
    }
}


def format_exception_response(code, message, details=None):
    """
    Format an exception into a standardized error response structure.
    
    Args:
        code (str): Error code identifier
        message (str): Human-readable error message
        details (dict, optional): Additional error details
        
    Returns:
        dict: Formatted error response dictionary
    """
    response = dict(ERROR_RESPONSE_TEMPLATE)
    response['error']['code'] = code
    response['error']['message'] = message
    if details is not None:
        response['error']['details'] = details
    return response


class BaseException(Exception):
    """
    Base exception class for all custom exceptions in the system.
    
    This class provides common functionality for all custom exceptions,
    including error code, status code, and detailed error information.
    """
    
    def __init__(self, message, details=None):
        """
        Initialize the base exception with message and details.
        
        Args:
            message (str): Human-readable error message
            details (dict, optional): Additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.code = 'error'  # Default error code
        self.status_code = 500  # Default status code
        
        # Log the exception
        log_exception(self)
    
    def to_dict(self):
        """
        Convert the exception to a dictionary representation.
        
        Returns:
            dict: Dictionary representation of the exception
        """
        return {
            'code': self.code,
            'message': self.message,
            'details': self.details
        }
    
    def __str__(self):
        """
        String representation of the exception.
        
        Returns:
            str: String representation
        """
        return f"{self.code}: {self.message} - {self.details}"


class ValidationException(BaseException):
    """
    Exception for validation errors in the application.
    
    This exception is raised when input data fails validation checks.
    """
    
    def __init__(self, message, details=None):
        """
        Initialize the validation exception.
        
        Args:
            message (str): Human-readable error message
            details (dict, optional): Additional error details
        """
        super().__init__(message, details)
        self.code = 'validation_error'
        self.status_code = status.HTTP_400_BAD_REQUEST


class PermissionException(BaseException):
    """
    Exception for permission denied errors.
    
    This exception is raised when a user attempts to access a resource
    or perform an action they don't have permission for.
    """
    
    def __init__(self, message, details=None):
        """
        Initialize the permission exception.
        
        Args:
            message (str): Human-readable error message
            details (dict, optional): Additional error details
        """
        super().__init__(message, details)
        self.code = 'permission_denied'
        self.status_code = status.HTTP_403_FORBIDDEN


class ResourceNotFoundException(BaseException):
    """
    Exception for resource not found errors.
    
    This exception is raised when a requested resource cannot be found.
    """
    
    def __init__(self, message, details=None):
        """
        Initialize the resource not found exception.
        
        Args:
            message (str): Human-readable error message
            details (dict, optional): Additional error details
        """
        super().__init__(message, details)
        self.code = 'not_found'
        self.status_code = status.HTTP_404_NOT_FOUND


class ServiceUnavailableException(BaseException):
    """
    Exception for service unavailable errors.
    
    This exception is raised when a service is temporarily unavailable.
    """
    
    def __init__(self, message, details=None):
        """
        Initialize the service unavailable exception.
        
        Args:
            message (str): Human-readable error message
            details (dict, optional): Additional error details
        """
        super().__init__(message, details)
        self.code = 'service_unavailable'
        self.status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class BadRequestException(BaseException):
    """
    Exception for bad request errors.
    
    This exception is raised when a request is malformed or invalid.
    """
    
    def __init__(self, message, details=None):
        """
        Initialize the bad request exception.
        
        Args:
            message (str): Human-readable error message
            details (dict, optional): Additional error details
        """
        super().__init__(message, details)
        self.code = 'bad_request'
        self.status_code = status.HTTP_400_BAD_REQUEST


class ConflictException(BaseException):
    """
    Exception for conflict errors (e.g., duplicate resources).
    
    This exception is raised when a request conflicts with the current
    state of the resource, such as trying to create a duplicate resource.
    """
    
    def __init__(self, message, details=None):
        """
        Initialize the conflict exception.
        
        Args:
            message (str): Human-readable error message
            details (dict, optional): Additional error details
        """
        super().__init__(message, details)
        self.code = 'conflict'
        self.status_code = status.HTTP_409_CONFLICT


class APIException(DRFAPIException):
    """
    Custom API exception that extends DRF's APIException with additional context.
    
    This exception provides additional context and standardized formatting
    for API-specific errors.
    """
    
    def __init__(self, detail=None, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR):
        """
        Initialize the API exception.
        
        Args:
            detail (str): Error detail message
            status_code (int): HTTP status code for the response
        """
        super().__init__(detail=detail, code=status_code)
        self.code = 'api_error'
        self.details = {}
        
        # Log the exception
        log_exception(self)
    
    def to_dict(self):
        """
        Convert the API exception to a dictionary representation.
        
        Returns:
            dict: Dictionary representation of the exception
        """
        return {
            'code': self.code,
            'message': str(self.detail),
            'details': self.details
        }