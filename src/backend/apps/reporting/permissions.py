"""
Defines custom permission classes for the reporting functionality in the loan management system.

These permission classes control access to report configurations, report generation,
scheduling, exporting, and permission management based on user roles and specific permissions.
"""

from rest_framework.permissions import BasePermission  # version 3.14+

from ...core.permissions import (
    IsAuthenticated, 
    IsSystemAdmin, 
    IsUnderwriter, 
    IsQC, 
    IsSchoolAdmin, 
    IsInternalUser,
    USER_ROLES
)
from ..models import ReportPermission


class CanViewReports(BasePermission):
    """Permission class that determines if a user can view reports"""
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to view reports
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # System administrators can view all reports
        if IsSystemAdmin().has_permission(request, view):
            return True
        
        # Underwriters can view reports
        if IsUnderwriter().has_permission(request, view):
            return True
        
        # QC personnel can view reports
        if IsQC().has_permission(request, view):
            return True
        
        # School administrators can view their school's reports
        if IsSchoolAdmin().has_permission(request, view):
            return True
        
        # All other user types don't have permission to view reports
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to view a specific report
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The report configuration or saved report object
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # System administrators can view all reports
        if IsSystemAdmin().has_permission(request, view):
            return True
        
        # Internal users (underwriters and QC) can view all reports
        if IsInternalUser().has_permission(request, view):
            return True
        
        # School administrators can only view their school's reports
        if IsSchoolAdmin().has_permission(request, view):
            # Check if this is a ReportConfiguration object
            if hasattr(obj, 'school'):
                return obj.school and obj.school.id == request.user.school_id
            
            # Check if this is a SavedReport object
            if hasattr(obj, 'configuration') and hasattr(obj.configuration, 'school'):
                return obj.configuration.school and obj.configuration.school.id == request.user.school_id
        
        # Check if user has explicit permission to view this report
        try:
            if hasattr(obj, 'permissions'):
                report_permission = obj.permissions.filter(user=request.user).first()
                if report_permission and report_permission.can_view:
                    return True
            elif hasattr(obj, 'configuration') and hasattr(obj.configuration, 'permissions'):
                report_permission = obj.configuration.permissions.filter(user=request.user).first()
                if report_permission and report_permission.can_view:
                    return True
        except Exception:
            pass
        
        return False


class CanManageReportConfigurations(BasePermission):
    """Permission class that determines if a user can create, update, or delete report configurations"""
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to manage report configurations
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # System administrators can manage all report configurations
        if IsSystemAdmin().has_permission(request, view):
            return True
        
        # School administrators can manage their school's report configurations
        if IsSchoolAdmin().has_permission(request, view):
            return True
        
        # All other user types don't have permission to manage report configurations
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to manage a specific report configuration
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The report configuration object
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # System administrators can manage all report configurations
        if IsSystemAdmin().has_permission(request, view):
            return True
        
        # School administrators can only manage their school's report configurations
        if IsSchoolAdmin().has_permission(request, view):
            return obj.school and obj.school.id == request.user.school_id
        
        return False


class CanGenerateReports(BasePermission):
    """Permission class that determines if a user can generate reports"""
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to generate reports
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # System administrators can generate any report
        if IsSystemAdmin().has_permission(request, view):
            return True
        
        # Underwriters can generate reports
        if IsUnderwriter().has_permission(request, view):
            return True
        
        # QC personnel can generate reports
        if IsQC().has_permission(request, view):
            return True
        
        # School administrators can generate their school's reports
        if IsSchoolAdmin().has_permission(request, view):
            return True
        
        # All other user types don't have permission to generate reports
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to generate a specific report
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The report configuration object
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # System administrators can generate any report
        if IsSystemAdmin().has_permission(request, view):
            return True
        
        # Internal users (underwriters and QC) can generate any report
        if IsInternalUser().has_permission(request, view):
            return True
        
        # School administrators can only generate their school's reports
        if IsSchoolAdmin().has_permission(request, view):
            # Check if this is a ReportConfiguration object with a school
            if hasattr(obj, 'school'):
                return obj.school and obj.school.id == request.user.school_id
        
        # Check if user has explicit permission to generate this report
        try:
            report_permission = obj.permissions.filter(user=request.user).first()
            if report_permission and report_permission.can_generate:
                return True
        except Exception:
            pass
        
        return False


class CanScheduleReports(BasePermission):
    """Permission class that determines if a user can schedule reports"""
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to schedule reports
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # System administrators can schedule any report
        if IsSystemAdmin().has_permission(request, view):
            return True
        
        # School administrators can schedule their school's reports
        if IsSchoolAdmin().has_permission(request, view):
            return True
        
        # All other user types don't have permission to schedule reports
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to schedule a specific report
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The report configuration or schedule object
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # System administrators can schedule any report
        if IsSystemAdmin().has_permission(request, view):
            return True
        
        # School administrators can only schedule their school's reports
        if IsSchoolAdmin().has_permission(request, view):
            # Check if this is a ReportConfiguration object
            if hasattr(obj, 'school'):
                return obj.school and obj.school.id == request.user.school_id
            
            # Check if this is a ReportSchedule object
            if hasattr(obj, 'configuration') and hasattr(obj.configuration, 'school'):
                return obj.configuration.school and obj.configuration.school.id == request.user.school_id
        
        # Check if user has explicit permission to schedule this report
        try:
            # Determine the configuration object
            configuration = obj if hasattr(obj, 'permissions') else obj.configuration
            report_permission = configuration.permissions.filter(user=request.user).first()
            if report_permission and report_permission.can_schedule:
                return True
        except Exception:
            pass
        
        return False


class CanExportReports(BasePermission):
    """Permission class that determines if a user can export reports"""
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to export reports
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # System administrators can export any report
        if IsSystemAdmin().has_permission(request, view):
            return True
        
        # Underwriters can export reports
        if IsUnderwriter().has_permission(request, view):
            return True
        
        # QC personnel can export reports
        if IsQC().has_permission(request, view):
            return True
        
        # School administrators can export their school's reports
        if IsSchoolAdmin().has_permission(request, view):
            return True
        
        # All other user types don't have permission to export reports
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to export a specific report
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The saved report object
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # System administrators can export any report
        if IsSystemAdmin().has_permission(request, view):
            return True
        
        # Internal users (underwriters and QC) can export any report
        if IsInternalUser().has_permission(request, view):
            return True
        
        # School administrators can only export their school's reports
        if IsSchoolAdmin().has_permission(request, view):
            if hasattr(obj, 'configuration') and hasattr(obj.configuration, 'school'):
                return obj.configuration.school and obj.configuration.school.id == request.user.school_id
        
        # Check if user has explicit permission to export this report
        try:
            report_permission = obj.configuration.permissions.filter(user=request.user).first()
            if report_permission and report_permission.can_export:
                return True
        except Exception:
            pass
        
        return False


class CanManageReportPermissions(BasePermission):
    """Permission class that determines if a user can manage report permissions"""
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to manage report permissions
        
        Args:
            request: The request object
            view: The view that triggered the check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # System administrators can manage all report permissions
        if IsSystemAdmin().has_permission(request, view):
            return True
        
        # School administrators can manage permissions for their school's reports
        if IsSchoolAdmin().has_permission(request, view):
            return True
        
        # All other user types don't have permission to manage report permissions
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to manage permissions for a specific report configuration
        
        Args:
            request: The request object
            view: The view that triggered the check
            obj: The report configuration object
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # System administrators can manage permissions for any report
        if IsSystemAdmin().has_permission(request, view):
            return True
        
        # School administrators can only manage permissions for their school's reports
        if IsSchoolAdmin().has_permission(request, view):
            if hasattr(obj, 'school'):
                return obj.school and obj.school.id == request.user.school_id
            
            # If we're working with a ReportPermission object, check its configuration
            if hasattr(obj, 'configuration') and hasattr(obj.configuration, 'school'):
                return obj.configuration.school and obj.configuration.school.id == request.user.school_id
        
        return False