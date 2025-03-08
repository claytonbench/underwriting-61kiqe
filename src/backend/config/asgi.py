"""
ASGI config for the loan management system.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os  # standard library

from django.core.asgi import get_asgi_application  # Django 4.2+

# Set the Django settings module to the production settings by default.
# This can be overridden by environment variables in deployment environments.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

# Create the ASGI application using Django's ASGI application factory.
# This application can be served by ASGI-compatible web servers like Daphne or Uvicorn.
application = get_asgi_application()