"""
State machine implementation for managing workflow transitions.

This module provides the core state machine functionality for managing workflow
transitions in the loan management system. It supports different workflow types
including loan applications, documents, and funding processes. The state machine
validates and executes transitions, tracks transition history, creates workflow
tasks, and handles notifications.
"""

import logging
from django.db import transaction  # Django 4.2+
from django.utils import timezone  # Django 4.2+
from django.core.exceptions import ValidationError  # Django 4.2+
from django.contrib.contenttypes.models import ContentType  # Django 4.2+

from .constants import (
    WORKFLOW_TYPES,
    APPLICATION_STATE_TRANSITIONS,
    DOCUMENT_STATE_TRANSITIONS,
    FUNDING_STATE_TRANSITIONS,
    INITIAL_STATES,
    TERMINAL_STATES,
    STATE_TRANSITION_PERMISSIONS,
    WORKFLOW_TRANSITION_EVENTS,
    WORKFLOW_NOTIFICATION_EVENTS,
    WORKFLOW_AUDIT_EVENTS,
    WORKFLOW_SLA_DEFINITIONS,
    REQUIRED_ACTIONS,
)
from .models import (
    WorkflowTransitionHistory,
    WorkflowTask,
    AutomaticTransitionSchedule,
)

# Setup logger
logger = logging.getLogger(__name__)


def create_transition_history(entity, from_state, to_state, user, reason, transition_event):
    """
    Creates a transition history record for a workflow state change.
    
    Args:
        entity: The entity being transitioned
        from_state (str): The starting state
        to_state (str): The ending state
        user: The user initiating the transition
        reason (str): The reason for the transition
        transition_event (str): The named event for this transition
        
    Returns:
        WorkflowTransitionHistory: The created transition history record
    """
    workflow_type = entity.get_workflow_type()
    content_type = ContentType.objects.get_for_model(entity)
    
    history = WorkflowTransitionHistory(
        workflow_type=workflow_type,
        from_state=from_state,
        to_state=to_state,
        transitioned_by=user,
        reason=reason,
        transition_event=transition_event,
        content_type=content_type,
        object_id=entity.id
    )
    history.save()
    
    return history


def create_workflow_tasks(entity, new_state):
    """
    Creates workflow tasks based on the entity's new state.
    
    Args:
        entity: The entity that has transitioned to a new state
        new_state (str): The new state of the entity
        
    Returns:
        list: List of created workflow tasks
    """
    workflow_type = entity.get_workflow_type()
    
    # Check if there are required actions for this state
    if new_state not in REQUIRED_ACTIONS:
        return []
    
    content_type = ContentType.objects.get_for_model(entity)
    created_tasks = []
    
    for action in REQUIRED_ACTIONS[new_state]:
        task = WorkflowTask(
            task_type=action['task_type'],
            description=action['description'],
            content_type=content_type,
            object_id=entity.id
        )
        
        # Set due date based on SLA if applicable
        if (workflow_type in WORKFLOW_SLA_DEFINITIONS and 
            new_state in WORKFLOW_SLA_DEFINITIONS[workflow_type]):
            sla_hours = WORKFLOW_SLA_DEFINITIONS[workflow_type][new_state]['hours']
            task.due_date = timezone.now() + timezone.timedelta(hours=sla_hours)
        
        task.save()
        created_tasks.append(task)
    
    return created_tasks


def process_workflow_notifications(entity, from_state, to_state, transition_event):
    """
    Processes notifications for workflow state transitions.
    
    Args:
        entity: The entity that has transitioned
        from_state (str): The starting state
        to_state (str): The ending state
        transition_event (str): The named event for this transition
        
    Returns:
        bool: True if notifications were processed successfully
    """
    # Check if this transition event should trigger notifications
    if transition_event not in WORKFLOW_NOTIFICATION_EVENTS:
        return True
    
    try:
        # Import notification service module
        # This is imported here to avoid circular imports
        from ...notifications.service import send_workflow_notification
        
        # Send notification based on the transition event
        send_workflow_notification(entity, transition_event, from_state, to_state)
        return True
    except Exception as e:
        logger.error(f"Error processing workflow notification: {str(e)}", exc_info=True)
        return False


def schedule_automatic_transition(entity, from_state, to_state, reason, delay_hours):
    """
    Schedules an automatic transition to occur after a delay.
    
    Args:
        entity: The entity to transition
        from_state (str): The starting state
        to_state (str): The ending state
        reason (str): The reason for the transition
        delay_hours (float): The delay in hours before the transition occurs
        
    Returns:
        AutomaticTransitionSchedule: The created schedule record
    """
    workflow_type = entity.get_workflow_type()
    content_type = ContentType.objects.get_for_model(entity)
    scheduled_date = timezone.now() + timezone.timedelta(hours=delay_hours)
    
    schedule = AutomaticTransitionSchedule(
        workflow_type=workflow_type,
        from_state=from_state,
        to_state=to_state,
        scheduled_date=scheduled_date,
        reason=reason,
        content_type=content_type,
        object_id=entity.id
    )
    schedule.save()
    
    return schedule


def check_automatic_transitions(entity, current_state):
    """
    Checks if the current state should trigger an automatic transition.
    
    Args:
        entity: The entity to check
        current_state (str): The current state of the entity
        
    Returns:
        bool: True if an automatic transition was scheduled
    """
    from .constants import AUTOMATIC_TRANSITIONS
    
    workflow_type = entity.get_workflow_type()
    
    # Check if this state has an automatic transition defined
    if current_state not in AUTOMATIC_TRANSITIONS:
        return False
    
    try:
        # Get the automatic transition configuration
        transition_config = AUTOMATIC_TRANSITIONS[current_state]
        
        # Schedule the automatic transition
        schedule_automatic_transition(
            entity,
            current_state,
            transition_config['to_state'],
            transition_config['reason'],
            transition_config['delay_hours']
        )
        
        return True
    except Exception as e:
        logger.error(f"Error scheduling automatic transition: {str(e)}", exc_info=True)
        return False


def get_transition_event(workflow_type, from_state, to_state):
    """
    Gets the transition event name for a state change.
    
    Args:
        workflow_type (str): The workflow type
        from_state (str): The starting state
        to_state (str): The ending state
        
    Returns:
        str: The transition event name or None if not found
    """
    for event_name, event_config in WORKFLOW_TRANSITION_EVENTS.items():
        # Check if the workflow type matches
        if event_config['workflow_type'] != workflow_type:
            continue
            
        # Check if to_state matches
        if event_config['to_state'] != to_state:
            continue
            
        # Check if from_state matches (may be a list of possible from_states)
        if isinstance(event_config['from_state'], list):
            if from_state in event_config['from_state']:
                return event_name
        elif event_config['from_state'] == from_state:
            return event_name
    
    return None


class StateMachine:
    """
    Core state machine implementation for managing workflow transitions.
    
    This class provides the functionality to manage state transitions for
    different types of workflow entities (applications, documents, funding).
    It validates transitions against defined rules, executes transitions,
    and maintains the state history.
    """
    
    def __init__(self, workflow_type):
        """
        Initializes the state machine with a specific workflow type.
        
        Args:
            workflow_type (str): The workflow type this state machine will manage
        
        Raises:
            ValueError: If an unsupported workflow_type is provided
        """
        self.workflow_type = workflow_type
        
        # Determine which state transition map to use
        if workflow_type == WORKFLOW_TYPES['APPLICATION']:
            self.state_transitions = APPLICATION_STATE_TRANSITIONS
        elif workflow_type == WORKFLOW_TYPES['DOCUMENT']:
            self.state_transitions = DOCUMENT_STATE_TRANSITIONS
        elif workflow_type == WORKFLOW_TYPES['FUNDING']:
            self.state_transitions = FUNDING_STATE_TRANSITIONS
        else:
            raise ValueError(f"Unsupported workflow type: {workflow_type}")
    
    def get_allowed_transitions(self, current_state):
        """
        Gets the allowed next states for a given current state.
        
        Args:
            current_state (str): The current state
            
        Returns:
            list: List of allowed next states
        """
        if current_state not in self.state_transitions:
            return []
        
        return self.state_transitions[current_state]
    
    def validate_transition(self, current_state, to_state, user=None):
        """
        Validates if a transition from current_state to to_state is allowed.
        
        Args:
            current_state (str): The current state
            to_state (str): The desired next state
            user: The user attempting the transition
            
        Returns:
            bool: True if transition is valid, False otherwise
        """
        # Check if current_state exists in transitions
        if current_state not in self.state_transitions:
            return False
        
        # Check if to_state is in allowed transitions
        if to_state not in self.state_transitions[current_state]:
            return False
        
        # Check if user has permission for this transition
        if user and to_state in STATE_TRANSITION_PERMISSIONS:
            user_type = getattr(user, 'user_type', None)
            if user_type not in STATE_TRANSITION_PERMISSIONS[to_state]:
                return False
        
        return True
    
    def transition(self, entity, to_state, user=None, reason=None, validate=True):
        """
        Executes a state transition for an entity.
        
        Args:
            entity: The entity to transition
            to_state (str): The desired next state
            user: The user initiating the transition
            reason (str): The reason for the transition
            validate (bool): Whether to validate the transition
            
        Returns:
            bool: True if transition was successful
            
        Raises:
            ValidationError: If transition is not valid and validate is True
        """
        current_state = entity.current_state
        
        # If already in the desired state, nothing to do
        if current_state == to_state:
            return True
        
        # Validate the transition if required
        if validate and not self.validate_transition(current_state, to_state, user):
            raise ValidationError(f"Invalid state transition from {current_state} to {to_state}")
        
        # Use a transaction to ensure data integrity
        with transaction.atomic():
            # Store the original state for history
            original_state = current_state
            
            # Update the entity state
            entity.current_state = to_state
            entity.state_changed_at = timezone.now()
            if user:
                entity.state_changed_by = user
            
            # Check if this is a terminal state
            if to_state in TERMINAL_STATES.get(self.workflow_type, []):
                entity.is_terminal = True
            
            # Save the entity
            entity.save()
            
            # Get the transition event name
            transition_event = get_transition_event(self.workflow_type, original_state, to_state)
            
            # Create transition history record
            create_transition_history(
                entity,
                original_state,
                to_state,
                user,
                reason or f"Transition from {original_state} to {to_state}",
                transition_event
            )
            
            # Create workflow tasks based on new state
            create_workflow_tasks(entity, to_state)
            
            # Process notifications
            if transition_event:
                process_workflow_notifications(entity, original_state, to_state, transition_event)
            
            # Check for automatic transitions
            check_automatic_transitions(entity, to_state)
            
            # Update SLA due date
            if hasattr(entity, 'update_sla_due_date'):
                entity.update_sla_due_date()
        
        return True
    
    def get_initial_state(self):
        """
        Gets the initial state for this workflow type.
        
        Returns:
            str: The initial state for this workflow type
        """
        return INITIAL_STATES[self.workflow_type]
    
    def is_terminal_state(self, state):
        """
        Checks if a state is a terminal state for this workflow type.
        
        Args:
            state (str): The state to check
            
        Returns:
            bool: True if the state is terminal, False otherwise
        """
        return state in TERMINAL_STATES.get(self.workflow_type, [])