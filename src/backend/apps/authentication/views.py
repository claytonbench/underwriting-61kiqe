"""
Authentication views for the loan management system.

This module provides API views for authentication-related functionality including user login,
token management, multi-factor authentication, password reset, session management, and user
profile operations. These views serve as the interface between clients and the authentication
service layer.
"""

import logging
from rest_framework.response import Response  # rest_framework 3.14+
from rest_framework import status  # rest_framework 3.14+
from rest_framework.views import APIView  # rest_framework 3.14+
from ipware import get_client_ip  # ipware 1.0.0+

from ...core.views import BaseAPIView
from ...core.exceptions import AuthenticationException, ValidationException
from ...core.permissions import IsAuthenticated

from .services import AuthenticationService, SessionService
from .serializers import (
    LoginSerializer, TokenResponseSerializer, RefreshTokenSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    MFAEnableSerializer, MFAVerifySerializer, MFADisableSerializer,
    SessionLogoutSerializer, UserSessionSerializer, UserProfileSerializer
)
from .auth0 import Auth0Authentication
from .permissions import CanManageSessions, CanManageMFA, AllowAnyForPasswordReset

# Configure logger
logger = logging.getLogger(__name__)


class LoginView(BaseAPIView):
    """
    API view for user login.
    
    Handles authentication requests and returns access tokens upon successful login.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the login view with authentication service."""
        super().__init__(*args, **kwargs)
        self.auth_service = AuthenticationService()
    
    def post(self, request):
        """
        Handle POST request for user login.
        
        Args:
            request: HTTP request object containing login credentials
            
        Returns:
            Response: Authentication response with tokens if successful
        """
        # Validate request data
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract credentials from validated data
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Get client IP and user agent for security tracking
        client_ip, _ = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Authenticate the user
        auth_result = self.auth_service.authenticate(
            email=email, 
            password=password, 
            ip_address=client_ip, 
            user_agent=user_agent
        )
        
        # Serialize and return the response
        response_serializer = TokenResponseSerializer(auth_result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class TokenRefreshView(BaseAPIView):
    """
    API view for refreshing access tokens.
    
    Handles refresh token requests to issue new access tokens without requiring
    the user to reauthenticate.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the token refresh view with authentication service."""
        super().__init__(*args, **kwargs)
        self.auth_service = AuthenticationService()
    
    def post(self, request):
        """
        Handle POST request for token refresh.
        
        Args:
            request: HTTP request object containing refresh token
            
        Returns:
            Response: New access token response if successful
        """
        # Validate request data
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract refresh token from validated data
        refresh_token = serializer.validated_data['refresh_token']
        
        # Refresh the token
        refresh_result = self.auth_service.refresh_token(refresh_token)
        
        # Serialize and return the response
        response_serializer = TokenResponseSerializer(refresh_result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class TokenValidateView(BaseAPIView):
    """
    API view for validating access tokens.
    
    Allows clients to verify if a token is valid without making an authenticated request.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the token validation view with authentication service."""
        super().__init__(*args, **kwargs)
        self.auth_service = AuthenticationService()
    
    def post(self, request):
        """
        Handle POST request for token validation.
        
        Args:
            request: HTTP request object containing token to validate
            
        Returns:
            Response: Token validation response
        """
        # Extract token from request data
        token = request.data.get('token')
        if not token:
            raise ValidationException("Token is required")
        
        # Validate the token
        validation_result = self.auth_service.validate_token(token)
        
        # Return the validation result
        return Response(validation_result, status=status.HTTP_200_OK)


class LogoutView(BaseAPIView):
    """
    API view for user logout.
    
    Handles session termination and token revocation.
    """
    
    authentication_classes = [Auth0Authentication]
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        """Initialize the logout view with authentication service."""
        super().__init__(*args, **kwargs)
        self.auth_service = AuthenticationService()
    
    def post(self, request):
        """
        Handle POST request for user logout.
        
        Args:
            request: Authenticated HTTP request
            
        Returns:
            Response: Logout confirmation response
        """
        # Extract session ID from auth token
        session_id = getattr(request.auth, 'session_id', None)
        
        # Log the user out
        self.auth_service.logout(session_id)
        
        # Return success response
        return Response(
            {"message": "Successfully logged out"}, 
            status=status.HTTP_200_OK
        )


class PasswordResetRequestView(BaseAPIView):
    """
    API view for requesting password reset.
    
    Initiates the password reset process by sending a reset link to the user's email.
    """
    
    permission_classes = [AllowAnyForPasswordReset]
    
    def __init__(self, *args, **kwargs):
        """Initialize the password reset request view with authentication service."""
        super().__init__(*args, **kwargs)
        self.auth_service = AuthenticationService()
    
    def post(self, request):
        """
        Handle POST request for password reset request.
        
        Args:
            request: HTTP request object containing user email
            
        Returns:
            Response: Password reset request confirmation
        """
        # Validate request data
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract email from validated data
        email = serializer.validated_data['email']
        
        # Request password reset
        self.auth_service.request_password_reset(email)
        
        # Return success response (always return success even if email doesn't exist for security)
        return Response(
            {"message": "Password reset instructions have been sent if the email exists"}, 
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(BaseAPIView):
    """
    API view for confirming password reset.
    
    Completes the password reset process by setting a new password using a valid token.
    """
    
    permission_classes = [AllowAnyForPasswordReset]
    
    def __init__(self, *args, **kwargs):
        """Initialize the password reset confirm view with authentication service."""
        super().__init__(*args, **kwargs)
        self.auth_service = AuthenticationService()
    
    def post(self, request):
        """
        Handle POST request for password reset confirmation.
        
        Args:
            request: HTTP request object containing reset token and new password
            
        Returns:
            Response: Password reset confirmation response
        """
        # Validate request data
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract token and new password from validated data
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        # Reset the password
        self.auth_service.reset_password(token, new_password)
        
        # Return success response
        return Response(
            {"message": "Password has been successfully reset"}, 
            status=status.HTTP_200_OK
        )


class MFAEnableView(BaseAPIView):
    """
    API view for enabling multi-factor authentication.
    
    Allows users to set up MFA for their account using methods like SMS, email, or authenticator apps.
    """
    
    authentication_classes = [Auth0Authentication]
    permission_classes = [IsAuthenticated, CanManageMFA]
    
    def __init__(self, *args, **kwargs):
        """Initialize the MFA enable view with authentication service."""
        super().__init__(*args, **kwargs)
        self.auth_service = AuthenticationService()
    
    def post(self, request):
        """
        Handle POST request for enabling MFA.
        
        Args:
            request: Authenticated HTTP request with MFA method and verification contact
            
        Returns:
            Response: MFA enrollment information
        """
        # Validate request data
        serializer = MFAEnableSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract method and verification contact from validated data
        method = serializer.validated_data['method']
        verification_contact = serializer.validated_data.get('verification_contact')
        
        # Get user from request
        user = request.user
        
        # Enable MFA for the user
        mfa_info = self.auth_service.enable_mfa(user, method, verification_contact)
        
        # Return MFA enrollment information
        return Response(mfa_info, status=status.HTTP_200_OK)


class MFAVerifyView(BaseAPIView):
    """
    API view for verifying multi-factor authentication.
    
    Handles verification of MFA codes during the enrollment or authentication process.
    """
    
    authentication_classes = [Auth0Authentication]
    permission_classes = [IsAuthenticated, CanManageMFA]
    
    def __init__(self, *args, **kwargs):
        """Initialize the MFA verify view with authentication service."""
        super().__init__(*args, **kwargs)
        self.auth_service = AuthenticationService()
    
    def post(self, request):
        """
        Handle POST request for verifying MFA.
        
        Args:
            request: Authenticated HTTP request with MFA method and verification code
            
        Returns:
            Response: MFA verification confirmation
        """
        # Validate request data
        serializer = MFAVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract method and code from validated data
        method = serializer.validated_data['method']
        code = serializer.validated_data['code']
        
        # Get user from request
        user = request.user
        
        # Verify MFA code
        self.auth_service.verify_mfa(user, method, code)
        
        # Return success response
        return Response(
            {"message": "MFA verification successful"}, 
            status=status.HTTP_200_OK
        )


class MFADisableView(BaseAPIView):
    """
    API view for disabling multi-factor authentication.
    
    Allows users to turn off MFA for their account.
    """
    
    authentication_classes = [Auth0Authentication]
    permission_classes = [IsAuthenticated, CanManageMFA]
    
    def __init__(self, *args, **kwargs):
        """Initialize the MFA disable view with authentication service."""
        super().__init__(*args, **kwargs)
        self.auth_service = AuthenticationService()
    
    def post(self, request):
        """
        Handle POST request for disabling MFA.
        
        Args:
            request: Authenticated HTTP request with MFA method to disable
            
        Returns:
            Response: MFA disable confirmation
        """
        # Validate request data
        serializer = MFADisableSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract method from validated data
        method = serializer.validated_data['method']
        
        # Get user from request
        user = request.user
        
        # Disable MFA for the user
        self.auth_service.disable_mfa(user, method)
        
        # Return success response
        return Response(
            {"message": "MFA has been disabled"}, 
            status=status.HTTP_200_OK
        )


class MFAStatusView(BaseAPIView):
    """
    API view for getting MFA status.
    
    Provides information about a user's current MFA configuration.
    """
    
    authentication_classes = [Auth0Authentication]
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        """Initialize the MFA status view with authentication service."""
        super().__init__(*args, **kwargs)
        self.auth_service = AuthenticationService()
    
    def get(self, request):
        """
        Handle GET request for MFA status.
        
        Args:
            request: Authenticated HTTP request
            
        Returns:
            Response: MFA status information
        """
        # Get user from request
        user = request.user
        
        # Get MFA methods for the user
        mfa_info = self.auth_service.get_mfa_methods(user)
        
        # Return MFA status information
        return Response(mfa_info, status=status.HTTP_200_OK)


class UserProfileView(BaseAPIView):
    """
    API view for getting user profile information.
    
    Provides access to the authenticated user's profile data.
    """
    
    authentication_classes = [Auth0Authentication]
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        """Initialize the user profile view with authentication service."""
        super().__init__(*args, **kwargs)
        self.auth_service = AuthenticationService()
    
    def get(self, request):
        """
        Handle GET request for user profile.
        
        Args:
            request: Authenticated HTTP request
            
        Returns:
            Response: User profile information
        """
        # Get user from request
        user = request.user
        
        # Get user profile
        profile = self.auth_service.get_user_profile(user)
        
        # Serialize and return the profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SessionListView(BaseAPIView):
    """
    API view for listing active user sessions.
    
    Provides information about all active sessions for the authenticated user.
    """
    
    authentication_classes = [Auth0Authentication]
    permission_classes = [IsAuthenticated, CanManageSessions]
    
    def __init__(self, *args, **kwargs):
        """Initialize the session list view with session service."""
        super().__init__(*args, **kwargs)
        self.session_service = SessionService()
    
    def get(self, request):
        """
        Handle GET request for listing sessions.
        
        Args:
            request: Authenticated HTTP request
            
        Returns:
            Response: List of active sessions
        """
        # Get user from request
        user = request.user
        
        # Get active sessions for the user
        sessions = self.session_service.get_active_sessions(user)
        
        # Serialize and return the sessions
        serializer = UserSessionSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SessionLogoutView(BaseAPIView):
    """
    API view for logging out a specific session.
    
    Allows users to terminate a specific session, useful for managing multiple devices.
    """
    
    authentication_classes = [Auth0Authentication]
    permission_classes = [IsAuthenticated, CanManageSessions]
    
    def __init__(self, *args, **kwargs):
        """Initialize the session logout view with session service."""
        super().__init__(*args, **kwargs)
        self.session_service = SessionService()
    
    def post(self, request):
        """
        Handle POST request for session logout.
        
        Args:
            request: Authenticated HTTP request with session ID to logout
            
        Returns:
            Response: Session logout confirmation
        """
        # Validate request data
        serializer = SessionLogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract session ID from validated data
        session_id = serializer.validated_data['session_id']
        
        # Get the session
        session = self.session_service.get_session(session_id)
        
        # Check if user has permission to manage this session
        if not self.permission_classes[1]().has_object_permission(request, self, session):
            raise AuthenticationException("You do not have permission to manage this session")
        
        # Invalidate the session
        self.session_service.invalidate_session(session)
        
        # Return success response
        return Response(
            {"message": "Session has been logged out"}, 
            status=status.HTTP_200_OK
        )


class SessionLogoutAllView(BaseAPIView):
    """
    API view for logging out all user sessions.
    
    Allows users to terminate all their active sessions at once.
    """
    
    authentication_classes = [Auth0Authentication]
    permission_classes = [IsAuthenticated, CanManageSessions]
    
    def __init__(self, *args, **kwargs):
        """Initialize the session logout all view with session service."""
        super().__init__(*args, **kwargs)
        self.session_service = SessionService()
    
    def post(self, request):
        """
        Handle POST request for logging out all sessions.
        
        Args:
            request: Authenticated HTTP request
            
        Returns:
            Response: All sessions logout confirmation
        """
        # Get user from request
        user = request.user
        
        # Invalidate all user sessions
        count = self.session_service.invalidate_all_user_sessions(user)
        
        # Return success response
        return Response(
            {
                "message": "All sessions have been logged out",
                "count": count
            }, 
            status=status.HTTP_200_OK
        )