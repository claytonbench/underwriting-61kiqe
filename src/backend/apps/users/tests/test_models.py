from django.test import TestCase
from unittest.mock import patch, mock
from django.utils import timezone
import uuid
from datetime import timedelta
from decimal import Decimal

from apps.users.models import (
    User, BorrowerProfile, EmploymentInfo, 
    SchoolAdminProfile, InternalUserProfile, UserPermission, 
    USER_ROLE_CHOICES
)
from apps.authentication.models import Auth0User
from utils.constants import (
    USER_TYPES, EMPLOYMENT_TYPES, HOUSING_STATUS, 
    CITIZENSHIP_STATUS, MINIMUM_AGE, MINIMUM_INCOME,
    MIN_EMPLOYMENT_DURATION_MONTHS
)


class TestUser(TestCase):
    """Test case for the User model"""
    
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
            first_name='John',
            last_name='Doe',
            email='test@example.com',
            phone='(555) 123-4567',
            user_type=USER_TYPES['BORROWER']
        )
    
    def test_user_creation(self):
        """Test that a User can be created with valid data"""
        # Create a new Auth0User for this test
        auth0_user = Auth0User.objects.create(
            auth0_id='auth0|987654321',
            email='newuser@example.com',
            email_verified=True
        )
        
        # Create a new User with valid data
        new_user = User(
            auth0_user=auth0_user,
            first_name='Jane',
            last_name='Smith',
            email='newuser@example.com',
            phone='(555) 987-6543',
            user_type=USER_TYPES['SCHOOL_ADMIN']
        )
        
        # Save the User instance
        new_user.save()
        
        # Assert that the User was created successfully
        self.assertIsNotNone(new_user.id)
        self.assertEqual(new_user.first_name, 'Jane')
        self.assertEqual(new_user.last_name, 'Smith')
        self.assertEqual(new_user.email, 'newuser@example.com')
        self.assertEqual(new_user.phone, '(555) 987-6543')
        self.assertEqual(new_user.user_type, USER_TYPES['SCHOOL_ADMIN'])
        self.assertTrue(new_user.is_active)
    
    def test_get_full_name(self):
        """Test that get_full_name returns the correct full name"""
        # Create a User with first_name='John' and last_name='Doe'
        user = User(
            first_name='John',
            last_name='Doe'
        )
        
        # Call get_full_name on the User instance
        full_name = user.get_full_name()
        
        # Assert that the result is 'John Doe'
        self.assertEqual(full_name, 'John Doe')
    
    def test_get_profile_borrower(self):
        """Test that get_profile returns the correct profile for a borrower"""
        # Create a User with user_type=USER_TYPES['BORROWER']
        user = User.objects.create(
            auth0_user=Auth0User.objects.create(
                auth0_id='auth0|borrower',
                email='borrower@example.com'
            ),
            first_name='Borrower',
            last_name='User',
            email='borrower@example.com',
            user_type=USER_TYPES['BORROWER']
        )
        
        # Create a BorrowerProfile for the User
        borrower_profile = BorrowerProfile.objects.create(
            user=user,
            ssn='123-45-6789',
            dob=timezone.now().date() - timedelta(days=365*30),
            citizenship_status=CITIZENSHIP_STATUS['US_CITIZEN'],
            address_line1='123 Main St',
            city='Anytown',
            state='CA',
            zip_code='12345',
            housing_status=HOUSING_STATUS['RENT'],
            housing_payment=Decimal('1500.00')
        )
        
        # Call get_profile on the User instance
        profile = user.get_profile()
        
        # Assert that the result is the BorrowerProfile instance
        self.assertEqual(profile, borrower_profile)
    
    def test_get_profile_school_admin(self):
        """Test that get_profile returns the correct profile for a school admin"""
        # Create a User with user_type=USER_TYPES['SCHOOL_ADMIN']
        user = User.objects.create(
            auth0_user=Auth0User.objects.create(
                auth0_id='auth0|schooladmin',
                email='schooladmin@example.com'
            ),
            first_name='School',
            last_name='Admin',
            email='schooladmin@example.com',
            user_type=USER_TYPES['SCHOOL_ADMIN']
        )
        
        # Mock a School object since we don't have access to the actual School model
        school_mock = mock.MagicMock()
        school_mock.id = uuid.uuid4()
        
        # Create a SchoolAdminProfile for the User
        # We need to use patch to avoid having to create a real School instance
        with patch('apps.users.models.SchoolAdminProfile.school') as school_field:
            school_field.return_value = school_mock
            school_admin_profile = SchoolAdminProfile.objects.create(
                user=user,
                school_id=school_mock.id,
                title='Director',
                department='Admissions',
                is_primary_contact=True,
                can_sign_documents=True
            )
            
            # Call get_profile on the User instance
            profile = user.get_profile()
            
            # Assert that the result is the SchoolAdminProfile instance
            self.assertEqual(profile, school_admin_profile)
    
    def test_get_profile_internal_user(self):
        """Test that get_profile returns the correct profile for an internal user"""
        # Create a User with user_type=USER_TYPES['UNDERWRITER']
        user = User.objects.create(
            auth0_user=Auth0User.objects.create(
                auth0_id='auth0|underwriter',
                email='underwriter@example.com'
            ),
            first_name='Under',
            last_name='Writer',
            email='underwriter@example.com',
            user_type=USER_TYPES['UNDERWRITER']
        )
        
        # Create an InternalUserProfile for the User
        internal_profile = InternalUserProfile.objects.create(
            user=user,
            employee_id='EMP12345',
            department='Underwriting',
            title='Loan Officer'
        )
        
        # Call get_profile on the User instance
        profile = user.get_profile()
        
        # Assert that the result is the InternalUserProfile instance
        self.assertEqual(profile, internal_profile)
    
    def test_get_profile_no_profile(self):
        """Test that get_profile returns None when no profile exists"""
        # Call get_profile on the User instance without creating any profile
        profile = self.user.get_profile()
        
        # Assert that the result is None
        self.assertIsNone(profile)
    
    def test_has_role(self):
        """Test that has_role correctly identifies user roles"""
        # Create a User with user_type=USER_TYPES['BORROWER']
        user = User(
            first_name='John',
            last_name='Doe',
            user_type=USER_TYPES['BORROWER']
        )
        
        # Call has_role with 'borrower'
        is_borrower = user.has_role(USER_TYPES['BORROWER'])
        
        # Assert that the result is True
        self.assertTrue(is_borrower)
        
        # Call has_role with 'underwriter'
        is_underwriter = user.has_role(USER_TYPES['UNDERWRITER'])
        
        # Assert that the result is False
        self.assertFalse(is_underwriter)
    
    def test_str_method(self):
        """Test that the __str__ method returns the expected string"""
        # Create a User with first_name='John', last_name='Doe', and email='john@example.com'
        user = User(
            first_name='John',
            last_name='Doe',
            email='john@example.com'
        )
        
        # Convert the User instance to a string
        user_str = str(user)
        
        # Assert that the result contains the user's name and email
        self.assertEqual(user_str, 'John Doe (john@example.com)')


class TestBorrowerProfile(TestCase):
    """Test case for the BorrowerProfile model"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create an Auth0User instance for testing
        self.auth0_user = Auth0User.objects.create(
            auth0_id='auth0|123456789',
            email='borrower@example.com',
            email_verified=True
        )
        
        # Create a User instance with user_type=USER_TYPES['BORROWER']
        self.user = User.objects.create(
            auth0_user=self.auth0_user,
            first_name='John',
            last_name='Doe',
            email='borrower@example.com',
            phone='(555) 123-4567',
            user_type=USER_TYPES['BORROWER']
        )
        
        # Create a BorrowerProfile instance for the User
        self.borrower_profile = BorrowerProfile.objects.create(
            user=self.user,
            ssn='123-45-6789',
            dob=timezone.now().date() - timedelta(days=365*30),  # 30 years ago
            citizenship_status=CITIZENSHIP_STATUS['US_CITIZEN'],
            address_line1='123 Main St',
            city='Anytown',
            state='CA',
            zip_code='12345',
            housing_status=HOUSING_STATUS['RENT'],
            housing_payment=Decimal('1500.00')
        )
    
    def test_borrower_profile_creation(self):
        """Test that a BorrowerProfile can be created with valid data"""
        # Create a new Auth0User for this test
        auth0_user = Auth0User.objects.create(
            auth0_id='auth0|987654321',
            email='newborrower@example.com',
            email_verified=True
        )
        
        # Create a new User
        user = User.objects.create(
            auth0_user=auth0_user,
            first_name='Jane',
            last_name='Smith',
            email='newborrower@example.com',
            phone='(555) 987-6543',
            user_type=USER_TYPES['BORROWER']
        )
        
        # Create a new BorrowerProfile with valid data
        profile = BorrowerProfile(
            user=user,
            ssn='987-65-4321',
            dob=timezone.now().date() - timedelta(days=365*25),  # 25 years ago
            citizenship_status=CITIZENSHIP_STATUS['US_CITIZEN'],
            address_line1='456 Elm St',
            city='Othertown',
            state='NY',
            zip_code='67890',
            housing_status=HOUSING_STATUS['OWN'],
            housing_payment=Decimal('2000.00')
        )
        
        # Save the BorrowerProfile instance
        profile.save()
        
        # Assert that the BorrowerProfile was created successfully
        self.assertIsNotNone(profile.id)
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.citizenship_status, CITIZENSHIP_STATUS['US_CITIZEN'])
        self.assertEqual(profile.address_line1, '456 Elm St')
        self.assertEqual(profile.city, 'Othertown')
        self.assertEqual(profile.state, 'NY')
        self.assertEqual(profile.zip_code, '67890')
        self.assertEqual(profile.housing_status, HOUSING_STATUS['OWN'])
        self.assertEqual(profile.housing_payment, Decimal('2000.00'))
    
    def test_get_full_address(self):
        """Test that get_full_address returns the correct formatted address"""
        # Set address fields on the BorrowerProfile
        self.borrower_profile.address_line1 = '123 Main St'
        self.borrower_profile.address_line2 = 'Apt 4B'
        self.borrower_profile.city = 'Anytown'
        self.borrower_profile.state = 'CA'
        self.borrower_profile.zip_code = '12345'
        
        # Call get_full_address on the BorrowerProfile instance
        address = self.borrower_profile.get_full_address()
        
        # Assert that the result is the correctly formatted address string
        expected_address = '123 Main St, Apt 4B, Anytown, CA 12345'
        self.assertEqual(address, expected_address)
        
        # Test without address_line2
        self.borrower_profile.address_line2 = None
        address = self.borrower_profile.get_full_address()
        expected_address = '123 Main St, Anytown, CA 12345'
        self.assertEqual(address, expected_address)
    
    def test_get_age(self):
        """Test that get_age calculates the correct age based on date of birth"""
        # Set dob to a date exactly 30 years ago
        today = timezone.now().date()
        thirty_years_ago = today.replace(year=today.year - 30)
        self.borrower_profile.dob = thirty_years_ago
        
        # Call get_age on the BorrowerProfile instance
        age = self.borrower_profile.get_age()
        
        # Assert that the result is 30
        self.assertEqual(age, 30)
        
        # Test with birthday tomorrow (should be 29)
        if today.month == 2 and today.day == 29:  # Handle leap year edge case
            tomorrow = today.replace(month=3, day=1)
        else:
            tomorrow = today + timedelta(days=1)
        
        dob = tomorrow.replace(year=today.year - 30)
        self.borrower_profile.dob = dob
        age = self.borrower_profile.get_age()
        self.assertEqual(age, 29)
    
    def test_is_eligible_by_age_eligible(self):
        """Test that is_eligible_by_age returns True for eligible ages"""
        # Set dob to a date that makes the borrower older than MINIMUM_AGE
        today = timezone.now().date()
        years_ago = today.replace(year=today.year - (MINIMUM_AGE + 1))
        self.borrower_profile.dob = years_ago
        
        # Call is_eligible_by_age on the BorrowerProfile instance
        eligible = self.borrower_profile.is_eligible_by_age()
        
        # Assert that the result is True
        self.assertTrue(eligible)
    
    def test_is_eligible_by_age_ineligible(self):
        """Test that is_eligible_by_age returns False for ineligible ages"""
        # Set dob to a date that makes the borrower younger than MINIMUM_AGE
        today = timezone.now().date()
        years_ago = today.replace(year=today.year - (MINIMUM_AGE - 1))
        self.borrower_profile.dob = years_ago
        
        # Call is_eligible_by_age on the BorrowerProfile instance
        eligible = self.borrower_profile.is_eligible_by_age()
        
        # Assert that the result is False
        self.assertFalse(eligible)
    
    def test_is_eligible_by_citizenship_eligible(self):
        """Test that is_eligible_by_citizenship returns True for eligible citizenship statuses"""
        # Set citizenship_status to CITIZENSHIP_STATUS['US_CITIZEN']
        self.borrower_profile.citizenship_status = CITIZENSHIP_STATUS['US_CITIZEN']
        
        # Call is_eligible_by_citizenship on the BorrowerProfile instance
        eligible = self.borrower_profile.is_eligible_by_citizenship()
        
        # Assert that the result is True
        self.assertTrue(eligible)
        
        # Test with PERMANENT_RESIDENT
        self.borrower_profile.citizenship_status = CITIZENSHIP_STATUS['PERMANENT_RESIDENT']
        eligible = self.borrower_profile.is_eligible_by_citizenship()
        self.assertTrue(eligible)
        
        # Test with ELIGIBLE_NON_CITIZEN
        self.borrower_profile.citizenship_status = CITIZENSHIP_STATUS['ELIGIBLE_NON_CITIZEN']
        eligible = self.borrower_profile.is_eligible_by_citizenship()
        self.assertTrue(eligible)
    
    def test_is_eligible_by_citizenship_ineligible(self):
        """Test that is_eligible_by_citizenship returns False for ineligible citizenship statuses"""
        # Set citizenship_status to CITIZENSHIP_STATUS['INELIGIBLE_NON_CITIZEN']
        self.borrower_profile.citizenship_status = CITIZENSHIP_STATUS['INELIGIBLE_NON_CITIZEN']
        
        # Call is_eligible_by_citizenship on the BorrowerProfile instance
        eligible = self.borrower_profile.is_eligible_by_citizenship()
        
        # Assert that the result is False
        self.assertFalse(eligible)
    
    def test_str_method(self):
        """Test that the __str__ method returns the expected string"""
        # Convert the BorrowerProfile instance to a string
        profile_str = str(self.borrower_profile)
        
        # Assert that the result contains the user's name and 'Borrower Profile'
        self.assertEqual(profile_str, 'John Doe Borrower Profile')


class TestEmploymentInfo(TestCase):
    """Test case for the EmploymentInfo model"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create an Auth0User instance for testing
        self.auth0_user = Auth0User.objects.create(
            auth0_id='auth0|123456789',
            email='borrower@example.com',
            email_verified=True
        )
        
        # Create a User instance with user_type=USER_TYPES['BORROWER']
        self.user = User.objects.create(
            auth0_user=self.auth0_user,
            first_name='John',
            last_name='Doe',
            email='borrower@example.com',
            phone='(555) 123-4567',
            user_type=USER_TYPES['BORROWER']
        )
        
        # Create a BorrowerProfile instance for the User
        self.borrower_profile = BorrowerProfile.objects.create(
            user=self.user,
            ssn='123-45-6789',
            dob=timezone.now().date() - timedelta(days=365*30),
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
            employer_name='ACME Inc.',
            occupation='Software Developer',
            employer_phone='(555) 987-6543',
            years_employed=2,
            months_employed=6,
            annual_income=Decimal('85000.00'),
            other_income=Decimal('5000.00'),
            other_income_source='Freelance Work'
        )
    
    def test_employment_info_creation(self):
        """Test that an EmploymentInfo can be created with valid data"""
        # Create a new EmploymentInfo with valid data
        employment_info = EmploymentInfo(
            profile=self.borrower_profile,
            employment_type=EMPLOYMENT_TYPES['PART_TIME'],
            employer_name='XYZ Corp',
            occupation='Designer',
            employer_phone='(555) 555-5555',
            years_employed=1,
            months_employed=3,
            annual_income=Decimal('45000.00')
        )
        
        # Save the EmploymentInfo instance
        employment_info.save()
        
        # Assert that the EmploymentInfo was created successfully
        self.assertIsNotNone(employment_info.id)
        self.assertEqual(employment_info.profile, self.borrower_profile)
        self.assertEqual(employment_info.employment_type, EMPLOYMENT_TYPES['PART_TIME'])
        self.assertEqual(employment_info.employer_name, 'XYZ Corp')
        self.assertEqual(employment_info.occupation, 'Designer')
        self.assertEqual(employment_info.employer_phone, '(555) 555-5555')
        self.assertEqual(employment_info.years_employed, 1)
        self.assertEqual(employment_info.months_employed, 3)
        self.assertEqual(employment_info.annual_income, Decimal('45000.00'))
        self.assertIsNone(employment_info.other_income)
        self.assertIsNone(employment_info.other_income_source)
    
    def test_get_total_income(self):
        """Test that get_total_income correctly calculates total income"""
        # Set annual_income to 50000 and other_income to 10000
        self.employment_info.annual_income = Decimal('50000.00')
        self.employment_info.other_income = Decimal('10000.00')
        
        # Call get_total_income on the EmploymentInfo instance
        total_income = self.employment_info.get_total_income()
        
        # Assert that the result is 60000
        self.assertEqual(total_income, Decimal('60000.00'))
        
        # Test with None other_income
        self.employment_info.other_income = None
        total_income = self.employment_info.get_total_income()
        self.assertEqual(total_income, Decimal('50000.00'))
    
    def test_get_monthly_income(self):
        """Test that get_monthly_income correctly calculates monthly income"""
        # Set annual_income to 60000 and other_income to 0
        self.employment_info.annual_income = Decimal('60000.00')
        self.employment_info.other_income = Decimal('0.00')
        
        # Call get_monthly_income on the EmploymentInfo instance
        monthly_income = self.employment_info.get_monthly_income()
        
        # Assert that the result is 5000
        self.assertEqual(monthly_income, Decimal('5000.00'))
        
        # Test with some other_income
        self.employment_info.other_income = Decimal('12000.00')
        monthly_income = self.employment_info.get_monthly_income()
        self.assertEqual(monthly_income, Decimal('6000.00'))
    
    def test_get_total_employment_duration(self):
        """Test that get_total_employment_duration correctly calculates total duration in months"""
        # Set years_employed to 2 and months_employed to 6
        self.employment_info.years_employed = 2
        self.employment_info.months_employed = 6
        
        # Call get_total_employment_duration on the EmploymentInfo instance
        duration = self.employment_info.get_total_employment_duration()
        
        # Assert that the result is 30 months
        self.assertEqual(duration, 30)
    
    def test_meets_minimum_employment_meets(self):
        """Test that meets_minimum_employment returns True when duration meets minimum"""
        # Set years_employed and months_employed to exceed MIN_EMPLOYMENT_DURATION_MONTHS
        self.employment_info.years_employed = 1
        self.employment_info.months_employed = 0
        
        # Ensure the minimum is less than what we set
        self.assertTrue(12 >= MIN_EMPLOYMENT_DURATION_MONTHS)
        
        # Call meets_minimum_employment on the EmploymentInfo instance
        meets_minimum = self.employment_info.meets_minimum_employment()
        
        # Assert that the result is True
        self.assertTrue(meets_minimum)
    
    def test_meets_minimum_employment_below(self):
        """Test that meets_minimum_employment returns False when duration is below minimum"""
        # Set years_employed and months_employed to be less than MIN_EMPLOYMENT_DURATION_MONTHS
        self.employment_info.years_employed = 0
        self.employment_info.months_employed = MIN_EMPLOYMENT_DURATION_MONTHS - 1
        
        # Call meets_minimum_employment on the EmploymentInfo instance
        meets_minimum = self.employment_info.meets_minimum_employment()
        
        # Assert that the result is False
        self.assertFalse(meets_minimum)
    
    def test_meets_minimum_income_meets(self):
        """Test that meets_minimum_income returns True when income meets minimum"""
        # Set annual_income to exceed MINIMUM_INCOME
        self.employment_info.annual_income = MINIMUM_INCOME + Decimal('1000.00')
        self.employment_info.other_income = Decimal('0.00')
        
        # Call meets_minimum_income on the EmploymentInfo instance
        meets_minimum = self.employment_info.meets_minimum_income()
        
        # Assert that the result is True
        self.assertTrue(meets_minimum)
        
        # Test with combined income meeting minimum
        self.employment_info.annual_income = MINIMUM_INCOME - Decimal('1000.00')
        self.employment_info.other_income = Decimal('2000.00')
        meets_minimum = self.employment_info.meets_minimum_income()
        self.assertTrue(meets_minimum)
    
    def test_meets_minimum_income_below(self):
        """Test that meets_minimum_income returns False when income is below minimum"""
        # Set annual_income to be less than MINIMUM_INCOME
        self.employment_info.annual_income = MINIMUM_INCOME - Decimal('1000.00')
        self.employment_info.other_income = Decimal('0.00')
        
        # Call meets_minimum_income on the EmploymentInfo instance
        meets_minimum = self.employment_info.meets_minimum_income()
        
        # Assert that the result is False
        self.assertFalse(meets_minimum)
    
    def test_str_method(self):
        """Test that the __str__ method returns the expected string"""
        # Convert the EmploymentInfo instance to a string
        employment_str = str(self.employment_info)
        
        # Assert that the result contains the employer name and occupation
        self.assertEqual(employment_str, 'ACME Inc. - Software Developer')


class TestSchoolAdminProfile(TestCase):
    """Test case for the SchoolAdminProfile model"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create an Auth0User instance for testing
        self.auth0_user = Auth0User.objects.create(
            auth0_id='auth0|schooladmin',
            email='admin@school.edu',
            email_verified=True
        )
        
        # Create a User instance with user_type=USER_TYPES['SCHOOL_ADMIN']
        self.user = User.objects.create(
            auth0_user=self.auth0_user,
            first_name='Sarah',
            last_name='Johnson',
            email='admin@school.edu',
            phone='(555) 123-4567',
            user_type=USER_TYPES['SCHOOL_ADMIN']
        )
        
        # Create a mock School instance
        self.school_mock = mock.MagicMock()
        self.school_mock.id = uuid.uuid4()
        self.school_mock.name = 'ABC School'
        
        # Mock the programs queryset
        self.programs_mock = mock.MagicMock()
        self.school_mock.programs.all.return_value = self.programs_mock
        
        # Create a SchoolAdminProfile instance for the User and School
        with patch('apps.users.models.SchoolAdminProfile.school') as school_field:
            school_field.return_value = self.school_mock
            self.school_admin_profile = SchoolAdminProfile.objects.create(
                user=self.user,
                school_id=self.school_mock.id,
                title='Director',
                department='Admissions',
                is_primary_contact=True,
                can_sign_documents=True
            )
    
    def test_school_admin_profile_creation(self):
        """Test that a SchoolAdminProfile can be created with valid data"""
        # Create a new Auth0User for this test
        auth0_user = Auth0User.objects.create(
            auth0_id='auth0|newadmin',
            email='newadmin@school.edu',
            email_verified=True
        )
        
        # Create a new User
        user = User.objects.create(
            auth0_user=auth0_user,
            first_name='New',
            last_name='Admin',
            email='newadmin@school.edu',
            phone='(555) 987-6543',
            user_type=USER_TYPES['SCHOOL_ADMIN']
        )
        
        # Create a mock School
        school_mock = mock.MagicMock()
        school_mock.id = uuid.uuid4()
        
        # Create a new SchoolAdminProfile with valid data
        with patch('apps.users.models.SchoolAdminProfile.school') as school_field:
            school_field.return_value = school_mock
            profile = SchoolAdminProfile(
                user=user,
                school_id=school_mock.id,
                title='Assistant Director',
                department='Financial Aid',
                is_primary_contact=False,
                can_sign_documents=True
            )
            
            # Save the SchoolAdminProfile instance
            profile.save()
            
            # Assert that the SchoolAdminProfile was created successfully
            self.assertIsNotNone(profile.id)
            self.assertEqual(profile.user, user)
            self.assertEqual(profile.school_id, school_mock.id)
            self.assertEqual(profile.title, 'Assistant Director')
            self.assertEqual(profile.department, 'Financial Aid')
            self.assertFalse(profile.is_primary_contact)
            self.assertTrue(profile.can_sign_documents)
    
    def test_get_managed_programs(self):
        """Test that get_managed_programs returns the correct programs"""
        # Call get_managed_programs on the SchoolAdminProfile instance
        with patch('apps.users.models.SchoolAdminProfile.school') as school_field:
            school_field.return_value = self.school_mock
            programs = self.school_admin_profile.get_managed_programs()
            
            # Assert that the result contains the expected Program instances
            self.assertEqual(programs, self.programs_mock)
            self.school_mock.programs.all.assert_called_once()
    
    def test_str_method(self):
        """Test that the __str__ method returns the expected string"""
        # Mock the string representation
        with patch('apps.users.models.SchoolAdminProfile.school') as school_field:
            school_field.return_value = self.school_mock
            
            # Convert the SchoolAdminProfile instance to a string
            profile_str = str(self.school_admin_profile)
            
            # Assert that the result contains the user's name and school name
            self.assertEqual(profile_str, 'Sarah Johnson - ABC School')


class TestInternalUserProfile(TestCase):
    """Test case for the InternalUserProfile model"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create an Auth0User instance for testing
        self.auth0_user = Auth0User.objects.create(
            auth0_id='auth0|underwriter',
            email='underwriter@loanmgmt.com',
            email_verified=True
        )
        
        # Create a User instance with user_type=USER_TYPES['UNDERWRITER']
        self.user = User.objects.create(
            auth0_user=self.auth0_user,
            first_name='Robert',
            last_name='Taylor',
            email='underwriter@loanmgmt.com',
            phone='(555) 123-4567',
            user_type=USER_TYPES['UNDERWRITER']
        )
        
        # Create a supervisor User instance
        self.supervisor_auth0 = Auth0User.objects.create(
            auth0_id='auth0|supervisor',
            email='supervisor@loanmgmt.com',
            email_verified=True
        )
        
        self.supervisor = User.objects.create(
            auth0_user=self.supervisor_auth0,
            first_name='Supervisor',
            last_name='User',
            email='supervisor@loanmgmt.com',
            phone='(555) 987-6543',
            user_type=USER_TYPES['UNDERWRITER']
        )
        
        # Create an InternalUserProfile for the supervisor
        self.supervisor_profile = InternalUserProfile.objects.create(
            user=self.supervisor,
            employee_id='EMP001',
            department='Underwriting',
            title='Senior Underwriter'
        )
        
        # Create an InternalUserProfile instance for the User
        self.internal_profile = InternalUserProfile.objects.create(
            user=self.user,
            employee_id='EMP002',
            department='Underwriting',
            title='Junior Underwriter',
            supervisor=self.supervisor_profile
        )
    
    def test_internal_user_profile_creation(self):
        """Test that an InternalUserProfile can be created with valid data"""
        # Create a new Auth0User for this test
        auth0_user = Auth0User.objects.create(
            auth0_id='auth0|newinternal',
            email='newinternal@loanmgmt.com',
            email_verified=True
        )
        
        # Create a new User
        user = User.objects.create(
            auth0_user=auth0_user,
            first_name='New',
            last_name='Internal',
            email='newinternal@loanmgmt.com',
            phone='(555) 555-5555',
            user_type=USER_TYPES['QC']
        )
        
        # Create a new InternalUserProfile with valid data
        profile = InternalUserProfile(
            user=user,
            employee_id='EMP003',
            department='Quality Control',
            title='QC Specialist',
            supervisor=self.supervisor_profile
        )
        
        # Save the InternalUserProfile instance
        profile.save()
        
        # Assert that the InternalUserProfile was created successfully
        self.assertIsNotNone(profile.id)
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.employee_id, 'EMP003')
        self.assertEqual(profile.department, 'Quality Control')
        self.assertEqual(profile.title, 'QC Specialist')
        self.assertEqual(profile.supervisor, self.supervisor_profile)
    
    def test_get_subordinates(self):
        """Test that get_subordinates returns the correct subordinate users"""
        # Create multiple InternalUserProfile instances with the test user as supervisor
        auth0_user1 = Auth0User.objects.create(
            auth0_id='auth0|sub1',
            email='sub1@loanmgmt.com',
            email_verified=True
        )
        
        user1 = User.objects.create(
            auth0_user=auth0_user1,
            first_name='Subordinate',
            last_name='One',
            email='sub1@loanmgmt.com',
            phone='(555) 111-1111',
            user_type=USER_TYPES['UNDERWRITER']
        )
        
        sub_profile1 = InternalUserProfile.objects.create(
            user=user1,
            employee_id='EMP101',
            department='Underwriting',
            title='Assistant Underwriter',
            supervisor=self.supervisor_profile
        )
        
        auth0_user2 = Auth0User.objects.create(
            auth0_id='auth0|sub2',
            email='sub2@loanmgmt.com',
            email_verified=True
        )
        
        user2 = User.objects.create(
            auth0_user=auth0_user2,
            first_name='Subordinate',
            last_name='Two',
            email='sub2@loanmgmt.com',
            phone='(555) 222-2222',
            user_type=USER_TYPES['UNDERWRITER']
        )
        
        sub_profile2 = InternalUserProfile.objects.create(
            user=user2,
            employee_id='EMP102',
            department='Underwriting',
            title='Assistant Underwriter',
            supervisor=self.supervisor_profile
        )
        
        # Call get_subordinates on the supervisor's InternalUserProfile instance
        subordinates = self.supervisor_profile.get_subordinates()
        
        # Assert that the result contains all the subordinate profiles
        self.assertEqual(subordinates.count(), 3)  # self.internal_profile and the two we just created
        self.assertIn(self.internal_profile, subordinates)
        self.assertIn(sub_profile1, subordinates)
        self.assertIn(sub_profile2, subordinates)
    
    def test_str_method(self):
        """Test that the __str__ method returns the expected string"""
        # Create an InternalUserProfile for a User with a known name, title='Underwriter', and department='Loan Processing'
        auth0_user = Auth0User.objects.create(
            auth0_id='auth0|teststr',
            email='teststr@loanmgmt.com',
            email_verified=True
        )
        
        user = User.objects.create(
            auth0_user=auth0_user,
            first_name='Test',
            last_name='User',
            email='teststr@loanmgmt.com',
            phone='(555) 333-3333',
            user_type=USER_TYPES['UNDERWRITER']
        )
        
        profile = InternalUserProfile.objects.create(
            user=user,
            employee_id='EMP999',
            department='Loan Processing',
            title='Underwriter'
        )
        
        # Convert the InternalUserProfile instance to a string
        profile_str = str(profile)
        
        # Assert that the result contains the user's name, title, and department
        self.assertEqual(profile_str, 'Test User - Underwriter, Loan Processing')


class TestUserPermission(TestCase):
    """Test case for the UserPermission model"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create an Auth0User instance for testing
        self.auth0_user = Auth0User.objects.create(
            auth0_id='auth0|123456789',
            email='test@example.com',
            email_verified=True
        )
        
        # Create a User instance
        self.user = User.objects.create(
            auth0_user=self.auth0_user,
            first_name='John',
            last_name='Doe',
            email='test@example.com',
            phone='(555) 123-4567',
            user_type=USER_TYPES['BORROWER']
        )
        
        # Create a UserPermission instance for the User
        self.permission = UserPermission.objects.create(
            user=self.user,
            permission_name='view_application',
            resource_type='application',
            resource_id=uuid.uuid4(),
            is_granted=True
        )
    
    def test_user_permission_creation(self):
        """Test that a UserPermission can be created with valid data"""
        # Create a new UserPermission with valid data
        permission = UserPermission(
            user=self.user,
            permission_name='edit_application',
            resource_type='application',
            resource_id=uuid.uuid4(),
            is_granted=True
        )
        
        # Save the UserPermission instance
        permission.save()
        
        # Assert that the UserPermission was created successfully
        self.assertIsNotNone(permission.id)
        self.assertEqual(permission.user, self.user)
        self.assertEqual(permission.permission_name, 'edit_application')
        self.assertEqual(permission.resource_type, 'application')
        self.assertIsNotNone(permission.resource_id)
        self.assertTrue(permission.is_granted)
    
    def test_str_method(self):
        """Test that the __str__ method returns the expected string"""
        # Convert the UserPermission instance to a string
        permission_str = str(self.permission)
        
        # Assert that the result contains the user's name, permission name, and resource type
        status = "granted" if self.permission.is_granted else "denied"
        expected_str = f"John Doe - view_application on application ({status})"
        self.assertEqual(permission_str, expected_str)