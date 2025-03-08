"""
Initialization file for the document templates module.

This module makes HTML templates available to the document generation system,
registers the templates directory with Django, and exports template-related
constants and utilities for document generation.
"""

import os
import logging  # standard library
from ..constants import DOCUMENT_TEMPLATE_PATHS, DOCUMENT_TYPES

# Configure logger for document templates
logger = logging.getLogger('document_templates')

# Define the absolute path to the templates directory
TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize a registry for custom template paths
TEMPLATE_REGISTRY = {}


def get_template_path(document_type):
    """
    Returns the absolute path to a template file based on document type.
    
    Args:
        document_type (str): The type of document for which to retrieve the template path.
            Must be one of the keys in DOCUMENT_TEMPLATE_PATHS.
            
    Returns:
        str: Absolute path to the template file
        
    Raises:
        ValueError: If the document type is not found in DOCUMENT_TEMPLATE_PATHS
    """
    if document_type in DOCUMENT_TEMPLATE_PATHS:
        template_path = os.path.join(TEMPLATE_DIR, DOCUMENT_TEMPLATE_PATHS[document_type])
        logger.debug(f"Accessing template path for {document_type}: {template_path}")
        return template_path
    else:
        error_msg = f"Document type '{document_type}' not found in template paths"
        logger.error(error_msg)
        raise ValueError(error_msg)


def register_template(document_type, template_path):
    """
    Registers a template in the template registry.
    
    This allows for custom templates to be used instead of the default ones.
    
    Args:
        document_type (str): The type of document for which to register the template
        template_path (str): The path to the template file
        
    Returns:
        None
    """
    TEMPLATE_REGISTRY[document_type] = template_path
    logger.info(f"Registered custom template for {document_type}: {template_path}")


def get_registered_template_path(document_type):
    """
    Returns the path of a registered template.
    
    If a custom template is registered for the document type, its path will be returned.
    Otherwise, falls back to the default template path.
    
    Args:
        document_type (str): The type of document for which to retrieve the template path
        
    Returns:
        str: Path to the registered template or default template
    """
    if document_type in TEMPLATE_REGISTRY:
        logger.debug(f"Using registered template for {document_type}: {TEMPLATE_REGISTRY[document_type]}")
        return TEMPLATE_REGISTRY[document_type]
    else:
        return get_template_path(document_type)


def validate_templates():
    """
    Validates that all required templates exist.
    
    Checks for the existence of each template file defined in DOCUMENT_TEMPLATE_PATHS.
    
    Returns:
        bool: True if all templates are valid, False otherwise
    """
    all_valid = True
    
    for doc_type, relative_path in DOCUMENT_TEMPLATE_PATHS.items():
        template_path = os.path.join(TEMPLATE_DIR, relative_path)
        if not os.path.exists(template_path):
            logger.error(f"Template file not found for {doc_type}: {template_path}")
            all_valid = False
        else:
            logger.debug(f"Validated template for {doc_type}: {template_path}")
            
    return all_valid


# Validate templates when module is imported
if not validate_templates():
    logger.warning("Some document templates are missing. Document generation may fail.")
    
# Export public functions and constants
__all__ = [
    'get_template_path',
    'register_template',
    'get_registered_template_path',
    'validate_templates',
    'TEMPLATE_DIR'
]