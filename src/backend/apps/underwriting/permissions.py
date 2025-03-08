"""
Defines permission classes for the underwriting module that control access to
underwriting data and operations based on user roles and relationships.

These permission classes enforce security policies for viewing, assigning, reviewing,
and making decisions on loan applications in the underwriting process.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS
from ...core.permissions import (
    IsAuthenticated, IsSystemAdmin, IsUnderwriter, IsQC, IsInternalUser,
    USER_ROLES, INTERNAL_ROLES
)
from .models import UnderwritingQueue, UnderwritingDecision
from .constants import UNDERWRITING_QUEUE_STATUS


class CanViewUnderwritingQueue(BasePermission):
    """
    Permission class that determines if a user can view the underwriting queue.
    
    Only system administrators, underwriters, and QC personnel have permission to
    view the underwriting queue.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to view the underwriting queue.
        
        Args:
            request: The request object
            view: The view that triggered the permission check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # System administrators can always view the queue
        if IsSystemAdmin().has_permission(request, view):
            return True
            
        # Underwriters can view the queue
        if IsUnderwriter().has_permission(request, view):
            return True
            
        # QC personnel can view the queue
        if IsQC().has_permission(request, view):
            return True
            
        # All other roles are denied access
        return False


class CanManageUnderwritingQueue(BasePermission):
    """
    Permission class that determines if a user can manage the underwriting queue 
    (assign applications, set priorities).
    
    Only system administrators have permission to manage the underwriting queue.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to manage the underwriting queue.
        
        Args:
            request: The request object
            view: The view that triggered the permission check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Only system administrators can manage the queue
        return IsSystemAdmin().has_permission(request, view)


class CanAssignUnderwritingQueue(BasePermission):
    """
    Permission class that determines if a user can assign applications in the 
    underwriting queue to underwriters.
    
    Only system administrators can assign applications to underwriters.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to assign applications in the underwriting queue.
        
        Args:
            request: The request object
            view: The view that triggered the permission check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Only system administrators can assign applications
        return IsSystemAdmin().has_permission(request, view)
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to assign a specific queue item.
        
        Args:
            request: The request object
            view: The view that triggered the permission check
            obj: The underwriting queue object being accessed
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # System administrators can assign any application
        if IsSystemAdmin().has_permission(request, view):
            return True
        
        # Only pending applications can be assigned
        if obj.status != UNDERWRITING_QUEUE_STATUS['PENDING']:
            return False
        
        return False


class CanReviewApplication(BasePermission):
    """
    Permission class that determines if a user can review an application in the
    underwriting process.
    
    System administrators can review any application. Underwriters can only review
    applications assigned to them.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to review applications.
        
        Args:
            request: The request object
            view: The view that triggered the permission check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # System administrators can review any application
        if IsSystemAdmin().has_permission(request, view):
            return True
            
        # Underwriters can review applications
        if IsUnderwriter().has_permission(request, view):
            return True
            
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to review a specific application.
        
        Args:
            request: The request object
            view: The view that triggered the permission check
            obj: The underwriting queue object or application being accessed
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # System administrators can review any application
        if IsSystemAdmin().has_permission(request, view):
            return True
        
        # Get the queue entry for this application
        if isinstance(obj, UnderwritingQueue):
            queue_entry = obj
        else:
            # If obj is not a queue entry, assume it's an application and get its queue entry
            try:
                queue_entry = UnderwritingQueue.objects.get(application=obj)
            except UnderwritingQueue.DoesNotExist:
                return False
        
        # Underwriters can only review applications assigned to them
        if IsUnderwriter().has_permission(request, view):
            return queue_entry.assigned_to == request.user
        
        return False


class CanMakeUnderwritingDecision(BasePermission):
    """
    Permission class that determines if a user can make an underwriting decision
    on an application.
    
    System administrators can make decisions on any application. Underwriters can
    only make decisions on applications assigned to them.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to make underwriting decisions.
        
        Args:
            request: The request object
            view: The view that triggered the permission check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # System administrators can make decisions on any application
        if IsSystemAdmin().has_permission(request, view):
            return True
            
        # Underwriters can make decisions
        if IsUnderwriter().has_permission(request, view):
            return True
            
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to make a decision on a specific application.
        
        Args:
            request: The request object
            view: The view that triggered the permission check
            obj: The application or queue entry being accessed
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # System administrators can make decisions on any application
        if IsSystemAdmin().has_permission(request, view):
            return True
        
        # Get the queue entry for this application
        if isinstance(obj, UnderwritingQueue):
            queue_entry = obj
        else:
            # If obj is not a queue entry, assume it's an application and get its queue entry
            try:
                queue_entry = UnderwritingQueue.objects.get(application=obj)
            except UnderwritingQueue.DoesNotExist:
                return False
        
        # Underwriters can only make decisions on applications assigned to them
        if IsUnderwriter().has_permission(request, view):
            # Check if the application is assigned to this underwriter
            if queue_entry.assigned_to == request.user:
                return True
                
            # Check if the application is in progress status
            if queue_entry.status == UNDERWRITING_QUEUE_STATUS['IN_PROGRESS']:
                return True
                
        return False


class CanViewUnderwritingDecision(BasePermission):
    """
    Permission class that determines if a user can view an underwriting decision.
    
    Internal users can view all decisions. School administrators can view decisions
    for their school's applications. Borrowers and co-borrowers can view decisions
    for their own applications.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to view underwriting decisions.
        
        Args:
            request: The request object
            view: The view that triggered the permission check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # User must be authenticated
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to view a specific underwriting decision.
        
        Args:
            request: The request object
            view: The view that triggered the permission check
            obj: The underwriting decision being accessed
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # Internal users (system admin, underwriter, QC) can view all decisions
        if request.user.role in INTERNAL_ROLES:
            return True
        
        # If the object is a decision, get the related application
        if isinstance(obj, UnderwritingDecision):
            application = obj.application
        else:
            # If obj is not a decision, assume it's an application
            application = obj
        
        # School administrators can view decisions for their school's applications
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            return application.school == request.user.schooladminprofile.school
        
        # Borrowers can view decisions for their own applications
        if request.user.role == USER_ROLES['BORROWER']:
            return application.borrower == request.user
            
        # Co-borrowers can view decisions for applications they co-signed
        if request.user.role == USER_ROLES['CO_BORROWER']:
            return application.co_borrower == request.user
            
        return False


class CanManageStipulations(BasePermission):
    """
    Permission class that determines if a user can manage stipulations for an application.
    
    System administrators can manage any stipulations. Underwriters can manage
    stipulations for applications assigned to them. QC personnel can manage
    stipulations for applications in QC review.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to manage stipulations.
        
        Args:
            request: The request object
            view: The view that triggered the permission check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # System administrators can manage any stipulations
        if IsSystemAdmin().has_permission(request, view):
            return True
            
        # Underwriters can manage stipulations
        if IsUnderwriter().has_permission(request, view):
            return True
            
        # QC personnel can manage stipulations
        if IsQC().has_permission(request, view):
            return True
            
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to manage stipulations for a specific application.
        
        Args:
            request: The request object
            view: The view that triggered the permission check
            obj: The stipulation or application being accessed
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # System administrators can manage any stipulations
        if IsSystemAdmin().has_permission(request, view):
            return True
        
        # Get the application from the stipulation or use the object if it's already an application
        application = getattr(obj, 'application', obj)
        
        # Underwriters can manage stipulations for applications assigned to them
        if IsUnderwriter().has_permission(request, view):
            try:
                queue_entry = UnderwritingQueue.objects.get(application=application)
                return queue_entry.assigned_to == request.user
            except UnderwritingQueue.DoesNotExist:
                return False
        
        # QC personnel can manage stipulations for applications in QC review
        if IsQC().has_permission(request, view):
            return application.status in [
                APPLICATION_STATUS['QC_REVIEW'],
                APPLICATION_STATUS['QC_APPROVED'],
                APPLICATION_STATUS['QC_REJECTED']
            ]
            
        return False


class CanSatisfyStipulations(BasePermission):
    """
    Permission class that determines if a user can satisfy stipulations for an application.
    
    System administrators can satisfy any stipulations. Internal users can satisfy stipulations.
    School administrators can satisfy stipulations for their school's applications.
    Borrowers and co-borrowers can satisfy stipulations for their own applications.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to satisfy stipulations.
        
        Args:
            request: The request object
            view: The view that triggered the permission check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # User must be authenticated
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to satisfy a specific stipulation.
        
        Args:
            request: The request object
            view: The view that triggered the permission check
            obj: The stipulation being accessed
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # System administrators can satisfy any stipulations
        if IsSystemAdmin().has_permission(request, view):
            return True
        
        # Internal users can satisfy stipulations
        if request.user.role in INTERNAL_ROLES:
            return True
        
        # Get the application from the stipulation
        application = obj.application
        
        # School administrators can satisfy stipulations for their school's applications
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            return application.school == request.user.schooladminprofile.school
        
        # Borrowers can satisfy stipulations for their own applications
        if request.user.role == USER_ROLES['BORROWER']:
            return application.borrower == request.user
            
        # Co-borrowers can satisfy stipulations for applications they co-signed
        if request.user.role == USER_ROLES['CO_BORROWER']:
            return application.co_borrower == request.user
            
        return False


class CanAddUnderwritingNote(BasePermission):
    """
    Permission class that determines if a user can add notes to an application
    in the underwriting process.
    
    System administrators can add notes to any application. Underwriters can add
    notes to applications assigned to them. QC personnel can add notes to
    applications in QC review.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to add underwriting notes.
        
        Args:
            request: The request object
            view: The view that triggered the permission check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # System administrators can add notes to any application
        if IsSystemAdmin().has_permission(request, view):
            return True
            
        # Underwriters can add notes
        if IsUnderwriter().has_permission(request, view):
            return True
            
        # QC personnel can add notes
        if IsQC().has_permission(request, view):
            return True
            
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to add notes to a specific application.
        
        Args:
            request: The request object
            view: The view that triggered the permission check
            obj: The application being accessed
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # System administrators can add notes to any application
        if IsSystemAdmin().has_permission(request, view):
            return True
        
        # Underwriters can add notes to applications assigned to them
        if IsUnderwriter().has_permission(request, view):
            try:
                queue_entry = UnderwritingQueue.objects.get(application=obj)
                return queue_entry.assigned_to == request.user
            except UnderwritingQueue.DoesNotExist:
                return False
        
        # QC personnel can add notes to applications in QC review
        if IsQC().has_permission(request, view):
            return obj.status in [
                APPLICATION_STATUS['QC_REVIEW'],
                APPLICATION_STATUS['QC_APPROVED'],
                APPLICATION_STATUS['QC_REJECTED']
            ]
            
        return False


class CanViewUnderwritingNotes(BasePermission):
    """
    Permission class that determines if a user can view notes for an application
    in the underwriting process.
    
    Internal users can view all notes. School administrators can view notes for their
    school's applications, except internal notes. Borrowers and co-borrowers can view
    notes for their own applications, except internal notes.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to view underwriting notes.
        
        Args:
            request: The request object
            view: The view that triggered the permission check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # User must be authenticated
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to view notes for a specific application.
        
        Args:
            request: The request object
            view: The view that triggered the permission check
            obj: The note or application being accessed
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # Internal users can view all notes
        if request.user.role in INTERNAL_ROLES:
            return True
        
        # If the note is internal and the user is not internal, deny access
        if hasattr(obj, 'is_internal') and obj.is_internal and request.user.role not in INTERNAL_ROLES:
            return False
        
        # Get the application from the note or use the object if it's already an application
        application = getattr(obj, 'application', obj)
        
        # School administrators can view notes for their school's applications
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            return application.school == request.user.schooladminprofile.school
        
        # Borrowers can view notes for their own applications
        if request.user.role == USER_ROLES['BORROWER']:
            return application.borrower == request.user
            
        # Co-borrowers can view notes for applications they co-signed
        if request.user.role == USER_ROLES['CO_BORROWER']:
            return application.co_borrower == request.user
            
        return False


class CanViewCreditInformation(BasePermission):
    """
    Permission class that determines if a user can view credit information for an application.
    
    System administrators can view credit information for any application. Underwriters
    can view credit information for applications assigned to them. QC personnel can
    view credit information for applications in QC review.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to view credit information.
        
        Args:
            request: The request object
            view: The view that triggered the permission check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # System administrators can view credit information for any application
        if IsSystemAdmin().has_permission(request, view):
            return True
            
        # Underwriters can view credit information
        if IsUnderwriter().has_permission(request, view):
            return True
            
        # QC personnel can view credit information
        if IsQC().has_permission(request, view):
            return True
            
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to view credit information for a specific application.
        
        Args:
            request: The request object
            view: The view that triggered the permission check
            obj: The credit information or application being accessed
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # System administrators can view credit information for any application
        if IsSystemAdmin().has_permission(request, view):
            return True
        
        # Get the application from the credit information or use the object if it's already an application
        application = getattr(obj, 'application', obj)
        
        # Underwriters can view credit information for applications assigned to them
        if IsUnderwriter().has_permission(request, view):
            try:
                queue_entry = UnderwritingQueue.objects.get(application=application)
                return queue_entry.assigned_to == request.user
            except UnderwritingQueue.DoesNotExist:
                return False
        
        # QC personnel can view credit information for applications in QC review
        if IsQC().has_permission(request, view):
            return application.status in [
                APPLICATION_STATUS['QC_REVIEW'],
                APPLICATION_STATUS['QC_APPROVED'],
                APPLICATION_STATUS['QC_REJECTED']
            ]
            
        return False


class CanUploadCreditInformation(BasePermission):
    """
    Permission class that determines if a user can upload credit information for an application.
    
    System administrators can upload credit information for any application. Underwriters
    can upload credit information for applications assigned to them.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to upload credit information.
        
        Args:
            request: The request object
            view: The view that triggered the permission check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # System administrators can upload credit information for any application
        if IsSystemAdmin().has_permission(request, view):
            return True
            
        # Underwriters can upload credit information
        if IsUnderwriter().has_permission(request, view):
            return True
            
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to upload credit information for a specific application.
        
        Args:
            request: The request object
            view: The view that triggered the permission check
            obj: The application being accessed
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # System administrators can upload credit information for any application
        if IsSystemAdmin().has_permission(request, view):
            return True
        
        # Underwriters can upload credit information for applications assigned to them
        if IsUnderwriter().has_permission(request, view):
            try:
                queue_entry = UnderwritingQueue.objects.get(application=obj)
                return queue_entry.assigned_to == request.user
            except UnderwritingQueue.DoesNotExist:
                return False
                
        return False