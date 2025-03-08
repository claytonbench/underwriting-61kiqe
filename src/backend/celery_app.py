"""
Entry point for the Celery application in the loan management system.

This module imports and re-exports the configured Celery application instance
from the config module, making it available for task registration and execution
throughout the application. It serves as a convenient import point for other
modules that need to use Celery for asynchronous task processing.

Usage:
    from celery_app import app
    
    @app.task
    def my_task():
        # Task implementation
"""

# Import the configured Celery application instance
from config.celery import app  # Celery 5.3+

# Re-export the app for use in task definitions throughout the application
# This allows other modules to import the Celery instance and its decorators
# from this central location rather than from the config module directly