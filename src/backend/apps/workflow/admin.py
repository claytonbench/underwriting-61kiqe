"""
Django admin configuration for workflow-related models.

This module provides custom admin classes for workflow models,
enabling efficient management of workflow state transitions,
tasks, and schedules through the Django admin interface.
"""

from django.contrib import admin  # Django 4.2+
from django.utils.html import format_html  # Django 4.2+

from .models import (
    WorkflowTransitionHistory,
    AutomaticTransitionSchedule,
    WorkflowTask,
)
from .constants import (
    WORKFLOW_TYPES,
    WORKFLOW_TASK_TYPES,
    WORKFLOW_TASK_STATUS,
)


class WorkflowTransitionHistoryAdmin(admin.ModelAdmin):
    """Admin interface for workflow transition history."""
    list_display = ('content_object', 'workflow_type', 'state_change', 'transition_date', 'transitioned_by')
    list_filter = ('workflow_type', 'from_state', 'to_state', 'transition_date')
    search_fields = ('workflow_type', 'from_state', 'to_state', 'reason', 'transition_event')
    readonly_fields = (
        'workflow_type', 'from_state', 'to_state', 'transition_date',
        'transitioned_by', 'reason', 'transition_event', 'content_type',
        'object_id', 'content_object'
    )
    fieldsets = (
        (None, {
            'fields': ('content_object', 'workflow_type')
        }),
        ('Transition Details', {
            'fields': ('from_state', 'to_state', 'transition_date', 'transitioned_by')
        }),
        ('Additional Information', {
            'fields': ('reason', 'transition_event')
        }),
    )

    def state_change(self, obj):
        """Format state transition with an arrow."""
        return format_html(
            '<span style="color: #666;">{}</span> &rarr; <span style="color: #007bff; font-weight: bold;">{}</span>',
            obj.from_state,
            obj.to_state
        )
    state_change.short_description = 'State Transition'

    def has_add_permission(self, request):
        """Disable adding transition history directly through admin."""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing transition history records through admin."""
        return False


class AutomaticTransitionScheduleAdmin(admin.ModelAdmin):
    """Admin interface for automatic transition schedules."""
    list_display = (
        'content_object', 'workflow_type', 'state_change', 'scheduled_date', 
        'status', 'executed_at'
    )
    list_filter = (
        'workflow_type', 'from_state', 'to_state', 'scheduled_date', 
        'is_executed'
    )
    search_fields = ('workflow_type', 'from_state', 'to_state', 'reason')
    readonly_fields = ('executed_at',)
    fieldsets = (
        (None, {
            'fields': ('content_object', 'workflow_type')
        }),
        ('Transition Details', {
            'fields': ('from_state', 'to_state', 'scheduled_date', 'reason')
        }),
        ('Execution Status', {
            'fields': ('is_executed', 'executed_at')
        }),
    )
    actions = ['execute_selected']

    def state_change(self, obj):
        """Format state transition with an arrow."""
        return format_html(
            '<span style="color: #666;">{}</span> &rarr; <span style="color: #007bff; font-weight: bold;">{}</span>',
            obj.from_state,
            obj.to_state
        )
    state_change.short_description = 'State Transition'

    def status(self, obj):
        """Format execution status with color coding."""
        if obj.is_executed:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">Executed</span>'
            )
        else:
            return format_html(
                '<span style="color: #ffc107; font-weight: bold;">Pending</span>'
            )
    status.short_description = 'Status'

    def execute_selected(self, request, queryset):
        """Admin action to manually execute selected scheduled transitions."""
        # Filter out already executed schedules
        not_executed = queryset.filter(is_executed=False)
        executed_count = 0
        
        for schedule in not_executed:
            if schedule.execute():
                executed_count += 1
        
        if executed_count > 0:
            self.message_user(
                request, 
                f"Successfully executed {executed_count} transition(s)."
            )
        else:
            self.message_user(
                request, 
                "No transitions were executed. They may have been already executed or failed."
            )
    execute_selected.short_description = "Execute selected transitions"


class WorkflowTaskAdmin(admin.ModelAdmin):
    """Admin interface for workflow tasks."""
    list_display = (
        'content_object', 'task_type', 'description', 'task_status', 
        'assigned_to', 'due_date_status', 'created_at'
    )
    list_filter = (
        'task_type', 'status', 'created_at', 'due_date', 
        'assigned_to', 'completed_by'
    )
    search_fields = ('description', 'notes', 'task_type')
    fieldsets = (
        (None, {
            'fields': ('content_object', 'task_type', 'description')
        }),
        ('Assignment Details', {
            'fields': ('status', 'assigned_to', 'due_date')
        }),
        ('Completion Details', {
            'fields': ('completed_at', 'completed_by', 'notes')
        }),
    )
    actions = ['mark_completed', 'mark_cancelled']

    def task_status(self, obj):
        """Format task status with color coding."""
        status_colors = {
            WORKFLOW_TASK_STATUS['PENDING']: '#ffc107',     # Yellow
            WORKFLOW_TASK_STATUS['IN_PROGRESS']: '#17a2b8', # Blue
            WORKFLOW_TASK_STATUS['COMPLETED']: '#28a745',   # Green
            WORKFLOW_TASK_STATUS['CANCELLED']: '#dc3545',   # Red
        }
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            status_colors.get(obj.status, '#6c757d'),
            obj.get_status_display() if hasattr(obj, 'get_status_display') else obj.status
        )
    task_status.short_description = 'Status'

    def due_date_status(self, obj):
        """Format due date status with color coding for overdue tasks."""
        if not obj.due_date:
            return 'No due date'
        
        if obj.is_overdue():
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">Overdue</span>'
            )
        else:
            return format_html(
                '<span style="color: #28a745;">{}</span>',
                obj.due_date.strftime('%Y-%m-%d')
            )
    due_date_status.short_description = 'Due Date'

    def mark_completed(self, request, queryset):
        """Mark selected tasks as completed."""
        # Filter to include only pending or in-progress tasks
        eligible_tasks = queryset.filter(
            status__in=[
                WORKFLOW_TASK_STATUS['PENDING'], 
                WORKFLOW_TASK_STATUS['IN_PROGRESS']
            ]
        )
        completed_count = 0
        
        for task in eligible_tasks:
            task.complete(request.user)
            completed_count += 1
        
        if completed_count > 0:
            self.message_user(
                request, 
                f"Successfully marked {completed_count} task(s) as completed."
            )
        else:
            self.message_user(
                request, 
                "No tasks were marked as completed. They may have been already completed or cancelled."
            )
    mark_completed.short_description = "Mark selected tasks as completed"

    def mark_cancelled(self, request, queryset):
        """Mark selected tasks as cancelled."""
        # Filter to include only pending or in-progress tasks
        eligible_tasks = queryset.filter(
            status__in=[
                WORKFLOW_TASK_STATUS['PENDING'], 
                WORKFLOW_TASK_STATUS['IN_PROGRESS']
            ]
        )
        cancelled_count = 0
        
        for task in eligible_tasks:
            task.cancel(request.user, reason="Cancelled via admin action")
            cancelled_count += 1
        
        if cancelled_count > 0:
            self.message_user(
                request, 
                f"Successfully cancelled {cancelled_count} task(s)."
            )
        else:
            self.message_user(
                request, 
                "No tasks were cancelled. They may have been already completed or cancelled."
            )
    mark_cancelled.short_description = "Mark selected tasks as cancelled"


# Register models with admin
admin.site.register(WorkflowTransitionHistory, WorkflowTransitionHistoryAdmin)
admin.site.register(AutomaticTransitionSchedule, AutomaticTransitionScheduleAdmin)
admin.site.register(WorkflowTask, WorkflowTaskAdmin)