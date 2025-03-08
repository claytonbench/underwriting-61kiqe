"""
Celery configuration for the loan management system.

This module configures and initializes the Celery application for the loan management system.
It serves as the central configuration point for all asynchronous task processing in the
application, enabling background tasks such as document generation, email notifications,
and scheduled processes without blocking user interactions.
"""

import os  # standard library
from celery import Celery  # 5.3+
from django.conf import settings  # 4.2+
from celery.schedules import crontab  # 5.3+
import logging  # standard library

from utils.logging import setup_logger

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Create logger for Celery
logger = setup_logger('celery', level=logging.INFO)

# Create a basic Celery application instance
app = Celery('loan_management')

def celery_init_app():
    """
    Initialize the Celery application with Django settings.
    
    Configures the Celery application with appropriate settings from Django configuration,
    registers task modules, and sets up logging for Celery tasks.
    
    Returns:
        Celery: Configured Celery application instance
    """
    # Configure the Celery application using Django settings namespace
    app.config_from_object('django.conf:settings', namespace='CELERY')
    
    # Set up task autodiscovery to find tasks in installed apps
    app.autodiscover_tasks()
    
    # Configure logging for Celery tasks
    logger.info('Celery application initialized')
    
    # Configure task routing
    app.conf.task_routes = {
        'apps.documents.*': {'queue': 'documents'},
        'apps.notifications.*': {'queue': 'notifications'},
        'apps.reports.*': {'queue': 'reports'},
        'apps.applications.*': {'queue': 'applications'},
    }
    
    # Configure task serialization
    app.conf.task_serializer = 'json'
    app.conf.result_serializer = 'json'
    app.conf.accept_content = ['json']
    
    # Configure Redis broker settings
    app.conf.broker_transport_options = {
        'visibility_timeout': 3600,  # 1 hour
    }
    
    # Configure task execution settings
    app.conf.task_time_limit = 1800  # 30 minutes
    app.conf.task_soft_time_limit = 1500  # 25 minutes
    app.conf.worker_prefetch_multiplier = 1  # One task per worker
    
    # Ensure Celery doesn't hijack the root logger
    app.conf.worker_hijack_root_logger = False
    
    return app

# Configure the Celery app
app = celery_init_app()

# Debug task for testing Celery configuration
@app.task(bind=True)
def debug_task(self):
    """Task to verify that Celery is working correctly."""
    logger.info(f'Request: {self.request!r}')