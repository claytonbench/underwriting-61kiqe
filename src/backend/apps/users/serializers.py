"""
Defines serializers for user-related data in the loan management system.

These serializers handle validation, data transformation, and representation for user models,
profiles, roles, and permissions, supporting the comprehensive user management system with
role-based access control.
"""

from rest_framework import serializers  # version 3.14+
from django.core.validators import validate_email  # version 4.2+
from django.contrib.auth.password_validation import validate_password  # version 4.2+

from ../../core.serializers import BaseSerializer, BaseModelSerializer, SensitiveDataMixin
from ../../core.exceptions import ValidationException
from .models import (
    User, Role, Permission, UserRole, RolePermission,
    BorrowerProfile, EmploymentInfo, SchoolAdminProfile, InternalUserProfile,
    USER_ROLE_CHOICES
)
from ../../utils.constants import (
    EMPLOYMENT_TYPES, HOUSING_STATUS, CITIZENSHIP_STATUS, US_STATES
)

# Define sensitive fields that need special handling
SENSITIVE_FIELDS = ['ssn', 'tax_id', 'dob']


class UserSerializer(BaseModelSerializer):
    """
    Basic serializer for User model with minimal fields.
    """
    
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 
            'user_type', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_profile_type(self, obj):
        """
        Returns the profile type based on user_type.
        
        Args:
            obj (User): The user instance
            
        Returns:
            str: Profile type name
        """
        if obj.user_type in ['borrower', 'co_borrower']:
            return 'borrower'
        elif obj.user_type == 'school_admin':
            return 'school_admin'
        elif obj.user_type in ['underwriter', 'qc', 'system_admin']:
            return 'internal'
        return None


class UserDetailSerializer(BaseModelSerializer):
    """
    Detailed serializer for User model with profile information.
    """
    
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 
            'user_type', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """
        Customizes the representation to include profile data.
        
        Args:
            instance (User): The user instance
            
        Returns:
            dict: Serialized user data with profile information
        """
        representation = super().to_representation(instance)
        
        # Get the user's profile based on user_type
        profile = instance.get_profile()
        
        if profile:
            # Add profile data based on user_type
            if instance.user_type in ['borrower', 'co_borrower']:
                profile_serializer = BorrowerProfileSerializer(profile)
                representation['borrower_profile'] = profile_serializer.data
                
                # Add employment information if available
                employment_infos = profile.employment_info.all()
                if employment_infos.exists():
                    employment_serializer = EmploymentInfoSerializer(employment_infos.first())
                    representation['employment_info'] = employment_serializer.data
                
            elif instance.user_type == 'school_admin':
                profile_serializer = SchoolAdminProfileSerializer(profile)
                representation['school_admin_profile'] = profile_serializer.data
                
            elif instance.user_type in ['underwriter', 'qc', 'system_admin']:
                profile_serializer = InternalUserProfileSerializer(profile)
                representation['internal_user_profile'] = profile_serializer.data
        
        # Get user roles if available
        user_roles = UserRole.objects.filter(user=instance)
        if user_roles.exists():
            role_serializer = UserRoleSerializer(user_roles, many=True)
            representation['roles'] = role_serializer.data
        
        return representation


class UserCreateSerializer(BaseSerializer):
    """
    Serializer for creating new User instances.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    user_type = serializers.ChoiceField(choices=USER_ROLE_CHOICES, required=True)
    is_active = serializers.BooleanField(default=True)
    profile_data = serializers.DictField(required=True)
    
    def validate_email(self, value):
        """
        Validates the email field.
        
        Args:
            value (str): The email value to validate
            
        Returns:
            str: Validated email
            
        Raises:
            ValidationException: If email validation fails
        """
        if not value:
            raise ValidationException("Email is required.")
        
        try:
            validate_email(value)
        except Exception as e:
            raise ValidationException(str(e))
        
        # Check if email is already in use
        if User.objects.filter(email=value.lower()).exists():
            raise ValidationException("Email address is already in use.")
        
        # Return lowercase email
        return value.lower()
    
    def validate_password(self, value):
        """
        Validates the password field.
        
        Args:
            value (str): The password value to validate
            
        Returns:
            str: Validated password
            
        Raises:
            ValidationException: If password validation fails
        """
        if not value:
            raise ValidationException("Password is required.")
        
        try:
            validate_password(value)
        except Exception as e:
            raise ValidationException(str(e))
        
        return value
    
    def validate_profile_data(self, value):
        """
        Validates the profile data based on user type.
        
        Args:
            value (dict): The profile data to validate
            
        Returns:
            dict: Validated profile data
            
        Raises:
            ValidationException: If profile data validation fails
        """
        user_type = self.initial_data.get('user_type')
        
        if not user_type:
            raise ValidationException("User type is required.")
        
        if user_type in ['borrower', 'co_borrower']:
            # Validate borrower profile data
            required_fields = [
                'ssn', 'dob', 'citizenship_status', 'address_line1', 
                'city', 'state', 'zip_code', 'housing_status', 'housing_payment'
            ]
            
            for field in required_fields:
                if field not in value:
                    raise ValidationException(f"'{field}' is required for borrower profile.")
            
            # Validate employment info if provided
            if 'employment_info' in value:
                employment_info = value['employment_info']
                emp_required_fields = [
                    'employment_type', 'employer_name', 'occupation', 
                    'years_employed', 'months_employed', 'annual_income'
                ]
                
                for field in emp_required_fields:
                    if field not in employment_info:
                        raise ValidationException(f"'{field}' is required in employment info.")
        
        elif user_type == 'school_admin':
            # Validate school admin profile data
            required_fields = ['school', 'title', 'department', 'is_primary_contact', 'can_sign_documents']
            
            for field in required_fields:
                if field not in value:
                    raise ValidationException(f"'{field}' is required for school admin profile.")
        
        elif user_type in ['underwriter', 'qc', 'system_admin']:
            # Validate internal user profile data
            required_fields = ['employee_id', 'department', 'title']
            
            for field in required_fields:
                if field not in value:
                    raise ValidationException(f"'{field}' is required for internal user profile.")
        
        return value


class UserUpdateSerializer(BaseSerializer):
    """
    Serializer for updating existing User instances.
    """
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)
    profile_data = serializers.DictField(required=False)
    
    def validate_profile_data(self, value):
        """
        Validates the profile data based on user type.
        
        Args:
            value (dict): The profile data to validate
            
        Returns:
            dict: Validated profile data
            
        Raises:
            ValidationException: If profile data validation fails
        """
        user = self.context.get('user')
        
        if not user:
            raise ValidationException("User context is required.")
        
        user_type = user.user_type
        
        if user_type in ['borrower', 'co_borrower']:
            # Validate borrower profile data
            for field in value:
                if field not in [
                    'address_line1', 'address_line2', 'city', 'state', 'zip_code',
                    'housing_status', 'housing_payment', 'citizenship_status'
                ]:
                    raise ValidationException(f"'{field}' is not a valid borrower profile field.")
            
            # Validate employment info if provided
            if 'employment_info' in value:
                employment_info = value['employment_info']
                for field in employment_info:
                    if field not in [
                        'employment_type', 'employer_name', 'occupation', 'employer_phone',
                        'years_employed', 'months_employed', 'annual_income',
                        'other_income', 'other_income_source'
                    ]:
                        raise ValidationException(f"'{field}' is not a valid employment info field.")
        
        elif user_type == 'school_admin':
            # Validate school admin profile data
            for field in value:
                if field not in [
                    'title', 'department', 'is_primary_contact', 'can_sign_documents'
                ]:
                    raise ValidationException(f"'{field}' is not a valid school admin profile field.")
        
        elif user_type in ['underwriter', 'qc', 'system_admin']:
            # Validate internal user profile data
            for field in value:
                if field not in [
                    'employee_id', 'department', 'title', 'supervisor'
                ]:
                    raise ValidationException(f"'{field}' is not a valid internal user profile field.")
        
        return value


class BorrowerProfileSerializer(BaseModelSerializer, SensitiveDataMixin):
    """
    Serializer for BorrowerProfile model.
    """
    sensitive_fields = ['ssn', 'dob']
    
    class Meta:
        model = BorrowerProfile
        fields = [
            'id', 'user', 'ssn', 'dob', 'citizenship_status',
            'address_line1', 'address_line2', 'city', 'state', 'zip_code',
            'housing_status', 'housing_payment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_full_address(self, obj):
        """
        Returns the borrower's full address as a formatted string.
        
        Args:
            obj (BorrowerProfile): The borrower profile instance
            
        Returns:
            str: Formatted full address
        """
        return obj.get_full_address()
    
    def get_age(self, obj):
        """
        Calculates the borrower's age based on date of birth.
        
        Args:
            obj (BorrowerProfile): The borrower profile instance
            
        Returns:
            int: Borrower's age in years
        """
        return obj.get_age()


class EmploymentInfoSerializer(BaseModelSerializer):
    """
    Serializer for EmploymentInfo model.
    """
    
    class Meta:
        model = EmploymentInfo
        fields = [
            'id', 'profile', 'employment_type', 'employer_name', 
            'occupation', 'employer_phone', 'years_employed', 'months_employed',
            'annual_income', 'other_income', 'other_income_source',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'profile', 'created_at', 'updated_at']
    
    def get_total_income(self, obj):
        """
        Calculates the total annual income including other income.
        
        Args:
            obj (EmploymentInfo): The employment info instance
            
        Returns:
            Decimal: Total annual income
        """
        return obj.get_total_income()
    
    def get_monthly_income(self, obj):
        """
        Calculates the monthly income based on annual income.
        
        Args:
            obj (EmploymentInfo): The employment info instance
            
        Returns:
            Decimal: Monthly income
        """
        return obj.get_monthly_income()
    
    def get_total_employment_duration(self, obj):
        """
        Calculates the total employment duration in months.
        
        Args:
            obj (EmploymentInfo): The employment info instance
            
        Returns:
            int: Total employment duration in months
        """
        return obj.get_total_employment_duration()


class SchoolAdminProfileSerializer(BaseModelSerializer):
    """
    Serializer for SchoolAdminProfile model.
    """
    
    class Meta:
        model = SchoolAdminProfile
        fields = [
            'id', 'user', 'school', 'title', 'department',
            'is_primary_contact', 'can_sign_documents',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_school_name(self, obj):
        """
        Returns the name of the school associated with the admin.
        
        Args:
            obj (SchoolAdminProfile): The school admin profile instance
            
        Returns:
            str: School name
        """
        return obj.school.name


class InternalUserProfileSerializer(BaseModelSerializer):
    """
    Serializer for InternalUserProfile model.
    """
    
    class Meta:
        model = InternalUserProfile
        fields = [
            'id', 'user', 'employee_id', 'department', 'title',
            'supervisor', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_supervisor_name(self, obj):
        """
        Returns the name of the user's supervisor.
        
        Args:
            obj (InternalUserProfile): The internal user profile instance
            
        Returns:
            str: Supervisor's full name
        """
        if obj.supervisor and obj.supervisor.user:
            return obj.supervisor.user.get_full_name()
        return None


class RoleSerializer(BaseModelSerializer):
    """
    Serializer for Role model.
    """
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_permissions_count(self, obj):
        """
        Returns the count of permissions assigned to the role.
        
        Args:
            obj (Role): The role instance
            
        Returns:
            int: Number of permissions
        """
        return RolePermission.objects.filter(role=obj).count()


class PermissionSerializer(BaseModelSerializer):
    """
    Serializer for Permission model.
    """
    
    class Meta:
        model = Permission
        fields = [
            'id', 'name', 'description', 'resource_type',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserRoleSerializer(BaseModelSerializer):
    """
    Serializer for UserRole model.
    """
    
    class Meta:
        model = UserRole
        fields = [
            'id', 'user', 'role', 'assigned_at', 'assigned_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'assigned_at', 'created_at', 'updated_at']
    
    def get_role_name(self, obj):
        """
        Returns the name of the role.
        
        Args:
            obj (UserRole): The user role instance
            
        Returns:
            str: Role name
        """
        return obj.role.name
    
    def get_assigned_by_name(self, obj):
        """
        Returns the name of the user who assigned the role.
        
        Args:
            obj (UserRole): The user role instance
            
        Returns:
            str: Assigner's full name
        """
        if obj.assigned_by:
            return obj.assigned_by.get_full_name()
        return None


class RolePermissionSerializer(BaseModelSerializer):
    """
    Serializer for RolePermission model.
    """
    
    class Meta:
        model = RolePermission
        fields = [
            'id', 'role', 'permission', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_permission_name(self, obj):
        """
        Returns the name of the permission.
        
        Args:
            obj (RolePermission): The role permission instance
            
        Returns:
            str: Permission name
        """
        return obj.permission.name
    
    def get_resource_type(self, obj):
        """
        Returns the resource type of the permission.
        
        Args:
            obj (RolePermission): The role permission instance
            
        Returns:
            str: Resource type
        """
        return obj.permission.resource_type


class PasswordChangeSerializer(BaseSerializer):
    """
    Serializer for password change requests.
    """
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)
    
    def validate_current_password(self, value):
        """
        Validates the current password field.
        
        Args:
            value (str): The current password value
            
        Returns:
            str: Validated current password
            
        Raises:
            ValidationException: If current password validation fails
        """
        if not value:
            raise ValidationException("Current password is required.")
        
        user = self.context.get('user')
        
        if not user:
            raise ValidationException("User context is required.")
        
        # Check if current password is correct
        if not user.auth0_user.check_password(value):
            raise ValidationException("Current password is incorrect.")
        
        return value
    
    def validate_new_password(self, value):
        """
        Validates the new password field.
        
        Args:
            value (str): The new password value
            
        Returns:
            str: Validated new password
            
        Raises:
            ValidationException: If new password validation fails
        """
        if not value:
            raise ValidationException("New password is required.")
        
        try:
            validate_password(value)
        except Exception as e:
            raise ValidationException(str(e))
        
        return value
    
    def validate(self, data):
        """
        Validates that new password and confirm password match.
        
        Args:
            data (dict): The data to validate
            
        Returns:
            dict: Validated data
            
        Raises:
            ValidationException: If passwords don't match
        """
        # Check if new_password and confirm_password match
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if new_password != confirm_password:
            raise ValidationException("New password and confirm password do not match.")
        
        return data