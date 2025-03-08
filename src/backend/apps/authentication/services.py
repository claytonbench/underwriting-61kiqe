"""
Authentication service classes for the loan management system.

This module provides high-level services that encapsulate the business logic
for user authentication, session management, multi-factor authentication, and
token handling, acting as an intermediary between the API views and the
underlying Auth0 integration.
"""

import uuid
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction

from .auth0 import Auth0Manager
from .models import (
    Auth0User, UserSession, RefreshToken, MFAVerification, 
    LoginAttempt, MFA_METHODS
)
from .tokens import (
    generate_jwt_token, validate_jwt_token,
    generate_refresh_token, validate_refresh_token,
    generate_password_reset_token, validate_password_reset_token
)
from ...core.exceptions import AuthenticationException, ValidationException
from ...utils.constants import (
    JWT_EXPIRATION_HOURS, REFRESH_TOKEN_EXPIRATION_DAYS
)

# Configure logger
logger = logging.getLogger(__name__)


class AuthenticationService:
    """
    Service for handling user authentication, token management, and MFA operations.
    """
    
    def __init__(self):
        """
        Initializes the AuthenticationService with an Auth0Manager instance.
        """
        self.auth0_manager = Auth0Manager()

    def authenticate(self, email, password, ip_address=None, user_agent=None):
        """
        Authenticates a user with email and password.

        Args:
            email (str): User's email
            password (str): User's password
            ip_address (str): IP address of the request
            user_agent (str): User agent of the request

        Returns:
            dict: Authentication result with tokens and user info

        Raises:
            AuthenticationException: If authentication fails
        """
        # Check if account is locked
        if LoginAttempt.is_account_locked(email):
            logger.warning(f"Login attempt for locked account: {email}")
            raise AuthenticationException("Account is temporarily locked due to too many failed attempts")

        try:
            # Authenticate with Auth0
            auth_result = self.auth0_manager.authenticate_user(email, password)
            user = Auth0User.objects.get(auth0_id=auth_result['user']['auth0_id'])
            
            # Record successful login attempt
            login_service = LoginAttemptService()
            login_service.record_login_attempt(
                email, True, ip_address, user_agent, None
            )
            
            # Create user session
            session_service = SessionService()
            session = session_service.create_session(user, ip_address, user_agent)
            
            # Generate tokens
            token_service = TokenService()
            token_data = token_service.create_tokens(user, session)
            
            # Update last login timestamp
            user.update_last_login()
            
            # Return authentication result with tokens and user info
            return {
                'tokens': token_data,
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'email_verified': user.email_verified,
                    'auth0_id': user.auth0_id,
                    'session_id': session.session_id
                }
            }
            
        except Exception as e:
            # Record failed login attempt
            login_service = LoginAttemptService()
            login_service.record_login_attempt(
                email, False, ip_address, user_agent, str(e)
            )
            
            logger.error(f"Authentication failed for {email}: {str(e)}")
            raise AuthenticationException(f"Authentication failed: {str(e)}")

    def validate_token(self, token):
        """
        Validates an access token.

        Args:
            token (str): JWT token to validate

        Returns:
            dict: Validated token payload with user info

        Raises:
            AuthenticationException: If token is invalid
        """
        try:
            # Validate token
            payload = validate_jwt_token(token)
            
            # Get user from token
            user = self.auth0_manager.get_user_from_token(payload)
                
            # Return token payload with user info
            return {
                'payload': payload,
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'auth0_id': user.auth0_id
                }
            }
                
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            raise AuthenticationException(f"Token validation failed: {str(e)}")

    def refresh_token(self, refresh_token_str):
        """
        Refreshes an access token using a refresh token.

        Args:
            refresh_token_str (str): Refresh token string

        Returns:
            dict: New tokens and user info

        Raises:
            AuthenticationException: If refresh fails
        """
        try:
            # Validate refresh token
            payload = validate_refresh_token(refresh_token_str)
            
            if 'user_id' not in payload:
                raise AuthenticationException("Invalid refresh token: missing user_id claim")
                
            # Get user from token
            try:
                user = Auth0User.objects.get(id=payload['user_id'])
            except Auth0User.DoesNotExist:
                raise AuthenticationException("User not found")
                
            # Find refresh token in database
            try:
                token = RefreshToken.objects.get(token=refresh_token_str)
                
                # Check if token is valid
                if not token.is_valid():
                    raise AuthenticationException("Refresh token is expired or revoked")
                    
                # Generate new tokens
                token_service = TokenService()
                session_service = SessionService()
                
                # Get active session or create new one
                session = None
                if 'session_id' in payload:
                    try:
                        session = UserSession.objects.get(session_id=payload['session_id'])
                        if not session.is_active or session.is_expired():
                            session = None
                    except UserSession.DoesNotExist:
                        session = None
                
                if not session:
                    session = session_service.create_session(user, None, None)
                
                # Generate new tokens
                new_tokens = token_service.create_tokens(user, session)
                
                # Revoke old refresh token
                token_service.revoke_refresh_token(token)
                
                # Return new tokens
                return {
                    'tokens': new_tokens,
                    'user': {
                        'id': str(user.id),
                        'email': user.email,
                        'auth0_id': user.auth0_id,
                        'session_id': session.session_id
                    }
                }
                
            except RefreshToken.DoesNotExist:
                raise AuthenticationException("Refresh token not found")
                
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise AuthenticationException(f"Token refresh failed: {str(e)}")

    def logout(self, session_id):
        """
        Logs out a user by invalidating their session and tokens.

        Args:
            session_id (str): Session ID to invalidate

        Returns:
            bool: True if logout successful

        Raises:
            AuthenticationException: If logout fails
        """
        try:
            # Find session
            try:
                session = UserSession.objects.get(session_id=session_id)
            except UserSession.DoesNotExist:
                raise AuthenticationException("Session not found")
                
            # Invalidate session
            session_service = SessionService()
            session_service.invalidate_session(session)
            
            # Revoke associated refresh tokens
            token_service = TokenService()
            RefreshToken.objects.filter(auth0_user=session.auth0_user).update(is_revoked=True)
            
            return True
            
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            raise AuthenticationException(f"Logout failed: {str(e)}")

    def enable_mfa(self, user, method, verification_contact=None):
        """
        Enables multi-factor authentication for a user.

        Args:
            user (Auth0User): User to enable MFA for
            method (str): MFA method (sms, email, authenticator)
            verification_contact (str): Contact info for verification (phone/email)

        Returns:
            dict: MFA enrollment information

        Raises:
            AuthenticationException: If enabling MFA fails
        """
        # Validate MFA method
        valid_methods = [MFA_METHODS[key] for key in MFA_METHODS]
        if method not in valid_methods:
            raise ValidationException(f"Invalid MFA method. Must be one of: {', '.join(valid_methods)}")
            
        try:
            # Enable MFA in Auth0
            mfa_info = self.auth0_manager.enable_mfa(user, method, verification_contact)
            
            # Update MFA verification record
            try:
                with transaction.atomic():
                    mfa_verification, created = MFAVerification.objects.get_or_create(
                        auth0_user=user,
                        defaults={
                            'mfa_method': method,
                            'verification_contact': verification_contact
                        }
                    )
                    
                    if not created:
                        mfa_verification.mfa_method = method
                        mfa_verification.verification_contact = verification_contact
                        
                    mfa_verification.enable()
            except Exception as e:
                logger.error(f"Failed to update MFA verification record: {str(e)}")
                
            return mfa_info
            
        except Exception as e:
            logger.error(f"Failed to enable MFA: {str(e)}")
            raise AuthenticationException(f"Failed to enable MFA: {str(e)}")

    def verify_mfa(self, user, method, code):
        """
        Verifies a multi-factor authentication code.

        Args:
            user (Auth0User): User verifying MFA
            method (str): MFA method used
            code (str): Verification code

        Returns:
            bool: True if verification successful

        Raises:
            AuthenticationException: If verification fails
        """
        # Validate MFA method
        valid_methods = [MFA_METHODS[key] for key in MFA_METHODS]
        if method not in valid_methods:
            raise ValidationException(f"Invalid MFA method. Must be one of: {', '.join(valid_methods)}")
            
        try:
            # Verify MFA code with Auth0
            verified = self.auth0_manager.verify_mfa(user, method, code)
            
            if verified:
                # Update MFA verification record
                try:
                    mfa_verification = MFAVerification.objects.get(auth0_user=user)
                    mfa_verification.update_verification()
                except MFAVerification.DoesNotExist:
                    logger.warning(f"MFA verification record not found for user {user.email}")
                    
                return True
            else:
                raise AuthenticationException("MFA verification failed")
                
        except Exception as e:
            logger.error(f"MFA verification failed: {str(e)}")
            raise AuthenticationException(f"MFA verification failed: {str(e)}")

    def disable_mfa(self, user, method):
        """
        Disables multi-factor authentication for a user.

        Args:
            user (Auth0User): User to disable MFA for
            method (str): MFA method to disable

        Returns:
            bool: True if MFA disabled successfully

        Raises:
            AuthenticationException: If disabling MFA fails
        """
        # Validate MFA method
        valid_methods = [MFA_METHODS[key] for key in MFA_METHODS]
        if method not in valid_methods:
            raise ValidationException(f"Invalid MFA method. Must be one of: {', '.join(valid_methods)}")
            
        try:
            # Disable MFA in Auth0
            disabled = self.auth0_manager.disable_mfa(user, method)
            
            if disabled:
                # Update MFA verification record
                try:
                    mfa_verification = MFAVerification.objects.get(auth0_user=user)
                    mfa_verification.disable()
                except MFAVerification.DoesNotExist:
                    logger.warning(f"MFA verification record not found for user {user.email}")
                    
                return True
            else:
                raise AuthenticationException("Failed to disable MFA")
                
        except Exception as e:
            logger.error(f"Failed to disable MFA: {str(e)}")
            raise AuthenticationException(f"Failed to disable MFA: {str(e)}")

    def get_mfa_methods(self, user):
        """
        Gets the MFA methods enabled for a user.

        Args:
            user (Auth0User): User to get MFA methods for

        Returns:
            dict: MFA methods and status

        Raises:
            AuthenticationException: If getting MFA methods fails
        """
        try:
            # Try to get MFA verification record
            try:
                mfa_verification = MFAVerification.objects.get(auth0_user=user)
                
                return {
                    'method': mfa_verification.mfa_method,
                    'status': mfa_verification.status,
                    'enabled': mfa_verification.is_enabled(),
                    'verification_contact': mfa_verification.verification_contact,
                    'last_verified_at': mfa_verification.last_verified_at.isoformat() if mfa_verification.last_verified_at else None
                }
            except MFAVerification.DoesNotExist:
                return {
                    'method': None,
                    'status': 'disabled',
                    'enabled': False,
                    'verification_contact': None,
                    'last_verified_at': None
                }
                
        except Exception as e:
            logger.error(f"Failed to get MFA methods: {str(e)}")
            raise AuthenticationException(f"Failed to get MFA methods: {str(e)}")

    def request_password_reset(self, email):
        """
        Initiates a password reset for a user.

        Args:
            email (str): User's email

        Returns:
            bool: True if reset request successful

        Raises:
            AuthenticationException: If reset request fails
        """
        try:
            # Request password reset from Auth0
            return self.auth0_manager.reset_password(email)
        except Exception as e:
            logger.error(f"Failed to request password reset: {str(e)}")
            return False

    def reset_password(self, token, new_password):
        """
        Resets a user's password using a reset token.

        Args:
            token (str): Password reset token
            new_password (str): New password

        Returns:
            bool: True if password reset successful

        Raises:
            AuthenticationException: If password reset fails
        """
        try:
            # Validate password reset token
            payload = validate_password_reset_token(token)
            
            if 'user_id' not in payload:
                raise AuthenticationException("Invalid reset token: missing user_id claim")
                
            # Get user
            try:
                user = Auth0User.objects.get(id=payload['user_id'])
            except Auth0User.DoesNotExist:
                raise AuthenticationException("User not found")
                
            # Change password in Auth0
            self.auth0_manager.change_password(user, new_password)
            
            # Invalidate all user sessions
            session_service = SessionService()
            session_service.invalidate_all_user_sessions(user)
            
            # Revoke all refresh tokens
            token_service = TokenService()
            token_service.revoke_all_user_tokens(user)
            
            return True
            
        except Exception as e:
            logger.error(f"Password reset failed: {str(e)}")
            raise AuthenticationException(f"Password reset failed: {str(e)}")

    def get_user_profile(self, user):
        """
        Gets a user's profile information.

        Args:
            user (Auth0User): User to get profile for

        Returns:
            dict: User profile information

        Raises:
            AuthenticationException: If getting profile fails
        """
        try:
            # Get user profile from Auth0
            profile = self.auth0_manager.get_user_profile(user)
            
            # Get MFA methods
            mfa_info = self.get_mfa_methods(user)
            
            # Combine profile and MFA information
            profile['mfa'] = mfa_info
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to get user profile: {str(e)}")
            raise AuthenticationException(f"Failed to get user profile: {str(e)}")


class SessionService:
    """
    Service for managing user sessions.
    """

    def create_session(self, user, ip_address=None, user_agent=None):
        """
        Creates a new user session.

        Args:
            user (Auth0User): The user to create a session for
            ip_address (str): IP address of the client
            user_agent (str): User agent of the client

        Returns:
            UserSession: Created session object

        Raises:
            AuthenticationException: If session creation fails
        """
        try:
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Calculate session expiration time based on user type
            # For now, use a fixed expiration time
            expires_at = timezone.now() + timedelta(hours=JWT_EXPIRATION_HOURS)
            
            # Create session record
            session = UserSession.objects.create(
                auth0_user=user,
                session_id=session_id,
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to create session: {str(e)}")
            raise AuthenticationException(f"Failed to create session: {str(e)}")

    def get_session(self, session_id):
        """
        Gets a user session by session ID.

        Args:
            session_id (str): Session ID to retrieve

        Returns:
            UserSession: Session object if found and valid

        Raises:
            AuthenticationException: If session not found or invalid
        """
        try:
            session = UserSession.objects.get(session_id=session_id)
            
            # Check if session is active
            if not session.is_active:
                raise AuthenticationException("Session is inactive")
                
            # Check if session is expired
            if session.is_expired():
                raise AuthenticationException("Session has expired")
                
            # Update last activity
            session.update_activity()
            
            return session
            
        except UserSession.DoesNotExist:
            raise AuthenticationException("Session not found")
        except Exception as e:
            logger.error(f"Failed to get session: {str(e)}")
            raise AuthenticationException(f"Failed to get session: {str(e)}")

    def get_active_sessions(self, user):
        """
        Gets all active sessions for a user.

        Args:
            user (Auth0User): User to get sessions for

        Returns:
            QuerySet: QuerySet of active user sessions
        """
        now = timezone.now()
        return UserSession.objects.filter(
            auth0_user=user,
            is_active=True,
            expires_at__gt=now
        )

    def invalidate_session(self, session):
        """
        Invalidates a specific user session.

        Args:
            session (UserSession): Session to invalidate

        Returns:
            bool: True if session invalidated successfully

        Raises:
            AuthenticationException: If invalidation fails
        """
        try:
            session.invalidate()
            return True
        except Exception as e:
            logger.error(f"Failed to invalidate session: {str(e)}")
            raise AuthenticationException(f"Failed to invalidate session: {str(e)}")

    def invalidate_all_user_sessions(self, user):
        """
        Invalidates all sessions for a user.

        Args:
            user (Auth0User): User to invalidate sessions for

        Returns:
            int: Number of sessions invalidated
        """
        active_sessions = self.get_active_sessions(user)
        count = 0
        
        for session in active_sessions:
            try:
                session.invalidate()
                count += 1
            except Exception as e:
                logger.warning(f"Failed to invalidate session {session.session_id}: {str(e)}")
                
        return count

    def extend_session(self, session):
        """
        Extends the expiration time of a session.

        Args:
            session (UserSession): Session to extend

        Returns:
            UserSession: Updated session object
        """
        # Calculate new expiration time
        new_expiry = timezone.now() + timedelta(hours=JWT_EXPIRATION_HOURS)
        
        # Update session
        session.expires_at = new_expiry
        session.update_activity()
        session.save()
        
        return session


class TokenService:
    """
    Service for managing authentication tokens.
    """

    def create_tokens(self, user, session):
        """
        Creates access and refresh tokens for a user.

        Args:
            user (Auth0User): User to create tokens for
            session (UserSession): User session

        Returns:
            dict: Dictionary containing access and refresh tokens
        """
        # Create token payload
        payload = {
            'user_id': str(user.id),
            'session_id': session.session_id,
            'user_type': 'user'  # This could be extracted from user metadata
        }
        
        # Generate access token
        access_token = generate_jwt_token(payload)
        
        # Generate refresh token
        refresh_token_str = generate_refresh_token(str(user.id))
        
        # Store refresh token in database
        refresh_token = RefreshToken.objects.create(
            auth0_user=user,
            token=refresh_token_str,
            expires_at=timezone.now() + timedelta(days=REFRESH_TOKEN_EXPIRATION_DAYS)
        )
        
        # Return token data
        return {
            'access_token': access_token,
            'refresh_token': refresh_token_str,
            'token_type': 'Bearer',
            'expires_in': JWT_EXPIRATION_HOURS * 3600  # Convert hours to seconds
        }

    def refresh_access_token(self, refresh_token):
        """
        Creates a new access token using a refresh token.

        Args:
            refresh_token (RefreshToken): Refresh token object

        Returns:
            dict: Dictionary containing new access token
        """
        # Check if refresh token is valid
        if not refresh_token.is_valid():
            raise AuthenticationException("Refresh token is expired or revoked")
            
        # Get user
        user = refresh_token.auth0_user
        
        # Create token payload
        payload = {
            'user_id': str(user.id),
            'user_type': 'user'  # This could be extracted from user metadata
        }
        
        # Generate new access token
        access_token = generate_jwt_token(payload)
        
        # Return token data
        return {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': JWT_EXPIRATION_HOURS * 3600  # Convert hours to seconds
        }

    def revoke_refresh_token(self, refresh_token):
        """
        Revokes a refresh token.

        Args:
            refresh_token (RefreshToken): Refresh token to revoke

        Returns:
            bool: True if token revoked successfully
        """
        try:
            refresh_token.revoke()
            return True
        except Exception as e:
            logger.error(f"Failed to revoke refresh token: {str(e)}")
            raise AuthenticationException(f"Failed to revoke refresh token: {str(e)}")

    def revoke_all_user_tokens(self, user):
        """
        Revokes all refresh tokens for a user.

        Args:
            user (Auth0User): User to revoke tokens for

        Returns:
            int: Number of tokens revoked
        """
        # Get all active refresh tokens for user
        active_tokens = RefreshToken.objects.filter(
            auth0_user=user,
            is_revoked=False,
            expires_at__gt=timezone.now()
        )
        
        count = 0
        for token in active_tokens:
            try:
                token.revoke()
                count += 1
            except Exception as e:
                logger.warning(f"Failed to revoke token {token.id}: {str(e)}")
                
        return count


class LoginAttemptService:
    """
    Service for tracking and managing login attempts.
    """

    def record_login_attempt(self, email, success, ip_address=None, user_agent=None, failure_reason=None):
        """
        Records a login attempt in the database.

        Args:
            email (str): Email address used for login
            success (bool): Whether the login attempt was successful
            ip_address (str): IP address of the client
            user_agent (str): User agent of the client
            failure_reason (str): Reason for failure if unsuccessful

        Returns:
            LoginAttempt: Created login attempt record
        """
        return LoginAttempt.objects.create(
            email=email,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason=failure_reason,
            timestamp=timezone.now()
        )

    def check_account_lockout(self, email):
        """
        Checks if an account is locked due to too many failed attempts.

        Args:
            email (str): Email address to check

        Returns:
            bool: True if account is locked, False otherwise
        """
        return LoginAttempt.is_account_locked(email)

    def get_login_history(self, email, limit=10):
        """
        Gets login history for a user.

        Args:
            email (str): Email address to get history for
            limit (int): Maximum number of entries to return

        Returns:
            QuerySet: QuerySet of login attempts
        """
        return LoginAttempt.objects.filter(email=email).order_by('-timestamp')[:limit]