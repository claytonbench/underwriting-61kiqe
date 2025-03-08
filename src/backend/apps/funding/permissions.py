from rest_framework.permissions import BasePermission, SAFE_METHODS
from ...core.permissions import (
    IsAuthenticated, IsSystemAdmin, IsQC, IsInternalUser, 
    USER_ROLES, has_object_permission_or_403
)
from .models import FundingRequest
from .constants import FUNDING_REQUEST_STATUS, FUNDING_APPROVAL_LEVELS, FUNDING_APPROVAL_THRESHOLDS


class CanViewFundingRequests(BasePermission):
    """
    Permission class that determines if a user can view funding requests.
    
    This permission allows System Administrators, QC personnel, and School Administrators
    to view funding requests. School Administrators can only view funding requests
    related to their school.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to view funding requests.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user has permission, False otherwise
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
            
        # System administrators can view all funding requests
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # QC personnel can view all funding requests
        if request.user.role == USER_ROLES['QC']:
            return True
            
        # School administrators can view funding requests for their school
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            return True
            
        # Other users cannot view funding requests
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to view a specific funding request.
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The funding request object
            
        Returns:
            True if user has permission, False otherwise
        """
        # System administrators can view all funding requests
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # QC personnel can view all funding requests
        if request.user.role == USER_ROLES['QC']:
            return True
            
        # School administrators can view funding requests for their school
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            # Check if the funding request's application is for the school admin's school
            return obj.application.school_id == request.user.school_id
            
        # Borrowers can view their own funding requests
        if request.user.role == USER_ROLES['BORROWER']:
            return obj.application.borrower_id == request.user.id
            
        # Co-borrowers can view their own funding requests
        if request.user.role == USER_ROLES['CO_BORROWER']:
            return obj.application.co_borrower_id == request.user.id
            
        # Other users cannot view funding requests
        return False


class CanManageFundingRequests(BasePermission):
    """
    Permission class that determines if a user can manage funding requests (create, update).
    
    This permission allows System Administrators and QC personnel to manage funding requests.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to manage funding requests.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user has permission, False otherwise
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
            
        # System administrators can manage funding requests
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # QC personnel can manage funding requests
        if request.user.role == USER_ROLES['QC']:
            return True
            
        # Other users cannot manage funding requests
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to manage a specific funding request.
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The funding request object
            
        Returns:
            True if user has permission, False otherwise
        """
        # System administrators can manage all funding requests
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # QC personnel can manage all funding requests
        if request.user.role == USER_ROLES['QC']:
            return True
            
        # Other users cannot manage funding requests
        return False


class CanVerifyEnrollment(BasePermission):
    """
    Permission class that determines if a user can verify enrollment for a funding request.
    
    This permission allows System Administrators, QC personnel, and School Administrators
    to verify enrollment. School Administrators can only verify enrollment for funding
    requests related to their school.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to verify enrollment.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user has permission, False otherwise
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
            
        # System administrators can verify enrollment
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # QC personnel can verify enrollment
        if request.user.role == USER_ROLES['QC']:
            return True
            
        # School administrators can verify enrollment for their school
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            return True
            
        # Other users cannot verify enrollment
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to verify enrollment for a specific funding request.
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The funding request object
            
        Returns:
            True if user has permission, False otherwise
        """
        # System administrators can verify enrollment for all funding requests
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # QC personnel can verify enrollment for all funding requests
        if request.user.role == USER_ROLES['QC']:
            return True
            
        # School administrators can verify enrollment for their school
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            # Check if the funding request's application is for the school admin's school
            school_match = obj.application.school_id == request.user.school_id
            
            # Verify that the funding request is in the appropriate status for enrollment verification
            status_check = obj.status == FUNDING_REQUEST_STATUS['PENDING']
            
            return school_match and status_check
            
        # Other users cannot verify enrollment
        return False


class CanCheckStipulations(BasePermission):
    """
    Permission class that determines if a user can check stipulations for a funding request.
    
    This permission allows System Administrators and QC personnel to check stipulations,
    but only for funding requests in appropriate statuses.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to check stipulations.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user has permission, False otherwise
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
            
        # System administrators can check stipulations
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # QC personnel can check stipulations
        if request.user.role == USER_ROLES['QC']:
            return True
            
        # Other users cannot check stipulations
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to check stipulations for a specific funding request.
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The funding request object
            
        Returns:
            True if user has permission, False otherwise
        """
        # System administrators can check stipulations for all funding requests
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # QC personnel can check stipulations for all funding requests
        if request.user.role == USER_ROLES['QC']:
            return True
            
        # Check if the funding request is in the appropriate status for stipulation checking
        valid_status = obj.status in [
            FUNDING_REQUEST_STATUS['ENROLLMENT_VERIFIED'],
            FUNDING_REQUEST_STATUS['PENDING_STIPULATIONS']
        ]
        
        if not valid_status:
            return False
            
        # Other users cannot check stipulations
        return False


class CanApproveFunding(BasePermission):
    """
    Permission class that determines if a user can approve a funding request.
    
    This permission allows System Administrators and QC personnel to approve funding
    requests, based on the required approval level for the funding amount.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to approve funding.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user has permission, False otherwise
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
            
        # System administrators can approve funding
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # QC personnel can approve funding
        if request.user.role == USER_ROLES['QC']:
            return True
            
        # Other users cannot approve funding
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to approve a specific funding request.
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The funding request object
            
        Returns:
            True if user has permission, False otherwise
        """
        # System administrators can approve all funding requests
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # QC personnel can approve funding requests
        if request.user.role == USER_ROLES['QC']:
            # Check if the funding request is in the appropriate status for approval
            if obj.status != FUNDING_REQUEST_STATUS['STIPULATIONS_COMPLETE']:
                return False
                
            # Get the required approval level for the funding amount
            required_level = FUNDING_APPROVAL_LEVELS['LEVEL_1']
            if obj.requested_amount > FUNDING_APPROVAL_THRESHOLDS['LEVEL_1']:
                required_level = FUNDING_APPROVAL_LEVELS['LEVEL_2']
                
            # Check if the user has the required approval level
            # QC personnel have Level 1 approval permission by default
            if required_level == FUNDING_APPROVAL_LEVELS['LEVEL_1']:
                return True
            else:
                # For Level 2, only system administrators have permission
                return False
                
        # Other users cannot approve funding
        return False


class CanScheduleDisbursement(BasePermission):
    """
    Permission class that determines if a user can schedule a disbursement for a funding request.
    
    This permission allows System Administrators and QC personnel to schedule disbursements,
    but only for funding requests that have been approved.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to schedule disbursements.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user has permission, False otherwise
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
            
        # System administrators can schedule disbursements
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # QC personnel can schedule disbursements
        if request.user.role == USER_ROLES['QC']:
            return True
            
        # Other users cannot schedule disbursements
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to schedule a disbursement for a specific funding request.
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The funding request object
            
        Returns:
            True if user has permission, False otherwise
        """
        # System administrators can schedule disbursements for all funding requests
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # QC personnel can schedule disbursements
        if request.user.role == USER_ROLES['QC']:
            # Check if the funding request is in the appropriate status for scheduling disbursements
            return obj.status == FUNDING_REQUEST_STATUS['APPROVED']
            
        # Other users cannot schedule disbursements
        return False


class CanProcessDisbursement(BasePermission):
    """
    Permission class that determines if a user can process a disbursement for a funding request.
    
    This permission allows only System Administrators to process disbursements for funding
    requests that have been scheduled for disbursement.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to process disbursements.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user has permission, False otherwise
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Only System administrators can process disbursements
        return request.user.role == USER_ROLES['SYSTEM_ADMIN']
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to process a disbursement for a specific funding request.
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The funding request object
            
        Returns:
            True if user has permission, False otherwise
        """
        # Only System administrators can process disbursements
        if request.user.role != USER_ROLES['SYSTEM_ADMIN']:
            return False
            
        # Check if the funding request is in the appropriate status for processing disbursements
        return obj.status == FUNDING_REQUEST_STATUS['SCHEDULED_FOR_DISBURSEMENT']


class CanCancelFunding(BasePermission):
    """
    Permission class that determines if a user can cancel a funding request.
    
    This permission allows System Administrators and QC personnel to cancel funding
    requests that have not been disbursed or rejected.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to cancel funding.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user has permission, False otherwise
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
            
        # System administrators can cancel funding
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # QC personnel can cancel funding
        if request.user.role == USER_ROLES['QC']:
            return True
            
        # Other users cannot cancel funding
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to cancel a specific funding request.
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The funding request object
            
        Returns:
            True if user has permission, False otherwise
        """
        # System administrators can cancel funding requests
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # QC personnel can cancel funding requests
        if request.user.role == USER_ROLES['QC']:
            # Cannot cancel disbursed or rejected funding requests
            if obj.status in [
                FUNDING_REQUEST_STATUS['DISBURSED'],
                FUNDING_REQUEST_STATUS['REJECTED']
            ]:
                return False
            return True
            
        # Other users cannot cancel funding
        return False


class CanAddFundingNote(BasePermission):
    """
    Permission class that determines if a user can add notes to a funding request.
    
    This permission allows System Administrators, QC personnel, and School Administrators
    to add notes to funding requests. School Administrators can only add notes to
    funding requests for their school.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to add funding notes.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user has permission, False otherwise
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
            
        # System administrators can add notes
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # QC personnel can add notes
        if request.user.role == USER_ROLES['QC']:
            return True
            
        # School administrators can add notes for their school
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            return True
            
        # Other users cannot add notes
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to add notes to a specific funding request.
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The funding request object
            
        Returns:
            True if user has permission, False otherwise
        """
        # System administrators can add notes to all funding requests
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # QC personnel can add notes to all funding requests
        if request.user.role == USER_ROLES['QC']:
            return True
            
        # School administrators can add notes to funding requests for their school
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            # Check if the funding request's application is for the school admin's school
            return obj.application.school_id == request.user.school_id
            
        # Other users cannot add notes
        return False


class CanViewFundingNotes(BasePermission):
    """
    Permission class that determines if a user can view notes for a funding request.
    
    This permission allows various users to view funding notes, with restrictions
    based on user role and note type (internal notes are only visible to internal users).
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to view funding notes.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user has permission, False otherwise
        """
        # User must be authenticated
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to view notes for a specific funding request.
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The funding note object
            
        Returns:
            True if user has permission, False otherwise
        """
        # System administrators can view all notes
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # QC personnel can view all notes
        if request.user.role == USER_ROLES['QC']:
            return True
            
        # Check if the note is internal and the user is not an internal user
        if getattr(obj, 'is_internal', False) and request.user.role not in [
            USER_ROLES['SYSTEM_ADMIN'],
            USER_ROLES['UNDERWRITER'],
            USER_ROLES['QC']
        ]:
            return False
            
        # School administrators can view notes for their school
        if request.user.role == USER_ROLES['SCHOOL_ADMIN']:
            # Check if the note's funding request's application is for the school admin's school
            return obj.funding_request.application.school_id == request.user.school_id
            
        # Borrowers can view notes for their own funding requests
        if request.user.role == USER_ROLES['BORROWER']:
            return obj.funding_request.application.borrower_id == request.user.id
            
        # Co-borrowers can view notes for their own funding requests
        if request.user.role == USER_ROLES['CO_BORROWER']:
            return obj.funding_request.application.co_borrower_id == request.user.id
            
        # Other users cannot view notes
        return False


class HasLevel1ApprovalPermission(BasePermission):
    """
    Permission class that checks if a user has Level 1 funding approval permission.
    
    This permission is used to determine if a user can approve funding requests
    that require Level 1 approval (typically lower amounts).
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has Level 1 approval permission.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user has Level 1 approval permission, False otherwise
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
            
        # System administrators have Level 1 approval permission
        if request.user.role == USER_ROLES['SYSTEM_ADMIN']:
            return True
            
        # QC personnel have Level 1 approval permission
        if request.user.role == USER_ROLES['QC']:
            return True
            
        # Other users don't have Level 1 approval permission
        return False


class HasLevel2ApprovalPermission(BasePermission):
    """
    Permission class that checks if a user has Level 2 funding approval permission.
    
    This permission is used to determine if a user can approve funding requests
    that require Level 2 approval (typically higher amounts).
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has Level 2 approval permission.
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            True if user has Level 2 approval permission, False otherwise
        """
        # User must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Only System administrators have Level 2 approval permission
        return request.user.role == USER_ROLES['SYSTEM_ADMIN']