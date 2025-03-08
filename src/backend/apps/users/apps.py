from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Django app configuration for the users app.
    
    This class configures the users app, which provides comprehensive user
    management with multiple user types (borrowers, co-borrowers, school
    administrators, underwriters, QC personnel) and role-based access control.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    label = 'users'
    verbose_name = 'User Management'
    
    def ready(self):
        """
        Initialize the users app when Django is ready.
        
        This method is called when the app is ready and performs initialization tasks:
        - Register signal handlers for user creation/modification events
        - Register signal handlers for profile creation/modification events
        - Register signal handlers for role assignment events
        - Set up any app-specific configurations
        """
        # Import signals module to register the signal handlers
        import apps.users.signals  # noqa