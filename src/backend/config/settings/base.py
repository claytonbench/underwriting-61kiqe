"""
Base Django settings for loan management system.

This file contains common settings shared across all environments
(development, staging, production, test) and serves as the foundation
for environment-specific settings files.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path
import environ  # version 1.0

# Build paths inside the project
# BASE_DIR points to the root of the project (parent directory of the config package)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Default primary key field type for models
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
# This is a placeholder, should be overridden by environment-specific settings
SECRET_KEY = 'placeholder-key-replaced-in-environment-settings'

# By default, no hosts are allowed
ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',              # Django REST Framework for API - version 3.14+
    'rest_framework.authtoken',    # Token authentication for REST API
    'corsheaders',                 # CORS support for API
    'drf_yasg',                    # Swagger API documentation
    'django_filters',              # Advanced filtering for API
    'storages',                    # Storage backends for file handling
    'django_celery_results',       # Store Celery results in Django ORM

    # Custom application modules
    'apps.authentication',         # Authentication and authorization
    'apps.users',                  # User management
    'apps.schools',                # School and program management
    'apps.applications',           # Loan application processing
    'apps.underwriting',           # Underwriting workflow
    'apps.documents',              # Document generation and management
    'apps.notifications',          # Email notifications
    'apps.funding',                # Loan funding management
    'apps.reporting',              # Reporting functionality
    'apps.qc',                     # Quality control
    'apps.workflow',               # Workflow management
]

# Middleware configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'config.middleware.request_logging_middleware.RequestLoggingMiddleware',
    'config.middleware.audit_middleware.AuditMiddleware',
]

# Root URL configuration
ROOT_URLCONF = 'config.urls'

# Template configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI application path
WSGI_APPLICATION = 'config.wsgi.application'

# ASGI application path
ASGI_APPLICATION = 'config.asgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
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

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # Enforce strong passwords
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (User uploaded content)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.authentication.auth0.Auth0Authentication',  # Custom Auth0 authentication
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
}

# CORS settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = []  # To be populated in environment-specific settings

# Security settings
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Auth0 Configuration
AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN')
AUTH0_API_AUDIENCE = os.environ.get('AUTH0_API_AUDIENCE')
AUTH0_ALGORITHMS = ['RS256']

# Celery settings (for asynchronous task processing)
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'django-db')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes max task execution time

# Cache settings - defaulting to local memory cache
# Should be overridden in production with Redis or other distributed cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Logging configuration
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
            'level': 'INFO',
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
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Field-level encryption key for sensitive data
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')

# DocuSign Integration Settings
DOCUSIGN_INTEGRATION_KEY = os.environ.get('DOCUSIGN_INTEGRATION_KEY')
DOCUSIGN_USER_ID = os.environ.get('DOCUSIGN_USER_ID')
DOCUSIGN_BASE_URL = os.environ.get('DOCUSIGN_BASE_URL', 'https://demo.docusign.net/restapi')
DOCUSIGN_ACCOUNT_ID = os.environ.get('DOCUSIGN_ACCOUNT_ID')
DOCUSIGN_PRIVATE_KEY_PATH = os.environ.get('DOCUSIGN_PRIVATE_KEY_PATH')

# SendGrid Email Settings
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@loanmanagementsystem.com')

# Swagger/OpenAPI settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'VALIDATOR_URL': None,
}