"""
Authentication models for the loan management system.

This module defines models for authentication-related functionality including Auth0 user
integration, multi-factor authentication tracking, session management, and login attempt
monitoring. These models provide the foundation for the system's authentication framework
and security features.
"""

from django.db import models  # Django 4.2+
from django.utils import timezone  # Django 4.2+
import uuid  # standard library
from datetime import timedelta  # standard library

from core.models import (
    CoreModel, UUIDModel, TimeStampedModel, SoftDeleteModel, AuditableModel
)
from utils.constants import (
    USER_TYPES, JWT_EXPIRATION_HOURS, REFRESH_TOKEN_EXPIRATION_DAYS,
    MAX_LOGIN_ATTEMPTS, ACCOUNT_LOCKOUT_MINUTES
)

# Constants for MFA methods
MFA_METHODS = {
    "SMS": "sms",
    "EMAIL": "email",
    "AUTHENTICATOR": "authenticator"
}

# Constants for MFA status
MFA_STATUS = {
    "ENABLED": "enabled",
    "DISABLED": "disabled",
    "PENDING": "pending"
}


class Auth0User(CoreModel):
    """
    Model for storing Auth0 user information and linking to application users.
    
    This model maintains a record of Auth0 users and their essential information,
    serving as a bridge between the external Auth0 identity provider and the
    application's internal user representation.
    """
    auth0_id = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    last_login = models.DateTimeField(null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    auth0_metadata = models.CharField(max_length=1024, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        """
        String representation of the Auth0User instance.
        
        Returns:
            str: String showing email and auth0_id
        """
        return f"{self.email} ({self.auth0_id})"

    def update_last_login(self):
        """
        Updates the last_login timestamp to current time.
        
        This method is typically called when a user successfully logs in to keep
        track of user activity and for security monitoring purposes.
        """
        self.last_login = timezone.now()
        self.save()


class MFAVerification(CoreModel):
    """
    Model for tracking multi-factor authentication status for users.
    
    This model maintains information about a user's MFA settings, including the
    chosen method, verification status, and relevant timestamps.
    """
    auth0_user = models.OneToOneField(
        Auth0User, 
        on_delete=models.CASCADE, 
        related_name="mfa_verification"
    )
    mfa_method = models.CharField(
        max_length=20,
        choices=[(v, v) for v in MFA_METHODS.values()],
        default=MFA_METHODS["AUTHENTICATOR"]
    )
    verification_contact = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[(v, v) for v in MFA_STATUS.values()],
        default=MFA_STATUS["DISABLED"]
    )
    enabled_at = models.DateTimeField(null=True, blank=True)
    last_verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        """
        String representation of the MFAVerification instance.
        
        Returns:
            str: String showing user email and MFA method
        """
        return f"{self.auth0_user.email} - {self.mfa_method}"

    def is_enabled(self):
        """
        Checks if MFA is enabled for the user.
        
        Returns:
            bool: True if MFA is enabled, False otherwise
        """
        return self.status == MFA_STATUS["ENABLED"]

    def enable(self):
        """
        Enables MFA for the user.
        
        Updates the status to 'enabled' and records the current time as the
        enabled_at timestamp.
        """
        self.status = MFA_STATUS["ENABLED"]
        self.enabled_at = timezone.now()
        self.save()

    def disable(self):
        """
        Disables MFA for the user.
        
        Updates the status to 'disabled'.
        """
        self.status = MFA_STATUS["DISABLED"]
        self.save()

    def update_verification(self):
        """
        Updates the last verification timestamp.
        
        This method is typically called when a user successfully verifies
        their identity using the MFA method.
        """
        self.last_verified_at = timezone.now()
        self.save()


class LoginAttempt(CoreModel):
    """
    Model for tracking user login attempts for security monitoring.
    
    This model records information about login attempts, including successful
    and failed attempts, to support security features like account lockout
    after multiple failed attempts.
    """
    email = models.EmailField()
    success = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    failure_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        """
        String representation of the LoginAttempt instance.
        
        Returns:
            str: String showing email, success status, and timestamp
        """
        status = "successful" if self.success else "failed"
        return f"{self.email} - {status} login attempt at {self.timestamp}"

    @classmethod
    def get_recent_failures(cls, email, minutes=ACCOUNT_LOCKOUT_MINUTES):
        """
        Gets recent failed login attempts for an email.
        
        Args:
            email (str): The email address to check
            minutes (int): The time window in minutes to check for failed attempts
            
        Returns:
            QuerySet: QuerySet of failed login attempts
        """
        threshold = timezone.now() - timedelta(minutes=minutes)
        return cls.objects.filter(
            email=email,
            success=False,
            timestamp__gte=threshold
        )

    @classmethod
    def is_account_locked(cls, email):
        """
        Checks if an account is locked due to too many failed attempts.
        
        Args:
            email (str): The email address to check
            
        Returns:
            bool: True if account is locked, False otherwise
        """
        recent_failures = cls.get_recent_failures(email)
        return recent_failures.count() >= MAX_LOGIN_ATTEMPTS


class UserSession(CoreModel):
    """
    Model for tracking active user sessions.
    
    This model maintains information about user sessions, including creation
    and expiration times, IP address, and user agent, supporting features like
    session timeout and concurrent session management.
    """
    auth0_user = models.ForeignKey(
        Auth0User, 
        on_delete=models.CASCADE, 
        related_name="sessions"
    )
    session_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    last_activity = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        """
        String representation of the UserSession instance.
        
        Returns:
            str: String showing user email and session ID
        """
        return f"{self.auth0_user.email} - {self.session_id}"

    def is_expired(self):
        """
        Checks if the session has expired.
        
        Returns:
            bool: True if session is expired, False otherwise
        """
        return timezone.now() > self.expires_at

    def update_activity(self):
        """
        Updates the last activity timestamp.
        
        This method is typically called when a user performs an action to
        keep track of session activity and support session timeout.
        """
        self.last_activity = timezone.now()
        self.save()

    def extend_session(self):
        """
        Extends the session expiration time.
        
        This method is typically called when a user continues to be active
        to prevent session timeout during active use.
        """
        self.expires_at = timezone.now() + timedelta(hours=JWT_EXPIRATION_HOURS)
        self.save()

    def invalidate(self):
        """
        Invalidates the session.
        
        This method is typically called when a user logs out or when the
        system detects suspicious activity.
        """
        self.is_active = False
        self.save()


class RefreshToken(CoreModel):
    """
    Model for storing refresh tokens for obtaining new access tokens.
    
    This model maintains information about refresh tokens issued to users,
    supporting the JWT authentication flow and token rotation for security.
    """
    auth0_user = models.ForeignKey(
        Auth0User, 
        on_delete=models.CASCADE, 
        related_name="refresh_tokens"
    )
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    is_revoked = models.BooleanField(default=False)

    def __str__(self):
        """
        String representation of the RefreshToken instance.
        
        Returns:
            str: String showing user email and token ID
        """
        return f"{self.auth0_user.email} - {str(self.id)[:8]}"

    def is_valid(self):
        """
        Checks if the refresh token is valid.
        
        Returns:
            bool: True if token is valid, False otherwise
        """
        return (not self.is_revoked and timezone.now() < self.expires_at)

    def revoke(self):
        """
        Revokes the refresh token.
        
        This method is typically called when a user logs out or when the
        system detects suspicious activity.
        """
        self.is_revoked = True
        self.save()