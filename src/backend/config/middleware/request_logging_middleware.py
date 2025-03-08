"""
Middleware that logs HTTP requests and responses for monitoring, debugging, and audit purposes.

This middleware captures detailed information about incoming requests and outgoing responses,
including timing information, while ensuring sensitive data is properly masked to protect
personally identifiable information (PII).
"""

import time
import json
from django.utils.deprecation import MiddlewareMixin  # Django 4.2+
from django.conf import settings  # Django 4.2+

from utils.logging import get_request_logger, mask_pii
from core.middleware import get_user_id, get_client_ip

# Request tracing header
REQUEST_ID_HEADER = 'X-Request-ID'

# Paths containing sensitive information that require extra masking
SENSITIVE_PATHS = ['/login', '/password', '/users', '/applications']

# Paths to exclude from logging entirely (health checks, static files, etc.)
EXCLUDED_PATHS = ['/health', '/metrics', '/static', '/media']

# Maximum length of request/response body to log
MAX_BODY_LENGTH = 10000


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware that logs HTTP requests and responses for monitoring, debugging, and audit purposes.
    
    This middleware captures details about incoming requests and outgoing responses,
    including timing information. It masks sensitive data to ensure PII is not
    exposed in logs while still providing comprehensive information for troubleshooting.
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
        Process the request, log details, and measure response time.
        
        Args:
            request (object): The HTTP request object
            
        Returns:
            object: The HTTP response object
        """
        # Skip logging for excluded paths
        path = request.path
        if any(path.startswith(prefix) for prefix in EXCLUDED_PATHS):
            return self.get_response(request)
        
        # Extract request ID and user ID
        request_id = request.META.get(REQUEST_ID_HEADER)
        user_id = get_user_id(request)
        
        # Get logger with request context
        logger = get_request_logger(request_id, user_id)
        
        # Extract and log request data
        request_data = self.get_request_data(request)
        logger.info(f"Request: {request.method} {path}", extra={"request_data": request_data})
        
        # Record start time
        start_time = time.time()
        
        try:
            # Get response
            response = self.get_response(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Extract and log response data
            response_data = self.get_response_data(response)
            logger.info(
                f"Response: {response.status_code} (Duration: {duration:.3f}s)",
                extra={"response_data": response_data, "duration": duration}
            )
            
            return response
            
        except Exception as e:
            # Log any exceptions during request processing
            duration = time.time() - start_time
            logger.error(
                f"Exception during request processing: {str(e)} (Duration: {duration:.3f}s)",
                extra={"error": str(e), "error_type": e.__class__.__name__, "duration": duration},
                exc_info=True
            )
            raise  # Re-raise the exception for the next middleware to handle
    
    def get_request_data(self, request):
        """
        Extract and format request data for logging.
        
        Args:
            request (object): The HTTP request object
            
        Returns:
            dict: Dictionary containing request details
        """
        request_data = {
            "method": request.method,
            "path": request.path,
            "query_params": dict(request.GET),
            "client_ip": get_client_ip(request),
            "user_agent": request.META.get('HTTP_USER_AGENT', 'Unknown'),
        }
        
        # Add request body for applicable content types and methods
        if request.method in ['POST', 'PUT', 'PATCH'] and hasattr(request, 'body') and request.body:
            try:
                content_type = request.META.get('CONTENT_TYPE', '')
                if 'application/json' in content_type:
                    body = json.loads(request.body.decode('utf-8'))
                    
                    # Truncate if too large
                    body_str = json.dumps(body)
                    if len(body_str) > MAX_BODY_LENGTH:
                        request_data['body_truncated'] = True
                        request_data['body_length'] = len(body_str)
                        # Only log a truncated version of the body
                        body = {"truncated": "Body too large to log completely"}
                    
                    # Mask PII in the body
                    masked_body = mask_pii(body)
                    request_data['body'] = masked_body
                else:
                    # For non-JSON content types, just log the content type and length
                    request_data['body_content_type'] = content_type
                    request_data['body_length'] = len(request.body)
            except json.JSONDecodeError:
                request_data['body_error'] = "Invalid JSON in request body"
            except Exception as e:
                request_data['body_error'] = f"Error processing request body: {str(e)}"
        
        return request_data
    
    def get_response_data(self, response):
        """
        Extract and format response data for logging.
        
        Args:
            response (object): The HTTP response object
            
        Returns:
            dict: Dictionary containing response details
        """
        response_data = {
            "status_code": response.status_code,
            "content_type": response.get('Content-Type', 'Unknown'),
        }
        
        # Add content length if available
        if 'Content-Length' in response:
            response_data['content_length'] = response['Content-Length']
        elif hasattr(response, 'content'):
            response_data['content_length'] = len(response.content)
        
        # Add response body for applicable content types
        if hasattr(response, 'content') and response.content:
            try:
                content_type = response.get('Content-Type', '')
                if 'application/json' in content_type:
                    try:
                        content = response.content.decode('utf-8')
                        body = json.loads(content)
                        
                        # Truncate if too large
                        body_str = json.dumps(body)
                        if len(body_str) > MAX_BODY_LENGTH:
                            response_data['body_truncated'] = True
                            response_data['body_length'] = len(body_str)
                            # Only log a truncated version of the body
                            body = {"truncated": "Body too large to log completely"}
                        
                        # Mask PII in the response
                        masked_body = mask_pii(body)
                        response_data['body'] = masked_body
                    except json.JSONDecodeError:
                        response_data['body_error'] = "Invalid JSON in response body"
                    except UnicodeDecodeError:
                        response_data['body_error'] = "Binary content, not logged"
                else:
                    # For non-JSON content types, just log the content type and length
                    response_data['body_content_type'] = content_type
                    response_data['body_length'] = len(response.content)
            except Exception as e:
                response_data['body_error'] = f"Error processing response body: {str(e)}"
        
        return response_data