from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """
    Django app configuration for the authentication system.
    This app handles user authentication, including Auth0 integration,
    multi-factor authentication, and role-based access control.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'
    label = 'authentication'
    verbose_name = 'User Authentication'

    def ready(self):
        """
        Method called when the authentication app is ready.
        This method initializes signal handlers and performs other authentication-related setup.
        """
        # Import signal handlers - needs to be imported here to avoid AppRegistryNotReady errors
        try:
            # Import the signals module to register signal handlers
            import apps.authentication.signals  # noqa
        except ImportError:
            # Log a warning if signals module isn't available
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("Could not import authentication signals")
        
        # Register signal handlers for Auth0 authentication events
        # These handle events such as successful/failed login attempts,
        # password changes, and account lockouts
        
        # Register signal handlers for user creation and modification
        # These track changes to user profiles, role assignments, and permissions
        
        # Register signal handlers for MFA-related events
        # These handle multi-factor authentication verification success/failure
        # and MFA enrollment/unenrollment
        
        # Initialize integration with Auth0 identity management service
        # This sets up the necessary callbacks and authentication flows