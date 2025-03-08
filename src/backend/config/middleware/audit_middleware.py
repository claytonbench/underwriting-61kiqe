import re
import json
from django.utils.deprecation import MiddlewareMixin  # Django 4.2+

from utils.logging import get_audit_logger, AuditAdapter
from core.middleware import get_user_id, get_client_ip
from utils.constants import AUDIT_LOG_RETENTION_DAYS

# Paths that contain sensitive operations which should be audited
SENSITIVE_OPERATIONS = ['/login', '/logout', '/password', '/users', '/applications', '/underwriting', '/documents', '/funding', '/schools']

# HTTP methods that indicate state-changing operations which should be audited
SENSITIVE_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']

# Patterns to identify resource types and IDs from URL paths
RESOURCE_PATTERNS = {
    '/users/(\\w+)': 'user',
    '/applications/(\\w+)': 'application',
    '/schools/(\\w+)': 'school',
    '/documents/(\\w+)': 'document',
    '/underwriting/(\\w+)': 'underwriting',
    '/funding/(\\w+)': 'funding'
}


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware that logs security and compliance-related events for audit purposes.
    
    Captures user actions on sensitive operations like authentication, authorization,
    data access, and modifications to critical resources. Ensures comprehensive audit
    trails for regulatory compliance and security monitoring.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware with the get_response function and set up the audit logger.
        
        Args:
            get_response (callable): The next middleware or view function
        """
        self.get_response = get_response
        self.logger = get_audit_logger()
    
    def __call__(self, request):
        """
        Process the request and log audit events for sensitive operations.
        
        Args:
            request (object): The HTTP request object
            
        Returns:
            object: The HTTP response object
        """
        # Determine if this request should be audited
        if self.is_sensitive_operation(request):
            # Extract user ID if available
            user_id = get_user_id(request)
            
            # Extract client IP
            client_ip = get_client_ip(request)
            
            # Determine action type based on path and method
            action = self._determine_action_type(request)
            
            # Identify the resource being accessed
            resource_type, resource_id = self.get_resource_identifier(request.path)
            
            # Create audit event details
            details = {
                'user_id': user_id,
                'ip_address': client_ip,
                'method': request.method,
                'path': request.path,
                'query_params': dict(request.GET),
                'resource_id': resource_id,
                'session_id': request.session.session_key if hasattr(request, 'session') else None,
            }
            
            # For POST/PUT/PATCH requests with JSON body, include summary of request data
            if request.method in ['POST', 'PUT', 'PATCH'] and request.content_type == 'application/json':
                try:
                    # Just include summary of data to avoid sensitive info
                    body_data = json.loads(request.body.decode('utf-8'))
                    # Include only a summary of the data fields, not the values
                    details['request_body_fields'] = list(body_data.keys())
                except Exception:
                    # If there's an error parsing the body, just note that there was a body
                    details['request_body'] = 'Unable to parse request body'
            
            # Log the audit event
            self.log_audit_event(action, resource_type, resource_id, details)
        
        # Process the request
        response = self.get_response(request)
        
        # Additional audit logging for sensitive operations after processing
        if self.is_sensitive_operation(request):
            # Log response status code for sensitive operations
            status_code = getattr(response, 'status_code', None)
            if status_code:
                # Add a filter for this specific log message
                adapter = AuditAdapter(
                    action='response', 
                    resource={'type': 'http_response', 'id': None},
                    details={'status_code': status_code, 'path': request.path, 'method': request.method}
                )
                self.logger.addFilter(adapter)
                
                if 200 <= status_code < 300:
                    self.logger.info(f"Request completed successfully with status {status_code}")
                elif 400 <= status_code < 500:
                    self.logger.warning(f"Request failed with client error {status_code}")
                elif 500 <= status_code < 600:
                    self.logger.error(f"Request failed with server error {status_code}")
                else:
                    self.logger.info(f"Request completed with status {status_code}")
                
                self.logger.removeFilter(adapter)
        
        return response
    
    def is_sensitive_operation(self, request):
        """
        Determine if a request is for a sensitive operation that should be audited.
        
        Args:
            request (object): The HTTP request object
            
        Returns:
            bool: True if the operation is sensitive and should be audited
        """
        # Check if the HTTP method is one we want to audit
        if request.method not in SENSITIVE_METHODS:
            return False
        
        # Check if the path matches any of our sensitive operations
        for operation in SENSITIVE_OPERATIONS:
            if operation in request.path:
                return True
        
        return False
    
    def get_resource_identifier(self, path):
        """
        Extract the resource type and ID from the request path.
        
        Args:
            path (str): The request path
            
        Returns:
            tuple: (resource_type, resource_id) or (None, None) if not identified
        """
        for pattern, resource_type in RESOURCE_PATTERNS.items():
            match = re.search(pattern, path)
            if match:
                resource_id = match.group(1)
                return resource_type, resource_id
        
        # If no specific resource identified, return general category
        for operation in SENSITIVE_OPERATIONS:
            if operation in path:
                return operation.lstrip('/'), None
        
        return None, None
    
    def log_audit_event(self, action, resource_type, resource_id, details):
        """
        Log an audit event with the specified action, resource, and details.
        
        Args:
            action (str): The action being performed (e.g., 'create', 'read', 'update', 'delete')
            resource_type (str): The type of resource being accessed
            resource_id (str): The ID of the resource being accessed
            details (dict): Additional details about the audit event
        """
        # Create audit adapter with context information
        adapter = AuditAdapter(
            action=action, 
            resource={'type': resource_type, 'id': resource_id}, 
            details=details
        )
        
        # Add the adapter as a filter to the logger
        self.logger.addFilter(adapter)
        
        # Log message
        message = f"{action.upper()} operation on {resource_type or 'resource'}"
        if resource_id:
            message += f" {resource_id}"
        
        # Log at the appropriate level based on action type
        if action in ['create', 'update', 'delete']:
            self.logger.info(message)
        elif action == 'access':
            self.logger.debug(message)
        elif action in ['login', 'logout', 'password_reset', 'password_change']:
            self.logger.info(message)
        elif action.startswith('auth_'):
            if action.endswith('_failure'):
                self.logger.warning(message)
            else:
                self.logger.info(message)
        else:
            self.logger.info(message)
        
        # Remove the filter after logging
        self.logger.removeFilter(adapter)
    
    def _determine_action_type(self, request):
        """
        Determine the type of action being performed based on the request.
        
        Args:
            request (object): The HTTP request object
            
        Returns:
            str: The action type
        """
        path = request.path.lower()
        method = request.method.upper()
        
        # Authentication actions
        if '/login' in path:
            return 'auth_login'
        elif '/logout' in path:
            return 'auth_logout'
        elif '/password' in path and 'reset' in path:
            return 'auth_password_reset'
        elif '/password' in path:
            return 'auth_password_change'
        
        # CRUD operations based on HTTP method
        if method == 'POST':
            return 'create'
        elif method == 'PUT' or method == 'PATCH':
            return 'update'
        elif method == 'DELETE':
            return 'delete'
        elif method == 'GET':
            return 'access'
        
        # Default
        return 'operation'