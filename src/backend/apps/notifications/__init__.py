"""
Initialization file for the notifications app that makes key components available at the package level for easier imports throughout the application.

This file exposes the main notification service classes, functions, and constants to simplify the API for other modules that need to interact with the notification system.
"""

# Import from services.py
from .services import NotificationService, EventNotificationManager

# Import from models.py
from .models import (
    NotificationTemplate, NotificationEvent, 
    Notification, NotificationEventMapping
)

# Import from constants.py
from .constants import (
    EMAIL_TEMPLATES, EMAIL_SUBJECTS, 
    NOTIFICATION_DELIVERY_METHODS, NOTIFICATION_PRIORITIES,
    NOTIFICATION_CATEGORIES, TEMPLATE_VARIABLES
)

# Import from tasks.py
from .tasks import send_notification, process_notification_batch_task

# Default app configuration
default_app_config = "src.backend.apps.notifications.apps.NotificationsConfig"