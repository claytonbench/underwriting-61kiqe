"""
Unit tests for the application models in the loan management system.

This file contains test cases to verify the functionality, validation rules, and 
business logic of the LoanApplication, LoanDetails, ApplicationDocument, 
ApplicationStatusHistory, and ApplicationNote models.
"""

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import datetime, timedelta
from unittest import mock

from ..models import (
    LoanApplication, 
    LoanDetails, 
    ApplicationDocument, 
    ApplicationStatusHistory, 
    ApplicationNote,
    ApplicationManager
)
from ..constants import (
    APPLICATION_TYPES, 
    RELATIONSHIP_TYPES, 
    APPLICATION_EDITABLE_STATUSES
)
from ...utils.constants import (
    APPLICATION_STATUS, 
    DOCUMENT_TYPES
)


class LoanApplicationModelTest(TestCase):
    """Test case for the LoanApplication model."""
    
    def setUp(self):
        """Set up test data for the test case."""
        # Create test users
        self.borrower_user = mock.MagicMock()
        self.borrower_user.id = '00000000-0000-0000-0000-000000000001'
        self.borrower_user.first_name = 'John'
        self.borrower_user.last_name = 'Doe'
        
        self.co_borrower_user = mock.MagicMock()
        self.co_borrower_user.id = '00000000-0000-0000-0000-000000000002'
        self.co_borrower_user.first_name = 'Jane'
        self.co_borrower_user.last_name = 'Doe'
        
        self.school_admin_user = mock.MagicMock()
        self.school_admin_user.id = '00000000-0000-0000-0000-000000000003'
        
        # Create test borrower profiles
        self.borrower_profile = mock.MagicMock()
        self.borrower_profile.user = self.borrower_user
        
        # Create test school, program, and program version
        self.school = mock.MagicMock()
        self.school.id = '00000000-0000-0000-0000-000000000004'
        self.school.name = 'Test School'
        
        self.program = mock.MagicMock()
        self.program.id = '00000000-0000-0000-0000-000000000005'
        self.program.name = 'Test Program'
        self.program.duration_weeks = 12
        
        self.program_version = mock.MagicMock()
        self.program_version.id = '00000000-0000-0000-0000-000000000006'
        self.program_version.program = self.program
        self.program_version.tuition_amount = Decimal('10000.00')
        
        # Create a test loan application
        self.application = LoanApplication(
            borrower=self.borrower_user,
            co_borrower=self.co_borrower_user,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            application_type=APPLICATION_TYPES['STANDARD'],
            relationship_type=RELATIONSHIP_TYPES['SPOUSE'],
            created_by=self.school_admin_user,
            updated_by=self.school_admin_user
        )
        self.application.save()
    
    def test_create_loan_application(self):
        """Test creating a loan application."""
        # Create a new application
        application = LoanApplication(
            borrower=self.borrower_user,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            application_type=APPLICATION_TYPES['STANDARD'],
            created_by=self.school_admin_user,
            updated_by=self.school_admin_user
        )
        application.save()
        
        # Assert that the application is created
        self.assertIsNotNone(application.id)
        self.assertEqual(application.borrower, self.borrower_user)
        self.assertEqual(application.school, self.school)
        self.assertEqual(application.program, self.program)
        self.assertEqual(application.program_version, self.program_version)
        self.assertEqual(application.application_type, APPLICATION_TYPES['STANDARD'])
        self.assertEqual(application.status, APPLICATION_STATUS['DRAFT'])
        self.assertIsNone(application.co_borrower)
        self.assertIsNone(application.relationship_type)
        self.assertIsNone(application.submission_date)
    
    def test_loan_application_str_method(self):
        """Test the string representation of a loan application."""
        expected_str = f"Application {self.application.id} - {self.borrower_user.first_name} {self.borrower_user.last_name}"
        self.assertEqual(str(self.application), expected_str)
    
    def test_application_is_editable(self):
        """Test the is_editable method for different application statuses."""
        # Test editable statuses
        for status in APPLICATION_EDITABLE_STATUSES:
            self.application.status = status
            self.assertTrue(self.application.is_editable())
        
        # Test non-editable statuses
        for status in [s for s in APPLICATION_STATUS.values() if s not in APPLICATION_EDITABLE_STATUSES]:
            self.application.status = status
            self.assertFalse(self.application.is_editable())
    
    @mock.patch('apps.applications.validators.validate_application_submission')
    def test_application_submit(self, mock_validate):
        """Test the submit method for a loan application."""
        # Setup
        mock_validate.return_value = True
        loan_details = mock.MagicMock()
        borrower_profile = mock.MagicMock()
        
        with mock.patch.object(self.application, 'get_loan_details', return_value=loan_details):
            with mock.patch('apps.users.models.BorrowerProfile.objects.get', return_value=borrower_profile):
                # Set application to draft status and ensure it's editable
                self.application.status = APPLICATION_STATUS['DRAFT']
                
                # Execute the submit method
                result = self.application.submit()
                
                # Verify the results
                self.assertTrue(result)
                self.assertEqual(self.application.status, APPLICATION_STATUS['SUBMITTED'])
                self.assertIsNotNone(self.application.submission_date)
                
                # Verify validate_application_submission was called with correct arguments
                mock_validate.assert_called_once_with(self.application, borrower_profile, loan_details)
    
    @mock.patch('apps.applications.validators.validate_application_submission')
    def test_application_submit_validation_failure(self, mock_validate):
        """Test the submit method when validation fails."""
        # Setup
        mock_validate.side_effect = ValidationError("Validation failed")
        loan_details = mock.MagicMock()
        borrower_profile = mock.MagicMock()
        
        with mock.patch.object(self.application, 'get_loan_details', return_value=loan_details):
            with mock.patch('apps.users.models.BorrowerProfile.objects.get', return_value=borrower_profile):
                # Set application to draft status
                self.application.status = APPLICATION_STATUS['DRAFT']
                original_status = self.application.status
                
                # Execute the submit method
                result = self.application.submit()
                
                # Verify the results
                self.assertFalse(result)
                self.assertEqual(self.application.status, original_status)
    
    def test_application_submit_not_editable(self):
        """Test the submit method when application is not editable."""
        # Set application to a non-editable status
        self.application.status = APPLICATION_STATUS['APPROVED']
        
        # Execute the submit method
        result = self.application.submit()
        
        # Verify the results
        self.assertFalse(result)
        self.assertEqual(self.application.status, APPLICATION_STATUS['APPROVED'])
    
    def test_get_loan_details(self):
        """Test the get_loan_details method."""
        # Create a loan details object
        loan_details = LoanDetails(
            application=self.application,
            tuition_amount=Decimal('10000.00'),
            deposit_amount=Decimal('1000.00'),
            other_funding=Decimal('0.00'),
            requested_amount=Decimal('9000.00'),
            start_date=timezone.now().date() + timedelta(days=30)
        )
        loan_details.save()
        
        # Get the loan details
        result = self.application.get_loan_details()
        
        # Verify the result
        self.assertEqual(result, loan_details)
    
    def test_get_documents(self):
        """Test the get_documents method."""
        # Create some documents
        doc1 = ApplicationDocument(
            application=self.application,
            document_type=DOCUMENT_TYPES['PROOF_OF_IDENTITY'],
            file_name='id.pdf',
            file_path='documents/id.pdf',
            uploaded_by=self.borrower_user
        )
        doc1.save()
        
        doc2 = ApplicationDocument(
            application=self.application,
            document_type=DOCUMENT_TYPES['PROOF_OF_INCOME'],
            file_name='income.pdf',
            file_path='documents/income.pdf',
            uploaded_by=self.borrower_user
        )
        doc2.save()
        
        # Get the documents
        documents = self.application.get_documents()
        
        # Verify the results
        self.assertEqual(documents.count(), 2)
        self.assertIn(doc1, documents)
        self.assertIn(doc2, documents)
    
    def test_get_status_history(self):
        """Test the get_status_history method."""
        # Create some status history records
        history1 = ApplicationStatusHistory(
            application=self.application,
            previous_status=APPLICATION_STATUS['DRAFT'],
            new_status=APPLICATION_STATUS['SUBMITTED'],
            changed_by=self.borrower_user,
            changed_at=timezone.now() - timedelta(days=5)
        )
        history1.save()
        
        history2 = ApplicationStatusHistory(
            application=self.application,
            previous_status=APPLICATION_STATUS['SUBMITTED'],
            new_status=APPLICATION_STATUS['IN_REVIEW'],
            changed_by=self.school_admin_user,
            changed_at=timezone.now() - timedelta(days=3)
        )
        history2.save()
        
        # Get the status history
        history = self.application.get_status_history()
        
        # Verify the results
        self.assertEqual(history.count(), 2)
        self.assertIn(history1, history)
        self.assertIn(history2, history)
        
        # Verify ordering (most recent first)
        self.assertEqual(history.first(), history2)
    
    def test_status_change_creates_history(self):
        """Test that changing the application status creates a history record."""
        # Record initial count of history records
        initial_count = ApplicationStatusHistory.objects.filter(application=self.application).count()
        
        # Change the status
        old_status = self.application.status
        new_status = APPLICATION_STATUS['IN_REVIEW']
        self.application.status = new_status
        self.application.save()
        
        # Verify a new history record was created
        new_count = ApplicationStatusHistory.objects.filter(application=self.application).count()
        self.assertEqual(new_count, initial_count + 1)
        
        # Verify the history record has correct values
        latest_history = ApplicationStatusHistory.objects.filter(application=self.application).latest('changed_at')
        self.assertEqual(latest_history.previous_status, old_status)
        self.assertEqual(latest_history.new_status, new_status)
    
    def test_clean_method_validation(self):
        """Test the clean method validation rules."""
        # Test validation for co-borrower without relationship_type
        app = LoanApplication(
            borrower=self.borrower_user,
            co_borrower=self.co_borrower_user,  # Has co-borrower
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            application_type=APPLICATION_TYPES['STANDARD'],
            relationship_type=None  # No relationship type
        )
        with self.assertRaises(ValidationError):
            app.clean()
        
        # Test validation for program_version not belonging to program
        different_program = mock.MagicMock()
        different_program.id = '00000000-0000-0000-0000-000000000007'
        
        program_version_mock = mock.MagicMock()
        program_version_mock.program = different_program
        
        app = LoanApplication(
            borrower=self.borrower_user,
            school=self.school,
            program=self.program,  # One program
            program_version=program_version_mock,  # Version belongs to different program
            application_type=APPLICATION_TYPES['STANDARD']
        )
        with self.assertRaises(ValidationError):
            app.clean()


class LoanDetailsModelTest(TestCase):
    """Test case for the LoanDetails model."""
    
    def setUp(self):
        """Set up test data for the test case."""
        # Create test user
        self.borrower_user = mock.MagicMock()
        self.borrower_user.id = '00000000-0000-0000-0000-000000000001'
        self.borrower_user.first_name = 'John'
        self.borrower_user.last_name = 'Doe'
        
        # Create test borrower profile
        self.borrower_profile = mock.MagicMock()
        self.borrower_profile.user = self.borrower_user
        
        # Create test school, program, and program version
        self.school = mock.MagicMock()
        self.school.id = '00000000-0000-0000-0000-000000000004'
        self.school.name = 'Test School'
        
        self.program = mock.MagicMock()
        self.program.id = '00000000-0000-0000-0000-000000000005'
        self.program.name = 'Test Program'
        self.program.duration_weeks = 12
        
        self.program_version = mock.MagicMock()
        self.program_version.id = '00000000-0000-0000-0000-000000000006'
        self.program_version.program = self.program
        self.program_version.tuition_amount = Decimal('10000.00')
        
        # Create a test loan application
        self.application = LoanApplication(
            borrower=self.borrower_user,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            application_type=APPLICATION_TYPES['STANDARD']
        )
        self.application.save()
        
        # Create test loan details
        self.loan_details = LoanDetails(
            application=self.application,
            tuition_amount=Decimal('10000.00'),
            deposit_amount=Decimal('1000.00'),
            other_funding=Decimal('500.00'),
            requested_amount=Decimal('8500.00'),
            start_date=timezone.now().date() + timedelta(days=30)
        )
        self.loan_details.save()
    
    def test_create_loan_details(self):
        """Test creating loan details."""
        # Create new loan details
        loan_details = LoanDetails(
            application=self.application,
            tuition_amount=Decimal('12000.00'),
            deposit_amount=Decimal('2000.00'),
            other_funding=Decimal('1000.00'),
            requested_amount=Decimal('9000.00'),
            start_date=timezone.now().date() + timedelta(days=60),
            completion_date=timezone.now().date() + timedelta(days=120)
        )
        loan_details.save()
        
        # Assert that the loan details are created
        self.assertIsNotNone(loan_details.id)
        self.assertEqual(loan_details.application, self.application)
        self.assertEqual(loan_details.tuition_amount, Decimal('12000.00'))
        self.assertEqual(loan_details.deposit_amount, Decimal('2000.00'))
        self.assertEqual(loan_details.other_funding, Decimal('1000.00'))
        self.assertEqual(loan_details.requested_amount, Decimal('9000.00'))
        self.assertIsNotNone(loan_details.start_date)
        self.assertIsNotNone(loan_details.completion_date)
    
    def test_loan_details_str_method(self):
        """Test the string representation of loan details."""
        expected_str = f"Application {self.application.id} - ${self.loan_details.requested_amount}"
        self.assertEqual(str(self.loan_details), expected_str)
    
    def test_get_net_tuition(self):
        """Test the get_net_tuition method."""
        # Set specific values
        self.loan_details.tuition_amount = Decimal('10000.00')
        self.loan_details.deposit_amount = Decimal('1000.00')
        self.loan_details.other_funding = Decimal('500.00')
        
        # Calculate expected net tuition
        expected_net_tuition = Decimal('8500.00')
        
        # Get the net tuition
        net_tuition = self.loan_details.get_net_tuition()
        
        # Verify the result
        self.assertEqual(net_tuition, expected_net_tuition)
    
    def test_get_program_duration_weeks(self):
        """Test the get_program_duration_weeks method."""
        # The program duration is set to 12 weeks in setUp
        expected_duration = 12
        
        # Get the program duration weeks
        duration = self.loan_details.get_program_duration_weeks()
        
        # Verify the result
        self.assertEqual(duration, expected_duration)
    
    def test_clean_method_validation(self):
        """Test the clean method validation rules."""
        # Test validation for negative tuition_amount
        self.loan_details.tuition_amount = Decimal('-1.00')
        with self.assertRaises(ValidationError):
            self.loan_details.clean()
        self.loan_details.tuition_amount = Decimal('10000.00')  # Reset
        
        # Test validation for negative deposit_amount
        self.loan_details.deposit_amount = Decimal('-1.00')
        with self.assertRaises(ValidationError):
            self.loan_details.clean()
        self.loan_details.deposit_amount = Decimal('1000.00')  # Reset
        
        # Test validation for negative other_funding
        self.loan_details.other_funding = Decimal('-1.00')
        with self.assertRaises(ValidationError):
            self.loan_details.clean()
        self.loan_details.other_funding = Decimal('500.00')  # Reset
        
        # Test validation for requested_amount exceeding net tuition
        self.loan_details.requested_amount = Decimal('9000.00')  # Net tuition is 8500.00
        with self.assertRaises(ValidationError):
            self.loan_details.clean()
        self.loan_details.requested_amount = Decimal('8500.00')  # Reset
        
        # Test validation for start_date in the past
        self.loan_details.start_date = timezone.now().date() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            self.loan_details.clean()
        self.loan_details.start_date = timezone.now().date() + timedelta(days=30)  # Reset
        
        # Test validation for completion_date before start_date
        self.loan_details.completion_date = self.loan_details.start_date - timedelta(days=1)
        with self.assertRaises(ValidationError):
            self.loan_details.clean()


class ApplicationDocumentModelTest(TestCase):
    """Test case for the ApplicationDocument model."""
    
    def setUp(self):
        """Set up test data for the test case."""
        # Create test users
        self.borrower_user = mock.MagicMock()
        self.borrower_user.id = '00000000-0000-0000-0000-000000000001'
        self.borrower_user.first_name = 'John'
        self.borrower_user.last_name = 'Doe'
        
        self.uploader_user = mock.MagicMock()
        self.uploader_user.id = '00000000-0000-0000-0000-000000000003'
        
        # Create test borrower profile
        self.borrower_profile = mock.MagicMock()
        self.borrower_profile.user = self.borrower_user
        
        # Create test school, program, and program version
        self.school = mock.MagicMock()
        self.school.id = '00000000-0000-0000-0000-000000000004'
        self.school.name = 'Test School'
        
        self.program = mock.MagicMock()
        self.program.id = '00000000-0000-0000-0000-000000000005'
        self.program.name = 'Test Program'
        
        self.program_version = mock.MagicMock()
        self.program_version.id = '00000000-0000-0000-0000-000000000006'
        self.program_version.program = self.program
        
        # Create a test loan application
        self.application = LoanApplication(
            borrower=self.borrower_user,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            application_type=APPLICATION_TYPES['STANDARD']
        )
        self.application.save()
        
        # Create test document
        self.document = ApplicationDocument(
            application=self.application,
            document_type=DOCUMENT_TYPES['PROOF_OF_IDENTITY'],
            file_name='id.pdf',
            file_path='documents/id.pdf',
            uploaded_by=self.uploader_user
        )
        self.document.save()
    
    def test_create_application_document(self):
        """Test creating an application document."""
        # Create a new document
        document = ApplicationDocument(
            application=self.application,
            document_type=DOCUMENT_TYPES['PROOF_OF_INCOME'],
            file_name='income.pdf',
            file_path='documents/income.pdf',
            uploaded_by=self.uploader_user
        )
        document.save()
        
        # Assert that the document is created
        self.assertIsNotNone(document.id)
        self.assertEqual(document.application, self.application)
        self.assertEqual(document.document_type, DOCUMENT_TYPES['PROOF_OF_INCOME'])
        self.assertEqual(document.file_name, 'income.pdf')
        self.assertEqual(document.file_path, 'documents/income.pdf')
        self.assertEqual(document.uploaded_by, self.uploader_user)
        self.assertEqual(document.status, 'pending')
    
    def test_application_document_str_method(self):
        """Test the string representation of an application document."""
        with mock.patch.object(self.document, 'get_document_type_display', return_value='Proof of Identity'):
            expected_str = f"Proof of Identity - Application {self.application.id}"
            self.assertEqual(str(self.document), expected_str)
    
    def test_get_download_url(self):
        """Test the get_download_url method."""
        # Mock the storage utility
        expected_url = 'https://example.com/documents/id.pdf'
        with mock.patch('utils.storage.get_presigned_url', return_value=expected_url) as mock_get_url:
            # Get the download URL
            url = self.document.get_download_url(expiry_seconds=3600)
            
            # Verify the result
            self.assertEqual(url, expected_url)
            mock_get_url.assert_called_once_with(self.document.file_path, 3600)
    
    def test_is_verified(self):
        """Test the is_verified method."""
        # Initially the document is not verified
        self.assertEqual(self.document.status, 'pending')
        self.assertFalse(self.document.is_verified())
        
        # Set status to verified
        self.document.status = 'verified'
        self.assertTrue(self.document.is_verified())
        
        # Set status to rejected
        self.document.status = 'rejected'
        self.assertFalse(self.document.is_verified())
    
    def test_verify(self):
        """Test the verify method."""
        # Initially the document is not verified
        self.assertEqual(self.document.status, 'pending')
        
        # Create a verifier user
        verifier = mock.MagicMock()
        verifier.id = '00000000-0000-0000-0000-000000000007'
        
        # Verify the document
        self.document.verify(verifier)
        
        # Check that status is now verified
        self.assertEqual(self.document.status, 'verified')


class ApplicationStatusHistoryModelTest(TestCase):
    """Test case for the ApplicationStatusHistory model."""
    
    def setUp(self):
        """Set up test data for the test case."""
        # Create test users
        self.borrower_user = mock.MagicMock()
        self.borrower_user.id = '00000000-0000-0000-0000-000000000001'
        self.borrower_user.first_name = 'John'
        self.borrower_user.last_name = 'Doe'
        
        self.status_changer = mock.MagicMock()
        self.status_changer.id = '00000000-0000-0000-0000-000000000003'
        
        # Create test borrower profile
        self.borrower_profile = mock.MagicMock()
        self.borrower_profile.user = self.borrower_user
        
        # Create test school, program, and program version
        self.school = mock.MagicMock()
        self.school.id = '00000000-0000-0000-0000-000000000004'
        self.school.name = 'Test School'
        
        self.program = mock.MagicMock()
        self.program.id = '00000000-0000-0000-0000-000000000005'
        self.program.name = 'Test Program'
        
        self.program_version = mock.MagicMock()
        self.program_version.id = '00000000-0000-0000-0000-000000000006'
        self.program_version.program = self.program
        
        # Create a test loan application
        self.application = LoanApplication(
            borrower=self.borrower_user,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            application_type=APPLICATION_TYPES['STANDARD']
        )
        self.application.save()
    
    def test_create_application_status_history(self):
        """Test creating an application status history record."""
        # Create a status history record
        history = ApplicationStatusHistory(
            application=self.application,
            previous_status=APPLICATION_STATUS['DRAFT'],
            new_status=APPLICATION_STATUS['SUBMITTED'],
            changed_by=self.status_changer,
            comments='Application submitted by borrower'
        )
        history.save()
        
        # Assert that the history record is created
        self.assertIsNotNone(history.id)
        self.assertEqual(history.application, self.application)
        self.assertEqual(history.previous_status, APPLICATION_STATUS['DRAFT'])
        self.assertEqual(history.new_status, APPLICATION_STATUS['SUBMITTED'])
        self.assertEqual(history.changed_by, self.status_changer)
        self.assertEqual(history.comments, 'Application submitted by borrower')
        self.assertIsNotNone(history.changed_at)
    
    def test_application_status_history_str_method(self):
        """Test the string representation of an application status history record."""
        history = ApplicationStatusHistory(
            application=self.application,
            previous_status=APPLICATION_STATUS['DRAFT'],
            new_status=APPLICATION_STATUS['SUBMITTED'],
            changed_by=self.status_changer
        )
        history.save()
        
        expected_str = f"Application {self.application.id}: {APPLICATION_STATUS['DRAFT']} → {APPLICATION_STATUS['SUBMITTED']}"
        self.assertEqual(str(history), expected_str)
    
    def test_save_sets_changed_at(self):
        """Test that the save method sets changed_at if not provided."""
        # Create a status history record without setting changed_at
        now = timezone.now()
        history = ApplicationStatusHistory(
            application=self.application,
            previous_status=APPLICATION_STATUS['DRAFT'],
            new_status=APPLICATION_STATUS['SUBMITTED'],
            changed_by=self.status_changer
        )
        history.save()
        
        # Verify changed_at was set automatically
        self.assertIsNotNone(history.changed_at)
        self.assertGreaterEqual(history.changed_at, now)


class ApplicationNoteModelTest(TestCase):
    """Test case for the ApplicationNote model."""
    
    def setUp(self):
        """Set up test data for the test case."""
        # Create test users
        self.borrower_user = mock.MagicMock()
        self.borrower_user.id = '00000000-0000-0000-0000-000000000001'
        self.borrower_user.first_name = 'John'
        self.borrower_user.last_name = 'Doe'
        
        self.note_creator = mock.MagicMock()
        self.note_creator.id = '00000000-0000-0000-0000-000000000003'
        
        # Create test borrower profile
        self.borrower_profile = mock.MagicMock()
        self.borrower_profile.user = self.borrower_user
        
        # Create test school, program, and program version
        self.school = mock.MagicMock()
        self.school.id = '00000000-0000-0000-0000-000000000004'
        self.school.name = 'Test School'
        
        self.program = mock.MagicMock()
        self.program.id = '00000000-0000-0000-0000-000000000005'
        self.program.name = 'Test Program'
        
        self.program_version = mock.MagicMock()
        self.program_version.id = '00000000-0000-0000-0000-000000000006'
        self.program_version.program = self.program
        
        # Create a test loan application
        self.application = LoanApplication(
            borrower=self.borrower_user,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            application_type=APPLICATION_TYPES['STANDARD']
        )
        self.application.save()
    
    def test_create_application_note(self):
        """Test creating an application note."""
        # Create a note
        note = ApplicationNote(
            application=self.application,
            note_text='This is a test note.',
            created_by=self.note_creator,
            is_internal=True
        )
        note.save()
        
        # Assert that the note is created
        self.assertIsNotNone(note.id)
        self.assertEqual(note.application, self.application)
        self.assertEqual(note.note_text, 'This is a test note.')
        self.assertEqual(note.created_by, self.note_creator)
        self.assertTrue(note.is_internal)
        self.assertIsNotNone(note.created_at)
    
    def test_application_note_str_method(self):
        """Test the string representation of an application note."""
        note = ApplicationNote(
            application=self.application,
            note_text='This is a test note that is longer than fifty characters to test truncation.',
            created_by=self.note_creator
        )
        note.save()
        
        expected_str = f"Application {self.application.id}: This is a test note that is longer than fifty characters..."
        self.assertEqual(str(note), expected_str)
    
    def test_save_sets_created_at(self):
        """Test that the save method sets created_at if not provided."""
        # Create a note without setting created_at
        now = timezone.now()
        note = ApplicationNote(
            application=self.application,
            note_text='This is a test note.',
            created_by=self.note_creator
        )
        note.save()
        
        # Verify created_at was set automatically
        self.assertIsNotNone(note.created_at)
        self.assertGreaterEqual(note.created_at, now)


class ApplicationManagerTest(TestCase):
    """Test case for the ApplicationManager custom manager."""
    
    def setUp(self):
        """Set up test data for the test case."""
        # Create test users for borrowers
        self.borrower1 = mock.MagicMock()
        self.borrower1.id = '00000000-0000-0000-0000-000000000001'
        
        self.borrower2 = mock.MagicMock()
        self.borrower2.id = '00000000-0000-0000-0000-000000000002'
        
        # Create test schools
        self.school1 = mock.MagicMock()
        self.school1.id = '00000000-0000-0000-0000-000000000003'
        
        self.school2 = mock.MagicMock()
        self.school2.id = '00000000-0000-0000-0000-000000000004'
        
        # Create test programs and versions
        self.program1 = mock.MagicMock()
        self.program1.id = '00000000-0000-0000-0000-000000000005'
        
        self.program_version1 = mock.MagicMock()
        self.program_version1.id = '00000000-0000-0000-0000-000000000006'
        self.program_version1.program = self.program1
        
        self.program2 = mock.MagicMock()
        self.program2.id = '00000000-0000-0000-0000-000000000007'
        
        self.program_version2 = mock.MagicMock()
        self.program_version2.id = '00000000-0000-0000-0000-000000000008'
        self.program_version2.program = self.program2
        
        # Create test applications with different statuses, borrowers, and schools
        # Application 1: DRAFT, borrower1, school1
        self.app1 = LoanApplication(
            borrower=self.borrower1,
            school=self.school1,
            program=self.program1,
            program_version=self.program_version1,
            application_type=APPLICATION_TYPES['STANDARD'],
            status=APPLICATION_STATUS['DRAFT']
        )
        self.app1.save()
        
        # Application 2: SUBMITTED, borrower1, school1
        self.app2 = LoanApplication(
            borrower=self.borrower1,
            school=self.school1,
            program=self.program1,
            program_version=self.program_version1,
            application_type=APPLICATION_TYPES['STANDARD'],
            status=APPLICATION_STATUS['SUBMITTED']
        )
        self.app2.save()
        
        # Application 3: IN_REVIEW, borrower2, school2
        self.app3 = LoanApplication(
            borrower=self.borrower2,
            school=self.school2,
            program=self.program2,
            program_version=self.program_version2,
            application_type=APPLICATION_TYPES['STANDARD'],
            status=APPLICATION_STATUS['IN_REVIEW']
        )
        self.app3.save()
        
        # Application 4: APPROVED, borrower2, school1
        self.app4 = LoanApplication(
            borrower=self.borrower2,
            school=self.school1,
            program=self.program1,
            program_version=self.program_version1,
            application_type=APPLICATION_TYPES['STANDARD'],
            status=APPLICATION_STATUS['APPROVED']
        )
        self.app4.save()
    
    def test_get_by_status(self):
        """Test the get_by_status method."""
        # Get applications with SUBMITTED status
        submitted_apps = LoanApplication.objects.get_by_status(APPLICATION_STATUS['SUBMITTED'])
        
        # Verify results
        self.assertEqual(submitted_apps.count(), 1)
        self.assertIn(self.app2, submitted_apps)
        
        # Get applications with IN_REVIEW status
        in_review_apps = LoanApplication.objects.get_by_status(APPLICATION_STATUS['IN_REVIEW'])
        
        # Verify results
        self.assertEqual(in_review_apps.count(), 1)
        self.assertIn(self.app3, in_review_apps)
    
    def test_get_by_borrower(self):
        """Test the get_by_borrower method."""
        # Get applications for borrower1
        borrower1_apps = LoanApplication.objects.get_by_borrower(self.borrower1)
        
        # Verify results
        self.assertEqual(borrower1_apps.count(), 2)
        self.assertIn(self.app1, borrower1_apps)
        self.assertIn(self.app2, borrower1_apps)
        
        # Get applications for borrower2
        borrower2_apps = LoanApplication.objects.get_by_borrower(self.borrower2)
        
        # Verify results
        self.assertEqual(borrower2_apps.count(), 2)
        self.assertIn(self.app3, borrower2_apps)
        self.assertIn(self.app4, borrower2_apps)
    
    def test_get_by_school(self):
        """Test the get_by_school method."""
        # Get applications for school1
        school1_apps = LoanApplication.objects.get_by_school(self.school1)
        
        # Verify results
        self.assertEqual(school1_apps.count(), 3)
        self.assertIn(self.app1, school1_apps)
        self.assertIn(self.app2, school1_apps)
        self.assertIn(self.app4, school1_apps)
        
        # Get applications for school2
        school2_apps = LoanApplication.objects.get_by_school(self.school2)
        
        # Verify results
        self.assertEqual(school2_apps.count(), 1)
        self.assertIn(self.app3, school2_apps)
    
    @mock.patch('apps.applications.constants.APPLICATION_REVIEWABLE_STATUSES', 
                [APPLICATION_STATUS['SUBMITTED'], APPLICATION_STATUS['IN_REVIEW']])
    def test_get_for_underwriting(self):
        """Test the get_for_underwriting method."""
        # Get applications for underwriting
        underwriting_apps = LoanApplication.objects.get_for_underwriting()
        
        # Verify results
        self.assertEqual(underwriting_apps.count(), 2)
        self.assertIn(self.app2, underwriting_apps)  # SUBMITTED
        self.assertIn(self.app3, underwriting_apps)  # IN_REVIEW