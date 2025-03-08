"""
Initialization file for the notification templates package.

This module enables the template directory to be treated as a Python package and
provides a registry of available email templates for the loan management system's 
notification features.
"""

import os  # standard library - v3.11+

from ..constants import EMAIL_TEMPLATES, TEMPLATE_DIR  # internal import

# Create a registry of available templates
TEMPLATE_REGISTRY = dict(EMAIL_TEMPLATES)

# Determine the absolute path to the templates directory
TEMPLATE_PATH = os.path.dirname(os.path.abspath(__file__))

def get_template_path(template_name):
    """
    Returns the absolute path to a template file.
    
    Args:
        template_name (str): The name of the template
        
    Returns:
        str: Absolute path to the template file
        
    Raises:
        ValueError: If the template name is not found in the registry
    """
    if template_name in TEMPLATE_REGISTRY:
        template_filename = TEMPLATE_REGISTRY[template_name]
        return os.path.join(TEMPLATE_PATH, template_filename)
    else:
        raise ValueError(f"Template '{template_name}' not found in template registry")

def list_available_templates():
    """
    Returns a list of all available template names.
    
    Returns:
        list: List of available template names
    """
    return list(TEMPLATE_REGISTRY.keys())