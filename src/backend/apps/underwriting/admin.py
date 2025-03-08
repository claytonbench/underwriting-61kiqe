"""
Admin configuration for underwriting models.

This module registers underwriting-related models with the Django admin interface
and provides custom admin classes with appropriate display, filtering, and search
capabilities.
"""

from django.contrib import admin  # Django 4.2+
from .models import (
    UnderwritingQueue, CreditInformation, UnderwritingDecision,
    DecisionReason, Stipulation, UnderwritingNote,
    UNDERWRITING_QUEUE_PRIORITY_CHOICES, UNDERWRITING_QUEUE_STATUS_CHOICES,
    UNDERWRITING_DECISION_CHOICES, STIPULATION_TYPE_CHOICES, STIPULATION_STATUS_CHOICES
)


class UnderwritingQueueAdmin(admin.ModelAdmin):
    """Admin interface for the UnderwritingQueue model."""
    list_display = ('application_id', 'borrower_name', 'status', 'priority', 
                    'assigned_to', 'underwriter_name', 'assignment_date', 'due_date', 
                    'overdue_status', 'created_at')
    list_filter = ('status', 'priority', 'assignment_date', 'due_date', 'is_deleted')
    search_fields = ('application__id', 'application__borrower__first_name', 'application__borrower__last_name',
                     'assigned_to__first_name', 'assigned_to__last_name')
    raw_id_fields = ('application', 'assigned_to', 'created_by', 'updated_by')
    readonly_fields = ('created_at', 'updated_at')
    
    def application_id(self, obj):
        """Display the application ID."""
        return obj.application.id
    
    def borrower_name(self, obj):
        """Display the borrower's full name."""
        borrower = obj.application.borrower
        return f"{borrower.first_name} {borrower.last_name}"
    
    def underwriter_name(self, obj):
        """Display the assigned underwriter's name or 'Unassigned'."""
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}"
        return "Unassigned"
    
    def overdue_status(self, obj):
        """Display whether the queue item is overdue."""
        return "Overdue" if obj.is_overdue() else "On Time"


class CreditInformationAdmin(admin.ModelAdmin):
    """Admin interface for the CreditInformation model."""
    list_display = ('application_id', 'borrower_name', 'is_co_borrower', 'credit_score', 
                    'credit_tier', 'report_date', 'monthly_debt', 'debt_to_income_ratio')
    list_filter = ('is_co_borrower', 'report_date', 'is_deleted')
    search_fields = ('application__id', 'borrower__first_name', 'borrower__last_name', 
                     'credit_score')
    raw_id_fields = ('application', 'borrower', 'uploaded_by', 'created_by', 'updated_by')
    
    def application_id(self, obj):
        """Display the application ID."""
        return obj.application.id
    
    def borrower_name(self, obj):
        """Display the borrower's full name."""
        return f"{obj.borrower.first_name} {obj.borrower.last_name}"
    
    def credit_tier(self, obj):
        """Display the credit tier based on credit score."""
        return obj.get_credit_tier()


class DecisionReasonInline(admin.TabularInline):
    """Inline admin for DecisionReason within UnderwritingDecision."""
    model = DecisionReason
    extra = 1
    fields = ('reason_code', 'description', 'is_primary')


class StipulationInline(admin.TabularInline):
    """Inline admin for Stipulation within UnderwritingDecision."""
    model = Stipulation
    extra = 1
    fields = ('stipulation_type', 'description', 'required_by_date', 'status')
    show_change_link = True


class UnderwritingDecisionAdmin(admin.ModelAdmin):
    """Admin interface for the UnderwritingDecision model."""
    list_display = ('application_id', 'borrower_name', 'decision', 'decision_date',
                    'underwriter_name', 'approved_amount', 'interest_rate', 'term_months')
    list_filter = ('decision', 'decision_date', 'is_deleted')
    search_fields = ('application__id', 'application__borrower__first_name', 
                     'application__borrower__last_name', 'underwriter__first_name', 
                     'underwriter__last_name', 'comments')
    raw_id_fields = ('application', 'underwriter', 'created_by', 'updated_by')
    inlines = [DecisionReasonInline]
    
    def application_id(self, obj):
        """Display the application ID."""
        return obj.application.id
    
    def borrower_name(self, obj):
        """Display the borrower's full name."""
        borrower = obj.application.borrower
        return f"{borrower.first_name} {borrower.last_name}"
    
    def underwriter_name(self, obj):
        """Display the underwriter's full name."""
        return f"{obj.underwriter.first_name} {obj.underwriter.last_name}"


class DecisionReasonAdmin(admin.ModelAdmin):
    """Admin interface for the DecisionReason model."""
    list_display = ('decision', 'reason_code', 'description', 'is_primary')
    list_filter = ('reason_code', 'is_primary', 'is_deleted')
    search_fields = ('description',)
    raw_id_fields = ('decision', 'created_by', 'updated_by')


class StipulationAdmin(admin.ModelAdmin):
    """Admin interface for the Stipulation model."""
    list_display = ('application_id', 'stipulation_type', 'required_by_date', 
                   'status', 'satisfaction_status', 'due_status', 'created_by', 
                   'satisfied_by', 'satisfied_at')
    list_filter = ('stipulation_type', 'status', 'required_by_date')
    search_fields = ('application__id', 'description', 'created_by__first_name',
                    'created_by__last_name')
    raw_id_fields = ('application', 'created_by', 'satisfied_by', 'updated_by')
    
    def application_id(self, obj):
        """Display the application ID."""
        return obj.application.id
    
    def satisfaction_status(self, obj):
        """Display whether the stipulation is satisfied."""
        return "Satisfied" if obj.is_satisfied() else "Not Satisfied"
    
    def due_status(self, obj):
        """Display whether the stipulation is overdue."""
        return "Overdue" if obj.is_overdue() else "On Time"


class UnderwritingNoteAdmin(admin.ModelAdmin):
    """Admin interface for the UnderwritingNote model."""
    list_display = ('application_id', 'author_name', 'note_preview', 'created_at', 
                   'is_internal')
    list_filter = ('created_at', 'is_internal', 'is_deleted')
    search_fields = ('application__id', 'note_text', 'created_by__first_name',
                    'created_by__last_name')
    raw_id_fields = ('application', 'created_by', 'updated_by')
    
    def application_id(self, obj):
        """Display the application ID."""
        return obj.application.id
    
    def author_name(self, obj):
        """Display the note author's full name."""
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"
    
    def note_preview(self, obj):
        """Display a preview of the note text."""
        if len(obj.note_text) > 50:
            return f"{obj.note_text[:50]}..."
        return obj.note_text


# Register models with the admin site
admin.site.register(UnderwritingQueue, UnderwritingQueueAdmin)
admin.site.register(CreditInformation, CreditInformationAdmin)
admin.site.register(UnderwritingDecision, UnderwritingDecisionAdmin)
admin.site.register(DecisionReason, DecisionReasonAdmin)
admin.site.register(Stipulation, StipulationAdmin)
admin.site.register(UnderwritingNote, UnderwritingNoteAdmin)