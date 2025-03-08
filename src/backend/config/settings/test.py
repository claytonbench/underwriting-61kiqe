"""
Django settings for the loan management system's test environment.

This file extends the base settings with test-specific configurations optimized
for automated testing, including in-memory database, disabled security features,
and test-specific caching and task execution settings.
"""

import os
import tempfile

# Import all settings from the base settings file
from .base import *

# Enable debug mode for testing
DEBUG = True

# Use a simple, insecure secret key for tests
SECRET_KEY = 'django-insecure-test-key-not-for-production'

# Allow testing hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', 'testserver']

# Use SQLite in-memory database for faster testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Use in-memory cache for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Use faster password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Use in-memory email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Configure Celery to execute tasks synchronously for testing
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Use temporary directory for media files during tests
MEDIA_ROOT = tempfile.mkdtemp()
MEDIA_URL = '/media/'

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Disable security features that can interfere with testing
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Mock Auth0 settings for testing
AUTH0_DOMAIN = 'test.auth0.com'
AUTH0_API_AUDIENCE = 'https://test-api.example.com'

# Mock encryption key for testing
ENCRYPTION_KEY = 'test-encryption-key-not-for-production'

# Mock DocuSign settings for testing
DOCUSIGN_INTEGRATION_KEY = 'test-integration-key'
DOCUSIGN_USER_ID = 'test-user-id'
DOCUSIGN_BASE_URL = 'https://demo.docusign.net/restapi'
DOCUSIGN_ACCOUNT_ID = 'test-account-id'
DOCUSIGN_PRIVATE_KEY_PATH = os.path.join(BASE_DIR, 'tests', 'test_docusign_private_key.pem')

# Mock SendGrid settings for testing
SENDGRID_API_KEY = 'test-sendgrid-key'
DEFAULT_FROM_EMAIL = 'test@loanmanagementsystem.com'

# Configure REST Framework for testing
REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # Include existing settings from base
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
}

# Reduce logging output during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}