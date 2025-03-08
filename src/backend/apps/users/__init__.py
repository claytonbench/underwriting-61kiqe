"""
Users app for the loan management system.

This app provides comprehensive user management functionality including:
- Multiple user types (borrowers, co-borrowers, school administrators, underwriters, QC personnel)
- Role-based access control
- User profile management
- Authentication and authorization

All functionality follows security best practices for handling sensitive user information.
"""

# Define the default app configuration
default_app_config = "src.backend.apps.users.apps.UsersConfig"

# Version of the users app
__version__ = "1.0.0"