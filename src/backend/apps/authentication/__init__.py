"""
Authentication module for the loan management system.

This module provides a comprehensive authentication framework, integrating with Auth0
for identity management and implementing secure session handling, multi-factor authentication,
and role-based access control.
"""

# Import app configuration
from .apps import AuthenticationConfig

# Import models
from .models import (
    Auth0User,
    UserSession,
    MFAVerification,
    PasswordResetToken,
    LoginAttempt,
    MFA_METHODS,
    SESSION_DURATIONS
)

# Import Auth0 integration
from .auth0 import (
    Auth0Client,
    Auth0Manager,
    validate_auth0_token
)

# Import token utilities
from .tokens import (
    generate_jwt_token,
    validate_jwt_token,
    generate_session_token
)

# Import permission classes
from .permissions import (
    CanManageUsers,
    CanManageSessions,
    CanManageMFA
)

# Configure default app config for Django app registry
default_app_config = "src.backend.apps.authentication.apps.AuthenticationConfig"

# Define public API
__all__ = [
    # Models
    'Auth0User',
    'UserSession',
    'MFAVerification',
    'PasswordResetToken',
    'LoginAttempt',
    'MFA_METHODS',
    'SESSION_DURATIONS',
    
    # Auth0 integration
    'Auth0Client',
    'Auth0Manager',
    'validate_auth0_token',
    
    # Token utilities
    'generate_jwt_token',
    'validate_jwt_token',
    'generate_session_token',
    
    # Permission classes
    'CanManageUsers',
    'CanManageSessions',
    'CanManageMFA',
]