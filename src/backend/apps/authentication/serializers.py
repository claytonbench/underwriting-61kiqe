"""
Serializers for authentication-related data in the loan management system.

These serializers handle validation, data transformation, and representation for authentication
operations including login, token management, MFA, password reset, and session management.
"""

from rest_framework import serializers  # version 3.14+
from django.core.validators import validate_email  # version 4.2+
from django.contrib.auth.password_validation import validate_password  # version 4.2+
from django.utils import timezone
import re
import uuid
import json

from ...core.serializers import BaseSerializer, BaseModelSerializer
from ...core.exceptions import ValidationException
from .models import Auth0User, UserSession, MFAVerification, MFA_METHODS


class LoginSerializer(BaseSerializer):
    """Serializer for user login requests"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        """
        Validates the email field.

        Args:
            value (str): Email value to validate

        Returns:
            str: Validated email

        Raises:
            ValidationException: If email validation fails
        """
        if not value:
            raise ValidationException("Email is required")
        
        try:
            validate_email(value)
        except Exception as e:
            raise ValidationException(f"Invalid email format: {str(e)}")
        
        # Return lowercase email for consistency
        return value.lower()

    def validate_password(self, value):
        """
        Validates the password field.

        Args:
            value (str): Password value to validate

        Returns:
            str: Validated password

        Raises:
            ValidationException: If password validation fails
        """
        if not value:
            raise ValidationException("Password is required")
        
        if len(value) < 12:  # Based on PASSWORD_MIN_LENGTH in constants.py
            raise ValidationException("Password must be at least 12 characters long")
        
        return value


class TokenResponseSerializer(BaseSerializer):
    """Serializer for authentication token responses"""
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    token_type = serializers.CharField()
    expires_in = serializers.IntegerField()
    user = serializers.DictField()


class RefreshTokenSerializer(BaseSerializer):
    """Serializer for refresh token requests"""
    refresh_token = serializers.CharField()

    def validate_refresh_token(self, value):
        """
        Validates the refresh token field.

        Args:
            value (str): Refresh token value to validate

        Returns:
            str: Validated refresh token

        Raises:
            ValidationException: If refresh token validation fails
        """
        if not value:
            raise ValidationException("Refresh token is required")
        
        if len(value) < 20:  # Typical JWT tokens are much longer
            raise ValidationException("Invalid refresh token format")
        
        return value


class PasswordResetRequestSerializer(BaseSerializer):
    """Serializer for password reset requests"""
    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Validates the email field.

        Args:
            value (str): Email value to validate

        Returns:
            str: Validated email

        Raises:
            ValidationException: If email validation fails
        """
        if not value:
            raise ValidationException("Email is required")
        
        try:
            validate_email(value)
        except Exception as e:
            raise ValidationException(f"Invalid email format: {str(e)}")
        
        # Return lowercase email for consistency
        return value.lower()


class PasswordResetConfirmSerializer(BaseSerializer):
    """Serializer for password reset confirmation"""
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_token(self, value):
        """
        Validates the token field.

        Args:
            value (str): Token value to validate

        Returns:
            str: Validated token

        Raises:
            ValidationException: If token validation fails
        """
        if not value:
            raise ValidationException("Token is required")
        
        if len(value) < 20:  # Typical reset tokens are quite long
            raise ValidationException("Invalid token format")
        
        return value

    def validate_new_password(self, value):
        """
        Validates the new password field.

        Args:
            value (str): New password value to validate

        Returns:
            str: Validated new password

        Raises:
            ValidationException: If new password validation fails
        """
        if not value:
            raise ValidationException("New password is required")
        
        try:
            validate_password(value)
        except Exception as e:
            raise ValidationException(f"Password validation failed: {str(e)}")
        
        return value


class MFAEnableSerializer(BaseSerializer):
    """Serializer for enabling multi-factor authentication"""
    method = serializers.ChoiceField(choices=list(MFA_METHODS.values()))
    verification_contact = serializers.CharField()

    def validate_method(self, value):
        """
        Validates the MFA method field.

        Args:
            value (str): MFA method value to validate

        Returns:
            str: Validated MFA method

        Raises:
            ValidationException: If MFA method validation fails
        """
        if not value:
            raise ValidationException("MFA method is required")
        
        if value not in MFA_METHODS.values():
            raise ValidationException(f"Invalid MFA method. Supported methods: {', '.join(MFA_METHODS.values())}")
        
        return value

    def validate_verification_contact(self, value):
        """
        Validates the verification contact field.

        Args:
            value (str): Verification contact value to validate

        Returns:
            str: Validated verification contact

        Raises:
            ValidationException: If verification contact validation fails
        """
        if not value:
            raise ValidationException("Verification contact is required")
        
        method = self.initial_data.get('method')
        
        if method == MFA_METHODS['EMAIL']:
            # Validate email format
            try:
                validate_email(value)
            except Exception:
                raise ValidationException("Invalid email format for verification contact")
        elif method == MFA_METHODS['SMS']:
            # Validate phone number format using regex from constants
            if not re.match(r'^\(\d{3}\) \d{3}-\d{4}$', value):
                raise ValidationException("Invalid phone format. Expected format: (XXX) XXX-XXXX")
        
        return value


class MFAVerifySerializer(BaseSerializer):
    """Serializer for verifying multi-factor authentication"""
    method = serializers.ChoiceField(choices=list(MFA_METHODS.values()))
    code = serializers.CharField()

    def validate_method(self, value):
        """
        Validates the MFA method field.

        Args:
            value (str): MFA method value to validate

        Returns:
            str: Validated MFA method

        Raises:
            ValidationException: If MFA method validation fails
        """
        if not value:
            raise ValidationException("MFA method is required")
        
        if value not in MFA_METHODS.values():
            raise ValidationException(f"Invalid MFA method. Supported methods: {', '.join(MFA_METHODS.values())}")
        
        return value

    def validate_code(self, value):
        """
        Validates the verification code field.

        Args:
            value (str): Verification code value to validate

        Returns:
            str: Validated verification code

        Raises:
            ValidationException: If verification code validation fails
        """
        if not value:
            raise ValidationException("Verification code is required")
        
        # Check if code is a 6-digit number
        if not re.match(r'^\d{6}$', value):
            raise ValidationException("Verification code must be a 6-digit number")
        
        return value


class MFADisableSerializer(BaseSerializer):
    """Serializer for disabling multi-factor authentication"""
    method = serializers.ChoiceField(choices=list(MFA_METHODS.values()))

    def validate_method(self, value):
        """
        Validates the MFA method field.

        Args:
            value (str): MFA method value to validate

        Returns:
            str: Validated MFA method

        Raises:
            ValidationException: If MFA method validation fails
        """
        if not value:
            raise ValidationException("MFA method is required")
        
        if value not in MFA_METHODS.values():
            raise ValidationException(f"Invalid MFA method. Supported methods: {', '.join(MFA_METHODS.values())}")
        
        return value


class SessionLogoutSerializer(BaseSerializer):
    """Serializer for session logout requests"""
    session_id = serializers.CharField()

    def validate_session_id(self, value):
        """
        Validates the session ID field.

        Args:
            value (str): Session ID value to validate

        Returns:
            str: Validated session ID

        Raises:
            ValidationException: If session ID validation fails
        """
        if not value:
            raise ValidationException("Session ID is required")
        
        # Validate UUID format
        try:
            uuid.UUID(value)
        except ValueError:
            raise ValidationException("Invalid session ID format")
        
        return value


class UserSessionSerializer(BaseModelSerializer):
    """Serializer for user session data"""
    remaining_time = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSession
        fields = ['id', 'session_id', 'created_at', 'expires_at', 'last_activity', 
                  'ip_address', 'user_agent', 'is_active', 'remaining_time']

    def get_remaining_time(self, obj):
        """
        Calculates remaining session time in seconds.

        Args:
            obj (UserSession): The session object

        Returns:
            int: Remaining time in seconds
        """
        if not obj.expires_at:
            return 0
        
        remaining = (obj.expires_at - timezone.now()).total_seconds()
        return max(0, int(remaining))


class UserProfileSerializer(BaseSerializer):
    """Serializer for user profile information"""
    auth0_id = serializers.CharField()
    email = serializers.EmailField()
    email_verified = serializers.BooleanField()
    mfa_methods = serializers.ListField(child=serializers.CharField(), required=False)
    user_metadata = serializers.DictField(required=False)


class Auth0UserSerializer(BaseModelSerializer):
    """Serializer for Auth0User model"""
    user_type = serializers.SerializerMethodField()
    
    class Meta:
        model = Auth0User
        fields = ['id', 'auth0_id', 'email', 'email_verified', 'last_login', 
                  'is_active', 'user_type']

    def get_user_type(self, obj):
        """
        Gets the user type from user metadata.

        Args:
            obj (Auth0User): The Auth0User object

        Returns:
            str: User type
        """
        if obj.auth0_metadata:
            try:
                metadata = json.loads(obj.auth0_metadata)
                return metadata.get('user_type', 'unknown')
            except Exception:
                pass
        
        return 'unknown'


class MFAVerificationSerializer(BaseModelSerializer):
    """Serializer for MFAVerification model"""
    
    class Meta:
        model = MFAVerification
        fields = ['id', 'auth0_user', 'mfa_method', 'verification_contact', 
                  'status', 'enabled_at', 'last_verified_at']