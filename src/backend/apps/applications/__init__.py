"""
Applications App

This module provides functionality for managing loan applications in the loan management system.
It handles the submission, validation, and processing of loan applications, including borrower
and co-borrower information, program details, and financial requirements.

The application system supports the complete application lifecycle, from draft creation
through submission, underwriting, approval/denial, document generation, and funding.
"""

# Define the default app configuration
default_app_config = "src.backend.apps.applications.apps.ApplicationsConfig"

# Define the version of the applications app
__version__ = "1.0.0"