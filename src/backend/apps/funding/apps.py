from django.apps import AppConfig  # Django 4.2+
from .signals import connect_funding_signals  # Import function to connect all funding-related signals


class FundingConfig(AppConfig):
    """
    Django app configuration class for the funding app that defines app metadata and initialization behavior
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.funding'
    label = 'funding'
    verbose_name = 'Funding Management'

    def ready(self):
        """
        Method called when the app is ready, used to perform initialization tasks such as registering signals
        """
        # Import funding-related signals
        # Call connect_funding_signals to register signal handlers for funding events
        connect_funding_signals()
        # Register signal handlers for funding request status changes
        # Register signal handlers for disbursement processing
        # Register signal handlers for enrollment verification
        # Register signal handlers for stipulation verification
        # Set up any app-specific configurations
        pass