"""
Initialization file for the documents app that exposes key models and constants,
and sets up default app configuration. This file makes the documents app importable
as a Python package and ensures proper initialization of document-related signals.
"""

from .models import DocumentTemplate  # Import DocumentTemplate model for direct access from the package
from .models import DocumentPackage  # Import DocumentPackage model for direct access from the package
from .models import Document  # Import Document model for direct access from the package
from .models import SignatureRequest  # Import SignatureRequest model for direct access from the package
from .models import DocumentField  # Import DocumentField model for direct access from the package
from .signals import connect_document_signals  # Import function to connect document-related signals

default_app_config = "src.backend.apps.documents.apps.DocumentsConfig"  # Define the default Django app configuration for the documents app

# Connect document-related signals
connect_document_signals()

__all__ = [  # Define what is exposed when someone imports * from this module
    'DocumentTemplate',  # Export DocumentTemplate model for direct import from the package
    'DocumentPackage',  # Export DocumentPackage model for direct import from the package
    'Document',  # Export Document model for direct import from the package
    'SignatureRequest',  # Export SignatureRequest model for direct import from the package
    'DocumentField',  # Export DocumentField model for direct import from the package
    'default_app_config',  # Export the default app config
]