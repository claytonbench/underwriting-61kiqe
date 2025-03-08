"""
Defines the data models for the Quality Control (QC) module of the loan management system.

This includes models for QC reviews, document verification, stipulation verification,
and checklist items. The QC process is a critical step that occurs after document
completion and before funding approval to ensure all loan documents are accurate,
complete, and compliant.
"""

from django.db import models  # Django 4.2+
from django.utils import timezone  # Django 4.2+
from django.core.exceptions import ValidationError  # Django 4.2+

from core.models import CoreModel, ActiveManager  # Importing CoreModel and ActiveManager
from apps.applications.models import LoanApplication  # Importing LoanApplication model
from apps.documents.models import Document  # Importing Document model
from apps.underwriting.models import Stipulation  # Importing Stipulation model
from apps.users.models import User  # Importing User model
from .constants import (  # Importing QC-related constants
    QC_STATUS, QC_VERIFICATION_STATUS, QC_RETURN_REASON,
    QC_CHECKLIST_CATEGORY, QC_PRIORITY, QC_ASSIGNMENT_TYPE,
    QC_STATUS_TO_APPLICATION_STATUS
)

# Defining global tuples for choices in model fields
QC_STATUS_CHOICES = ([(status, label) for status, label in QC_STATUS.items()])
QC_VERIFICATION_STATUS_CHOICES = ([(status, label) for status, label in QC_VERIFICATION_STATUS.items()])
QC_RETURN_REASON_CHOICES = ([(reason, label) for reason, label in QC_RETURN_REASON.items()])
QC_CHECKLIST_CATEGORY_CHOICES = ([(category, label) for category, label in QC_CHECKLIST_CATEGORY.items()])
QC_PRIORITY_CHOICES = ([(priority, label) for priority, label in QC_PRIORITY.items()])
QC_ASSIGNMENT_TYPE_CHOICES = ([(assignment_type, label) for assignment_type, label in QC_ASSIGNMENT_TYPE.items()])


class QCReviewManager(ActiveManager):
    """
    Custom manager for QCReview model to provide additional query methods
    """

    def get_by_status(self, status):
        """
        Returns QC reviews filtered by status
        Args:
            status (str): The status to filter by
        Returns:
            QuerySet: QuerySet of QCReview objects with the specified status
        """
        queryset = self.get_queryset()  # Get the base queryset from parent method
        return queryset.filter(status=status)  # Filter queryset by the specified status

    def get_pending_reviews(self):
        """
        Returns QC reviews that are pending review
        Returns:
            QuerySet: QuerySet of QCReview objects with PENDING status
        """
        queryset = self.get_queryset()  # Get the base queryset from parent method
        return queryset.filter(status=QC_STATUS['PENDING'])  # Filter queryset where status is QC_STATUS['PENDING']

    def get_in_progress_reviews(self):
        """
        Returns QC reviews that are in progress
        Returns:
            QuerySet: QuerySet of QCReview objects with IN_REVIEW status
        """
        queryset = self.get_queryset()  # Get the base queryset from parent method
        return queryset.filter(status=QC_STATUS['IN_REVIEW'])  # Filter queryset where status is QC_STATUS['IN_REVIEW']

    def get_approved_reviews(self):
        """
        Returns QC reviews that have been approved
        Returns:
            QuerySet: QuerySet of QCReview objects with APPROVED status
        """
        queryset = self.get_queryset()  # Get the base queryset from parent method
        return queryset.filter(status=QC_STATUS['APPROVED'])  # Filter queryset where status is QC_STATUS['APPROVED']

    def get_returned_reviews(self):
        """
        Returns QC reviews that have been returned for correction
        Returns:
            QuerySet: QuerySet of QCReview objects with RETURNED status
        """
        queryset = self.get_queryset()  # Get the base queryset from parent method
        return queryset.filter(status=QC_STATUS['RETURNED'])  # Filter queryset where status is QC_STATUS['RETURNED']

    def get_by_reviewer(self, reviewer):
        """
        Returns QC reviews assigned to a specific reviewer
        Args:
            reviewer (User): The reviewer to filter by
        Returns:
            QuerySet: QuerySet of QCReview objects assigned to the specified reviewer
        """
        queryset = self.get_queryset()  # Get the base queryset from parent method
        return queryset.filter(assigned_to=reviewer)  # Filter queryset where assigned_to is the specified reviewer

    def get_by_priority(self, priority):
        """
        Returns QC reviews with a specific priority
        Args:
            priority (str): The priority to filter by
        Returns:
            QuerySet: QuerySet of QCReview objects with the specified priority
        """
        queryset = self.get_queryset()  # Get the base queryset from parent method
        return queryset.filter(priority=priority)  # Filter queryset where priority is the specified priority


class QCReview(CoreModel):
    """
    Model representing a quality control review for a loan application
    """
    application = models.OneToOneField(
        LoanApplication,
        on_delete=models.CASCADE,
        related_name='qc_review'
    )
    status = models.CharField(
        max_length=20,
        choices=QC_STATUS_CHOICES,
        default=QC_STATUS['PENDING']
    )
    priority = models.CharField(
        max_length=20,
        choices=QC_PRIORITY_CHOICES,
        default=QC_PRIORITY['MEDIUM']
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_qc_reviews'
    )
    assignment_type = models.CharField(
        max_length=20,
        choices=QC_ASSIGNMENT_TYPE_CHOICES,
        default=QC_ASSIGNMENT_TYPE['MANUAL']
    )
    assigned_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    return_reason = models.CharField(
        max_length=50,
        choices=QC_RETURN_REASON_CHOICES,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True)

    # Custom managers
    objects = QCReviewManager()
    all_objects = models.Manager()

    def save(self, **kwargs):
        """
        Override save method to handle QC review-specific logic
        Args:
            **kwargs: Additional keyword arguments to pass to the parent save method
        Returns:
            None: No return value
        """
        if not self.pk:  # If this is a new QC review (no ID)
            if not self.assigned_at:
                self.assigned_at = timezone.now()  # set assigned_at to current time if not provided

        if self.status == QC_STATUS['APPROVED']:  # If status is changing to APPROVED
            self.completed_at = timezone.now()  # set completed_at to current time
        elif self.status == QC_STATUS['RETURNED']:  # If status is changing to RETURNED
            self.completed_at = timezone.now()  # set completed_at to current time

        if self.pk:  # If status is changing
            try:
                old_instance = QCReview.objects.get(pk=self.pk)
                if old_instance.status != self.status:
                    # Update application status based on QC_STATUS_TO_APPLICATION_STATUS
                    new_application_status = QC_STATUS_TO_APPLICATION_STATUS.get(self.status)
                    if new_application_status:
                        self.application.status = new_application_status
                        self.application.save()
            except QCReview.DoesNotExist:
                pass

        super().save(**kwargs)  # Call parent save method with kwargs

    def assign_to(self, reviewer, assignment_type=QC_ASSIGNMENT_TYPE['MANUAL']):
        """
        Assigns the QC review to a specific reviewer
        Args:
            reviewer (User): The reviewer to assign to
            assignment_type (str): The assignment type (default to QC_ASSIGNMENT_TYPE['MANUAL'] if not provided)
        Returns:
            bool: True if assignment was successful, False otherwise
        """
        self.assigned_to = reviewer  # Set assigned_to to the specified reviewer
        self.assignment_type = assignment_type  # Set assignment_type to the specified type (default to QC_ASSIGNMENT_TYPE['MANUAL'] if not provided)
        self.assigned_at = timezone.now()  # Set assigned_at to current time
        if self.status == QC_STATUS['PENDING']:  # If currently PENDING
            self.status = QC_STATUS['IN_REVIEW']  # Set status to QC_STATUS['IN_REVIEW']
        self.save()  # Save the QC review
        return True  # Return True if assignment was successful, False otherwise

    def approve(self, reviewer, notes=None):
        """
        Approves the QC review
        Args:
            reviewer (User): The reviewer approving the QC review
            notes (str): Additional notes for the approval
        Returns:
            bool: True if approval was successful, False otherwise
        """
        if not self.is_checklist_complete():  # Validate that all checklist items are verified or waived using is_checklist_complete()
            return False
        if not self.is_document_verification_complete():  # Validate that all document verifications are complete using is_document_verification_complete()
            return False
        if not self.is_stipulation_verification_complete():  # Validate that all stipulation verifications are complete using is_stipulation_verification_complete()
            self.status = QC_STATUS['APPROVED']  # Set status to QC_STATUS['APPROVED']
            self.completed_at = timezone.now()  # Set completed_at to current time
            if notes:  # Set notes if provided
                self.notes = notes
            self.save()  # Save the QC review
            return True  # Return True if approval was successful, False otherwise
        return False

    def return_for_correction(self, reviewer, return_reason, notes=None):
        """
        Returns the QC review for correction
        Args:
            reviewer (User): The reviewer returning the QC review
            return_reason (str): The reason for returning the QC review
            notes (str): Additional notes for the return
        Returns:
            bool: True if return was successful, False otherwise
        """
        if return_reason not in QC_RETURN_REASON:  # Validate that return_reason is provided and valid
            return False
        self.status = QC_STATUS['RETURNED']  # Set status to QC_STATUS['RETURNED']
        self.return_reason = return_reason  # Set return_reason to the specified reason
        self.completed_at = timezone.now()  # Set completed_at to current time
        if notes:  # Set notes if provided
            self.notes = notes
        self.save()  # Save the QC review
        return True  # Return True if return was successful, False otherwise

    def reopen(self, user):
        """
        Reopens a returned QC review
        Args:
            user (User): The user reopening the QC review
        Returns:
            bool: True if reopening was successful, False otherwise
        """
        if self.status != QC_STATUS['RETURNED']:  # Validate that status is QC_STATUS['RETURNED']
            return False
        self.status = QC_STATUS['IN_REVIEW']  # Set status to QC_STATUS['IN_REVIEW']
        self.return_reason = None  # Set return_reason to None
        self.completed_at = None  # Set completed_at to None
        self.save()  # Save the QC review
        return True  # Return True if reopening was successful, False otherwise

    def get_checklist_items(self):
        """
        Returns all checklist items for this QC review
        Returns:
            QuerySet: QuerySet of QCChecklistItem objects
        """
        return QCChecklistItem.objects.filter(qc_review=self)  # Filter QCChecklistItem objects by this QC review

    def get_document_verifications(self):
        """
        Returns all document verifications for this QC review
        Returns:
            QuerySet: QuerySet of DocumentVerification objects
        """
        return DocumentVerification.objects.filter(qc_review=self)  # Filter DocumentVerification objects by this QC review

    def get_stipulation_verifications(self):
        """
        Returns all stipulation verifications for this QC review
        Returns:
            QuerySet: QuerySet of QCStipulationVerification objects
        """
        return QCStipulationVerification.objects.filter(qc_review=self)  # Filter QCStipulationVerification objects by this QC review

    def is_checklist_complete(self):
        """
        Checks if all checklist items are verified, rejected, or waived
        Returns:
            bool: True if all checklist items are complete, False otherwise
        """
        checklist_items = self.get_checklist_items()  # Get all checklist items for this QC review
        # Check if all items have a status of VERIFIED, REJECTED, or WAIVED
        return all(item.status in (QC_VERIFICATION_STATUS['VERIFIED'], QC_VERIFICATION_STATUS['REJECTED'], QC_VERIFICATION_STATUS['WAIVED']) for item in checklist_items)

    def is_document_verification_complete(self):
        """
        Checks if all document verifications are complete
        Returns:
            bool: True if all document verifications are complete, False otherwise
        """
        document_verifications = self.get_document_verifications()  # Get all document verifications for this QC review
        # Check if all verifications have a status of VERIFIED, REJECTED, or WAIVED
        return all(verification.status in (QC_VERIFICATION_STATUS['VERIFIED'], QC_VERIFICATION_STATUS['REJECTED'], QC_VERIFICATION_STATUS['WAIVED']) for verification in document_verifications)

    def is_stipulation_verification_complete(self):
        """
        Checks if all stipulation verifications are complete
        Returns:
            bool: True if all stipulation verifications are complete, False otherwise
        """
        stipulation_verifications = self.get_stipulation_verifications()  # Get all stipulation verifications for this QC review
        # Check if all verifications have a status of VERIFIED, REJECTED, or WAIVED
        return all(verification.status in (QC_VERIFICATION_STATUS['VERIFIED'], QC_VERIFICATION_STATUS['REJECTED'], QC_VERIFICATION_STATUS['WAIVED']) for verification in stipulation_verifications)

    def is_complete(self):
        """
        Checks if the entire QC review is complete
        Returns:
            bool: True if the QC review is complete, False otherwise
        """
        if not self.is_checklist_complete():  # Check if checklist is complete using is_checklist_complete()
            return False
        if not self.is_document_verification_complete():  # Check if document verification is complete using is_document_verification_complete()
            return False
        if not self.is_stipulation_verification_complete():  # Check if stipulation verification is complete using is_stipulation_verification_complete()
            return False
        return True  # Return True if all components are complete, False otherwise

    def get_completion_percentage(self):
        """
        Calculates the overall completion percentage of the QC review
        Returns:
            float: Percentage of completed items (0-100)
        """
        checklist_items = self.get_checklist_items()
        document_verifications = self.get_document_verifications()
        stipulation_verifications = self.get_stipulation_verifications()

        total_checklist_items = checklist_items.count()
        total_document_verifications = document_verifications.count()
        total_stipulation_verifications = stipulation_verifications.count()

        completed_checklist_items = checklist_items.filter(status=QC_VERIFICATION_STATUS['VERIFIED']).count()
        completed_document_verifications = document_verifications.filter(status=QC_VERIFICATION_STATUS['VERIFIED']).count()
        completed_stipulation_verifications = stipulation_verifications.filter(status=QC_VERIFICATION_STATUS['VERIFIED']).count()

        total_items = total_checklist_items + total_document_verifications + total_stipulation_verifications
        total_completed = completed_checklist_items + completed_document_verifications + completed_stipulation_verifications

        if total_items == 0:
            return 0.0

        return (total_completed / total_items) * 100

    def __str__(self):
        """
        String representation of the QCReview instance
        Returns:
            str: Application ID with status
        """
        return f"Application {self.application.id} - {self.status}"


class DocumentVerification(CoreModel):
    """
    Model for tracking document verification in the QC process
    """
    qc_review = models.ForeignKey(
        QCReview,
        on_delete=models.CASCADE,
        related_name='document_verifications'
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='verifications'
    )
    status = models.CharField(
        max_length=20,
        choices=QC_VERIFICATION_STATUS_CHOICES,
        default=QC_VERIFICATION_STATUS['UNVERIFIED']
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True)

    # Custom managers
    objects = ActiveManager()
    all_objects = models.Manager()

    def save(self, **kwargs):
        """
        Override save method to set initial values
        Args:
            **kwargs: Additional keyword arguments to pass to the parent save method
        Returns:
            None: No return value
        """
        if not self.pk:  # If this is a new verification (no ID)
            if not self.status:
                self.status = QC_VERIFICATION_STATUS['UNVERIFIED']  # set status to QC_VERIFICATION_STATUS['UNVERIFIED'] if not provided
        super().save(**kwargs)  # Call parent save method with kwargs

    def verify(self, user, comments=None):
        """
        Marks the document as verified
        Args:
            user (User): The user verifying the document
            comments (str): Additional comments for the verification
        Returns:
            bool: True if verification was successful, False otherwise
        """
        self.status = QC_VERIFICATION_STATUS['VERIFIED']  # Set status to QC_VERIFICATION_STATUS['VERIFIED']
        self.verified_by = user  # Set verified_by to user
        self.verified_at = timezone.now()  # Set verified_at to current time
        if comments:  # Set comments if provided
            self.comments = comments
        self.save()  # Save the document verification
        return True  # Return True if verification was successful, False otherwise

    def reject(self, user, comments=None):
        """
        Marks the document verification as rejected
        Args:
            user (User): The user rejecting the document verification
            comments (str): Additional comments for the rejection
        Returns:
            bool: True if rejection was successful, False otherwise
        """
        self.status = QC_VERIFICATION_STATUS['REJECTED']  # Set status to QC_VERIFICATION_STATUS['REJECTED']
        self.verified_by = user  # Set verified_by to user
        self.verified_at = timezone.now()  # Set verified_at to current time
        if comments:  # Set comments if provided
            self.comments = comments
        self.save()  # Save the document verification
        return True  # Return True if rejection was successful, False otherwise

    def waive(self, user, comments=None):
        """
        Marks the document verification as waived
        Args:
            user (User): The user waiving the document verification
            comments (str): Additional comments for the waiver
        Returns:
            bool: True if waiver was successful, False otherwise
        """
        self.status = QC_VERIFICATION_STATUS['WAIVED']  # Set status to QC_VERIFICATION_STATUS['WAIVED']
        self.verified_by = user  # Set verified_by to user
        self.verified_at = timezone.now()  # Set verified_at to current time
        if comments:  # Set comments if provided
            self.comments = comments
        self.save()  # Save the document verification
        return True  # Return True if waiver was successful, False otherwise

    def is_verified(self):
        """
        Checks if the document has been verified
        Returns:
            bool: True if verified, False otherwise
        """
        return self.status == QC_VERIFICATION_STATUS['VERIFIED']  # Check if status is QC_VERIFICATION_STATUS['VERIFIED']

    def is_rejected(self):
        """
        Checks if the document verification has been rejected
        Returns:
            bool: True if rejected, False otherwise
        """
        return self.status == QC_VERIFICATION_STATUS['REJECTED']  # Check if status is QC_VERIFICATION_STATUS['REJECTED']

    def is_waived(self):
        """
        Checks if the document verification has been waived
        Returns:
            bool: True if waived, False otherwise
        """
        return self.status == QC_VERIFICATION_STATUS['WAIVED']  # Check if status is QC_VERIFICATION_STATUS['WAIVED']

    def __str__(self):
        """
        String representation of the DocumentVerification instance
        Returns:
            str: Document type with status
        """
        return f"{self.document.get_document_type_display()} - {self.status}"


class QCStipulationVerification(CoreModel):
    """
    Model for tracking stipulation verification in the QC process
    """
    qc_review = models.ForeignKey(
        QCReview,
        on_delete=models.CASCADE,
        related_name='stipulation_verifications'
    )
    stipulation = models.ForeignKey(
        Stipulation,
        on_delete=models.CASCADE,
        related_name='verifications'
    )
    status = models.CharField(
        max_length=20,
        choices=QC_VERIFICATION_STATUS_CHOICES,
        default=QC_VERIFICATION_STATUS['UNVERIFIED']
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_stipulations'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True)

    # Custom managers
    objects = ActiveManager()
    all_objects = models.Manager()

    def save(self, **kwargs):
        """
        Override save method to set initial values
        Args:
            **kwargs: Additional keyword arguments to pass to the parent save method
        Returns:
            None: No return value
        """
        if not self.pk:  # If this is a new verification (no ID)
            if not self.status:
                self.status = QC_VERIFICATION_STATUS['UNVERIFIED']  # set status to QC_VERIFICATION_STATUS['UNVERIFIED'] if not provided
        super().save(**kwargs)  # Call parent save method with kwargs

    def verify(self, user, comments=None):
        """
        Marks the stipulation as verified
        Args:
            user (User): The user verifying the stipulation
            comments (str): Additional comments for the verification
        Returns:
            bool: True if verification was successful, False otherwise
        """
        self.status = QC_VERIFICATION_STATUS['VERIFIED']  # Set status to QC_VERIFICATION_STATUS['VERIFIED']
        self.verified_by = user  # Set verified_by to user
        self.verified_at = timezone.now()  # Set verified_at to current time
        if comments:  # Set comments if provided
            self.comments = comments
        self.save()  # Save the stipulation verification
        return True  # Return True if verification was successful, False otherwise

    def reject(self, user, comments=None):
        """
        Marks the stipulation verification as rejected
        Args:
            user (User): The user rejecting the stipulation verification
            comments (str): Additional comments for the rejection
        Returns:
            bool: True if rejection was successful, False otherwise
        """
        self.status = QC_VERIFICATION_STATUS['REJECTED']  # Set status to QC_VERIFICATION_STATUS['REJECTED']
        self.verified_by = user  # Set verified_by to user
        self.verified_at = timezone.now()  # Set verified_at to current time
        if comments:  # Set comments if provided
            self.comments = comments
        self.save()  # Save the stipulation verification
        return True  # Return True if rejection was successful, False otherwise

    def waive(self, user, comments=None):
        """
        Marks the stipulation verification as waived
        Args:
            user (User): The user waiving the stipulation verification
            comments (str): Additional comments for the waiver
        Returns:
            bool: True if waiver was successful, False otherwise
        """
        self.status = QC_VERIFICATION_STATUS['WAIVED']  # Set status to QC_VERIFICATION_STATUS['WAIVED']
        self.verified_by = user  # Set verified_by to user
        self.verified_at = timezone.now()  # Set verified_at to current time
        if comments:  # Set comments if provided
            self.comments = comments
        self.save()  # Save the stipulation verification
        return True  # Return True if waiver was successful, False otherwise

    def is_verified(self):
        """
        Checks if the stipulation has been verified
        Returns:
            bool: True if verified, False otherwise
        """
        return self.status == QC_VERIFICATION_STATUS['VERIFIED']  # Check if status is QC_VERIFICATION_STATUS['VERIFIED']

    def is_rejected(self):
        """
        Checks if the stipulation verification has been rejected
        Returns:
            bool: True if rejected, False otherwise
        """
        return self.status == QC_VERIFICATION_STATUS['REJECTED']  # Check if status is QC_VERIFICATION_STATUS['REJECTED']

    def is_waived(self):
        """
        Checks if the stipulation verification has been waived
        Returns:
            bool: True if waived, False otherwise
        """
        return self.status == QC_VERIFICATION_STATUS['WAIVED']  # Check if status is QC_VERIFICATION_STATUS['WAIVED']

    def __str__(self):
        """
        String representation of the QCStipulationVerification instance
        Returns:
            str: Stipulation description with status
        """
        return f"{self.stipulation.description} - {self.status}"


class QCChecklistItem(CoreModel):
    """
    Model representing an item in the QC checklist
    """
    qc_review = models.ForeignKey(
        QCReview,
        on_delete=models.CASCADE,
        related_name='checklist_items'
    )
    category = models.CharField(
        max_length=50,
        choices=QC_CHECKLIST_CATEGORY_CHOICES
    )
    item_text = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=QC_VERIFICATION_STATUS_CHOICES,
        default=QC_VERIFICATION_STATUS['UNVERIFIED']
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_checklist_items'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True)

    # Custom managers
    objects = ActiveManager()
    all_objects = models.Manager()

    def save(self, **kwargs):
        """
        Override save method to set initial values
        Args:
            **kwargs: Additional keyword arguments to pass to the parent save method
        Returns:
            None: No return value
        """
        if not self.pk:  # If this is a new checklist item (no ID)
            if not self.status:
                self.status = QC_VERIFICATION_STATUS['UNVERIFIED']  # set status to QC_VERIFICATION_STATUS['UNVERIFIED'] if not provided
        super().save(**kwargs)  # Call parent save method with kwargs

    def verify(self, user, comments=None):
        """
        Marks the checklist item as verified
        Args:
            user (User): The user verifying the checklist item
            comments (str): Additional comments for the verification
        Returns:
            bool: True if verification was successful, False otherwise
        """
        self.status = QC_VERIFICATION_STATUS['VERIFIED']  # Set status to QC_VERIFICATION_STATUS['VERIFIED']
        self.verified_by = user  # Set verified_by to user
        self.verified_at = timezone.now()  # Set verified_at to current time
        if comments:  # Set comments if provided
            self.comments = comments
        self.save()  # Save the checklist item
        return True  # Return True if verification was successful, False otherwise

    def reject(self, user, comments=None):
        """
        Marks the checklist item as rejected
        Args:
            user (User): The user rejecting the checklist item
            comments (str): Additional comments for the rejection
        Returns:
            bool: True if rejection was successful, False otherwise
        """
        self.status = QC_VERIFICATION_STATUS['REJECTED']  # Set status to QC_VERIFICATION_STATUS['REJECTED']
        self.verified_by = user  # Set verified_by to user
        self.verified_at = timezone.now()  # Set verified_at to current time
        if comments:  # Set comments if provided
            self.comments = comments
        self.save()  # Save the checklist item
        return True  # Return True if rejection was successful, False otherwise

    def waive(self, user, comments=None):
        """
        Marks the checklist item as waived
        Args:
            user (User): The user waiving the checklist item
            comments (str): Additional comments for the waiver
        Returns:
            bool: True if waiver was successful, False otherwise
        """
        self.status = QC_VERIFICATION_STATUS['WAIVED']  # Set status to QC_VERIFICATION_STATUS['WAIVED']
        self.verified_by = user  # Set verified_by to user
        self.verified_at = timezone.now()  # Set verified_at to current time
        if comments:  # Set comments if provided
            self.comments = comments
        self.save()  # Save the checklist item
        return True  # Return True if waiver was successful, False otherwise

    def is_verified(self):
        """
        Checks if the checklist item has been verified
        Returns:
            bool: True if verified, False otherwise
        """
        return self.status == QC_VERIFICATION_STATUS['VERIFIED']  # Check if status is QC_VERIFICATION_STATUS['VERIFIED']

    def is_rejected(self):
        """
        Checks if the checklist item has been rejected
        Returns:
            bool: True if rejected, False otherwise
        """
        return self.status == QC_VERIFICATION_STATUS['REJECTED']  # Check if status is QC_VERIFICATION_STATUS['REJECTED']

    def is_waived(self):
        """
        Checks if the checklist item has been waived
        Returns:
            bool: True if waived, False otherwise
        """
        return self.status == QC_VERIFICATION_STATUS['WAIVED']  # Check if status is QC_VERIFICATION_STATUS['WAIVED']

    def __str__(self):
        """
        String representation of the QCChecklistItem instance
        Returns:
            str: Item text with status
        """
        return f"{self.item_text} - {self.status}"