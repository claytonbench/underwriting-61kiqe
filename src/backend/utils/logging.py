"""
Logging utilities for the loan management system.

This module provides comprehensive logging utilities including structured logging,
PII masking, audit logging, and request tracking capabilities to support security,
compliance, and operational monitoring requirements.
"""

import logging
import os
import sys
import uuid
import json
import re
from datetime import datetime
from django.conf import settings  # Django 4.2+

from utils.constants import AUDIT_LOG_RETENTION_DAYS

# Global configuration
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
REQUEST_ID_HEADER = 'X-Request-ID'

# PII detection and masking patterns
PII_PATTERNS = {
    "ssn": r"\d{3}-\d{2}-\d{4}",
    "credit_card": r"\d{4}-\d{4}-\d{4}-\d{4}",
    "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "phone": r"\(\d{3}\) \d{3}-\d{4}"
}

PII_REPLACEMENTS = {
    "ssn": "XXX-XX-****",
    "credit_card": "XXXX-XXXX-XXXX-****",
    "email": "****@****.com",
    "phone": "(XXX) XXX-****"
}


class JsonFormatter(logging.Formatter):
    """
    Custom log formatter that outputs logs in JSON format for structured logging.
    """
    
    def __init__(self):
        """Initialize the JSON formatter."""
        super().__init__()
        self.default_msec_format = '%s.%03d'
    
    def format(self, record):
        """
        Format the log record as a JSON string.
        
        Args:
            record (logging.LogRecord): The log record to format
            
        Returns:
            str: JSON formatted log string
        """
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'line': record.lineno
        }
        
        # Add any additional attributes that were added to the record
        for attr in dir(record):
            if attr.startswith('_') or attr in log_data or not hasattr(record, attr):
                continue
            try:
                log_data[attr] = getattr(record, attr)
            except (AttributeError, TypeError):
                pass
        
        return json.dumps(log_data)


class RequestAdapter(logging.Filter):
    """
    Filter that adds request-specific context to log records.
    """
    
    def __init__(self, request_id, user_id):
        """
        Initialize the request adapter with request context.
        
        Args:
            request_id (str): The unique request identifier
            user_id (str): The user identifier (anonymized if needed)
        """
        super().__init__()
        self.request_id = request_id
        self.user_id = user_id
    
    def filter(self, record):
        """
        Add request context to the log record.
        
        Args:
            record (logging.LogRecord): The log record to enhance
            
        Returns:
            bool: True (always passes the filter)
        """
        record.request_id = self.request_id
        record.user_id = self.user_id
        return True


class AuditAdapter(logging.Filter):
    """
    Filter that adds audit-specific context to log records.
    """
    
    def __init__(self, action, resource, details):
        """
        Initialize the audit adapter with audit context.
        
        Args:
            action (str): The action being performed (e.g., 'create', 'read', 'update', 'delete')
            resource (str): The resource being accessed (e.g., 'application', 'document')
            details (dict): Additional details about the audit event
        """
        super().__init__()
        self.action = action
        self.resource = resource
        self.details = details
    
    def filter(self, record):
        """
        Add audit context to the log record.
        
        Args:
            record (logging.LogRecord): The log record to enhance
            
        Returns:
            bool: True (always passes the filter)
        """
        record.action = self.action
        record.resource = self.resource
        record.details = self.details
        record.audit_timestamp = datetime.now().isoformat()
        return True


class PiiFilter(logging.Filter):
    """
    Filter that masks PII in log messages.
    """
    
    def __init__(self):
        """Initialize the PII filter."""
        super().__init__()
        self.patterns = {
            key: re.compile(pattern) for key, pattern in PII_PATTERNS.items()
        }
    
    def filter(self, record):
        """
        Mask PII in the log record.
        
        Args:
            record (logging.LogRecord): The log record to mask
            
        Returns:
            bool: True (always passes the filter)
        """
        # Mask message if it's a string
        if isinstance(record.msg, str):
            record.msg = mask_pii(record.msg)
        
        # Mask args if present
        if record.args:
            masked_args = []
            for arg in record.args:
                if isinstance(arg, (str, dict)):
                    masked_args.append(mask_pii(arg))
                else:
                    masked_args.append(arg)
            record.args = tuple(masked_args)
        
        return True


def setup_logger(name, log_level=None, log_format=None):
    """
    Configure and return a logger with appropriate handlers and formatters.
    
    Args:
        name (str): Name of the logger
        log_level (str): Log level to use (default is from environment or 'INFO')
        log_format (str): Format string for the log formatter
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Set log level
    level = log_level or LOG_LEVEL
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers if any
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    if log_format:
        formatter = logging.Formatter(log_format)
    else:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def generate_request_id():
    """
    Generate a unique request ID for request tracing.
    
    Returns:
        str: Unique request ID
    """
    return str(uuid.uuid4())


def get_request_logger(request_id, user_id=None):
    """
    Get a logger configured for HTTP request logging with request context.
    
    Args:
        request_id (str): The unique request identifier
        user_id (str): The user identifier (anonymized if needed)
        
    Returns:
        logging.Logger: Request logger instance
    """
    logger = setup_logger('request')
    
    # Add request context filter
    adapter = RequestAdapter(request_id, user_id)
    logger.addFilter(adapter)
    
    # Add PII filter
    pii_filter = PiiFilter()
    logger.addFilter(pii_filter)
    
    return logger


def get_audit_logger():
    """
    Get a specialized logger for security and compliance audit events.
    
    Returns:
        logging.Logger: Audit logger instance
    """
    logger = setup_logger('audit')
    
    # Set up file handler for audit logs
    try:
        # Ensure log directory exists
        log_dir = os.path.join(settings.BASE_DIR, 'logs', 'audit')
        os.makedirs(log_dir, exist_ok=True)
        
        # Create file handler with rotation
        from logging.handlers import TimedRotatingFileHandler
        file_handler = TimedRotatingFileHandler(
            os.path.join(log_dir, 'audit.log'),
            when='midnight',
            interval=1,
            backupCount=AUDIT_LOG_RETENTION_DAYS
        )
        
        # Use JSON formatter for structured audit logs
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)
        
    except Exception as e:
        logger.error(f"Failed to set up audit log file handler: {e}")
    
    # Add PII filter
    pii_filter = PiiFilter()
    logger.addFilter(pii_filter)
    
    return logger


def mask_pii(data):
    """
    Mask personally identifiable information in log data.
    
    Args:
        data (dict or str): Data to mask
        
    Returns:
        dict or str: Data with PII masked
    """
    if isinstance(data, str):
        # Apply regex replacements
        result = data
        for pii_type, pattern in PII_PATTERNS.items():
            replacement = PII_REPLACEMENTS.get(pii_type)
            if replacement:
                result = re.sub(pattern, replacement, result)
        return result
    
    elif isinstance(data, dict):
        # Process dictionary recursively
        result = {}
        for key, value in data.items():
            # Completely redact sensitive keys
            if key.lower() in ('password', 'ssn', 'social_security_number', 'credit_card', 'card_number'):
                result[key] = '[REDACTED]'
            # Recursively process nested dictionaries
            elif isinstance(value, dict):
                result[key] = mask_pii(value)
            # Process strings
            elif isinstance(value, str):
                result[key] = mask_pii(value)
            # Keep other types as is
            else:
                result[key] = value
        return result
    
    # Return other types unchanged
    return data