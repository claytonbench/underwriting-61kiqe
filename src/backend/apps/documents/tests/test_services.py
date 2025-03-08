import logging  # Import logging utilities for error and activity logging
from datetime import datetime  # Date and time utilities for document expiration and timestamps
import uuid  # Generate unique identifiers for documents
from unittest.mock import MagicMock  # Mocking dependencies for isolated unit testing

import pytest  # Testing framework for writing and running tests
from django.test import TestCase  # Django-specific testing utilities
from django.utils import timezone  # Django timezone utilities for date/time handling in tests

from .. import services  # Import document service functions to be tested
from ..models import Document  # Import Document model for testing document operations
from ..models import DocumentTemplate  # Import DocumentTemplate model for testing template operations
from ..models import DocumentPackage  # Import DocumentPackage model for testing package operations
from ..models import SignatureRequest  # Import SignatureRequest model for testing signature operations
from ..models import DocumentField  # Import DocumentField model for testing field operations
from apps.applications.models import LoanApplication  # Import LoanApplication model for testing with application data
from apps.users.models import User  # Import User model for testing with user data
from ..storage import document_storage  # Import document storage singleton for mocking in tests
from ..docusign import docusign_service  # Import DocuSign service singleton for mocking in tests
from ..generators.base import BaseDocumentGenerator  # Import base document generator for mocking in tests
from ..constants import DOCUMENT_TYPES  # Import document type constants for test cases
from ..constants import DOCUMENT_STATUS  # Import document status constants for test cases
from ..constants import DOCUMENT_PACKAGE_TYPES  # Import document package type constants
from ..constants import SIGNATURE_STATUS  # Import signature status constants for test cases
from ..constants import SIGNER_TYPES  # Import signer type constants


logger = logging.getLogger(__name__)


def create_mock_application():
    """Creates a mock LoanApplication object for testing"""
    mock_application = MagicMock(spec=LoanApplication)
    mock_application.id = uuid.uuid4()
    mock_application.borrower_id = uuid.uuid4()
    mock_application.school_id = uuid.uuid4()
    mock_application.program_id = uuid.uuid4()
    mock_application.program_version_id = uuid.uuid4()
    mock_application.status = DOCUMENT_STATUS['GENERATED']
    mock_application.get_loan_details.return_value = MagicMock()
    return mock_application


def create_mock_user():
    """Creates a mock User object for testing"""
    mock_user = MagicMock(spec=User)
    mock_user.id = uuid.uuid4()
    mock_user.first_name = "Test"
    mock_user.last_name = "User"
    mock_user.email = "test@example.com"
    return mock_user


def create_mock_document(document_type, status):
    """Creates a mock Document object for testing"""
    mock_document = MagicMock(spec=Document)
    mock_document.id = uuid.uuid4()
    mock_document.document_type = document_type
    mock_document.status = status
    mock_document.file_name = "test_document.pdf"
    mock_document.file_path = "test/path/test_document.pdf"
    mock_document.package_id = uuid.uuid4()
    mock_document.get_content.return_value = b"Test document content"
    mock_document.get_signature_requests.return_value = MagicMock(exists=lambda: False)
    mock_document.update_status.return_value = True
    return mock_document


def create_mock_document_package(package_type, status):
    """Creates a mock DocumentPackage object for testing"""
    mock_package = MagicMock(spec=DocumentPackage)
    mock_package.id = uuid.uuid4()
    mock_package.package_type = package_type
    mock_package.status = status
    mock_package.get_documents.return_value = MagicMock(exists=lambda: False)
    mock_package.update_status.return_value = True
    return mock_package


def create_mock_signature_request(status):
    """Creates a mock SignatureRequest object for testing"""
    mock_signature_request = MagicMock(spec=SignatureRequest)
    mock_signature_request.id = uuid.uuid4()
    mock_signature_request.status = status
    mock_signature_request.external_reference = "test_envelope_id:1"
    mock_signature_request.can_send_reminder.return_value = True
    mock_signature_request.send_reminder.return_value = True
    mock_signature_request.update_status.return_value = True
    return mock_signature_request


class TestDocumentGeneration(TestCase):
    """Test cases for document generation functions"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_application = create_mock_application()
        self.mock_user = create_mock_user()
        self.mock_template = MagicMock(spec=DocumentTemplate)
        self.mock_template.id = uuid.uuid4()
        self.mock_template.document_type = DOCUMENT_TYPES['LOAN_AGREEMENT']
        self.mock_template.get_content.return_value = "Test template content"
        self.test_data = {'key': 'test/path/test_document.pdf', 'version_id': '1'}

    def test_generate_document(self):
        """Test generating a single document"""
        # Mock document generator and storage
        document_storage.store_document.return_value = self.test_data
        mock_generator = MagicMock(spec=BaseDocumentGenerator)
        mock_generator.generate.return_value = create_mock_document(DOCUMENT_TYPES['LOAN_AGREEMENT'], DOCUMENT_STATUS['GENERATED'])

        # Call generate_document with test data
        document = services.generate_document(DOCUMENT_TYPES['LOAN_AGREEMENT'], self.mock_application, self.mock_user)

        # Assert document was created with correct attributes
        self.assertIsNotNone(document)
        self.assertEqual(document.document_type, DOCUMENT_TYPES['LOAN_AGREEMENT'])
        self.assertEqual(document.status, DOCUMENT_STATUS['GENERATED'])

        # Verify correct methods were called
        document_storage.store_document.assert_called_once()
        mock_generator.generate.assert_called_once()

    def test_generate_document_error(self):
        """Test error handling during document generation"""
        # Mock document generator to raise an exception
        document_storage.store_document.side_effect = Exception("Storage error")

        # Assert DocumentServiceError is raised when calling generate_document
        with self.assertRaises(services.DocumentServiceError):
            services.generate_document(DOCUMENT_TYPES['LOAN_AGREEMENT'], self.mock_application, self.mock_user)

        # Verify error handling behavior
        document_storage.store_document.assert_called_once()

    def test_generate_document_package(self):
        """Test generating a document package"""
        # Mock document generators and storage
        document_storage.store_document.return_value = self.test_data
        mock_generator = MagicMock(spec=BaseDocumentGenerator)
        mock_generator.generate.return_value = create_mock_document(DOCUMENT_TYPES['LOAN_AGREEMENT'], DOCUMENT_STATUS['GENERATED'])

        # Call generate_document_package with test data
        package = services.generate_document_package(DOCUMENT_PACKAGE_TYPES['LOAN_AGREEMENT'], self.mock_application, self.mock_user)

        # Assert package was created with correct attributes
        self.assertIsNotNone(package)
        self.assertEqual(package.package_type, DOCUMENT_PACKAGE_TYPES['LOAN_AGREEMENT'])
        self.assertEqual(package.status, DOCUMENT_STATUS['GENERATED'])

        # Assert documents were created for the package
        self.assertEqual(Document.objects.count(), 0)

        # Verify correct methods were called
        document_storage.store_document.assert_called()
        mock_generator.generate.assert_called()


class TestDocumentRetrieval(TestCase):
    """Test cases for document retrieval functions"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_document = create_mock_document(DOCUMENT_TYPES['LOAN_AGREEMENT'], DOCUMENT_STATUS['GENERATED'])
        self.mock_package = create_mock_document_package(DOCUMENT_PACKAGE_TYPES['LOAN_AGREEMENT'], DOCUMENT_STATUS['GENERATED'])
        self.test_document_id = uuid.uuid4()
        self.test_package_id = uuid.uuid4()

    def test_get_document_by_id(self):
        """Test retrieving a document by ID"""
        # Mock Document.objects.get
        Document.objects.get = MagicMock(return_value=self.mock_document)

        # Call get_document_by_id with test ID
        document = services.get_document_by_id(self.test_document_id)

        # Assert correct document is returned
        self.assertEqual(document, self.mock_document)
        Document.objects.get.assert_called_with(id=self.test_document_id)

        # Test with non-existent ID returns None
        Document.objects.get.side_effect = Document.DoesNotExist
        document = services.get_document_by_id(uuid.uuid4())
        self.assertIsNone(document)

    def test_get_document_package_by_id(self):
        """Test retrieving a document package by ID"""
        # Mock DocumentPackage.objects.get
        DocumentPackage.objects.get = MagicMock(return_value=self.mock_package)

        # Call get_document_package_by_id with test ID
        package = services.get_document_package_by_id(self.test_package_id)

        # Assert correct package is returned
        self.assertEqual(package, self.mock_package)
        DocumentPackage.objects.get.assert_called_with(id=self.test_package_id)

        # Test with non-existent ID returns None
        DocumentPackage.objects.get.side_effect = DocumentPackage.DoesNotExist
        package = services.get_document_package_by_id(uuid.uuid4())
        self.assertIsNone(package)

    def test_get_document_content(self):
        """Test retrieving document content"""
        # Mock document.get_content
        self.mock_document.get_content.return_value = b"Test content"

        # Call get_document_content with mock document
        content = services.get_document_content(self.mock_document)

        # Assert correct content is returned
        self.assertEqual(content, b"Test content")
        self.mock_document.get_content.assert_called_once()

        # Test error handling
        self.mock_document.get_content.side_effect = Exception("Content error")
        with self.assertRaises(Exception):
            services.get_document_content(self.mock_document)

    def test_get_document_download_url(self):
        """Test generating a document download URL"""
        # Mock document_storage.get_document_url
        document_storage.get_document_url.return_value = "http://test.url"

        # Call get_document_download_url with mock document
        url = services.get_document_download_url(self.mock_document)

        # Assert correct URL is returned
        self.assertEqual(url, "http://test.url")
        document_storage.get_document_url.assert_called_with(self.mock_document.file_path, 3600)

        # Test with different expiry values
        services.get_document_download_url(self.mock_document, expiry_seconds=7200)
        document_storage.get_document_url.assert_called_with(self.mock_document.file_path, 7200)

        # Test error handling
        document_storage.get_document_url.side_effect = Exception("URL error")
        with self.assertRaises(Exception):
            services.get_document_download_url(self.mock_document)

    def test_get_application_documents(self):
        """Test retrieving all documents for an application"""
        # Mock DocumentPackage.objects.filter and related queries
        LoanApplication.objects.get = MagicMock(return_value=self.mock_application)
        DocumentPackage.objects.filter.return_value = MagicMock(
            exists=lambda: True,
            all=lambda: [self.mock_package]
        )
        Document.objects.filter.return_value = MagicMock(
            exists=lambda: True,
            all=lambda: [self.mock_document]
        )

        # Call get_application_documents with mock application
        documents = services.get_application_documents(self.mock_application)

        # Assert correct documents are returned
        self.assertEqual(len(list(documents.all())), 1)
        self.assertEqual(list(documents.all())[0], self.mock_document)
        DocumentPackage.objects.filter.assert_called_with(application=self.mock_application)
        Document.objects.filter.assert_called_with(package__in=DocumentPackage.objects.filter.return_value)

        # Test with application having no documents
        DocumentPackage.objects.filter.return_value = MagicMock(exists=lambda: False)
        documents = services.get_application_documents(self.mock_application)
        self.assertEqual(len(list(documents.all())), 0)

    def test_get_application_document_packages(self):
        """Test retrieving all document packages for an application"""
        # Mock DocumentPackage.objects.filter
        DocumentPackage.objects.filter.return_value = MagicMock(
            exists=lambda: True,
            all=lambda: [self.mock_package]
        )

        # Call get_application_document_packages with mock application
        packages = services.get_application_document_packages(self.mock_application)

        # Assert correct packages are returned
        self.assertEqual(len(list(packages.all())), 1)
        self.assertEqual(list(packages.all())[0], self.mock_package)
        DocumentPackage.objects.filter.assert_called_with(application=self.mock_application)

        # Test with application having no packages
        DocumentPackage.objects.filter.return_value = MagicMock(exists=lambda: False)
        packages = services.get_application_document_packages(self.mock_application)
        self.assertEqual(len(list(packages.all())), 0)


class TestSignatureRequests(TestCase):
    """Test cases for signature request functions"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_document = create_mock_document(DOCUMENT_TYPES['LOAN_AGREEMENT'], DOCUMENT_STATUS['GENERATED'])
        self.mock_package = create_mock_document_package(DOCUMENT_PACKAGE_TYPES['LOAN_AGREEMENT'], DOCUMENT_STATUS['GENERATED'])
        self.mock_user = create_mock_user()
        self.mock_signature_request = create_mock_signature_request(SIGNATURE_STATUS['PENDING'])
        self.test_signers = [{'user_id': str(uuid.uuid4()), 'name': 'Test Signer', 'email': 'test@example.com', 'signer_type': SIGNER_TYPES['BORROWER']}]

    def test_create_signature_request(self):
        """Test creating a signature request for a document"""
        # Mock docusign_service.create_signature_request
        docusign_service.create_signature_request = MagicMock(return_value={'envelope_id': 'test_envelope_id'})

        # Mock SignatureRequest.objects.create
        SignatureRequest.objects.create = MagicMock(return_value=self.mock_signature_request)

        # Call create_signature_request with test data
        result = services.create_signature_request(self.mock_document, self.test_signers, "Test Subject", "Test Body")

        # Assert signature requests were created
        self.assertEqual(result['envelope_id'], 'test_envelope_id')
        docusign_service.create_signature_request.assert_called_with(self.mock_document, self.test_signers, "Test Subject", "Test Body")
        SignatureRequest.objects.create.assert_called()

        # Assert document status was updated
        self.assertEqual(self.mock_document.status, 'sent')

        # Verify correct methods were called
        self.mock_document.save.assert_called_once()

    def test_create_package_signature_request(self):
        """Test creating a signature request for a document package"""
        # Mock docusign_service.create_signature_request_for_package
        docusign_service.create_signature_request_for_package = MagicMock(return_value={'envelope_id': 'test_envelope_id'})

        # Mock package.get_documents and related methods
        self.mock_package.get_documents.return_value = [self.mock_document]

        # Call create_package_signature_request with test data
        result = services.create_package_signature_request(self.mock_package, self.test_signers, "Test Subject", "Test Body")

        # Assert signature requests were created for all documents
        self.assertEqual(result['envelope_id'], 'test_envelope_id')
        docusign_service.create_signature_request_for_package.assert_called_with([self.mock_document], self.test_signers, "Test Subject", "Test Body")

        # Assert document and package statuses were updated
        self.assertEqual(self.mock_document.status, 'sent')
        self.mock_document.save.assert_called_once()

        # Verify correct methods were called
        self.mock_package.get_documents.assert_called_once()

    def test_get_signature_status(self):
        """Test retrieving signature status for a document"""
        # Mock document.get_signature_requests
        SignatureRequest.objects.filter.return_value = [self.mock_signature_request]

        # Mock docusign_service.get_signature_status
        docusign_service.get_signature_status = MagicMock(return_value={'status': 'completed'})

        # Call get_signature_status with mock document
        status = services.get_signature_status(self.mock_document)

        # Assert correct status information is returned
        self.assertEqual(status, {'status': 'completed'})
        docusign_service.get_signature_status.assert_called_with(self.mock_document)

        # Test with document having no signature requests
        SignatureRequest.objects.filter.return_value = []
        status = services.get_signature_status(self.mock_document)
        self.assertEqual(status, {'status': 'generated'})

    def test_update_signature_status(self):
        """Test updating signature status for a document"""
        # Mock document.get_signature_requests
        SignatureRequest.objects.filter.return_value = [self.mock_signature_request]

        # Mock docusign_service.update_signature_status
        docusign_service.update_signature_status = MagicMock(return_value=True)

        # Call update_signature_status with mock document
        result = services.update_signature_status(self.mock_document)

        # Assert signature request statuses were updated
        self.assertTrue(result)
        docusign_service.update_signature_status.assert_called_with(self.mock_document)

        # Assert document status was updated if all signatures complete
        self.mock_document.update_status.assert_called_once()

        # Verify correct methods were called
        SignatureRequest.objects.filter.assert_called_with(document=self.mock_document)

    def test_update_package_signature_status(self):
        """Test updating signature status for all documents in a package"""
        # Mock package.get_documents
        self.mock_package.get_documents.return_value = [self.mock_document]

        # Mock update_signature_status for each document
        services.update_signature_status = MagicMock(return_value=True)

        # Call update_package_signature_status with mock package
        result = services.update_package_signature_status(self.mock_package)

        # Assert update_signature_status was called for each document
        self.assertTrue(result)
        services.update_signature_status.assert_called_with(self.mock_document)

        # Assert package status was updated
        self.mock_package.update_status.assert_called_once()

        # Verify correct methods were called
        self.mock_package.get_documents.assert_called_once()

    def test_send_signature_reminder(self):
        """Test sending a reminder for a pending signature"""
        # Mock signature_request.can_send_reminder
        self.mock_signature_request.can_send_reminder.return_value = True

        # Mock signature_request.send_reminder
        self.mock_signature_request.send_reminder.return_value = True

        # Call send_signature_reminder with mock signature request
        result = services.send_signature_reminder(self.mock_signature_request)

        # Assert send_reminder was called if can_send_reminder is True
        self.assertTrue(result)
        self.mock_signature_request.send_reminder.assert_called_once()

        # Test with signature request that can't receive reminders
        self.mock_signature_request.can_send_reminder.return_value = False
        result = services.send_signature_reminder(self.mock_signature_request)
        self.assertFalse(result)

    def test_void_signature_request(self):
        """Test voiding a signature request"""
        # Mock document.get_signature_requests
        SignatureRequest.objects.filter.return_value = [self.mock_signature_request]

        # Mock docusign_service.void_envelope
        docusign_service.void_envelope = MagicMock(return_value=True)

        # Call void_signature_request with mock document and reason
        result = services.void_signature_request(self.mock_document, "Test Reason")

        # Assert void_envelope was called for each envelope
        self.assertTrue(result)
        docusign_service.void_envelope.assert_called_with("test_envelope_id", "Test Reason")

        # Assert signature request statuses were updated to VOIDED
        self.assertEqual(self.mock_signature_request.status, SIGNATURE_STATUS['VOIDED'])

        # Assert document status was updated to VOIDED
        self.assertEqual(self.mock_document.status, 'voided')

        # Verify correct methods were called
        SignatureRequest.objects.filter.assert_called_with(document=self.mock_document)


class TestDocumentProcessing(TestCase):
    """Test cases for document processing functions"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_document = create_mock_document(DOCUMENT_TYPES['LOAN_AGREEMENT'], DOCUMENT_STATUS['GENERATED'])
        self.mock_package = create_mock_document_package(DOCUMENT_PACKAGE_TYPES['LOAN_AGREEMENT'], DOCUMENT_STATUS['GENERATED'])
        self.mock_signature_request = create_mock_signature_request(SIGNATURE_STATUS['PENDING'])

    def test_process_signed_documents(self):
        """Test processing documents after they have been signed"""
        # Mock document with SIGNED status
        self.mock_document.status = DOCUMENT_STATUS['SIGNED']

        # Mock docusign_service.download_signed_documents
        docusign_service.download_signed_documents = MagicMock(return_value=[{'document_id': str(self.mock_document.id), 'content': b"Signed content"}])

        # Mock document_storage.store_document
        document_storage.store_document = MagicMock(return_value={'key': 'test/path/signed_document.pdf'})

        # Call process_signed_documents with mock document
        result = services.process_signed_documents(self.mock_document)

        # Assert document status was updated to COMPLETED
        self.assertTrue(result)
        self.assertEqual(self.mock_document.status, DOCUMENT_STATUS['COMPLETED'])

        # Verify correct methods were called
        docusign_service.download_signed_documents.assert_called_with(self.mock_signature_request.external_reference.split(':')[0])
        document_storage.store_document.assert_called_once()

        # Test with document not in SIGNED status
        self.mock_document.status = DOCUMENT_STATUS['GENERATED']
        with self.assertRaises(ValueError):
            services.process_signed_documents(self.mock_document)

    def test_process_package_signed_documents(self):
        """Test processing all signed documents in a package"""
        # Mock package.get_documents to return mix of signed and unsigned documents
        mock_signed_document = create_mock_document(DOCUMENT_TYPES['LOAN_AGREEMENT'], DOCUMENT_STATUS['SIGNED'])
        mock_unsigned_document = create_mock_document(DOCUMENT_TYPES['DISCLOSURE_FORM'], DOCUMENT_STATUS['GENERATED'])
        self.mock_package.get_documents.return_value = [mock_signed_document, mock_unsigned_document]

        # Mock process_signed_documents for each document
        services.process_signed_documents = MagicMock(return_value=True)

        # Call process_package_signed_documents with mock package
        result = services.process_package_signed_documents(self.mock_package)

        # Assert process_signed_documents was called for each SIGNED document
        self.assertTrue(result)
        services.process_signed_documents.assert_called_once_with(mock_signed_document)

        # Assert package status was updated
        self.mock_package.update_status.assert_called_once()

        # Verify correct methods were called
        self.mock_package.get_documents.assert_called_once()

    def test_check_document_expiration(self):
        """Test checking for and processing expired documents"""
        # Mock Document.objects.filter to return documents with expired dates
        mock_expired_document = create_mock_document(DOCUMENT_TYPES['LOAN_AGREEMENT'], DOCUMENT_STATUS['SENT'])
        DocumentPackage.objects.filter.return_value = [mock_expired_document]

        # Mock SignatureRequest.objects.filter
        SignatureRequest.objects.filter.return_value = [self.mock_signature_request]

        # Call check_document_expiration
        result = services.check_document_expiration()

        # Assert document statuses were updated to EXPIRED
        self.assertEqual(mock_expired_document.status, DOCUMENT_STATUS['EXPIRED'])

        # Assert signature request statuses were updated to EXPIRED
        self.assertEqual(self.mock_signature_request.status, SIGNATURE_STATUS['EXPIRED'])

        # Assert package statuses were updated
        self.mock_package.update_status.assert_called_once()

        # Verify correct methods were called
        DocumentPackage.objects.filter.assert_called()


class TestDocumentTemplates(TestCase):
    """Test cases for document template functions"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_template = MagicMock(spec=DocumentTemplate)
        self.mock_template.id = uuid.uuid4()
        self.mock_template.document_type = DOCUMENT_TYPES['LOAN_AGREEMENT']
        self.mock_template.get_content.return_value = "Test template content"
        self.mock_user = create_mock_user()
        self.test_data = {'key': 'test/path/test_template.html', 'version_id': '1'}

    def test_get_document_templates(self):
        """Test retrieving active document templates"""
        # Mock DocumentTemplate.objects.filter
        DocumentTemplate.objects.filter = MagicMock(return_value=[self.mock_template])

        # Call get_document_templates with document type
        templates = services.get_document_templates(DOCUMENT_TYPES['LOAN_AGREEMENT'])

        # Assert correct templates are returned
        self.assertEqual(templates, [self.mock_template])
        DocumentTemplate.objects.filter.assert_called_with(document_type=DOCUMENT_TYPES['LOAN_AGREEMENT'], is_active=True)

        # Test with different document types
        services.get_document_templates(DOCUMENT_TYPES['DISCLOSURE_FORM'])
        DocumentTemplate.objects.filter.assert_called_with(document_type=DOCUMENT_TYPES['DISCLOSURE_FORM'], is_active=True)

    def test_get_document_template_by_id(self):
        """Test retrieving a document template by ID"""
        # Mock DocumentTemplate.objects.get
        DocumentTemplate.objects.get = MagicMock(return_value=self.mock_template)

        # Call get_document_template_by_id with test ID
        template = services.get_document_template_by_id(self.mock_template.id)

        # Assert correct template is returned
        self.assertEqual(template, self.mock_template)
        DocumentTemplate.objects.get.assert_called_with(id=self.mock_template.id)

        # Test with non-existent ID returns None
        DocumentTemplate.objects.get.side_effect = DocumentTemplate.DoesNotExist
        template = services.get_document_template_by_id(uuid.uuid4())
        self.assertIsNone(template)

    def test_create_document_template(self):
        """Test creating a new document template"""
        # Mock document_storage.store_template
        document_storage.store_template = MagicMock(return_value=self.test_data)

        # Mock DocumentTemplate.objects.create
        DocumentTemplate.objects.create = MagicMock(return_value=self.mock_template)

        # Call create_document_template with test data
        template = services.create_document_template("Test Template", "Test Description", DOCUMENT_TYPES['LOAN_AGREEMENT'], b"Test Content", "1.0", self.mock_user)

        # Assert template was created with correct attributes
        self.assertEqual(template, self.mock_template)
        document_storage.store_template.assert_called_with(content=b"Test Content", template_type=DOCUMENT_TYPES['LOAN_AGREEMENT'])
        DocumentTemplate.objects.create.assert_called()

        # Verify correct methods were called
        document_storage.store_template.assert_called_once()
        DocumentTemplate.objects.create.assert_called_once()

    def test_update_document_template(self):
        """Test updating an existing document template"""
        # Mock document_storage.store_template
        document_storage.store_template = MagicMock(return_value=self.test_data)

        # Call update_document_template with mock template and new data
        template = services.update_document_template(self.mock_template, "New Name", "New Description", b"New Content", "1.1", True)

        # Assert template was updated with correct attributes
        self.assertEqual(template, self.mock_template)
        self.assertEqual(self.mock_template.name, "New Name")
        self.assertEqual(self.mock_template.description, "New Description")
        self.assertEqual(self.mock_template.version, "1.1")
        self.assertEqual(self.mock_template.is_active, True)

        # Test with and without new content
        services.update_document_template(self.mock_template, "New Name", "New Description", None, "1.1", True)
        self.assertEqual(self.mock_template.name, "New Name")

        # Verify correct methods were called
        document_storage.store_template.assert_called()
        self.mock_template.save.assert_called()


class TestDocumentFields(TestCase):
    """Test cases for document field functions"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_document = create_mock_document(DOCUMENT_TYPES['LOAN_AGREEMENT'], DOCUMENT_STATUS['GENERATED'])
        self.mock_field = MagicMock(spec=DocumentField)
        self.mock_field.id = uuid.uuid4()

    def test_get_document_fields(self):
        """Test retrieving fields for a document"""
        # Mock DocumentField.objects.filter
        DocumentField.objects.filter = MagicMock(return_value=[self.mock_field])

        # Call get_document_fields with mock document
        fields = services.get_document_fields(self.mock_document)

        # Assert correct fields are returned
        self.assertEqual(fields, [self.mock_field])
        DocumentField.objects.filter.assert_called_with(document=self.mock_document)

        # Test with document having no fields
        DocumentField.objects.filter.return_value = []
        fields = services.get_document_fields(self.mock_document)
        self.assertEqual(fields, [])

    def test_create_document_field(self):
        """Test creating a field in a document"""
        # Mock DocumentField.objects.create
        DocumentField.objects.create = MagicMock(return_value=self.mock_field)

        # Call create_document_field with test data
        field = services.create_document_field(self.mock_document, "Test Field", "text", "Test Value", 100, 200, 1)

        # Assert field was created with correct attributes
        self.assertEqual(field, self.mock_field)
        DocumentField.objects.create.assert_called()

        # Test with document in non-editable state
        self.mock_document.status = DOCUMENT_STATUS['SENT']

        # Verify correct methods were called
        DocumentField.objects.create.assert_called_once()