"""
Implements core middleware components for the loan management system, including request ID handling,
exception handling, and utility functions for middleware operations. These middleware components
provide cross-cutting functionality such as request tracing, error handling, and context extraction.
"""

from django.utils.deprecation import MiddlewareMixin  # Django 4.2+
from django.http import JsonResponse  # Django 4.2+
from django.conf import settings  # Django 4.2+
from rest_framework.exceptions import APIException  # DRF 3.14+

from .exceptions import format_exception_response, BaseException
from ..utils.logging import generate_request_id, get_request_logger, mask_pii

# Request ID header name
REQUEST_ID_HEADER = 'X-Request-ID'


def get_client_ip(request):
    """
    Extract the client IP address from the request.
    
    Args:
        request (object): The HTTP request object
        
    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Get the first IP in case of multiple proxies
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_id(request):
    """
    Extract the user ID from the request if the user is authenticated.
    
    Args:
        request (object): The HTTP request object
        
    Returns:
        str: User ID or None if not authenticated
    """
    if hasattr(request, 'user') and request.user.is_authenticated:
        return str(request.user.id)
    return None


class RequestIDMiddleware(MiddlewareMixin):
    """
    Middleware that ensures each request has a unique request ID for tracing and debugging.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware with the get_response function.
        
        Args:
            get_response (callable): The next middleware or view function
        """
        self.get_response = get_response
    
    def __call__(self, request):
        """
        Process the request, ensuring it has a request ID.
        
        Args:
            request (object): The HTTP request object
            
        Returns:
            object: The HTTP response object
        """
        # Check if request already has a request ID
        request_id = request.META.get(REQUEST_ID_HEADER)
        
        # If not, generate a new one
        if not request_id:
            request_id = generate_request_id()
        
        # Store the request ID in the request metadata
        request.META[REQUEST_ID_HEADER] = request_id
        
        # Process the request
        response = self.get_response(request)
        
        # Add the request ID to the response headers
        response[REQUEST_ID_HEADER] = request_id
        
        return response


class ExceptionMiddleware(MiddlewareMixin):
    """
    Middleware that handles exceptions and formats them into consistent JSON responses.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware with the get_response function.
        
        Args:
            get_response (callable): The next middleware or view function
        """
        self.get_response = get_response
    
    def __call__(self, request):
        """
        Process the request and handle any exceptions.
        
        Args:
            request (object): The HTTP request object
            
        Returns:
            object: The HTTP response object
        """
        try:
            return self.get_response(request)
        except BaseException as e:
            # Handle custom exceptions
            error_data = e.to_dict()
            return JsonResponse({'status': 'error', 'error': error_data}, status=e.status_code)
        except APIException as e:
            # Handle DRF API exceptions
            error_data = format_exception_response(
                code=getattr(e, 'code', 'api_error'),
                message=str(e.detail),
                details=getattr(e, 'details', {})
            )
            return JsonResponse({'status': 'error', 'error': error_data}, status=e.status_code)
        except Exception as e:
            # Handle other exceptions as server errors
            error_data = format_exception_response(
                code='server_error',
                message=str(e),
                details={'type': e.__class__.__name__}
            )
            return JsonResponse({'status': 'error', 'error': error_data}, status=500)
    
    def process_exception(self, request, exception):
        """
        Process exceptions that occur during view processing.
        
        Args:
            request (object): The HTTP request object
            exception (Exception): The exception that was raised
            
        Returns:
            object: The HTTP response object or None
        """
        # In DEBUG mode, let Django handle the exception for better debug info
        if settings.DEBUG:
            return None
            
        if isinstance(exception, BaseException):
            # Handle custom exceptions
            error_data = exception.to_dict()
            return JsonResponse({'status': 'error', 'error': error_data}, status=exception.status_code)
        elif isinstance(exception, APIException):
            # Handle DRF API exceptions
            error_data = format_exception_response(
                code=getattr(exception, 'code', 'api_error'),
                message=str(exception.detail),
                details=getattr(exception, 'details', {})
            )
            return JsonResponse({'status': 'error', 'error': error_data}, status=exception.status_code)
        else:
            # Handle other exceptions as server errors
            error_data = format_exception_response(
                code='server_error',
                message=str(exception),
                details={'type': exception.__class__.__name__}
            )
            return JsonResponse({'status': 'error', 'error': error_data}, status=500)


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware stub for audit logging, actual implementation in config.middleware.audit_middleware.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware with the get_response function.
        
        Args:
            get_response (callable): The next middleware or view function
        """
        self.get_response = get_response
    
    def __call__(self, request):
        """
        Process the request and pass through to the actual implementation.
        
        Args:
            request (object): The HTTP request object
            
        Returns:
            object: The HTTP response object
        """
        return self.get_response(request)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware stub for request logging, actual implementation in config.middleware.request_logging_middleware.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware with the get_response function.
        
        Args:
            get_response (callable): The next middleware or view function
        """
        self.get_response = get_response
    
    def __call__(self, request):
        """
        Process the request and pass through to the actual implementation.
        
        Args:
            request (object): The HTTP request object
            
        Returns:
            object: The HTTP response object
        """
        return self.get_response(request)