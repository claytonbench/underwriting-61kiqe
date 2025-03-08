from rest_framework.permissions import BasePermission, SAFE_METHODS
from ...core.permissions import (
    IsSystemAdmin,
    IsSchoolAdmin,
    IsInternalUser,
    IsSchoolAdminForSchool,
    USER_ROLES,
    has_object_permission_or_403
)


class CanManageSchools(BasePermission):
    """
    Permission class that allows system administrators to manage schools
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to manage schools
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user is a system administrator, False otherwise
        """
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == USER_ROLES['SYSTEM_ADMIN']
        )


class CanViewSchools(BasePermission):
    """
    Permission class that allows system administrators, internal users, and school administrators to view schools
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to view schools
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user is a system administrator, internal user, or school administrator, False otherwise
        """
        if not request.user or not request.user.is_authenticated:
            return False
            
        # System admins and internal users can view all schools
        if request.user.role == USER_ROLES['SYSTEM_ADMIN'] or IsInternalUser().has_permission(request, view):
            return True
            
        # School admins can view schools
        return request.user.role == USER_ROLES['SCHOOL_ADMIN']
        
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to view a specific school
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The school object
            
        Returns:
            True if user is a system administrator, internal user, or administrator for this school, False otherwise
        """
        # System admins and internal users can view any school
        if request.user.role == USER_ROLES['SYSTEM_ADMIN'] or IsInternalUser().has_permission(request, view):
            return True
            
        # School admins can only view their own school
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            # For a school object, check if the user is an admin for this school
            return IsSchoolAdminForSchool().has_object_permission(request, view, obj)
            
        return False


class CanManageSchoolPrograms(BasePermission):
    """
    Permission class that allows system administrators and school administrators to manage programs for a school
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to manage school programs
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user is a system administrator or school administrator, False otherwise
        """
        if not request.user or not request.user.is_authenticated:
            return False
            
        # System admins can manage all programs
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # School admins can manage their school's programs
        return request.user.role == USER_ROLES['SCHOOL_ADMIN']
        
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to manage programs for a specific school
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The program object
            
        Returns:
            True if user is a system administrator or administrator for this school, False otherwise
        """
        # System admins can manage any program
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # School admins can only manage programs for their school
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            # For a program object, check if the user is an admin for this school
            return IsSchoolAdminForSchool().has_object_permission(request, view, obj)
            
        return False


class CanViewSchoolPrograms(BasePermission):
    """
    Permission class that allows system administrators, internal users, and school administrators to view programs
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to view school programs
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user is a system administrator, internal user, or school administrator, False otherwise
        """
        if not request.user or not request.user.is_authenticated:
            return False
            
        # System admins and internal users can view all programs
        if request.user.role == USER_ROLES['SYSTEM_ADMIN'] or IsInternalUser().has_permission(request, view):
            return True
            
        # School admins can view their school's programs
        return request.user.role == USER_ROLES['SCHOOL_ADMIN']
        
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to view programs for a specific school
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The program object
            
        Returns:
            True if user is a system administrator, internal user, or administrator for this school, False otherwise
        """
        # System admins and internal users can view any program
        if request.user.role == USER_ROLES['SYSTEM_ADMIN'] or IsInternalUser().has_permission(request, view):
            return True
            
        # School admins can only view programs for their school
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            # For a program object, check if the user is an admin for this school
            return IsSchoolAdminForSchool().has_object_permission(request, view, obj)
            
        return False


class CanManageProgramVersions(BasePermission):
    """
    Permission class that allows system administrators and school administrators to manage program versions
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to manage program versions
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user is a system administrator or school administrator, False otherwise
        """
        if not request.user or not request.user.is_authenticated:
            return False
            
        # System admins can manage all program versions
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # School admins can manage versions for their school's programs
        return request.user.role == USER_ROLES['SCHOOL_ADMIN']
        
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to manage versions for a specific program
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The program version object
            
        Returns:
            True if user is a system administrator or administrator for the program's school, False otherwise
        """
        # System admins can manage any program version
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # School admins can only manage versions for their school's programs
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            # For program versions, we need to check the school through the program
            program = obj.program
            return IsSchoolAdminForSchool().has_object_permission(request, view, program)
            
        return False


class CanViewProgramVersions(BasePermission):
    """
    Permission class that allows system administrators, internal users, and school administrators to view program versions
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to view program versions
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user is a system administrator, internal user, or school administrator, False otherwise
        """
        if not request.user or not request.user.is_authenticated:
            return False
            
        # System admins and internal users can view all program versions
        if request.user.role == USER_ROLES['SYSTEM_ADMIN'] or IsInternalUser().has_permission(request, view):
            return True
            
        # School admins can view versions for their school's programs
        return request.user.role == USER_ROLES['SCHOOL_ADMIN']
        
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to view versions for a specific program
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The program version object
            
        Returns:
            True if user is a system administrator, internal user, or administrator for the program's school, False otherwise
        """
        # System admins and internal users can view any program version
        if request.user.role == USER_ROLES['SYSTEM_ADMIN'] or IsInternalUser().has_permission(request, view):
            return True
            
        # School admins can only view versions for their school's programs
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            # For program versions, we need to check the school through the program
            program = obj.program
            return IsSchoolAdminForSchool().has_object_permission(request, view, program)
            
        return False


class CanManageSchoolContacts(BasePermission):
    """
    Permission class that allows system administrators and school administrators to manage school contacts
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to manage school contacts
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user is a system administrator or school administrator, False otherwise
        """
        if not request.user or not request.user.is_authenticated:
            return False
            
        # System admins can manage all school contacts
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # School admins can manage contacts for their school
        return request.user.role == USER_ROLES['SCHOOL_ADMIN']
        
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to manage contacts for a specific school
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The school contact object
            
        Returns:
            True if user is a system administrator or administrator for this school, False otherwise
        """
        # System admins can manage any school contact
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # School admins can only manage contacts for their school
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            # For school contacts, check if the user is an admin for this school
            return IsSchoolAdminForSchool().has_object_permission(request, view, obj)
            
        return False


class CanViewSchoolContacts(BasePermission):
    """
    Permission class that allows system administrators, internal users, and school administrators to view school contacts
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to view school contacts
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user is a system administrator, internal user, or school administrator, False otherwise
        """
        if not request.user or not request.user.is_authenticated:
            return False
            
        # System admins and internal users can view all school contacts
        if request.user.role == USER_ROLES['SYSTEM_ADMIN'] or IsInternalUser().has_permission(request, view):
            return True
            
        # School admins can view contacts for their school
        return request.user.role == USER_ROLES['SCHOOL_ADMIN']
        
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to view contacts for a specific school
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The school contact object
            
        Returns:
            True if user is a system administrator, internal user, or administrator for this school, False otherwise
        """
        # System admins and internal users can view any school contact
        if request.user.role == USER_ROLES['SYSTEM_ADMIN'] or IsInternalUser().has_permission(request, view):
            return True
            
        # School admins can only view contacts for their school
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            # For school contacts, check if the user is an admin for this school
            return IsSchoolAdminForSchool().has_object_permission(request, view, obj)
            
        return False


class CanManageSchoolDocuments(BasePermission):
    """
    Permission class that allows system administrators and school administrators to manage school documents
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to manage school documents
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user is a system administrator or school administrator, False otherwise
        """
        if not request.user or not request.user.is_authenticated:
            return False
            
        # System admins can manage all school documents
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # School admins can manage documents for their school
        return request.user.role == USER_ROLES['SCHOOL_ADMIN']
        
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to manage documents for a specific school
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The school document object
            
        Returns:
            True if user is a system administrator or administrator for this school, False otherwise
        """
        # System admins can manage any school document
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # School admins can only manage documents for their school
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            # For school documents, check if the user is an admin for this school
            return IsSchoolAdminForSchool().has_object_permission(request, view, obj)
            
        return False


class CanViewSchoolDocuments(BasePermission):
    """
    Permission class that allows system administrators, internal users, and school administrators to view school documents
    """
    def has_permission(self, request, view):
        """
        Check if the user has permission to view school documents
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user is a system administrator, internal user, or school administrator, False otherwise
        """
        if not request.user or not request.user.is_authenticated:
            return False
            
        # System admins and internal users can view all school documents
        if request.user.role == USER_ROLES['SYSTEM_ADMIN'] or IsInternalUser().has_permission(request, view):
            return True
            
        # School admins can view documents for their school
        return request.user.role == USER_ROLES['SCHOOL_ADMIN']
        
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to view documents for a specific school
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The school document object
            
        Returns:
            True if user is a system administrator, internal user, or administrator for this school, False otherwise
        """
        # System admins and internal users can view any school document
        if request.user.role == USER_ROLES['SYSTEM_ADMIN'] or IsInternalUser().has_permission(request, view):
            return True
            
        # School admins can only view documents for their school
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            # For school documents, check if the user is an admin for this school
            return IsSchoolAdminForSchool().has_object_permission(request, view, obj)
            
        return False