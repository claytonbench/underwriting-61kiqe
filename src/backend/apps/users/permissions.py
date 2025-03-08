"""
User-specific permission classes for the loan management system.

This module defines permission classes that extend the core permissions 
framework to provide fine-grained access control for user management
operations, profile viewing and editing, and role management.
"""
from rest_framework.permissions import BasePermission
from ...core.permissions import (
    IsAuthenticated, 
    IsSystemAdmin, 
    IsInternalUser, 
    IsSchoolAdmin,
    IsBorrower, 
    IsCoBorrower, 
    IsOwner, 
    IsOwnerOrInternalUser,
    USER_ROLES,
    has_object_permission_or_403
)


class CanViewUserProfile(BasePermission):
    """
    Permission class that allows users to view their own profile, 
    school admins to view profiles associated with their school,
    and internal users to view any profile.
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to view user profiles.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user is authenticated, False otherwise
        """
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user can view a specific user profile.
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The user object to check permissions for
            
        Returns:
            bool: True if user can view the profile, False otherwise
        """
        # Internal users can view any profile
        if request.user.role in ['system_admin', 'underwriter', 'qc']:
            return True
        
        # Users can view their own profile
        if obj.id == request.user.id:
            return True
        
        # School admins can view profiles associated with their school
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            # If obj has a school_id field or relationship
            if hasattr(obj, 'school_id') and obj.school_id == request.user.school_id:
                return True
            # If obj has a school_admin_profile with school_id
            if hasattr(obj, 'school_admin_profile') and obj.school_admin_profile.school_id == request.user.school_id:
                return True
            
        return False


class CanEditUserProfile(BasePermission):
    """
    Permission class that allows users to edit their own profile,
    system administrators to edit any profile, and school admins 
    to edit profiles associated with their school.
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to edit user profiles.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user is authenticated, False otherwise
        """
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user can edit a specific user profile.
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The user object to check permissions for
            
        Returns:
            bool: True if user can edit the profile, False otherwise
        """
        # System admins can edit any profile
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
        
        # Users can edit their own profile
        if obj.id == request.user.id:
            return True
        
        # School admins can edit profiles associated with their school
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            # If obj has a school_id field or relationship
            if hasattr(obj, 'school_id') and obj.school_id == request.user.school_id:
                return True
            # If obj has a school_admin_profile with school_id
            if hasattr(obj, 'school_admin_profile') and obj.school_admin_profile.school_id == request.user.school_id:
                return True
            
        return False


class CanViewBorrowerProfile(BasePermission):
    """
    Permission class that allows borrowers to view their own profile,
    co-borrowers to view associated profiles, and internal users to 
    view any borrower profile.
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to view borrower profiles.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user is authenticated, False otherwise
        """
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user can view a specific borrower profile.
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The borrower profile object to check permissions for
            
        Returns:
            bool: True if user can view the borrower profile, False otherwise
        """
        # Internal users can view any borrower profile
        if request.user.role in ['system_admin', 'underwriter', 'qc']:
            return True
        
        # Borrowers can view their own profile
        if hasattr(obj, 'user') and obj.user.id == request.user.id:
            return True
        
        # Co-borrowers can view the borrower profile if they are on the same application
        if request.user.role == USER_ROLES['CO_BORROWER']:
            # Check if borrower and co-borrower are on the same application
            from ..applications.models import LoanApplication
            borrower_applications = LoanApplication.objects.filter(borrower_id=obj.user.id)
            co_borrower_applications = LoanApplication.objects.filter(co_borrower_id=request.user.id)
            
            # Check if there's any overlap in applications
            if borrower_applications.filter(id__in=co_borrower_applications.values_list('id', flat=True)).exists():
                return True
                
        # School admins can view borrower profiles associated with their school
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            # Check if there are any applications from this borrower at the admin's school
            from ..applications.models import LoanApplication
            if LoanApplication.objects.filter(
                borrower_id=obj.user.id,
                school_id=request.user.school_id
            ).exists():
                return True
            
        return False


class CanEditBorrowerProfile(BasePermission):
    """
    Permission class that allows borrowers to edit their own profile
    and internal users to edit any borrower profile.
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to edit borrower profiles.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user is authenticated, False otherwise
        """
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user can edit a specific borrower profile.
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The borrower profile object to check permissions for
            
        Returns:
            bool: True if user can edit the borrower profile, False otherwise
        """
        # System admins and underwriters can edit any borrower profile
        if request.user.role in [USER_ROLES['SYSTEM_ADMIN'], USER_ROLES['UNDERWRITER']]:
            return True
        
        # Borrowers can edit their own profile
        if hasattr(obj, 'user') and obj.user.id == request.user.id:
            return True
        
        return False


class CanManageRoles(BasePermission):
    """
    Permission class that allows only system administrators to manage
    roles and permissions.
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to manage roles and permissions.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user is a system administrator, False otherwise
        """
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == USER_ROLES['SYSTEM_ADMIN']
        )


class CanAssignUserRoles(BasePermission):
    """
    Permission class that allows system administrators to assign roles to any user 
    and school administrators to assign roles to users within their school.
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to assign roles to users.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user is a system administrator or school administrator, False otherwise
        """
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.role == USER_ROLES['SYSTEM_ADMIN'] or 
             request.user.role == USER_ROLES['SCHOOL_ADMIN'])
        )
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user can assign roles to a specific user.
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The user object to check permissions for
            
        Returns:
            bool: True if user can assign roles to the target user, False otherwise
        """
        # System admins can assign roles to any user
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
        
        # School admins can only assign roles to users within their school
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            # If target user has a school_id field or relationship
            if hasattr(obj, 'school_id') and obj.school_id == request.user.school_id:
                return True
            # If target user has a school_admin_profile with school_id
            if hasattr(obj, 'school_admin_profile') and obj.school_admin_profile.school_id == request.user.school_id:
                return True
            
        return False


class CanViewSchoolUsers(BasePermission):
    """
    Permission class that allows school administrators to view users 
    associated with their school and internal users to view any school's users.
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to view school users.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user is a school administrator or internal user, False otherwise
        """
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.role == USER_ROLES['SCHOOL_ADMIN'] or 
             request.user.role in ['system_admin', 'underwriter', 'qc'])
        )
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user can view users for a specific school.
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The school object to check permissions for
            
        Returns:
            bool: True if user can view the school's users, False otherwise
        """
        # Internal users can view any school's users
        if request.user.role in ['system_admin', 'underwriter', 'qc']:
            return True
        
        # School admins can only view users from their own school
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            return obj.id == request.user.school_id
            
        return False