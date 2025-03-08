"""
Defines the user data models for the loan management system.

This module implements the user-related data models for the loan management system, 
including the core User model and role-specific profiles for different user types 
(borrowers, co-borrowers, school administrators, underwriters, QC personnel, and 
system administrators).
"""

from django.db import models  # Django 4.2+
from django.utils import timezone  # Django 4.2+
from decimal import Decimal  # standard library

from core.models import (
    CoreModel, UUIDModel, TimeStampedModel, 
    SoftDeleteModel, AuditableModel, ActiveManager
)
from apps.authentication.models import Auth0User
from utils.constants import (
    USER_TYPES, EMPLOYMENT_TYPES, HOUSING_STATUS, 
    CITIZENSHIP_STATUS, US_STATES
)
from utils.encryption import EncryptedField

# User role choices for form fields and validation
USER_ROLE_CHOICES = (
    (USER_TYPES['BORROWER'], 'Borrower'),
    (USER_TYPES['CO_BORROWER'], 'Co-Borrower'),
    (USER_TYPES['SCHOOL_ADMIN'], 'School Administrator'),
    (USER_TYPES['UNDERWRITER'], 'Underwriter'),
    (USER_TYPES['QC'], 'Quality Control'),
    (USER_TYPES['SYSTEM_ADMIN'], 'System Administrator')
)


class User(CoreModel):
    """
    Core user model that extends CoreModel and links to Auth0User for authentication.
    
    This model serves as the primary user record in the system and is linked to role-specific
    profiles based on the user's type.
    """
    auth0_user = models.OneToOneField(
        Auth0User,
        on_delete=models.CASCADE,
        related_name='application_user'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    user_type = models.CharField(
        max_length=20,
        choices=USER_ROLE_CHOICES,
        default=USER_TYPES['BORROWER']
    )
    is_active = models.BooleanField(default=True)
    
    # Managers
    objects = ActiveManager()
    all_objects = models.Manager()
    
    def get_full_name(self):
        """
        Returns the user's full name.
        
        Returns:
            str: User's full name
        """
        return f"{self.first_name} {self.last_name}"
    
    def get_profile(self):
        """
        Returns the user's role-specific profile.
        
        Returns:
            object: Role-specific profile object or None
        """
        if self.user_type == USER_TYPES['BORROWER'] or self.user_type == USER_TYPES['CO_BORROWER']:
            try:
                return self.borrowerprofile
            except BorrowerProfile.DoesNotExist:
                return None
        elif self.user_type == USER_TYPES['SCHOOL_ADMIN']:
            try:
                return self.schooladminprofile
            except SchoolAdminProfile.DoesNotExist:
                return None
        elif self.user_type in [USER_TYPES['UNDERWRITER'], USER_TYPES['QC'], USER_TYPES['SYSTEM_ADMIN']]:
            try:
                return self.internaluserprofile
            except InternalUserProfile.DoesNotExist:
                return None
        return None
    
    def has_role(self, role):
        """
        Checks if the user has a specific role.
        
        Args:
            role (str): The role to check against
            
        Returns:
            bool: True if user has the role, False otherwise
        """
        return self.user_type == role
    
    def __str__(self):
        """
        String representation of the User instance.
        
        Returns:
            str: User's full name and email
        """
        return f"{self.get_full_name()} ({self.email})"


class BorrowerProfile(CoreModel):
    """
    Profile model for borrowers with personal and financial information.
    
    This model stores additional information for users who are borrowers or co-borrowers,
    including personal, financial, and eligibility information needed for loan applications.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='borrowerprofile'
    )
    ssn = models.CharField(max_length=255)  # Stored encrypted, accessed via get_ssn/set_ssn
    dob = models.DateField()
    citizenship_status = models.CharField(
        max_length=30,
        choices=[(v, v) for v in CITIZENSHIP_STATUS.values()],
        default=CITIZENSHIP_STATUS['US_CITIZEN']
    )
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(
        max_length=2,
        choices=[(k, v) for k, v in US_STATES.items()]
    )
    zip_code = models.CharField(max_length=10)
    housing_status = models.CharField(
        max_length=20,
        choices=[(v, v) for v in HOUSING_STATUS.values()],
        default=HOUSING_STATUS['RENT']
    )
    housing_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Managers
    objects = ActiveManager()
    all_objects = models.Manager()
    
    def get_ssn(self):
        """
        Gets the decrypted SSN.
        
        Returns:
            str: Decrypted SSN
        """
        from utils.encryption import decrypt_ssn
        return decrypt_ssn(self.ssn)
    
    def set_ssn(self, value):
        """
        Sets the SSN with encryption.
        
        Args:
            value (str): The SSN value to encrypt and store
        """
        from utils.encryption import encrypt_ssn
        self.ssn = encrypt_ssn(value)
    
    def get_full_address(self):
        """
        Returns the borrower's full address as a formatted string.
        
        Returns:
            str: Formatted full address
        """
        address = f"{self.address_line1}"
        if self.address_line2:
            address += f", {self.address_line2}"
        address += f", {self.city}, {self.state} {self.zip_code}"
        return address
    
    def get_age(self):
        """
        Calculates the borrower's age based on date of birth.
        
        Returns:
            int: Borrower's age in years
        """
        today = timezone.now().date()
        birth_date = self.dob
        age = today.year - birth_date.year
        
        # Adjust age if birthday hasn't occurred yet this year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
            
        return age
    
    def is_eligible_by_age(self):
        """
        Checks if the borrower meets the minimum age requirement.
        
        Returns:
            bool: True if eligible, False otherwise
        """
        from utils.constants import MINIMUM_AGE
        return self.get_age() >= MINIMUM_AGE
    
    def is_eligible_by_citizenship(self):
        """
        Checks if the borrower meets citizenship requirements.
        
        Returns:
            bool: True if eligible, False otherwise
        """
        eligible_statuses = [
            CITIZENSHIP_STATUS['US_CITIZEN'],
            CITIZENSHIP_STATUS['PERMANENT_RESIDENT'],
            CITIZENSHIP_STATUS['ELIGIBLE_NON_CITIZEN']
        ]
        return self.citizenship_status in eligible_statuses
    
    def __str__(self):
        """
        String representation of the BorrowerProfile instance.
        
        Returns:
            str: User's name with 'Borrower Profile'
        """
        return f"{self.user.get_full_name()} Borrower Profile"


class EmploymentInfo(CoreModel):
    """
    Model for storing borrower employment and income information.
    
    This model contains employment details and income information for borrowers,
    which is used during the loan application and underwriting process.
    """
    profile = models.ForeignKey(
        BorrowerProfile,
        on_delete=models.CASCADE,
        related_name='employment_info'
    )
    employment_type = models.CharField(
        max_length=20,
        choices=[(v, v) for v in EMPLOYMENT_TYPES.values()],
        default=EMPLOYMENT_TYPES['FULL_TIME']
    )
    employer_name = models.CharField(max_length=100)
    occupation = models.CharField(max_length=100)
    employer_phone = models.CharField(max_length=20)
    years_employed = models.IntegerField(default=0)
    months_employed = models.IntegerField(default=0)
    annual_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    other_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        blank=True,
        null=True
    )
    other_income_source = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    
    # Managers
    objects = ActiveManager()
    all_objects = models.Manager()
    
    def get_total_income(self):
        """
        Calculates the total annual income including other income.
        
        Returns:
            Decimal: Total annual income
        """
        other = self.other_income or Decimal('0.00')
        return self.annual_income + other
    
    def get_monthly_income(self):
        """
        Calculates the monthly income based on annual income.
        
        Returns:
            Decimal: Monthly income
        """
        return self.get_total_income() / Decimal('12.0')
    
    def get_total_employment_duration(self):
        """
        Calculates the total employment duration in months.
        
        Returns:
            int: Total employment duration in months
        """
        return (self.years_employed * 12) + self.months_employed
    
    def meets_minimum_employment(self):
        """
        Checks if the employment duration meets minimum requirements.
        
        Returns:
            bool: True if meets minimum, False otherwise
        """
        from utils.constants import MIN_EMPLOYMENT_DURATION_MONTHS
        return self.get_total_employment_duration() >= MIN_EMPLOYMENT_DURATION_MONTHS
    
    def meets_minimum_income(self):
        """
        Checks if the income meets minimum requirements.
        
        Returns:
            bool: True if meets minimum, False otherwise
        """
        from utils.constants import MINIMUM_INCOME
        return self.get_total_income() >= MINIMUM_INCOME
    
    def __str__(self):
        """
        String representation of the EmploymentInfo instance.
        
        Returns:
            str: Employment information summary
        """
        return f"{self.employer_name} - {self.occupation}"


class SchoolAdminProfile(CoreModel):
    """
    Profile model for school administrators.
    
    This model contains additional information for users who are school administrators,
    including their role within the school and document signing capabilities.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='schooladminprofile'
    )
    school = models.ForeignKey(
        'schools.School',  # Using string reference to avoid circular import
        on_delete=models.CASCADE,
        related_name='administrators'
    )
    title = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    is_primary_contact = models.BooleanField(default=False)
    can_sign_documents = models.BooleanField(default=False)
    
    # Managers
    objects = ActiveManager()
    all_objects = models.Manager()
    
    def get_managed_programs(self):
        """
        Returns programs associated with the administrator's school.
        
        Returns:
            QuerySet: QuerySet of Program objects
        """
        return self.school.programs.all()
    
    def __str__(self):
        """
        String representation of the SchoolAdminProfile instance.
        
        Returns:
            str: User's name with school name
        """
        return f"{self.user.get_full_name()} - {self.school.name}"


class InternalUserProfile(CoreModel):
    """
    Profile model for internal staff (underwriters, QC, system admins).
    
    This model contains additional information for internal users including
    their employee information, department, and reporting structure.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='internaluserprofile'
    )
    employee_id = models.CharField(max_length=50)
    department = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    supervisor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates'
    )
    
    # Managers
    objects = ActiveManager()
    all_objects = models.Manager()
    
    def get_subordinates(self):
        """
        Returns users who have this user as their supervisor.
        
        Returns:
            QuerySet: QuerySet of InternalUserProfile objects
        """
        return InternalUserProfile.objects.filter(supervisor=self)
    
    def __str__(self):
        """
        String representation of the InternalUserProfile instance.
        
        Returns:
            str: User's name with title and department
        """
        return f"{self.user.get_full_name()} - {self.title}, {self.department}"


class UserPermission(CoreModel):
    """
    Model for storing custom permissions for users beyond their role-based permissions.
    
    This model allows for granular permission control on specific resources,
    enabling exceptions to the standard role-based access control.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='custom_permissions'
    )
    permission_name = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=100)
    resource_id = models.UUIDField(null=True, blank=True)
    is_granted = models.BooleanField(default=True)
    
    # Managers
    objects = ActiveManager()
    all_objects = models.Manager()
    
    def __str__(self):
        """
        String representation of the UserPermission instance.
        
        Returns:
            str: Permission details
        """
        status = "granted" if self.is_granted else "denied"
        return f"{self.user.get_full_name()} - {self.permission_name} on {self.resource_type} ({status})"