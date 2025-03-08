"""
Provides service functions for the workflow module, handling operations related to workflow
state transitions, task management, and SLA monitoring. This file implements the business
logic layer for workflow operations, abstracting the complexity of state transitions and
related operations from the views and API endpoints.
"""

import logging
from datetime import datetime, timedelta

from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from .constants import (
    WORKFLOW_TYPES,
    WORKFLOW_TASK_TYPES,
    WORKFLOW_TASK_STATUS,
    WORKFLOW_SLA_DEFINITIONS,
    REQUIRED_ACTIONS,
    WORKFLOW_NOTIFICATION_EVENTS,
    WORKFLOW_TRANSITION_EVENTS,
    AUTOMATIC_TRANSITIONS,
)
from .models import (
    WorkflowTransitionHistory,
    WorkflowTask,
    AutomaticTransitionSchedule,
)
from .state_machine import (
    StateMachine,
    validate_transition as state_machine_validate_transition,
    get_allowed_transitions as state_machine_get_allowed_transitions,
    get_initial_state
)
from .transitions import (
    TransitionHandlerFactory,
    initialize_workflow,
    transition_entity
)

# Configure logger
logger = logging.getLogger(__name__)


def get_entity_workflow_type(entity):
    """
    Gets the workflow type for an entity based on its class.
    
    Args:
        entity: The entity to get the workflow type for
    
    Returns:
        str: The workflow type string or None if not found
    """
    try:
        # If entity has a get_workflow_type method, use it
        if hasattr(entity, 'get_workflow_type') and callable(entity.get_workflow_type):
            return entity.get_workflow_type()
        
        # Otherwise, determine based on class name
        class_name = entity.__class__.__name__
        if 'Application' in class_name:
            return WORKFLOW_TYPES['APPLICATION']
        elif 'Document' in class_name:
            return WORKFLOW_TYPES['DOCUMENT']
        elif 'Funding' in class_name:
            return WORKFLOW_TYPES['FUNDING']
        
        logger.warning(f"Could not determine workflow type for entity: {entity}")
        return None
    except Exception as e:
        logger.error(f"Error getting workflow type: {str(e)}", exc_info=True)
        return None


def get_allowed_transitions(entity):
    """
    Gets the allowed next states for an entity's current state.
    
    Args:
        entity: The entity to get allowed transitions for
        
    Returns:
        list: List of allowed next states
    """
    workflow_type = get_entity_workflow_type(entity)
    if not workflow_type:
        return []
    
    try:
        state_machine = StateMachine(workflow_type)
        current_state = entity.current_state
        return state_machine.get_allowed_transitions(current_state)
    except Exception as e:
        logger.error(f"Error getting allowed transitions: {str(e)}", exc_info=True)
        return []


def validate_transition(entity, to_state, user):
    """
    Validates if a transition from current state to target state is allowed.
    
    Args:
        entity: The entity to validate transition for
        to_state (str): The target state
        user: The user attempting the transition
        
    Returns:
        bool: True if transition is valid, False otherwise
    """
    workflow_type = get_entity_workflow_type(entity)
    if not workflow_type:
        return False
    
    try:
        handler = TransitionHandlerFactory.get_handler_for_entity(entity)
        return handler.validate_transition(entity, to_state, user)
    except Exception as e:
        logger.error(f"Error validating transition: {str(e)}", exc_info=True)
        return False


def perform_transition(entity, to_state, user, reason=None, validate=True):
    """
    Transitions an entity to a new state with validation and error handling.
    
    Args:
        entity: The entity to transition
        to_state (str): The target state
        user: The user initiating the transition
        reason (str): The reason for the transition
        validate (bool): Whether to validate the transition first
        
    Returns:
        bool: True if transition was successful, False otherwise
    """
    logger.info(f"Attempting to transition entity to state: {to_state}")
    
    # Validate the transition if required
    if validate and not validate_transition(entity, to_state, user):
        logger.error(f"Invalid transition to state: {to_state}")
        return False
    
    try:
        # Use the transition_entity function from transitions.py
        success = transition_entity(entity, to_state, user, reason)
        if success:
            logger.info(f"Successfully transitioned entity to state: {to_state}")
        return success
    except Exception as e:
        logger.error(f"Error performing transition: {str(e)}", exc_info=True)
        return False


def initialize_entity_workflow(entity, user):
    """
    Initializes workflow for a new entity.
    
    Args:
        entity: The entity to initialize workflow for
        user: The user initializing the workflow
        
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    logger.info(f"Initializing workflow for entity: {entity}")
    
    try:
        success = initialize_workflow(entity)
        if success:
            logger.info(f"Workflow initialized successfully for entity: {entity}")
        return success
    except Exception as e:
        logger.error(f"Error initializing workflow: {str(e)}", exc_info=True)
        return False


def get_transition_history(entity, limit=None):
    """
    Gets the transition history for an entity.
    
    Args:
        entity: The entity to get history for
        limit (int): Maximum number of history records to return
        
    Returns:
        QuerySet: QuerySet of WorkflowTransitionHistory objects
    """
    try:
        content_type = ContentType.objects.get_for_model(entity)
        history = WorkflowTransitionHistory.objects.filter(
            content_type=content_type,
            object_id=entity.id
        ).order_by('-transition_date')
        
        if limit:
            history = history[:limit]
            
        return history
    except Exception as e:
        logger.error(f"Error getting transition history: {str(e)}", exc_info=True)
        return WorkflowTransitionHistory.objects.none()


def create_workflow_task(entity, task_type, description, assigned_to, due_date=None):
    """
    Creates a workflow task for an entity.
    
    Args:
        entity: The entity to create a task for
        task_type (str): The type of task
        description (str): Description of the task
        assigned_to: The user assigned to the task
        due_date (datetime): The due date for the task
        
    Returns:
        WorkflowTask: The created task
    """
    try:
        content_type = ContentType.objects.get_for_model(entity)
        
        task = WorkflowTask(
            task_type=task_type,
            description=description,
            status=WORKFLOW_TASK_STATUS['PENDING'],
            assigned_to=assigned_to,
            due_date=due_date,
            created_at=timezone.now(),
            content_type=content_type,
            object_id=entity.id
        )
        task.save()
        
        logger.info(f"Created workflow task: {task_type} for entity: {entity.id}")
        return task
    except Exception as e:
        logger.error(f"Error creating workflow task: {str(e)}", exc_info=True)
        return None


def get_entity_tasks(entity, status=None):
    """
    Gets tasks associated with an entity.
    
    Args:
        entity: The entity to get tasks for
        status (str): Optional status to filter by
        
    Returns:
        QuerySet: QuerySet of WorkflowTask objects
    """
    try:
        content_type = ContentType.objects.get_for_model(entity)
        tasks = WorkflowTask.objects.filter(
            content_type=content_type,
            object_id=entity.id
        )
        
        if status:
            tasks = tasks.filter(status=status)
            
        return tasks.order_by('due_date')
    except Exception as e:
        logger.error(f"Error getting entity tasks: {str(e)}", exc_info=True)
        return WorkflowTask.objects.none()


def get_pending_tasks(entity):
    """
    Gets pending tasks for an entity.
    
    Args:
        entity: The entity to get pending tasks for
        
    Returns:
        QuerySet: QuerySet of pending WorkflowTask objects
    """
    return get_entity_tasks(entity, WORKFLOW_TASK_STATUS['PENDING'])


def complete_task(task_id, user, notes=None):
    """
    Marks a workflow task as completed.
    
    Args:
        task_id (UUID): The ID of the task to complete
        user: The user completing the task
        notes (str): Optional notes about the completion
        
    Returns:
        bool: True if task was completed successfully, False otherwise
    """
    try:
        task = WorkflowTask.objects.get(id=task_id)
        task.complete(user, notes)
        logger.info(f"Task {task_id} completed by user {user}")
        return True
    except WorkflowTask.DoesNotExist:
        logger.error(f"Task {task_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error completing task: {str(e)}", exc_info=True)
        return False


def cancel_task(task_id, user, reason=None):
    """
    Cancels a workflow task.
    
    Args:
        task_id (UUID): The ID of the task to cancel
        user: The user cancelling the task
        reason (str): The reason for cancellation
        
    Returns:
        bool: True if task was cancelled successfully, False otherwise
    """
    try:
        task = WorkflowTask.objects.get(id=task_id)
        task.cancel(user, reason)
        logger.info(f"Task {task_id} cancelled by user {user}")
        return True
    except WorkflowTask.DoesNotExist:
        logger.error(f"Task {task_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error cancelling task: {str(e)}", exc_info=True)
        return False


def reassign_task(task_id, new_assignee, reassigned_by, reason=None):
    """
    Reassigns a workflow task to another user.
    
    Args:
        task_id (UUID): The ID of the task to reassign
        new_assignee: The user to reassign the task to
        reassigned_by: The user making the reassignment
        reason (str): The reason for reassignment
        
    Returns:
        bool: True if task was reassigned successfully, False otherwise
    """
    try:
        task = WorkflowTask.objects.get(id=task_id)
        task.reassign(new_assignee, reassigned_by, reason)
        logger.info(f"Task {task_id} reassigned to {new_assignee} by {reassigned_by}")
        return True
    except WorkflowTask.DoesNotExist:
        logger.error(f"Task {task_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error reassigning task: {str(e)}", exc_info=True)
        return False


def get_overdue_tasks(workflow_type=None):
    """
    Gets overdue tasks across the system.
    
    Args:
        workflow_type (str): Optional workflow type to filter by
        
    Returns:
        QuerySet: QuerySet of overdue WorkflowTask objects
    """
    now = timezone.now()
    try:
        # Get tasks that are pending and past their due date
        tasks = WorkflowTask.objects.filter(
            Q(status=WORKFLOW_TASK_STATUS['PENDING']) | 
            Q(status=WORKFLOW_TASK_STATUS['IN_PROGRESS']),
            due_date__isnull=False,
            due_date__lt=now
        )
        
        # Filter by content type if workflow_type is provided
        if workflow_type:
            # This would need to be implemented based on the application's model structure
            # For now, we'll skip filtering by workflow_type
            pass
            
        return tasks.order_by('due_date')
    except Exception as e:
        logger.error(f"Error getting overdue tasks: {str(e)}", exc_info=True)
        return WorkflowTask.objects.none()


def schedule_automatic_transition(entity, to_state, reason, delay_hours):
    """
    Schedules an automatic transition to occur after a delay.
    
    Args:
        entity: The entity to transition
        to_state (str): The target state
        reason (str): The reason for the transition
        delay_hours (float): The delay in hours before the transition occurs
        
    Returns:
        AutomaticTransitionSchedule: The created schedule record
    """
    workflow_type = get_entity_workflow_type(entity)
    if not workflow_type:
        logger.error(f"Could not determine workflow type for entity: {entity}")
        return None
        
    try:
        content_type = ContentType.objects.get_for_model(entity)
        scheduled_date = timezone.now() + timezone.timedelta(hours=delay_hours)
        
        schedule = AutomaticTransitionSchedule(
            workflow_type=workflow_type,
            from_state=entity.current_state,
            to_state=to_state,
            scheduled_date=scheduled_date,
            reason=reason,
            content_type=content_type,
            object_id=entity.id
        )
        schedule.save()
        
        logger.info(f"Scheduled automatic transition to {to_state} for entity {entity.id}")
        return schedule
    except Exception as e:
        logger.error(f"Error scheduling automatic transition: {str(e)}", exc_info=True)
        return None


def process_automatic_transitions():
    """
    Processes all scheduled automatic transitions that are due.
    
    Returns:
        int: Number of transitions processed
    """
    now = timezone.now()
    processed_count = 0
    
    try:
        # Get all scheduled transitions that are due and not yet executed
        scheduled_transitions = AutomaticTransitionSchedule.objects.filter(
            scheduled_date__lte=now,
            is_executed=False
        )
        
        for schedule in scheduled_transitions:
            try:
                entity = schedule.content_object
                if not entity:
                    logger.warning(f"Entity not found for scheduled transition: {schedule.id}")
                    continue
                    
                success = perform_transition(
                    entity=entity,
                    to_state=schedule.to_state,
                    user=None,
                    reason=schedule.reason
                )
                
                if success:
                    schedule.is_executed = True
                    schedule.executed_at = timezone.now()
                    schedule.save()
                    processed_count += 1
                    logger.info(f"Processed automatic transition: {schedule.id}")
                else:
                    logger.warning(f"Failed to process automatic transition: {schedule.id}")
            except Exception as e:
                logger.error(f"Error processing transition {schedule.id}: {str(e)}", exc_info=True)
                
        return processed_count
    except Exception as e:
        logger.error(f"Error processing automatic transitions: {str(e)}", exc_info=True)
        return processed_count


def check_for_automatic_transitions(entity):
    """
    Checks if the current state should trigger an automatic transition.
    
    Args:
        entity: The entity to check for automatic transitions
        
    Returns:
        bool: True if an automatic transition was scheduled
    """
    current_state = entity.current_state
    
    # Check if current state has an automatic transition defined
    if current_state not in AUTOMATIC_TRANSITIONS:
        return False
        
    try:
        transition_config = AUTOMATIC_TRANSITIONS[current_state]
        
        # Schedule the automatic transition
        schedule = schedule_automatic_transition(
            entity=entity,
            to_state=transition_config['to_state'],
            reason=transition_config['reason'],
            delay_hours=transition_config['delay_hours']
        )
        
        return schedule is not None
    except Exception as e:
        logger.error(f"Error checking for automatic transitions: {str(e)}", exc_info=True)
        return False


def check_sla_violations():
    """
    Checks for SLA violations across all workflow entities.
    
    Returns:
        dict: Dictionary of SLA violations by workflow type
    """
    now = timezone.now()
    results = {
        WORKFLOW_TYPES['APPLICATION']: {},
        WORKFLOW_TYPES['DOCUMENT']: {},
        WORKFLOW_TYPES['FUNDING']: {}
    }
    
    try:
        # For each workflow type, query the corresponding model
        # Note: This implementation avoids circular imports by not directly importing
        # the application models. In an actual implementation, you would need to
        # either use a registry pattern or dynamic imports.
        
        for workflow_type, violations in results.items():
            # In an actual implementation, you would get the model class for each workflow type
            # and perform the query. For now, we'll just return the empty dictionary.
            pass
        
        # Log the violations
        violation_count = sum(len(states) for states in results.values())
        if violation_count > 0:
            logger.warning(f"Found {violation_count} SLA violations: {results}")
            
        return results
    except Exception as e:
        logger.error(f"Error checking SLA violations: {str(e)}", exc_info=True)
        return results


def get_sla_status(entity):
    """
    Gets the SLA status for an entity.
    
    Args:
        entity: The entity to get SLA status for
        
    Returns:
        dict: Dictionary with SLA status information
    """
    workflow_type = get_entity_workflow_type(entity)
    current_state = entity.current_state
    
    # Check if there's an SLA defined for this workflow type and state
    if (
        not workflow_type or
        workflow_type not in WORKFLOW_SLA_DEFINITIONS or
        current_state not in WORKFLOW_SLA_DEFINITIONS[workflow_type]
    ):
        return {
            'has_sla': False,
            'message': 'No SLA defined for this state'
        }
    
    try:
        sla_definition = WORKFLOW_SLA_DEFINITIONS[workflow_type][current_state]
        sla_hours = sla_definition['hours']
        description = sla_definition['description']
        
        # Calculate elapsed time since state change
        now = timezone.now()
        state_changed_at = entity.state_changed_at or now
        elapsed = now - state_changed_at
        elapsed_hours = elapsed.total_seconds() / 3600
        
        # Calculate remaining time until SLA breach
        sla_due_at = entity.sla_due_at
        if sla_due_at:
            remaining = sla_due_at - now
            remaining_hours = remaining.total_seconds() / 3600
            is_breached = remaining_hours < 0
        else:
            # If no due date is set, calculate based on state_changed_at and SLA hours
            sla_due_at = state_changed_at + timezone.timedelta(hours=sla_hours)
            remaining = sla_due_at - now
            remaining_hours = remaining.total_seconds() / 3600
            is_breached = remaining_hours < 0
        
        # Determine status
        if is_breached:
            status = 'breached'
        elif remaining_hours < sla_hours * 0.25:  # Less than 25% time remaining
            status = 'at_risk'
        else:
            status = 'on_track'
        
        return {
            'has_sla': True,
            'description': description,
            'sla_hours': sla_hours,
            'elapsed_hours': elapsed_hours,
            'remaining_hours': remaining_hours,
            'status': status,
            'state_changed_at': state_changed_at,
            'sla_due_at': sla_due_at,
            'is_breached': is_breached
        }
    except Exception as e:
        logger.error(f"Error getting SLA status: {str(e)}", exc_info=True)
        return {
            'has_sla': False,
            'error': str(e),
            'message': 'Error determining SLA status'
        }


def update_sla_due_dates():
    """
    Updates SLA due dates for entities based on their current state.
    
    Returns:
        int: Number of entities updated
    """
    updated_count = 0
    
    try:
        # For each workflow type, update entities that need SLA due dates
        # Note: This implementation avoids circular imports by not directly importing
        # the application models. In an actual implementation, you would need to
        # either use a registry pattern or dynamic imports.
        
        # In an actual implementation, the logic would iterate through each workflow type,
        # get the corresponding model, and update the SLA due dates for entities that need it.
        # For now, we'll just return 0.
        
        return updated_count
    except Exception as e:
        logger.error(f"Error updating SLA due dates: {str(e)}", exc_info=True)
        return updated_count


def get_workflow_metrics(workflow_type=None, start_date=None, end_date=None):
    """
    Gets workflow metrics for reporting and monitoring.
    
    Args:
        workflow_type (str): Optional workflow type to filter by
        start_date (datetime): Optional start date for the metrics period
        end_date (datetime): Optional end date for the metrics period
        
    Returns:
        dict: Dictionary with workflow metrics
    """
    metrics = {}
    
    try:
        # Define the date range
        if not end_date:
            end_date = timezone.now()
        if not start_date:
            start_date = end_date - timezone.timedelta(days=30)  # Default to 30 days
        
        # If workflow_type is provided, only get metrics for that type
        workflow_types = [workflow_type] if workflow_type else WORKFLOW_TYPES.values()
        
        for wf_type in workflow_types:
            type_metrics = {}
            
            # Get transition history for this workflow type in the date range
            transitions = WorkflowTransitionHistory.objects.filter(
                workflow_type=wf_type,
                transition_date__gte=start_date,
                transition_date__lte=end_date
            )
            
            # Calculate metrics based on transitions
            if transitions.exists():
                # Count transitions by type (from_state -> to_state)
                transition_counts = {}
                for t in transitions:
                    key = f"{t.from_state} -> {t.to_state}"
                    transition_counts[key] = transition_counts.get(key, 0) + 1
                
                # Calculate average time in each state
                # This would require more complex analysis of transition history
                
                # Calculate SLA compliance rates
                # This would require checking if transitions occurred within SLA
                
                type_metrics['transition_counts'] = transition_counts
                type_metrics['total_transitions'] = transitions.count()
                
                # Add more metrics as needed
            
            metrics[wf_type] = type_metrics
        
        return metrics
    except Exception as e:
        logger.error(f"Error getting workflow metrics: {str(e)}", exc_info=True)
        return metrics


class WorkflowService:
    """
    Service class for workflow operations.
    """
    
    @staticmethod
    def get_allowed_transitions(entity):
        """
        Gets the allowed next states for an entity's current state.
        
        Args:
            entity: The entity to get allowed transitions for
            
        Returns:
            list: List of allowed next states
        """
        return get_allowed_transitions(entity)
    
    @staticmethod
    def validate_transition(entity, to_state, user):
        """
        Validates if a transition from current state to target state is allowed.
        
        Args:
            entity: The entity to validate transition for
            to_state (str): The target state
            user: The user attempting the transition
            
        Returns:
            bool: True if transition is valid, False otherwise
        """
        return validate_transition(entity, to_state, user)
    
    @staticmethod
    def perform_transition(entity, to_state, user, reason=None, validate=True):
        """
        Transitions an entity to a new state with validation and error handling.
        
        Args:
            entity: The entity to transition
            to_state (str): The target state
            user: The user initiating the transition
            reason (str): The reason for the transition
            validate (bool): Whether to validate the transition first
            
        Returns:
            bool: True if transition was successful, False otherwise
        """
        return perform_transition(entity, to_state, user, reason, validate)
    
    @staticmethod
    def initialize_entity_workflow(entity, user):
        """
        Initializes workflow for a new entity.
        
        Args:
            entity: The entity to initialize workflow for
            user: The user initializing the workflow
            
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        return initialize_entity_workflow(entity, user)
    
    @staticmethod
    def get_transition_history(entity, limit=None):
        """
        Gets the transition history for an entity.
        
        Args:
            entity: The entity to get history for
            limit (int): Maximum number of history records to return
            
        Returns:
            QuerySet: QuerySet of WorkflowTransitionHistory objects
        """
        return get_transition_history(entity, limit)
    
    @staticmethod
    def create_workflow_task(entity, task_type, description, assigned_to, due_date=None):
        """
        Creates a workflow task for an entity.
        
        Args:
            entity: The entity to create a task for
            task_type (str): The type of task
            description (str): Description of the task
            assigned_to: The user assigned to the task
            due_date (datetime): The due date for the task
            
        Returns:
            WorkflowTask: The created task
        """
        return create_workflow_task(entity, task_type, description, assigned_to, due_date)
    
    @staticmethod
    def get_entity_tasks(entity, status=None):
        """
        Gets tasks associated with an entity.
        
        Args:
            entity: The entity to get tasks for
            status (str): Optional status to filter by
            
        Returns:
            QuerySet: QuerySet of WorkflowTask objects
        """
        return get_entity_tasks(entity, status)
    
    @staticmethod
    def get_pending_tasks(entity):
        """
        Gets pending tasks for an entity.
        
        Args:
            entity: The entity to get pending tasks for
            
        Returns:
            QuerySet: QuerySet of pending WorkflowTask objects
        """
        return get_pending_tasks(entity)
    
    @staticmethod
    def complete_task(task_id, user, notes=None):
        """
        Marks a workflow task as completed.
        
        Args:
            task_id (UUID): The ID of the task to complete
            user: The user completing the task
            notes (str): Optional notes about the completion
            
        Returns:
            bool: True if task was completed successfully, False otherwise
        """
        return complete_task(task_id, user, notes)
    
    @staticmethod
    def cancel_task(task_id, user, reason=None):
        """
        Cancels a workflow task.
        
        Args:
            task_id (UUID): The ID of the task to cancel
            user: The user cancelling the task
            reason (str): The reason for cancellation
            
        Returns:
            bool: True if task was cancelled successfully, False otherwise
        """
        return cancel_task(task_id, user, reason)
    
    @staticmethod
    def reassign_task(task_id, new_assignee, reassigned_by, reason=None):
        """
        Reassigns a workflow task to another user.
        
        Args:
            task_id (UUID): The ID of the task to reassign
            new_assignee: The user to reassign the task to
            reassigned_by: The user making the reassignment
            reason (str): The reason for reassignment
            
        Returns:
            bool: True if task was reassigned successfully, False otherwise
        """
        return reassign_task(task_id, new_assignee, reassigned_by, reason)
    
    @staticmethod
    def get_overdue_tasks(workflow_type=None):
        """
        Gets overdue tasks across the system.
        
        Args:
            workflow_type (str): Optional workflow type to filter by
            
        Returns:
            QuerySet: QuerySet of overdue WorkflowTask objects
        """
        return get_overdue_tasks(workflow_type)
    
    @staticmethod
    def schedule_automatic_transition(entity, to_state, reason, delay_hours):
        """
        Schedules an automatic transition to occur after a delay.
        
        Args:
            entity: The entity to transition
            to_state (str): The target state
            reason (str): The reason for the transition
            delay_hours (float): The delay in hours before the transition occurs
            
        Returns:
            AutomaticTransitionSchedule: The created schedule record
        """
        return schedule_automatic_transition(entity, to_state, reason, delay_hours)
    
    @staticmethod
    def process_automatic_transitions():
        """
        Processes all scheduled automatic transitions that are due.
        
        Returns:
            int: Number of transitions processed
        """
        return process_automatic_transitions()
    
    @staticmethod
    def check_for_automatic_transitions(entity):
        """
        Checks if the current state should trigger an automatic transition.
        
        Args:
            entity: The entity to check for automatic transitions
            
        Returns:
            bool: True if an automatic transition was scheduled
        """
        return check_for_automatic_transitions(entity)
    
    @staticmethod
    def check_sla_violations():
        """
        Checks for SLA violations across all workflow entities.
        
        Returns:
            dict: Dictionary of SLA violations by workflow type
        """
        return check_sla_violations()
    
    @staticmethod
    def get_sla_status(entity):
        """
        Gets the SLA status for an entity.
        
        Args:
            entity: The entity to get SLA status for
            
        Returns:
            dict: Dictionary with SLA status information
        """
        return get_sla_status(entity)
    
    @staticmethod
    def update_sla_due_dates():
        """
        Updates SLA due dates for entities based on their current state.
        
        Returns:
            int: Number of entities updated
        """
        return update_sla_due_dates()
    
    @staticmethod
    def get_workflow_metrics(workflow_type=None, start_date=None, end_date=None):
        """
        Gets workflow metrics for reporting and monitoring.
        
        Args:
            workflow_type (str): Optional workflow type to filter by
            start_date (datetime): Optional start date for the metrics period
            end_date (datetime): Optional end date for the metrics period
            
        Returns:
            dict: Dictionary with workflow metrics
        """
        return get_workflow_metrics(workflow_type, start_date, end_date)