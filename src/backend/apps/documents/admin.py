"""
Django admin configuration for the document management components.

This module registers document-related models with the Django admin interface and
configures custom admin classes with appropriate display, filtering, and search
capabilities for document templates, packages, documents, signature requests,
and document fields.
"""

from django.contrib import admin  # Django 4.2+
from django.utils.safestring import mark_safe

from .models import (
    DocumentTemplate, DocumentPackage, Document, SignatureRequest, DocumentField,
    DOCUMENT_TYPE_CHOICES, DOCUMENT_STATUS_CHOICES, DOCUMENT_PACKAGE_TYPE_CHOICES,
    SIGNATURE_STATUS_CHOICES, SIGNER_TYPE_CHOICES, DOCUMENT_FIELD_TYPE_CHOICES
)


class DocumentTemplateAdmin(admin.ModelAdmin):
    """Admin interface for document templates."""
    
    list_display = ('name', 'document_type', 'version', 'is_active', 'created_at', 'template_preview')
    list_filter = ('document_type', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'document_type')
    readonly_fields = ('created_at', 'created_by')
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'description', 'document_type', 'version', 'is_active')
        }),
        ('File Information', {
            'fields': ('file_path',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def template_preview(self, obj):
        """
        Generate a preview link for the template.
        
        Args:
            obj: DocumentTemplate instance
            
        Returns:
            str: HTML link for template preview
        """
        url = f"/admin/documents/preview/{obj.id}/"
        return mark_safe(f'<a href="{url}" target="_blank">Preview</a>')
    template_preview.short_description = 'Preview'
    template_preview.allow_tags = True


class DocumentInline(admin.TabularInline):
    """Inline admin for documents within a package."""
    model = Document
    extra = 0
    fields = ('document_type', 'file_name', 'status', 'generated_at')
    show_change_link = True


class DocumentPackageAdmin(admin.ModelAdmin):
    """Admin interface for document packages."""
    
    list_display = ('id', 'application_id', 'package_type', 'status', 'created_at', 
                    'expiration_date', 'document_count', 'completion_status', 'expiration_status')
    list_filter = ('package_type', 'status', 'created_at')
    search_fields = ('application__id', 'package_type')
    raw_id_fields = ('application',)
    inlines = [DocumentInline]
    
    def application_id(self, obj):
        """
        Get application ID for display in admin.
        
        Args:
            obj: DocumentPackage instance
            
        Returns:
            str: Application ID
        """
        return obj.application.id
    application_id.short_description = 'Application ID'
    
    def document_count(self, obj):
        """
        Get count of documents in the package.
        
        Args:
            obj: DocumentPackage instance
            
        Returns:
            int: Number of documents
        """
        return obj.get_documents().count()
    document_count.short_description = 'Document Count'
    
    def completion_status(self, obj):
        """
        Get completion status of the package.
        
        Args:
            obj: DocumentPackage instance
            
        Returns:
            str: 'Complete' or 'Incomplete'
        """
        return 'Complete' if obj.is_complete() else 'Incomplete'
    completion_status.short_description = 'Completion Status'
    
    def expiration_status(self, obj):
        """
        Get expiration status of the package.
        
        Args:
            obj: DocumentPackage instance
            
        Returns:
            str: 'Expired' or 'Active'
        """
        return 'Expired' if obj.is_expired() else 'Active'
    expiration_status.short_description = 'Expiration Status'


class SignatureRequestInline(admin.TabularInline):
    """Inline admin for signature requests within a document."""
    model = SignatureRequest
    extra = 0
    fields = ('signer', 'signer_type', 'status', 'requested_at', 'completed_at')
    show_change_link = True


class DocumentFieldInline(admin.TabularInline):
    """Inline admin for document fields within a document."""
    model = DocumentField
    extra = 0
    fields = ('field_name', 'field_type', 'field_value', 'x_position', 'y_position', 'page_number')
    show_change_link = True


class DocumentAdmin(admin.ModelAdmin):
    """Admin interface for documents."""
    
    list_display = ('id', 'package_id', 'document_type', 'file_name', 'status', 
                    'generated_at', 'signature_count', 'field_count', 'signing_status', 'download_link')
    list_filter = ('document_type', 'status', 'generated_at')
    search_fields = ('file_name', 'package__application__id')
    raw_id_fields = ('package', 'generated_by')
    inlines = [SignatureRequestInline, DocumentFieldInline]
    
    def package_id(self, obj):
        """
        Get package ID for display in admin.
        
        Args:
            obj: Document instance
            
        Returns:
            str: Package ID
        """
        return obj.package.id
    package_id.short_description = 'Package ID'
    
    def signature_count(self, obj):
        """
        Get count of signature requests for the document.
        
        Args:
            obj: Document instance
            
        Returns:
            int: Number of signature requests
        """
        return obj.get_signature_requests().count()
    signature_count.short_description = 'Signatures'
    
    def field_count(self, obj):
        """
        Get count of fields in the document.
        
        Args:
            obj: Document instance
            
        Returns:
            int: Number of fields
        """
        return obj.get_fields().count()
    field_count.short_description = 'Fields'
    
    def signing_status(self, obj):
        """
        Get signing status of the document.
        
        Args:
            obj: Document instance
            
        Returns:
            str: 'Signed' or 'Unsigned'
        """
        return 'Signed' if obj.is_signed() else 'Unsigned'
    signing_status.short_description = 'Signing Status'
    
    def download_link(self, obj):
        """
        Generate a download link for the document.
        
        Args:
            obj: Document instance
            
        Returns:
            str: HTML link for document download
        """
        try:
            url = obj.get_download_url()
            return mark_safe(f'<a href="{url}" target="_blank">Download</a>')
        except:
            return "N/A"
    download_link.short_description = 'Download'
    download_link.allow_tags = True


class SignatureRequestAdmin(admin.ModelAdmin):
    """Admin interface for signature requests."""
    
    list_display = ('id', 'document_type', 'signer_name', 'signer_type', 'status', 
                    'requested_at', 'completed_at', 'reminder_count', 'reminder_available')
    list_filter = ('status', 'signer_type', 'requested_at')
    search_fields = ('signer__first_name', 'signer__last_name', 'signer__email',
                     'document__file_name', 'document__document_type')
    raw_id_fields = ('document', 'signer')
    
    def document_type(self, obj):
        """
        Get document type for display in admin.
        
        Args:
            obj: SignatureRequest instance
            
        Returns:
            str: Document type
        """
        return obj.document.get_document_type_display()
    document_type.short_description = 'Document Type'
    
    def signer_name(self, obj):
        """
        Get signer's full name for display in admin.
        
        Args:
            obj: SignatureRequest instance
            
        Returns:
            str: Signer's full name
        """
        return obj.signer.get_full_name()
    signer_name.short_description = 'Signer'
    
    def reminder_available(self, obj):
        """
        Check if a reminder can be sent for this signature request.
        
        Args:
            obj: SignatureRequest instance
            
        Returns:
            str: 'Yes' or 'No'
        """
        return 'Yes' if obj.can_send_reminder() else 'No'
    reminder_available.short_description = 'Can Send Reminder'


class DocumentFieldAdmin(admin.ModelAdmin):
    """Admin interface for document fields."""
    
    list_display = ('id', 'document_id', 'field_name', 'field_type', 'page_number', 
                    'x_position', 'y_position')
    list_filter = ('field_type', 'page_number')
    search_fields = ('field_name', 'field_value', 'document__file_name')
    raw_id_fields = ('document',)
    
    def document_id(self, obj):
        """
        Get document ID for display in admin.
        
        Args:
            obj: DocumentField instance
            
        Returns:
            str: Document ID
        """
        return obj.document.id
    document_id.short_description = 'Document ID'


# Register the models with their admin classes
admin.site.register(DocumentTemplate, DocumentTemplateAdmin)
admin.site.register(DocumentPackage, DocumentPackageAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(SignatureRequest, SignatureRequestAdmin)
admin.site.register(DocumentField, DocumentFieldAdmin)