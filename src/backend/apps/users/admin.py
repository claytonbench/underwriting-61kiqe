"""
Django admin configuration for user-related models in the loan management system.

This module registers user-related models with the Django admin interface and provides
custom admin classes with appropriate display, filtering, and search capabilities
for managing user data.
"""

from django.contrib import admin  # Django 4.2+
from .models import (
    User, BorrowerProfile, EmploymentInfo, 
    SchoolAdminProfile, InternalUserProfile, UserPermission
)
from ...utils.constants import (
    USER_TYPES, EMPLOYMENT_TYPES, HOUSING_STATUS, CITIZENSHIP_STATUS
)


class UserAdmin(admin.ModelAdmin):
    """Custom admin class for User model with appropriate display and filtering options."""
    list_display = ('id', 'email', 'full_name', 'user_type', 'phone', 'is_active', 'created_at')
    list_filter = ('user_type', 'is_active', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    fieldsets = (
        ('User Information', {
            'fields': ('auth0_user', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Account Details', {
            'fields': ('user_type', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')

    def full_name(self, obj):
        """
        Custom admin display method for showing the user's full name.
        
        Args:
            obj (User): The User instance
            
        Returns:
            str: User's full name
        """
        return obj.get_full_name()
    
    full_name.short_description = 'Full Name'


class BorrowerProfileAdmin(admin.ModelAdmin):
    """Custom admin class for BorrowerProfile model with appropriate display and filtering options."""
    list_display = ('id', 'user', 'full_address', 'borrower_age', 'citizenship_status', 'housing_status')
    list_filter = ('citizenship_status', 'housing_status', 'state')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'city', 'state', 'zip_code')
    raw_id_fields = ('user',)
    fieldsets = (
        ('User Association', {
            'fields': ('user',)
        }),
        ('Personal Information', {
            'fields': ('ssn', 'dob', 'citizenship_status')
        }),
        ('Address Information', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'zip_code')
        }),
        ('Housing Information', {
            'fields': ('housing_status', 'housing_payment')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    
    def full_address(self, obj):
        """
        Custom admin display method for showing the borrower's full address.
        
        Args:
            obj (BorrowerProfile): The BorrowerProfile instance
            
        Returns:
            str: Formatted full address
        """
        return obj.get_full_address()
    
    full_address.short_description = 'Address'
    
    def borrower_age(self, obj):
        """
        Custom admin display method for showing the borrower's age.
        
        Args:
            obj (BorrowerProfile): The BorrowerProfile instance
            
        Returns:
            int: Borrower's age in years
        """
        return obj.get_age()
    
    borrower_age.short_description = 'Age'


class EmploymentInfoAdmin(admin.ModelAdmin):
    """Custom admin class for EmploymentInfo model with appropriate display and filtering options."""
    list_display = ('id', 'profile', 'employer_name', 'occupation', 'employment_type', 
                    'monthly_income', 'total_income', 'years_employed', 'months_employed')
    list_filter = ('employment_type',)
    search_fields = ('profile__user__first_name', 'profile__user__last_name', 
                    'employer_name', 'occupation')
    raw_id_fields = ('profile',)
    
    def monthly_income(self, obj):
        """
        Custom admin display method for showing the monthly income.
        
        Args:
            obj (EmploymentInfo): The EmploymentInfo instance
            
        Returns:
            str: Formatted monthly income
        """
        return f"${obj.get_monthly_income():.2f}"
    
    monthly_income.short_description = 'Monthly Income'
    
    def total_income(self, obj):
        """
        Custom admin display method for showing the total annual income.
        
        Args:
            obj (EmploymentInfo): The EmploymentInfo instance
            
        Returns:
            str: Formatted total annual income
        """
        return f"${obj.get_total_income():.2f}"
    
    total_income.short_description = 'Total Annual Income'


class SchoolAdminProfileAdmin(admin.ModelAdmin):
    """Custom admin class for SchoolAdminProfile model with appropriate display and filtering options."""
    list_display = ('id', 'user', 'school', 'title', 'department', 'is_primary_contact', 'can_sign_documents')
    list_filter = ('is_primary_contact', 'can_sign_documents', 'school')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'school__name', 'title', 'department')
    raw_id_fields = ('user', 'school')


class InternalUserProfileAdmin(admin.ModelAdmin):
    """Custom admin class for InternalUserProfile model with appropriate display and filtering options."""
    list_display = ('id', 'user', 'employee_id', 'department', 'title', 'supervisor')
    list_filter = ('department',)
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'employee_id', 'department', 'title')
    raw_id_fields = ('user', 'supervisor')


class UserPermissionAdmin(admin.ModelAdmin):
    """Custom admin class for UserPermission model with appropriate display and filtering options."""
    list_display = ('id', 'user', 'permission_name', 'resource_type', 'resource_id', 'is_granted')
    list_filter = ('permission_name', 'resource_type', 'is_granted')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'permission_name', 'resource_type')
    raw_id_fields = ('user',)


# Register models with the admin site
admin.site.register(User, UserAdmin)
admin.site.register(BorrowerProfile, BorrowerProfileAdmin)
admin.site.register(EmploymentInfo, EmploymentInfoAdmin)
admin.site.register(SchoolAdminProfile, SchoolAdminProfileAdmin)
admin.site.register(InternalUserProfile, InternalUserProfileAdmin)
admin.site.register(UserPermission, UserPermissionAdmin)