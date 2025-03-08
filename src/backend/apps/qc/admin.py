from django.contrib import admin  # Django 4.2+

from .models import (  # Importing QC-related models
    QCReview, DocumentVerification, QCStipulationVerification,
    QCChecklistItem, QC_STATUS_CHOICES, QC_VERIFICATION_STATUS_CHOICES,
    QC_RETURN_REASON_CHOICES, QC_CHECKLIST_CATEGORY_CHOICES,
    QC_PRIORITY_CHOICES, QC_ASSIGNMENT_TYPE_CHOICES
)


@admin.register(QCReview)
class QCReviewAdmin(admin.ModelAdmin):
    """
    Custom admin class for QCReview model with appropriate display and filtering options
    """
    list_display = [
        'application_id',
        'borrower_name',
        'school_name',
        'status',
        'priority',
        'assigned_to_name',
        'completion_percentage',
        'is_complete_status'
    ]
    list_filter = [
        'status',
        'priority',
        'assigned_to',
        'assignment_type'
    ]
    search_fields = [
        'application__id',
        'application__borrower__first_name',
        'application__borrower__last_name',
        'application__school__name',
        'assigned_to__first_name',
        'assigned_to__last_name'
    ]
    fieldsets = (
        (None, {
            'fields': ('application', 'status', 'priority', 'assigned_to', 'assignment_type', 'return_reason', 'notes')
        }),
    )
    readonly_fields = ('application',)
    inlines = [
        'DocumentVerificationInline',
        'QCStipulationVerificationInline',
        'QCChecklistItemInline'
    ]

    def application_id(self, obj):
        """
        Custom admin display method for showing the application ID
        Args:
            obj: QCReview object
        Returns:
            str: Application ID
        """
        return obj.application.id

    application_id.short_description = 'Application ID'  # Human-readable column header

    def borrower_name(self, obj):
        """
        Custom admin display method for showing the borrower's full name
        Args:
            obj: QCReview object
        Returns:
            str: Borrower's full name
        """
        return obj.application.borrower.get_full_name()

    borrower_name.short_description = 'Borrower Name'  # Human-readable column header

    def school_name(self, obj):
        """
        Custom admin display method for showing the school name
        Args:
            obj: QCReview object
        Returns:
            str: School name
        """
        return obj.application.school.name

    school_name.short_description = 'School Name'  # Human-readable column header

    def assigned_to_name(self, obj):
        """
        Custom admin display method for showing the assigned reviewer's name
        Args:
            obj: QCReview object
        Returns:
            str: Assigned reviewer's name or 'Unassigned'
        """
        if obj.assigned_to:
            return obj.assigned_to.get_full_name()
        return 'Unassigned'

    assigned_to_name.short_description = 'Assigned To'  # Human-readable column header

    def completion_percentage(self, obj):
        """
        Custom admin display method for showing the QC review completion percentage
        Args:
            obj: QCReview object
        Returns:
            str: Formatted completion percentage
        """
        return f"{obj.get_completion_percentage():.2f}%"

    completion_percentage.short_description = 'Completion (%)'  # Human-readable column header

    def is_complete_status(self, obj):
        """
        Custom admin display method for showing whether the QC review is complete
        Args:
            obj: QCReview object
        Returns:
            str: 'Complete' or 'Incomplete'
        """
        return 'Complete' if obj.is_complete() else 'Incomplete'

    is_complete_status.short_description = 'Complete'  # Human-readable column header


class DocumentVerificationInline(admin.TabularInline):
    """
    Inline admin class for displaying document verifications within the QC review admin interface
    """
    model = DocumentVerification
    extra = 1
    fields = ['document', 'status', 'verified_by', 'verified_at', 'comments']
    show_change_link = True


class QCStipulationVerificationInline(admin.TabularInline):
    """
    Inline admin class for displaying stipulation verifications within the QC review admin interface
    """
    model = QCStipulationVerification
    extra = 1
    fields = ['stipulation', 'status', 'verified_by', 'verified_at', 'comments']
    show_change_link = True


class QCChecklistItemInline(admin.TabularInline):
    """
    Inline admin class for displaying checklist items within the QC review admin interface
    """
    model = QCChecklistItem
    extra = 1
    fields = ['category', 'item_text', 'status', 'verified_by', 'verified_at', 'comments']
    show_change_link = True


@admin.register(DocumentVerification)
class DocumentVerificationAdmin(admin.ModelAdmin):
    """
    Custom admin class for DocumentVerification model with appropriate display and filtering options
    """
    list_display = [
        'application_id',
        'document_type',
        'status',
        'verification_status',
        'verified_by',
        'verified_at'
    ]
    list_filter = [
        'status',
        'verified_by',
        'verified_at'
    ]
    search_fields = [
        'qc_review__application__id',
        'document__document_type',
        'verified_by__first_name',
        'verified_by__last_name'
    ]
    raw_id_fields = ['qc_review', 'document', 'verified_by']

    def application_id(self, obj):
        """
        Custom admin display method for showing the application ID
        Args:
            obj: DocumentVerification object
        Returns:
            str: Application ID
        """
        return obj.qc_review.application.id

    application_id.short_description = 'Application ID'  # Human-readable column header

    def document_type(self, obj):
        """
        Custom admin display method for showing the document type
        Args:
            obj: DocumentVerification object
        Returns:
            str: Document type
        """
        return obj.document.get_document_type_display()

    document_type.short_description = 'Document Type'  # Human-readable column header

    def verification_status(self, obj):
        """
        Custom admin display method for showing the document verification status
        Args:
            obj: DocumentVerification object
        Returns:
            str: Verification status as 'Verified', 'Rejected', 'Waived', or 'Unverified'
        """
        return obj.status


    verification_status.short_description = 'Verification Status'  # Human-readable column header


@admin.register(QCStipulationVerification)
class QCStipulationVerificationAdmin(admin.ModelAdmin):
    """
    Custom admin class for QCStipulationVerification model with appropriate display and filtering options
    """
    list_display = [
        'application_id',
        'stipulation_description',
        'status',
        'verification_status',
        'verified_by',
        'verified_at'
    ]
    list_filter = [
        'status',
        'verified_by',
        'verified_at'
    ]
    search_fields = [
        'qc_review__application__id',
        'stipulation__description',
        'verified_by__first_name',
        'verified_by__last_name'
    ]
    raw_id_fields = ['qc_review', 'stipulation', 'verified_by']

    def application_id(self, obj):
        """
        Custom admin display method for showing the application ID
        Args:
            obj: QCStipulationVerification object
        Returns:
            str: Application ID
        """
        return obj.qc_review.application.id

    application_id.short_description = 'Application ID'  # Human-readable column header

    def stipulation_description(self, obj):
        """
        Custom admin display method for showing the stipulation description
        Args:
            obj: QCStipulationVerification object
        Returns:
            str: Stipulation description
        """
        return obj.stipulation.description

    stipulation_description.short_description = 'Stipulation Description'  # Human-readable column header

    def verification_status(self, obj):
        """
        Custom admin display method for showing the stipulation verification status
        Args:
            obj: QCStipulationVerification object
        Returns:
            str: Verification status as 'Verified', 'Rejected', 'Waived', or 'Unverified'
        """
        return obj.status

    verification_status.short_description = 'Verification Status'  # Human-readable column header


@admin.register(QCChecklistItem)
class QCChecklistItemAdmin(admin.ModelAdmin):
    """
    Custom admin class for QCChecklistItem model with appropriate display and filtering options
    """
    list_display = [
        'application_id',
        'category',
        'item_text',
        'status',
        'verification_status',
        'verified_by',
        'verified_at'
    ]
    list_filter = [
        'category',
        'status',
        'verified_by',
        'verified_at'
    ]
    search_fields = [
        'qc_review__application__id',
        'item_text',
        'verified_by__first_name',
        'verified_by__last_name'
    ]
    raw_id_fields = ['qc_review', 'verified_by']

    def application_id(self, obj):
        """
        Custom admin display method for showing the application ID
        Args:
            obj: QCChecklistItem object
        Returns:
            str: Application ID
        """
        return obj.qc_review.application.id

    application_id.short_description = 'Application ID'  # Human-readable column header

    def verification_status(self, obj):
        """
        Custom admin display method for showing the checklist item verification status
        Args:
            obj: QCChecklistItem object
        Returns:
            str: Verification status as 'Verified', 'Rejected', 'Waived', or 'Unverified'
        """
        return obj.status

    verification_status.short_description = 'Verification Status'  # Human-readable column header