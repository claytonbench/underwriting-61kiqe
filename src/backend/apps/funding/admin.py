from django.contrib import admin

from .models import (
    FundingRequest, 
    Disbursement, 
    EnrollmentVerification, 
    StipulationVerification, 
    FundingNote,
    FUNDING_REQUEST_STATUS_CHOICES,
    DISBURSEMENT_METHOD_CHOICES,
    DISBURSEMENT_STATUS_CHOICES,
    ENROLLMENT_VERIFICATION_TYPE_CHOICES,
    VERIFICATION_STATUS_CHOICES,
    FUNDING_NOTE_TYPE_CHOICES,
    FUNDING_APPROVAL_LEVEL_CHOICES
)


class DisbursementInline(admin.TabularInline):
    model = Disbursement
    extra = 0
    fields = ['amount', 'disbursement_date', 'disbursement_method', 'status', 'reference_number']
    show_change_link = True


class EnrollmentVerificationInline(admin.StackedInline):
    model = EnrollmentVerification
    extra = 0
    fields = ['verification_type', 'start_date', 'verified_at', 'verified_by', 'comments', 'document']
    show_change_link = True


class StipulationVerificationInline(admin.TabularInline):
    model = StipulationVerification
    extra = 0
    fields = ['stipulation', 'status', 'verified_at', 'verified_by', 'comments']
    show_change_link = True


class FundingNoteInline(admin.TabularInline):
    model = FundingNote
    extra = 0
    fields = ['note_type', 'note_text', 'created_at', 'created_by']
    show_change_link = True


class FundingRequestAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'application_id', 
        'borrower_name',
        'school_name', 
        'requested_amount', 
        'approved_amount', 
        'status', 
        'disbursement_count',
        'has_enrollment_verification',
        'requested_at', 
        'approved_at'
    ]
    
    list_filter = [
        'status',
        'requested_at',
        'approved_at',
        'approval_level'
    ]
    
    search_fields = [
        'id',
        'application__id',
        'application__borrower__first_name',
        'application__borrower__last_name',
        'application__school__name',
        'requested_amount',
        'approved_amount'
    ]
    
    fieldsets = (
        ('Request Information', {
            'fields': (
                'application', 
                'status', 
                'requested_amount', 
                'approved_amount',
                'requested_at',
                'requested_by'
            )
        }),
        ('Approval Information', {
            'fields': (
                'approval_level', 
                'approved_at', 
                'approved_by'
            )
        })
    )
    
    readonly_fields = ['requested_at', 'requested_by', 'approved_at', 'approved_by']
    
    inlines = [
        EnrollmentVerificationInline,
        StipulationVerificationInline,
        DisbursementInline,
        FundingNoteInline
    ]
    
    def application_id(self, obj):
        """Return the application ID."""
        return obj.application.id
    
    def borrower_name(self, obj):
        """Return the borrower's full name."""
        return obj.application.borrower.get_full_name()
    
    def school_name(self, obj):
        """Return the school name."""
        return obj.application.school.name
    
    def disbursement_count(self, obj):
        """Return the count of associated disbursements."""
        return obj.get_disbursements().count()
    
    def has_enrollment_verification(self, obj):
        """Return True if enrollment has been verified, False otherwise."""
        return obj.get_enrollment_verification() is not None


class DisbursementAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'application_id',
        'funding_request', 
        'amount', 
        'disbursement_date', 
        'disbursement_method',
        'status',
        'reference_number',
        'completion_status',
        'processed_by'
    ]
    
    list_filter = [
        'status',
        'disbursement_method',
        'disbursement_date'
    ]
    
    search_fields = [
        'id',
        'funding_request__id',
        'funding_request__application__id',
        'reference_number',
        'amount'
    ]
    
    raw_id_fields = ['funding_request', 'processed_by']
    
    def application_id(self, obj):
        """Return the application ID."""
        return obj.funding_request.application.id
    
    def completion_status(self, obj):
        """Return 'Completed' if disbursement is completed, 'Pending' otherwise."""
        return 'Completed' if obj.is_completed() else 'Pending'


class EnrollmentVerificationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'application_id',
        'funding_request',
        'verification_type',
        'start_date',
        'verified_at',
        'verified_by'
    ]
    
    list_filter = [
        'verification_type',
        'start_date',
        'verified_at'
    ]
    
    search_fields = [
        'id',
        'funding_request__id',
        'funding_request__application__id',
        'comments'
    ]
    
    raw_id_fields = ['funding_request', 'verified_by', 'document']
    
    def application_id(self, obj):
        """Return the application ID."""
        return obj.funding_request.application.id


class StipulationVerificationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'application_id',
        'funding_request',
        'stipulation',
        'stipulation_description',
        'status',
        'verification_status',
        'verified_at',
        'verified_by'
    ]
    
    list_filter = [
        'status',
        'verified_at'
    ]
    
    search_fields = [
        'id',
        'funding_request__id',
        'funding_request__application__id',
        'stipulation__id',
        'stipulation__description',
        'comments'
    ]
    
    raw_id_fields = ['funding_request', 'stipulation', 'verified_by']
    
    def application_id(self, obj):
        """Return the application ID."""
        return obj.funding_request.application.id
    
    def stipulation_description(self, obj):
        """Return the stipulation description."""
        return obj.stipulation.description
    
    def verification_status(self, obj):
        """Return 'Verified' if stipulation is verified, 'Not Verified' otherwise."""
        return 'Verified' if obj.is_verified() else 'Not Verified'


class FundingNoteAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'application_id',
        'funding_request',
        'note_type',
        'note_text',
        'created_at',
        'created_by'
    ]
    
    list_filter = [
        'note_type',
        'created_at'
    ]
    
    search_fields = [
        'id',
        'funding_request__id',
        'funding_request__application__id',
        'note_text'
    ]
    
    raw_id_fields = ['funding_request', 'created_by']
    
    def application_id(self, obj):
        """Return the application ID."""
        return obj.funding_request.application.id


# Register models to the admin site
admin.site.register(FundingRequest, FundingRequestAdmin)
admin.site.register(Disbursement, DisbursementAdmin)
admin.site.register(EnrollmentVerification, EnrollmentVerificationAdmin)
admin.site.register(StipulationVerification, StipulationVerificationAdmin)
admin.site.register(FundingNote, FundingNoteAdmin)