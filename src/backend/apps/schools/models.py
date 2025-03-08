"""
Defines the data models for schools and educational programs in the loan management system.
"""

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal

from core.models import (
    CoreModel, UUIDModel, TimeStampedModel, SoftDeleteModel, 
    AuditableModel, ActiveManager
)
from utils.constants import US_STATES
from utils.validators import (
    validate_state_code, validate_zip_code, validate_phone, 
    validate_positive_number
)
from utils.encryption import EncryptedField

# Status choices
SCHOOL_STATUS_CHOICES = [
    ("active", "Active"),
    ("inactive", "Inactive"),
    ("pending", "Pending Approval"),
    ("rejected", "Rejected")
]

PROGRAM_STATUS_CHOICES = [
    ("active", "Active"),
    ("inactive", "Inactive")
]

DOCUMENT_TYPE_CHOICES = [
    ("enrollment_agreement", "Enrollment Agreement"),
    ("accreditation", "Accreditation Document"),
    ("catalog", "School Catalog"),
    ("other", "Other Document")
]


class School(CoreModel):
    """
    Model representing an educational institution that offers programs eligible for financing.
    """
    name = models.CharField(max_length=100)
    legal_name = models.CharField(max_length=200)
    tax_id = models.CharField(max_length=20)  # Will be encrypted through the application layer
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)
    phone = models.CharField(max_length=14)  # Format: (XXX) XXX-XXXX
    website = models.URLField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, choices=SCHOOL_STATUS_CHOICES, default="pending")
    
    objects = ActiveManager()
    all_objects = models.Manager()
    
    def clean(self):
        """
        Validates the school data before saving.
        """
        super().clean()
        try:
            validate_state_code(self.state)
            validate_zip_code(self.zip_code)
            validate_phone(self.phone)
        except ValidationError as e:
            raise ValidationError(str(e))
        
    def get_active_programs(self):
        """
        Returns all active programs offered by this school.
        
        Returns:
            QuerySet of active Program objects
        """
        return self.program_set.filter(status='active')
    
    def get_administrators(self):
        """
        Returns all administrators associated with this school.
        
        Returns:
            QuerySet of SchoolAdminProfile objects
        """
        # This references a SchoolAdminProfile model defined in the users app
        from apps.users.models import SchoolAdminProfile
        return SchoolAdminProfile.objects.filter(school=self)
    
    def get_primary_contact(self):
        """
        Returns the primary contact administrator for this school.
        
        Returns:
            SchoolAdminProfile: The primary contact or None if not found
        """
        contacts = self.contacts.filter(is_primary=True)
        return contacts.first() if contacts.exists() else None
    
    def get_full_address(self):
        """
        Returns the school's full address as a formatted string.
        
        Returns:
            str: Formatted full address
        """
        address = self.address_line1
        if self.address_line2:
            address += f", {self.address_line2}"
        address += f", {self.city}, {self.state} {self.zip_code}"
        return address
    
    def get_applications(self):
        """
        Returns all loan applications associated with this school.
        
        Returns:
            QuerySet of LoanApplication objects
        """
        # This references a LoanApplication model defined in the applications app
        from apps.applications.models import LoanApplication
        return LoanApplication.objects.filter(school=self)
    
    def __str__(self):
        return self.name


class Program(CoreModel):
    """
    Model representing an educational program offered by a school.
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration_hours = models.IntegerField()
    duration_weeks = models.IntegerField()
    status = models.CharField(max_length=20, choices=PROGRAM_STATUS_CHOICES, default="active")
    
    objects = ActiveManager()
    all_objects = models.Manager()
    
    def clean(self):
        """
        Validates the program data before saving.
        """
        super().clean()
        try:
            validate_positive_number(self.duration_hours)
            validate_positive_number(self.duration_weeks)
        except ValidationError as e:
            raise ValidationError(str(e))
    
    def get_current_version(self):
        """
        Returns the current active version of this program.
        
        Returns:
            ProgramVersion: The current ProgramVersion object or None if not found
        """
        return self.programversion_set.filter(is_current=True).first()
    
    def get_all_versions(self):
        """
        Returns all versions of this program ordered by version number.
        
        Returns:
            QuerySet of ProgramVersion objects
        """
        return self.programversion_set.order_by('-version_number')
    
    def get_current_tuition(self):
        """
        Returns the current tuition amount for this program.
        
        Returns:
            Decimal: Current tuition amount or None if no current version
        """
        current_version = self.get_current_version()
        return current_version.tuition_amount if current_version else None
    
    def create_new_version(self, tuition_amount, effective_date):
        """
        Creates a new version of this program with updated tuition.
        
        Args:
            tuition_amount (Decimal): The new tuition amount
            effective_date (date): The date when the new version becomes effective
            
        Returns:
            ProgramVersion: The newly created ProgramVersion object
        """
        # Get all existing versions
        versions = self.get_all_versions()
        
        # Determine the next version number
        next_version = 1
        if versions.exists():
            next_version = versions.first().version_number + 1
        
        # Set all existing versions to not current
        self.programversion_set.update(is_current=False)
        
        # Create the new version
        new_version = ProgramVersion.objects.create(
            program=self,
            version_number=next_version,
            effective_date=effective_date,
            tuition_amount=tuition_amount,
            is_current=True
        )
        
        return new_version
    
    def __str__(self):
        return f"{self.name} - {self.school.name}"


class ProgramVersion(CoreModel):
    """
    Model representing a specific version of a program with its tuition amount and effective date.
    """
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    version_number = models.IntegerField()
    effective_date = models.DateField()
    tuition_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_current = models.BooleanField(default=False)
    
    objects = ActiveManager()
    all_objects = models.Manager()
    
    class Meta:
        unique_together = ('program', 'version_number')
    
    def clean(self):
        """
        Validates the program version data before saving.
        """
        super().clean()
        try:
            validate_positive_number(self.tuition_amount)
        except ValidationError as e:
            raise ValidationError(str(e))
    
    def save(self, **kwargs):
        """
        Override save method to handle version management.
        
        If this is a new version and is set as current, update all other versions
        to not be current before saving.
        """
        if not self.pk and self.is_current:
            ProgramVersion.objects.filter(program=self.program).update(is_current=False)
        
        super().save(**kwargs)
        return self
    
    def __str__(self):
        return f"{self.program.name} v{self.version_number} - ${self.tuition_amount}"


class SchoolDocument(CoreModel):
    """
    Model representing a document associated with a school.
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(default=timezone.now)
    uploaded_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL, 
        null=True,
        related_name='uploaded_school_documents'
    )
    status = models.CharField(max_length=20, default="active")
    
    objects = ActiveManager()
    all_objects = models.Manager()
    
    def get_download_url(self, expiry_seconds=3600):
        """
        Generates a download URL for the document.
        
        Args:
            expiry_seconds (int): URL expiration time in seconds
            
        Returns:
            str: Presigned URL for downloading the document
        """
        # Import here to avoid circular imports
        from utils.storage import get_presigned_url
        return get_presigned_url(self.file_path, expiry_seconds)
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.school.name}"


class SchoolContactManager(ActiveManager):
    """
    Custom manager for SchoolContact model to provide additional query methods.
    """
    def get_primary_contacts(self):
        """
        Returns all primary contacts across all schools.
        
        Returns:
            QuerySet of SchoolContact objects that are primary contacts
        """
        return self.filter(is_primary=True)
    
    def get_signers(self):
        """
        Returns all contacts that can sign documents.
        
        Returns:
            QuerySet of SchoolContact objects that can sign documents
        """
        return self.filter(can_sign_documents=True)


class SchoolContact(CoreModel):
    """
    Model representing a contact person for a school who is not necessarily a user.
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='contacts')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=14)  # Format: (XXX) XXX-XXXX
    is_primary = models.BooleanField(default=False)
    can_sign_documents = models.BooleanField(default=False)
    
    objects = SchoolContactManager()
    all_objects = models.Manager()
    
    def clean(self):
        """
        Validates the contact data before saving.
        """
        super().clean()
        try:
            validate_phone(self.phone)
        except ValidationError as e:
            raise ValidationError(str(e))
    
    def get_full_name(self):
        """
        Returns the contact's full name.
        
        Returns:
            str: Contact's full name
        """
        return f"{self.first_name} {self.last_name}"
    
    def save(self, **kwargs):
        """
        Override save method to handle primary contact logic.
        
        If this contact is being set as primary, set all other contacts
        for this school to not primary before saving.
        """
        if self.is_primary:
            SchoolContact.objects.filter(school=self.school).exclude(pk=self.pk).update(is_primary=False)
        
        super().save(**kwargs)
        return self
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.school.name}"