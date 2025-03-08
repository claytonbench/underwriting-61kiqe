"""
Django admin configuration for the School and Program management models.

This module registers School, Program, ProgramVersion, SchoolDocument, and SchoolContact
models with the Django admin interface, providing custom admin classes with appropriate
display, filtering, and search capabilities.
"""

from django.contrib import admin  # Django 4.2+

from .models import (
    School,
    Program,
    ProgramVersion,
    SchoolDocument,
    SchoolContact,
    SCHOOL_STATUS_CHOICES,
    PROGRAM_STATUS_CHOICES,
    DOCUMENT_TYPE_CHOICES
)


class ProgramInline(admin.TabularInline):
    """Inline admin for programs within a school."""
    model = Program
    extra = 1
    fields = ('name', 'description', 'duration_weeks', 'duration_hours', 'status')
    show_change_link = True


class SchoolContactInline(admin.TabularInline):
    """Inline admin for contacts within a school."""
    model = SchoolContact
    extra = 1
    fields = ('first_name', 'last_name', 'title', 'email', 'phone', 'is_primary', 'can_sign_documents')
    show_change_link = True


class SchoolAdmin(admin.ModelAdmin):
    """Admin interface for the School model."""
    list_display = ('name', 'legal_name', 'city', 'state', 'status', 'full_address', 'active_programs_count', 'phone')
    list_filter = ('status', 'state', 'created_at')
    search_fields = ('name', 'legal_name', 'city', 'address_line1', 'phone')
    fieldsets = (
        ('School Information', {
            'fields': ('name', 'legal_name', 'tax_id', 'status', 'website')
        }),
        ('Address Information', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'zip_code', 'phone')
        }),
        ('Audit Information', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by')
        }),
    )
    inlines = [ProgramInline, SchoolContactInline]
    
    def full_address(self, obj):
        """Display the school's full address."""
        return obj.get_full_address()
    full_address.short_description = 'Full Address'
    
    def active_programs_count(self, obj):
        """Display count of active programs for the school."""
        return obj.get_active_programs().count()
    active_programs_count.short_description = 'Active Programs'


class ProgramVersionInline(admin.TabularInline):
    """Inline admin for program versions within a program."""
    model = ProgramVersion
    extra = 1
    fields = ('version_number', 'effective_date', 'tuition_amount', 'is_current')
    show_change_link = True


class ProgramAdmin(admin.ModelAdmin):
    """Admin interface for the Program model."""
    list_display = ('name', 'school', 'duration_weeks', 'duration_hours', 'status', 'current_tuition')
    list_filter = ('status', 'school')
    search_fields = ('name', 'school__name', 'description')
    raw_id_fields = ['school']
    inlines = [ProgramVersionInline]
    
    def current_tuition(self, obj):
        """Display the current tuition amount for the program."""
        tuition = obj.get_current_tuition()
        if tuition:
            return f"${tuition:,.2f}"
        return "N/A"
    current_tuition.short_description = 'Current Tuition'


class ProgramVersionAdmin(admin.ModelAdmin):
    """Admin interface for the ProgramVersion model."""
    list_display = ('program', 'version_number', 'effective_date', 'tuition_amount', 'is_current')
    list_filter = ('is_current', 'effective_date', 'program__school')
    search_fields = ('program__name', 'program__school__name')
    raw_id_fields = ['program']


class SchoolDocumentAdmin(admin.ModelAdmin):
    """Admin interface for the SchoolDocument model."""
    list_display = ('school', 'document_type', 'file_name', 'uploaded_at', 'uploaded_by', 'status')
    list_filter = ('document_type', 'status', 'uploaded_at')
    search_fields = ('school__name', 'file_name', 'document_type')
    raw_id_fields = ['school', 'uploaded_by']


class SchoolContactAdmin(admin.ModelAdmin):
    """Admin interface for the SchoolContact model."""
    list_display = ('contact_name', 'school', 'title', 'email', 'phone', 'is_primary', 'can_sign_documents')
    list_filter = ('is_primary', 'can_sign_documents', 'school')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'school__name')
    raw_id_fields = ['school']
    
    def contact_name(self, obj):
        """Display the contact's full name."""
        return obj.get_full_name()
    contact_name.short_description = 'Name'


# Register models with the admin site
admin.site.register(School, SchoolAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(ProgramVersion, ProgramVersionAdmin)
admin.site.register(SchoolDocument, SchoolDocumentAdmin)
admin.site.register(SchoolContact, SchoolContactAdmin)