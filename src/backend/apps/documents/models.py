"""
Defines the data models for document management in the loan management system.

This includes models for document templates, document packages, individual documents,
signature requests, and document fields. These models support the generation, storage,
signing, and tracking of all loan-related documents throughout the application lifecycle.
"""

from django.db import models  # Django 4.2+
from django.utils import timezone  # Django 4.2+
from datetime import timedelta  # standard library
from django.core.exceptions import ValidationError  # Django 4.2+

from core.models import CoreModel, ActiveManager
from apps.applications.models import LoanApplication
from apps.users.models import User
from .storage import DocumentStorage
from .constants import (
    DOCUMENT_TYPES, DOCUMENT_STATUS, DOCUMENT_PACKAGE_TYPES,
    SIGNATURE_STATUS, SIGNER_TYPES, DOCUMENT_FIELD_TYPES,
    DOCUMENT_EXPIRATION_DAYS
)

# Create choice tuples for model fields
DOCUMENT_TYPE_CHOICES = ([(doc_type, doc_name) for doc_type, doc_name in DOCUMENT_TYPES.items()])
DOCUMENT_STATUS_CHOICES = ([(status, label) for status, label in DOCUMENT_STATUS.items()])
DOCUMENT_PACKAGE_TYPE_CHOICES = ([(pkg_type, label) for pkg_type, label in DOCUMENT_PACKAGE_TYPES.items()])
SIGNATURE_STATUS_CHOICES = ([(status, label) for status, label in SIGNATURE_STATUS.items()])
SIGNER_TYPE_CHOICES = ([(signer_type, label) for signer_type, label in SIGNER_TYPES.items()])
DOCUMENT_FIELD_TYPE_CHOICES = ([(field_type, label) for field_type, label in DOCUMENT_FIELD_TYPES.items()])

# Initialize document storage
document_storage = DocumentStorage()


class DocumentTemplate(CoreModel):
    """
    Model for storing document templates used to generate loan documents.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    file_path = models.CharField(max_length=255)
    version = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_templates'
    )
    
    objects = ActiveManager()
    all_objects = models.Manager()
    
    def get_content(self):
        """
        Retrieves the template content from storage.
        
        Returns:
            str: Template content as string
        """
        try:
            content, _, _ = document_storage.retrieve_document(self.file_path)
            return content.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to retrieve template content: {str(e)}")
    
    def save(self, **kwargs):
        """
        Override save method to handle template versioning.
        
        If this is a new template (no ID), set created_at to current time.
        If version is not set, set it to '1.0'.
        If is_active is True, deactivate other templates of the same type.
        """
        if not self.pk:
            self.created_at = timezone.now()
            
        if not self.version:
            self.version = '1.0'
            
        # If this template is active, deactivate other templates of the same type
        if self.is_active:
            DocumentTemplate.objects.filter(
                document_type=self.document_type,
                is_active=True
            ).exclude(pk=self.pk).update(is_active=False)
            
        super().save(**kwargs)
    
    def __str__(self):
        """
        String representation of the DocumentTemplate instance.
        
        Returns:
            str: Template name and version
        """
        return f"{self.name} - v{self.version}"


class DocumentPackage(CoreModel):
    """
    Model for grouping related documents that should be processed together.
    """
    application = models.ForeignKey(
        LoanApplication,
        on_delete=models.CASCADE,
        related_name='document_packages'
    )
    package_type = models.CharField(max_length=50, choices=DOCUMENT_PACKAGE_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=DOCUMENT_STATUS_CHOICES, default=DOCUMENT_STATUS['DRAFT'])
    created_at = models.DateTimeField(default=timezone.now)
    expiration_date = models.DateTimeField(null=True, blank=True)
    
    objects = ActiveManager()
    all_objects = models.Manager()
    
    def save(self, **kwargs):
        """
        Override save method to set created_at and expiration_date.
        
        If this is a new package (no ID), set created_at to current time.
        If expiration_date is not set, calculate it as created_at + DOCUMENT_EXPIRATION_DAYS.
        """
        if not self.pk:
            self.created_at = timezone.now()
            
        if not self.expiration_date:
            self.expiration_date = self.created_at + timedelta(days=DOCUMENT_EXPIRATION_DAYS)
            
        super().save(**kwargs)
    
    def get_documents(self):
        """
        Returns all documents in this package.
        
        Returns:
            QuerySet: QuerySet of Document objects in this package
        """
        return Document.objects.filter(package=self)
    
    def is_complete(self):
        """
        Checks if all documents in the package are completed.
        
        Returns:
            bool: True if all documents are completed, False otherwise
        """
        documents = self.get_documents()
        if not documents.exists():
            return False
        
        return all(doc.status == DOCUMENT_STATUS['COMPLETED'] for doc in documents)
    
    def is_expired(self):
        """
        Checks if the package has expired.
        
        Returns:
            bool: True if package is expired, False otherwise
        """
        return timezone.now() > self.expiration_date if self.expiration_date else False
    
    def update_status(self):
        """
        Updates the package status based on document statuses.
        
        Returns:
            bool: True if status was updated, False otherwise
        """
        documents = self.get_documents()
        if not documents.exists():
            return False
        
        old_status = self.status
        
        # Check if all documents are completed
        if all(doc.status == DOCUMENT_STATUS['COMPLETED'] for doc in documents):
            self.status = DOCUMENT_STATUS['COMPLETED']
        # Check if any document is expired
        elif any(doc.status == DOCUMENT_STATUS['EXPIRED'] for doc in documents):
            self.status = DOCUMENT_STATUS['EXPIRED']
        # Check if any document is declined
        elif any(doc.status == DOCUMENT_STATUS['DECLINED'] for doc in documents):
            self.status = DOCUMENT_STATUS['DECLINED']
        # Check if all documents are at least generated
        elif all(doc.status != DOCUMENT_STATUS['DRAFT'] for doc in documents):
            if any(doc.status == DOCUMENT_STATUS['SIGNED'] for doc in documents):
                self.status = DOCUMENT_STATUS['SIGNED']
            elif any(doc.status == DOCUMENT_STATUS['SENT'] for doc in documents):
                self.status = DOCUMENT_STATUS['SENT']
            else:
                self.status = DOCUMENT_STATUS['GENERATED']
        
        if old_status != self.status:
            self.save(update_fields=['status'])
            return True
        
        return False
    
    def __str__(self):
        """
        String representation of the DocumentPackage instance.
        
        Returns:
            str: Package type and application ID
        """
        return f"{self.get_package_type_display()} - Application {self.application.id}"


class Document(CoreModel):
    """
    Model representing an individual document in the system.
    """
    package = models.ForeignKey(
        DocumentPackage,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    version = models.CharField(max_length=20, default='1.0')
    status = models.CharField(
        max_length=20, 
        choices=DOCUMENT_STATUS_CHOICES,
        default=DOCUMENT_STATUS['DRAFT']
    )
    generated_at = models.DateTimeField(null=True, blank=True)
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_documents'
    )
    
    objects = ActiveManager()
    all_objects = models.Manager()
    
    def save(self, **kwargs):
        """
        Override save method to set generated_at and handle status changes.
        
        If this is a new document (no ID), set generated_at to current time.
        If status is changing, handle any side effects (e.g., update package status).
        """
        if not self.pk:
            self.generated_at = timezone.now()
        
        # If status changed to COMPLETED, check if package should be updated
        if self.pk:
            try:
                old_document = Document.objects.get(pk=self.pk)
                if old_document.status != self.status and self.status == DOCUMENT_STATUS['COMPLETED']:
                    # We'll update the package status after saving this document
                    update_package = True
                else:
                    update_package = False
            except Document.DoesNotExist:
                update_package = False
        else:
            update_package = False
        
        super().save(**kwargs)
        
        # Update package status if needed
        if update_package:
            self.package.update_status()
    
    def get_content(self):
        """
        Retrieves the document content from storage.
        
        Returns:
            bytes: Document content as bytes
        """
        try:
            content, _, _ = document_storage.retrieve_document(self.file_path)
            return content
        except Exception as e:
            raise ValueError(f"Failed to retrieve document content: {str(e)}")
    
    def get_download_url(self, expiry_seconds=3600):
        """
        Generates a download URL for the document.
        
        Args:
            expiry_seconds (int): URL expiration time in seconds
            
        Returns:
            str: Presigned URL for downloading the document
        """
        try:
            return document_storage.get_document_url(self.file_path, expiry_seconds)
        except Exception as e:
            raise ValueError(f"Failed to generate download URL: {str(e)}")
    
    def get_signature_requests(self):
        """
        Returns all signature requests for this document.
        
        Returns:
            QuerySet: QuerySet of SignatureRequest objects
        """
        return SignatureRequest.objects.filter(document=self)
    
    def get_fields(self):
        """
        Returns all document fields for this document.
        
        Returns:
            QuerySet: QuerySet of DocumentField objects
        """
        return DocumentField.objects.filter(document=self)
    
    def update_status(self, new_status):
        """
        Updates the document status.
        
        Args:
            new_status (str): New status value
            
        Returns:
            bool: True if status was updated, False otherwise
        """
        if new_status not in dict(DOCUMENT_STATUS_CHOICES):
            raise ValidationError(f"Invalid status: {new_status}")
        
        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])
            
            # Update package status
            self.package.update_status()
            return True
        
        return False
    
    def is_signed(self):
        """
        Checks if the document has been signed by all required signers.
        
        Returns:
            bool: True if document is signed, False otherwise
        """
        signature_requests = self.get_signature_requests()
        if not signature_requests.exists():
            return False
        
        return all(sig.status == SIGNATURE_STATUS['COMPLETED'] for sig in signature_requests)
    
    def is_expired(self):
        """
        Checks if the document has expired.
        
        Returns:
            bool: True if document is expired, False otherwise
        """
        return self.package.is_expired()
    
    def __str__(self):
        """
        String representation of the Document instance.
        
        Returns:
            str: Document type and file name
        """
        return f"{self.get_document_type_display()} - {self.file_name}"


class SignatureRequest(CoreModel):
    """
    Model tracking signature requests for documents.
    """
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='signature_requests'
    )
    signer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='signature_requests'
    )
    signer_type = models.CharField(max_length=20, choices=SIGNER_TYPE_CHOICES)
    status = models.CharField(
        max_length=20,
        choices=SIGNATURE_STATUS_CHOICES,
        default=SIGNATURE_STATUS['PENDING']
    )
    requested_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    reminder_count = models.IntegerField(default=0)
    last_reminder_at = models.DateTimeField(null=True, blank=True)
    external_reference = models.CharField(max_length=255, null=True, blank=True)
    
    objects = ActiveManager()
    all_objects = models.Manager()
    
    def save(self, **kwargs):
        """
        Override save method to set requested_at and handle status changes.
        
        If this is a new request (no ID), set requested_at to current time.
        If status is changing to 'COMPLETED', set completed_at to current time.
        """
        if not self.pk:
            self.requested_at = timezone.now()
        
        # If status changed to COMPLETED, set completed_at
        if self.pk:
            try:
                old_request = SignatureRequest.objects.get(pk=self.pk)
                if old_request.status != self.status and self.status == SIGNATURE_STATUS['COMPLETED']:
                    self.completed_at = timezone.now()
            except SignatureRequest.DoesNotExist:
                pass
        
        super().save(**kwargs)
        
        # If all signatures are complete, update document status
        if self.status == SIGNATURE_STATUS['COMPLETED']:
            # Check if all signatures for this document are complete
            document_signatures = SignatureRequest.objects.filter(document=self.document)
            if all(sig.status == SIGNATURE_STATUS['COMPLETED'] for sig in document_signatures):
                self.document.update_status(DOCUMENT_STATUS['COMPLETED'])
    
    def update_status(self, new_status):
        """
        Updates the signature request status.
        
        Args:
            new_status (str): New status value
            
        Returns:
            bool: True if status was updated, False otherwise
        """
        if new_status not in dict(SIGNATURE_STATUS_CHOICES):
            raise ValidationError(f"Invalid status: {new_status}")
        
        if self.status != new_status:
            self.status = new_status
            
            # If completing, set the completed_at timestamp
            if new_status == SIGNATURE_STATUS['COMPLETED']:
                self.completed_at = timezone.now()
                
            self.save(update_fields=['status', 'completed_at'] if new_status == SIGNATURE_STATUS['COMPLETED'] else ['status'])
            
            # Check if document status should be updated
            if new_status == SIGNATURE_STATUS['COMPLETED']:
                # If all signature requests for this document are complete, update document status
                all_signatures = SignatureRequest.objects.filter(document=self.document)
                if all(sig.status == SIGNATURE_STATUS['COMPLETED'] for sig in all_signatures):
                    self.document.update_status(DOCUMENT_STATUS['COMPLETED'])
            
            return True
        
        return False
    
    def send_reminder(self):
        """
        Sends a reminder to the signer.
        
        Returns:
            bool: True if reminder was sent, False otherwise
        """
        from .constants import MAX_REMINDERS, REMINDER_INTERVAL_DAYS
        
        # Don't send reminder if already completed or max reminders reached
        if self.status == SIGNATURE_STATUS['COMPLETED'] or self.reminder_count >= MAX_REMINDERS:
            return False
        
        # Don't send reminder if last reminder was sent recently
        if self.last_reminder_at and (timezone.now() - self.last_reminder_at).days < REMINDER_INTERVAL_DAYS:
            return False
        
        # Increment reminder count and update last reminder date
        self.reminder_count += 1
        self.last_reminder_at = timezone.now()
        self.save(update_fields=['reminder_count', 'last_reminder_at'])
        
        # Trigger notification (this would integrate with your notification system)
        try:
            # This is a placeholder - in a real implementation, you would call your notification service
            # notification_service.send_signature_reminder(self)
            return True
        except Exception as e:
            return False
    
    def can_send_reminder(self):
        """
        Checks if a reminder can be sent.
        
        Returns:
            bool: True if reminder can be sent, False otherwise
        """
        from .constants import MAX_REMINDERS, REMINDER_INTERVAL_DAYS
        
        # Don't send reminder if already completed or max reminders reached
        if self.status == SIGNATURE_STATUS['COMPLETED'] or self.reminder_count >= MAX_REMINDERS:
            return False
        
        # Don't send reminder if last reminder was sent recently
        if self.last_reminder_at and (timezone.now() - self.last_reminder_at).days < REMINDER_INTERVAL_DAYS:
            return False
        
        return True
    
    def get_signing_url(self, return_url=None):
        """
        Gets the URL for signing the document.
        
        Args:
            return_url (str): URL to redirect to after signing
            
        Returns:
            str: URL for signing the document
        """
        # This would integrate with your e-signature service provider (e.g., DocuSign)
        try:
            # This is a placeholder - in a real implementation, you would call your e-signature service
            # from integrations.docusign import DocuSignService
            # docusign = DocuSignService()
            # return docusign.get_signing_url(self, return_url)
            return f"https://example.com/sign/{self.external_reference}?return={return_url}"
        except Exception as e:
            raise ValueError(f"Failed to generate signing URL: {str(e)}")
    
    def __str__(self):
        """
        String representation of the SignatureRequest instance.
        
        Returns:
            str: Document type, signer name, and status
        """
        return f"{self.document.get_document_type_display()} - {self.signer.get_full_name()} - {self.get_status_display()}"


class DocumentField(CoreModel):
    """
    Model representing a field in a document (signature, date, text, etc.).
    """
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='fields'
    )
    field_name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20, choices=DOCUMENT_FIELD_TYPE_CHOICES)
    field_value = models.TextField(null=True, blank=True)
    x_position = models.IntegerField()
    y_position = models.IntegerField()
    page_number = models.IntegerField(default=1)
    
    objects = ActiveManager()
    all_objects = models.Manager()
    
    def to_docusign_tab(self):
        """
        Converts the field to a DocuSign tab definition.
        
        Returns:
            dict: DocuSign tab definition
        """
        # Base tab properties common to all types
        tab = {
            'documentId': str(self.document.id),
            'pageNumber': self.page_number,
            'xPosition': self.x_position,
            'yPosition': self.y_position
        }
        
        # Add type-specific properties
        if self.field_type == DOCUMENT_FIELD_TYPES['SIGNATURE']:
            tab.update({
                'tabType': 'signHereTab',
                'tabLabel': self.field_name,
                'signatureNameRequired': True
            })
        elif self.field_type == DOCUMENT_FIELD_TYPES['DATE']:
            tab.update({
                'tabType': 'dateSignedTab',
                'tabLabel': self.field_name
            })
        elif self.field_type == DOCUMENT_FIELD_TYPES['TEXT']:
            tab.update({
                'tabType': 'textTab',
                'tabLabel': self.field_name,
                'value': self.field_value or ''
            })
        elif self.field_type == DOCUMENT_FIELD_TYPES['CHECKBOX']:
            tab.update({
                'tabType': 'checkboxTab',
                'tabLabel': self.field_name,
                'selected': self.field_value == 'true' if self.field_value else False
            })
        elif self.field_type == DOCUMENT_FIELD_TYPES['INITIAL']:
            tab.update({
                'tabType': 'initialHereTab',
                'tabLabel': self.field_name
            })
        
        return tab
    
    def __str__(self):
        """
        String representation of the DocumentField instance.
        
        Returns:
            str: Field name and type
        """
        return f"{self.field_name} ({self.get_field_type_display()})"