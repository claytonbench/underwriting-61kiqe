"""
Unit tests for the encryption utility module.

This module tests the encryption and decryption functionality used to protect sensitive
data throughout the loan management system, including PII and financial information.
"""

import unittest
from unittest.mock import patch, MagicMock
import base64

from ../../utils.encryption import (
    generate_key,
    encrypt,
    decrypt,
    encrypt_ssn,
    decrypt_ssn,
    mask_ssn,
    encrypt_field,
    decrypt_field,
    encrypt_with_kms,
    decrypt_with_kms,
    EncryptedField
)
from ../../utils.constants import SSN_FORMAT, SSN_DISPLAY_FORMAT


class TestEncryption(unittest.TestCase):
    """Test case class for testing the encryption utility functions."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Generate a test encryption key
        self.test_key = generate_key()
        # Set up test data
        self.test_text = "This is a secret message"
        self.test_ssn = "123456789"
        self.test_ssn_formatted = "123-45-6789"
    
    def test_generate_key(self):
        """Test that generate_key produces a valid Fernet key."""
        key = generate_key()
        
        # Verify it's a bytes object
        self.assertIsInstance(key, bytes)
        
        # Verify it's the correct length for a Fernet key (44 bytes when encoded in URL-safe base64)
        self.assertEqual(len(key), 44)
        
        # Verify it's URL-safe base64 encoded by checking for valid characters
        try:
            decoded = base64.urlsafe_b64decode(key)
            # The decoded key should be 32 bytes (256 bits)
            self.assertEqual(len(decoded), 32)
        except Exception as e:
            self.fail(f"Key is not a valid URL-safe base64 encoded string: {e}")
    
    def test_encrypt_decrypt(self):
        """Test the encrypt and decrypt functions work correctly together."""
        # Encrypt the test text
        encrypted = encrypt(self.test_text, self.test_key)
        
        # Verify the encrypted value is different from the original
        self.assertNotEqual(encrypted, self.test_text)
        
        # Decrypt the encrypted value
        decrypted = decrypt(encrypted, self.test_key)
        
        # Verify the decrypted value matches the original
        self.assertEqual(decrypted, self.test_text)
    
    def test_encrypt_decrypt_none_value(self):
        """Test that encrypt and decrypt handle None values correctly."""
        # Encrypt None value
        encrypted = encrypt(None, self.test_key)
        
        # Verify the result is None
        self.assertIsNone(encrypted)
        
        # Decrypt None value
        decrypted = decrypt(None, self.test_key)
        
        # Verify the result is None
        self.assertIsNone(decrypted)
    
    def test_encrypt_ssn_decrypt_ssn(self):
        """Test SSN-specific encryption and decryption."""
        # Encrypt the SSN
        encrypted_ssn = encrypt_ssn(self.test_ssn, self.test_key)
        
        # Verify the encrypted value is different from the original
        self.assertNotEqual(encrypted_ssn, self.test_ssn)
        
        # Decrypt the encrypted SSN
        decrypted_ssn = decrypt_ssn(encrypted_ssn, self.test_key)
        
        # Verify the decrypted value matches the original with proper formatting
        self.assertEqual(decrypted_ssn, self.test_ssn_formatted)
    
    def test_encrypt_ssn_with_hyphens(self):
        """Test that encrypt_ssn handles SSNs with hyphens correctly."""
        # Create an SSN with hyphens
        ssn_with_hyphens = "123-45-6789"
        
        # Encrypt the SSN with hyphens
        encrypted_ssn = encrypt_ssn(ssn_with_hyphens, self.test_key)
        
        # Decrypt the encrypted SSN
        decrypted_ssn = decrypt_ssn(encrypted_ssn, self.test_key)
        
        # Verify the decrypted value has the correct format with hyphens
        self.assertEqual(decrypted_ssn, "123-45-6789")
    
    def test_mask_ssn(self):
        """Test the SSN masking functionality."""
        # Mask the SSN
        masked_ssn = mask_ssn(self.test_ssn)
        
        # Verify the masked SSN format is correct
        self.assertEqual(masked_ssn, "XXX-XX-6789")
        
        # Verify only the last 4 digits are visible
        self.assertTrue(masked_ssn.startswith("XXX-XX-"))
        self.assertTrue(masked_ssn.endswith("6789"))
    
    def test_mask_ssn_with_hyphens(self):
        """Test that mask_ssn handles SSNs with hyphens correctly."""
        # Create an SSN with hyphens
        ssn_with_hyphens = "123-45-6789"
        
        # Mask the SSN with hyphens
        masked_ssn = mask_ssn(ssn_with_hyphens)
        
        # Verify the masked SSN format is correct
        self.assertEqual(masked_ssn, "XXX-XX-6789")
        
        # Verify only the last 4 digits are visible
        self.assertTrue(masked_ssn.startswith("XXX-XX-"))
        self.assertTrue(masked_ssn.endswith("6789"))
    
    def test_mask_ssn_none_value(self):
        """Test that mask_ssn handles None values correctly."""
        # Mask None value
        masked_ssn = mask_ssn(None)
        
        # Verify the result is None
        self.assertIsNone(masked_ssn)
    
    def test_encrypt_field_decrypt_field(self):
        """Test generic field encryption and decryption."""
        # Encrypt a generic field
        encrypted_field = encrypt_field(self.test_text, "generic", self.test_key)
        
        # Verify the encrypted value is different from the original
        self.assertNotEqual(encrypted_field, self.test_text)
        
        # Decrypt the encrypted field
        decrypted_field = decrypt_field(encrypted_field, "generic", self.test_key)
        
        # Verify the decrypted value matches the original
        self.assertEqual(decrypted_field, self.test_text)
    
    def test_encrypt_field_decrypt_field_ssn(self):
        """Test field encryption and decryption with SSN field type."""
        # Encrypt an SSN field
        encrypted_field = encrypt_field(self.test_ssn, "ssn", self.test_key)
        
        # Verify the encrypted value is different from the original
        self.assertNotEqual(encrypted_field, self.test_ssn)
        
        # Decrypt the encrypted field
        decrypted_field = decrypt_field(encrypted_field, "ssn", self.test_key)
        
        # Verify the decrypted value matches the original with proper formatting
        self.assertEqual(decrypted_field, self.test_ssn_formatted)
    
    def test_encrypt_field_decrypt_field_none_value(self):
        """Test that encrypt_field and decrypt_field handle None values correctly."""
        # Encrypt None value
        encrypted_field = encrypt_field(None, "generic", self.test_key)
        
        # Verify the result is None
        self.assertIsNone(encrypted_field)
        
        # Decrypt None value
        decrypted_field = decrypt_field(None, "generic", self.test_key)
        
        # Verify the result is None
        self.assertIsNone(decrypted_field)
    
    def test_encrypted_field_descriptor(self):
        """Test the EncryptedField descriptor class."""
        # Create a test instance
        test_model = TestModelWithEncryptedFields()
        
        # Test setting values
        test_model.ssn_field = "123456789"
        test_model.generic_field = "Secret value"
        
        # Verify values are encrypted in instance __dict__
        self.assertNotEqual(test_model._ssn_field, "123456789")
        self.assertNotEqual(test_model._generic_field, "Secret value")
        
        # Verify accessing attributes returns decrypted values
        self.assertEqual(test_model.ssn_field, "123-45-6789")
        self.assertEqual(test_model.generic_field, "Secret value")
        
        # Test setting None values
        test_model.ssn_field = None
        test_model.generic_field = None
        
        # Verify None values are stored as None
        self.assertIsNone(test_model._ssn_field)
        self.assertIsNone(test_model._generic_field)
        
        # Verify accessing attributes returns None
        self.assertIsNone(test_model.ssn_field)
        self.assertIsNone(test_model.generic_field)
    
    @patch('boto3.client')
    def test_kms_encryption_decryption(self, mock_boto3_client):
        """Test AWS KMS encryption and decryption."""
        # Set up mock KMS client
        mock_kms = MagicMock()
        mock_boto3_client.return_value = mock_kms
        
        # Set up mock encrypt response
        mock_encrypt_response = {
            'CiphertextBlob': b'encrypted-data'
        }
        mock_kms.encrypt.return_value = mock_encrypt_response
        
        # Set up mock decrypt response
        mock_decrypt_response = {
            'Plaintext': self.test_text.encode('utf-8')
        }
        mock_kms.decrypt.return_value = mock_decrypt_response
        
        # Test encryption with KMS
        encrypted_data = encrypt_with_kms(self.test_text, "test-key-id")
        
        # Verify KMS client was called correctly
        mock_boto3_client.assert_called_with('kms')
        mock_kms.encrypt.assert_called_with(
            KeyId="test-key-id",
            Plaintext=self.test_text.encode('utf-8')
        )
        
        # Test decryption with KMS
        decrypted_data = decrypt_with_kms(encrypted_data)
        
        # Verify KMS client was called correctly for decryption
        mock_kms.decrypt.assert_called_with(
            CiphertextBlob=b'encrypted-data'
        )
        
        # Verify the decrypted value matches the original
        self.assertEqual(decrypted_data, self.test_text)
    
    @patch('boto3.client')
    def test_kms_encryption_decryption_none_value(self, mock_boto3_client):
        """Test that KMS encryption and decryption handle None values correctly."""
        # Set up mock KMS client
        mock_kms = MagicMock()
        mock_boto3_client.return_value = mock_kms
        
        # Test encryption with None value
        encrypted_data = encrypt_with_kms(None, "test-key-id")
        
        # Verify the result is None
        self.assertIsNone(encrypted_data)
        
        # Verify KMS client was not called
        mock_kms.encrypt.assert_not_called()
        
        # Test decryption with None value
        decrypted_data = decrypt_with_kms(None)
        
        # Verify the result is None
        self.assertIsNone(decrypted_data)
        
        # Verify KMS client was not called
        mock_kms.decrypt.assert_not_called()


class TestModelWithEncryptedFields:
    """Test class that uses EncryptedField descriptors for testing."""
    
    ssn_field = EncryptedField('ssn')
    generic_field = EncryptedField('generic')
    
    def __init__(self):
        """Initialize the test model."""
        self._ssn_field = None
        self._generic_field = None