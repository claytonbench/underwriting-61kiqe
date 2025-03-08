"""
Django admin configuration for authentication app.

This module registers authentication-related models with the Django admin interface,
providing custom admin classes with appropriate display, filtering, and search capabilities
for managing authentication data in the loan management system. It enables administrative
management of Auth0 users, MFA verification, login attempts, user sessions, and refresh
tokens, supporting the system's authentication framework and security monitoring requirements.
"""

from django.contrib import admin  # Django 4.2+
from .models import (
    Auth0User, MFAVerification, LoginAttempt, UserSession, RefreshToken,
    MFA_METHODS, MFA_STATUS
)


@admin.register(Auth0User)
class Auth0UserAdmin(admin.ModelAdmin):
    """
    Admin configuration for Auth0User model.
    
    Provides interface for managing Auth0 user accounts linked to the system.
    """
    list_display = ('email', 'auth0_id', 'last_login', 'email_verified', 'is_active')
    list_filter = ('email_verified', 'is_active', 'last_login')
    search_fields = ('email', 'auth0_id')
    readonly_fields = ('auth0_id', 'last_login')


@admin.register(MFAVerification)
class MFAVerificationAdmin(admin.ModelAdmin):
    """
    Admin configuration for MFAVerification model.
    
    Provides interface for managing multi-factor authentication settings.
    """
    list_display = ('auth0_user', 'mfa_method', 'status', 'enabled_at', 'last_verified_at')
    list_filter = ('mfa_method', 'status', 'enabled_at')
    search_fields = ('auth0_user__email',)
    raw_id_fields = ('auth0_user',)


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """
    Admin configuration for LoginAttempt model.
    
    Provides interface for monitoring login attempts for security purposes.
    """
    list_display = ('email', 'success', 'timestamp', 'ip_address', 'failure_reason')
    list_filter = ('success', 'timestamp')
    search_fields = ('email', 'ip_address', 'user_agent')
    readonly_fields = ('email', 'success', 'timestamp', 'ip_address', 'user_agent', 'failure_reason')


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserSession model.
    
    Provides interface for managing and monitoring user sessions.
    """
    list_display = ('auth0_user', 'session_id', 'created_at', 'expires_at', 'last_activity', 'is_session_active')
    list_filter = ('is_active', 'created_at', 'expires_at')
    search_fields = ('auth0_user__email', 'session_id', 'ip_address')
    raw_id_fields = ('auth0_user',)
    readonly_fields = ('session_id', 'created_at', 'expires_at', 'last_activity', 'ip_address', 'user_agent')
    
    def is_session_active(self, obj):
        """
        Custom admin display method to show if a session is active and not expired.
        
        Args:
            obj (UserSession): The UserSession instance
            
        Returns:
            bool: True if session is active and not expired, False otherwise
        """
        return obj.is_active and not obj.is_expired()
    
    is_session_active.boolean = True
    is_session_active.short_description = 'Active'


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    """
    Admin configuration for RefreshToken model.
    
    Provides interface for managing refresh tokens used for authentication.
    """
    list_display = ('auth0_user', 'created_at', 'expires_at', 'is_revoked', 'token_validity')
    list_filter = ('is_revoked', 'created_at', 'expires_at')
    search_fields = ('auth0_user__email', 'token')
    raw_id_fields = ('auth0_user',)
    readonly_fields = ('created_at', 'expires_at')
    
    def token_validity(self, obj):
        """
        Custom admin display method to show if a token is valid.
        
        Args:
            obj (RefreshToken): The RefreshToken instance
            
        Returns:
            bool: True if token is valid, False otherwise
        """
        return obj.is_valid()
    
    token_validity.boolean = True
    token_validity.short_description = 'Valid'