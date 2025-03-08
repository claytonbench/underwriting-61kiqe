"""
Service layer for user management in the loan management system.

This module provides business logic for user operations including CRUD operations,
profile management, role and permission management, and user authentication integration
with Auth0.
"""

from django.db import transaction  # Django 4.2+
import logging  # standard library
import uuid  # standard library

from .models import (
    User, BorrowerProfile, EmploymentInfo, SchoolAdminProfile,
    InternalUserProfile, UserPermission, Role, Permission, UserRole, RolePermission
)
from ..authentication.models import Auth0User
from ..authentication.auth0 import Auth0Manager
from ...utils.constants import USER_TYPES
from ...core.exceptions import (
    ValidationException, ResourceNotFoundException, 
    PermissionException, ConflictException
)

# Configure logger
logger = logging.getLogger(__name__)


class UserService:
    """Service class for user management operations"""
    
    def __init__(self):
        """Initialize the UserService with Auth0Manager"""
        self.auth0_manager = Auth0Manager()
        
    def get_user_by_id(self, user_id):
        """
        Retrieves a user by ID.
        
        Args:
            user_id (uuid.UUID): User's ID
            
        Returns:
            User: User object if found
            
        Raises:
            ResourceNotFoundException: If user doesn't exist
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ResourceNotFoundException(f"User with ID {user_id} not found")
    
    def get_user_by_email(self, email):
        """
        Retrieves a user by email address.
        
        Args:
            email (str): User's email address
            
        Returns:
            User: User object if found
            
        Raises:
            ResourceNotFoundException: If user doesn't exist
        """
        try:
            # Case-insensitive lookup
            return User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise ResourceNotFoundException(f"User with email {email} not found")
    
    def get_users(self, filters=None):
        """
        Retrieves users with optional filtering.
        
        Args:
            filters (dict): Filter parameters
            
        Returns:
            QuerySet: QuerySet of User objects
        """
        # Start with all active users
        users = User.objects.all()
        
        # Apply filters if provided
        if filters:
            # Filter by email (case insensitive)
            if 'email' in filters:
                users = users.filter(email__icontains=filters['email'])
                
            # Filter by user type
            if 'user_type' in filters:
                users = users.filter(user_type=filters['user_type'])
                
            # Filter by name (first or last)
            if 'name' in filters:
                name_query = filters['name']
                users = users.filter(
                    models.Q(first_name__icontains=name_query) | 
                    models.Q(last_name__icontains=name_query)
                )
                
            # Filter by active status
            if 'is_active' in filters:
                users = users.filter(is_active=filters['is_active'])
                
        return users
    
    @transaction.atomic
    def create_user(self, user_data):
        """
        Creates a new user with associated profile.
        
        Args:
            user_data (dict): User data including profile information
            
        Returns:
            User: Created User object
            
        Raises:
            ValidationException: If required data is missing or invalid
            ConflictException: If email already exists
        """
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'user_type']
        for field in required_fields:
            if field not in user_data:
                raise ValidationException(f"Missing required field: {field}")
        
        email = user_data['email']
        password = user_data['password']
        user_type = user_data['user_type']
        
        # Check if email is already in use
        if User.objects.filter(email__iexact=email).exists():
            raise ConflictException(f"User with email {email} already exists")
        
        # Validate user_type
        if user_type not in USER_TYPES.values():
            raise ValidationException(f"Invalid user_type: {user_type}")
        
        try:
            # Create Auth0 user
            auth0_user = self.auth0_manager.create_user(
                email=email,
                password=password,
                user_type=user_type,
                user_metadata={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name']
                }
            )
            
            # Create Django user
            user = User.objects.create(
                auth0_user=auth0_user,
                email=email,
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                phone=user_data.get('phone', ''),
                user_type=user_type
            )
            
            # Create appropriate profile based on user_type
            if user_type in [USER_TYPES['BORROWER'], USER_TYPES['CO_BORROWER']]:
                profile_data = user_data.get('profile_data', {})
                self.create_borrower_profile(user, profile_data)
                
            elif user_type == USER_TYPES['SCHOOL_ADMIN']:
                profile_data = user_data.get('profile_data', {})
                self.create_school_admin_profile(user, profile_data)
                
            elif user_type in [USER_TYPES['UNDERWRITER'], USER_TYPES['QC'], USER_TYPES['SYSTEM_ADMIN']]:
                profile_data = user_data.get('profile_data', {})
                self.create_internal_user_profile(user, profile_data)
            
            logger.info(f"Created new user: {user.id} ({user.email})")
            return user
            
        except Exception as e:
            # Rollback will happen automatically due to @transaction.atomic
            logger.error(f"Error creating user: {str(e)}")
            # Re-raise as ValidationException for client-friendly error message
            raise ValidationException(f"Failed to create user: {str(e)}")
    
    @transaction.atomic
    def update_user(self, user, user_data):
        """
        Updates an existing user and their profile.
        
        Args:
            user (User): The user to update
            user_data (dict): User data to update
            
        Returns:
            User: Updated User object
            
        Raises:
            ValidationException: If data is invalid
        """
        try:
            # Update basic user fields
            for field in ['first_name', 'last_name', 'phone', 'is_active']:
                if field in user_data:
                    setattr(user, field, user_data[field])
            
            # Update email if provided (requires Auth0 update as well)
            if 'email' in user_data and user_data['email'] != user.email:
                # Check if new email is already in use
                if User.objects.filter(email__iexact=user_data['email']).exclude(id=user.id).exists():
                    raise ConflictException(f"User with email {user_data['email']} already exists")
                
                # Update Auth0 user email
                self.auth0_manager.update_user(
                    user.auth0_user,
                    {'email': user_data['email']}
                )
                
                user.email = user_data['email']
            
            # Save user changes
            user.save()
            
            # Update profile if profile_data is provided
            if 'profile_data' in user_data:
                profile_data = user_data['profile_data']
                profile = user.get_profile()
                
                if profile:
                    # Update existing profile based on user_type
                    if user.user_type in [USER_TYPES['BORROWER'], USER_TYPES['CO_BORROWER']]:
                        self.update_borrower_profile(profile, profile_data)
                        
                    elif user.user_type == USER_TYPES['SCHOOL_ADMIN']:
                        self.update_school_admin_profile(profile, profile_data)
                        
                    elif user.user_type in [USER_TYPES['UNDERWRITER'], USER_TYPES['QC'], USER_TYPES['SYSTEM_ADMIN']]:
                        self.update_internal_user_profile(profile, profile_data)
                else:
                    # Create profile if it doesn't exist
                    if user.user_type in [USER_TYPES['BORROWER'], USER_TYPES['CO_BORROWER']]:
                        self.create_borrower_profile(user, profile_data)
                        
                    elif user.user_type == USER_TYPES['SCHOOL_ADMIN']:
                        self.create_school_admin_profile(user, profile_data)
                        
                    elif user.user_type in [USER_TYPES['UNDERWRITER'], USER_TYPES['QC'], USER_TYPES['SYSTEM_ADMIN']]:
                        self.create_internal_user_profile(user, profile_data)
            
            logger.info(f"Updated user: {user.id} ({user.email})")
            return user
            
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise ValidationException(f"Failed to update user: {str(e)}")
    
    @transaction.atomic
    def delete_user(self, user):
        """
        Deletes a user (soft delete).
        
        Args:
            user (User): The user to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            ValidationException: If deletion fails
        """
        try:
            # Soft delete in our system
            user.is_active = False
            user.save()
            
            # Delete in Auth0 if needed
            # Note: In some cases you might prefer to just disable Auth0 users
            # rather than delete them, depending on your business requirements
            try:
                self.auth0_manager.delete_user(user.auth0_user)
            except Exception as auth0_error:
                logger.warning(f"Failed to delete Auth0 user: {str(auth0_error)}")
            
            logger.info(f"Deleted user: {user.id} ({user.email})")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            raise ValidationException(f"Failed to delete user: {str(e)}")
    
    def get_user_profile(self, user):
        """
        Retrieves a user's profile based on their user_type.
        
        Args:
            user (User): The user to get profile for
            
        Returns:
            object: Profile object (BorrowerProfile, SchoolAdminProfile, or InternalUserProfile)
            
        Raises:
            ResourceNotFoundException: If profile doesn't exist
        """
        profile = user.get_profile()
        if not profile:
            raise ResourceNotFoundException(f"Profile for user {user.id} not found")
        return profile
    
    def create_borrower_profile(self, user, profile_data):
        """
        Creates a borrower profile for a user.
        
        Args:
            user (User): The user to create profile for
            profile_data (dict): Profile data
            
        Returns:
            BorrowerProfile: Created BorrowerProfile object
            
        Raises:
            ValidationException: If required data is missing
        """
        # Validate required fields
        required_fields = ['ssn', 'dob', 'address_line1', 'city', 'state', 'zip_code']
        for field in required_fields:
            if field not in profile_data:
                raise ValidationException(f"Missing required field for borrower profile: {field}")
        
        # Create the profile
        profile = BorrowerProfile.objects.create(
            user=user,
            # Add basic fields
            ssn=profile_data['ssn'],
            dob=profile_data['dob'],
            citizenship_status=profile_data.get('citizenship_status', 'us_citizen'),
            address_line1=profile_data['address_line1'],
            address_line2=profile_data.get('address_line2', ''),
            city=profile_data['city'],
            state=profile_data['state'],
            zip_code=profile_data['zip_code'],
            housing_status=profile_data.get('housing_status', 'rent'),
            housing_payment=profile_data.get('housing_payment', 0.0)
        )
        
        # Create employment info if provided
        if 'employment_info' in profile_data:
            emp_data = profile_data['employment_info']
            EmploymentInfo.objects.create(
                profile=profile,
                employment_type=emp_data.get('employment_type', 'full_time'),
                employer_name=emp_data.get('employer_name', ''),
                occupation=emp_data.get('occupation', ''),
                employer_phone=emp_data.get('employer_phone', ''),
                years_employed=emp_data.get('years_employed', 0),
                months_employed=emp_data.get('months_employed', 0),
                annual_income=emp_data.get('annual_income', 0.0),
                other_income=emp_data.get('other_income', 0.0),
                other_income_source=emp_data.get('other_income_source', '')
            )
        
        return profile
    
    def update_borrower_profile(self, profile, profile_data):
        """
        Updates a borrower's profile.
        
        Args:
            profile (BorrowerProfile): The profile to update
            profile_data (dict): Profile data
            
        Returns:
            BorrowerProfile: Updated BorrowerProfile object
        """
        # Update basic fields
        for field in [
            'citizenship_status', 'address_line1', 'address_line2', 
            'city', 'state', 'zip_code', 'housing_status', 'housing_payment'
        ]:
            if field in profile_data:
                setattr(profile, field, profile_data[field])
        
        # Update SSN if provided
        if 'ssn' in profile_data:
            profile.set_ssn(profile_data['ssn'])
        
        # Update DOB if provided
        if 'dob' in profile_data:
            profile.dob = profile_data['dob']
        
        profile.save()
        
        # Update employment info if provided
        if 'employment_info' in profile_data:
            emp_data = profile_data['employment_info']
            try:
                # Try to get existing employment info
                emp_info = EmploymentInfo.objects.get(profile=profile)
                
                # Update fields
                for field in [
                    'employment_type', 'employer_name', 'occupation', 'employer_phone',
                    'years_employed', 'months_employed', 'annual_income', 
                    'other_income', 'other_income_source'
                ]:
                    if field in emp_data:
                        setattr(emp_info, field, emp_data[field])
                
                emp_info.save()
            except EmploymentInfo.DoesNotExist:
                # Create new employment info if it doesn't exist
                EmploymentInfo.objects.create(
                    profile=profile,
                    employment_type=emp_data.get('employment_type', 'full_time'),
                    employer_name=emp_data.get('employer_name', ''),
                    occupation=emp_data.get('occupation', ''),
                    employer_phone=emp_data.get('employer_phone', ''),
                    years_employed=emp_data.get('years_employed', 0),
                    months_employed=emp_data.get('months_employed', 0),
                    annual_income=emp_data.get('annual_income', 0.0),
                    other_income=emp_data.get('other_income', 0.0),
                    other_income_source=emp_data.get('other_income_source', '')
                )
        
        return profile
    
    def create_school_admin_profile(self, user, profile_data):
        """
        Creates a school administrator profile for a user.
        
        Args:
            user (User): The user to create profile for
            profile_data (dict): Profile data
            
        Returns:
            SchoolAdminProfile: Created SchoolAdminProfile object
            
        Raises:
            ValidationException: If required data is missing
        """
        # Validate required fields
        if 'school_id' not in profile_data:
            raise ValidationException("Missing required field for school admin profile: school_id")
        
        # Create the profile
        profile = SchoolAdminProfile.objects.create(
            user=user,
            school_id=profile_data['school_id'],
            title=profile_data.get('title', ''),
            department=profile_data.get('department', ''),
            is_primary_contact=profile_data.get('is_primary_contact', False),
            can_sign_documents=profile_data.get('can_sign_documents', False)
        )
        
        return profile
    
    def update_school_admin_profile(self, profile, profile_data):
        """
        Updates a school administrator's profile.
        
        Args:
            profile (SchoolAdminProfile): The profile to update
            profile_data (dict): Profile data
            
        Returns:
            SchoolAdminProfile: Updated SchoolAdminProfile object
        """
        # Update basic fields
        for field in ['title', 'department', 'is_primary_contact', 'can_sign_documents']:
            if field in profile_data:
                setattr(profile, field, profile_data[field])
        
        # Update school if provided
        if 'school_id' in profile_data:
            profile.school_id = profile_data['school_id']
        
        profile.save()
        return profile
    
    def create_internal_user_profile(self, user, profile_data):
        """
        Creates an internal user profile for a user.
        
        Args:
            user (User): The user to create profile for
            profile_data (dict): Profile data
            
        Returns:
            InternalUserProfile: Created InternalUserProfile object
            
        Raises:
            ValidationException: If required data is missing
        """
        # Validate required fields
        required_fields = ['employee_id', 'department', 'title']
        for field in required_fields:
            if field not in profile_data:
                raise ValidationException(f"Missing required field for internal user profile: {field}")
        
        # Create the profile
        profile = InternalUserProfile.objects.create(
            user=user,
            employee_id=profile_data['employee_id'],
            department=profile_data['department'],
            title=profile_data['title'],
            supervisor_id=profile_data.get('supervisor_id')
        )
        
        return profile
    
    def update_internal_user_profile(self, profile, profile_data):
        """
        Updates an internal user's profile.
        
        Args:
            profile (InternalUserProfile): The profile to update
            profile_data (dict): Profile data
            
        Returns:
            InternalUserProfile: Updated InternalUserProfile object
        """
        # Update basic fields
        for field in ['employee_id', 'department', 'title']:
            if field in profile_data:
                setattr(profile, field, profile_data[field])
        
        # Update supervisor if provided
        if 'supervisor_id' in profile_data:
            profile.supervisor_id = profile_data['supervisor_id']
        
        profile.save()
        return profile
    
    def change_password(self, user, current_password, new_password):
        """
        Changes a user's password.
        
        Args:
            user (User): The user to change password for
            current_password (str): Current password
            new_password (str): New password
            
        Returns:
            bool: True if password change was successful
            
        Raises:
            ValidationException: If password change fails
        """
        try:
            # Change password in Auth0
            self.auth0_manager.change_password(user.auth0_user, new_password)
            
            logger.info(f"Password changed for user: {user.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            raise ValidationException(f"Failed to change password: {str(e)}")
    
    def reset_password(self, email):
        """
        Initiates a password reset for a user.
        
        Args:
            email (str): The email address of the user
            
        Returns:
            bool: True if password reset was initiated successfully
        """
        try:
            # Initiate password reset in Auth0
            result = self.auth0_manager.reset_password(email)
            
            if result:
                logger.info(f"Password reset initiated for email: {email}")
            else:
                logger.warning(f"Password reset failed for email: {email}")
                
            return result
            
        except Exception as e:
            logger.error(f"Error initiating password reset: {str(e)}")
            return False


class RoleService:
    """Service class for role and permission management"""
    
    def get_roles(self, filters=None):
        """
        Retrieves all roles with optional filtering.
        
        Args:
            filters (dict): Filter parameters
            
        Returns:
            QuerySet: QuerySet of Role objects
        """
        # Start with all active roles
        roles = Role.objects.filter(is_active=True)
        
        # Apply filters if provided
        if filters:
            # Filter by name
            if 'name' in filters:
                roles = roles.filter(name__icontains=filters['name'])
        
        return roles
    
    def get_role_by_id(self, role_id):
        """
        Retrieves a role by ID.
        
        Args:
            role_id (uuid.UUID): Role's ID
            
        Returns:
            Role: Role object if found
            
        Raises:
            ResourceNotFoundException: If role doesn't exist
        """
        try:
            return Role.objects.get(id=role_id, is_active=True)
        except Role.DoesNotExist:
            raise ResourceNotFoundException(f"Role with ID {role_id} not found")
    
    def create_role(self, role_data):
        """
        Creates a new role.
        
        Args:
            role_data (dict): Role data
            
        Returns:
            Role: Created Role object
            
        Raises:
            ValidationException: If required data is missing
            ConflictException: If role with the same name already exists
        """
        # Validate required fields
        required_fields = ['name', 'description']
        for field in required_fields:
            if field not in role_data:
                raise ValidationException(f"Missing required field: {field}")
        
        # Check if role with the same name already exists
        if Role.objects.filter(name__iexact=role_data['name']).exists():
            raise ConflictException(f"Role with name '{role_data['name']}' already exists")
        
        try:
            # Create the role
            role = Role.objects.create(
                name=role_data['name'],
                description=role_data['description']
            )
            
            logger.info(f"Created new role: {role.id} ({role.name})")
            return role
            
        except Exception as e:
            logger.error(f"Error creating role: {str(e)}")
            raise ValidationException(f"Failed to create role: {str(e)}")
    
    def update_role(self, role, role_data):
        """
        Updates an existing role.
        
        Args:
            role (Role): The role to update
            role_data (dict): Role data
            
        Returns:
            Role: Updated Role object
            
        Raises:
            ValidationException: If data is invalid
            ConflictException: If role name conflicts with existing role
        """
        try:
            # Check for name conflicts if name is being changed
            if 'name' in role_data and role_data['name'] != role.name:
                if Role.objects.filter(name__iexact=role_data['name']).exclude(id=role.id).exists():
                    raise ConflictException(f"Role with name '{role_data['name']}' already exists")
                role.name = role_data['name']
            
            # Update description if provided
            if 'description' in role_data:
                role.description = role_data['description']
            
            role.save()
            
            logger.info(f"Updated role: {role.id} ({role.name})")
            return role
            
        except ConflictException as ce:
            # Re-raise conflict exceptions
            raise ce
        except Exception as e:
            logger.error(f"Error updating role: {str(e)}")
            raise ValidationException(f"Failed to update role: {str(e)}")
    
    def delete_role(self, role):
        """
        Deletes a role (soft delete).
        
        Args:
            role (Role): The role to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            ValidationException: If deletion fails
        """
        try:
            # Soft delete
            role.is_active = False
            role.save()
            
            logger.info(f"Deleted role: {role.id} ({role.name})")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting role: {str(e)}")
            raise ValidationException(f"Failed to delete role: {str(e)}")
    
    def get_permissions(self, filters=None):
        """
        Retrieves all permissions with optional filtering.
        
        Args:
            filters (dict): Filter parameters
            
        Returns:
            QuerySet: QuerySet of Permission objects
        """
        # Start with all active permissions
        permissions = Permission.objects.filter(is_active=True)
        
        # Apply filters if provided
        if filters:
            # Filter by name
            if 'name' in filters:
                permissions = permissions.filter(name__icontains=filters['name'])
            
            # Filter by resource type
            if 'resource_type' in filters:
                permissions = permissions.filter(resource_type=filters['resource_type'])
        
        return permissions
    
    def get_permission_by_id(self, permission_id):
        """
        Retrieves a permission by ID.
        
        Args:
            permission_id (uuid.UUID): Permission's ID
            
        Returns:
            Permission: Permission object if found
            
        Raises:
            ResourceNotFoundException: If permission doesn't exist
        """
        try:
            return Permission.objects.get(id=permission_id, is_active=True)
        except Permission.DoesNotExist:
            raise ResourceNotFoundException(f"Permission with ID {permission_id} not found")
    
    def create_permission(self, permission_data):
        """
        Creates a new permission.
        
        Args:
            permission_data (dict): Permission data
            
        Returns:
            Permission: Created Permission object
            
        Raises:
            ValidationException: If required data is missing
            ConflictException: If permission with the same name already exists
        """
        # Validate required fields
        required_fields = ['name', 'description', 'resource_type']
        for field in required_fields:
            if field not in permission_data:
                raise ValidationException(f"Missing required field: {field}")
        
        # Check if permission with the same name already exists
        if Permission.objects.filter(
            name__iexact=permission_data['name'],
            resource_type=permission_data['resource_type']
        ).exists():
            raise ConflictException(
                f"Permission with name '{permission_data['name']}' "
                f"for resource type '{permission_data['resource_type']}' already exists"
            )
        
        try:
            # Create the permission
            permission = Permission.objects.create(
                name=permission_data['name'],
                description=permission_data['description'],
                resource_type=permission_data['resource_type']
            )
            
            logger.info(f"Created new permission: {permission.id} ({permission.name})")
            return permission
            
        except Exception as e:
            logger.error(f"Error creating permission: {str(e)}")
            raise ValidationException(f"Failed to create permission: {str(e)}")
    
    def update_permission(self, permission, permission_data):
        """
        Updates an existing permission.
        
        Args:
            permission (Permission): The permission to update
            permission_data (dict): Permission data
            
        Returns:
            Permission: Updated Permission object
            
        Raises:
            ValidationException: If data is invalid
            ConflictException: If permission name conflicts with existing permission
        """
        try:
            # Check for name/resource_type conflicts if they're being changed
            name_changed = 'name' in permission_data and permission_data['name'] != permission.name
            type_changed = 'resource_type' in permission_data and permission_data['resource_type'] != permission.resource_type
            
            if (name_changed or type_changed) and Permission.objects.filter(
                name__iexact=permission_data.get('name', permission.name),
                resource_type=permission_data.get('resource_type', permission.resource_type)
            ).exclude(id=permission.id).exists():
                raise ConflictException(
                    f"Permission with name '{permission_data.get('name', permission.name)}' "
                    f"for resource type '{permission_data.get('resource_type', permission.resource_type)}' already exists"
                )
            
            # Update fields if provided
            for field in ['name', 'description', 'resource_type']:
                if field in permission_data:
                    setattr(permission, field, permission_data[field])
            
            permission.save()
            
            logger.info(f"Updated permission: {permission.id} ({permission.name})")
            return permission
            
        except ConflictException as ce:
            # Re-raise conflict exceptions
            raise ce
        except Exception as e:
            logger.error(f"Error updating permission: {str(e)}")
            raise ValidationException(f"Failed to update permission: {str(e)}")
    
    def delete_permission(self, permission):
        """
        Deletes a permission (soft delete).
        
        Args:
            permission (Permission): The permission to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            ValidationException: If deletion fails
        """
        try:
            # Soft delete
            permission.is_active = False
            permission.save()
            
            logger.info(f"Deleted permission: {permission.id} ({permission.name})")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting permission: {str(e)}")
            raise ValidationException(f"Failed to delete permission: {str(e)}")
    
    def get_user_roles(self, user):
        """
        Retrieves all roles assigned to a user.
        
        Args:
            user (User): The user to get roles for
            
        Returns:
            QuerySet: QuerySet of Role objects
        """
        # Get all user-role relationships for the user
        user_roles = UserRole.objects.filter(user=user)
        
        # Extract the roles
        role_ids = user_roles.values_list('role_id', flat=True)
        return Role.objects.filter(id__in=role_ids, is_active=True)
    
    def get_role_permissions(self, role):
        """
        Retrieves all permissions assigned to a role.
        
        Args:
            role (Role): The role to get permissions for
            
        Returns:
            QuerySet: QuerySet of Permission objects
        """
        # Get all role-permission relationships for the role
        role_permissions = RolePermission.objects.filter(role=role)
        
        # Extract the permissions
        permission_ids = role_permissions.values_list('permission_id', flat=True)
        return Permission.objects.filter(id__in=permission_ids, is_active=True)
    
    def get_user_permissions(self, user):
        """
        Retrieves all permissions assigned to a user through their roles.
        
        Args:
            user (User): The user to get permissions for
            
        Returns:
            QuerySet: QuerySet of Permission objects
        """
        # Get all roles for the user
        roles = self.get_user_roles(user)
        
        # Get all permissions for these roles
        permission_sets = [self.get_role_permissions(role) for role in roles]
        
        # Combine all permissions into one queryset
        if not permission_sets:
            return Permission.objects.none()
        
        combined_permissions = permission_sets[0]
        for permission_set in permission_sets[1:]:
            combined_permissions = combined_permissions | permission_set
        
        return combined_permissions.distinct()
    
    def assign_role_to_user(self, user, role, assigned_by):
        """
        Assigns a role to a user.
        
        Args:
            user (User): The user to assign role to
            role (Role): The role to assign
            assigned_by (User): The user making the assignment
            
        Returns:
            UserRole: Created UserRole object
            
        Raises:
            ConflictException: If user already has the role
        """
        # Check if user already has the role
        if UserRole.objects.filter(user=user, role=role).exists():
            raise ConflictException(f"User {user.id} already has role {role.name}")
        
        try:
            # Create the user-role relationship
            user_role = UserRole.objects.create(
                user=user,
                role=role,
                assigned_by=assigned_by
            )
            
            logger.info(f"Assigned role {role.name} to user {user.id} by {assigned_by.id}")
            return user_role
            
        except Exception as e:
            logger.error(f"Error assigning role to user: {str(e)}")
            raise ValidationException(f"Failed to assign role to user: {str(e)}")
    
    def remove_role_from_user(self, user, role):
        """
        Removes a role from a user.
        
        Args:
            user (User): The user to remove role from
            role (Role): The role to remove
            
        Returns:
            bool: True if removal was successful
            
        Raises:
            ResourceNotFoundException: If user doesn't have the role
        """
        try:
            # Get the user-role relationship
            user_role = UserRole.objects.get(user=user, role=role)
            
            # Delete the relationship
            user_role.delete()
            
            logger.info(f"Removed role {role.name} from user {user.id}")
            return True
            
        except UserRole.DoesNotExist:
            raise ResourceNotFoundException(f"User {user.id} doesn't have role {role.name}")
    
    def assign_permission_to_role(self, role, permission):
        """
        Assigns a permission to a role.
        
        Args:
            role (Role): The role to assign permission to
            permission (Permission): The permission to assign
            
        Returns:
            RolePermission: Created RolePermission object
            
        Raises:
            ConflictException: If role already has the permission
        """
        # Check if role already has the permission
        if RolePermission.objects.filter(role=role, permission=permission).exists():
            raise ConflictException(f"Role {role.name} already has permission {permission.name}")
        
        try:
            # Create the role-permission relationship
            role_permission = RolePermission.objects.create(
                role=role,
                permission=permission
            )
            
            logger.info(f"Assigned permission {permission.name} to role {role.name}")
            return role_permission
            
        except Exception as e:
            logger.error(f"Error assigning permission to role: {str(e)}")
            raise ValidationException(f"Failed to assign permission to role: {str(e)}")
    
    def remove_permission_from_role(self, role, permission):
        """
        Removes a permission from a role.
        
        Args:
            role (Role): The role to remove permission from
            permission (Permission): The permission to remove
            
        Returns:
            bool: True if removal was successful
            
        Raises:
            ResourceNotFoundException: If role doesn't have the permission
        """
        try:
            # Get the role-permission relationship
            role_permission = RolePermission.objects.get(role=role, permission=permission)
            
            # Delete the relationship
            role_permission.delete()
            
            logger.info(f"Removed permission {permission.name} from role {role.name}")
            return True
            
        except RolePermission.DoesNotExist:
            raise ResourceNotFoundException(f"Role {role.name} doesn't have permission {permission.name}")
    
    def check_user_has_permission(self, user, permission_name, resource_type, resource_id=None):
        """
        Checks if a user has a specific permission.
        
        Args:
            user (User): The user to check
            permission_name (str): The name of the permission
            resource_type (str): The type of resource
            resource_id (uuid.UUID, optional): The specific resource ID
            
        Returns:
            bool: True if user has the permission, False otherwise
        """
        # Get all permissions for the user
        permissions = self.get_user_permissions(user)
        
        # Check if any permission matches the criteria
        for permission in permissions:
            if permission.name == permission_name and permission.resource_type == resource_type:
                return True
        
        # Check for specific resource permission in UserPermission
        if resource_id:
            try:
                # Check if there's a custom permission grant for this specific resource
                user_permission = UserPermission.objects.get(
                    user=user,
                    permission_name=permission_name,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    is_granted=True
                )
                return True
            except UserPermission.DoesNotExist:
                pass
        
        return False
    
    def grant_user_permission(self, user, permission_name, resource_type, resource_id=None):
        """
        Grants a specific permission to a user for a resource.
        
        Args:
            user (User): The user to grant permission to
            permission_name (str): The name of the permission
            resource_type (str): The type of resource
            resource_id (uuid.UUID, optional): The specific resource ID
            
        Returns:
            UserPermission: Created UserPermission object
            
        Raises:
            ConflictException: If user already has the permission
        """
        # Check if user already has this specific permission
        if UserPermission.objects.filter(
            user=user,
            permission_name=permission_name,
            resource_type=resource_type,
            resource_id=resource_id,
            is_granted=True
        ).exists():
            raise ConflictException(f"User {user.id} already has permission {permission_name} on {resource_type}")
        
        try:
            # Create or update the user permission
            user_permission, created = UserPermission.objects.update_or_create(
                user=user,
                permission_name=permission_name,
                resource_type=resource_type,
                resource_id=resource_id,
                defaults={'is_granted': True}
            )
            
            logger.info(
                f"Granted permission {permission_name} on {resource_type} "
                f"{'resource ' + str(resource_id) if resource_id else 'all resources'} to user {user.id}"
            )
            return user_permission
            
        except Exception as e:
            logger.error(f"Error granting permission to user: {str(e)}")
            raise ValidationException(f"Failed to grant permission to user: {str(e)}")
    
    def revoke_user_permission(self, user, permission_name, resource_type, resource_id=None):
        """
        Revokes a specific permission from a user for a resource.
        
        Args:
            user (User): The user to revoke permission from
            permission_name (str): The name of the permission
            resource_type (str): The type of resource
            resource_id (uuid.UUID, optional): The specific resource ID
            
        Returns:
            bool: True if revocation was successful
            
        Raises:
            ResourceNotFoundException: If user doesn't have the permission
        """
        try:
            # Get the user permission
            user_permission = UserPermission.objects.get(
                user=user,
                permission_name=permission_name,
                resource_type=resource_type,
                resource_id=resource_id
            )
            
            # Set is_granted to False or delete the permission
            user_permission.is_granted = False
            user_permission.save()
            
            logger.info(
                f"Revoked permission {permission_name} on {resource_type} "
                f"{'resource ' + str(resource_id) if resource_id else 'all resources'} from user {user.id}"
            )
            return True
            
        except UserPermission.DoesNotExist:
            raise ResourceNotFoundException(
                f"User {user.id} doesn't have permission {permission_name} on {resource_type} "
                f"{'resource ' + str(resource_id) if resource_id else 'all resources'}"
            )