"""
Initialization file for the schools app test package.
This file contains shared test utilities, fixtures, and imports
used across multiple test modules in the schools app.
"""

from apps.schools.models import School, Program, ProgramVersion, SchoolContact, SchoolDocument
from django.contrib.auth import get_user_model

User = get_user_model()

# Test data dictionaries
TEST_SCHOOL_DATA = {
    'name': 'ABC School',
    'legal_name': 'ABC School of Technology, Inc.',
    'tax_id': '12-3456789',
    'address_line1': '123 Education Street',
    'address_line2': 'Suite 100',
    'city': 'Anytown',
    'state': 'CA',
    'zip_code': '90210',
    'phone': '(555) 987-6543',
    'website': 'https://www.abcschool.edu',
    'status': 'active'
}

TEST_PROGRAM_DATA = {
    'name': 'Web Development Bootcamp',
    'description': 'Intensive coding bootcamp covering front-end and back-end development technologies',
    'duration_hours': 480,
    'duration_weeks': 12,
    'status': 'active'
}

TEST_PROGRAM_VERSION_DATA = {
    'version_number': 1,
    'effective_date': '2023-05-01',
    'tuition_amount': '10000.00',
    'is_current': True
}

TEST_SCHOOL_CONTACT_DATA = {
    'first_name': 'Sarah',
    'last_name': 'Johnson',
    'title': 'Admissions Director',
    'email': 'sarah@abcschool.edu',
    'phone': '(555) 123-4567',
    'is_primary': True,
    'can_sign_documents': True
}

TEST_SCHOOL_DOCUMENT_DATA = {
    'document_type': 'accreditation',
    'file_name': 'accreditation_certificate.pdf',
    'file_path': 'schools/documents/accreditation_certificate.pdf',
    'status': 'active'
}

# Utility functions to create test instances

def create_test_school(data=None):
    """
    Creates a test School instance with default or specified data.
    
    Args:
        data (dict): Optional. Data to override default values.
        
    Returns:
        School: The created School instance.
    """
    school_data = TEST_SCHOOL_DATA.copy()
    if data:
        school_data.update(data)
    return School.objects.create(**school_data)

def create_test_program(school, data=None):
    """
    Creates a test Program instance with default or specified data.
    
    Args:
        school (School): The school to associate with the program.
        data (dict): Optional. Data to override default values.
        
    Returns:
        Program: The created Program instance.
    """
    program_data = TEST_PROGRAM_DATA.copy()
    if data:
        program_data.update(data)
    return Program.objects.create(school=school, **program_data)

def create_test_program_version(program, data=None):
    """
    Creates a test ProgramVersion instance with default or specified data.
    
    Args:
        program (Program): The program to associate with the version.
        data (dict): Optional. Data to override default values.
        
    Returns:
        ProgramVersion: The created ProgramVersion instance.
    """
    version_data = TEST_PROGRAM_VERSION_DATA.copy()
    if data:
        version_data.update(data)
    return ProgramVersion.objects.create(program=program, **version_data)

def create_test_school_contact(school, data=None):
    """
    Creates a test SchoolContact instance with default or specified data.
    
    Args:
        school (School): The school to associate with the contact.
        data (dict): Optional. Data to override default values.
        
    Returns:
        SchoolContact: The created SchoolContact instance.
    """
    contact_data = TEST_SCHOOL_CONTACT_DATA.copy()
    if data:
        contact_data.update(data)
    return SchoolContact.objects.create(school=school, **contact_data)

def create_test_school_document(school, user, data=None):
    """
    Creates a test SchoolDocument instance with default or specified data.
    
    Args:
        school (School): The school to associate with the document.
        user (User): The user who uploaded the document.
        data (dict): Optional. Data to override default values.
        
    Returns:
        SchoolDocument: The created SchoolDocument instance.
    """
    document_data = TEST_SCHOOL_DOCUMENT_DATA.copy()
    if data:
        document_data.update(data)
    return SchoolDocument.objects.create(school=school, uploaded_by=user, **document_data)

class SchoolTestMixin:
    """
    Mixin class providing utility methods for school-related tests.
    """
    
    def create_school(self, data=None):
        """
        Creates a test School instance.
        
        Args:
            data (dict): Optional. Data to override default values.
            
        Returns:
            School: The created School instance.
        """
        return create_test_school(data)
    
    def create_program(self, school, data=None):
        """
        Creates a test Program instance.
        
        Args:
            school (School): The school to associate with the program.
            data (dict): Optional. Data to override default values.
            
        Returns:
            Program: The created Program instance.
        """
        return create_test_program(school, data)
    
    def create_program_version(self, program, data=None):
        """
        Creates a test ProgramVersion instance.
        
        Args:
            program (Program): The program to associate with the version.
            data (dict): Optional. Data to override default values.
            
        Returns:
            ProgramVersion: The created ProgramVersion instance.
        """
        return create_test_program_version(program, data)
    
    def create_school_contact(self, school, data=None):
        """
        Creates a test SchoolContact instance.
        
        Args:
            school (School): The school to associate with the contact.
            data (dict): Optional. Data to override default values.
            
        Returns:
            SchoolContact: The created SchoolContact instance.
        """
        return create_test_school_contact(school, data)
    
    def create_school_document(self, school, user, data=None):
        """
        Creates a test SchoolDocument instance.
        
        Args:
            school (School): The school to associate with the document.
            user (User): The user who uploaded the document.
            data (dict): Optional. Data to override default values.
            
        Returns:
            SchoolDocument: The created SchoolDocument instance.
        """
        return create_test_school_document(school, user, data)
    
    def assert_school_data(self, school, expected_data):
        """
        Asserts that a School instance has the expected data.
        
        Args:
            school (School): The school instance to check.
            expected_data (dict): The expected data.
            
        Returns:
            None: No return value.
        """
        for key, value in expected_data.items():
            assert getattr(school, key) == value, f"School.{key} expected {value}, got {getattr(school, key)}"
    
    def assert_program_data(self, program, expected_data):
        """
        Asserts that a Program instance has the expected data.
        
        Args:
            program (Program): The program instance to check.
            expected_data (dict): The expected data.
            
        Returns:
            None: No return value.
        """
        for key, value in expected_data.items():
            assert getattr(program, key) == value, f"Program.{key} expected {value}, got {getattr(program, key)}"