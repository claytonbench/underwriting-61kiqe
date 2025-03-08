"""
Authentication-specific permission classes for the loan management system.

These permission classes extend the core permissions framework to provide
fine-grained access control for authentication-related operations such as
user management, session management, and multi-factor authentication.
"""

from rest_framework.permissions import BasePermission, AllowAny
from core.permissions import IsAuthenticated, IsSystemAdmin, IsInternalUser, USER_ROLES
from .models import Auth0User, UserSession


class CanManageUsers(BasePermission):
    """
    Permission class that allows only system administrators to manage users.
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to manage users.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user is a system administrator, False otherwise
        """
        return IsSystemAdmin().has_permission(request, view)


class CanManageSessions(BasePermission):
    """
    Permission class that allows users to manage their own sessions and 
    system administrators to manage any session.
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to access session management.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user is authenticated, False otherwise
        """
        return IsAuthenticated().has_permission(request, view)
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user can manage a specific session.
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The session object being accessed
            
        Returns:
            bool: True if user owns the session or is a system admin, False otherwise
        """
        # System administrators can manage any session
        if IsSystemAdmin().has_permission(request, view):
            return True
        
        # Users can manage their own sessions
        if isinstance(obj, UserSession):
            # Check if the session belongs to the current user
            if hasattr(request.user, 'auth0_user'):
                return obj.auth0_user.id == request.user.auth0_user.id
        
        return False


class CanManageMFA(BasePermission):
    """
    Permission class that allows users to manage their own MFA settings and 
    system administrators to manage any user's MFA.
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to manage MFA settings.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user is authenticated, False otherwise
        """
        return IsAuthenticated().has_permission(request, view)
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user can manage MFA for a specific user.
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The Auth0User object being accessed
            
        Returns:
            bool: True if user is managing their own MFA or is a system admin, False otherwise
        """
        # System administrators can manage any user's MFA
        if IsSystemAdmin().has_permission(request, view):
            return True
        
        # Users can manage their own MFA
        if isinstance(obj, Auth0User):
            # Check if the Auth0User belongs to the current user
            if hasattr(request.user, 'auth0_user'):
                return obj.id == request.user.auth0_user.id
        
        return False


class AllowAnyForPasswordReset(AllowAny):
    """
    Permission class that allows anyone to request a password reset.
    """
    def has_permission(self, request, view):
        """
        Always allow access for password reset functionality.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: Always returns True
        """
        return True


class CanViewLoginAttempts(BasePermission):
    """
    Permission class that allows only internal users to view login attempts.
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to view login attempts.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user is an internal user, False otherwise
        """
        return IsInternalUser().has_permission(request, view)


class CanManageAuthSettings(BasePermission):
    """
    Permission class that allows only system administrators to manage authentication settings.
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to manage authentication settings.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user is a system administrator, False otherwise
        """
        return IsSystemAdmin().has_permission(request, view)