"""
Test utilities and fixtures for document management tests.

This module provides common test utilities, fixtures, and helper functions used
across multiple test modules for testing document generation, e-signature 
integration, and document lifecycle management.
"""

import unittest
from unittest import mock
import datetime
import uuid

from ...users.models import User
from ...applications.models import LoanApplication
from ..models import Document, DocumentPackage, SignatureRequest
from ..constants import (
    DOCUMENT_TYPES, DOCUMENT_STATUS, DOCUMENT_PACKAGE_TYPES,
    SIGNATURE_STATUS, SIGNER_TYPES
)


def create_test_user(email, first_name, last_name, user_type):
    """
    Creates a test user with specified attributes for use in tests.
    
    Args:
        email (str): Email for the test user
        first_name (str): First name for the test user
        last_name (str): Last name for the test user
        user_type (str): Type of user (borrower, co_borrower, school_admin, etc.)
        
    Returns:
        User: Created User object
    """
    # In real tests, you would need to properly set up the auth0_user relationship
    # before saving this user to the database
    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        phone="(555) 555-5555",  # Default test phone
        user_type=user_type,
        is_active=True
    )
    # Note: Call user.save() in your test after setting up relationships
    return user


def create_test_application(borrower, co_borrower=None, additional_data=None):
    """
    Creates a test loan application with specified borrower and co-borrower.
    
    Args:
        borrower (User): The primary borrower for the application
        co_borrower (User, optional): The co-borrower for the application
        additional_data (dict, optional): Additional data to set on the application
        
    Returns:
        LoanApplication: Created LoanApplication object
    """
    # In real tests, you would need to properly set up school, program, and other
    # required relationships before saving this application to the database
    application = LoanApplication(
        borrower=borrower,
        co_borrower=co_borrower
    )
    
    # Set additional data if provided
    if additional_data:
        for key, value in additional_data.items():
            setattr(application, key, value)
    
    # Note: Call application.save() in your test after setting up relationships
    return application


def create_test_document_package(application, package_type, status=DOCUMENT_STATUS['DRAFT']):
    """
    Creates a test document package for a loan application.
    
    Args:
        application (LoanApplication): The loan application to associate with the package
        package_type (str): The type of document package
        status (str, optional): The status of the document package
        
    Returns:
        DocumentPackage: Created DocumentPackage object
    """
    # Create a document package with a future expiration date
    expiration_date = datetime.datetime.now() + datetime.timedelta(days=90)
    
    package = DocumentPackage(
        application=application,
        package_type=package_type,
        status=status,
        expiration_date=expiration_date
    )
    # Note: Call package.save() in your test after setting up relationships
    return package


def create_test_document(package, document_type, status=DOCUMENT_STATUS['DRAFT'], generated_by=None):
    """
    Creates a test document with specified attributes.
    
    Args:
        package (DocumentPackage): The document package to associate with the document
        document_type (str): The type of document
        status (str, optional): The status of the document
        generated_by (User, optional): The user who generated the document
        
    Returns:
        Document: Created Document object
    """
    # Generate a test file name and path
    file_name = f"test_{uuid.uuid4().hex[:8]}.pdf"
    file_path = f"test/documents/{file_name}"
    
    document = Document(
        package=package,
        document_type=document_type,
        file_name=file_name,
        file_path=file_path,
        status=status,
        generated_by=generated_by,
        version="1.0"
    )
    # Note: Call document.save() in your test after setting up relationships
    return document


def create_test_signature_request(document, signer, signer_type, status=SIGNATURE_STATUS['PENDING']):
    """
    Creates a test signature request for a document.
    
    Args:
        document (Document): The document requiring signature
        signer (User): The user who should sign the document
        signer_type (str): The type of signer (borrower, co-borrower, etc.)
        status (str, optional): The status of the signature request
        
    Returns:
        SignatureRequest: Created SignatureRequest object
    """
    # Generate a test external reference ID
    external_reference = f"env-{uuid.uuid4().hex[:8]}"
    
    signature_request = SignatureRequest(
        document=document,
        signer=signer,
        signer_type=signer_type,
        status=status,
        external_reference=external_reference
    )
    # Note: Call signature_request.save() in your test after setting up relationships
    return signature_request


def mock_storage_service():
    """
    Creates a mock for the document storage service.
    
    Returns:
        MagicMock: Mock storage service object
    """
    storage_mock = mock.MagicMock()
    
    # Configure common mock methods
    storage_mock.store_document.return_value = {
        'key': 'test/documents/test_file.pdf',
        'file_path': 'test/documents/test_file.pdf',
        'file_name': 'test_file.pdf',
        'version_id': 'test-version-id'
    }
    
    storage_mock.retrieve_document.return_value = (
        b'Test document content',
        'application/pdf',
        {'metadata-key': 'metadata-value'}
    )
    
    storage_mock.get_document_url.return_value = 'https://example.com/test-document-url'
    
    return storage_mock


def mock_docusign_service():
    """
    Creates a mock for the DocuSign integration service.
    
    Returns:
        MagicMock: Mock DocuSign service object
    """
    docusign_mock = mock.MagicMock()
    
    # Configure common mock methods
    docusign_mock.create_signature_request.return_value = {
        'envelope_id': 'test-envelope-id',
        'signing_url': 'https://example.com/sign-document'
    }
    
    docusign_mock.get_signature_status.return_value = {
        'status': SIGNATURE_STATUS['SENT'],
        'delivered': True,
        'signed': False,
        'completed': False
    }
    
    return docusign_mock


class DocumentTestMixin:
    """
    Mixin class providing common setup and utility methods for document tests.
    
    This mixin can be used in test cases to quickly set up a complete test environment
    for document-related tests. In a real test case, you would need to handle database
    setup and teardown appropriately.
    """
    
    def create_test_data(self):
        """
        Creates common test data for document tests.
        
        Returns:
            dict: Dictionary containing created test objects
        """
        # Create test users
        borrower = create_test_user(
            email='borrower1@example.com',
            first_name='John',
            last_name='Doe',
            user_type='borrower'
        )
        
        co_borrower = create_test_user(
            email='coborrower1@example.com',
            first_name='Jane',
            last_name='Doe',
            user_type='co_borrower'
        )
        
        staff_user = create_test_user(
            email='staff1@example.com',
            first_name='Staff',
            last_name='User',
            user_type='underwriter'
        )
        
        # Create test application
        application = create_test_application(
            borrower=borrower,
            co_borrower=co_borrower,
            additional_data={
                'status': 'approved'
            }
        )
        
        # Create test document package
        package = create_test_document_package(
            application=application,
            package_type=DOCUMENT_PACKAGE_TYPES['LOAN_AGREEMENT'],
            status=DOCUMENT_STATUS['DRAFT']
        )
        
        # Create test documents
        loan_agreement = create_test_document(
            package=package,
            document_type=DOCUMENT_TYPES['LOAN_AGREEMENT'],
            status=DOCUMENT_STATUS['GENERATED'],
            generated_by=staff_user
        )
        
        disclosure = create_test_document(
            package=package,
            document_type=DOCUMENT_TYPES['DISCLOSURE_FORM'],
            status=DOCUMENT_STATUS['GENERATED'],
            generated_by=staff_user
        )
        
        # Create test signature requests
        borrower_signature = create_test_signature_request(
            document=loan_agreement,
            signer=borrower,
            signer_type=SIGNER_TYPES['BORROWER'],
            status=SIGNATURE_STATUS['PENDING']
        )
        
        co_borrower_signature = create_test_signature_request(
            document=loan_agreement,
            signer=co_borrower,
            signer_type=SIGNER_TYPES['CO_BORROWER'],
            status=SIGNATURE_STATUS['PENDING']
        )
        
        return {
            'borrower': borrower,
            'co_borrower': co_borrower,
            'staff_user': staff_user,
            'application': application,
            'package': package,
            'loan_agreement': loan_agreement,
            'disclosure': disclosure,
            'borrower_signature': borrower_signature,
            'co_borrower_signature': co_borrower_signature
        }
    
    def setup_mocks(self):
        """
        Sets up common mocks for document tests.
        
        Returns:
            dict: Dictionary containing mock objects
        """
        # Create mocks for various services
        storage_mock = mock_storage_service()
        docusign_mock = mock_docusign_service()
        
        # Mock document generation function
        generate_document_mock = mock.MagicMock()
        generate_document_mock.return_value = {
            'content': b'Test document content',
            'file_name': 'test_document.pdf',
            'file_path': 'test/documents/test_document.pdf'
        }
        
        return {
            'storage_service': storage_mock,
            'docusign_service': docusign_mock,
            'generate_document': generate_document_mock
        }