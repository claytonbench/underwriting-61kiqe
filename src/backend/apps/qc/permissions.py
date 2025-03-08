"""Defines permission classes for the Quality Control (QC) module of the loan management system.
These classes control access to QC-related views and operations based on user roles and relationships to QC reviews.
The permissions ensure that only authorized users can view, create, assign, and manage QC reviews, as well as verify documents, stipulations, and checklist items."""

from rest_framework.permissions import BasePermission  # rest_framework.permissions version: 3.14+
from rest_framework.exceptions import PermissionDenied  # rest_framework.exceptions version: 3.14+

from core.permissions import IsAuthenticated, IsQC, IsSystemAdmin, has_object_permission_or_403, USER_ROLES  # Importing permission classes and utility function
from .models import QCReview  # Importing QCReview model
from .constants import QC_STATUS  # Importing QC status constants


class CanViewQCReviews(BasePermission):
    """Permission class that allows QC personnel and system administrators to view QC reviews"""

    def has_permission(self, request, view):
        """Check if the user has permission to view QC reviews

        Args:
            request: The request object
            view: The view that triggered the check

        Returns:
            bool: True if user is QC personnel or system admin, False otherwise
        """
        if not IsAuthenticated().has_permission(request, view):
            return False

        return request.user.role in [USER_ROLES['QC'], USER_ROLES['SYSTEM_ADMIN']]


class CanManageQCReviews(BasePermission):
    """Permission class that allows QC personnel and system administrators to create and manage QC reviews"""

    def has_permission(self, request, view):
        """Check if the user has permission to manage QC reviews

        Args:
            request: The request object
            view: The view that triggered the check

        Returns:
            bool: True if user is QC personnel or system admin, False otherwise
        """
        if not IsAuthenticated().has_permission(request, view):
            return False

        return request.user.role in [USER_ROLES['QC'], USER_ROLES['SYSTEM_ADMIN']]


class IsAssignedQCReviewer(BasePermission):
    """Permission class that checks if the user is the assigned reviewer for a QC review"""

    def has_permission(self, request, view):
        """Check if the user has QC role

        Args:
            request: The request object
            view: The view that triggered the check

        Returns:
            bool: True if user is QC personnel, False otherwise
        """
        if not IsAuthenticated().has_permission(request, view):
            return False

        return IsQC().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        """Check if the user is the assigned reviewer for the QC review

        Args:
            request: The request object
            view: The view that triggered the check
            obj: The object to check permissions for

        Returns:
            bool: True if user is the assigned reviewer or system admin, False otherwise
        """
        if IsSystemAdmin().has_permission(request, view):
            return True

        return obj.assigned_to == request.user


class CanAssignQCReviews(BasePermission):
    """Permission class that allows QC personnel and system administrators to assign QC reviews"""

    def has_permission(self, request, view):
        """Check if the user has permission to assign QC reviews

        Args:
            request: The request object
            view: The view that triggered the check

        Returns:
            bool: True if user is QC personnel or system admin, False otherwise
        """
        if not IsAuthenticated().has_permission(request, view):
            return False

        return request.user.role in [USER_ROLES['QC'], USER_ROLES['SYSTEM_ADMIN']]


class CanApproveQCReview(BasePermission):
    """Permission class that allows QC personnel to approve QC reviews"""

    def has_permission(self, request, view):
        """Check if the user has QC role

        Args:
            request: The request object
            view: The view that triggered the check

        Returns:
            bool: True if user is QC personnel, False otherwise
        """
        if not IsAuthenticated().has_permission(request, view):
            return False

        return IsQC().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        """Check if the user is the assigned reviewer and the review is in a state that can be approved

        Args:
            request: The request object
            view: The view that triggered the check
            obj: The object to check permissions for

        Returns:
            bool: True if user is assigned and review can be approved, False otherwise
        """
        if IsSystemAdmin().has_permission(request, view):
            return True

        if obj.assigned_to != request.user:
            return False

        if obj.status != QC_STATUS['IN_REVIEW']:
            return False

        if not obj.is_complete():
            return False

        return True


class CanReturnQCReview(BasePermission):
    """Permission class that allows QC personnel to return QC reviews for correction"""

    def has_permission(self, request, view):
        """Check if the user has QC role

        Args:
            request: The request object
            view: The view that triggered the check

        Returns:
            bool: True if user is QC personnel, False otherwise
        """
        if not IsAuthenticated().has_permission(request, view):
            return False

        return IsQC().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        """Check if the user is the assigned reviewer and the review is in a state that can be returned

        Args:
            request: The request object
            view: The view that triggered the check
            obj: The object to check permissions for

        Returns:
            bool: True if user is assigned and review can be returned, False otherwise
        """
        if IsSystemAdmin().has_permission(request, view):
            return True

        if obj.assigned_to != request.user:
            return False

        if obj.status != QC_STATUS['IN_REVIEW']:
            return False

        return True


class CanVerifyDocuments(BasePermission):
    """Permission class that allows QC personnel to verify documents"""

    def has_permission(self, request, view):
        """Check if the user has QC role

        Args:
            request: The request object
            view: The view that triggered the check

        Returns:
            bool: True if user is QC personnel, False otherwise
        """
        if not IsAuthenticated().has_permission(request, view):
            return False

        return IsQC().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        """Check if the user is the assigned reviewer for the QC review associated with the document

        Args:
            request: The request object
            view: The view that triggered the check
            obj: The object to check permissions for

        Returns:
            bool: True if user is assigned to the associated QC review, False otherwise
        """
        if IsSystemAdmin().has_permission(request, view):
            return True

        qc_review = obj.qc_review

        if qc_review.assigned_to != request.user:
            return False

        if qc_review.status != QC_STATUS['IN_REVIEW']:
            return False

        return True


class CanVerifyStipulations(BasePermission):
    """Permission class that allows QC personnel to verify stipulations"""

    def has_permission(self, request, view):
        """Check if the user has QC role

        Args:
            request: The request object
            view: The view that triggered the check

        Returns:
            bool: True if user is QC personnel, False otherwise
        """
        if not IsAuthenticated().has_permission(request, view):
            return False

        return IsQC().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        """Check if the user is the assigned reviewer for the QC review associated with the stipulation

        Args:
            request: The request object
            view: The view that triggered the check
            obj: The object to check permissions for

        Returns:
            bool: True if user is assigned to the associated QC review, False otherwise
        """
        if IsSystemAdmin().has_permission(request, view):
            return True

        qc_review = obj.qc_review

        if qc_review.assigned_to != request.user:
            return False

        if qc_review.status != QC_STATUS['IN_REVIEW']:
            return False

        return True


class CanManageQCChecklist(BasePermission):
    """Permission class that allows QC personnel to manage checklist items"""

    def has_permission(self, request, view):
        """Check if the user has QC role

        Args:
            request: The request object
            view: The view that triggered the check

        Returns:
            bool: True if user is QC personnel, False otherwise
        """
        if not IsAuthenticated().has_permission(request, view):
            return False

        return IsQC().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        """Check if the user is the assigned reviewer for the QC review associated with the checklist item

        Args:
            request: The request object
            view: The view that triggered the check
            obj: The object to check permissions for

        Returns:
            bool: True if user is assigned to the associated QC review, False otherwise
        """
        if IsSystemAdmin().has_permission(request, view):
            return True

        qc_review = obj.qc_review

        if qc_review.assigned_to != request.user:
            return False

        if qc_review.status != QC_STATUS['IN_REVIEW']:
            return False

        return True