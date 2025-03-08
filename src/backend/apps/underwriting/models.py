"""
Defines the data models for the loan underwriting process in the loan management system.

This module implements the models that support the underwriting workflow, including
queue management, credit information tracking, decision recording, and stipulation
management for loan applications.
"""

from django.db import models  # Django 4.2+
from django.utils import timezone  # Django 4.2+
from decimal import Decimal  # standard library

from core.models import CoreModel, ActiveManager
from apps.applications.models import LoanApplication
from apps.users.models import User
from .constants import (
    UNDERWRITING_QUEUE_PRIORITY, UNDERWRITING_QUEUE_STATUS,
    UNDERWRITING_QUEUE_SLA_HOURS, CREDIT_SCORE_TIERS,
    DECISION_REASON_CODES, DECISION_REASON_DESCRIPTIONS,
    UNDERWRITING_DECISION_TRANSITIONS
)
from utils.constants import (
    UNDERWRITING_DECISION, STIPULATION_TYPES, STIPULATION_STATUS
)

# Choice tuples for model fields
UNDERWRITING_QUEUE_PRIORITY_CHOICES = ([
    (UNDERWRITING_QUEUE_PRIORITY['HIGH'], 'High'),
    (UNDERWRITING_QUEUE_PRIORITY['MEDIUM'], 'Medium'),
    (UNDERWRITING_QUEUE_PRIORITY['LOW'], 'Low')
])

UNDERWRITING_QUEUE_STATUS_CHOICES = ([
    (UNDERWRITING_QUEUE_STATUS['PENDING'], 'Pending'),
    (UNDERWRITING_QUEUE_STATUS['ASSIGNED'], 'Assigned'),
    (UNDERWRITING_QUEUE_STATUS['IN_PROGRESS'], 'In Progress'),
    (UNDERWRITING_QUEUE_STATUS['COMPLETED'], 'Completed'),
    (UNDERWRITING_QUEUE_STATUS['RETURNED'], 'Returned')
])

UNDERWRITING_DECISION_CHOICES = ([
    (UNDERWRITING_DECISION['APPROVE'], 'Approve'),
    (UNDERWRITING_DECISION['DENY'], 'Deny'),
    (UNDERWRITING_DECISION['REVISE'], 'Request Revision')
])

DECISION_REASON_CHOICES = ([reason for reason in DECISION_REASON_CODES.items()])
STIPULATION_TYPE_CHOICES = ([stipulation for stipulation in STIPULATION_TYPES.items()])
STIPULATION_STATUS_CHOICES = ([status for status in STIPULATION_STATUS.items()])


class UnderwritingQueueManager(ActiveManager):
    """
    Custom manager for UnderwritingQueue model to provide additional query methods.
    Extends the ActiveManager to filter out soft-deleted records.
    """
    
    def get_by_status(self, status):
        """
        Returns queue items filtered by status.
        
        Args:
            status (str): The status to filter by
            
        Returns:
            QuerySet: QuerySet of UnderwritingQueue objects with the specified status
        """
        return self.get_queryset().filter(status=status)
    
    def get_by_underwriter(self, underwriter):
        """
        Returns queue items assigned to a specific underwriter.
        
        Args:
            underwriter (User): The underwriter to filter by
            
        Returns:
            QuerySet: QuerySet of UnderwritingQueue objects assigned to the specified underwriter
        """
        return self.get_queryset().filter(assigned_to=underwriter)
    
    def get_pending(self):
        """
        Returns queue items with pending status.
        
        Returns:
            QuerySet: QuerySet of UnderwritingQueue objects with pending status
        """
        return self.get_queryset().filter(status=UNDERWRITING_QUEUE_STATUS['PENDING'])
    
    def get_by_priority(self, priority):
        """
        Returns queue items filtered by priority.
        
        Args:
            priority (str): The priority to filter by
            
        Returns:
            QuerySet: QuerySet of UnderwritingQueue objects with the specified priority
        """
        return self.get_queryset().filter(priority=priority)
    
    def get_overdue(self):
        """
        Returns queue items that are past their due date.
        
        Returns:
            QuerySet: QuerySet of UnderwritingQueue objects past their due date
        """
        now = timezone.now()
        return self.get_queryset().filter(
            due_date__lt=now,
            status__in=[
                UNDERWRITING_QUEUE_STATUS['PENDING'],
                UNDERWRITING_QUEUE_STATUS['ASSIGNED'],
                UNDERWRITING_QUEUE_STATUS['IN_PROGRESS']
            ]
        )


class UnderwritingQueue(CoreModel):
    """
    Model representing an application in the underwriting queue.
    
    This model tracks applications as they move through the underwriting process,
    including assignment to underwriters, priority, status, and SLA timing.
    """
    application = models.ForeignKey(
        LoanApplication, 
        on_delete=models.CASCADE,
        related_name='underwriting_queue_entries'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_applications'
    )
    assignment_date = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(
        max_length=20,
        choices=UNDERWRITING_QUEUE_PRIORITY_CHOICES,
        default=UNDERWRITING_QUEUE_PRIORITY['MEDIUM']
    )
    status = models.CharField(
        max_length=20,
        choices=UNDERWRITING_QUEUE_STATUS_CHOICES,
        default=UNDERWRITING_QUEUE_STATUS['PENDING']
    )
    due_date = models.DateTimeField(null=True, blank=True)
    
    # Custom managers
    objects = UnderwritingQueueManager()
    all_objects = models.Manager()
    
    def save(self, **kwargs):
        """
        Override save method to handle queue-specific logic.
        
        Sets default status for new entries, calculates due date based on priority,
        and updates assignment_date when an underwriter is assigned.
        
        Args:
            **kwargs: Additional arguments to pass to parent save method
        """
        # For new entries, set default status if not provided
        if not self.pk and not self.status:
            self.status = UNDERWRITING_QUEUE_STATUS['PENDING']
        
        # If assigned_to is set but assignment_date isn't, set assignment_date
        if self.assigned_to and not self.assignment_date:
            self.assignment_date = timezone.now()
        
        # Calculate due date based on priority if not set
        if not self.due_date:
            # Get SLA hours based on priority
            sla_hours = UNDERWRITING_QUEUE_SLA_HOURS.get(
                self.priority, 
                UNDERWRITING_QUEUE_SLA_HOURS['MEDIUM']
            )
            self.due_date = timezone.now() + timezone.timedelta(hours=sla_hours)
        
        super().save(**kwargs)
    
    def assign(self, underwriter):
        """
        Assigns the queue item to an underwriter.
        
        Args:
            underwriter (User): The underwriter to assign to
            
        Returns:
            bool: True if assignment successful, False otherwise
        """
        if not underwriter:
            return False
        
        self.assigned_to = underwriter
        self.assignment_date = timezone.now()
        self.status = UNDERWRITING_QUEUE_STATUS['ASSIGNED']
        self.save()
        return True
    
    def start_review(self):
        """
        Marks the queue item as in progress.
        
        Returns:
            bool: True if status update successful, False otherwise
        """
        if not self.assigned_to:
            return False
        
        self.status = UNDERWRITING_QUEUE_STATUS['IN_PROGRESS']
        self.save()
        return True
    
    def complete(self):
        """
        Marks the queue item as completed.
        
        Returns:
            bool: True if status update successful, False otherwise
        """
        if self.status != UNDERWRITING_QUEUE_STATUS['IN_PROGRESS']:
            return False
        
        self.status = UNDERWRITING_QUEUE_STATUS['COMPLETED']
        self.save()
        return True
    
    def return_to_queue(self):
        """
        Returns the queue item to the pending queue.
        
        Returns:
            bool: True if status update successful, False otherwise
        """
        self.status = UNDERWRITING_QUEUE_STATUS['RETURNED']
        self.assigned_to = None
        self.assignment_date = None
        self.save()
        return True
    
    def is_overdue(self):
        """
        Checks if the queue item is past its due date.
        
        Returns:
            bool: True if overdue, False otherwise
        """
        if not self.due_date:
            return False
        
        return (
            self.due_date < timezone.now() and 
            self.status != UNDERWRITING_QUEUE_STATUS['COMPLETED']
        )
    
    def __str__(self):
        """
        String representation of the UnderwritingQueue instance.
        
        Returns:
            str: Application ID with status and priority
        """
        return f"Application {self.application.id} - {self.status} (Priority: {self.priority})"


class CreditInformation(CoreModel):
    """
    Model for storing credit report information for borrowers and co-borrowers.
    
    This model contains credit scores, report references, and financial metrics used
    during the underwriting decision process.
    """
    application = models.ForeignKey(
        LoanApplication,
        on_delete=models.CASCADE,
        related_name='credit_information'
    )
    borrower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='credit_reports'
    )
    is_co_borrower = models.BooleanField(default=False)
    credit_score = models.IntegerField()
    report_date = models.DateTimeField(default=timezone.now)
    report_reference = models.CharField(max_length=100)
    file_path = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_credit_reports'
    )
    uploaded_at = models.DateTimeField(default=timezone.now)
    monthly_debt = models.DecimalField(max_digits=10, decimal_places=2)
    debt_to_income_ratio = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Custom managers
    objects = ActiveManager()
    all_objects = models.Manager()
    
    def save(self, **kwargs):
        """
        Override save method to set uploaded_at and report_date if not provided.
        
        Args:
            **kwargs: Additional arguments to pass to parent save method
        """
        if not self.uploaded_at:
            self.uploaded_at = timezone.now()
            
        if not self.report_date:
            self.report_date = timezone.now()
            
        super().save(**kwargs)
    
    def get_credit_tier(self):
        """
        Determines the credit tier based on credit score.
        
        Returns:
            str: Credit tier (EXCELLENT, GOOD, FAIR, POOR, or BAD)
        """
        score = self.credit_score
        
        if score >= CREDIT_SCORE_TIERS['EXCELLENT']:
            return 'EXCELLENT'
        elif score >= CREDIT_SCORE_TIERS['GOOD']:
            return 'GOOD'
        elif score >= CREDIT_SCORE_TIERS['FAIR']:
            return 'FAIR'
        elif score >= CREDIT_SCORE_TIERS['POOR']:
            return 'POOR'
        elif score >= CREDIT_SCORE_TIERS['BAD']:
            return 'BAD'
        else:
            return 'BAD'  # Anything below the BAD threshold is still BAD
    
    def calculate_dti(self, monthly_income):
        """
        Calculates debt-to-income ratio based on monthly debt and income.
        
        Args:
            monthly_income (Decimal): Monthly income amount
            
        Returns:
            Decimal: Debt-to-income ratio
        """
        if not monthly_income or monthly_income <= Decimal('0'):
            return Decimal('0')
            
        return self.monthly_debt / monthly_income
    
    def get_download_url(self, expiry_seconds=3600):
        """
        Generates a download URL for the credit report file.
        
        Args:
            expiry_seconds (int): URL expiration time in seconds
            
        Returns:
            str: Presigned URL for downloading the credit report
        """
        from utils.storage import get_presigned_url
        return get_presigned_url(self.file_path, expiry_seconds)
    
    def __str__(self):
        """
        String representation of the CreditInformation instance.
        
        Returns:
            str: Borrower name with credit score
        """
        borrower_type = "Co-borrower" if self.is_co_borrower else "Borrower"
        return f"{borrower_type} {self.borrower.first_name} {self.borrower.last_name} - Score: {self.credit_score}"


class UnderwritingDecision(CoreModel):
    """
    Model for recording underwriting decisions for loan applications.
    
    This model captures the approval/denial/revision decision along with relevant
    terms and conditions for approved loans.
    """
    application = models.OneToOneField(
        LoanApplication,
        on_delete=models.CASCADE,
        related_name='underwriting_decision'
    )
    decision = models.CharField(
        max_length=20,
        choices=UNDERWRITING_DECISION_CHOICES
    )
    decision_date = models.DateTimeField(default=timezone.now)
    underwriter = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='underwriting_decisions'
    )
    comments = models.TextField(blank=True)
    approved_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    term_months = models.IntegerField(null=True, blank=True)
    
    # Custom managers
    objects = ActiveManager()
    all_objects = models.Manager()
    
    def save(self, **kwargs):
        """
        Override save method to handle decision-specific logic.
        
        Sets decision_date if not provided and updates application status
        based on the decision.
        
        Args:
            **kwargs: Additional arguments to pass to parent save method
        """
        # Set decision date if not provided
        if not self.decision_date:
            self.decision_date = timezone.now()
            
        # Update application status if this is a new decision
        is_new = not self.pk
        
        # Save first to ensure we have a valid record
        super().save(**kwargs)
        
        # Update application status if this is a new decision
        if is_new:
            self.update_application_status()
    
    def update_application_status(self):
        """
        Updates the application status based on the underwriting decision.
        
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            # Get the application
            application = self.application
            
            # Determine new status based on decision
            new_status = APPLICATION_STATUS[UNDERWRITING_DECISION_TRANSITIONS[self.decision]]
            
            # Update application status
            application.status = new_status
            application.save()
            
            return True
        except Exception:
            return False
    
    def get_reasons(self):
        """
        Returns the decision reasons associated with this decision.
        
        Returns:
            QuerySet: QuerySet of DecisionReason objects
        """
        return DecisionReason.objects.filter(decision=self)
    
    def get_stipulations(self):
        """
        Returns the stipulations associated with this decision.
        
        Returns:
            QuerySet: QuerySet of Stipulation objects
        """
        return Stipulation.objects.filter(application=self.application)
    
    def is_approved(self):
        """
        Checks if the decision is an approval.
        
        Returns:
            bool: True if approved, False otherwise
        """
        return self.decision == UNDERWRITING_DECISION['APPROVE']
    
    def is_denied(self):
        """
        Checks if the decision is a denial.
        
        Returns:
            bool: True if denied, False otherwise
        """
        return self.decision == UNDERWRITING_DECISION['DENY']
    
    def is_revision_requested(self):
        """
        Checks if the decision is a revision request.
        
        Returns:
            bool: True if revision requested, False otherwise
        """
        return self.decision == UNDERWRITING_DECISION['REVISE']
    
    def __str__(self):
        """
        String representation of the UnderwritingDecision instance.
        
        Returns:
            str: Application ID with decision
        """
        return f"Application {self.application.id} - {self.get_decision_display()}"


class DecisionReason(CoreModel):
    """
    Model for storing reasons for underwriting decisions.
    
    This model captures specific reasons for approvals, denials, or revision requests,
    allowing for detailed explanation of underwriting decisions.
    """
    decision = models.ForeignKey(
        UnderwritingDecision,
        on_delete=models.CASCADE,
        related_name='reasons'
    )
    reason_code = models.CharField(
        max_length=50,
        choices=DECISION_REASON_CHOICES
    )
    description = models.TextField(blank=True)
    is_primary = models.BooleanField(default=False)
    
    # Custom managers
    objects = ActiveManager()
    all_objects = models.Manager()
    
    def save(self, **kwargs):
        """
        Override save method to set description from reason code if not provided.
        
        Args:
            **kwargs: Additional arguments to pass to parent save method
        """
        # Set description from reason code if not provided
        if not self.description:
            self.description = DECISION_REASON_DESCRIPTIONS.get(self.reason_code, "")
            
        super().save(**kwargs)
    
    def __str__(self):
        """
        String representation of the DecisionReason instance.
        
        Returns:
            str: Reason code with description
        """
        primary = " (Primary)" if self.is_primary else ""
        return f"{self.get_reason_code_display()}{primary} - {self.description[:50]}"


class Stipulation(CoreModel):
    """
    Model for tracking required conditions for loan approval.
    
    This model captures requirements that must be fulfilled before a loan can be funded,
    such as providing additional documentation or meeting specific conditions.
    """
    application = models.ForeignKey(
        LoanApplication,
        on_delete=models.CASCADE,
        related_name='stipulations'
    )
    stipulation_type = models.CharField(
        max_length=50,
        choices=STIPULATION_TYPE_CHOICES
    )
    description = models.TextField()
    required_by_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STIPULATION_STATUS_CHOICES,
        default=STIPULATION_STATUS['PENDING']
    )
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_stipulations'
    )
    satisfied_at = models.DateTimeField(null=True, blank=True)
    satisfied_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='satisfied_stipulations'
    )
    
    # Custom managers
    objects = ActiveManager()
    all_objects = models.Manager()
    
    def save(self, **kwargs):
        """
        Override save method to set created_at if not provided.
        
        Args:
            **kwargs: Additional arguments to pass to parent save method
        """
        if not self.created_at:
            self.created_at = timezone.now()
            
        if not self.status:
            self.status = STIPULATION_STATUS['PENDING']
            
        super().save(**kwargs)
    
    def satisfy(self, user):
        """
        Marks the stipulation as satisfied.
        
        Args:
            user (User): User who satisfied the stipulation
            
        Returns:
            bool: True if update successful, False otherwise
        """
        self.status = STIPULATION_STATUS['SATISFIED']
        self.satisfied_at = timezone.now()
        self.satisfied_by = user
        self.save()
        return True
    
    def is_satisfied(self):
        """
        Checks if the stipulation has been satisfied.
        
        Returns:
            bool: True if satisfied, False otherwise
        """
        return self.status == STIPULATION_STATUS['SATISFIED']
    
    def is_pending(self):
        """
        Checks if the stipulation is pending.
        
        Returns:
            bool: True if pending, False otherwise
        """
        return self.status == STIPULATION_STATUS['PENDING']
    
    def is_waived(self):
        """
        Checks if the stipulation has been waived.
        
        Returns:
            bool: True if waived, False otherwise
        """
        return self.status == STIPULATION_STATUS['WAIVED']
    
    def is_overdue(self):
        """
        Checks if the stipulation is past its required date.
        
        Returns:
            bool: True if overdue, False otherwise
        """
        return (
            self.required_by_date < timezone.now().date() and
            self.status not in [
                STIPULATION_STATUS['SATISFIED'],
                STIPULATION_STATUS['WAIVED']
            ]
        )
    
    def __str__(self):
        """
        String representation of the Stipulation instance.
        
        Returns:
            str: Stipulation type with status
        """
        return f"{self.get_stipulation_type_display()} - {self.status}"


class UnderwritingNote(CoreModel):
    """
    Model for storing notes related to the underwriting process.
    
    This model captures comments and notes made during the underwriting process,
    providing a record of observations and considerations.
    """
    application = models.ForeignKey(
        LoanApplication,
        on_delete=models.CASCADE,
        related_name='underwriting_notes'
    )
    note_text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='underwriting_notes'
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
            **kwargs: Additional arguments to pass to parent save method
        """
        if not self.created_at:
            self.created_at = timezone.now()
            
        super().save(**kwargs)
    
    def __str__(self):
        """
        String representation of the UnderwritingNote instance.
        
        Returns:
            str: Note preview with application ID
        """
        preview = self.note_text[:50] + "..." if len(self.note_text) > 50 else self.note_text
        return f"Application {self.application.id}: {preview}"