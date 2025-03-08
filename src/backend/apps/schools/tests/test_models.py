"""
Unit tests for the School, Program, ProgramVersion, SchoolDocument, and SchoolContact models 
in the loan management system.
"""

from django.test import TestCase
from unittest.mock import mock, patch
from django.utils import timezone
from decimal import Decimal

from django.contrib.auth import get_user_model

from apps.schools.models import (
    School, Program, ProgramVersion, SchoolDocument, SchoolContact,
    SCHOOL_STATUS_CHOICES, PROGRAM_STATUS_CHOICES, DOCUMENT_TYPE_CHOICES
)
from apps.schools.tests import (
    SchoolTestMixin, TEST_SCHOOL_DATA, TEST_PROGRAM_DATA, 
    TEST_PROGRAM_VERSION_DATA, TEST_SCHOOL_CONTACT_DATA, TEST_SCHOOL_DOCUMENT_DATA
)
from utils.validators import ValidationError
from utils.constants import US_STATES


class TestSchoolModel(TestCase, SchoolTestMixin):
    """Test case for the School model"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.school = self.create_school()
    
    def test_school_creation(self):
        """Test that a school can be created with valid data"""
        self.assertTrue(isinstance(self.school, School))
        self.assertEqual(self.school.name, TEST_SCHOOL_DATA['name'])
        self.assertEqual(self.school.legal_name, TEST_SCHOOL_DATA['legal_name'])
        self.assertEqual(self.school.tax_id, TEST_SCHOOL_DATA['tax_id'])
        self.assertEqual(self.school.address_line1, TEST_SCHOOL_DATA['address_line1'])
        self.assertEqual(self.school.address_line2, TEST_SCHOOL_DATA['address_line2'])
        self.assertEqual(self.school.city, TEST_SCHOOL_DATA['city'])
        self.assertEqual(self.school.state, TEST_SCHOOL_DATA['state'])
        self.assertEqual(self.school.zip_code, TEST_SCHOOL_DATA['zip_code'])
        self.assertEqual(self.school.phone, TEST_SCHOOL_DATA['phone'])
        self.assertEqual(self.school.website, TEST_SCHOOL_DATA['website'])
        self.assertEqual(self.school.status, TEST_SCHOOL_DATA['status'])
    
    def test_school_string_representation(self):
        """Test the string representation of a School instance"""
        self.assertEqual(str(self.school), self.school.name)
    
    def test_school_clean_method_valid_data(self):
        """Test that the clean method validates valid school data"""
        try:
            self.school.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly with valid data")
    
    def test_school_clean_method_invalid_state(self):
        """Test that the clean method validates state code"""
        school = self.create_school({'state': 'XX'})  # Invalid state code
        with self.assertRaises(ValidationError):
            school.clean()
    
    def test_school_clean_method_invalid_zip(self):
        """Test that the clean method validates zip code"""
        school = self.create_school({'zip_code': 'invalid'})  # Invalid zip code
        with self.assertRaises(ValidationError):
            school.clean()
    
    def test_school_clean_method_invalid_phone(self):
        """Test that the clean method validates phone number"""
        school = self.create_school({'phone': '555-1234'})  # Invalid phone format
        with self.assertRaises(ValidationError):
            school.clean()
    
    def test_get_active_programs(self):
        """Test the get_active_programs method"""
        # Create active and inactive programs
        active_program1 = self.create_program(self.school)
        active_program2 = self.create_program(self.school)
        inactive_program = self.create_program(self.school, {'status': 'inactive'})
        
        # Get active programs
        active_programs = self.school.get_active_programs()
        
        # Assert that only active programs are returned
        self.assertEqual(active_programs.count(), 2)
        self.assertIn(active_program1, active_programs)
        self.assertIn(active_program2, active_programs)
        self.assertNotIn(inactive_program, active_programs)
    
    def test_get_administrators(self):
        """Test the get_administrators method"""
        # Mock the SchoolAdminProfile model and queryset
        with patch('apps.users.models.SchoolAdminProfile.objects.filter') as mock_filter:
            mock_queryset = mock.MagicMock()
            mock_filter.return_value = mock_queryset
            
            # Call the method
            admins = self.school.get_administrators()
            
            # Assert that the filter method was called with the school
            mock_filter.assert_called_once_with(school=self.school)
            # Assert that the returned value is the mock queryset
            self.assertEqual(admins, mock_queryset)
    
    def test_get_primary_contact(self):
        """Test the get_primary_contact method"""
        # Create primary and non-primary contacts
        primary_contact = self.create_school_contact(self.school)
        non_primary_contact = self.create_school_contact(
            self.school, {'is_primary': False, 'email': 'other@example.com'}
        )
        
        # Get the primary contact
        contact = self.school.get_primary_contact()
        
        # Assert that the primary contact is returned
        self.assertEqual(contact, primary_contact)
        self.assertTrue(contact.is_primary)
    
    def test_get_full_address(self):
        """Test the get_full_address method"""
        # Test with address_line2
        full_address = self.school.get_full_address()
        expected_address = f"{self.school.address_line1}, {self.school.address_line2}, {self.school.city}, {self.school.state} {self.school.zip_code}"
        self.assertEqual(full_address, expected_address)
        
        # Test without address_line2
        school_no_address2 = self.create_school({'address_line2': None})
        full_address = school_no_address2.get_full_address()
        expected_address = f"{school_no_address2.address_line1}, {school_no_address2.city}, {school_no_address2.state} {school_no_address2.zip_code}"
        self.assertEqual(full_address, expected_address)
    
    def test_get_applications(self):
        """Test the get_applications method"""
        # Mock the LoanApplication model and queryset
        with patch('apps.applications.models.LoanApplication.objects.filter') as mock_filter:
            mock_queryset = mock.MagicMock()
            mock_filter.return_value = mock_queryset
            
            # Call the method
            applications = self.school.get_applications()
            
            # Assert that the filter method was called with the school
            mock_filter.assert_called_once_with(school=self.school)
            # Assert that the returned value is the mock queryset
            self.assertEqual(applications, mock_queryset)

    def test_school_soft_delete(self):
        """Test that soft deleting a school works correctly"""
        # Soft delete the school
        self.school.delete()
        
        # Check that is_deleted is True and deleted_at is set
        self.assertTrue(self.school.is_deleted)
        self.assertIsNotNone(self.school.deleted_at)
        
        # Check that the school is not in the default queryset
        self.assertFalse(School.objects.filter(id=self.school.id).exists())
        
        # Check that the school is still in the all_objects queryset
        self.assertTrue(School.all_objects.filter(id=self.school.id).exists())


class TestProgramModel(TestCase, SchoolTestMixin):
    """Test case for the Program model"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        self.school = self.create_school()
        self.program = self.create_program(self.school)
    
    def test_program_creation(self):
        """Test that a program can be created with valid data"""
        self.assertTrue(isinstance(self.program, Program))
        self.assertEqual(self.program.name, TEST_PROGRAM_DATA['name'])
        self.assertEqual(self.program.description, TEST_PROGRAM_DATA['description'])
        self.assertEqual(self.program.duration_hours, TEST_PROGRAM_DATA['duration_hours'])
        self.assertEqual(self.program.duration_weeks, TEST_PROGRAM_DATA['duration_weeks'])
        self.assertEqual(self.program.status, TEST_PROGRAM_DATA['status'])
        self.assertEqual(self.program.school, self.school)
    
    def test_program_string_representation(self):
        """Test the string representation of a Program instance"""
        expected_str = f"{self.program.name} - {self.school.name}"
        self.assertEqual(str(self.program), expected_str)
    
    def test_program_clean_method_valid_data(self):
        """Test that the clean method validates valid program data"""
        try:
            self.program.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly with valid data")
    
    def test_program_clean_method_invalid_duration_hours(self):
        """Test that the clean method validates duration_hours"""
        program = self.create_program(self.school, {'duration_hours': -10})  # Invalid hours
        with self.assertRaises(ValidationError):
            program.clean()
    
    def test_program_clean_method_invalid_duration_weeks(self):
        """Test that the clean method validates duration_weeks"""
        program = self.create_program(self.school, {'duration_weeks': -2})  # Invalid weeks
        with self.assertRaises(ValidationError):
            program.clean()
    
    def test_get_current_version(self):
        """Test the get_current_version method"""
        # Create a program version with is_current=True
        version = self.create_program_version(self.program)
        
        # Get the current version
        current_version = self.program.get_current_version()
        
        # Assert that the correct version is returned
        self.assertEqual(current_version, version)
        self.assertTrue(current_version.is_current)
    
    def test_get_all_versions(self):
        """Test the get_all_versions method"""
        # Create multiple program versions
        version1 = self.create_program_version(self.program)
        version2 = self.create_program_version(
            self.program, 
            {'version_number': 2, 'effective_date': '2023-06-01', 'is_current': False}
        )
        version3 = self.create_program_version(
            self.program, 
            {'version_number': 3, 'effective_date': '2023-07-01', 'is_current': False}
        )
        
        # Get all versions
        versions = self.program.get_all_versions()
        
        # Assert that all versions are returned and ordered correctly
        self.assertEqual(versions.count(), 3)
        self.assertEqual(list(versions), [version3, version2, version1])
    
    def test_get_current_tuition(self):
        """Test the get_current_tuition method"""
        # Create a program version with a specific tuition amount
        version = self.create_program_version(self.program)
        
        # Get current tuition
        tuition = self.program.get_current_tuition()
        
        # Assert that the correct tuition amount is returned
        self.assertEqual(tuition, Decimal(TEST_PROGRAM_VERSION_DATA['tuition_amount']))
        
        # Test with no current version
        program_no_version = self.create_program(self.school, {'name': 'No Version Program'})
        self.assertIsNone(program_no_version.get_current_tuition())
    
    def test_create_new_version(self):
        """Test the create_new_version method"""
        # Create an initial version
        initial_version = self.create_program_version(self.program)
        
        # Create a new version with different tuition
        new_tuition = Decimal('12000.00')
        effective_date = timezone.now().date()
        new_version = self.program.create_new_version(new_tuition, effective_date)
        
        # Assert that the new version is created correctly
        self.assertTrue(isinstance(new_version, ProgramVersion))
        self.assertEqual(new_version.tuition_amount, new_tuition)
        self.assertEqual(new_version.effective_date, effective_date)
        self.assertEqual(new_version.version_number, initial_version.version_number + 1)
        self.assertTrue(new_version.is_current)
        
        # Refresh the initial version from the database
        initial_version.refresh_from_db()
        self.assertFalse(initial_version.is_current)
    
    def test_program_soft_delete(self):
        """Test that soft deleting a program works correctly"""
        # Soft delete the program
        self.program.delete()
        
        # Check that is_deleted is True and deleted_at is set
        self.assertTrue(self.program.is_deleted)
        self.assertIsNotNone(self.program.deleted_at)
        
        # Check that the program is not in the default queryset
        self.assertFalse(Program.objects.filter(id=self.program.id).exists())
        
        # Check that the program is still in the all_objects queryset
        self.assertTrue(Program.all_objects.filter(id=self.program.id).exists())


class TestProgramVersionModel(TestCase, SchoolTestMixin):
    """Test case for the ProgramVersion model"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        self.school = self.create_school()
        self.program = self.create_program(self.school)
        self.program_version = self.create_program_version(self.program)
    
    def test_program_version_creation(self):
        """Test that a program version can be created with valid data"""
        self.assertTrue(isinstance(self.program_version, ProgramVersion))
        self.assertEqual(self.program_version.version_number, TEST_PROGRAM_VERSION_DATA['version_number'])
        self.assertEqual(str(self.program_version.effective_date), TEST_PROGRAM_VERSION_DATA['effective_date'])
        self.assertEqual(self.program_version.tuition_amount, Decimal(TEST_PROGRAM_VERSION_DATA['tuition_amount']))
        self.assertEqual(self.program_version.is_current, TEST_PROGRAM_VERSION_DATA['is_current'])
        self.assertEqual(self.program_version.program, self.program)
    
    def test_program_version_string_representation(self):
        """Test the string representation of a ProgramVersion instance"""
        expected_str = f"{self.program.name} v{self.program_version.version_number} - ${self.program_version.tuition_amount}"
        self.assertEqual(str(self.program_version), expected_str)
    
    def test_program_version_clean_method_valid_data(self):
        """Test that the clean method validates valid program version data"""
        try:
            self.program_version.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly with valid data")
    
    def test_program_version_clean_method_invalid_tuition(self):
        """Test that the clean method validates tuition_amount"""
        program_version = self.create_program_version(
            self.program, 
            {'tuition_amount': Decimal('-5000.00'), 'is_current': False}
        )  # Invalid tuition
        with self.assertRaises(ValidationError):
            program_version.clean()
    
    def test_program_version_save_method_current_version(self):
        """Test that the save method handles is_current flag correctly"""
        # Create a program
        program = self.create_program(self.school, {'name': 'New Program'})
        
        # Create an initial version with is_current=True
        version1 = self.create_program_version(program)
        self.assertTrue(version1.is_current)
        
        # Create a second version with is_current=True
        version2 = self.create_program_version(
            program, 
            {'version_number': 2, 'effective_date': '2023-06-01'}
        )
        
        # Refresh version1 from the database
        version1.refresh_from_db()
        
        # Assert that version1 is no longer current and version2 is current
        self.assertFalse(version1.is_current)
        self.assertTrue(version2.is_current)
    
    def test_program_version_soft_delete(self):
        """Test that soft deleting a program version works correctly"""
        # Soft delete the program version
        self.program_version.delete()
        
        # Check that is_deleted is True and deleted_at is set
        self.assertTrue(self.program_version.is_deleted)
        self.assertIsNotNone(self.program_version.deleted_at)
        
        # Check that the program version is not in the default queryset
        self.assertFalse(ProgramVersion.objects.filter(id=self.program_version.id).exists())
        
        # Check that the program version is still in the all_objects queryset
        self.assertTrue(ProgramVersion.all_objects.filter(id=self.program_version.id).exists())


class TestSchoolDocumentModel(TestCase, SchoolTestMixin):
    """Test case for the SchoolDocument model"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.school = self.create_school()
        self.document = self.create_school_document(self.school, self.user)
    
    def test_school_document_creation(self):
        """Test that a school document can be created with valid data"""
        self.assertTrue(isinstance(self.document, SchoolDocument))
        self.assertEqual(self.document.document_type, TEST_SCHOOL_DOCUMENT_DATA['document_type'])
        self.assertEqual(self.document.file_name, TEST_SCHOOL_DOCUMENT_DATA['file_name'])
        self.assertEqual(self.document.file_path, TEST_SCHOOL_DOCUMENT_DATA['file_path'])
        self.assertEqual(self.document.status, TEST_SCHOOL_DOCUMENT_DATA['status'])
        self.assertEqual(self.document.school, self.school)
        self.assertEqual(self.document.uploaded_by, self.user)
    
    def test_school_document_string_representation(self):
        """Test the string representation of a SchoolDocument instance"""
        expected_str = f"{self.document.get_document_type_display()} - {self.school.name}"
        self.assertEqual(str(self.document), expected_str)
    
    def test_get_download_url(self):
        """Test the get_download_url method"""
        # Mock the storage utility
        with patch('utils.storage.get_presigned_url') as mock_get_url:
            mock_url = "https://example.com/document.pdf"
            mock_get_url.return_value = mock_url
            
            # Call the method
            url = self.document.get_download_url(expiry_seconds=3600)
            
            # Assert that the storage utility was called correctly
            mock_get_url.assert_called_once_with(self.document.file_path, 3600)
            # Assert that the method returns the expected URL
            self.assertEqual(url, mock_url)
    
    def test_school_document_soft_delete(self):
        """Test that soft deleting a school document works correctly"""
        # Soft delete the document
        self.document.delete()
        
        # Check that is_deleted is True and deleted_at is set
        self.assertTrue(self.document.is_deleted)
        self.assertIsNotNone(self.document.deleted_at)
        
        # Check that the document is not in the default queryset
        self.assertFalse(SchoolDocument.objects.filter(id=self.document.id).exists())
        
        # Check that the document is still in the all_objects queryset
        self.assertTrue(SchoolDocument.all_objects.filter(id=self.document.id).exists())


class TestSchoolContactModel(TestCase, SchoolTestMixin):
    """Test case for the SchoolContact model"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        self.school = self.create_school()
        self.contact = self.create_school_contact(self.school)
    
    def test_school_contact_creation(self):
        """Test that a school contact can be created with valid data"""
        self.assertTrue(isinstance(self.contact, SchoolContact))
        self.assertEqual(self.contact.first_name, TEST_SCHOOL_CONTACT_DATA['first_name'])
        self.assertEqual(self.contact.last_name, TEST_SCHOOL_CONTACT_DATA['last_name'])
        self.assertEqual(self.contact.title, TEST_SCHOOL_CONTACT_DATA['title'])
        self.assertEqual(self.contact.email, TEST_SCHOOL_CONTACT_DATA['email'])
        self.assertEqual(self.contact.phone, TEST_SCHOOL_CONTACT_DATA['phone'])
        self.assertEqual(self.contact.is_primary, TEST_SCHOOL_CONTACT_DATA['is_primary'])
        self.assertEqual(self.contact.can_sign_documents, TEST_SCHOOL_CONTACT_DATA['can_sign_documents'])
        self.assertEqual(self.contact.school, self.school)
    
    def test_school_contact_string_representation(self):
        """Test the string representation of a SchoolContact instance"""
        expected_str = f"{self.contact.get_full_name()} - {self.school.name}"
        self.assertEqual(str(self.contact), expected_str)
    
    def test_school_contact_clean_method_valid_data(self):
        """Test that the clean method validates valid school contact data"""
        try:
            self.contact.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly with valid data")
    
    def test_school_contact_clean_method_invalid_phone(self):
        """Test that the clean method validates phone number"""
        contact = self.create_school_contact(self.school, {'phone': '555-1234'})  # Invalid phone format
        with self.assertRaises(ValidationError):
            contact.clean()
    
    def test_get_full_name(self):
        """Test the get_full_name method"""
        full_name = self.contact.get_full_name()
        expected_name = f"{self.contact.first_name} {self.contact.last_name}"
        self.assertEqual(full_name, expected_name)
    
    def test_save_method_primary_contact(self):
        """Test that the save method handles primary contact logic correctly"""
        # Create a school
        school = self.create_school({'name': 'Another School'})
        
        # Create an initial contact with is_primary=True
        contact1 = self.create_school_contact(school)
        self.assertTrue(contact1.is_primary)
        
        # Create a second contact with is_primary=True
        contact2 = self.create_school_contact(
            school, 
            {'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com'}
        )
        
        # Refresh contact1 from the database
        contact1.refresh_from_db()
        
        # Assert that contact1 is no longer primary and contact2 is primary
        self.assertFalse(contact1.is_primary)
        self.assertTrue(contact2.is_primary)
        
        # Create a contact for a different school with is_primary=True
        other_school = self.create_school({'name': 'Other School'})
        other_contact = self.create_school_contact(
            other_school, 
            {'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane@example.com'}
        )
        
        # Refresh contact2 from the database
        contact2.refresh_from_db()
        
        # Assert that contact2 is still primary (not affected by other school's contact)
        self.assertTrue(contact2.is_primary)
        # And the other school's contact is also primary
        self.assertTrue(other_contact.is_primary)
    
    def test_school_contact_manager_get_primary_contacts(self):
        """Test the SchoolContactManager.get_primary_contacts method"""
        # Create primary and non-primary contacts
        primary_contact1 = self.contact  # from setUp (is_primary=True)
        non_primary_contact = self.create_school_contact(
            self.school, 
            {'is_primary': False, 'email': 'nonprimary@example.com'}
        )
        
        # Create another school with a primary contact
        other_school = self.create_school({'name': 'Other School'})
        primary_contact2 = self.create_school_contact(other_school)
        
        # Get primary contacts
        primary_contacts = SchoolContact.objects.get_primary_contacts()
        
        # Assert that only primary contacts are returned
        self.assertEqual(primary_contacts.count(), 2)
        self.assertIn(primary_contact1, primary_contacts)
        self.assertIn(primary_contact2, primary_contacts)
        self.assertNotIn(non_primary_contact, primary_contacts)
    
    def test_school_contact_manager_get_signers(self):
        """Test the SchoolContactManager.get_signers method"""
        # Create contacts that can and cannot sign documents
        signer1 = self.contact  # from setUp (can_sign_documents=True)
        non_signer = self.create_school_contact(
            self.school, 
            {'can_sign_documents': False, 'email': 'nonsigner@example.com'}
        )
        
        # Create another school with a signer
        other_school = self.create_school({'name': 'Other School'})
        signer2 = self.create_school_contact(other_school)
        
        # Get signers
        signers = SchoolContact.objects.get_signers()
        
        # Assert that only signers are returned
        self.assertEqual(signers.count(), 2)
        self.assertIn(signer1, signers)
        self.assertIn(signer2, signers)
        self.assertNotIn(non_signer, signers)
    
    def test_school_contact_soft_delete(self):
        """Test that soft deleting a school contact works correctly"""
        # Soft delete the contact
        self.contact.delete()
        
        # Check that is_deleted is True and deleted_at is set
        self.assertTrue(self.contact.is_deleted)
        self.assertIsNotNone(self.contact.deleted_at)
        
        # Check that the contact is not in the default queryset
        self.assertFalse(SchoolContact.objects.filter(id=self.contact.id).exists())
        
        # Check that the contact is still in the all_objects queryset
        self.assertTrue(SchoolContact.all_objects.filter(id=self.contact.id).exists())