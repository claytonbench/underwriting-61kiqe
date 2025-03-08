"""
WSGI config for loan management system.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os  # standard library

from django.core.wsgi import get_wsgi_application  # Django 4.2+

# Set the Django settings module to use the production settings if not already set
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

# Get the WSGI application
application = get_wsgi_application()