"""
Development settings for loan management system.

This file extends the base settings with configurations specific to the
development environment, including:
- Debug mode enabled
- Development tools (django-extensions, debug-toolbar)
- Local database configuration
- Console email backend
- Relaxed security settings
"""

import os
import socket
from .base import *  # Import all settings from base settings

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-development-key-not-for-production'

# Allow requests from localhost and hostname
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', socket.gethostname()]

# Add development apps
INSTALLED_APPS = INSTALLED_APPS + ['django_extensions', 'debug_toolbar']

# Add debug toolbar middleware
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

# Required for django-debug-toolbar
INTERNAL_IPS = ['127.0.0.1']

# Relax CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Disable HTTPS requirements for local development
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Database configuration for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'loan_management'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Use local memory cache for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Output emails to console instead of sending them
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Execute Celery tasks synchronously in development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'django-db'

# Media and static files configuration
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Enhance REST framework configuration for development
REST_FRAMEWORK = REST_FRAMEWORK.copy()

# Detailed logging for development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Development credentials for external services
AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN', 'dev-example.auth0.com')
AUTH0_API_AUDIENCE = os.environ.get('AUTH0_API_AUDIENCE', 'https://api.example.com')

# Field-level encryption key for development
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', 'development-encryption-key-not-for-production')

# DocuSign development settings
DOCUSIGN_INTEGRATION_KEY = os.environ.get('DOCUSIGN_INTEGRATION_KEY', 'dev-integration-key')
DOCUSIGN_USER_ID = os.environ.get('DOCUSIGN_USER_ID', 'dev-user-id')
DOCUSIGN_BASE_URL = os.environ.get('DOCUSIGN_BASE_URL', 'https://demo.docusign.net/restapi')
DOCUSIGN_ACCOUNT_ID = os.environ.get('DOCUSIGN_ACCOUNT_ID', 'dev-account-id')
DOCUSIGN_PRIVATE_KEY_PATH = os.environ.get('DOCUSIGN_PRIVATE_KEY_PATH', os.path.join(BASE_DIR, 'dev_docusign_private_key.pem'))

# SendGrid development settings
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', 'dev-sendgrid-key')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@loanmanagementsystem.com')