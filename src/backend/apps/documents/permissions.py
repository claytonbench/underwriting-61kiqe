"""Defines permission classes for document management in the loan management system.
These classes control access to document templates, document packages, individual documents,
and signature requests based on user roles and relationships to the documents."""

from rest_framework.permissions import BasePermission, SAFE_METHODS  # rest_framework.permissions 3.14+

from core.permissions import IsAuthenticated, IsSystemAdmin, IsUnderwriter, IsQC, IsSchoolAdmin, IsBorrower, IsCoBorrower, IsInternalUser, IsOwnerOrInternalUser, IsSchoolAdminForSchool, has_object_permission_or_403, USER_ROLES  # Internal import
from .models import Document, DocumentPackage, SignatureRequest  # Internal import
from .constants import SIGNER_TYPES  # Internal import


class CanManageDocumentTemplates(BasePermission):
    """Permission class that allows only system administrators to manage document templates"""

    def __init__(self):
        """Default constructor inherited from BasePermission"""
        super().__init__()

    def has_permission(self, request, view):
        """Check if the user has permission to manage document templates

        Args:
            request: The request object
            view: The view that triggered the check

        Returns:
            bool: True if user is a system administrator, False otherwise
        """
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return bool(request.user and request.user.is_authenticated and request.user.role == USER_ROLES['SYSTEM_ADMIN'])


class CanGenerateDocuments(BasePermission):
    """Permission class that allows internal users and school administrators to generate documents"""

    def __init__(self):
        """Default constructor inherited from BasePermission"""
        super().__init__()

    def has_permission(self, request, view):
        """Check if the user has permission to generate documents

        Args:
            request: The request object
            view: The view that triggered the check

        Returns:
            bool: True if user is an internal user or school administrator, False otherwise
        """
        if not request.user or not request.user.is_authenticated:
            return False

        is_internal = request.user.role in ['system_admin', 'underwriter', 'qc']
        is_school_admin = request.user.role == 'school_admin'

        return is_internal or is_school_admin


class CanViewDocument(BasePermission):
    """Permission class that checks if a user can view a document"""

    def __init__(self):
        """Default constructor inherited from BasePermission"""
        super().__init__()

    def has_permission(self, request, view):
        """Check if the user is authenticated

        Args:
            request: The request object
            view: The view that triggered the check

        Returns:
            bool: True if user is authenticated, False otherwise
        """
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Check if the user can view the specific document

        Args:
            request: The request object
            view: The view that triggered the check
            obj: The object to check permissions for

        Returns:
            bool: True if user has permission to view the document, False otherwise
        """
        # Allow internal users (system admin, underwriter, QC)
        if request.user.role in ['system_admin', 'underwriter', 'qc']:
            return True

        # Get the application associated with the document
        application = obj.package.application

        # Check if user is the borrower of the application
        if request.user == application.borrower:
            return True

        # Check if user is the co-borrower of the application
        if application.co_borrower and request.user == application.co_borrower:
            return True

        # Check if user is a school admin for the application's school
        if request.user.role == 'school_admin' and request.user.school_id == application.school_id:
            return True

        return False


class CanViewDocumentPackage(BasePermission):
    """Permission class that checks if a user can view a document package"""

    def __init__(self):
        """Default constructor inherited from BasePermission"""
        super().__init__()

    def has_permission(self, request, view):
        """Check if the user is authenticated

        Args:
            request: The request object
            view: The view that triggered the check

        Returns:
            bool: True if user is authenticated, False otherwise
        """
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Check if the user can view the specific document package

        Args:
            request: The request object
            view: The view that triggered the check
            obj: The object to check permissions for

        Returns:
            bool: True if user has permission to view the document package, False otherwise
        """
        # Allow internal users (system admin, underwriter, QC)
        if request.user.role in ['system_admin', 'underwriter', 'qc']:
            return True

        # Get the application associated with the document package
        application = obj.application

        # Check if user is the borrower of the application
        if request.user == application.borrower:
            return True

        # Check if user is the co-borrower of the application
        if application.co_borrower and request.user == application.co_borrower:
            return True

        # Check if user is a school admin for the application's school
        if request.user.role == 'school_admin' and request.user.school_id == application.school_id:
            return True

        return False


class CanDownloadDocument(BasePermission):
    """Permission class that checks if a user can download a document"""

    def __init__(self):
        """Default constructor inherited from BasePermission"""
        super().__init__()

    def has_permission(self, request, view):
        """Check if the user is authenticated

        Args:
            request: The request object
            view: The view that triggered the check

        Returns:
            bool: True if user is authenticated, False otherwise
        """
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Check if the user can download the specific document

        Args:
            request: The request object
            view: The view that triggered the check
            obj: The object to check permissions for

        Returns:
            bool: True if user has permission to download the document, False otherwise
        """
        # Allow internal users (system admin, underwriter, QC)
        if request.user.role in ['system_admin', 'underwriter', 'qc']:
            return True

        # Get the application associated with the document
        application = obj.package.application

        # Check if user is the borrower of the application
        if request.user == application.borrower:
            return True

        # Check if user is the co-borrower of the application
        if application.co_borrower and request.user == application.co_borrower:
            return True

        # Check if user is a school admin for the application's school
        if request.user.role == 'school_admin' and request.user.school_id == application.school_id:
            return True

        return False


class CanSignDocument(BasePermission):
    """Permission class that checks if a user can sign a document"""

    def __init__(self):
        """Default constructor inherited from BasePermission"""
        super().__init__()

    def has_permission(self, request, view):
        """Check if the user is authenticated

        Args:
            request: The request object
            view: The view that triggered the check

        Returns:
            bool: True if user is authenticated, False otherwise
        """
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Check if the user can sign the specific document

        Args:
            request: The request object
            view: The view that triggered the check
            obj: The object to check permissions for

        Returns:
            bool: True if user has permission to sign the document, False otherwise
        """
        # Get the signature requests for the document
        signature_requests = obj.signature_requests.all()

        # Filter signature requests for the current user
        user_signature_requests = [sig for sig in signature_requests if sig.signer == request.user]

        # Check if there are any pending signature requests for the user
        has_pending_request = any(sig.status == 'pending' for sig in user_signature_requests)

        return has_pending_request


class IsDocumentSigner(BasePermission):
    """Permission class that checks if a user is a signer for a signature request"""

    def __init__(self):
        """Default constructor inherited from BasePermission"""
        super().__init__()

    def has_permission(self, request, view):
        """Check if the user is authenticated

        Args:
            request: The request object
            view: The view that triggered the check

        Returns:
            bool: True if user is authenticated, False otherwise
        """
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Check if the user is the signer for the signature request

        Args:
            request: The request object
            view: The view that triggered the check
            obj: The object to check permissions for

        Returns:
            bool: True if user is the signer, False otherwise
        """
        # Check if user is the signer for the signature request
        return obj.signer == request.user


class CanManageSignatureRequests(BasePermission):
    """Permission class that allows internal users to manage signature requests"""

    def __init__(self):
        """Default constructor inherited from BasePermission"""
        super().__init__()

    def has_permission(self, request, view):
        """Check if the user has permission to manage signature requests

        Args:
            request: The request object
            view: The view that triggered the check

        Returns:
            bool: True if user is an internal user, False otherwise
        """
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.role in ['system_admin', 'underwriter', 'qc']

    def has_object_permission(self, request, view, obj):
        """Check if the user can manage the specific signature request

        Args:
            request: The request object
            view: The view that triggered the check
            obj: The object to check permissions for

        Returns:
            bool: True if user is an internal user, False otherwise
        """
        return request.user.role in ['system_admin', 'underwriter', 'qc']


class CanRequestSignatures(BasePermission):
    """Permission class that allows internal users and school administrators to request signatures"""

    def __init__(self):
        """Default constructor inherited from BasePermission"""
        super().__init__()

    def has_permission(self, request, view):
        """Check if the user has permission to request signatures

        Args:
            request: The request object
            view: The view that triggered the check

        Returns:
            bool: True if user is an internal user or school administrator, False otherwise
        """
        if not request.user or not request.user.is_authenticated:
            return False

        is_internal = request.user.role in ['system_admin', 'underwriter', 'qc']
        is_school_admin = request.user.role == 'school_admin'

        return is_internal or is_school_admin

    def has_object_permission(self, request, view, obj):
        """Check if the user can request signatures for the specific document

        Args:
            request: The request object
            view: The view that triggered the check
            obj: The object to check permissions for

        Returns:
            bool: True if user has permission to request signatures, False otherwise
        """
        # Allow internal users (system admin, underwriter, QC)
        if request.user.role in ['system_admin', 'underwriter', 'qc']:
            return True

        # Get the application associated with the document
        application = obj.package.application

        # Check if user is a school admin for the application's school
        if request.user.role == 'school_admin' and request.user.school_id == application.school_id:
            return True

        return False


class CanAccessDocuSignWebhook(BasePermission):
    """Permission class that allows DocuSign webhook requests"""

    def __init__(self):
        """Default constructor inherited from BasePermission"""
        super().__init__()

    def has_permission(self, request, view):
        """Check if the request is a valid DocuSign webhook request

        Args:
            request: The request object
            view: The view that triggered the check

        Returns:
            bool: True if request is a valid DocuSign webhook request, False otherwise
        """
        # Check for DocuSign webhook headers or authentication tokens
        # Validate the webhook request based on DocuSign security requirements
        # (e.g., HMAC signature verification)
        # For simplicity, this example always returns True
        return True