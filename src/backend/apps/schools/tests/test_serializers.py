"""
Tests for the serializers in the schools app.

This module contains unit tests for all serializers in the schools app,
ensuring proper serialization, deserialization, validation, and data handling.
"""

from decimal import Decimal
from unittest.mock import mock, patch
from django.test import TestCase
from django.utils import timezone
from django.db import transaction

from apps.schools.serializers import (
    SchoolSerializer, SchoolDetailSerializer, SchoolCreateSerializer, SchoolUpdateSerializer,
    ProgramSerializer, ProgramDetailSerializer, ProgramCreateSerializer, ProgramUpdateSerializer,
    ProgramVersionSerializer, ProgramVersionCreateSerializer,
    SchoolContactSerializer, SchoolDocumentSerializer, UserSerializer, SchoolAdminSerializer
)
from apps.schools.models import School, Program, ProgramVersion, SchoolContact, SchoolDocument
from apps.users.models import SchoolAdminProfile, User
from core.exceptions import ValidationException
from core.serializers import SENSITIVE_FIELDS
from .import SchoolTestMixin, TEST_SCHOOL_DATA, TEST_PROGRAM_DATA, TEST_PROGRAM_VERSION_DATA, TEST_SCHOOL_CONTACT_DATA, TEST_SCHOOL_DOCUMENT_DATA


class TestSchoolSerializer(TestCase, SchoolTestMixin):
    """Test case for the SchoolSerializer class"""
    
    def setUp(self):
        """Set up test data"""
        self.school = self.create_school()
        self.serializer = SchoolSerializer(self.school)
        
    def test_serializer_contains_expected_fields(self):
        """Test that the serializer contains all expected fields"""
        data = self.serializer.data
        
        expected_fields = [
            'id', 'name', 'legal_name', 'address_line1', 'address_line2', 'city', 
            'state', 'zip_code', 'phone', 'website', 'status', 'created_at', 
            'updated_at', 'active_programs_count'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)
    
    def test_get_active_programs_count(self):
        """Test that get_active_programs_count returns the correct count"""
        # Create 3 active programs and 1 inactive program
        self.create_program(self.school)
        self.create_program(self.school)
        self.create_program(self.school)
        self.create_program(self.school, {'status': 'inactive'})
        
        # Mock the active programs queryset count
        with patch.object(School, 'get_active_programs') as mock_method:
            mock_method.return_value.count.return_value = 3
            count = self.serializer.get_active_programs_count()
            self.assertEqual(count, 3)
            
            # Verify the method was called on the instance
            mock_method.assert_called_once()
    
    def test_sensitive_data_masking(self):
        """Test that sensitive data is properly masked in serialized output"""
        # tax_id is a sensitive field that should be masked
        school = self.create_school({'tax_id': '12-3456789'})
        serializer = SchoolSerializer(school)
        self.assertIn('tax_id', SENSITIVE_FIELDS)
        # If tax_id is in the serialized data, it should be masked
        # Note: SchoolSerializer may or may not include tax_id based on its fields definition
        if 'tax_id' in serializer.data:
            self.assertNotEqual(serializer.data['tax_id'], '12-3456789')


class TestSchoolDetailSerializer(TestCase, SchoolTestMixin):
    """Test case for the SchoolDetailSerializer class"""
    
    def setUp(self):
        """Set up test data"""
        self.school = self.create_school()
        self.serializer = SchoolDetailSerializer(self.school)
        
    def test_serializer_contains_expected_fields(self):
        """Test that the serializer contains all expected fields"""
        data = self.serializer.data
        
        expected_fields = [
            'id', 'name', 'legal_name', 'address_line1', 'address_line2', 'city', 
            'state', 'zip_code', 'phone', 'website', 'status', 'created_at', 
            'updated_at', 'active_programs_count', 'administrators', 'active_programs'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)
    
    def test_get_administrators(self):
        """Test that get_administrators returns serialized administrator data"""
        # Create test user
        user = User.objects.create(
            email='admin@example.com',
            first_name='Admin',
            last_name='User'
        )
        
        # Create a school admin profile
        admin_profile = SchoolAdminProfile.objects.create(
            user=user,
            school=self.school,
            title='Administrator',
            department='Administration',
            is_primary_contact=True,
            can_sign_documents=True
        )
        
        # Mock the school.get_administrators method to return the admin profiles
        with patch.object(School, 'get_administrators') as mock_method:
            mock_method.return_value = [admin_profile]
            
            # Call the get_administrators method
            result = self.serializer.get_administrators(self.school)
            
            # Verify the result is a list with one item
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 1)
            
            # Verify the result contains expected fields
            admin_data = result[0]
            self.assertEqual(admin_data['id'], user.id)
            self.assertEqual(admin_data['name'], user.get_full_name())
            self.assertEqual(admin_data['email'], user.email)
            self.assertEqual(admin_data['title'], admin_profile.title)
            self.assertEqual(admin_data['is_primary_contact'], admin_profile.is_primary_contact)
            self.assertEqual(admin_data['can_sign_documents'], admin_profile.can_sign_documents)
    
    def test_get_active_programs(self):
        """Test that get_active_programs returns serialized program data"""
        # Create active programs
        program1 = self.create_program(self.school)
        program2 = self.create_program(self.school, {'name': 'Data Science'})
        
        # Create program versions
        self.create_program_version(program1)
        self.create_program_version(program2)
        
        # Mock the school.get_active_programs method to return the programs
        with patch.object(School, 'get_active_programs') as mock_method:
            mock_method.return_value = [program1, program2]
            
            # Call the get_active_programs method
            result = self.serializer.get_active_programs(self.school)
            
            # Verify the result is a list with 2 items
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)
            
            # Verify the first program data
            program_data = result[0]
            self.assertEqual(program_data['id'], str(program1.id))
            self.assertEqual(program_data['name'], program1.name)


class TestSchoolCreateSerializer(TestCase, SchoolTestMixin):
    """Test case for the SchoolCreateSerializer class"""
    
    def setUp(self):
        """Set up test data"""
        # Create test data based on TEST_SCHOOL_DATA
        self.data = TEST_SCHOOL_DATA.copy()
        
        # Add administrators
        self.user = User.objects.create(
            email='admin@example.com',
            first_name='Admin', 
            last_name='User'
        )
        self.data['administrators'] = [self.user.id]
        
        # Create the serializer with the data
        self.serializer = SchoolCreateSerializer(data=self.data)
        
    def test_validate_valid_data(self):
        """Test that validate accepts valid school data"""
        # Call validate directly
        validated_data = self.serializer.validate(self.data)
        
        # Verify the returned data matches the input data
        for key, value in self.data.items():
            self.assertEqual(validated_data.get(key), value)
    
    def test_validate_invalid_state(self):
        """Test that validate rejects invalid state code"""
        # Set an invalid state code
        invalid_data = self.data.copy()
        invalid_data['state'] = 'XX'  # Invalid state code
        
        # Create a new serializer with the invalid data
        serializer = SchoolCreateSerializer(data=invalid_data)
        
        # Validate should raise a ValidationException
        with self.assertRaises(ValidationException):
            serializer.validate(invalid_data)
    
    def test_validate_invalid_zip(self):
        """Test that validate rejects invalid zip code"""
        # Set an invalid zip code
        invalid_data = self.data.copy()
        invalid_data['zip_code'] = 'invalid-zip'
        
        # Create a new serializer with the invalid data
        serializer = SchoolCreateSerializer(data=invalid_data)
        
        # Validate should raise a ValidationException
        with self.assertRaises(ValidationException):
            serializer.validate(invalid_data)
    
    def test_validate_invalid_phone(self):
        """Test that validate rejects invalid phone number"""
        # Set an invalid phone number
        invalid_data = self.data.copy()
        invalid_data['phone'] = '555-123-4567'  # Not in (XXX) XXX-XXXX format
        
        # Create a new serializer with the invalid data
        serializer = SchoolCreateSerializer(data=invalid_data)
        
        # Validate should raise a ValidationException
        with self.assertRaises(ValidationException):
            serializer.validate(invalid_data)
    
    def test_validate_no_administrators(self):
        """Test that validate rejects data with no administrators"""
        # Create data without administrators
        invalid_data = self.data.copy()
        invalid_data.pop('administrators')
        
        # Create a new serializer with the invalid data
        serializer = SchoolCreateSerializer(data=invalid_data)
        
        # Validate should raise a ValidationException
        with self.assertRaises(ValidationException):
            serializer.validate(invalid_data)
    
    def test_create(self):
        """Test that create properly creates a school with administrators"""
        # Create validated data
        validated_data = self.data.copy()
        
        # Mock transaction.atomic
        with patch('django.db.transaction.atomic') as mock_atomic:
            # Mock School.objects.create
            with patch('apps.schools.models.School.objects.create') as mock_create_school:
                # Set up the mock to return a school instance
                mock_school = mock.MagicMock(spec=School)
                mock_create_school.return_value = mock_school
                
                # Mock SchoolAdminProfile.objects.create
                with patch('apps.users.models.SchoolAdminProfile.objects.create') as mock_create_profile:
                    # Call create method
                    school = self.serializer.create(validated_data)
                    
                    # Verify School.objects.create was called with the right data
                    expected_school_data = {
                        k: v for k, v in validated_data.items() 
                        if k != 'administrators'
                    }
                    mock_create_school.assert_called_once_with(**expected_school_data)
                    
                    # Verify SchoolAdminProfile.objects.create was called
                    mock_create_profile.assert_called()
                    
                    # Verify the method returns the created school
                    self.assertEqual(school, mock_school)


class TestSchoolUpdateSerializer(TestCase, SchoolTestMixin):
    """Test case for the SchoolUpdateSerializer class"""
    
    def setUp(self):
        """Set up test data"""
        self.school = self.create_school()
        self.data = {
            'name': 'Updated School Name',
            'phone': '(555) 123-9876',
            'status': 'inactive'
        }
        self.serializer = SchoolUpdateSerializer(self.school, data=self.data, partial=True)
    
    def test_validate_valid_data(self):
        """Test that validate accepts valid update data"""
        # Call validate directly
        validated_data = self.serializer.validate(self.data)
        
        # Verify the returned data matches the input data
        for key, value in self.data.items():
            self.assertEqual(validated_data.get(key), value)
    
    def test_validate_invalid_state(self):
        """Test that validate rejects invalid state code"""
        # Set an invalid state code
        invalid_data = self.data.copy()
        invalid_data['state'] = 'XX'  # Invalid state code
        
        # Create a new serializer with the invalid data
        serializer = SchoolUpdateSerializer(data=invalid_data)
        
        # Validate should raise a ValidationException
        with self.assertRaises(ValidationException):
            serializer.validate(invalid_data)
    
    def test_validate_invalid_zip(self):
        """Test that validate rejects invalid zip code"""
        # Set an invalid zip code
        invalid_data = self.data.copy()
        invalid_data['zip_code'] = 'invalid-zip'
        
        # Create a new serializer with the invalid data
        serializer = SchoolUpdateSerializer(data=invalid_data)
        
        # Validate should raise a ValidationException
        with self.assertRaises(ValidationException):
            serializer.validate(invalid_data)
    
    def test_validate_invalid_phone(self):
        """Test that validate rejects invalid phone number"""
        # Set an invalid phone number
        invalid_data = self.data.copy()
        invalid_data['phone'] = '555-123-4567'  # Not in (XXX) XXX-XXXX format
        
        # Create a new serializer with the invalid data
        serializer = SchoolUpdateSerializer(data=invalid_data)
        
        # Validate should raise a ValidationException
        with self.assertRaises(ValidationException):
            serializer.validate(invalid_data)
    
    def test_update(self):
        """Test that update properly updates a school instance"""
        # Create a school instance to update
        school = self.create_school()
        
        # Create validated update data
        validated_data = self.data.copy()
        
        # Call update method
        updated_school = self.serializer.update(school, validated_data)
        
        # Verify the school instance was updated with the new values
        for key, value in validated_data.items():
            self.assertEqual(getattr(updated_school, key), value)


class TestProgramSerializer(TestCase, SchoolTestMixin):
    """Test case for the ProgramSerializer class"""
    
    def setUp(self):
        """Set up test data"""
        self.school = self.create_school()
        self.program = self.create_program(self.school)
        self.serializer = ProgramSerializer(self.program)
    
    def test_serializer_contains_expected_fields(self):
        """Test that the serializer contains all expected fields"""
        data = self.serializer.data
        
        expected_fields = [
            'id', 'school', 'name', 'description', 'duration_hours', 
            'duration_weeks', 'status', 'created_at', 'updated_at', 'current_tuition'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)
    
    def test_get_current_tuition(self):
        """Test that get_current_tuition returns the correct tuition amount"""
        # Create a program version with a specific tuition amount
        version = self.create_program_version(
            self.program, 
            {'tuition_amount': Decimal('12500.00')}
        )
        
        # Mock the program.get_current_version method to return the version
        with patch.object(Program, 'get_current_version') as mock_method:
            mock_method.return_value = version
            
            # Call the get_current_tuition method
            result = self.serializer.get_current_tuition(self.program)
            
            # Verify the result matches the expected tuition amount
            self.assertEqual(result, Decimal('12500.00'))
    
    def test_get_current_tuition_no_version(self):
        """Test that get_current_tuition returns None when no current version exists"""
        # Mock the program.get_current_version method to return None
        with patch.object(Program, 'get_current_version') as mock_method:
            mock_method.return_value = None
            
            # Call the get_current_tuition method
            result = self.serializer.get_current_tuition(self.program)
            
            # Verify the result is None
            self.assertIsNone(result)


class TestProgramDetailSerializer(TestCase, SchoolTestMixin):
    """Test case for the ProgramDetailSerializer class"""
    
    def setUp(self):
        """Set up test data"""
        self.school = self.create_school()
        self.program = self.create_program(self.school)
        self.serializer = ProgramDetailSerializer(self.program)
    
    def test_serializer_contains_expected_fields(self):
        """Test that the serializer contains all expected fields"""
        data = self.serializer.data
        
        expected_fields = [
            'id', 'school', 'name', 'description', 'duration_hours', 
            'duration_weeks', 'status', 'created_at', 'updated_at', 
            'current_tuition', 'versions', 'current_version'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)
    
    def test_get_versions(self):
        """Test that get_versions returns serialized version data"""
        # Create multiple program versions
        version1 = self.create_program_version(self.program, {
            'version_number': 1,
            'is_current': False
        })
        version2 = self.create_program_version(self.program, {
            'version_number': 2,
            'is_current': True
        })
        
        # Mock the program.get_all_versions method to return the versions
        with patch.object(Program, 'get_all_versions') as mock_method:
            mock_method.return_value = [version2, version1]  # Newest first
            
            # Call the get_versions method
            result = self.serializer.get_versions(self.program)
            
            # Verify the result is a list with 2 items
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 2)
            
            # Verify the first version data
            version_data = result[0]
            self.assertEqual(version_data['id'], str(version2.id))
            self.assertEqual(version_data['version_number'], 2)
            self.assertTrue(version_data['is_current'])
    
    def test_get_current_version(self):
        """Test that get_current_version returns serialized current version data"""
        # Create a program version with is_current=True
        current_version = self.create_program_version(self.program, {
            'version_number': 1,
            'is_current': True
        })
        
        # Mock the program.get_current_version method to return the version
        with patch.object(Program, 'get_current_version') as mock_method:
            mock_method.return_value = current_version
            
            # Call the get_current_version method
            result = self.serializer.get_current_version(self.program)
            
            # Verify the result contains expected data
            self.assertEqual(result['id'], str(current_version.id))
            self.assertEqual(result['version_number'], 1)
            self.assertTrue(result['is_current'])
    
    def test_get_current_version_none(self):
        """Test that get_current_version returns None when no current version exists"""
        # Mock the program.get_current_version method to return None
        with patch.object(Program, 'get_current_version') as mock_method:
            mock_method.return_value = None
            
            # Call the get_current_version method
            result = self.serializer.get_current_version(self.program)
            
            # Verify the result is None
            self.assertIsNone(result)


class TestProgramCreateSerializer(TestCase, SchoolTestMixin):
    """Test case for the ProgramCreateSerializer class"""
    
    def setUp(self):
        """Set up test data"""
        self.school = self.create_school()
        
        # Create test data based on TEST_PROGRAM_DATA
        self.data = TEST_PROGRAM_DATA.copy()
        self.data['school'] = self.school.id
        self.data['tuition_amount'] = Decimal('10000.00')
        self.data['effective_date'] = '2023-05-01'
        
        # Create the serializer with the data
        self.serializer = ProgramCreateSerializer(data=self.data)
    
    def test_validate_valid_data(self):
        """Test that validate accepts valid program data"""
        # Call validate directly
        validated_data = self.serializer.validate(self.data)
        
        # Verify the returned data matches the input data
        for key, value in self.data.items():
            self.assertEqual(validated_data.get(key), value)
    
    def test_validate_invalid_duration_hours(self):
        """Test that validate rejects negative duration_hours"""
        # Set a negative duration_hours
        invalid_data = self.data.copy()
        invalid_data['duration_hours'] = -10
        
        # Create a new serializer with the invalid data
        serializer = ProgramCreateSerializer(data=invalid_data)
        
        # Validate should raise a ValidationException
        with self.assertRaises(ValidationException):
            serializer.validate(invalid_data)
    
    def test_validate_invalid_duration_weeks(self):
        """Test that validate rejects negative duration_weeks"""
        # Set a negative duration_weeks
        invalid_data = self.data.copy()
        invalid_data['duration_weeks'] = -2
        
        # Create a new serializer with the invalid data
        serializer = ProgramCreateSerializer(data=invalid_data)
        
        # Validate should raise a ValidationException
        with self.assertRaises(ValidationException):
            serializer.validate(invalid_data)
    
    def test_validate_invalid_tuition(self):
        """Test that validate rejects negative tuition_amount"""
        # Set a negative tuition_amount
        invalid_data = self.data.copy()
        invalid_data['tuition_amount'] = -1000
        
        # Create a new serializer with the invalid data
        serializer = ProgramCreateSerializer(data=invalid_data)
        
        # Validate should raise a ValidationException
        with self.assertRaises(ValidationException):
            serializer.validate(invalid_data)
    
    def test_validate_missing_effective_date(self):
        """Test that validate rejects data without effective_date"""
        # Create data without effective_date
        invalid_data = self.data.copy()
        invalid_data.pop('effective_date')
        
        # Create a new serializer with the invalid data
        serializer = ProgramCreateSerializer(data=invalid_data)
        
        # Validate should raise a ValidationException
        with self.assertRaises(ValidationException):
            serializer.validate(invalid_data)
    
    def test_create(self):
        """Test that create properly creates a program with initial version"""
        # Create validated data
        validated_data = self.data.copy()
        
        # Mock transaction.atomic
        with patch('django.db.transaction.atomic') as mock_atomic:
            # Mock Program.objects.create
            with patch('apps.schools.models.Program.objects.create') as mock_create_program:
                # Set up the mock to return a program instance
                mock_program = mock.MagicMock(spec=Program)
                mock_create_program.return_value = mock_program
                
                # Mock ProgramVersion.objects.create
                with patch('apps.schools.models.ProgramVersion.objects.create') as mock_create_version:
                    # Call create method
                    program = self.serializer.create(validated_data)
                    
                    # Verify Program.objects.create was called with the right data
                    expected_program_data = {
                        k: v for k, v in validated_data.items() 
                        if k not in ['tuition_amount', 'effective_date']
                    }
                    mock_create_program.assert_called_once_with(**expected_program_data)
                    
                    # Verify ProgramVersion.objects.create was called with the right data
                    mock_create_version.assert_called_once_with(
                        program=mock_program,
                        version_number=1,
                        effective_date=validated_data['effective_date'],
                        tuition_amount=validated_data['tuition_amount'],
                        is_current=True
                    )
                    
                    # Verify the method returns the created program
                    self.assertEqual(program, mock_program)


class TestProgramUpdateSerializer(TestCase, SchoolTestMixin):
    """Test case for the ProgramUpdateSerializer class"""
    
    def setUp(self):
        """Set up test data"""
        self.school = self.create_school()
        self.program = self.create_program(self.school)
        self.data = {
            'name': 'Updated Program Name',
            'duration_weeks': 16,
            'status': 'inactive'
        }
        self.serializer = ProgramUpdateSerializer(self.program, data=self.data, partial=True)
    
    def test_validate_valid_data(self):
        """Test that validate accepts valid update data"""
        # Call validate directly
        validated_data = self.serializer.validate(self.data)
        
        # Verify the returned data matches the input data
        for key, value in self.data.items():
            self.assertEqual(validated_data.get(key), value)
    
    def test_validate_invalid_duration_hours(self):
        """Test that validate rejects negative duration_hours"""
        # Set a negative duration_hours
        invalid_data = self.data.copy()
        invalid_data['duration_hours'] = -10
        
        # Create a new serializer with the invalid data
        serializer = ProgramUpdateSerializer(data=invalid_data)
        
        # Validate should raise a ValidationException
        with self.assertRaises(ValidationException):
            serializer.validate(invalid_data)
    
    def test_validate_invalid_duration_weeks(self):
        """Test that validate rejects negative duration_weeks"""
        # Set a negative duration_weeks
        invalid_data = self.data.copy()
        invalid_data['duration_weeks'] = -2
        
        # Create a new serializer with the invalid data
        serializer = ProgramUpdateSerializer(data=invalid_data)
        
        # Validate should raise a ValidationException
        with self.assertRaises(ValidationException):
            serializer.validate(invalid_data)
    
    def test_validate_invalid_tuition(self):
        """Test that validate rejects negative tuition_amount"""
        # Set a negative tuition_amount
        invalid_data = self.data.copy()
        invalid_data['tuition_amount'] = -1000
        
        # Create a new serializer with the invalid data
        serializer = ProgramUpdateSerializer(data=invalid_data)
        
        # Validate should raise a ValidationException
        with self.assertRaises(ValidationException):
            serializer.validate(invalid_data)
    
    def test_validate_tuition_without_effective_date(self):
        """Test that validate rejects tuition_amount without effective_date"""
        # Create data with tuition_amount but no effective_date
        invalid_data = self.data.copy()
        invalid_data['tuition_amount'] = 12000
        
        # Create a new serializer with the invalid data
        serializer = ProgramUpdateSerializer(data=invalid_data)
        
        # Validate should raise a ValidationException
        with self.assertRaises(ValidationException):
            serializer.validate(invalid_data)
    
    def test_update_without_tuition_change(self):
        """Test that update properly updates a program without changing tuition"""
        # Create a program instance to update
        program = self.create_program(self.school)
        
        # Create validated update data without tuition_amount
        validated_data = self.data.copy()
        
        # Call update method
        updated_program = self.serializer.update(program, validated_data)
        
        # Verify the program instance was updated with the new values
        for key, value in validated_data.items():
            self.assertEqual(getattr(updated_program, key), value)
    
    def test_update_with_tuition_change(self):
        """Test that update properly updates a program and creates a new version when tuition changes"""
        # Create a program instance to update
        program = self.create_program(self.school)
        
        # Create validated update data with tuition_amount and effective_date
        validated_data = self.data.copy()
        validated_data['tuition_amount'] = Decimal('12000.00')
        validated_data['effective_date'] = timezone.now().date()
        
        # Mock create_new_version method
        program.create_new_version = mock.MagicMock()
        
        # Mock transaction.atomic
        with patch('django.db.transaction.atomic'):
            # Call update method
            updated_program = self.serializer.update(program, validated_data)
            
            # Verify the program instance was updated with the new values
            for key, value in validated_data.items():
                if key not in ['tuition_amount', 'effective_date']:
                    self.assertEqual(getattr(updated_program, key), value)
            
            # Verify create_new_version was called with tuition_amount and effective_date
            program.create_new_version.assert_called_once_with(
                validated_data['tuition_amount'],
                validated_data['effective_date']
            )


class TestProgramVersionSerializer(TestCase, SchoolTestMixin):
    """Test case for the ProgramVersionSerializer class"""
    
    def setUp(self):
        """Set up test data"""
        self.school = self.create_school()
        self.program = self.create_program(self.school)
        self.program_version = self.create_program_version(self.program)
        self.serializer = ProgramVersionSerializer(self.program_version)
    
    def test_serializer_contains_expected_fields(self):
        """Test that the serializer contains all expected fields"""
        data = self.serializer.data
        
        expected_fields = [
            'id', 'program', 'version_number', 'effective_date', 
            'tuition_amount', 'is_current', 'created_at', 'updated_at'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)


class TestProgramVersionCreateSerializer(TestCase, SchoolTestMixin):
    """Test case for the ProgramVersionCreateSerializer class"""
    
    def setUp(self):
        """Set up test data"""
        self.school = self.create_school()
        self.program = self.create_program(self.school)
        
        # Create test data based on TEST_PROGRAM_VERSION_DATA
        self.data = TEST_PROGRAM_VERSION_DATA.copy()
        self.data['program'] = self.program.id
        
        # Create the serializer with the data
        self.serializer = ProgramVersionCreateSerializer(data=self.data)
    
    def test_validate_valid_data(self):
        """Test that validate accepts valid program version data"""
        # Set effective_date to a future date to pass validation
        future_date = (timezone.now() + timezone.timedelta(days=1)).date()
        self.data['effective_date'] = future_date.isoformat()
        
        # Call validate directly
        validated_data = self.serializer.validate(self.data)
        
        # Verify the returned data matches the input data
        for key, value in self.data.items():
            if key == 'effective_date':
                # Compare dates as strings to handle date parsing
                self.assertEqual(validated_data.get(key).isoformat(), value)
            else:
                self.assertEqual(validated_data.get(key), value)
    
    def test_validate_invalid_tuition(self):
        """Test that validate rejects negative tuition_amount"""
        # Set a negative tuition_amount
        invalid_data = self.data.copy()
        invalid_data['tuition_amount'] = -1000
        
        # Create a new serializer with the invalid data
        serializer = ProgramVersionCreateSerializer(data=invalid_data)
        
        # Validate should raise a ValidationException
        with self.assertRaises(ValidationException):
            serializer.validate(invalid_data)
    
    def test_validate_missing_effective_date(self):
        """Test that validate rejects data without effective_date"""
        # Create data without effective_date
        invalid_data = self.data.copy()
        invalid_data.pop('effective_date')
        
        # Create a new serializer with the invalid data
        serializer = ProgramVersionCreateSerializer(data=invalid_data)
        
        # Validate should raise a ValidationException
        with self.assertRaises(ValidationException):
            serializer.validate(invalid_data)
    
    def test_validate_past_effective_date(self):
        """Test that validate rejects effective_date in the past"""
        # Set an effective_date in the past
        invalid_data = self.data.copy()
        past_date = (timezone.now() - timezone.timedelta(days=1)).date()
        invalid_data['effective_date'] = past_date.isoformat()
        
        # Create a new serializer with the invalid data
        serializer = ProgramVersionCreateSerializer(data=invalid_data)
        
        # Validate should raise a ValidationException
        with self.assertRaises(ValidationException):
            serializer.validate(invalid_data)
    
    def test_create(self):
        """Test that create properly creates a new program version"""
        # Create a program instance
        program = self.program
        
        # Create validated data with program, tuition_amount, and effective_date
        future_date = (timezone.now() + timezone.timedelta(days=1)).date()
        validated_data = {
            'program': program,
            'tuition_amount': Decimal('12000.00'),
            'effective_date': future_date,
        }
        
        # Mock program.create_new_version method
        with patch.object(Program, 'create_new_version') as mock_method:
            # Set up the mock to return a new version instance
            new_version = mock.MagicMock(spec=ProgramVersion)
            mock_method.return_value = new_version
            
            # Call create method
            version = self.serializer.create(validated_data)
            
            # Verify create_new_version was called with the right data
            mock_method.assert_called_once_with(
                validated_data['tuition_amount'],
                validated_data['effective_date']
            )
            
            # Verify the method returns the created version
            self.assertEqual(version, new_version)


class TestSchoolContactSerializer(TestCase, SchoolTestMixin):
    """Test case for the SchoolContactSerializer class"""
    
    def setUp(self):
        """Set up test data"""
        self.school = self.create_school()
        self.school_contact = self.create_school_contact(self.school)
        self.serializer = SchoolContactSerializer(self.school_contact)
    
    def test_serializer_contains_expected_fields(self):
        """Test that the serializer contains all expected fields"""
        data = self.serializer.data
        
        expected_fields = [
            'id', 'school', 'first_name', 'last_name', 'full_name', 'title', 
            'email', 'phone', 'is_primary', 'can_sign_documents', 
            'created_at', 'updated_at'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)
    
    def test_validate_valid_data(self):
        """Test that validate accepts valid school contact data"""
        # Create test data based on TEST_SCHOOL_CONTACT_DATA
        data = TEST_SCHOOL_CONTACT_DATA.copy()
        data['school'] = self.school.id
        
        # Create the serializer with the data
        serializer = SchoolContactSerializer(data=data)
        
        # Call validate directly
        validated_data = serializer.validate(data)
        
        # Verify the returned data matches the input data
        for key, value in data.items():
            self.assertEqual(validated_data.get(key), value)
    
    def test_validate_invalid_phone(self):
        """Test that validate rejects invalid phone number"""
        # Set an invalid phone number
        invalid_data = TEST_SCHOOL_CONTACT_DATA.copy()
        invalid_data['school'] = self.school.id
        invalid_data['phone'] = '555-123-4567'  # Not in (XXX) XXX-XXXX format
        
        # Create a new serializer with the invalid data
        serializer = SchoolContactSerializer(data=invalid_data)
        
        # Validate should raise a ValidationException
        with self.assertRaises(ValidationException):
            serializer.validate(invalid_data)
    
    def test_to_representation(self):
        """Test that to_representation adds full_name field"""
        # Mock the contact's get_full_name method
        with patch.object(SchoolContact, 'get_full_name') as mock_method:
            mock_method.return_value = 'Sarah Johnson'
            
            # Call to_representation directly
            result = self.serializer.to_representation(self.school_contact)
            
            # Verify the result contains the full_name field with the expected value
            self.assertIn('full_name', result)
            self.assertEqual(result['full_name'], 'Sarah Johnson')
            
            # Verify the original fields are still present
            self.assertEqual(result['id'], str(self.school_contact.id))
            self.assertEqual(result['first_name'], self.school_contact.first_name)
            self.assertEqual(result['last_name'], self.school_contact.last_name)


class TestSchoolDocumentSerializer(TestCase, SchoolTestMixin):
    """Test case for the SchoolDocumentSerializer class"""
    
    def setUp(self):
        """Set up test data"""
        # Create a test user for document uploads
        self.user = User.objects.create(
            email='user@example.com',
            first_name='Test',
            last_name='User'
        )
        
        self.school = self.create_school()
        self.school_document = self.create_school_document(self.school, self.user)
        self.serializer = SchoolDocumentSerializer(self.school_document)
    
    def test_serializer_contains_expected_fields(self):
        """Test that the serializer contains all expected fields"""
        data = self.serializer.data
        
        expected_fields = [
            'id', 'school', 'document_type', 'file_name', 'file_path',
            'uploaded_at', 'uploaded_by', 'status', 'download_url',
            'created_at', 'updated_at'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)
    
    def test_get_download_url(self):
        """Test that get_download_url returns the correct URL"""
        # Mock the document's get_download_url method
        with patch.object(SchoolDocument, 'get_download_url') as mock_method:
            mock_method.return_value = 'https://example.com/download/document'
            
            # Call get_download_url on the serializer
            result = self.serializer.get_download_url(self.school_document)
            
            # Verify the result matches the expected URL
            self.assertEqual(result, 'https://example.com/download/document')
            
            # Verify the mock was called with default expiry_seconds
            mock_method.assert_called_once()
    
    def test_get_uploaded_by(self):
        """Test that get_uploaded_by returns the correct user information"""
        # Set up a document with a specific uploader
        document = self.school_document
        document.uploaded_by = self.user
        
        # Call get_uploaded_by on the serializer
        result = self.serializer.get_uploaded_by(document)
        
        # Verify the result contains the expected user information
        self.assertEqual(result['id'], self.user.id)
        self.assertEqual(result['name'], self.user.get_full_name())
        self.assertEqual(result['email'], self.user.email)


class TestUserSerializer(TestCase):
    """Test case for the UserSerializer class used in school-related contexts"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create(
            email='user@example.com',
            first_name='Test',
            last_name='User',
            phone='(555) 123-4567',
            user_type='borrower'
        )
        self.serializer = UserSerializer(self.user)
    
    def test_serializer_contains_expected_fields(self):
        """Test that the serializer contains all expected fields"""
        data = self.serializer.data
        
        expected_fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name', 'phone', 'user_type'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)
    
    def test_get_full_name(self):
        """Test that get_full_name returns the correct full name"""
        # Mock the user's get_full_name method
        with patch.object(User, 'get_full_name') as mock_method:
            mock_method.return_value = 'Test User'
            
            # Call get_full_name on the serializer
            result = self.serializer.get_full_name(self.user)
            
            # Verify the result matches the expected name
            self.assertEqual(result, 'Test User')


class TestSchoolAdminSerializer(TestCase, SchoolTestMixin):
    """Test case for the SchoolAdminSerializer class"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create(
            email='admin@example.com',
            first_name='Admin',
            last_name='User'
        )
        
        self.school = self.create_school()
        
        # Create SchoolAdminProfile
        self.admin_profile = SchoolAdminProfile.objects.create(
            user=self.user,
            school=self.school,
            title='Administrator',
            department='Administration',
            is_primary_contact=True,
            can_sign_documents=True
        )
        
        self.serializer = SchoolAdminSerializer(self.admin_profile)
    
    def test_serializer_contains_expected_fields(self):
        """Test that the serializer contains all expected fields"""
        data = self.serializer.data
        
        expected_fields = [
            'id', 'user', 'school', 'title', 'department', 
            'is_primary_contact', 'can_sign_documents',
            'user_details', 'created_at', 'updated_at'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)
    
    def test_get_user_details(self):
        """Test that get_user_details returns the correct user information"""
        # Call get_user_details on the serializer
        result = self.serializer.get_user_details(self.admin_profile)
        
        # Verify the result is the serialized user data
        self.assertEqual(result['id'], str(self.user.id))
        self.assertEqual(result['email'], self.user.email)
        self.assertEqual(result['first_name'], self.user.first_name)
        self.assertEqual(result['last_name'], self.user.last_name)
        self.assertEqual(result['full_name'], self.user.get_full_name())