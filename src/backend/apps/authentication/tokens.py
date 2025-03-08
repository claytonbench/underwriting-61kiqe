"""
JWT token management for the loan management system.

This module provides utilities for creating, validating, and managing JWT tokens
for authentication, refresh tokens, and password reset tokens used throughout
the loan management system.

The tokens implement security best practices including:
- Token expiration
- Token type designation
- Unique token identifiers
- Optional encryption for sensitive data
"""

import jwt  # PyJWT 2.8+
from datetime import datetime, timedelta
import uuid
from django.conf import settings  # Django 4.2+
from rest_framework.exceptions import AuthenticationFailed  # DRF 3.14+

from ...utils.constants import (
    JWT_EXPIRATION_HOURS,
    REFRESH_TOKEN_EXPIRATION_DAYS,
    PASSWORD_RESET_EXPIRATION_HOURS
)
from ...utils.encryption import encrypt, decrypt

# Global constants
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = "HS256"

def generate_jwt_token(payload):
    """
    Generates a JWT access token for a user.
    
    The token includes:
    - Original payload data (typically user ID and roles)
    - Issued at timestamp (iat)
    - Expiration timestamp (exp)
    - Unique token ID (jti)
    
    Args:
        payload (dict): The payload to include in the token
        
    Returns:
        str: JWT token string
    """
    # Add issued at time
    payload['iat'] = datetime.utcnow().timestamp()
    
    # Add expiration time
    exp_time = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload['exp'] = exp_time.timestamp()
    
    # Add unique token ID
    payload['jti'] = str(uuid.uuid4())
    
    # Generate and return token
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def validate_jwt_token(token):
    """
    Validates a JWT token and returns the decoded payload.
    
    This function:
    - Decodes the JWT token
    - Verifies the signature
    - Checks if the token has expired
    
    Args:
        token (str): The JWT token to validate
        
    Returns:
        dict: Decoded token payload
        
    Raises:
        AuthenticationFailed: If token is invalid or expired
    """
    try:
        # Decode the token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Check if token has expired
        if is_token_expired(payload):
            raise AuthenticationFailed('Token has expired')
            
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token has expired')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token')

def generate_refresh_token(user_id):
    """
    Generates a refresh token for obtaining new access tokens.
    
    The refresh token:
    - Has a longer expiration time than access tokens
    - Contains the user ID
    - Is specifically designated as a refresh token
    - Includes a unique token ID
    
    Args:
        user_id (str): The ID of the user
        
    Returns:
        str: Refresh token string
    """
    payload = {
        'user_id': user_id,
        'token_type': 'refresh',
        'iat': datetime.utcnow().timestamp()
    }
    
    # Add expiration time
    exp_time = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRATION_DAYS)
    payload['exp'] = exp_time.timestamp()
    
    # Add unique token ID
    payload['jti'] = str(uuid.uuid4())
    
    # Generate and return token
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def validate_refresh_token(token):
    """
    Validates a refresh token and returns the decoded payload.
    
    This function:
    - Decodes the refresh token
    - Verifies the signature
    - Checks if the token has expired
    - Confirms the token is specifically a refresh token
    
    Args:
        token (str): The refresh token to validate
        
    Returns:
        dict: Decoded token payload
        
    Raises:
        AuthenticationFailed: If token is invalid, expired or not a refresh token
    """
    try:
        # Decode the token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Check if token has expired
        if is_token_expired(payload):
            raise AuthenticationFailed('Refresh token has expired')
            
        # Check if it's a refresh token
        if payload.get('token_type') != 'refresh':
            raise AuthenticationFailed('Not a valid refresh token')
            
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Refresh token has expired')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid refresh token')

def generate_password_reset_token(user_id):
    """
    Generates a password reset token.
    
    The password reset token:
    - Contains the user ID
    - Is specifically designated as a password reset token
    - Has a shorter expiration time (typically 24 hours)
    - Includes a unique token ID
    
    Args:
        user_id (str): The ID of the user
        
    Returns:
        str: Password reset token string
    """
    payload = {
        'user_id': user_id,
        'token_type': 'password_reset',
        'iat': datetime.utcnow().timestamp()
    }
    
    # Add expiration time
    exp_time = datetime.utcnow() + timedelta(hours=PASSWORD_RESET_EXPIRATION_HOURS)
    payload['exp'] = exp_time.timestamp()
    
    # Add unique token ID
    payload['jti'] = str(uuid.uuid4())
    
    # Generate and return token
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def validate_password_reset_token(token):
    """
    Validates a password reset token and returns the decoded payload.
    
    This function:
    - Decodes the password reset token
    - Verifies the signature
    - Checks if the token has expired
    - Confirms the token is specifically a password reset token
    
    Args:
        token (str): The password reset token to validate
        
    Returns:
        dict: Decoded token payload
        
    Raises:
        AuthenticationFailed: If token is invalid, expired or not a password reset token
    """
    try:
        # Decode the token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Check if token has expired
        if is_token_expired(payload):
            raise AuthenticationFailed('Password reset token has expired')
            
        # Check if it's a password reset token
        if payload.get('token_type') != 'password_reset':
            raise AuthenticationFailed('Not a valid password reset token')
            
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Password reset token has expired')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid password reset token')

def get_token_expiration(hours):
    """
    Calculates token expiration datetime based on hours from now.
    
    Args:
        hours (int): Number of hours until token expires
        
    Returns:
        datetime: Expiration datetime
    """
    return datetime.utcnow() + timedelta(hours=hours)

def get_token_remaining_time(payload):
    """
    Calculates remaining time for a token in seconds.
    
    Args:
        payload (dict): The token payload containing expiration time
        
    Returns:
        int: Remaining seconds until expiration
    """
    exp_timestamp = payload.get('exp')
    if not exp_timestamp:
        return 0
        
    exp_datetime = datetime.fromtimestamp(exp_timestamp)
    current_datetime = datetime.utcnow()
    
    # Calculate time difference in seconds
    time_diff = (exp_datetime - current_datetime).total_seconds()
    
    # Return 0 if expired
    return max(0, time_diff)

def is_token_expired(payload):
    """
    Checks if a token is expired based on its payload.
    
    Args:
        payload (dict): The token payload containing expiration time
        
    Returns:
        bool: True if token is expired, False otherwise
    """
    exp_timestamp = payload.get('exp')
    if not exp_timestamp:
        return True
        
    current_timestamp = datetime.utcnow().timestamp()
    return current_timestamp > exp_timestamp

def encrypt_token_data(data):
    """
    Encrypts sensitive token data for additional security.
    
    This function can be used to add an extra layer of encryption
    beyond the JWT signature for highly sensitive data.
    
    Args:
        data (dict): Data to encrypt
        
    Returns:
        str: Encrypted data string
    """
    import json
    json_data = json.dumps(data)
    return encrypt(json_data)

def decrypt_token_data(encrypted_data):
    """
    Decrypts token data that was encrypted.
    
    Args:
        encrypted_data (str): Encrypted data to decrypt
        
    Returns:
        dict: Decrypted data dictionary
    """
    import json
    decrypted_json = decrypt(encrypted_data)
    return json.loads(decrypted_json)