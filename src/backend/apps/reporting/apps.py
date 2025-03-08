from django.apps import AppConfig


class ReportingConfig(AppConfig):
    """
    Django app configuration class for the reporting app that defines 
    app metadata and initialization behavior for the reporting system.
    
    This configuration sets up the infrastructure for generating and exporting
    various types of reports including application reports, underwriting reports,
    document reports, funding reports, and operational reports.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reporting'
    label = 'reporting'
    verbose_name = 'Reporting'

    def ready(self):
        """
        Method called when the app is ready. Performs initialization tasks
        for the reporting system such as setting up report generators,
        exporters, scheduled tasks, and signal handlers.
        
        Initializes the reporting system that supports:
        - Application reports (volume, status, source)
        - Underwriting reports (approval rates, denial reasons, decision timing)
        - Document reports (completion, signature status, expiration risk)
        - Funding reports (disbursement volume, timeline, school payments)
        - Operational reports (user activity, system performance, error rates)
        
        Also configures export capabilities for PDF, Excel, and CSV formats.
        """
        # Avoid importing at module level to prevent AppRegistryNotReady exception
        try:
            # Import here to prevent circular imports and app registry issues
            from .services import initialize_reporting_system
            
            # Initialize all reporting components
            initialize_reporting_system()
            
        except Exception as e:
            # Log initialization errors but don't prevent app from loading
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error initializing reporting app: {e}")