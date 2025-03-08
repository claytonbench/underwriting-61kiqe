"""
Schools application package.

This package provides functionality for managing schools, educational programs, 
and related data in the loan management system.
"""

from .apps import SchoolsConfig

# Specify the default app configuration class for Django's app loading mechanism
default_app_config = 'src.backend.apps.schools.apps.SchoolsConfig'