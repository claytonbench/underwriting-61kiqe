"""
Defines the data models for loan applications in the loan management system.

This module implements the core data models for the loan application process, including
the primary LoanApplication model, financial details, document management, status history,
and application notes.
"""

from django.db import models  # Django 4.2+
from django.utils import timezone  # Django 4.2+
from decimal import Decimal  # standard library
from django.core.exceptions import ValidationError  # Django 4.2+

from core.models import CoreModel, ActiveManager
from apps.users.models import User, BorrowerProfile
from apps.schools.models import School, Program, ProgramVersion
from utils.constants import APPLICATION_STATUS, DOCUMENT_TYPES
from apps.applications.constants import (
    APPLICATION_TYPES, RELATIONSHIP_TYPES, 
    APPLICATION_EDITABLE_STATUSES
)
from apps.applications.validators import (
    validate_application_editable,
    validate_application_submission
)

# Define choice tuples for model fields
APPLICATION_TYPE_CHOICES = ([(APPLICATION_TYPES['STANDARD'], 'Standard'), 
                            (APPLICATION_TYPES['REFINANCE'], 'Refinance'), 
                            (APPLICATION_TYPES['COSIGNED'], 'Co-signed')])

RELATIONSHIP_TYPE_CHOICES = ([(RELATIONSHIP_TYPES['SPOUSE'], 'Spouse'), 
                             (RELATIONSHIP_TYPES['PARENT'], 'Parent'), 
                             (RELATIONSHIP_TYPES['SIBLING'], 'Sibling'), 
                             (RELATIONSHIP_TYPES['RELATIVE'], 'Relative'), 
                             (RELATIONSHIP_TYPES['FRIEND'], 'Friend'), 
                             (RELATIONSHIP_TYPES['OTHER'], 'Other')])

APPLICATION_STATUS_CHOICES = ([status for status in APPLICATION_STATUS.items()])

DOCUMENT_TYPE_CHOICES = ([doc_type for doc_type in DOCUMENT_TYPES.items()])


class ApplicationManager(ActiveManager):
    """
    Custom manager for LoanApplication model to provide additional query methods.
    """
    
    def get_by_status(self, status):
        """
        Returns applications filtered by status.
        
        Args:
            status (str): The status to filter by
            
        Returns:
            QuerySet: Applications with the specified status
        """
        return self.get_queryset().filter(status=status)
    
    def get_by_borrower(self, borrower):
        """
        Returns applications for a specific borrower.
        
        Args:
            borrower (User): The borrower to filter by
            
        Returns:
            QuerySet: Applications for the specified borrower
        """
        return self.get_queryset().filter(borrower=borrower)
    
    def get_by_school(self, school):
        """
        Returns applications for a specific school.
        
        Args:
            school (School): The school to filter by
            
        Returns:
            QuerySet: Applications for the specified school
        """
        return self.get_queryset().filter(school=school)
    
    def get_for_underwriting(self):
        """
        Returns applications ready for underwriting review.
        
        Returns:
            QuerySet: Applications in reviewable statuses
        """
        from apps.applications.constants import APPLICATION_REVIEWABLE_STATUSES
        return self.get_queryset().filter(status__in=APPLICATION_REVIEWABLE_STATUSES)


class LoanApplication(CoreModel):
    """
    Core model representing a loan application in the system.
    
    This model stores the central application information and provides relationships
    to borrowers, schools, programs, and all related application entities.
    """
    borrower = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="applications_as_borrower"
    )
    co_borrower = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="applications_as_co_borrower",
        null=True,
        blank=True
    )
    school = models.ForeignKey(
        School,
        on_delete=models.PROTECT,
        related_name="applications"
    )
    program = models.ForeignKey(
        Program,
        on_delete=models.PROTECT,
        related_name="applications"
    )
    program_version = models.ForeignKey(
        ProgramVersion,
        on_delete=models.PROTECT,
        related_name="applications"
    )
    application_type = models.CharField(
        max_length=20,
        choices=APPLICATION_TYPE_CHOICES,
        default=APPLICATION_TYPES['STANDARD']
    )
    status = models.CharField(
        max_length=30,
        choices=APPLICATION_STATUS_CHOICES,
        default=APPLICATION_STATUS['DRAFT']
    )
    relationship_type = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_TYPE_CHOICES,
        null=True,
        blank=True
    )
    submission_date = models.DateTimeField(null=True, blank=True)
    
    # Custom managers
    objects = ApplicationManager()
    all_objects = models.Manager()
    
    def clean(self):
        """
        Validates the application data before saving.
        
        Raises:
            ValidationError: If application data is invalid
        """
        super().clean()
        
        # Validate relationship_type is provided if co_borrower is present
        if self.co_borrower and not self.relationship_type:
            raise ValidationError("Relationship type is required when a co-borrower is specified.")
        
        # Validate program_version belongs to the selected program
        if self.program and self.program_version and self.program_version.program != self.program:
            raise ValidationError("The program version must belong to the selected program.")
    
    def save(self, **kwargs):
        """
        Override save method to handle application-specific logic.
        
        Args:
            **kwargs: Additional arguments passed to parent save method
        """
        # Set status to DRAFT for new applications
        if not self.pk:
            self.status = APPLICATION_STATUS['DRAFT']
        
        # Create status history record if status is changing
        if self.pk:
            try:
                old_instance = LoanApplication.objects.get(pk=self.pk)
                if old_instance.status != self.status:
                    ApplicationStatusHistory.objects.create(
                        application=self,
                        previous_status=old_instance.status,
                        new_status=self.status,
                        changed_by=kwargs.get('user', self.updated_by),
                        comments=kwargs.pop('status_comment', '')
                    )
                    
                    # Set submission_date when status changes to SUBMITTED
                    if self.status == APPLICATION_STATUS['SUBMITTED'] and not self.submission_date:
                        self.submission_date = timezone.now()
            except LoanApplication.DoesNotExist:
                pass
        
        super().save(**kwargs)
    
    def submit(self):
        """
        Submits the application for review.
        
        Returns:
            bool: True if submission was successful, False otherwise
        """
        try:
            # Validate application is in an editable state
            validate_application_editable(self)
            
            # Get the loan details and borrower profile for validation
            loan_details = self.get_loan_details()
            borrower_profile = BorrowerProfile.objects.get(user=self.borrower)
            
            # Validate the application data
            validate_application_submission(self, borrower_profile, loan_details)
            
            # Update status and save
            self.status = APPLICATION_STATUS['SUBMITTED']
            self.save(status_comment='Application submitted by borrower')
            return True
        except ValidationError:
            return False
    
    def is_editable(self):
        """
        Checks if the application is in an editable state.
        
        Returns:
            bool: True if application can be edited, False otherwise
        """
        return self.status in APPLICATION_EDITABLE_STATUSES
    
    def get_loan_details(self):
        """
        Returns the associated loan details.
        
        Returns:
            LoanDetails: The associated loan details object or None if not found
        """
        try:
            return LoanDetails.objects.get(application=self)
        except LoanDetails.DoesNotExist:
            return None
    
    def get_documents(self):
        """
        Returns all documents associated with this application.
        
        Returns:
            QuerySet: All documents for this application
        """
        return ApplicationDocument.objects.filter(application=self)
    
    def get_status_history(self):
        """
        Returns the status history for this application.
        
        Returns:
            QuerySet: Status history records ordered by most recent first
        """
        return ApplicationStatusHistory.objects.filter(application=self).order_by('-changed_at')
    
    def get_underwriting_decision(self):
        """
        Returns the underwriting decision for this application.
        
        Returns:
            UnderwritingDecision: The decision object or None if not found
        """
        try:
            # This will be implemented in the underwriting app
            from apps.underwriting.models import UnderwritingDecision
            return UnderwritingDecision.objects.get(application=self)
        except ImportError:
            # If underwriting app is not available yet
            return None
        except:
            return None
    
    def get_funding_request(self):
        """
        Returns the funding request for this application.
        
        Returns:
            FundingRequest: The funding request object or None if not found
        """
        try:
            # This will be implemented in the funding app
            from apps.funding.models import FundingRequest
            return FundingRequest.objects.get(application=self)
        except ImportError:
            # If funding app is not available yet
            return None
        except:
            return None
    
    def __str__(self):
        """
        String representation of the LoanApplication instance.
        
        Returns:
            str: Application ID and borrower name
        """
        return f"Application {self.id} - {self.borrower.first_name} {self.borrower.last_name}"


class LoanDetails(CoreModel):
    """
    Model storing financial details for a loan application.
    
    This model contains all the financial information related to a loan application,
    including tuition amount, deposit, funding, and requested/approved amounts.
    """
    application = models.OneToOneField(
        LoanApplication,
        on_delete=models.CASCADE,
        related_name="loan_details"
    )
    tuition_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    deposit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    other_funding = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    requested_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    approved_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    start_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    
    # Custom managers
    objects = ActiveManager()
    all_objects = models.Manager()
    
    def clean(self):
        """
        Validates the loan details before saving.
        
        Raises:
            ValidationError: If loan details are invalid
        """
        super().clean()
        
        # Validate tuition_amount is positive
        if self.tuition_amount <= Decimal('0'):
            raise ValidationError("Tuition amount must be positive.")
        
        # Validate deposit_amount is non-negative
        if self.deposit_amount < Decimal('0'):
            raise ValidationError("Deposit amount cannot be negative.")
        
        # Validate other_funding is non-negative
        if self.other_funding < Decimal('0'):
            raise ValidationError("Other funding amount cannot be negative.")
        
        # Validate requested_amount is positive
        if self.requested_amount <= Decimal('0'):
            raise ValidationError("Requested loan amount must be positive.")
        
        # Validate requested amount does not exceed net tuition
        if self.requested_amount > self.get_net_tuition():
            raise ValidationError("Requested amount cannot exceed tuition minus deposit and other funding.")
        
        # Validate start_date is in the future
        today = timezone.now().date()
        if self.start_date and self.start_date < today:
            raise ValidationError("Start date must be in the future.")
        
        # Validate completion_date is after start_date
        if self.completion_date and self.start_date and self.completion_date <= self.start_date:
            raise ValidationError("Completion date must be after start date.")
    
    def get_net_tuition(self):
        """
        Calculates the net tuition after deposit and other funding.
        
        Returns:
            Decimal: Net tuition amount
        """
        return self.tuition_amount - self.deposit_amount - self.other_funding
    
    def get_program_duration_weeks(self):
        """
        Returns the program duration in weeks.
        
        Returns:
            int: Program duration in weeks
        """
        if self.application and self.application.program:
            return self.application.program.duration_weeks
        return None
    
    def __str__(self):
        """
        String representation of the LoanDetails instance.
        
        Returns:
            str: Application ID and requested amount
        """
        return f"Application {self.application.id} - ${self.requested_amount}"


class ApplicationDocument(CoreModel):
    """
    Model representing a document uploaded for a loan application.
    
    This model tracks documents uploaded as part of the loan application process,
    including their type, storage location, and verification status.
    """
    application = models.ForeignKey(
        LoanApplication,
        on_delete=models.CASCADE,
        related_name="documents"
    )
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES
    )
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(default=timezone.now)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_documents"
    )
    status = models.CharField(
        max_length=20,
        default="pending",
        choices=[
            ("pending", "Pending Review"),
            ("verified", "Verified"),
            ("rejected", "Rejected")
        ]
    )
    
    # Custom managers
    objects = ActiveManager()
    all_objects = models.Manager()
    
    def get_download_url(self, expiry_seconds=3600):
        """
        Generates a download URL for the document.
        
        Args:
            expiry_seconds (int): Expiry time for the URL in seconds
            
        Returns:
            str: Presigned URL for downloading the document
        """
        from utils.storage import get_presigned_url
        return get_presigned_url(self.file_path, expiry_seconds)
    
    def is_verified(self):
        """
        Checks if the document has been verified.
        
        Returns:
            bool: True if document is verified, False otherwise
        """
        return self.status == "verified"
    
    def verify(self, verified_by):
        """
        Marks the document as verified.
        
        Args:
            verified_by (User): User who verified the document
        """
        self.status = "verified"
        self.save(user=verified_by)
    
    def __str__(self):
        """
        String representation of the ApplicationDocument instance.
        
        Returns:
            str: Document type and application ID
        """
        return f"{self.get_document_type_display()} - Application {self.application.id}"


class ApplicationStatusHistory(CoreModel):
    """
    Model tracking status changes for loan applications.
    
    This model maintains a complete history of all status changes for an application,
    including when the change occurred and who made the change.
    """
    application = models.ForeignKey(
        LoanApplication,
        on_delete=models.CASCADE,
        related_name="status_history"
    )
    previous_status = models.CharField(
        max_length=30,
        choices=APPLICATION_STATUS_CHOICES
    )
    new_status = models.CharField(
        max_length=30,
        choices=APPLICATION_STATUS_CHOICES
    )
    changed_at = models.DateTimeField(default=timezone.now)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="application_status_changes"
    )
    comments = models.TextField(blank=True, null=True)
    
    # Custom managers
    objects = ActiveManager()
    all_objects = models.Manager()
    
    def save(self, **kwargs):
        """
        Override save method to set changed_at if not provided.
        
        Args:
            **kwargs: Additional arguments passed to parent save method
        """
        if not self.changed_at:
            self.changed_at = timezone.now()
        super().save(**kwargs)
    
    def __str__(self):
        """
        String representation of the ApplicationStatusHistory instance.
        
        Returns:
            str: Status change description
        """
        return f"Application {self.application.id}: {self.previous_status} → {self.new_status}"


class ApplicationNote(CoreModel):
    """
    Model for storing notes related to loan applications.
    
    This model allows users to add notes to applications, which can be used for
    internal communication, decision justification, or tracking important information.
    """
    application = models.ForeignKey(
        LoanApplication,
        on_delete=models.CASCADE,
        related_name="notes"
    )
    note_text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="application_notes"
    )
    is_internal = models.BooleanField(
        default=True,
        help_text="If true, note is only visible to internal staff"
    )
    
    # Custom managers
    objects = ActiveManager()
    all_objects = models.Manager()
    
    def save(self, **kwargs):
        """
        Override save method to set created_at if not provided.
        
        Args:
            **kwargs: Additional arguments passed to parent save method
        """
        if not self.created_at:
            self.created_at = timezone.now()
        super().save(**kwargs)
    
    def __str__(self):
        """
        String representation of the ApplicationNote instance.
        
        Returns:
            str: Note preview with application ID
        """
        preview = self.note_text[:50] + "..." if len(self.note_text) > 50 else self.note_text
        return f"Application {self.application.id}: {preview}"