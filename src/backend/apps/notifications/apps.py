from django.apps import AppConfig  # django.apps 4.2+


class NotificationsConfig(AppConfig):
    """
    Django app configuration for the notifications app.
    
    This class defines the app's configuration, including metadata like app name,
    label, and verbose name. It also handles initialization of notification-related
    functionality when the app is ready.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    label = 'notifications'
    verbose_name = 'Notifications'

    def ready(self):
        """
        Method called when the app is ready. Used to perform initialization tasks
        such as registering signals and setting up periodic tasks.
        
        This method connects signal handlers for various events in the loan lifecycle
        that should trigger notifications, and sets up periodic tasks for notification
        processing.
        """
        # Import notification-related signals and handlers
        # Import happens inside the method to avoid circular imports
        try:
            # Import the local signals module
            from . import signals
            
            # Register signal handlers for application status changes
            from apps.loan_applications.signals import application_status_changed
            application_status_changed.connect(signals.create_application_status_notification)
            
            # Register signal handlers for document status changes
            from apps.documents.signals import document_status_changed
            document_status_changed.connect(signals.create_document_status_notification)
            
            # Register signal handlers for underwriting decision events
            from apps.underwriting.signals import underwriting_decision_created
            underwriting_decision_created.connect(signals.create_underwriting_decision_notification)
            
            # Register signal handlers for funding status changes
            from apps.funding.signals import funding_status_changed
            funding_status_changed.connect(signals.create_funding_status_notification)
            
            # Set up Celery periodic tasks for notification processing
            self._setup_periodic_tasks()
            
            # Initialize email delivery service configuration
            self._initialize_email_service()
            
        except ImportError as e:
            # Log import errors during app initialization
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error during notifications app initialization: {e}")

    def _setup_periodic_tasks(self):
        """
        Set up Celery periodic tasks for notification processing.
        
        This includes tasks for retrying failed notifications and
        sending scheduled notification digests.
        """
        try:
            from django.conf import settings
            from celery.schedules import crontab
            
            app = settings.CELERY_APP
            
            # Register periodic tasks with Celery beat scheduler
            app.conf.beat_schedule.update({
                'retry-failed-notifications': {
                    'task': 'apps.notifications.tasks.retry_failed_notifications',
                    'schedule': crontab(minute='*/15'),  # Every 15 minutes
                },
                'send-notification-digests': {
                    'task': 'apps.notifications.tasks.send_notification_digests',
                    'schedule': crontab(hour=8, minute=0),  # Daily at 8 AM
                }
            })
        except (ImportError, AttributeError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error setting up notification periodic tasks: {e}")

    def _initialize_email_service(self):
        """
        Initialize the email delivery service configuration.
        
        This sets up the connection to the email service provider (SendGrid)
        and configures the necessary settings.
        """
        try:
            from django.conf import settings
            from .services import EmailDeliveryService
            
            # Initialize the email service with settings from Django configuration
            EmailDeliveryService.initialize(
                api_key=settings.EMAIL_SERVICE_API_KEY,
                sender_email=settings.DEFAULT_FROM_EMAIL,
                sender_name=settings.DEFAULT_FROM_NAME,
                max_retries=settings.EMAIL_MAX_RETRIES
            )
        except (ImportError, AttributeError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error initializing email delivery service: {e}")