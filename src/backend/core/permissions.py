from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

# Define user role constants for use throughout the application
USER_ROLES = {
    'SYSTEM_ADMIN': 'system_admin',
    'UNDERWRITER': 'underwriter',
    'QC': 'qc',
    'SCHOOL_ADMIN': 'school_admin',
    'BORROWER': 'borrower',
    'CO_BORROWER': 'co_borrower'
}

# Define roles that are considered internal to the organization
INTERNAL_ROLES = ['system_admin', 'underwriter', 'qc']


def has_object_permission_or_403(permission_class, request, view, obj):
    """
    Utility function to check object permission and raise exception if denied.
    
    Args:
        permission_class: The permission class to check
        request: The request object
        view: The view that triggered the check
        obj: The object to check permissions for
        
    Returns:
        True if permission is granted
        
    Raises:
        PermissionDenied: If permission is denied
    """
    if hasattr(permission_class, 'has_object_permission'):
        if permission_class.has_object_permission(request, view, obj):
            return True
        else:
            raise PermissionDenied("You do not have permission to perform this action.")
    return True


class IsAuthenticated(BasePermission):
    """
    Permission class that allows access only to authenticated users.
    """
    def has_permission(self, request, view):
        """
        Check if the user is authenticated.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user is authenticated, False otherwise
        """
        return bool(request.user and request.user.is_authenticated)


class IsSystemAdmin(BasePermission):
    """
    Permission class that allows access only to system administrators.
    """
    def has_permission(self, request, view):
        """
        Check if the user is a system administrator.
        
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


class IsUnderwriter(BasePermission):
    """
    Permission class that allows access only to underwriters.
    """
    def has_permission(self, request, view):
        """
        Check if the user is an underwriter.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user is an underwriter, False otherwise
        """
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == USER_ROLES['UNDERWRITER']
        )


class IsQC(BasePermission):
    """
    Permission class that allows access only to quality control personnel.
    """
    def has_permission(self, request, view):
        """
        Check if the user is a QC personnel.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user is a QC personnel, False otherwise
        """
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == USER_ROLES['QC']
        )


class IsSchoolAdmin(BasePermission):
    """
    Permission class that allows access only to school administrators.
    """
    def has_permission(self, request, view):
        """
        Check if the user is a school administrator.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user is a school administrator, False otherwise
        """
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == USER_ROLES['SCHOOL_ADMIN']
        )


class IsBorrower(BasePermission):
    """
    Permission class that allows access only to borrowers.
    """
    def has_permission(self, request, view):
        """
        Check if the user is a borrower.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user is a borrower, False otherwise
        """
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == USER_ROLES['BORROWER']
        )


class IsCoBorrower(BasePermission):
    """
    Permission class that allows access only to co-borrowers.
    """
    def has_permission(self, request, view):
        """
        Check if the user is a co-borrower.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user is a co-borrower, False otherwise
        """
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == USER_ROLES['CO_BORROWER']
        )


class IsInternalUser(BasePermission):
    """
    Permission class that allows access only to internal users 
    (system admin, underwriter, QC).
    """
    def has_permission(self, request, view):
        """
        Check if the user is an internal user.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user is an internal user, False otherwise
        """
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in INTERNAL_ROLES
        )


class ReadOnly(BasePermission):
    """
    Permission class that allows read-only access.
    """
    def has_permission(self, request, view):
        """
        Check if the request method is a safe method (GET, HEAD, OPTIONS).
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if request method is safe, False otherwise
        """
        return request.method in SAFE_METHODS


class IsOwner(BasePermission):
    """
    Base permission class for checking if user is the owner of an object.
    """
    def has_permission(self, request, view):
        """
        Check if the user is authenticated.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user is authenticated, False otherwise
        """
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user is the owner of the object.
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The object to check ownership for
            
        Returns:
            True if user is the owner, False otherwise
        """
        # Check if object has user or owner attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsOwnerOrReadOnly(BasePermission):
    """
    Permission class that allows read-only access to all users, 
    but write access only to the owner.
    """
    def has_permission(self, request, view):
        """
        Check if the user is authenticated for write operations.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if request is safe or user is authenticated, False otherwise
        """
        # Allow read-only access for all users
        if request.method in SAFE_METHODS:
            return True
        
        # Require authentication for write operations
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user is the owner for write operations.
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The object to check ownership for
            
        Returns:
            True if request is safe or user is the owner, False otherwise
        """
        # Allow read-only access for all users
        if request.method in SAFE_METHODS:
            return True
        
        # Check if object has user or owner attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsOwnerOrInternalUser(BasePermission):
    """
    Permission class that allows access to the owner of an object or internal users.
    """
    def has_permission(self, request, view):
        """
        Check if the user is authenticated.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user is authenticated, False otherwise
        """
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user is the owner or an internal user.
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The object to check permissions for
            
        Returns:
            True if user is the owner or an internal user, False otherwise
        """
        # Allow access for internal users
        if request.user.role in INTERNAL_ROLES:
            return True
        
        # Check if object has user or owner attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsSchoolAdminForSchool(BasePermission):
    """
    Permission class that checks if a user is a school admin for a specific school.
    """
    def has_permission(self, request, view):
        """
        Check if the user is a school administrator.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user is a school administrator, False otherwise
        """
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == USER_ROLES['SCHOOL_ADMIN']
        )
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user is a school admin for the object's school.
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The object to check permissions for
            
        Returns:
            True if user is a school admin for the object's school, False otherwise
        """
        # First, verify user is a school admin
        if request.user.role != USER_ROLES['SCHOOL_ADMIN']:
            return False
        
        # Get school_id from object (direct or through relationship)
        obj_school_id = None
        
        # Direct school_id
        if hasattr(obj, 'school_id'):
            obj_school_id = obj.school_id
        # Direct school object
        elif hasattr(obj, 'school') and hasattr(obj.school, 'id'):
            obj_school_id = obj.school.id
        # Through borrower relationship
        elif hasattr(obj, 'borrower') and hasattr(obj.borrower, 'school_id'):
            obj_school_id = obj.borrower.school_id
        # Special case for application
        elif hasattr(obj, 'application') and hasattr(obj.application, 'school_id'):
            obj_school_id = obj.application.school_id
        
        # Compare with user's school_id
        return obj_school_id == request.user.school_id


class DjangoModelPermissions(BasePermission):
    """
    Permission class that maps to Django's model permissions.
    """
    # Map of HTTP methods to Django model permissions
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }
    
    def has_permission(self, request, view):
        """
        Check if the user has the required Django model permissions.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user has the required permissions, False otherwise
        """
        # Authentication is required
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Get the queryset from the view
        queryset = getattr(view, 'queryset', None)
        if queryset is None:
            return False
            
        # Get model from queryset
        model_cls = queryset.model
        
        # Get app label and model name
        app_label = model_cls._meta.app_label
        model_name = model_cls._meta.model_name
        
        # Get permissions required for this method
        perms = self.perms_map.get(request.method, [])
        
        # Format permission strings with app label and model name
        required_perms = [
            perm % {'app_label': app_label, 'model_name': model_name}
            for perm in perms
        ]
        
        # Check if user has all required permissions
        return (
            request.user.is_superuser or
            (required_perms and request.user.has_perms(required_perms))
        )