from django.test import TestCase
from unittest.mock import mock, patch
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model

from ..models import (
    DocumentTemplate, DocumentPackage, Document, 
    SignatureRequest, DocumentField
)
from ..storage import document_storage
from ..constants import (
    DOCUMENT_TYPES, DOCUMENT_STATUS, DOCUMENT_PACKAGE_TYPES,
    SIGNATURE_STATUS, SIGNER_TYPES, DOCUMENT_EXPIRATION_DAYS
)
from ...applications.models import LoanApplication


class TestDocumentTemplate(TestCase):
    """Test case for the DocumentTemplate model"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create a test user for document creation
        User = get_user_model()
        self.user = User.objects.create(
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        
        # Create a test document template with test data
        self.template = DocumentTemplate.objects.create(
            name="Test Template",
            description="Test template description",
            document_type=DOCUMENT_TYPES['LOAN_AGREEMENT'],
            file_path="templates/test_template.html",
            version="1.0",
            is_active=True,
            created_by=self.user
        )

    def test_template_creation(self):
        """Test that a document template can be created with valid data"""
        template = DocumentTemplate(
            name="Another Template",
            description="Another description",
            document_type=DOCUMENT_TYPES['DISCLOSURE_FORM'],
            file_path="templates/another_template.html",
            version="1.0",
            is_active=True,
            created_by=self.user
        )
        template.save()
        
        self.assertIsNotNone(template.pk)
        self.assertEqual(template.name, "Another Template")
        self.assertEqual(template.document_type, DOCUMENT_TYPES['DISCLOSURE_FORM'])

    def test_template_versioning(self):
        """Test that template versioning works correctly"""
        # Create a template with version '1.0'
        template1 = DocumentTemplate.objects.create(
            name="Version Test",
            document_type=DOCUMENT_TYPES['LOAN_AGREEMENT'],
            file_path="templates/version_test.html",
            version="1.0",
            is_active=True,
            created_by=self.user
        )
        
        # Create another template of the same type with version '2.0'
        template2 = DocumentTemplate.objects.create(
            name="Version Test",
            document_type=DOCUMENT_TYPES['LOAN_AGREEMENT'],
            file_path="templates/version_test_v2.html",
            version="2.0",
            is_active=True,
            created_by=self.user
        )
        
        # Assert that both templates exist
        self.assertIsNotNone(template1.pk)
        self.assertIsNotNone(template2.pk)
        
        # Refresh from database to get updated values
        template1.refresh_from_db()
        
        # Set the second template as active
        self.assertTrue(template2.is_active)
        
        # Assert that the first template is now inactive
        self.assertFalse(template1.is_active)
        
        # Assert that the second template is active
        self.assertTrue(template2.is_active)

    @patch('apps.documents.storage.document_storage.retrieve_document')
    def test_get_content(self, mock_retrieve):
        """Test that get_content retrieves template content correctly"""
        # Set up mock return value
        mock_content = b"Test template content"
        mock_retrieve.return_value = (mock_content, 'text/html', {})
        
        # Call get_content on the template
        content = self.template.get_content()
        
        # Assert that document_storage.retrieve_document was called with the correct parameters
        mock_retrieve.assert_called_once_with(self.template.file_path)
        
        # Assert that the returned content matches the expected content
        self.assertEqual(content, "Test template content")

    def test_str_representation(self):
        """Test the string representation of the template"""
        # Create a template with known name and version
        template = DocumentTemplate(
            name="Test String",
            version="1.5"
        )
        
        # Assert that str(template) returns the expected string
        expected = "Test String - v1.5"
        self.assertEqual(str(template), expected)


class TestDocumentPackage(TestCase):
    """Test case for the DocumentPackage model"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create a test user for document creation
        User = get_user_model()
        self.user = User.objects.create(
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        
        # Create a test loan application
        self.application = LoanApplication.objects.create(
            status="draft",
            created_by=self.user
        )
        
        # Create a test document package associated with the loan application
        self.package = DocumentPackage.objects.create(
            application=self.application,
            package_type=DOCUMENT_PACKAGE_TYPES['LOAN_AGREEMENT'],
            status=DOCUMENT_STATUS['DRAFT'],
            created_by=self.user
        )

    def test_package_creation(self):
        """Test that a document package can be created with valid data"""
        # Create a new document package with valid data
        package = DocumentPackage(
            application=self.application,
            package_type=DOCUMENT_PACKAGE_TYPES['DISCLOSURE'],
            status=DOCUMENT_STATUS['DRAFT'],
            created_by=self.user
        )
        package.save()
        
        # Assert that the package was created successfully
        self.assertIsNotNone(package.pk)
        
        # Assert that the package has the expected attributes
        self.assertEqual(package.package_type, DOCUMENT_PACKAGE_TYPES['DISCLOSURE'])
        self.assertEqual(package.status, DOCUMENT_STATUS['DRAFT'])

    def test_expiration_date_calculation(self):
        """Test that expiration_date is calculated correctly"""
        # Create a new document package without setting expiration_date
        now = timezone.now()
        package = DocumentPackage.objects.create(
            application=self.application,
            package_type=DOCUMENT_PACKAGE_TYPES['DISCLOSURE'],
            created_at=now,
            created_by=self.user
        )
        
        # Assert that expiration_date is set to created_at + DOCUMENT_EXPIRATION_DAYS
        expected_expiration = now + timedelta(days=DOCUMENT_EXPIRATION_DAYS)
        self.assertAlmostEqual(
            package.expiration_date.timestamp(),
            expected_expiration.timestamp(),
            delta=5  # Allow 5 seconds difference
        )

    def test_get_documents(self):
        """Test that get_documents returns all documents in the package"""
        # Create multiple test documents associated with the package
        document1 = Document.objects.create(
            package=self.package,
            document_type=DOCUMENT_TYPES['LOAN_AGREEMENT'],
            file_name="test_doc1.pdf",
            file_path="documents/test_doc1.pdf",
            status=DOCUMENT_STATUS['GENERATED'],
            generated_by=self.user
        )
        
        document2 = Document.objects.create(
            package=self.package,
            document_type=DOCUMENT_TYPES['DISCLOSURE_FORM'],
            file_name="test_doc2.pdf",
            file_path="documents/test_doc2.pdf",
            status=DOCUMENT_STATUS['GENERATED'],
            generated_by=self.user
        )
        
        # Call get_documents on the package
        documents = self.package.get_documents()
        
        # Assert that the returned queryset contains all the expected documents
        self.assertEqual(documents.count(), 2)
        self.assertIn(document1, documents)
        self.assertIn(document2, documents)

    def test_is_complete(self):
        """Test that is_complete returns the correct status"""
        # Test when all documents are completed: is_complete should return True
        document1 = Document.objects.create(
            package=self.package,
            document_type=DOCUMENT_TYPES['LOAN_AGREEMENT'],
            file_name="test_doc1.pdf",
            file_path="documents/test_doc1.pdf",
            status=DOCUMENT_STATUS['COMPLETED'],
            generated_by=self.user
        )
        
        document2 = Document.objects.create(
            package=self.package,
            document_type=DOCUMENT_TYPES['DISCLOSURE_FORM'],
            file_name="test_doc2.pdf",
            file_path="documents/test_doc2.pdf",
            status=DOCUMENT_STATUS['COMPLETED'],
            generated_by=self.user
        )
        
        self.assertTrue(self.package.is_complete())
        
        # Test when some documents are not completed: is_complete should return False
        document2.status = DOCUMENT_STATUS['SENT']
        document2.save()
        
        self.assertFalse(self.package.is_complete())

    def test_is_expired(self):
        """Test that is_expired returns the correct status"""
        # Create a package with expiration_date in the future
        future_date = timezone.now() + timedelta(days=10)
        self.package.expiration_date = future_date
        self.package.save()
        
        # Assert that is_expired returns False
        self.assertFalse(self.package.is_expired())
        
        # Create a package with expiration_date in the past
        past_date = timezone.now() - timedelta(days=1)
        self.package.expiration_date = past_date
        self.package.save()
        
        # Assert that is_expired returns True
        self.assertTrue(self.package.is_expired())

    def test_update_status(self):
        """Test that update_status updates the package status correctly"""
        # Create multiple test documents with different statuses
        Document.objects.create(
            package=self.package,
            document_type=DOCUMENT_TYPES['LOAN_AGREEMENT'],
            file_name="doc1.pdf",
            file_path="documents/doc1.pdf",
            status=DOCUMENT_STATUS['GENERATED'],
            generated_by=self.user
        )
        
        Document.objects.create(
            package=self.package,
            document_type=DOCUMENT_TYPES['DISCLOSURE_FORM'],
            file_name="doc2.pdf",
            file_path="documents/doc2.pdf",
            status=DOCUMENT_STATUS['SENT'],
            generated_by=self.user
        )
        
        # Call update_status on the package
        result = self.package.update_status()
        
        # Assert that the package status is updated based on document statuses
        self.assertTrue(result)
        self.assertEqual(self.package.status, DOCUMENT_STATUS['SENT'])
        
        # Test when all documents are completed
        for doc in Document.objects.filter(package=self.package):
            doc.status = DOCUMENT_STATUS['COMPLETED']
            doc.save()
        
        result = self.package.update_status()
        self.assertTrue(result)
        self.assertEqual(self.package.status, DOCUMENT_STATUS['COMPLETED'])

    def test_str_representation(self):
        """Test the string representation of the package"""
        # Create a package with known type and application
        expected = f"{self.package.get_package_type_display()} - Application {self.application.id}"
        self.assertEqual(str(self.package), expected)


class TestDocument(TestCase):
    """Test case for the Document model"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create a test user for document creation
        User = get_user_model()
        self.user = User.objects.create(
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        
        # Create a test loan application
        self.application = LoanApplication.objects.create(
            status="draft",
            created_by=self.user
        )
        
        # Create a test document package
        self.package = DocumentPackage.objects.create(
            application=self.application,
            package_type=DOCUMENT_PACKAGE_TYPES['LOAN_AGREEMENT'],
            status=DOCUMENT_STATUS['DRAFT'],
            created_by=self.user
        )
        
        # Create a test document associated with the package
        self.document = Document.objects.create(
            package=self.package,
            document_type=DOCUMENT_TYPES['LOAN_AGREEMENT'],
            file_name="test_document.pdf",
            file_path="documents/test_document.pdf",
            status=DOCUMENT_STATUS['GENERATED'],
            generated_by=self.user
        )

    def test_document_creation(self):
        """Test that a document can be created with valid data"""
        # Create a new document with valid data
        document = Document(
            package=self.package,
            document_type=DOCUMENT_TYPES['DISCLOSURE_FORM'],
            file_name="another_document.pdf",
            file_path="documents/another_document.pdf",
            status=DOCUMENT_STATUS['DRAFT'],
            generated_by=self.user
        )
        document.save()
        
        # Assert that the document was created successfully
        self.assertIsNotNone(document.pk)
        
        # Assert that the document has the expected attributes
        self.assertEqual(document.document_type, DOCUMENT_TYPES['DISCLOSURE_FORM'])
        self.assertEqual(document.status, DOCUMENT_STATUS['DRAFT'])
        
        # Assert that generated_at is set automatically
        self.assertIsNotNone(document.generated_at)

    @patch('apps.documents.storage.document_storage.retrieve_document')
    def test_get_content(self, mock_retrieve):
        """Test that get_content retrieves document content correctly"""
        # Mock document_storage.retrieve_document to return test content
        mock_content = b"Test document content"
        mock_retrieve.return_value = (mock_content, 'application/pdf', {})
        
        # Call get_content on the document
        content = self.document.get_content()
        
        # Assert that document_storage.retrieve_document was called with the correct parameters
        mock_retrieve.assert_called_once_with(self.document.file_path)
        
        # Assert that the returned content matches the expected content
        self.assertEqual(content, mock_content)

    @patch('apps.documents.storage.document_storage.get_document_url')
    def test_get_download_url(self, mock_get_url):
        """Test that get_download_url generates a download URL correctly"""
        # Mock document_storage.get_document_url to return a test URL
        expected_url = "https://example.com/documents/test_document.pdf"
        mock_get_url.return_value = expected_url
        
        # Call get_download_url on the document
        url = self.document.get_download_url(expiry_seconds=1800)
        
        # Assert that document_storage.get_document_url was called with the correct parameters
        mock_get_url.assert_called_once_with(self.document.file_path, 1800)
        
        # Assert that the returned URL matches the expected URL
        self.assertEqual(url, expected_url)

    def test_get_signature_requests(self):
        """Test that get_signature_requests returns all signature requests for the document"""
        # Create multiple test signature requests associated with the document
        signer1 = get_user_model().objects.create(
            email="signer1@example.com",
            first_name="Signer",
            last_name="One"
        )
        
        signer2 = get_user_model().objects.create(
            email="signer2@example.com",
            first_name="Signer",
            last_name="Two"
        )
        
        sig_req1 = SignatureRequest.objects.create(
            document=self.document,
            signer=signer1,
            signer_type=SIGNER_TYPES['BORROWER'],
            status=SIGNATURE_STATUS['PENDING'],
            created_by=self.user
        )
        
        sig_req2 = SignatureRequest.objects.create(
            document=self.document,
            signer=signer2,
            signer_type=SIGNER_TYPES['CO_BORROWER'],
            status=SIGNATURE_STATUS['PENDING'],
            created_by=self.user
        )
        
        # Call get_signature_requests on the document
        signature_requests = self.document.get_signature_requests()
        
        # Assert that the returned queryset contains all the expected signature requests
        self.assertEqual(signature_requests.count(), 2)
        self.assertIn(sig_req1, signature_requests)
        self.assertIn(sig_req2, signature_requests)

    def test_get_fields(self):
        """Test that get_fields returns all document fields for the document"""
        # Create multiple test document fields associated with the document
        field1 = DocumentField.objects.create(
            document=self.document,
            field_name="signature",
            field_type="signature",
            x_position=100,
            y_position=100,
            page_number=1,
            created_by=self.user
        )
        
        field2 = DocumentField.objects.create(
            document=self.document,
            field_name="date",
            field_type="date",
            x_position=200,
            y_position=100,
            page_number=1,
            created_by=self.user
        )
        
        # Call get_fields on the document
        fields = self.document.get_fields()
        
        # Assert that the returned queryset contains all the expected document fields
        self.assertEqual(fields.count(), 2)
        self.assertIn(field1, fields)
        self.assertIn(field2, fields)

    def test_update_status(self):
        """Test that update_status updates the document status correctly"""
        # Call update_status with a new status
        result = self.document.update_status(DOCUMENT_STATUS['SENT'])
        
        # Assert that the document status is updated
        self.assertTrue(result)
        self.assertEqual(self.document.status, DOCUMENT_STATUS['SENT'])
        
        # Assert that update_status returns True when status changes
        result = self.document.update_status(DOCUMENT_STATUS['SIGNED'])
        self.assertTrue(result)
        
        # Assert that update_status returns False when status doesn't change
        result = self.document.update_status(DOCUMENT_STATUS['SIGNED'])
        self.assertFalse(result)
        
        # Test with invalid status (should raise ValidationError)
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            self.document.update_status("invalid_status")

    def test_is_signed(self):
        """Test that is_signed returns the correct status"""
        # Create multiple test signature requests with different statuses
        signer = get_user_model().objects.create(
            email="signer@example.com",
            first_name="Signer",
            last_name="Test"
        )
        
        SignatureRequest.objects.create(
            document=self.document,
            signer=signer,
            signer_type=SIGNER_TYPES['BORROWER'],
            status=SIGNATURE_STATUS['PENDING'],
            created_by=self.user
        )
        
        # Test when some signatures are not completed: is_signed should return False
        self.assertFalse(self.document.is_signed())
        
        # Update all signature requests to completed status
        for sig_req in SignatureRequest.objects.filter(document=self.document):
            sig_req.status = SIGNATURE_STATUS['COMPLETED']
            sig_req.save()
        
        # Test when all required signatures are completed: is_signed should return True
        self.assertTrue(self.document.is_signed())

    @patch('apps.documents.models.DocumentPackage.is_expired')
    def test_is_expired(self, mock_is_expired):
        """Test that is_expired returns the correct status"""
        # Mock package.is_expired to return different values
        
        # Test when package is not expired
        mock_is_expired.return_value = False
        self.assertFalse(self.document.is_expired())
        
        # Test when package is expired
        mock_is_expired.return_value = True
        self.assertTrue(self.document.is_expired())

    def test_str_representation(self):
        """Test the string representation of the document"""
        # Create a document with known type and file name
        expected = f"{self.document.get_document_type_display()} - {self.document.file_name}"
        self.assertEqual(str(self.document), expected)


class TestSignatureRequest(TestCase):
    """Test case for the SignatureRequest model"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create a test user for document creation
        User = get_user_model()
        self.user = User.objects.create(
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        
        # Create a test signer user
        self.signer = User.objects.create(
            email="signer@example.com",
            first_name="Signer",
            last_name="Test"
        )
        
        # Create a test loan application
        self.application = LoanApplication.objects.create(
            status="draft",
            created_by=self.user
        )
        
        # Create a test document package
        self.package = DocumentPackage.objects.create(
            application=self.application,
            package_type=DOCUMENT_PACKAGE_TYPES['LOAN_AGREEMENT'],
            status=DOCUMENT_STATUS['DRAFT'],
            created_by=self.user
        )
        
        # Create a test document
        self.document = Document.objects.create(
            package=self.package,
            document_type=DOCUMENT_TYPES['LOAN_AGREEMENT'],
            file_name="test_document.pdf",
            file_path="documents/test_document.pdf",
            status=DOCUMENT_STATUS['GENERATED'],
            generated_by=self.user
        )
        
        # Create a test signature request associated with the document and signer
        self.signature_request = SignatureRequest.objects.create(
            document=self.document,
            signer=self.signer,
            signer_type=SIGNER_TYPES['BORROWER'],
            status=SIGNATURE_STATUS['PENDING'],
            created_by=self.user
        )

    def test_signature_request_creation(self):
        """Test that a signature request can be created with valid data"""
        # Create a new signature request with valid data
        sig_req = SignatureRequest(
            document=self.document,
            signer=self.signer,
            signer_type=SIGNER_TYPES['CO_BORROWER'],
            status=SIGNATURE_STATUS['PENDING'],
            created_by=self.user
        )
        sig_req.save()
        
        # Assert that the signature request was created successfully
        self.assertIsNotNone(sig_req.pk)
        
        # Assert that the signature request has the expected attributes
        self.assertEqual(sig_req.signer_type, SIGNER_TYPES['CO_BORROWER'])
        self.assertEqual(sig_req.status, SIGNATURE_STATUS['PENDING'])
        
        # Assert that requested_at is set automatically
        self.assertIsNotNone(sig_req.requested_at)

    def test_update_status(self):
        """Test that update_status updates the signature request status correctly"""
        # Call update_status with a new status
        result = self.signature_request.update_status(SIGNATURE_STATUS['SENT'])
        
        # Assert that the signature request status is updated
        self.assertTrue(result)
        self.assertEqual(self.signature_request.status, SIGNATURE_STATUS['SENT'])
        
        # Assert that update_status returns True when status changes
        result = self.signature_request.update_status(SIGNATURE_STATUS['DELIVERED'])
        self.assertTrue(result)
        
        # Assert that update_status returns False when status doesn't change
        result = self.signature_request.update_status(SIGNATURE_STATUS['DELIVERED'])
        self.assertFalse(result)
        
        # Test that completed_at is set when status changes to 'COMPLETED'
        self.assertIsNone(self.signature_request.completed_at)
        result = self.signature_request.update_status(SIGNATURE_STATUS['COMPLETED'])
        self.assertTrue(result)
        self.assertEqual(self.signature_request.status, SIGNATURE_STATUS['COMPLETED'])
        self.assertIsNotNone(self.signature_request.completed_at)
        
        # Test with invalid status (should raise ValidationError)
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            self.signature_request.update_status("invalid_status")

    @patch('apps.documents.models.SignatureRequest.can_send_reminder')
    def test_send_reminder(self, mock_can_send):
        """Test that send_reminder sends a reminder correctly"""
        # Mock can_send_reminder to return True
        mock_can_send.return_value = True
        
        # Call send_reminder
        result = self.signature_request.send_reminder()
        
        # Assert that reminder_count is incremented
        self.signature_request.refresh_from_db()
        self.assertEqual(self.signature_request.reminder_count, 1)
        
        # Assert that last_reminder_at is updated
        self.assertIsNotNone(self.signature_request.last_reminder_at)
        
        # Assert that send_reminder returns True
        self.assertTrue(result)
        
        # Mock can_send_reminder to return False
        mock_can_send.return_value = False
        
        # Call send_reminder
        result = self.signature_request.send_reminder()
        
        # Assert that send_reminder returns False
        self.assertFalse(result)

    def test_can_send_reminder(self):
        """Test that can_send_reminder returns the correct status"""
        # Import constants needed for testing
        from ..constants import MAX_REMINDERS, REMINDER_INTERVAL_DAYS
        
        # Test when status is 'COMPLETED': can_send_reminder should return False
        self.signature_request.status = SIGNATURE_STATUS['COMPLETED']
        self.signature_request.save()
        self.assertFalse(self.signature_request.can_send_reminder())
        
        # Reset status for further tests
        self.signature_request.status = SIGNATURE_STATUS['PENDING']
        self.signature_request.save()
        
        # Test when reminder_count >= MAX_REMINDERS: can_send_reminder should return False
        self.signature_request.reminder_count = MAX_REMINDERS
        self.signature_request.save()
        self.assertFalse(self.signature_request.can_send_reminder())
        
        # Reset reminder_count for further tests
        self.signature_request.reminder_count = 0
        self.signature_request.save()
        
        # Test when last_reminder_at is recent: can_send_reminder should return False
        self.signature_request.last_reminder_at = timezone.now()
        self.signature_request.save()
        self.assertFalse(self.signature_request.can_send_reminder())
        
        # Test when all conditions are met: can_send_reminder should return True
        self.signature_request.last_reminder_at = timezone.now() - timedelta(days=REMINDER_INTERVAL_DAYS + 1)
        self.signature_request.save()
        self.assertTrue(self.signature_request.can_send_reminder())

    def test_str_representation(self):
        """Test the string representation of the signature request"""
        # Create a signature request with known document, signer, and status
        expected = f"{self.document.get_document_type_display()} - {self.signer.get_full_name()} - {self.signature_request.get_status_display()}"
        self.assertEqual(str(self.signature_request), expected)


class TestDocumentField(TestCase):
    """Test case for the DocumentField model"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create a test user for document creation
        User = get_user_model()
        self.user = User.objects.create(
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        
        # Create a test loan application
        self.application = LoanApplication.objects.create(
            status="draft",
            created_by=self.user
        )
        
        # Create a test document package
        self.package = DocumentPackage.objects.create(
            application=self.application,
            package_type=DOCUMENT_PACKAGE_TYPES['LOAN_AGREEMENT'],
            status=DOCUMENT_STATUS['DRAFT'],
            created_by=self.user
        )
        
        # Create a test document
        self.document = Document.objects.create(
            package=self.package,
            document_type=DOCUMENT_TYPES['LOAN_AGREEMENT'],
            file_name="test_document.pdf",
            file_path="documents/test_document.pdf",
            status=DOCUMENT_STATUS['GENERATED'],
            generated_by=self.user
        )
        
        # Create a test document field associated with the document
        self.field = DocumentField.objects.create(
            document=self.document,
            field_name="signature",
            field_type="signature",
            x_position=100,
            y_position=100,
            page_number=1,
            created_by=self.user
        )

    def test_document_field_creation(self):
        """Test that a document field can be created with valid data"""
        # Create a new document field with valid data
        field = DocumentField(
            document=self.document,
            field_name="date",
            field_type="date",
            x_position=200,
            y_position=100,
            page_number=1,
            created_by=self.user
        )
        field.save()
        
        # Assert that the document field was created successfully
        self.assertIsNotNone(field.pk)
        
        # Assert that the document field has the expected attributes
        self.assertEqual(field.field_name, "date")
        self.assertEqual(field.field_type, "date")
        self.assertEqual(field.x_position, 200)

    def test_to_docusign_tab(self):
        """Test that to_docusign_tab converts the field to a DocuSign tab correctly"""
        # Create document fields of different types (signature, date, text, etc.)
        # Test signature field
        self.field.field_type = "signature"
        tab = self.field.to_docusign_tab()
        self.assertEqual(tab['tabType'], 'signHereTab')
        self.assertEqual(tab['tabLabel'], self.field.field_name)
        self.assertEqual(tab['xPosition'], 100)
        self.assertEqual(tab['yPosition'], 100)
        self.assertEqual(tab['pageNumber'], 1)
        
        # Test date field
        self.field.field_type = "date"
        tab = self.field.to_docusign_tab()
        self.assertEqual(tab['tabType'], 'dateSignedTab')
        
        # Test text field
        self.field.field_type = "text"
        self.field.field_value = "Sample text"
        tab = self.field.to_docusign_tab()
        self.assertEqual(tab['tabType'], 'textTab')
        self.assertEqual(tab['value'], "Sample text")
        
        # Test checkbox field
        self.field.field_type = "checkbox"
        self.field.field_value = "true"
        tab = self.field.to_docusign_tab()
        self.assertEqual(tab['tabType'], 'checkboxTab')
        self.assertTrue(tab['selected'])

    def test_str_representation(self):
        """Test the string representation of the document field"""
        # Create a document field with known name and type
        expected = f"{self.field.field_name} ({self.field.get_field_type_display()})"
        self.assertEqual(str(self.field), expected)