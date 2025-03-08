from django.apps import AppConfig


class SchoolsConfig(AppConfig):
    """
    Django app configuration class for the schools app that defines app metadata
    and initialization behavior.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.schools'
    label = 'schools'
    verbose_name = 'Schools'

    def ready(self):
        """
        Method called when the app is ready, used to perform initialization tasks
        such as registering signals.
        
        This registers signal handlers for:
        - School creation/modification events
        - Program creation/modification events
        - Program version events
        - School document events
        """
        # Import signals module to register signal handlers
        # This will connect handlers for school, program, and program version events
        try:
            import apps.schools.signals  # noqa
        except ImportError:
            # Signals module might not exist yet during initial setup, which is fine
            pass