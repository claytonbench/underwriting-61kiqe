"""
Encryption utility module for the loan management system.

This module provides encryption and decryption utilities for securing sensitive
data such as PII (Personally Identifiable Information) and financial information.
It implements field-level encryption and integrates with AWS KMS for key management.
"""

import base64
import os
from cryptography.fernet import Fernet  # version 39.0.0
import boto3  # version 1.26.0
from django.conf import settings  # version 4.2+

from .constants import SSN_FORMAT, SSN_DISPLAY_FORMAT

# Global encryption key from settings if available
ENCRYPTION_KEY = settings.ENCRYPTION_KEY if hasattr(settings, 'ENCRYPTION_KEY') else None


def generate_key():
    """
    Generates a new Fernet encryption key.
    
    Returns:
        bytes: A new Fernet key for encryption
    """
    return Fernet.generate_key()


def encrypt(value, key=None):
    """
    Encrypts a string value using Fernet symmetric encryption.
    
    Args:
        value (str): The value to encrypt
        key (bytes, optional): The encryption key to use. Defaults to ENCRYPTION_KEY from settings.
    
    Returns:
        str: Base64-encoded encrypted value
    """
    if value is None:
        return None
    
    if key is None:
        key = ENCRYPTION_KEY
        
    if not key:
        raise ValueError("Encryption key not provided and not available in settings")
    
    cipher = Fernet(key)
    encoded_value = value.encode('utf-8')
    encrypted_value = cipher.encrypt(encoded_value)
    return encrypted_value.decode('utf-8')


def decrypt(encrypted_value, key=None):
    """
    Decrypts an encrypted string value using Fernet symmetric encryption.
    
    Args:
        encrypted_value (str): The encrypted value to decrypt
        key (bytes, optional): The encryption key to use. Defaults to ENCRYPTION_KEY from settings.
    
    Returns:
        str: Decrypted string value
    """
    if encrypted_value is None:
        return None
    
    if key is None:
        key = ENCRYPTION_KEY
        
    if not key:
        raise ValueError("Encryption key not provided and not available in settings")
    
    cipher = Fernet(key)
    encoded_value = encrypted_value.encode('utf-8')
    decrypted_value = cipher.decrypt(encoded_value)
    return decrypted_value.decode('utf-8')


def encrypt_ssn(ssn, key=None):
    """
    Encrypts a Social Security Number with special formatting handling.
    
    Args:
        ssn (str): The SSN to encrypt, can be with or without hyphens
        key (bytes, optional): The encryption key to use
    
    Returns:
        str: Encrypted SSN value
    """
    if ssn is None:
        return None
    
    # Normalize the SSN by removing hyphens
    normalized_ssn = ssn.replace('-', '')
    
    # Encrypt the normalized SSN
    return encrypt(normalized_ssn, key)


def decrypt_ssn(encrypted_ssn, key=None):
    """
    Decrypts an encrypted Social Security Number and formats it with hyphens.
    
    Args:
        encrypted_ssn (str): The encrypted SSN to decrypt
        key (bytes, optional): The encryption key to use
    
    Returns:
        str: Decrypted SSN with proper formatting (XXX-XX-XXXX)
    """
    if encrypted_ssn is None:
        return None
    
    # Decrypt the SSN
    decrypted_ssn = decrypt(encrypted_ssn, key)
    
    # Format the SSN with hyphens
    if len(decrypted_ssn) == 9:
        return f"{decrypted_ssn[:3]}-{decrypted_ssn[3:5]}-{decrypted_ssn[5:]}"
    
    return decrypted_ssn


def mask_ssn(ssn):
    """
    Masks a Social Security Number to show only the last 4 digits.
    
    Args:
        ssn (str): The SSN to mask, can be with or without hyphens
    
    Returns:
        str: Masked SSN in format XXX-XX-1234
    """
    if ssn is None:
        return None
    
    # Normalize the SSN by removing hyphens
    normalized_ssn = ssn.replace('-', '')
    
    if len(normalized_ssn) != 9:
        return ssn  # Return original if not a valid SSN
    
    # Get the last 4 digits
    last_four = normalized_ssn[-4:]
    
    # Return the masked SSN
    return f"XXX-XX-{last_four}"


def encrypt_field(value, field_type, key=None):
    """
    Generic function to encrypt sensitive field values with type-specific handling.
    
    Args:
        value (str): The value to encrypt
        field_type (str): The type of field (e.g., 'ssn', 'generic')
        key (bytes, optional): The encryption key to use
    
    Returns:
        str: Encrypted field value
    """
    if value is None:
        return None
    
    if field_type == 'ssn':
        return encrypt_ssn(value, key)
    
    # Default to generic encryption
    return encrypt(value, key)


def decrypt_field(encrypted_value, field_type, key=None):
    """
    Generic function to decrypt sensitive field values with type-specific handling.
    
    Args:
        encrypted_value (str): The encrypted value to decrypt
        field_type (str): The type of field (e.g., 'ssn', 'generic')
        key (bytes, optional): The encryption key to use
    
    Returns:
        str: Decrypted field value
    """
    if encrypted_value is None:
        return None
    
    if field_type == 'ssn':
        return decrypt_ssn(encrypted_value, key)
    
    # Default to generic decryption
    return decrypt(encrypted_value, key)


def encrypt_with_kms(plaintext, key_id=None):
    """
    Encrypts data using AWS KMS for enhanced security.
    
    Args:
        plaintext (str): The plaintext to encrypt
        key_id (str, optional): The KMS key ID to use. Defaults to AWS_KMS_KEY_ID from settings.
    
    Returns:
        str: Base64-encoded encrypted data
    """
    if plaintext is None:
        return None
    
    if key_id is None:
        key_id = getattr(settings, 'AWS_KMS_KEY_ID', None)
        
    if not key_id:
        raise ValueError("KMS key ID not provided and not available in settings")
    
    # Create KMS client
    kms = boto3.client('kms')
    
    # Encrypt the data
    response = kms.encrypt(
        KeyId=key_id,
        Plaintext=plaintext.encode('utf-8')
    )
    
    # Encode the encrypted data as base64
    encrypted_data = base64.b64encode(response['CiphertextBlob']).decode('utf-8')
    
    return encrypted_data


def decrypt_with_kms(ciphertext):
    """
    Decrypts data that was encrypted using AWS KMS.
    
    Args:
        ciphertext (str): Base64-encoded encrypted data
    
    Returns:
        str: Decrypted plaintext
    """
    if ciphertext is None:
        return None
    
    # Decode the base64-encoded ciphertext
    decoded_ciphertext = base64.b64decode(ciphertext.encode('utf-8'))
    
    # Create KMS client
    kms = boto3.client('kms')
    
    # Decrypt the data
    response = kms.decrypt(
        CiphertextBlob=decoded_ciphertext
    )
    
    # Return the decrypted plaintext
    return response['Plaintext'].decode('utf-8')


class EncryptedField:
    """
    Descriptor class for handling encrypted field values in model classes.
    
    This class can be used to declare encrypted fields in model classes,
    automatically handling encryption and decryption when getting or setting values.
    
    Example:
        class User:
            ssn = EncryptedField('ssn')
            
            def __init__(self, ssn=None):
                self._ssn = None
                self.ssn = ssn
    """
    
    def __init__(self, field_type):
        """
        Initialize the EncryptedField descriptor.
        
        Args:
            field_type (str): The type of field (e.g., 'ssn', 'generic')
        """
        self.field_type = field_type
        self.name = None
    
    def __set_name__(self, owner, name):
        """
        Sets the descriptor name when the class is created.
        
        Args:
            owner (object): The owning class
            name (str): The attribute name
        """
        self.name = name
    
    def __get__(self, instance, owner):
        """
        Retrieves and decrypts the field value when accessed.
        
        Args:
            instance (object): The instance accessing the attribute
            owner (object): The owning class
        
        Returns:
            str: Decrypted field value
        """
        if instance is None:
            return self
        
        encrypted_value = instance.__dict__.get(f"_{self.name}")
        if encrypted_value is None:
            return None
        
        return decrypt_field(encrypted_value, self.field_type)
    
    def __set__(self, instance, value):
        """
        Encrypts and stores the field value when assigned.
        
        Args:
            instance (object): The instance the attribute is being set on
            value (str): The value to encrypt and store
        """
        if value is None:
            instance.__dict__[f"_{self.name}"] = None
        else:
            encrypted_value = encrypt_field(value, self.field_type)
            instance.__dict__[f"_{self.name}"] = encrypted_value