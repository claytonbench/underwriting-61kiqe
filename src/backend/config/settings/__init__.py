"""
Django settings module initialization.

This module determines which settings module to use based on the DJANGO_ENVIRONMENT
environment variable and dynamically imports it. The supported environments include
development, staging, production, and test.
"""
import os  # standard library
import importlib  # standard library

# Determine which environment we're in, defaulting to development
ENVIRONMENT = os.environ.get('DJANGO_ENVIRONMENT', 'development')

# Construct the settings module path
SETTINGS_MODULE = f'config.settings.{ENVIRONMENT}'

# Dynamically import the appropriate settings module
settings_module = importlib.import_module(SETTINGS_MODULE)

# Export ENVIRONMENT and SETTINGS_MODULE
__all__ = ['ENVIRONMENT', 'SETTINGS_MODULE']

def get_settings_module():
    """
    Determines and returns the appropriate settings module based on environment.
    
    Returns:
        module: The imported settings module (development, staging, production, or test)
    """
    # Get the environment name from DJANGO_ENVIRONMENT environment variable, defaulting to 'development'
    env = os.environ.get('DJANGO_ENVIRONMENT', 'development')
    
    # Construct the full module path (e.g., 'config.settings.development')
    module_path = f'config.settings.{env}'
    
    # Dynamically import the module using importlib
    return importlib.import_module(module_path)