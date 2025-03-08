"""
Auth0 integration for the loan management system's authentication framework.

This module provides a client for interacting with Auth0's Management and Authentication APIs,
handling user authentication, token validation, and identity management operations. It also
includes a custom Django REST Framework authentication class for validating Auth0 JWT tokens.
"""

import requests  # requests 2.28+
import jwt  # PyJWT 2.8+
import json  # standard library
import logging  # standard library
from datetime import timedelta  # standard library

from django.conf import settings  # Django 4.2+
from django.utils import timezone  # Django 4.2+
from rest_framework.authentication import BaseAuthentication, get_authorization_header  # DRF 3.14+
from rest_framework.exceptions import AuthenticationFailed  # DRF 3.14+

from .models import Auth0User
from .tokens import validate_jwt_token
from ...core.exceptions import AuthenticationException, ValidationException

# Configure logger
logger = logging.getLogger(__name__)


class Auth0Manager:
    """
    Client for interacting with Auth0 Management and Authentication APIs.

    This class provides methods for authenticating users, validating tokens,
    and managing user identities through Auth0's APIs.
    """

    def __init__(self, domain=None, audience=None, client_id=None, client_secret=None):
        """
        Initialize the Auth0Manager with configuration from Django settings.
        
        Args:
            domain (str, optional): Auth0 domain. Defaults to settings.AUTH0_DOMAIN.
            audience (str, optional): Auth0 API audience. Defaults to settings.AUTH0_API_AUDIENCE.
            client_id (str, optional): Auth0 client ID. Defaults to settings.AUTH0_CLIENT_ID.
            client_secret (str, optional): Auth0 client secret. Defaults to settings.AUTH0_CLIENT_SECRET.
        """
        self.domain = domain or getattr(settings, 'AUTH0_DOMAIN', None)
        self.audience = audience or getattr(settings, 'AUTH0_API_AUDIENCE', None)
        self.client_id = client_id or getattr(settings, 'AUTH0_CLIENT_ID', None)
        self.client_secret = client_secret or getattr(settings, 'AUTH0_CLIENT_SECRET', None)
        
        # Validate required settings
        if not all([self.domain, self.audience, self.client_id, self.client_secret]):
            raise ValueError("Auth0 configuration missing. Check AUTH0_DOMAIN, AUTH0_API_AUDIENCE, AUTH0_CLIENT_ID, and AUTH0_CLIENT_SECRET settings.")
        
        self.management_token = None
        self.token_expiry = None

    def _get_management_token(self):
        """
        Obtains a management API token from Auth0.

        Returns:
            str: Management API token
        """
        # Check if we already have a valid token
        if self.management_token and self.token_expiry and timezone.now() < self.token_expiry:
            return self.management_token

        # Prepare the request payload
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'audience': f'https://{self.domain}/api/v2/',
            'grant_type': 'client_credentials'
        }

        # Make the request to Auth0
        response = requests.post(f'https://{self.domain}/oauth/token', json=payload)

        # Check if the request was successful
        if response.status_code != 200:
            logger.error(f"Failed to get management token: {response.text}")
            raise AuthenticationException("Failed to get Auth0 management token")

        # Extract the token from the response
        token_data = response.json()
        self.management_token = token_data.get('access_token')
        
        # Set token expiry time (subtract 5 minutes for safety margin)
        expires_in = token_data.get('expires_in', 86400)  # Default to 24 hours
        self.token_expiry = timezone.now() + timedelta(seconds=expires_in - 300)

        return self.management_token

    def _make_management_api_request(self, method, endpoint, data=None, params=None):
        """
        Makes an authenticated request to the Auth0 Management API.

        Args:
            method (str): HTTP method to use (GET, POST, PATCH, DELETE)
            endpoint (str): API endpoint path
            data (dict): Request payload data
            params (dict): Query parameters

        Returns:
            dict: API response data
        """
        # Get management token
        token = self._get_management_token()

        # Prepare headers
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        # Build full URL
        url = f'https://{self.domain}/api/v2/{endpoint}'

        # Make the request
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Check if the request was successful
            if response.status_code < 200 or response.status_code >= 300:
                logger.error(f"Auth0 API request failed: {response.text}")
                raise AuthenticationException(f"Auth0 API request failed with status {response.status_code}")

            # Return the response data as JSON
            return response.json() if response.text else {}

        except requests.RequestException as e:
            logger.error(f"Auth0 API request error: {str(e)}")
            raise AuthenticationException(f"Auth0 API request error: {str(e)}")

    def authenticate_user(self, email, password):
        """
        Authenticates a user with email and password against Auth0.

        Args:
            email (str): User's email address
            password (str): User's password

        Returns:
            dict: Authentication result with tokens and user info
        """
        try:
            # Prepare authentication payload
            payload = {
                'username': email,
                'password': password,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'password',
                'scope': 'openid profile email'
            }

            # Make authentication request to Auth0
            response = requests.post(
                f'https://{self.domain}/oauth/token',
                json=payload,
                headers={'Content-Type': 'application/json'}
            )

            # Check if the authentication was successful
            if response.status_code != 200:
                logger.warning(f"Authentication failed for {email}: {response.text}")
                raise AuthenticationException("Authentication failed")

            # Extract tokens from response
            token_data = response.json()
            access_token = token_data.get('access_token')
            id_token = token_data.get('id_token')
            refresh_token = token_data.get('refresh_token')

            # Decode the ID token to get user information
            # Note: We don't validate here as we trust Auth0's response
            id_token_payload = jwt.decode(id_token, options={"verify_signature": False})
            
            # Get user information from token
            auth0_id = id_token_payload.get('sub')
            
            try:
                # Get or create Auth0User in our database
                auth0_user, created = Auth0User.objects.get_or_create(
                    auth0_id=auth0_id,
                    defaults={
                        'email': email,
                        'email_verified': id_token_payload.get('email_verified', False),
                        'auth0_metadata': json.dumps(id_token_payload.get('user_metadata', {}))
                    }
                )
                
                # Update last login timestamp
                auth0_user.update_last_login()
                
                # Return authentication result
                return {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'id_token': id_token,
                    'user': {
                        'id': str(auth0_user.id),
                        'auth0_id': auth0_id,
                        'email': email,
                        'email_verified': auth0_user.email_verified
                    }
                }

            except Exception as e:
                logger.error(f"Error getting/creating Auth0User: {str(e)}")
                raise AuthenticationException("Error processing authenticated user")

        except requests.RequestException as e:
            logger.error(f"Auth0 authentication request error: {str(e)}")
            raise AuthenticationException(f"Authentication request error: {str(e)}")

    def validate_token(self, token):
        """
        Validates an Auth0 JWT token.

        Args:
            token (str): JWT token to validate

        Returns:
            dict: Decoded token payload

        Raises:
            AuthenticationException: If token is invalid or expired
        """
        try:
            # Use the imported validate_jwt_token function from tokens.py
            return validate_jwt_token(token)
        except AuthenticationFailed as e:
            # Convert DRF exception to our custom exception
            raise AuthenticationException(str(e))
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            raise AuthenticationException(f"Token validation error: {str(e)}")

    def get_user_from_token(self, token_payload):
        """
        Gets user information from a validated token.

        Args:
            token_payload (dict): Decoded token payload

        Returns:
            Auth0User: User object corresponding to the token

        Raises:
            AuthenticationException: If user not found
        """
        try:
            # Extract user ID from token payload
            auth0_id = token_payload.get('sub')
            if not auth0_id:
                raise AuthenticationException("Token does not contain user ID (sub claim)")
            
            # Get user from database
            try:
                user = Auth0User.objects.get(auth0_id=auth0_id)
                return user
            except Auth0User.DoesNotExist:
                raise AuthenticationException("User not found in the system")
                
        except Exception as e:
            logger.error(f"Error getting user from token: {str(e)}")
            raise AuthenticationException(f"Error getting user from token: {str(e)}")

    def create_user(self, email, password, user_type, user_metadata=None):
        """
        Creates a new user in Auth0 and local database.

        Args:
            email (str): User's email address
            password (str): User's password
            user_type (str): Type of user (borrower, co-borrower, etc.)
            user_metadata (dict): Additional user metadata

        Returns:
            Auth0User: Created user object
        """
        # Prepare user data
        user_data = {
            'email': email,
            'password': password,
            'connection': 'Username-Password-Authentication',
            'email_verified': False,
            'user_metadata': user_metadata or {}
        }
        
        # Add user_type to metadata
        if 'user_type' not in user_data['user_metadata']:
            user_data['user_metadata']['user_type'] = user_type
        
        try:
            # Create user in Auth0
            auth0_user = self._make_management_api_request('POST', 'users', data=user_data)
            
            # Create user in our database
            auth0_id = auth0_user.get('user_id')
            user = Auth0User.objects.create(
                auth0_id=auth0_id,
                email=email,
                email_verified=auth0_user.get('email_verified', False),
                auth0_metadata=json.dumps(auth0_user.get('user_metadata', {}))
            )
            
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise AuthenticationException(f"Failed to create user: {str(e)}")

    def update_user(self, auth0_user, user_data):
        """
        Updates an existing user in Auth0 and local database.

        Args:
            auth0_user (Auth0User): The user to update
            user_data (dict): User data to update

        Returns:
            Auth0User: Updated user object
        """
        # Prepare update data
        update_data = {}
        
        # Map fields to Auth0 fields
        field_mapping = {
            'email': 'email',
            'email_verified': 'email_verified',
            'user_metadata': 'user_metadata',
            'app_metadata': 'app_metadata',
            'blocked': 'blocked',
            'verify_email': 'verify_email'
        }
        
        # Add fields to update data if present in user_data
        for field, auth0_field in field_mapping.items():
            if field in user_data:
                update_data[auth0_field] = user_data[field]
        
        try:
            # Update user in Auth0
            auth0_id = auth0_user.auth0_id
            self._make_management_api_request('PATCH', f'users/{auth0_id}', data=update_data)
            
            # Update user in our database
            for field, value in user_data.items():
                if hasattr(auth0_user, field):
                    setattr(auth0_user, field, value)
            
            # Special handling for metadata field
            if 'user_metadata' in user_data:
                auth0_user.auth0_metadata = json.dumps(user_data['user_metadata'])
            
            auth0_user.save()
            return auth0_user
            
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise AuthenticationException(f"Failed to update user: {str(e)}")

    def delete_user(self, auth0_user):
        """
        Deletes a user from Auth0 and local database.

        Args:
            auth0_user (Auth0User): The user to delete

        Returns:
            bool: True if deletion was successful
        """
        try:
            # Delete user from Auth0
            auth0_id = auth0_user.auth0_id
            self._make_management_api_request('DELETE', f'users/{auth0_id}')
            
            # Delete user from our database
            auth0_user.delete()
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            raise AuthenticationException(f"Failed to delete user: {str(e)}")

    def enable_mfa(self, auth0_user, mfa_method, verification_contact=None):
        """
        Enables multi-factor authentication for a user in Auth0.

        Args:
            auth0_user (Auth0User): The user to enable MFA for
            mfa_method (str): MFA method to enable (sms, email, authenticator)
            verification_contact (str): Contact info for verification (phone/email)

        Returns:
            dict: MFA enrollment information
        """
        # Validate MFA method
        valid_methods = ['sms', 'email', 'authenticator']
        if mfa_method not in valid_methods:
            raise ValidationException(f"Invalid MFA method. Must be one of: {', '.join(valid_methods)}")
        
        # Prepare enrollment data
        enrollment_data = {
            'user_id': auth0_user.auth0_id,
            'factor_type': mfa_method
        }
        
        # Add phone number for SMS
        if mfa_method == 'sms' and verification_contact:
            enrollment_data['phone_number'] = verification_contact
        
        try:
            # Enable MFA in Auth0
            response = self._make_management_api_request('POST', 'guardian/enrollments', data=enrollment_data)
            
            # Update local MFA tracking - would connect to MFAVerification model
            # Here we would update the MFAVerification model for this user
            try:
                mfa_verification = getattr(auth0_user, 'mfa_verification', None)
                if mfa_verification:
                    mfa_verification.mfa_method = mfa_method
                    mfa_verification.verification_contact = verification_contact
                    mfa_verification.enable()
            except Exception as mfa_ex:
                logger.warning(f"Unable to update local MFA verification status: {str(mfa_ex)}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error enabling MFA: {str(e)}")
            raise AuthenticationException(f"Failed to enable MFA: {str(e)}")

    def verify_mfa(self, auth0_user, mfa_method, code):
        """
        Verifies a multi-factor authentication code.

        Args:
            auth0_user (Auth0User): The user verifying MFA
            mfa_method (str): MFA method being verified
            code (str): Verification code

        Returns:
            bool: True if verification was successful
        """
        # Validate MFA method
        valid_methods = ['sms', 'email', 'authenticator']
        if mfa_method not in valid_methods:
            raise ValidationException(f"Invalid MFA method. Must be one of: {', '.join(valid_methods)}")
        
        # Prepare verification data
        verification_data = {
            'user_id': auth0_user.auth0_id,
            'factor_type': mfa_method,
            'code': code
        }
        
        try:
            # Verify MFA code with Auth0
            response = self._make_management_api_request('POST', 'guardian/verify', data=verification_data)
            
            # Update local MFA verification status
            try:
                mfa_verification = getattr(auth0_user, 'mfa_verification', None)
                if mfa_verification:
                    mfa_verification.update_verification()
            except Exception as mfa_ex:
                logger.warning(f"Unable to update local MFA verification status: {str(mfa_ex)}")
            
            return True
            
        except Exception as e:
            logger.error(f"MFA verification failed: {str(e)}")
            raise AuthenticationException(f"MFA verification failed: {str(e)}")

    def disable_mfa(self, auth0_user, mfa_method):
        """
        Disables multi-factor authentication for a user in Auth0.

        Args:
            auth0_user (Auth0User): The user to disable MFA for
            mfa_method (str): MFA method to disable

        Returns:
            bool: True if MFA was disabled successfully
        """
        # Validate MFA method
        valid_methods = ['sms', 'email', 'authenticator']
        if mfa_method not in valid_methods:
            raise ValidationException(f"Invalid MFA method. Must be one of: {', '.join(valid_methods)}")
        
        try:
            # First get the enrollment ID
            enrollments = self._make_management_api_request('GET', f'guardian/enrollments?user_id={auth0_user.auth0_id}')
            
            # Find the enrollment for the specified method
            enrollment_id = None
            for enrollment in enrollments:
                if enrollment.get('factor_type') == mfa_method:
                    enrollment_id = enrollment.get('id')
                    break
            
            if not enrollment_id:
                raise AuthenticationException(f"No {mfa_method} MFA enrollment found for user")
            
            # Delete the enrollment
            self._make_management_api_request('DELETE', f'guardian/enrollments/{enrollment_id}')
            
            # Update local MFA tracking
            try:
                mfa_verification = getattr(auth0_user, 'mfa_verification', None)
                if mfa_verification and mfa_verification.mfa_method == mfa_method:
                    mfa_verification.disable()
            except Exception as mfa_ex:
                logger.warning(f"Unable to update local MFA verification status: {str(mfa_ex)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error disabling MFA: {str(e)}")
            raise AuthenticationException(f"Failed to disable MFA: {str(e)}")

    def reset_password(self, email):
        """
        Initiates a password reset for a user in Auth0.

        Args:
            email (str): The email address of the user

        Returns:
            bool: True if password reset was initiated successfully
        """
        # Prepare password reset data
        reset_data = {
            'email': email,
            'client_id': self.client_id,
            'connection': 'Username-Password-Authentication'
        }
        
        try:
            # Initiate password reset with Auth0
            response = requests.post(
                f'https://{self.domain}/dbconnections/change_password',
                json=reset_data,
                headers={'Content-Type': 'application/json'}
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                logger.info(f"Password reset initiated for email: {email}")
                return True
            else:
                logger.error(f"Password reset failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error initiating password reset: {str(e)}")
            return False

    def change_password(self, auth0_user, new_password):
        """
        Changes a user's password in Auth0.

        Args:
            auth0_user (Auth0User): The user to change password for
            new_password (str): The new password

        Returns:
            bool: True if password was changed successfully
        """
        # Prepare password change data
        password_data = {
            'password': new_password
        }
        
        try:
            # Update password in Auth0
            auth0_id = auth0_user.auth0_id
            self._make_management_api_request('PATCH', f'users/{auth0_id}', data=password_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            raise AuthenticationException(f"Failed to change password: {str(e)}")

    def get_user_profile(self, auth0_user):
        """
        Gets a user's profile information from Auth0.

        Args:
            auth0_user (Auth0User): The user to get profile for

        Returns:
            dict: User profile information
        """
        try:
            # Get user profile from Auth0
            auth0_id = auth0_user.auth0_id
            user_data = self._make_management_api_request('GET', f'users/{auth0_id}')
            
            # Extract relevant profile information
            profile = {
                'user_id': user_data.get('user_id'),
                'email': user_data.get('email'),
                'email_verified': user_data.get('email_verified', False),
                'created_at': user_data.get('created_at'),
                'updated_at': user_data.get('updated_at'),
                'last_login': user_data.get('last_login'),
                'logins_count': user_data.get('logins_count', 0),
                'user_metadata': user_data.get('user_metadata', {})
            }
            
            return profile
            
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            raise AuthenticationException(f"Failed to get user profile: {str(e)}")


class Auth0Authentication(BaseAuthentication):
    """
    Django REST Framework authentication class for validating Auth0 JWT tokens.

    This class extracts and validates JWT tokens from request headers, retrieving
    the associated user for request authentication.
    """

    def authenticate(self, request):
        """
        Authenticates a request using Auth0 JWT token.

        Args:
            request: HTTP request object

        Returns:
            tuple: Tuple of (user, token) if authentication successful

        Raises:
            AuthenticationFailed: If authentication fails
        """
        # Get authorization header
        auth_header = get_authorization_header(request).split()
        
        # Check if header exists and has Bearer token
        if not auth_header or len(auth_header) != 2 or auth_header[0].lower() != b'bearer':
            return None
        
        # Extract token
        token = auth_header[1].decode('utf-8')
        
        try:
            # Validate token
            auth0_manager = Auth0Manager()
            token_payload = auth0_manager.validate_token(token)
            
            # Get user from token
            user = auth0_manager.get_user_from_token(token_payload)
            
            # Return authenticated user and token
            return (user, token)
            
        except AuthenticationException as e:
            logger.warning(f"Authentication failed: {str(e)}")
            raise AuthenticationFailed(str(e))
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise AuthenticationFailed("Authentication failed")

    def authenticate_header(self, request):
        """
        Returns the authentication scheme used.

        Args:
            request: HTTP request object

        Returns:
            str: Authentication scheme (Bearer)
        """
        return 'Bearer'