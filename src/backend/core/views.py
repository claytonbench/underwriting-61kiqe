"""
Core view classes for the loan management system.

This module defines base view classes that serve as the foundation for all API views
in the loan management system. These base views provide common functionality such as
error handling, response formatting, permission checking, and audit logging to ensure
consistency across the application's API layer.
"""

import logging
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db import transaction

from .exceptions import BaseException, ValidationException, ResourceNotFoundException, format_exception_response
from .serializers import BaseSerializer, BaseModelSerializer
from .permissions import has_object_permission_or_403
from ..utils.logging import get_request_logger

# Configure module logger
logger = logging.getLogger(__name__)

# Standard success response template
SUCCESS_RESPONSE_TEMPLATE = {
    'status': 'success',
    'data': None
}


def format_success_response(data):
    """
    Formats a successful response using the standard template.
    
    Args:
        data: The data to include in the response
        
    Returns:
        dict: Formatted success response dictionary
    """
    response = dict(SUCCESS_RESPONSE_TEMPLATE)
    response['data'] = data
    return response


def get_object_or_exception(queryset, filter_kwargs, exception_class=None, message=None):
    """
    Gets an object from a queryset or raises a custom exception.
    
    Args:
        queryset: The queryset to search
        filter_kwargs: The filter criteria
        exception_class: The exception class to raise if not found (default: ResourceNotFoundException)
        message: The error message
        
    Returns:
        The requested object if found
        
    Raises:
        exception_class: If the object is not found
    """
    try:
        return queryset.get(**filter_kwargs)
    except queryset.model.DoesNotExist:
        if exception_class is None:
            exception_class = ResourceNotFoundException
        raise exception_class(message or f"{queryset.model.__name__} not found")


class BaseAPIView(APIView):
    """
    Base API view class that provides common functionality for all API views.
    
    This class extends DRF's APIView with consistent error handling,
    response formatting, and logging.
    """
    
    logger = None  # Type: logging.Logger
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the base API view with logging.
        """
        super().__init__(*args, **kwargs)
        # Set up logger using get_request_logger
        self.logger = get_request_logger('unknown', None)
    
    def handle_exception(self, exc):
        """
        Override handle_exception to provide consistent error handling.
        
        Args:
            exc (Exception): The exception to handle
            
        Returns:
            Response: Formatted error response
        """
        # Log the exception with appropriate level
        if isinstance(exc, BaseException):
            self.logger.error(f"Handled exception: {exc}", exc_info=True)
            error_data = exc.to_dict()
            status_code = exc.status_code
        elif isinstance(exc, ValidationError):
            self.logger.warning(f"Validation error: {exc}")
            validation_exc = ValidationException(str(exc), exc.detail if hasattr(exc, 'detail') else None)
            error_data = validation_exc.to_dict()
            status_code = validation_exc.status_code
        else:
            self.logger.error(f"Unhandled exception: {exc}", exc_info=True)
            error_data = format_exception_response('server_error', str(exc))
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        # Return formatted error response
        return Response(
            {'status': 'error', 'error': error_data},
            status=status_code
        )
    
    def finalize_response(self, request, response, *args, **kwargs):
        """
        Override finalize_response to ensure consistent response formatting.
        
        Args:
            request (object): The request object
            response (Response): The response object
            *args (dict): Additional arguments
            **kwargs (dict): Additional keyword arguments
            
        Returns:
            Response: Finalized response
        """
        # If response data is not already formatted and status code is 2xx
        if hasattr(response, 'data') and isinstance(response.data, dict) and \
           'status' not in response.data and 200 <= response.status_code < 300:
            response.data = format_success_response(response.data)
        
        # Call parent finalize_response method
        return super().finalize_response(request, response, *args, **kwargs)


class BaseGenericAPIView(GenericAPIView):
    """
    Base generic API view that extends GenericAPIView with common functionality.
    
    This class provides consistent error handling, response formatting,
    permission checking, and logging for generic API views.
    """
    
    logger = None  # Type: logging.Logger
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the base generic API view with logging.
        """
        super().__init__(*args, **kwargs)
        # Set up logger using get_request_logger
        self.logger = get_request_logger('unknown', None)
    
    def handle_exception(self, exc):
        """
        Override handle_exception to provide consistent error handling.
        
        Args:
            exc (Exception): The exception to handle
            
        Returns:
            Response: Formatted error response
        """
        # Log the exception with appropriate level
        if isinstance(exc, BaseException):
            self.logger.error(f"Handled exception: {exc}", exc_info=True)
            error_data = exc.to_dict()
            status_code = exc.status_code
        elif isinstance(exc, ValidationError):
            self.logger.warning(f"Validation error: {exc}")
            validation_exc = ValidationException(str(exc), exc.detail if hasattr(exc, 'detail') else None)
            error_data = validation_exc.to_dict()
            status_code = validation_exc.status_code
        else:
            self.logger.error(f"Unhandled exception: {exc}", exc_info=True)
            error_data = format_exception_response('server_error', str(exc))
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        # Return formatted error response
        return Response(
            {'status': 'error', 'error': error_data},
            status=status_code
        )
    
    def finalize_response(self, request, response, *args, **kwargs):
        """
        Override finalize_response to ensure consistent response formatting.
        
        Args:
            request (object): The request object
            response (Response): The response object
            *args (dict): Additional arguments
            **kwargs (dict): Additional keyword arguments
            
        Returns:
            Response: Finalized response
        """
        # If response data is not already formatted and status code is 2xx
        if hasattr(response, 'data') and isinstance(response.data, dict) and \
           'status' not in response.data and 200 <= response.status_code < 300:
            response.data = format_success_response(response.data)
        
        # Call parent finalize_response method
        return super().finalize_response(request, response, *args, **kwargs)
    
    def get_object(self):
        """
        Override get_object to use custom permission checking.
        
        Returns:
            object: The requested object if found and permitted
        """
        # Get the object using parent get_object method
        obj = super().get_object()
        
        # Check object permissions with each permission class
        for permission in self.get_permissions():
            has_object_permission_or_403(permission, self.request, self, obj)
        
        # Return the object if all permission checks pass
        return obj
    
    def get_serializer_context(self):
        """
        Override get_serializer_context to add request user.
        
        Returns:
            dict: Serializer context dictionary
        """
        # Get context from parent get_serializer_context method
        context = super().get_serializer_context()
        
        # Add request.user to context if available
        if hasattr(self, 'request') and hasattr(self.request, 'user'):
            context['user'] = self.request.user
        
        # Return the updated context dictionary
        return context


class TransactionMixin:
    """
    Mixin that provides database transaction support for views.
    
    This mixin wraps create, update, and delete operations in database
    transactions to ensure data consistency.
    """
    
    def perform_create(self, serializer):
        """
        Override perform_create to wrap in a transaction.
        
        Args:
            serializer (object): The serializer instance
            
        Returns:
            object: Created object
        """
        # Start a database transaction
        with transaction.atomic():
            # Call save on the serializer
            instance = serializer.save()
            
            # Return the created instance
            return instance
    
    def perform_update(self, serializer):
        """
        Override perform_update to wrap in a transaction.
        
        Args:
            serializer (object): The serializer instance
            
        Returns:
            object: Updated object
        """
        # Start a database transaction
        with transaction.atomic():
            # Call save on the serializer
            instance = serializer.save()
            
            # Return the updated instance
            return instance
    
    def perform_destroy(self, instance):
        """
        Override perform_destroy to wrap in a transaction.
        
        Args:
            instance (object): The instance to delete
            
        Returns:
            None: No return value
        """
        # Start a database transaction
        with transaction.atomic():
            # Call delete on the instance
            instance.delete()


class AuditLogMixin:
    """
    Mixin that provides audit logging for view actions.
    
    This mixin adds audit logging for create, update, and delete operations
    to track changes for compliance and security purposes.
    """
    
    def perform_create(self, serializer):
        """
        Override perform_create to add audit logging.
        
        Args:
            serializer (object): The serializer instance
            
        Returns:
            object: Created object
        """
        # Call parent perform_create method (if exists)
        if hasattr(super(), 'perform_create'):
            instance = super().perform_create(serializer)
        else:
            instance = serializer.save()
        
        # Log the creation action
        self.logger.info(
            f"Created {instance.__class__.__name__} with ID {instance.id}",
            extra={
                'action': 'create',
                'resource': instance.__class__.__name__,
                'resource_id': instance.id,
                'user_id': getattr(self.request.user, 'id', None) if hasattr(self, 'request') else None
            }
        )
        
        # Return the created instance
        return instance
    
    def perform_update(self, serializer):
        """
        Override perform_update to add audit logging.
        
        Args:
            serializer (object): The serializer instance
            
        Returns:
            object: Updated object
        """
        # Call parent perform_update method (if exists)
        if hasattr(super(), 'perform_update'):
            instance = super().perform_update(serializer)
        else:
            instance = serializer.save()
        
        # Log the update action
        self.logger.info(
            f"Updated {instance.__class__.__name__} with ID {instance.id}",
            extra={
                'action': 'update',
                'resource': instance.__class__.__name__,
                'resource_id': instance.id,
                'user_id': getattr(self.request.user, 'id', None) if hasattr(self, 'request') else None
            }
        )
        
        # Return the updated instance
        return instance
    
    def perform_destroy(self, instance):
        """
        Override perform_destroy to add audit logging.
        
        Args:
            instance (object): The instance to delete
            
        Returns:
            None: No return value
        """
        # Log the delete action
        self.logger.info(
            f"Deleted {instance.__class__.__name__} with ID {instance.id}",
            extra={
                'action': 'delete',
                'resource': instance.__class__.__name__,
                'resource_id': instance.id,
                'user_id': getattr(self.request.user, 'id', None) if hasattr(self, 'request') else None
            }
        )
        
        # Call parent perform_destroy method (if exists)
        if hasattr(super(), 'perform_destroy'):
            super().perform_destroy(instance)
        else:
            instance.delete()


class ReadOnlyViewMixin:
    """
    Mixin that enforces read-only behavior for views.
    
    This mixin overrides create, update, and delete methods to return
    method not allowed responses, enforcing read-only access.
    """
    
    def create(self, request, *args, **kwargs):
        """
        Override create to prevent creation.
        
        Args:
            request (object): The request object
            *args (dict): Additional arguments
            **kwargs (dict): Additional keyword arguments
            
        Returns:
            Response: Method not allowed response
        """
        return Response(
            {'status': 'error', 'error': {'code': 'method_not_allowed', 'message': 'Method not allowed'}},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def update(self, request, *args, **kwargs):
        """
        Override update to prevent updates.
        
        Args:
            request (object): The request object
            *args (dict): Additional arguments
            **kwargs (dict): Additional keyword arguments
            
        Returns:
            Response: Method not allowed response
        """
        return Response(
            {'status': 'error', 'error': {'code': 'method_not_allowed', 'message': 'Method not allowed'}},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def partial_update(self, request, *args, **kwargs):
        """
        Override partial_update to prevent partial updates.
        
        Args:
            request (object): The request object
            *args (dict): Additional arguments
            **kwargs (dict): Additional keyword arguments
            
        Returns:
            Response: Method not allowed response
        """
        return Response(
            {'status': 'error', 'error': {'code': 'method_not_allowed', 'message': 'Method not allowed'}},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def destroy(self, request, *args, **kwargs):
        """
        Override destroy to prevent deletion.
        
        Args:
            request (object): The request object
            *args (dict): Additional arguments
            **kwargs (dict): Additional keyword arguments
            
        Returns:
            Response: Method not allowed response
        """
        return Response(
            {'status': 'error', 'error': {'code': 'method_not_allowed', 'message': 'Method not allowed'}},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )