from django.contrib import admin  # Django 4.2+
from .models import (
    LoanApplication, LoanDetails, ApplicationDocument, 
    ApplicationStatusHistory, ApplicationNote,
    APPLICATION_STATUS_CHOICES, APPLICATION_TYPE_CHOICES,
    RELATIONSHIP_TYPE_CHOICES, DOCUMENT_TYPE_CHOICES
)

class LoanDetailsInline(admin.StackedInline):
    """
    Inline admin class for displaying loan details within the loan application admin interface.
    """
    model = LoanDetails
    extra = 0
    fields = ['tuition_amount', 'deposit_amount', 'other_funding', 'requested_amount', 
              'approved_amount', 'start_date', 'completion_date']
    show_change_link = True

class ApplicationDocumentInline(admin.TabularInline):
    """
    Inline admin class for displaying application documents within the loan application admin interface.
    """
    model = ApplicationDocument
    extra = 0
    fields = ['document_type', 'file_name', 'status', 'uploaded_at', 'uploaded_by']
    show_change_link = True

class ApplicationStatusHistoryInline(admin.TabularInline):
    """
    Inline admin class for displaying status history within the loan application admin interface.
    """
    model = ApplicationStatusHistory
    extra = 0
    fields = ['previous_status', 'new_status', 'changed_at', 'changed_by', 'comments']
    readonly_fields = ['previous_status', 'new_status', 'changed_at', 'changed_by', 'comments']
    show_change_link = True

class ApplicationNoteInline(admin.TabularInline):
    """
    Inline admin class for displaying application notes within the loan application admin interface.
    """
    model = ApplicationNote
    extra = 0
    fields = ['note_text', 'created_at', 'created_by', 'is_internal']
    show_change_link = True

class LoanApplicationAdmin(admin.ModelAdmin):
    """
    Custom admin class for LoanApplication model with appropriate display and filtering options.
    """
    list_display = ['id', 'borrower_name', 'school_name', 'program_name', 'application_type',
                    'status', 'requested_amount', 'submission_date', 'document_count']
    list_filter = ['status', 'application_type', 'school', 'program', 'submission_date', 'created_at']
    search_fields = ['id', 'borrower__first_name', 'borrower__last_name', 'borrower__email', 'school__name']
    
    fieldsets = (
        ('Application Information', {
            'fields': ('borrower', 'co_borrower', 'application_type', 'relationship_type', 'status', 'submission_date')
        }),
        ('School Information', {
            'fields': ('school', 'program', 'program_version')
        }),
    )
    
    readonly_fields = ['submission_date']
    inlines = [LoanDetailsInline, ApplicationDocumentInline, ApplicationStatusHistoryInline, ApplicationNoteInline]
    
    def borrower_name(self, obj):
        """
        Custom admin display method for showing the borrower's full name.
        
        Args:
            obj: The LoanApplication object
            
        Returns:
            str: Borrower's full name
        """
        return obj.borrower.get_full_name()
    
    def school_name(self, obj):
        """
        Custom admin display method for showing the school name.
        
        Args:
            obj: The LoanApplication object
            
        Returns:
            str: School name
        """
        return obj.school.name
    
    def program_name(self, obj):
        """
        Custom admin display method for showing the program name.
        
        Args:
            obj: The LoanApplication object
            
        Returns:
            str: Program name
        """
        return obj.program.name
    
    def requested_amount(self, obj):
        """
        Custom admin display method for showing the requested loan amount.
        
        Args:
            obj: The LoanApplication object
            
        Returns:
            str: Formatted requested amount or 'N/A' if not available
        """
        loan_details = obj.get_loan_details()
        if loan_details:
            return f"${loan_details.requested_amount:,.2f}"
        return "N/A"
    
    def document_count(self, obj):
        """
        Custom admin display method for showing the count of associated documents.
        
        Args:
            obj: The LoanApplication object
            
        Returns:
            int: Count of associated documents
        """
        return obj.get_documents().count()

class LoanDetailsAdmin(admin.ModelAdmin):
    """
    Custom admin class for LoanDetails model with appropriate display and filtering options.
    """
    list_display = ['application', 'tuition_amount', 'deposit_amount', 'other_funding', 
                    'requested_amount', 'approved_amount', 'net_tuition', 'start_date']
    list_filter = ['start_date', 'created_at']
    search_fields = ['application__id', 'application__borrower__first_name', 
                     'application__borrower__last_name']
    raw_id_fields = ['application']
    
    def net_tuition(self, obj):
        """
        Custom admin display method for showing the net tuition amount.
        
        Args:
            obj: The LoanDetails object
            
        Returns:
            str: Formatted net tuition amount
        """
        return f"${obj.get_net_tuition():,.2f}"

class ApplicationDocumentAdmin(admin.ModelAdmin):
    """
    Custom admin class for ApplicationDocument model with appropriate display and filtering options.
    """
    list_display = ['application', 'document_type', 'file_name', 'verification_status', 
                    'uploaded_at', 'uploaded_by']
    list_filter = ['document_type', 'status', 'uploaded_at']
    search_fields = ['application__id', 'file_name', 'document_type']
    raw_id_fields = ['application', 'uploaded_by']
    
    def verification_status(self, obj):
        """
        Custom admin display method for showing the document verification status.
        
        Args:
            obj: The ApplicationDocument object
            
        Returns:
            str: Verification status as 'Verified' or 'Not Verified'
        """
        return "Verified" if obj.is_verified() else "Not Verified"

class ApplicationStatusHistoryAdmin(admin.ModelAdmin):
    """
    Custom admin class for ApplicationStatusHistory model with appropriate display and filtering options.
    """
    list_display = ['application', 'previous_status', 'new_status', 'changed_at', 'changed_by']
    list_filter = ['previous_status', 'new_status', 'changed_at']
    search_fields = ['application__id', 'comments']
    raw_id_fields = ['application', 'changed_by']
    readonly_fields = ['previous_status', 'new_status', 'changed_at', 'changed_by', 'comments']

class ApplicationNoteAdmin(admin.ModelAdmin):
    """
    Custom admin class for ApplicationNote model with appropriate display and filtering options.
    """
    list_display = ['application', 'note_text', 'created_at', 'created_by', 'is_internal']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['application__id', 'note_text']
    raw_id_fields = ['application', 'created_by']

# Register models with admin site
admin.site.register(LoanApplication, LoanApplicationAdmin)
admin.site.register(LoanDetails, LoanDetailsAdmin)
admin.site.register(ApplicationDocument, ApplicationDocumentAdmin)
admin.site.register(ApplicationStatusHistory, ApplicationStatusHistoryAdmin)
admin.site.register(ApplicationNote, ApplicationNoteAdmin)