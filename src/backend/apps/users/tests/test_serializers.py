"""
Unit tests for user serializers in the loan management system.

These tests verify the functionality of serializers related to users, profiles,
roles, and permissions to ensure proper data validation, transformation, and
security handling.
"""

import uuid
import datetime
from decimal import Decimal
from unittest.mock import patch, mock
from django.test import TestCase
from django.utils import timezone

# Import serializers
from apps.users.serializers import (
    UserSerializer, UserDetailSerializer, UserCreateSerializer, UserUpdateSerializer,
    BorrowerProfileSerializer, EmploymentInfoSerializer, SchoolAdminProfileSerializer,
    InternalUserProfileSerializer, RoleSerializer, PermissionSerializer, UserRoleSerializer,
    RolePermissionSerializer, PasswordChangeSerializer
)

# Import models
from apps.users.models import (
    User, BorrowerProfile, EmploymentInfo, SchoolAdminProfile,
    InternalUserProfile, Role, Permission, UserRole, RolePermission
)
from apps.authentication.models import Auth0User

# Import exceptions and constants
from core.exceptions import ValidationException
from utils.constants import (
    USER_TYPES, EMPLOYMENT_TYPES, HOUSING_STATUS, CITIZENSHIP_STATUS, US_STATES
)
from core.serializers import SENSITIVE_FIELDS


class TestUserSerializer(TestCase):
    """Test case for the UserSerializer class"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create an Auth0User instance for testing
        self.auth0_user = Auth0User.objects.create(
            auth0_id='auth0|123456789',
            email='test@example.com',
            email_verified=True
        )
        
        # Create a User instance linked to the Auth0User
        self.user = User.objects.create(
            auth0_user=self.auth0_user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            phone='(555) 123-4567',
            user_type=USER_TYPES['BORROWER']
        )
        
        # Create the UserSerializer instance with the User
        self.serializer = UserSerializer(instance=self.user)
    
    def test_serializer_contains_expected_fields(self):
        """Test that the serializer contains all expected fields"""
        data = self.serializer.data
        
        # Assert that the data contains expected fields
        self.assertIn('id', data)
        self.assertIn('first_name', data)
        self.assertIn('last_name', data)
        self.assertIn('email', data)
        self.assertIn('phone', data)
        self.assertIn('user_type', data)
        self.assertIn('is_active', data)
        
        # Check field values
        self.assertEqual(data['first_name'], 'Test')
        self.assertEqual(data['last_name'], 'User')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['phone'], '(555) 123-4567')
        self.assertEqual(data['user_type'], USER_TYPES['BORROWER'])
        self.assertTrue(data['is_active'])
    
    def test_get_profile_type_borrower(self):
        """Test that get_profile_type returns 'borrower' for borrower users"""
        # Set user_type to borrower
        self.user.user_type = USER_TYPES['BORROWER']
        self.user.save()
        
        # Get the profile type
        profile_type = self.serializer.get_profile_type(self.user)
        
        # Assert that the profile type is 'borrower'
        self.assertEqual(profile_type, 'borrower')
    
    def test_get_profile_type_school_admin(self):
        """Test that get_profile_type returns 'school_admin' for school admin users"""
        # Set user_type to school_admin
        self.user.user_type = USER_TYPES['SCHOOL_ADMIN']
        self.user.save()
        
        # Get the profile type
        profile_type = self.serializer.get_profile_type(self.user)
        
        # Assert that the profile type is 'school_admin'
        self.assertEqual(profile_type, 'school_admin')
    
    def test_get_profile_type_internal(self):
        """Test that get_profile_type returns 'internal' for internal users"""
        # Set user_type to underwriter (an internal user type)
        self.user.user_type = USER_TYPES['UNDERWRITER']
        self.user.save()
        
        # Get the profile type
        profile_type = self.serializer.get_profile_type(self.user)
        
        # Assert that the profile type is 'internal'
        self.assertEqual(profile_type, 'internal')


class TestUserDetailSerializer(TestCase):
    """Test case for the UserDetailSerializer class"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create an Auth0User instance for testing
        self.auth0_user = Auth0User.objects.create(
            auth0_id='auth0|123456789',
            email='test@example.com',
            email_verified=True
        )
        
        # Create a User instance linked to the Auth0User
        self.user = User.objects.create(
            auth0_user=self.auth0_user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            phone='(555) 123-4567',
            user_type=USER_TYPES['BORROWER']
        )
        
        # Create the UserDetailSerializer instance with the User
        self.serializer = UserDetailSerializer(instance=self.user)
    
    def test_serializer_contains_expected_fields(self):
        """Test that the serializer contains all expected fields"""
        data = self.serializer.data
        
        # Assert that the data contains expected fields
        self.assertIn('id', data)
        self.assertIn('first_name', data)
        self.assertIn('last_name', data)
        self.assertIn('email', data)
        self.assertIn('phone', data)
        self.assertIn('user_type', data)
        self.assertIn('is_active', data)
    
    def test_to_representation_with_borrower_profile(self):
        """Test that to_representation includes borrower profile data"""
        # Set user_type to borrower
        self.user.user_type = USER_TYPES['BORROWER']
        self.user.save()
        
        # Create a BorrowerProfile for the User
        borrower_profile = BorrowerProfile.objects.create(
            user=self.user,
            ssn='123-45-6789',
            dob=timezone.now().date() - datetime.timedelta(days=365*30),  # 30 years ago
            citizenship_status=CITIZENSHIP_STATUS['US_CITIZEN'],
            address_line1='123 Main St',
            city='Anytown',
            state='CA',
            zip_code='12345',
            housing_status=HOUSING_STATUS['RENT'],
            housing_payment=Decimal('1500.00')
        )
        
        # Mock the get_profile method to return the borrower profile
        with patch.object(User, 'get_profile', return_value=borrower_profile):
            # Call to_representation
            representation = self.serializer.to_representation(self.user)
            
            # Assert that the representation contains borrower profile data
            self.assertIn('borrower_profile', representation)
            self.assertEqual(representation['borrower_profile']['address_line1'], '123 Main St')
            self.assertEqual(representation['borrower_profile']['city'], 'Anytown')
    
    def test_to_representation_with_school_admin_profile(self):
        """Test that to_representation includes school admin profile data"""
        # Set user_type to school_admin
        self.user.user_type = USER_TYPES['SCHOOL_ADMIN']
        self.user.save()
        
        # Create a mock School
        school_id = uuid.uuid4()
        
        # Create a SchoolAdminProfile for the User
        school_admin_profile = SchoolAdminProfile.objects.create(
            user=self.user,
            school_id=school_id,
            title='Director',
            department='Admissions',
            is_primary_contact=True,
            can_sign_documents=True
        )
        
        # Mock the get_profile method to return the school admin profile
        with patch.object(User, 'get_profile', return_value=school_admin_profile):
            # Call to_representation
            representation = self.serializer.to_representation(self.user)
            
            # Assert that the representation contains school admin profile data
            self.assertIn('school_admin_profile', representation)
            self.assertEqual(representation['school_admin_profile']['title'], 'Director')
            self.assertEqual(representation['school_admin_profile']['department'], 'Admissions')
    
    def test_to_representation_with_internal_profile(self):
        """Test that to_representation includes internal user profile data"""
        # Set user_type to underwriter (an internal user type)
        self.user.user_type = USER_TYPES['UNDERWRITER']
        self.user.save()
        
        # Create an InternalUserProfile for the User
        internal_profile = InternalUserProfile.objects.create(
            user=self.user,
            employee_id='EMP123',
            department='Underwriting',
            title='Senior Underwriter'
        )
        
        # Mock the get_profile method to return the internal profile
        with patch.object(User, 'get_profile', return_value=internal_profile):
            # Call to_representation
            representation = self.serializer.to_representation(self.user)
            
            # Assert that the representation contains internal profile data
            self.assertIn('internal_user_profile', representation)
            self.assertEqual(representation['internal_user_profile']['employee_id'], 'EMP123')
            self.assertEqual(representation['internal_user_profile']['department'], 'Underwriting')
    
    def test_to_representation_without_profile(self):
        """Test that to_representation handles users without profiles"""
        # Mock the get_profile method to return None
        with patch.object(User, 'get_profile', return_value=None):
            # Call to_representation
            representation = self.serializer.to_representation(self.user)
            
            # Assert that the representation doesn't contain profile data
            self.assertNotIn('borrower_profile', representation)
            self.assertNotIn('school_admin_profile', representation)
            self.assertNotIn('internal_user_profile', representation)


class TestUserCreateSerializer(TestCase):
    """Test case for the UserCreateSerializer class"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create valid data for a new user
        self.valid_data = {
            'email': 'new@example.com',
            'password': 'SecureP@ssw0rd123',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '(555) 987-6543',
            'user_type': USER_TYPES['BORROWER'],
            'profile_data': {
                'ssn': '987-65-4321',
                'dob': '1990-01-01',
                'citizenship_status': CITIZENSHIP_STATUS['US_CITIZEN'],
                'address_line1': '456 Oak St',
                'city': 'Somewhere',
                'state': 'NY',
                'zip_code': '54321',
                'housing_status': HOUSING_STATUS['RENT'],
                'housing_payment': '1200.00'
            }
        }
        
        # Create the UserCreateSerializer instance with the data
        self.serializer = UserCreateSerializer(data=self.valid_data)
    
    def test_validate_email_valid(self):
        """Test that validate_email accepts valid email addresses"""
        # Call validate_email with a valid email
        valid_email = 'test@example.com'
        result = self.serializer.validate_email(valid_email)
        
        # Assert that the result is the lowercase email
        self.assertEqual(result, valid_email.lower())
    
    def test_validate_email_invalid(self):
        """Test that validate_email rejects invalid email addresses"""
        # Call validate_email with an invalid email
        invalid_email = 'not-an-email'
        
        # Assert that ValidationException is raised
        with self.assertRaises(ValidationException):
            self.serializer.validate_email(invalid_email)
    
    def test_validate_email_duplicate(self):
        """Test that validate_email rejects duplicate email addresses"""
        # Create a User with a specific email
        auth0_user = Auth0User.objects.create(
            auth0_id='auth0|987654321',
            email='existing@example.com',
            email_verified=True
        )
        
        user = User.objects.create(
            auth0_user=auth0_user,
            first_name='Existing',
            last_name='User',
            email='existing@example.com',
            phone='(555) 111-2222',
            user_type=USER_TYPES['BORROWER']
        )
        
        # Call validate_email with the same email
        with self.assertRaises(ValidationException):
            self.serializer.validate_email('existing@example.com')
    
    def test_validate_password_valid(self):
        """Test that validate_password accepts valid passwords"""
        # Call validate_password with a valid password
        valid_password = 'SecureP@ssw0rd123'
        
        # Mock Django's validate_password to avoid actual validation (since it might be complex)
        with patch('apps.users.serializers.validate_password'):
            result = self.serializer.validate_password(valid_password)
            
            # Assert that the result is the password
            self.assertEqual(result, valid_password)
    
    def test_validate_password_invalid(self):
        """Test that validate_password rejects invalid passwords"""
        # Call validate_password with an invalid password
        invalid_password = 'short'
        
        # Mock Django's validate_password to raise a ValidationError
        with patch('apps.users.serializers.validate_password', side_effect=Exception('Password is too short')):
            # Assert that ValidationException is raised
            with self.assertRaises(ValidationException):
                self.serializer.validate_password(invalid_password)
    
    def test_validate_profile_data_borrower_valid(self):
        """Test that validate_profile_data accepts valid borrower profile data"""
        # Create valid borrower profile data
        valid_profile_data = {
            'ssn': '987-65-4321',
            'dob': '1990-01-01',
            'citizenship_status': CITIZENSHIP_STATUS['US_CITIZEN'],
            'address_line1': '456 Oak St',
            'city': 'Somewhere',
            'state': 'NY',
            'zip_code': '54321',
            'housing_status': HOUSING_STATUS['RENT'],
            'housing_payment': '1200.00'
        }
        
        # Set user_type in initial_data
        self.serializer.initial_data['user_type'] = USER_TYPES['BORROWER']
        
        # Call validate_profile_data
        result = self.serializer.validate_profile_data(valid_profile_data)
        
        # Assert that the result is the validated profile data
        self.assertEqual(result, valid_profile_data)
    
    def test_validate_profile_data_borrower_invalid(self):
        """Test that validate_profile_data rejects invalid borrower profile data"""
        # Create invalid borrower profile data (missing required fields)
        invalid_profile_data = {
            'ssn': '987-65-4321',
            # Missing dob and other required fields
            'city': 'Somewhere',
            'state': 'NY'
        }
        
        # Set user_type in initial_data
        self.serializer.initial_data['user_type'] = USER_TYPES['BORROWER']
        
        # Assert that ValidationException is raised
        with self.assertRaises(ValidationException):
            self.serializer.validate_profile_data(invalid_profile_data)
    
    def test_validate_profile_data_school_admin_valid(self):
        """Test that validate_profile_data accepts valid school admin profile data"""
        # Create valid school admin profile data
        valid_profile_data = {
            'school': uuid.uuid4(),
            'title': 'Program Director',
            'department': 'Admissions',
            'is_primary_contact': True,
            'can_sign_documents': True
        }
        
        # Set user_type in initial_data
        self.serializer.initial_data['user_type'] = USER_TYPES['SCHOOL_ADMIN']
        
        # Call validate_profile_data
        result = self.serializer.validate_profile_data(valid_profile_data)
        
        # Assert that the result is the validated profile data
        self.assertEqual(result, valid_profile_data)
    
    def test_validate_profile_data_school_admin_invalid(self):
        """Test that validate_profile_data rejects invalid school admin profile data"""
        # Create invalid school admin profile data (missing required fields)
        invalid_profile_data = {
            'title': 'Program Director',
            # Missing school and other required fields
        }
        
        # Set user_type in initial_data
        self.serializer.initial_data['user_type'] = USER_TYPES['SCHOOL_ADMIN']
        
        # Assert that ValidationException is raised
        with self.assertRaises(ValidationException):
            self.serializer.validate_profile_data(invalid_profile_data)
    
    def test_validate_profile_data_internal_valid(self):
        """Test that validate_profile_data accepts valid internal user profile data"""
        # Create valid internal user profile data
        valid_profile_data = {
            'employee_id': 'EMP456',
            'department': 'Underwriting',
            'title': 'Senior Underwriter'
        }
        
        # Set user_type in initial_data
        self.serializer.initial_data['user_type'] = USER_TYPES['UNDERWRITER']
        
        # Call validate_profile_data
        result = self.serializer.validate_profile_data(valid_profile_data)
        
        # Assert that the result is the validated profile data
        self.assertEqual(result, valid_profile_data)
    
    def test_validate_profile_data_internal_invalid(self):
        """Test that validate_profile_data rejects invalid internal user profile data"""
        # Create invalid internal user profile data (missing required fields)
        invalid_profile_data = {
            'department': 'Underwriting',
            # Missing employee_id and other required fields
        }
        
        # Set user_type in initial_data
        self.serializer.initial_data['user_type'] = USER_TYPES['UNDERWRITER']
        
        # Assert that ValidationException is raised
        with self.assertRaises(ValidationException):
            self.serializer.validate_profile_data(invalid_profile_data)


class TestUserUpdateSerializer(TestCase):
    """Test case for the UserUpdateSerializer class"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create an Auth0User instance for testing
        self.auth0_user = Auth0User.objects.create(
            auth0_id='auth0|123456789',
            email='test@example.com',
            email_verified=True
        )
        
        # Create a User instance linked to the Auth0User
        self.user = User.objects.create(
            auth0_user=self.auth0_user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            phone='(555) 123-4567',
            user_type=USER_TYPES['BORROWER']
        )
        
        # Create valid update data
        self.valid_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone': '(555) 987-6543',
            'profile_data': {
                'address_line1': '789 Pine St',
                'city': 'New City',
                'state': 'CA',
                'zip_code': '98765',
                'housing_status': HOUSING_STATUS['OWN'],
                'housing_payment': '2000.00'
            }
        }
        
        # Create the UserUpdateSerializer instance with the data and context
        self.serializer = UserUpdateSerializer(
            data=self.valid_data,
            context={'user': self.user}
        )
    
    def test_validate_profile_data_borrower_valid(self):
        """Test that validate_profile_data accepts valid borrower profile data"""
        # Create a User with borrower type
        borrower = User.objects.create(
            auth0_user=Auth0User.objects.create(
                auth0_id='auth0|borrower',
                email='borrower@example.com'
            ),
            first_name='Borrower',
            last_name='User',
            email='borrower@example.com',
            user_type=USER_TYPES['BORROWER']
        )
        
        # Create valid borrower profile data
        valid_profile_data = {
            'address_line1': '789 Pine St',
            'city': 'New City',
            'state': 'CA',
            'zip_code': '98765',
            'housing_status': HOUSING_STATUS['OWN'],
            'housing_payment': '2000.00'
        }
        
        # Create serializer with borrower context
        serializer = UserUpdateSerializer(
            data={'profile_data': valid_profile_data},
            context={'user': borrower}
        )
        
        # Call validate_profile_data
        result = serializer.validate_profile_data(valid_profile_data)
        
        # Assert that the result is the validated profile data
        self.assertEqual(result, valid_profile_data)
    
    def test_validate_profile_data_borrower_invalid(self):
        """Test that validate_profile_data rejects invalid borrower profile data"""
        # Create a User with borrower type
        borrower = User.objects.create(
            auth0_user=Auth0User.objects.create(
                auth0_id='auth0|borrower2',
                email='borrower2@example.com'
            ),
            first_name='Borrower',
            last_name='User',
            email='borrower2@example.com',
            user_type=USER_TYPES['BORROWER']
        )
        
        # Create invalid borrower profile data (with invalid field)
        invalid_profile_data = {
            'address_line1': '789 Pine St',
            'invalid_field': 'This field is not valid',
            'city': 'New City'
        }
        
        # Create serializer with borrower context
        serializer = UserUpdateSerializer(
            data={'profile_data': invalid_profile_data},
            context={'user': borrower}
        )
        
        # Assert that ValidationException is raised
        with self.assertRaises(ValidationException):
            serializer.validate_profile_data(invalid_profile_data)
    
    def test_validate_profile_data_school_admin_valid(self):
        """Test that validate_profile_data accepts valid school admin profile data"""
        # Create a User with school admin type
        school_admin = User.objects.create(
            auth0_user=Auth0User.objects.create(
                auth0_id='auth0|schooladmin',
                email='admin@school.edu'
            ),
            first_name='School',
            last_name='Admin',
            email='admin@school.edu',
            user_type=USER_TYPES['SCHOOL_ADMIN']
        )
        
        # Create valid school admin profile data
        valid_profile_data = {
            'title': 'Program Manager',
            'department': 'Student Services',
            'is_primary_contact': False,
            'can_sign_documents': True
        }
        
        # Create serializer with school admin context
        serializer = UserUpdateSerializer(
            data={'profile_data': valid_profile_data},
            context={'user': school_admin}
        )
        
        # Call validate_profile_data
        result = serializer.validate_profile_data(valid_profile_data)
        
        # Assert that the result is the validated profile data
        self.assertEqual(result, valid_profile_data)
    
    def test_validate_profile_data_school_admin_invalid(self):
        """Test that validate_profile_data rejects invalid school admin profile data"""
        # Create a User with school admin type
        school_admin = User.objects.create(
            auth0_user=Auth0User.objects.create(
                auth0_id='auth0|schooladmin2',
                email='admin2@school.edu'
            ),
            first_name='School',
            last_name='Admin',
            email='admin2@school.edu',
            user_type=USER_TYPES['SCHOOL_ADMIN']
        )
        
        # Create invalid school admin profile data (with invalid field)
        invalid_profile_data = {
            'title': 'Program Manager',
            'invalid_field': 'This field is not valid'
        }
        
        # Create serializer with school admin context
        serializer = UserUpdateSerializer(
            data={'profile_data': invalid_profile_data},
            context={'user': school_admin}
        )
        
        # Assert that ValidationException is raised
        with self.assertRaises(ValidationException):
            serializer.validate_profile_data(invalid_profile_data)
    
    def test_validate_profile_data_internal_valid(self):
        """Test that validate_profile_data accepts valid internal user profile data"""
        # Create a User with underwriter type
        underwriter = User.objects.create(
            auth0_user=Auth0User.objects.create(
                auth0_id='auth0|underwriter',
                email='under@example.com'
            ),
            first_name='Under',
            last_name='Writer',
            email='under@example.com',
            user_type=USER_TYPES['UNDERWRITER']
        )
        
        # Create valid internal user profile data
        valid_profile_data = {
            'employee_id': 'EMP789',
            'department': 'Risk Assessment',
            'title': 'Lead Underwriter'
        }
        
        # Create serializer with underwriter context
        serializer = UserUpdateSerializer(
            data={'profile_data': valid_profile_data},
            context={'user': underwriter}
        )
        
        # Call validate_profile_data
        result = serializer.validate_profile_data(valid_profile_data)
        
        # Assert that the result is the validated profile data
        self.assertEqual(result, valid_profile_data)
    
    def test_validate_profile_data_internal_invalid(self):
        """Test that validate_profile_data rejects invalid internal user profile data"""
        # Create a User with underwriter type
        underwriter = User.objects.create(
            auth0_user=Auth0User.objects.create(
                auth0_id='auth0|underwriter2',
                email='under2@example.com'
            ),
            first_name='Under',
            last_name='Writer',
            email='under2@example.com',
            user_type=USER_TYPES['UNDERWRITER']
        )
        
        # Create invalid internal user profile data (with invalid field)
        invalid_profile_data = {
            'employee_id': 'EMP789',
            'invalid_field': 'This field is not valid'
        }
        
        # Create serializer with underwriter context
        serializer = UserUpdateSerializer(
            data={'profile_data': invalid_profile_data},
            context={'user': underwriter}
        )
        
        # Assert that ValidationException is raised
        with self.assertRaises(ValidationException):
            serializer.validate_profile_data(invalid_profile_data)


class TestBorrowerProfileSerializer(TestCase):
    """Test case for the BorrowerProfileSerializer class"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create an Auth0User instance for testing
        self.auth0_user = Auth0User.objects.create(
            auth0_id='auth0|123456789',
            email='test@example.com',
            email_verified=True
        )
        
        # Create a User instance with borrower type
        self.user = User.objects.create(
            auth0_user=self.auth0_user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            phone='(555) 123-4567',
            user_type=USER_TYPES['BORROWER']
        )
        
        # Create a BorrowerProfile instance for the User
        self.borrower_profile = BorrowerProfile.objects.create(
            user=self.user,
            ssn='123-45-6789',
            dob=timezone.now().date() - datetime.timedelta(days=365*30),  # 30 years ago
            citizenship_status=CITIZENSHIP_STATUS['US_CITIZEN'],
            address_line1='123 Main St',
            city='Anytown',
            state='CA',
            zip_code='12345',
            housing_status=HOUSING_STATUS['RENT'],
            housing_payment=Decimal('1500.00')
        )
        
        # Create the BorrowerProfileSerializer instance with the BorrowerProfile
        self.serializer = BorrowerProfileSerializer(instance=self.borrower_profile)
    
    def test_serializer_contains_expected_fields(self):
        """Test that the serializer contains all expected fields"""
        data = self.serializer.data
        
        # Assert that the data contains expected fields
        self.assertIn('id', data)
        self.assertIn('user', data)
        self.assertIn('ssn', data)
        self.assertIn('dob', data)
        self.assertIn('citizenship_status', data)
        self.assertIn('address_line1', data)
        self.assertIn('city', data)
        self.assertIn('state', data)
        self.assertIn('zip_code', data)
        self.assertIn('housing_status', data)
        self.assertIn('housing_payment', data)
        
        # Check that sensitive fields are masked
        self.assertNotEqual(data['ssn'], '123-45-6789')
    
    def test_get_full_address(self):
        """Test that get_full_address returns the correct formatted address"""
        # Set up BorrowerProfile with address fields
        self.borrower_profile.address_line1 = '123 Main St'
        self.borrower_profile.address_line2 = 'Apt 4B'
        self.borrower_profile.city = 'Anytown'
        self.borrower_profile.state = 'CA'
        self.borrower_profile.zip_code = '12345'
        self.borrower_profile.save()
        
        # Mock the profile's get_full_address method
        expected_address = '123 Main St, Apt 4B, Anytown, CA 12345'
        with patch.object(BorrowerProfile, 'get_full_address', return_value=expected_address):
            # Call get_full_address on the serializer
            full_address = self.serializer.get_full_address(self.borrower_profile)
            
            # Assert that the result is the expected address
            self.assertEqual(full_address, expected_address)
    
    def test_get_age(self):
        """Test that get_age returns the correct age based on date of birth"""
        # Set up BorrowerProfile with dob field
        birthday = timezone.now().date() - datetime.timedelta(days=365*30)  # 30 years ago
        self.borrower_profile.dob = birthday
        self.borrower_profile.save()
        
        # Mock the profile's get_age method
        with patch.object(BorrowerProfile, 'get_age', return_value=30):
            # Call get_age on the serializer
            age = self.serializer.get_age(self.borrower_profile)
            
            # Assert that the result is 30
            self.assertEqual(age, 30)
    
    def test_sensitive_data_masking(self):
        """Test that sensitive data is properly masked in serialized output"""
        # Set up BorrowerProfile with sensitive data
        self.borrower_profile.ssn = '123-45-6789'
        self.borrower_profile.save()
        
        # Get the serialized data
        data = self.serializer.data
        
        # Assert that ssn is masked
        self.assertIn('ssn', data)
        self.assertNotEqual(data['ssn'], '123-45-6789')
        self.assertTrue(data['ssn'].startswith('XXX-XX-'))


class TestEmploymentInfoSerializer(TestCase):
    """Test case for the EmploymentInfoSerializer class"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create an Auth0User instance for testing
        self.auth0_user = Auth0User.objects.create(
            auth0_id='auth0|123456789',
            email='test@example.com',
            email_verified=True
        )
        
        # Create a User instance with borrower type
        self.user = User.objects.create(
            auth0_user=self.auth0_user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            phone='(555) 123-4567',
            user_type=USER_TYPES['BORROWER']
        )
        
        # Create a BorrowerProfile instance for the User
        self.borrower_profile = BorrowerProfile.objects.create(
            user=self.user,
            ssn='123-45-6789',
            dob=timezone.now().date() - datetime.timedelta(days=365*30),  # 30 years ago
            citizenship_status=CITIZENSHIP_STATUS['US_CITIZEN'],
            address_line1='123 Main St',
            city='Anytown',
            state='CA',
            zip_code='12345',
            housing_status=HOUSING_STATUS['RENT'],
            housing_payment=Decimal('1500.00')
        )
        
        # Create an EmploymentInfo instance for the BorrowerProfile
        self.employment_info = EmploymentInfo.objects.create(
            profile=self.borrower_profile,
            employment_type=EMPLOYMENT_TYPES['FULL_TIME'],
            employer_name='ABC Company',
            occupation='Software Developer',
            employer_phone='(555) 987-6543',
            years_employed=3,
            months_employed=6,
            annual_income=Decimal('85000.00'),
            other_income=Decimal('5000.00'),
            other_income_source='Freelance Work'
        )
        
        # Create the EmploymentInfoSerializer instance with the EmploymentInfo
        self.serializer = EmploymentInfoSerializer(instance=self.employment_info)
    
    def test_serializer_contains_expected_fields(self):
        """Test that the serializer contains all expected fields"""
        data = self.serializer.data
        
        # Assert that the data contains expected fields
        self.assertIn('id', data)
        self.assertIn('profile', data)
        self.assertIn('employment_type', data)
        self.assertIn('employer_name', data)
        self.assertIn('occupation', data)
        self.assertIn('employer_phone', data)
        self.assertIn('years_employed', data)
        self.assertIn('months_employed', data)
        self.assertIn('annual_income', data)
        self.assertIn('other_income', data)
        self.assertIn('other_income_source', data)
        
        # Check field values
        self.assertEqual(data['employment_type'], EMPLOYMENT_TYPES['FULL_TIME'])
        self.assertEqual(data['employer_name'], 'ABC Company')
        self.assertEqual(data['occupation'], 'Software Developer')
        self.assertEqual(data['years_employed'], 3)
        self.assertEqual(data['months_employed'], 6)
    
    def test_get_total_income(self):
        """Test that get_total_income returns the correct total income"""
        # Set up EmploymentInfo with annual_income and other_income
        self.employment_info.annual_income = Decimal('85000.00')
        self.employment_info.other_income = Decimal('5000.00')
        self.employment_info.save()
        
        # Mock the employment info's get_total_income method
        expected_total = Decimal('90000.00')
        with patch.object(EmploymentInfo, 'get_total_income', return_value=expected_total):
            # Call get_total_income on the serializer
            total_income = self.serializer.get_total_income(self.employment_info)
            
            # Assert that the result is the expected total
            self.assertEqual(total_income, expected_total)
    
    def test_get_monthly_income(self):
        """Test that get_monthly_income returns the correct monthly income"""
        # Set up EmploymentInfo with annual_income
        self.employment_info.annual_income = Decimal('84000.00')
        self.employment_info.other_income = Decimal('6000.00')
        self.employment_info.save()
        
        # Mock the employment info's get_monthly_income method
        expected_monthly = Decimal('7500.00')  # (84000 + 6000) / 12 = 7500
        with patch.object(EmploymentInfo, 'get_monthly_income', return_value=expected_monthly):
            # Call get_monthly_income on the serializer
            monthly_income = self.serializer.get_monthly_income(self.employment_info)
            
            # Assert that the result is the expected monthly income
            self.assertEqual(monthly_income, expected_monthly)
    
    def test_get_total_employment_duration(self):
        """Test that get_total_employment_duration returns the correct duration in months"""
        # Set up EmploymentInfo with years_employed and months_employed
        self.employment_info.years_employed = 3
        self.employment_info.months_employed = 6
        self.employment_info.save()
        
        # Mock the employment info's get_total_employment_duration method
        expected_duration = 3 * 12 + 6  # 42 months
        with patch.object(EmploymentInfo, 'get_total_employment_duration', return_value=expected_duration):
            # Call get_total_employment_duration on the serializer
            duration = self.serializer.get_total_employment_duration(self.employment_info)
            
            # Assert that the result is the expected duration
            self.assertEqual(duration, expected_duration)


class TestSchoolAdminProfileSerializer(TestCase):
    """Test case for the SchoolAdminProfileSerializer class"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create an Auth0User instance for testing
        self.auth0_user = Auth0User.objects.create(
            auth0_id='auth0|123456789',
            email='admin@school.edu',
            email_verified=True
        )
        
        # Create a User instance with school admin type
        self.user = User.objects.create(
            auth0_user=self.auth0_user,
            first_name='School',
            last_name='Admin',
            email='admin@school.edu',
            phone='(555) 123-4567',
            user_type=USER_TYPES['SCHOOL_ADMIN']
        )
        
        # Create a mock School
        self.school_id = uuid.uuid4()
        
        # Create a SchoolAdminProfile instance for the User
        self.school_admin_profile = SchoolAdminProfile.objects.create(
            user=self.user,
            school_id=self.school_id,
            title='Program Director',
            department='Admissions',
            is_primary_contact=True,
            can_sign_documents=True
        )
        
        # Create the SchoolAdminProfileSerializer instance with the SchoolAdminProfile
        self.serializer = SchoolAdminProfileSerializer(instance=self.school_admin_profile)
    
    def test_serializer_contains_expected_fields(self):
        """Test that the serializer contains all expected fields"""
        data = self.serializer.data
        
        # Assert that the data contains expected fields
        self.assertIn('id', data)
        self.assertIn('user', data)
        self.assertIn('school', data)
        self.assertIn('title', data)
        self.assertIn('department', data)
        self.assertIn('is_primary_contact', data)
        self.assertIn('can_sign_documents', data)
        
        # Check field values
        self.assertEqual(str(data['school']), str(self.school_id))
        self.assertEqual(data['title'], 'Program Director')
        self.assertEqual(data['department'], 'Admissions')
        self.assertTrue(data['is_primary_contact'])
        self.assertTrue(data['can_sign_documents'])
    
    def test_get_school_name(self):
        """Test that get_school_name returns the correct school name"""
        # Mock the school object
        mock_school = mock.MagicMock()
        mock_school.name = 'Test School'
        
        # Replace the school attribute on the profile with our mock
        self.school_admin_profile.school = mock_school
        
        # Call get_school_name on the serializer
        school_name = self.serializer.get_school_name(self.school_admin_profile)
        
        # Assert that the result is the expected school name
        self.assertEqual(school_name, 'Test School')


class TestInternalUserProfileSerializer(TestCase):
    """Test case for the InternalUserProfileSerializer class"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create an Auth0User instance for testing
        self.auth0_user = Auth0User.objects.create(
            auth0_id='auth0|123456789',
            email='internal@example.com',
            email_verified=True
        )
        
        # Create a User instance with underwriter type
        self.user = User.objects.create(
            auth0_user=self.auth0_user,
            first_name='Internal',
            last_name='User',
            email='internal@example.com',
            phone='(555) 123-4567',
            user_type=USER_TYPES['UNDERWRITER']
        )
        
        # Create a supervisor Auth0User and User
        self.supervisor_auth0_user = Auth0User.objects.create(
            auth0_id='auth0|supervisor',
            email='supervisor@example.com',
            email_verified=True
        )
        
        self.supervisor_user = User.objects.create(
            auth0_user=self.supervisor_auth0_user,
            first_name='Super',
            last_name='Visor',
            email='supervisor@example.com',
            phone='(555) 987-6543',
            user_type=USER_TYPES['UNDERWRITER']
        )
        
        # Create a supervisor InternalUserProfile
        self.supervisor_profile = InternalUserProfile.objects.create(
            user=self.supervisor_user,
            employee_id='EMP001',
            department='Underwriting',
            title='Manager'
        )
        
        # Create an InternalUserProfile instance for the User with supervisor
        self.internal_profile = InternalUserProfile.objects.create(
            user=self.user,
            employee_id='EMP002',
            department='Underwriting',
            title='Senior Underwriter',
            supervisor=self.supervisor_profile
        )
        
        # Create the InternalUserProfileSerializer instance with the InternalUserProfile
        self.serializer = InternalUserProfileSerializer(instance=self.internal_profile)
    
    def test_serializer_contains_expected_fields(self):
        """Test that the serializer contains all expected fields"""
        data = self.serializer.data
        
        # Assert that the data contains expected fields
        self.assertIn('id', data)
        self.assertIn('user', data)
        self.assertIn('employee_id', data)
        self.assertIn('department', data)
        self.assertIn('title', data)
        self.assertIn('supervisor', data)
        
        # Check field values
        self.assertEqual(data['employee_id'], 'EMP002')
        self.assertEqual(data['department'], 'Underwriting')
        self.assertEqual(data['title'], 'Senior Underwriter')
        self.assertEqual(str(data['supervisor']), str(self.supervisor_profile.id))
    
    def test_get_supervisor_name(self):
        """Test that get_supervisor_name returns the correct supervisor name"""
        # Mock the supervisor's full name
        with patch.object(User, 'get_full_name', return_value='Super Visor'):
            # Call get_supervisor_name on the serializer
            supervisor_name = self.serializer.get_supervisor_name(self.internal_profile)
            
            # Assert that the result is the expected supervisor name
            self.assertEqual(supervisor_name, 'Super Visor')
    
    def test_get_supervisor_name_no_supervisor(self):
        """Test that get_supervisor_name returns None when no supervisor exists"""
        # Create a profile with no supervisor
        profile_without_supervisor = InternalUserProfile.objects.create(
            user=User.objects.create(
                auth0_user=Auth0User.objects.create(
                    auth0_id='auth0|nosupervisor',
                    email='nosupervisor@example.com'
                ),
                first_name='No',
                last_name='Supervisor',
                email='nosupervisor@example.com',
                user_type=USER_TYPES['UNDERWRITER']
            ),
            employee_id='EMP003',
            department='Underwriting',
            title='Underwriter'
        )
        
        # Create a serializer for the profile without supervisor
        serializer = InternalUserProfileSerializer(instance=profile_without_supervisor)
        
        # Call get_supervisor_name on the serializer
        supervisor_name = serializer.get_supervisor_name(profile_without_supervisor)
        
        # Assert that the result is None
        self.assertIsNone(supervisor_name)


class TestRoleSerializer(TestCase):
    """Test case for the RoleSerializer class"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create a Role instance
        self.role = Role.objects.create(
            name='Underwriting Manager',
            description='Manages the underwriting process and team'
        )
        
        # Create the RoleSerializer instance with the Role
        self.serializer = RoleSerializer(instance=self.role)
    
    def test_serializer_contains_expected_fields(self):
        """Test that the serializer contains all expected fields"""
        data = self.serializer.data
        
        # Assert that the data contains expected fields
        self.assertIn('id', data)
        self.assertIn('name', data)
        self.assertIn('description', data)
        
        # Check field values
        self.assertEqual(data['name'], 'Underwriting Manager')
        self.assertEqual(data['description'], 'Manages the underwriting process and team')
    
    def test_get_permissions_count(self):
        """Test that get_permissions_count returns the correct count of permissions"""
        # Create multiple Permission instances
        permission1 = Permission.objects.create(
            name='view_application',
            description='Can view loan applications',
            resource_type='application'
        )
        
        permission2 = Permission.objects.create(
            name='approve_application',
            description='Can approve loan applications',
            resource_type='application'
        )
        
        # Link permissions to the role
        RolePermission.objects.create(role=self.role, permission=permission1)
        RolePermission.objects.create(role=self.role, permission=permission2)
        
        # Call get_permissions_count on the serializer
        permissions_count = self.serializer.get_permissions_count(self.role)
        
        # Assert that the result is the expected count
        self.assertEqual(permissions_count, 2)


class TestPermissionSerializer(TestCase):
    """Test case for the PermissionSerializer class"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create a Permission instance
        self.permission = Permission.objects.create(
            name='view_application',
            description='Can view loan applications',
            resource_type='application'
        )
        
        # Create the PermissionSerializer instance with the Permission
        self.serializer = PermissionSerializer(instance=self.permission)
    
    def test_serializer_contains_expected_fields(self):
        """Test that the serializer contains all expected fields"""
        data = self.serializer.data
        
        # Assert that the data contains expected fields
        self.assertIn('id', data)
        self.assertIn('name', data)
        self.assertIn('description', data)
        self.assertIn('resource_type', data)
        
        # Check field values
        self.assertEqual(data['name'], 'view_application')
        self.assertEqual(data['description'], 'Can view loan applications')
        self.assertEqual(data['resource_type'], 'application')


class TestUserRoleSerializer(TestCase):
    """Test case for the UserRoleSerializer class"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create a User instance
        self.auth0_user = Auth0User.objects.create(
            auth0_id='auth0|123456789',
            email='test@example.com',
            email_verified=True
        )
        
        self.user = User.objects.create(
            auth0_user=self.auth0_user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            phone='(555) 123-4567',
            user_type=USER_TYPES['BORROWER']
        )
        
        # Create a Role instance
        self.role = Role.objects.create(
            name='Borrower',
            description='Standard borrower role'
        )
        
        # Create an assigner User instance
        self.assigner_auth0_user = Auth0User.objects.create(
            auth0_id='auth0|assigner',
            email='assigner@example.com',
            email_verified=True
        )
        
        self.assigner = User.objects.create(
            auth0_user=self.assigner_auth0_user,
            first_name='Admin',
            last_name='User',
            email='assigner@example.com',
            phone='(555) 987-6543',
            user_type=USER_TYPES['SYSTEM_ADMIN']
        )
        
        # Create a UserRole instance
        self.user_role = UserRole.objects.create(
            user=self.user,
            role=self.role,
            assigned_by=self.assigner
        )
        
        # Create the UserRoleSerializer instance with the UserRole
        self.serializer = UserRoleSerializer(instance=self.user_role)
    
    def test_serializer_contains_expected_fields(self):
        """Test that the serializer contains all expected fields"""
        data = self.serializer.data
        
        # Assert that the data contains expected fields
        self.assertIn('id', data)
        self.assertIn('user', data)
        self.assertIn('role', data)
        self.assertIn('assigned_at', data)
        self.assertIn('assigned_by', data)
        
        # Check field values
        self.assertEqual(str(data['user']), str(self.user.id))
        self.assertEqual(str(data['role']), str(self.role.id))
        self.assertEqual(str(data['assigned_by']), str(self.assigner.id))
    
    def test_get_role_name(self):
        """Test that get_role_name returns the correct role name"""
        # Call get_role_name on the serializer
        role_name = self.serializer.get_role_name(self.user_role)
        
        # Assert that the result is the expected role name
        self.assertEqual(role_name, 'Borrower')
    
    def test_get_assigned_by_name(self):
        """Test that get_assigned_by_name returns the correct assigner name"""
        # Mock the assigner's full name
        with patch.object(User, 'get_full_name', return_value='Admin User'):
            # Call get_assigned_by_name on the serializer
            assigner_name = self.serializer.get_assigned_by_name(self.user_role)
            
            # Assert that the result is the expected assigner name
            self.assertEqual(assigner_name, 'Admin User')
    
    def test_get_assigned_by_name_no_assigner(self):
        """Test that get_assigned_by_name returns None when no assigner exists"""
        # Create a UserRole with no assigner
        user_role_without_assigner = UserRole.objects.create(
            user=self.user,
            role=self.role,
            assigned_by=None
        )
        
        # Create a serializer for the UserRole without assigner
        serializer = UserRoleSerializer(instance=user_role_without_assigner)
        
        # Call get_assigned_by_name on the serializer
        assigner_name = serializer.get_assigned_by_name(user_role_without_assigner)
        
        # Assert that the result is None
        self.assertIsNone(assigner_name)


class TestRolePermissionSerializer(TestCase):
    """Test case for the RolePermissionSerializer class"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create a Role instance
        self.role = Role.objects.create(
            name='Underwriter',
            description='Can review and make decisions on loan applications'
        )
        
        # Create a Permission instance
        self.permission = Permission.objects.create(
            name='approve_loan',
            description='Can approve loan applications',
            resource_type='application'
        )
        
        # Create a RolePermission instance
        self.role_permission = RolePermission.objects.create(
            role=self.role,
            permission=self.permission
        )
        
        # Create the RolePermissionSerializer instance with the RolePermission
        self.serializer = RolePermissionSerializer(instance=self.role_permission)
    
    def test_serializer_contains_expected_fields(self):
        """Test that the serializer contains all expected fields"""
        data = self.serializer.data
        
        # Assert that the data contains expected fields
        self.assertIn('id', data)
        self.assertIn('role', data)
        self.assertIn('permission', data)
        
        # Check field values
        self.assertEqual(str(data['role']), str(self.role.id))
        self.assertEqual(str(data['permission']), str(self.permission.id))
    
    def test_get_permission_name(self):
        """Test that get_permission_name returns the correct permission name"""
        # Call get_permission_name on the serializer
        permission_name = self.serializer.get_permission_name(self.role_permission)
        
        # Assert that the result is the expected permission name
        self.assertEqual(permission_name, 'approve_loan')
    
    def test_get_resource_type(self):
        """Test that get_resource_type returns the correct resource type"""
        # Call get_resource_type on the serializer
        resource_type = self.serializer.get_resource_type(self.role_permission)
        
        # Assert that the result is the expected resource type
        self.assertEqual(resource_type, 'application')


class TestPasswordChangeSerializer(TestCase):
    """Test case for the PasswordChangeSerializer class"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create a User instance with a known password
        self.auth0_user = Auth0User.objects.create(
            auth0_id='auth0|123456789',
            email='test@example.com',
            email_verified=True
        )
        
        # Mock the check_password method to simulate a known password
        self.auth0_user.check_password = lambda password: password == 'CurrentP@ssword'
        
        self.user = User.objects.create(
            auth0_user=self.auth0_user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            phone='(555) 123-4567',
            user_type=USER_TYPES['BORROWER']
        )
        
        # Create valid password change data
        self.valid_data = {
            'current_password': 'CurrentP@ssword',
            'new_password': 'NewSecureP@ssword123',
            'confirm_password': 'NewSecureP@ssword123'
        }
        
        # Create the PasswordChangeSerializer instance with the data and context
        self.serializer = PasswordChangeSerializer(
            data=self.valid_data,
            context={'user': self.user}
        )
    
    def test_validate_current_password_valid(self):
        """Test that validate_current_password accepts correct current password"""
        # Call validate_current_password with the correct password
        result = self.serializer.validate_current_password('CurrentP@ssword')
        
        # Assert that the result is the current password
        self.assertEqual(result, 'CurrentP@ssword')
    
    def test_validate_current_password_invalid(self):
        """Test that validate_current_password rejects incorrect current password"""
        # Call validate_current_password with an incorrect password
        with self.assertRaises(ValidationException):
            self.serializer.validate_current_password('WrongPassword')
    
    def test_validate_new_password_valid(self):
        """Test that validate_new_password accepts valid new passwords"""
        # Call validate_new_password with a valid password
        with patch('apps.users.serializers.validate_password'):
            result = self.serializer.validate_new_password('NewSecureP@ssword123')
            
            # Assert that the result is the new password
            self.assertEqual(result, 'NewSecureP@ssword123')
    
    def test_validate_new_password_invalid(self):
        """Test that validate_new_password rejects invalid new passwords"""
        # Call validate_new_password with an invalid password
        with patch('apps.users.serializers.validate_password', side_effect=Exception('Password is too short')):
            with self.assertRaises(ValidationException):
                self.serializer.validate_new_password('short')
    
    def test_validate_passwords_match(self):
        """Test that validate accepts when new_password and confirm_password match"""
        # Create data with matching passwords
        data = {
            'current_password': 'CurrentP@ssword',
            'new_password': 'NewSecureP@ssword123',
            'confirm_password': 'NewSecureP@ssword123'
        }
        
        # Call validate with the data
        result = self.serializer.validate(data)
        
        # Assert that the result is the data
        self.assertEqual(result, data)
    
    def test_validate_passwords_mismatch(self):
        """Test that validate rejects when new_password and confirm_password don't match"""
        # Create data with mismatched passwords
        data = {
            'current_password': 'CurrentP@ssword',
            'new_password': 'NewSecureP@ssword123',
            'confirm_password': 'DifferentP@ssword'
        }
        
        # Call validate with the data
        with self.assertRaises(ValidationException):
            self.serializer.validate(data)