"""
Models for the workflow management system.

This module defines the data models for the workflow system that manages state transitions
for loan applications, documents, and funding processes. This includes models for tracking
transition history, scheduling automatic transitions, and managing workflow tasks.
"""

from django.db import models  # Django 4.2+
from django.utils import timezone  # Django 4.2+
from django.contrib.contenttypes.models import ContentType  # Django 4.2+
from django.contrib.contenttypes.fields import GenericForeignKey  # Django 4.2+

from ...core.models import CoreModel, ActiveManager
from .constants import (
    WORKFLOW_TYPES,
    WORKFLOW_TASK_TYPES,
    WORKFLOW_TASK_STATUS,
    WORKFLOW_SLA_DEFINITIONS,
)

# Create tuples for choices fields from dictionaries in constants
WORKFLOW_TASK_STATUS_CHOICES = [(key, value) for key, value in WORKFLOW_TASK_STATUS.items()]
WORKFLOW_TASK_TYPE_CHOICES = [(key, value) for key, value in WORKFLOW_TASK_TYPES.items()]


class WorkflowTransitionHistory(CoreModel):
    """
    Model for tracking history of workflow state transitions.
    
    Records the transition of an entity from one state to another, including
    the date, user who made the transition, and reason for the transition.
    """
    workflow_type = models.CharField(max_length=50)
    from_state = models.CharField(max_length=50)
    to_state = models.CharField(max_length=50)
    transition_date = models.DateTimeField(null=True, blank=True)
    transitioned_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workflow_transitions'
    )
    reason = models.TextField(blank=True)
    transition_event = models.CharField(max_length=100, blank=True)
    
    # Generic foreign key to link to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Custom manager
    objects = ActiveManager()
    
    def save(self, **kwargs):
        """
        Override save method to set transition_date if not provided.
        
        Args:
            **kwargs: Additional keyword arguments to pass to the parent save method.
        """
        if not self.transition_date:
            self.transition_date = timezone.now()
        super().save(**kwargs)
    
    def __str__(self):
        """
        String representation of the transition history record.
        
        Returns:
            str: Description of the transition.
        """
        return f"{self.workflow_type}: {self.from_state} → {self.to_state} on {self.transition_date}"


class AutomaticTransitionSchedule(CoreModel):
    """
    Model for scheduling automatic state transitions.
    
    Allows the system to schedule state transitions to occur automatically
    at a specific time, such as document expirations or reminder notifications.
    """
    workflow_type = models.CharField(max_length=50)
    from_state = models.CharField(max_length=50)
    to_state = models.CharField(max_length=50)
    scheduled_date = models.DateTimeField()
    is_executed = models.BooleanField(default=False)
    executed_at = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(blank=True)
    
    # Generic foreign key to link to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Custom manager
    objects = ActiveManager()
    
    def execute(self):
        """
        Executes the scheduled transition.
        
        Returns:
            bool: True if transition was successful, False otherwise.
        """
        if self.is_executed:
            return False
        
        # Import the appropriate state machine based on workflow_type
        if self.workflow_type == WORKFLOW_TYPES['APPLICATION']:
            from ..loan.state_machines import ApplicationStateMachine
            state_machine = ApplicationStateMachine(self.content_object)
        elif self.workflow_type == WORKFLOW_TYPES['DOCUMENT']:
            from ..documents.state_machines import DocumentStateMachine
            state_machine = DocumentStateMachine(self.content_object)
        elif self.workflow_type == WORKFLOW_TYPES['FUNDING']:
            from ..funding.state_machines import FundingStateMachine
            state_machine = FundingStateMachine(self.content_object)
        else:
            return False
        
        # Perform the transition
        success = state_machine.transition_to(self.to_state, reason=self.reason)
        
        if success:
            self.is_executed = True
            self.executed_at = timezone.now()
            self.save()
        
        return success
    
    def __str__(self):
        """
        String representation of the scheduled transition.
        
        Returns:
            str: Description of the scheduled transition.
        """
        return f"{self.workflow_type}: {self.from_state} → {self.to_state} scheduled for {self.scheduled_date}"


class WorkflowTaskManager(ActiveManager):
    """
    Custom manager for WorkflowTask model.
    
    Provides specialized query methods for retrieving tasks.
    """
    def get_pending_tasks(self):
        """
        Returns pending tasks.
        
        Returns:
            QuerySet: QuerySet of pending WorkflowTask objects.
        """
        return self.get_queryset().filter(status=WORKFLOW_TASK_STATUS['PENDING'])
    
    def get_tasks_by_entity(self, entity):
        """
        Returns tasks for a specific entity.
        
        Args:
            entity: The entity to get tasks for.
            
        Returns:
            QuerySet: QuerySet of WorkflowTask objects for the entity.
        """
        content_type = ContentType.objects.get_for_model(entity)
        return self.get_queryset().filter(
            content_type=content_type,
            object_id=entity.id
        )
    
    def get_tasks_by_type(self, task_type):
        """
        Returns tasks of a specific type.
        
        Args:
            task_type (str): The task type to filter by.
            
        Returns:
            QuerySet: QuerySet of WorkflowTask objects of the specified type.
        """
        return self.get_queryset().filter(task_type=task_type)
    
    def get_tasks_by_assignee(self, assignee):
        """
        Returns tasks assigned to a specific user.
        
        Args:
            assignee (User): The user to get tasks for.
            
        Returns:
            QuerySet: QuerySet of WorkflowTask objects assigned to the user.
        """
        return self.get_queryset().filter(assigned_to=assignee)


class WorkflowTask(CoreModel):
    """
    Model representing a task in a workflow process.
    
    Tasks are created as part of workflow transitions and assigned to users for completion.
    They represent actions that need to be taken to move the workflow forward.
    """
    task_type = models.CharField(max_length=50, choices=WORKFLOW_TASK_TYPE_CHOICES)
    description = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=WORKFLOW_TASK_STATUS_CHOICES,
        default=WORKFLOW_TASK_STATUS['PENDING']
    )
    created_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    completed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='completed_tasks'
    )
    notes = models.TextField(blank=True)
    
    # Generic foreign key to link to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Custom manager
    objects = WorkflowTaskManager()
    
    def save(self, **kwargs):
        """
        Override save method to set created_at if not provided.
        
        Args:
            **kwargs: Additional keyword arguments to pass to the parent save method.
        """
        if not self.created_at:
            self.created_at = timezone.now()
        
        # If this is a new task (no ID), set status to PENDING
        if not self.pk:
            self.status = WORKFLOW_TASK_STATUS['PENDING']
            
        super().save(**kwargs)
    
    def complete(self, user, notes=None):
        """
        Marks the task as completed.
        
        Args:
            user (User): The user completing the task.
            notes (str, optional): Notes about task completion.
        """
        self.status = WORKFLOW_TASK_STATUS['COMPLETED']
        self.completed_at = timezone.now()
        self.completed_by = user
        
        if notes:
            if self.notes:
                self.notes += f"\n\nCompletion notes ({timezone.now()}): {notes}"
            else:
                self.notes = f"Completion notes ({timezone.now()}): {notes}"
        
        self.save()
    
    def cancel(self, user, reason=None):
        """
        Cancels the task.
        
        Args:
            user (User): The user canceling the task.
            reason (str, optional): Reason for cancellation.
        """
        self.status = WORKFLOW_TASK_STATUS['CANCELLED']
        self.completed_at = timezone.now()
        self.completed_by = user
        
        if reason:
            if self.notes:
                self.notes += f"\n\nCancellation reason ({timezone.now()}): {reason}"
            else:
                self.notes = f"Cancellation reason ({timezone.now()}): {reason}"
        
        self.save()
    
    def reassign(self, new_assignee, reassigned_by, reason=None):
        """
        Reassigns the task to another user.
        
        Args:
            new_assignee (User): The user to reassign the task to.
            reassigned_by (User): The user making the reassignment.
            reason (str, optional): Reason for reassignment.
        """
        old_assignee = self.assigned_to
        self.assigned_to = new_assignee
        
        if reason:
            if self.notes:
                self.notes += f"\n\nReassigned from {old_assignee} to {new_assignee} by {reassigned_by} ({timezone.now()}): {reason}"
            else:
                self.notes = f"Reassigned from {old_assignee} to {new_assignee} by {reassigned_by} ({timezone.now()}): {reason}"
        
        self.save()
    
    def is_overdue(self):
        """
        Checks if the task is overdue.
        
        Returns:
            bool: True if task is overdue, False otherwise.
        """
        if not self.due_date:
            return False
        
        return (
            self.due_date < timezone.now() and
            self.status in [WORKFLOW_TASK_STATUS['PENDING'], WORKFLOW_TASK_STATUS['IN_PROGRESS']]
        )
    
    def __str__(self):
        """
        String representation of the workflow task.
        
        Returns:
            str: Description of the task.
        """
        return f"{self.task_type}: {self.description}"


class WorkflowEntity(models.Model):
    """
    Abstract model providing workflow state functionality for models.
    
    This model should be inherited by any model that needs to track workflow state
    and transitions, such as loan applications, documents, and funding requests.
    """
    current_state = models.CharField(max_length=50)
    state_changed_at = models.DateTimeField(null=True, blank=True)
    state_changed_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(app_label)s_%(class)s_state_changes'
    )
    is_terminal = models.BooleanField(default=False)
    sla_due_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def save(self, **kwargs):
        """
        Override save method to handle workflow state changes.
        
        Args:
            **kwargs: Additional keyword arguments to pass to the parent save method.
        """
        # If this is a new entity (no ID), set state_changed_at to current time
        if not self.pk:
            self.state_changed_at = timezone.now()
        
        # Call parent save method with kwargs
        super().save(**kwargs)
    
    def get_workflow_type(self):
        """
        Abstract method to get the workflow type for this entity.
        
        Returns:
            str: Workflow type string.
        
        Raises:
            NotImplementedError: If not overridden by subclass.
        """
        raise NotImplementedError("Subclasses must implement get_workflow_type()")
    
    def get_transition_history(self):
        """
        Gets the transition history for this entity.
        
        Returns:
            QuerySet: QuerySet of WorkflowTransitionHistory objects.
        """
        content_type = ContentType.objects.get_for_model(self)
        return WorkflowTransitionHistory.objects.filter(
            content_type=content_type,
            object_id=self.id
        ).order_by('-transition_date')
    
    def get_pending_tasks(self):
        """
        Gets pending tasks for this entity.
        
        Returns:
            QuerySet: QuerySet of pending WorkflowTask objects.
        """
        content_type = ContentType.objects.get_for_model(self)
        return WorkflowTask.objects.filter(
            content_type=content_type,
            object_id=self.id,
            status=WORKFLOW_TASK_STATUS['PENDING']
        )
    
    def calculate_sla_due_date(self):
        """
        Calculates the SLA due date based on current state.
        
        Returns:
            datetime: Calculated SLA due date or None if no SLA defined.
        """
        workflow_type = self.get_workflow_type()
        
        # Check if there's an SLA definition for this workflow type and state
        if (
            workflow_type in WORKFLOW_SLA_DEFINITIONS and
            self.current_state in WORKFLOW_SLA_DEFINITIONS[workflow_type]
        ):
            # Get the SLA hours from the definitions
            sla_hours = WORKFLOW_SLA_DEFINITIONS[workflow_type][self.current_state]['hours']
            
            # Calculate the due date
            return self.state_changed_at + timezone.timedelta(hours=sla_hours)
        
        return None
    
    def update_sla_due_date(self):
        """
        Updates the SLA due date based on current state.
        """
        self.sla_due_at = self.calculate_sla_due_date()
        self.save(update_fields=['sla_due_at'])
    
    def is_sla_breached(self):
        """
        Checks if the SLA for the current state is breached.
        
        Returns:
            bool: True if SLA is breached, False otherwise.
        """
        if not self.sla_due_at:
            return False
        
        return timezone.now() > self.sla_due_at