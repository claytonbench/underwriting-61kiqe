from django.apps import AppConfig  # Django 4.2+

from .signals import connect_document_signals  # Import function to connect all document-related signals


class DocumentsConfig(AppConfig):
    """
    Django app configuration class for the documents app that defines app metadata and initialization behavior
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'documents'
    label = 'documents'
    verbose_name = 'Documents'

    def __init__(self, *args, **kwargs):
        """Initializes the DocumentsConfig class with default values"""
        super().__init__(*args, **kwargs)

    def ready(self):
        """
        Method called when the app is ready, used to perform initialization tasks such as registering signals
        """
        # Import document-related signals
        # from . import signals  # Import document-related signals

        # Call connect_document_signals to register signal handlers for document events
        connect_document_signals()

        # Register signal handlers for document status changes
        # signals.document_status_signal.connect(signals.handle_document_status_change)

        # Register signal handlers for signature request events
        # signals.signature_status_signal.connect(signals.handle_signature_status_change)

        # Set up any app-specific configurations
        # For example, you could load settings from a file or initialize a cache
        pass