from rest_framework.permissions import BasePermission, SAFE_METHODS

from ...core.permissions import (
    IsAuthenticated, IsSystemAdmin, IsUnderwriter, IsQC, IsSchoolAdmin,
    IsBorrower, IsCoBorrower, IsInternalUser, IsOwner, IsOwnerOrReadOnly,
    IsOwnerOrInternalUser, IsSchoolAdminForSchool, USER_ROLES, INTERNAL_ROLES
)
from ...utils.constants import APPLICATION_STATUS
from ..applications.constants import APPLICATION_EDITABLE_STATUSES


class CanViewApplication(BasePermission):
    """
    Permission class that determines if a user can view a loan application
    """

    def has_permission(self, request, view):
        """
        Check if the user has permission to view applications
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # User must be authenticated to view applications
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to view a specific application
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The loan application object
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        user = request.user

        # System admins, underwriters, and QC personnel can view all applications
        if (user.role == USER_ROLES['SYSTEM_ADMIN'] or 
            user.role == USER_ROLES['UNDERWRITER'] or 
            user.role == USER_ROLES['QC']):
            return True
        
        # School admins can view applications for their school
        if user.role == USER_ROLES['SCHOOL_ADMIN'] and obj.school_id == user.school_id:
            return True
        
        # Borrowers can view their own applications
        if user.role == USER_ROLES['BORROWER'] and obj.borrower_id == user.id:
            return True
        
        # Co-borrowers can view applications they're associated with
        if user.role == USER_ROLES['CO_BORROWER'] and obj.co_borrower_id == user.id:
            return True
        
        return False


class CanCreateApplication(BasePermission):
    """
    Permission class that determines if a user can create a loan application
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to create applications
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        user = request.user
        
        # User must be authenticated
        if not user or not user.is_authenticated:
            return False
        
        # System admins can create applications
        if user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
        
        # School admins can create applications
        if user.role == USER_ROLES['SCHOOL_ADMIN']:
            return True
        
        # Borrowers can create applications
        if user.role == USER_ROLES['BORROWER']:
            return True
        
        return False


class CanEditApplication(BasePermission):
    """
    Permission class that determines if a user can edit a loan application
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to edit applications
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # User must be authenticated to edit applications
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to edit a specific application
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The loan application object
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        user = request.user
        
        # System admins can edit any application
        if user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
        
        # Applications must be in an editable status
        if obj.status not in APPLICATION_EDITABLE_STATUSES:
            return False
        
        # School admins can edit applications for their school
        if user.role == USER_ROLES['SCHOOL_ADMIN'] and obj.school_id == user.school_id:
            return True
        
        # Borrowers can edit their own applications
        if user.role == USER_ROLES['BORROWER'] and obj.borrower_id == user.id:
            return True
        
        return False


class CanSubmitApplication(BasePermission):
    """
    Permission class that determines if a user can submit a loan application
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to submit applications
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # User must be authenticated to submit applications
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to submit a specific application
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The loan application object
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        user = request.user
        
        # Application must be in DRAFT status to be submitted
        if obj.status != APPLICATION_STATUS['DRAFT']:
            return False
        
        # System admins can submit any application
        if user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
        
        # School admins can submit applications for their school
        if user.role == USER_ROLES['SCHOOL_ADMIN'] and obj.school_id == user.school_id:
            return True
        
        # Borrowers can submit their own applications
        if user.role == USER_ROLES['BORROWER'] and obj.borrower_id == user.id:
            return True
        
        return False


class CanUpdateApplicationStatus(BasePermission):
    """
    Permission class that determines if a user can update the status of a loan application
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to update application status
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        user = request.user
        
        # User must be authenticated
        if not user or not user.is_authenticated:
            return False
        
        # System admins can update status
        if user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
        
        # Underwriters can update status
        if user.role == USER_ROLES['UNDERWRITER']:
            return True
        
        # QC personnel can update status
        if user.role == USER_ROLES['QC']:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to update status of a specific application
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The loan application object
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        user = request.user
        
        # System admins can update any application status
        if user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
        
        # Determine the new status from the request data
        new_status = request.data.get('status', obj.status)
        current_status = obj.status
        
        # Underwriters can update status within their permitted transitions
        if user.role == USER_ROLES['UNDERWRITER']:
            # Check if the status transition is valid for underwriters
            valid_transitions = {
                APPLICATION_STATUS['SUBMITTED']: [
                    APPLICATION_STATUS['IN_REVIEW'],
                    APPLICATION_STATUS['INCOMPLETE']
                ],
                APPLICATION_STATUS['IN_REVIEW']: [
                    APPLICATION_STATUS['APPROVED'],
                    APPLICATION_STATUS['DENIED'],
                    APPLICATION_STATUS['REVISION_REQUESTED']
                ],
                APPLICATION_STATUS['REVISION_REQUESTED']: [
                    APPLICATION_STATUS['IN_REVIEW']
                ],
                APPLICATION_STATUS['COUNTER_OFFER_MADE']: [
                    APPLICATION_STATUS['IN_REVIEW']
                ]
            }
            
            if current_status in valid_transitions and new_status in valid_transitions.get(current_status, []):
                return True
        
        # QC personnel can update status within their permitted transitions
        if user.role == USER_ROLES['QC']:
            # Check if the status transition is valid for QC
            valid_transitions = {
                APPLICATION_STATUS['FULLY_EXECUTED']: [
                    APPLICATION_STATUS['QC_REVIEW']
                ],
                APPLICATION_STATUS['QC_REVIEW']: [
                    APPLICATION_STATUS['QC_APPROVED'],
                    APPLICATION_STATUS['QC_REJECTED']
                ],
                APPLICATION_STATUS['QC_REJECTED']: [
                    APPLICATION_STATUS['QC_REVIEW']
                ],
                APPLICATION_STATUS['QC_APPROVED']: [
                    APPLICATION_STATUS['READY_TO_FUND']
                ]
            }
            
            if current_status in valid_transitions and new_status in valid_transitions.get(current_status, []):
                return True
        
        return False


class CanDeleteApplication(BasePermission):
    """
    Permission class that determines if a user can delete a loan application
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to delete applications
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # User must be authenticated to delete applications
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to delete a specific application
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The loan application object
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        user = request.user
        
        # System admins can delete any application
        if user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
        
        # Applications must be in DRAFT status to be deleted
        if obj.status != APPLICATION_STATUS['DRAFT']:
            return False
        
        # School admins can delete applications for their school
        if user.role == USER_ROLES['SCHOOL_ADMIN'] and obj.school_id == user.school_id:
            return True
        
        # Borrowers can delete their own applications
        if user.role == USER_ROLES['BORROWER'] and obj.borrower_id == user.id:
            return True
        
        return False


class CanUploadDocuments(BasePermission):
    """
    Permission class that determines if a user can upload documents to a loan application
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to upload documents
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # User must be authenticated to upload documents
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to upload documents to a specific application
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The loan application object
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        user = request.user
        
        # System admins can upload documents to any application
        if user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
        
        # School admins can upload documents to applications for their school
        if user.role == USER_ROLES['SCHOOL_ADMIN'] and obj.school_id == user.school_id:
            return True
        
        # Borrowers can upload documents to their own applications
        if user.role == USER_ROLES['BORROWER'] and obj.borrower_id == user.id:
            return True
        
        # Co-borrowers can upload documents to applications they're associated with
        if user.role == USER_ROLES['CO_BORROWER'] and obj.co_borrower_id == user.id:
            return True
        
        return False


class CanViewApplicationDocuments(BasePermission):
    """
    Permission class that determines if a user can view documents of a loan application
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to view application documents
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # User must be authenticated to view application documents
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to view documents of a specific application
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The loan application object
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        user = request.user
        
        # System admins, underwriters, and QC personnel can view all application documents
        if (user.role == USER_ROLES['SYSTEM_ADMIN'] or 
            user.role == USER_ROLES['UNDERWRITER'] or 
            user.role == USER_ROLES['QC']):
            return True
        
        # School admins can view documents for applications from their school
        if user.role == USER_ROLES['SCHOOL_ADMIN'] and obj.school_id == user.school_id:
            return True
        
        # Borrowers can view documents for their own applications
        if user.role == USER_ROLES['BORROWER'] and obj.borrower_id == user.id:
            return True
        
        # Co-borrowers can view documents for applications they're associated with
        if user.role == USER_ROLES['CO_BORROWER'] and obj.co_borrower_id == user.id:
            return True
        
        return False


class CanDeleteApplicationDocument(BasePermission):
    """
    Permission class that determines if a user can delete a document from a loan application
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to delete application documents
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # User must be authenticated to delete application documents
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to delete a specific document
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The document object
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        user = request.user
        
        # System admins can delete any document
        if user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
        
        # Get the application associated with the document
        application = obj.application
        
        # Applications must be in an editable status
        if application.status not in APPLICATION_EDITABLE_STATUSES:
            return False
        
        # User who uploaded the document can delete it
        if obj.uploaded_by == user.id:
            return True
        
        # School admins can delete documents for applications from their school
        if user.role == USER_ROLES['SCHOOL_ADMIN'] and application.school_id == user.school_id:
            return True
        
        return False