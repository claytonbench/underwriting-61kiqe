"""
Unit tests for authentication serializers in the loan management system.

These tests validate the functionality of serializers used for authentication, token
management, MFA, password reset, and session management.
"""

import pytest
import uuid
from datetime import timedelta
from django.utils import timezone
from freezegun import freeze_time

from ..serializers import (
    LoginSerializer, TokenResponseSerializer, RefreshTokenSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    MFAEnableSerializer, MFAVerifySerializer, MFADisableSerializer,
    SessionLogoutSerializer, UserSessionSerializer, UserProfileSerializer,
    Auth0UserSerializer, MFAVerificationSerializer
)
from ..models import Auth0User, UserSession, MFAVerification, MFA_METHODS
from ...core.exceptions import ValidationException


@pytest.mark.serializer
@pytest.mark.auth
class TestLoginSerializer:
    """Test case for the LoginSerializer class"""
    
    def test_valid_data(self):
        """Test that valid login data passes validation"""
        data = {
            'email': 'test@example.com',
            'password': 'securepassword123'
        }
        serializer = LoginSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['email'] == 'test@example.com'
        assert serializer.validated_data['password'] == 'securepassword123'
    
    def test_missing_email(self):
        """Test that missing email fails validation"""
        data = {
            'password': 'securepassword123'
        }
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
    
    def test_invalid_email_format(self):
        """Test that invalid email format fails validation"""
        data = {
            'email': 'not_an_email',
            'password': 'securepassword123'
        }
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
    
    def test_missing_password(self):
        """Test that missing password fails validation"""
        data = {
            'email': 'test@example.com'
        }
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors
    
    def test_short_password(self):
        """Test that password shorter than minimum length fails validation"""
        data = {
            'email': 'test@example.com',
            'password': 'short'
        }
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors
    
    def test_email_normalization(self):
        """Test that email is normalized to lowercase"""
        data = {
            'email': 'Test@Example.com',
            'password': 'securepassword123'
        }
        serializer = LoginSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['email'] == 'test@example.com'


@pytest.mark.serializer
@pytest.mark.auth
class TestTokenResponseSerializer:
    """Test case for the TokenResponseSerializer class"""
    
    def test_valid_data(self):
        """Test that valid token response data is serialized correctly"""
        data = {
            'access_token': 'access_token_value',
            'refresh_token': 'refresh_token_value',
            'token_type': 'Bearer',
            'expires_in': 3600,
            'user': {'id': '123', 'email': 'test@example.com'}
        }
        serializer = TokenResponseSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['access_token'] == 'access_token_value'
        assert serializer.validated_data['refresh_token'] == 'refresh_token_value'
        assert serializer.validated_data['token_type'] == 'Bearer'
        assert serializer.validated_data['expires_in'] == 3600
        assert serializer.validated_data['user'] == {'id': '123', 'email': 'test@example.com'}
    
    def test_missing_fields(self):
        """Test that missing required fields fail validation"""
        data = {
            'access_token': 'access_token_value',
            'token_type': 'Bearer'
        }
        serializer = TokenResponseSerializer(data=data)
        assert not serializer.is_valid()
        assert 'refresh_token' in serializer.errors
        assert 'expires_in' in serializer.errors
        assert 'user' in serializer.errors


@pytest.mark.serializer
@pytest.mark.auth
class TestRefreshTokenSerializer:
    """Test case for the RefreshTokenSerializer class"""
    
    def test_valid_refresh_token(self):
        """Test that valid refresh token passes validation"""
        data = {
            'refresh_token': 'valid_refresh_token_value_123456789'
        }
        serializer = RefreshTokenSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['refresh_token'] == 'valid_refresh_token_value_123456789'
    
    def test_missing_refresh_token(self):
        """Test that missing refresh token fails validation"""
        data = {}
        serializer = RefreshTokenSerializer(data=data)
        assert not serializer.is_valid()
        assert 'refresh_token' in serializer.errors
    
    def test_short_refresh_token(self):
        """Test that refresh token shorter than minimum length fails validation"""
        data = {
            'refresh_token': 'short'
        }
        serializer = RefreshTokenSerializer(data=data)
        assert not serializer.is_valid()
        assert 'refresh_token' in serializer.errors


@pytest.mark.serializer
@pytest.mark.auth
class TestPasswordResetRequestSerializer:
    """Test case for the PasswordResetRequestSerializer class"""
    
    def test_valid_email(self):
        """Test that valid email passes validation"""
        data = {
            'email': 'test@example.com'
        }
        serializer = PasswordResetRequestSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['email'] == 'test@example.com'
    
    def test_missing_email(self):
        """Test that missing email fails validation"""
        data = {}
        serializer = PasswordResetRequestSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
    
    def test_invalid_email_format(self):
        """Test that invalid email format fails validation"""
        data = {
            'email': 'not_an_email'
        }
        serializer = PasswordResetRequestSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
    
    def test_email_normalization(self):
        """Test that email is normalized to lowercase"""
        data = {
            'email': 'Test@Example.com'
        }
        serializer = PasswordResetRequestSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['email'] == 'test@example.com'


@pytest.mark.serializer
@pytest.mark.auth
class TestPasswordResetConfirmSerializer:
    """Test case for the PasswordResetConfirmSerializer class"""
    
    def test_valid_data(self):
        """Test that valid reset confirmation data passes validation"""
        data = {
            'token': 'valid_token_string_123456789abcdef',
            'new_password': 'new_secure_password123'
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['token'] == 'valid_token_string_123456789abcdef'
        assert serializer.validated_data['new_password'] == 'new_secure_password123'
    
    def test_missing_token(self):
        """Test that missing token fails validation"""
        data = {
            'new_password': 'new_secure_password123'
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        assert not serializer.is_valid()
        assert 'token' in serializer.errors
    
    def test_missing_new_password(self):
        """Test that missing new password fails validation"""
        data = {
            'token': 'valid_token_string_123456789abcdef'
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        assert not serializer.is_valid()
        assert 'new_password' in serializer.errors
    
    def test_short_token(self):
        """Test that token shorter than minimum length fails validation"""
        data = {
            'token': 'short',
            'new_password': 'new_secure_password123'
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        assert not serializer.is_valid()
        assert 'token' in serializer.errors
    
    def test_weak_password(self):
        """Test that weak password fails validation"""
        data = {
            'token': 'valid_token_string_123456789abcdef',
            'new_password': 'weak'
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        assert not serializer.is_valid()
        assert 'new_password' in serializer.errors


@pytest.mark.serializer
@pytest.mark.auth
class TestMFAEnableSerializer:
    """Test case for the MFAEnableSerializer class"""
    
    def test_valid_sms_method(self):
        """Test that valid SMS MFA method passes validation"""
        data = {
            'method': MFA_METHODS['SMS'],
            'verification_contact': '(555) 123-4567'
        }
        serializer = MFAEnableSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['method'] == MFA_METHODS['SMS']
        assert serializer.validated_data['verification_contact'] == '(555) 123-4567'
    
    def test_valid_email_method(self):
        """Test that valid email MFA method passes validation"""
        data = {
            'method': MFA_METHODS['EMAIL'],
            'verification_contact': 'test@example.com'
        }
        serializer = MFAEnableSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['method'] == MFA_METHODS['EMAIL']
        assert serializer.validated_data['verification_contact'] == 'test@example.com'
    
    def test_valid_authenticator_method(self):
        """Test that valid authenticator MFA method passes validation"""
        data = {
            'method': MFA_METHODS['AUTHENTICATOR'],
            'verification_contact': ''  # Not needed for authenticator
        }
        serializer = MFAEnableSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['method'] == MFA_METHODS['AUTHENTICATOR']
    
    def test_missing_method(self):
        """Test that missing method fails validation"""
        data = {
            'verification_contact': '(555) 123-4567'
        }
        serializer = MFAEnableSerializer(data=data)
        assert not serializer.is_valid()
        assert 'method' in serializer.errors
    
    def test_invalid_method(self):
        """Test that invalid MFA method fails validation"""
        data = {
            'method': 'invalid_method',
            'verification_contact': '(555) 123-4567'
        }
        serializer = MFAEnableSerializer(data=data)
        assert not serializer.is_valid()
        assert 'method' in serializer.errors
    
    def test_missing_verification_contact(self):
        """Test that missing verification contact fails validation for SMS/email methods"""
        data = {
            'method': MFA_METHODS['SMS']
        }
        serializer = MFAEnableSerializer(data=data)
        assert not serializer.is_valid()
        assert 'verification_contact' in serializer.errors
    
    def test_invalid_phone_format(self):
        """Test that invalid phone format fails validation for SMS method"""
        data = {
            'method': MFA_METHODS['SMS'],
            'verification_contact': '5551234567'  # Missing formatting
        }
        serializer = MFAEnableSerializer(data=data)
        assert not serializer.is_valid()
        assert 'verification_contact' in serializer.errors
    
    def test_invalid_email_format(self):
        """Test that invalid email format fails validation for email method"""
        data = {
            'method': MFA_METHODS['EMAIL'],
            'verification_contact': 'not_an_email'
        }
        serializer = MFAEnableSerializer(data=data)
        assert not serializer.is_valid()
        assert 'verification_contact' in serializer.errors


@pytest.mark.serializer
@pytest.mark.auth
class TestMFAVerifySerializer:
    """Test case for the MFAVerifySerializer class"""
    
    def test_valid_data(self):
        """Test that valid MFA verification data passes validation"""
        data = {
            'method': MFA_METHODS['SMS'],
            'code': '123456'
        }
        serializer = MFAVerifySerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['method'] == MFA_METHODS['SMS']
        assert serializer.validated_data['code'] == '123456'
    
    def test_missing_method(self):
        """Test that missing method fails validation"""
        data = {
            'code': '123456'
        }
        serializer = MFAVerifySerializer(data=data)
        assert not serializer.is_valid()
        assert 'method' in serializer.errors
    
    def test_invalid_method(self):
        """Test that invalid MFA method fails validation"""
        data = {
            'method': 'invalid_method',
            'code': '123456'
        }
        serializer = MFAVerifySerializer(data=data)
        assert not serializer.is_valid()
        assert 'method' in serializer.errors
    
    def test_missing_code(self):
        """Test that missing verification code fails validation"""
        data = {
            'method': MFA_METHODS['SMS']
        }
        serializer = MFAVerifySerializer(data=data)
        assert not serializer.is_valid()
        assert 'code' in serializer.errors
    
    def test_invalid_code_format(self):
        """Test that non-numeric code fails validation"""
        data = {
            'method': MFA_METHODS['SMS'],
            'code': 'abcdef'
        }
        serializer = MFAVerifySerializer(data=data)
        assert not serializer.is_valid()
        assert 'code' in serializer.errors
    
    def test_short_code(self):
        """Test that code shorter than required length fails validation"""
        data = {
            'method': MFA_METHODS['SMS'],
            'code': '12345'  # Only 5 digits instead of 6
        }
        serializer = MFAVerifySerializer(data=data)
        assert not serializer.is_valid()
        assert 'code' in serializer.errors


@pytest.mark.serializer
@pytest.mark.auth
class TestMFADisableSerializer:
    """Test case for the MFADisableSerializer class"""
    
    def test_valid_method(self):
        """Test that valid MFA method passes validation"""
        data = {
            'method': MFA_METHODS['SMS']
        }
        serializer = MFADisableSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['method'] == MFA_METHODS['SMS']
    
    def test_missing_method(self):
        """Test that missing method fails validation"""
        data = {}
        serializer = MFADisableSerializer(data=data)
        assert not serializer.is_valid()
        assert 'method' in serializer.errors
    
    def test_invalid_method(self):
        """Test that invalid MFA method fails validation"""
        data = {
            'method': 'invalid_method'
        }
        serializer = MFADisableSerializer(data=data)
        assert not serializer.is_valid()
        assert 'method' in serializer.errors


@pytest.mark.serializer
@pytest.mark.auth
class TestSessionLogoutSerializer:
    """Test case for the SessionLogoutSerializer class"""
    
    def test_valid_session_id(self):
        """Test that valid session ID passes validation"""
        session_id = str(uuid.uuid4())
        data = {
            'session_id': session_id
        }
        serializer = SessionLogoutSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['session_id'] == session_id
    
    def test_missing_session_id(self):
        """Test that missing session ID fails validation"""
        data = {}
        serializer = SessionLogoutSerializer(data=data)
        assert not serializer.is_valid()
        assert 'session_id' in serializer.errors
    
    def test_invalid_session_id_format(self):
        """Test that non-UUID session ID fails validation"""
        data = {
            'session_id': 'not-a-uuid'
        }
        serializer = SessionLogoutSerializer(data=data)
        assert not serializer.is_valid()
        assert 'session_id' in serializer.errors


@pytest.mark.serializer
@pytest.mark.auth
class TestUserSessionSerializer:
    """Test case for the UserSessionSerializer class"""
    
    def test_serialization(self):
        """Test that UserSession is serialized correctly"""
        auth0_user = Auth0User(
            auth0_id='auth0|123456',
            email='test@example.com',
            email_verified=True,
            is_active=True
        )
        
        # Create a UserSession instance
        session = UserSession(
            auth0_user=auth0_user,
            session_id=str(uuid.uuid4()),
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address='127.0.0.1',
            user_agent='Test User Agent',
            is_active=True
        )
        
        serializer = UserSessionSerializer(session)
        data = serializer.data
        
        # Verify all expected fields are present
        assert 'id' in data
        assert 'session_id' in data
        assert 'created_at' in data
        assert 'expires_at' in data
        assert 'last_activity' in data
        assert 'ip_address' in data
        assert 'user_agent' in data
        assert 'is_active' in data
        assert 'remaining_time' in data
        
        # Check values
        assert data['session_id'] == session.session_id
        assert data['ip_address'] == '127.0.0.1'
        assert data['user_agent'] == 'Test User Agent'
        assert data['is_active'] is True
    
    def test_get_remaining_time_active(self):
        """Test that get_remaining_time returns correct value for active session"""
        auth0_user = Auth0User(
            auth0_id='auth0|123456',
            email='test@example.com'
        )
        
        now = timezone.now()
        expiry_time = now + timedelta(hours=1)
        
        # Create a UserSession instance with future expiration
        session = UserSession(
            auth0_user=auth0_user,
            session_id=str(uuid.uuid4()),
            expires_at=expiry_time,
            is_active=True
        )
        
        with freeze_time(now):
            serializer = UserSessionSerializer(session)
            remaining_time = serializer.get_remaining_time(session)
            
            # Should be close to 3600 seconds (1 hour)
            assert remaining_time > 0
            assert abs(remaining_time - 3600) < 5  # Allow for small processing time differences
    
    def test_get_remaining_time_expired(self):
        """Test that get_remaining_time returns 0 for expired session"""
        auth0_user = Auth0User(
            auth0_id='auth0|123456',
            email='test@example.com'
        )
        
        now = timezone.now()
        expiry_time = now - timedelta(hours=1)  # Expired 1 hour ago
        
        # Create a UserSession instance with past expiration
        session = UserSession(
            auth0_user=auth0_user,
            session_id=str(uuid.uuid4()),
            expires_at=expiry_time,
            is_active=True
        )
        
        serializer = UserSessionSerializer(session)
        remaining_time = serializer.get_remaining_time(session)
        
        # Should be 0 for expired session
        assert remaining_time == 0


@pytest.mark.serializer
@pytest.mark.auth
class TestUserProfileSerializer:
    """Test case for the UserProfileSerializer class"""
    
    def test_valid_data(self):
        """Test that valid user profile data is serialized correctly"""
        data = {
            'auth0_id': 'auth0|123456',
            'email': 'test@example.com',
            'email_verified': True,
            'mfa_methods': ['sms', 'authenticator'],
            'user_metadata': {'name': 'Test User', 'preferences': {'theme': 'dark'}}
        }
        serializer = UserProfileSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['auth0_id'] == 'auth0|123456'
        assert serializer.validated_data['email'] == 'test@example.com'
        assert serializer.validated_data['email_verified'] is True
        assert serializer.validated_data['mfa_methods'] == ['sms', 'authenticator']
        assert serializer.validated_data['user_metadata'] == {'name': 'Test User', 'preferences': {'theme': 'dark'}}
    
    def test_missing_fields(self):
        """Test that missing required fields fail validation"""
        data = {
            'auth0_id': 'auth0|123456',
            'email_verified': True
        }
        serializer = UserProfileSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors


@pytest.mark.serializer
@pytest.mark.auth
class TestAuth0UserSerializer:
    """Test case for the Auth0UserSerializer class"""
    
    def test_serialization(self):
        """Test that Auth0User is serialized correctly"""
        user = Auth0User(
            auth0_id='auth0|123456',
            email='test@example.com',
            email_verified=True,
            auth0_metadata='{"user_type": "borrower", "name": "Test User"}',
            is_active=True
        )
        
        serializer = Auth0UserSerializer(user)
        data = serializer.data
        
        # Verify all expected fields are present
        assert 'id' in data
        assert 'auth0_id' in data
        assert 'email' in data
        assert 'email_verified' in data
        assert 'last_login' in data
        assert 'is_active' in data
        assert 'user_type' in data
        
        # Check values
        assert data['auth0_id'] == 'auth0|123456'
        assert data['email'] == 'test@example.com'
        assert data['email_verified'] is True
        assert data['is_active'] is True
        assert data['user_type'] == 'borrower'
    
    def test_get_user_type(self):
        """Test that get_user_type returns correct user type from metadata"""
        user = Auth0User(
            auth0_id='auth0|123456',
            email='test@example.com',
            auth0_metadata='{"user_type": "borrower"}'
        )
        
        serializer = Auth0UserSerializer(user)
        user_type = serializer.get_user_type(user)
        
        assert user_type == 'borrower'
    
    def test_get_user_type_default(self):
        """Test that get_user_type returns 'unknown' when user_type not in metadata"""
        user = Auth0User(
            auth0_id='auth0|123456',
            email='test@example.com',
            auth0_metadata='{"name": "Test User"}'  # No user_type
        )
        
        serializer = Auth0UserSerializer(user)
        user_type = serializer.get_user_type(user)
        
        assert user_type == 'unknown'


@pytest.mark.serializer
@pytest.mark.auth
class TestMFAVerificationSerializer:
    """Test case for the MFAVerificationSerializer class"""
    
    def test_serialization(self):
        """Test that MFAVerification is serialized correctly"""
        auth0_user = Auth0User(
            auth0_id='auth0|123456',
            email='test@example.com'
        )
        
        mfa = MFAVerification(
            auth0_user=auth0_user,
            mfa_method=MFA_METHODS['SMS'],
            verification_contact='(555) 123-4567',
            status='enabled',
            enabled_at=timezone.now(),
            last_verified_at=timezone.now()
        )
        
        serializer = MFAVerificationSerializer(mfa)
        data = serializer.data
        
        # Verify all expected fields are present
        assert 'id' in data
        assert 'auth0_user' in data
        assert 'mfa_method' in data
        assert 'verification_contact' in data
        assert 'status' in data
        assert 'enabled_at' in data
        assert 'last_verified_at' in data
        
        # Check values
        assert data['mfa_method'] == MFA_METHODS['SMS']
        assert data['verification_contact'] == '(555) 123-4567'
        assert data['status'] == 'enabled'