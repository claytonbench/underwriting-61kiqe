"""
Configuration package initialization for the loan management system.

This module serves as the entry point for the Django configuration package
and exposes the Celery application instance for asynchronous task processing
throughout the project. The Celery app handles background tasks such as document
generation, email notifications, and scheduled processes without blocking user
interactions.
"""

from .celery import app

__all__ = ['app']