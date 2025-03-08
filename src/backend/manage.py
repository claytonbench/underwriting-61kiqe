#!/usr/bin/env python
"""Django's command-line utility for administrative tasks.

This script serves as the entry point for executing Django management commands such as
running the development server, applying migrations, creating superusers, and other
administrative operations for the loan management system.
"""
import os
import sys


def main():
    """Run administrative tasks for the loan management system.
    
    This function:
    1. Sets up the Django environment with the appropriate settings
    2. Executes management commands from the command line
    3. Handles exceptions that may occur during execution
    """
    # Set the Django settings module to development by default
    # This can be overridden with an environment variable
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    
    try:
        # Import Django's management module to execute commands
        from django.core.management import execute_from_command_line  # django 4.2+
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Execute the command provided in command line arguments
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()