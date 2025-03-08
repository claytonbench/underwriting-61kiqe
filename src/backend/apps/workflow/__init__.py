"""
Workflow app package initialization module.

This module initializes the workflow app package and exposes key components of the
workflow state machine system that manages transitions between different states
in the loan application lifecycle. It provides access to state machines, transition
handlers, workflow models, and utility functions for managing workflow states.
"""

# Version information
__version__ = "1.0.0"

# Import state machine components
from .state_machine import (
    StateMachine,
    ApplicationStateMachine,
    DocumentStateMachine,
    FundingStateMachine,
    validate_transition,
    get_transition_rules,
    get_transition_event,
    create_transition_history,
    schedule_automatic_transitions,
    create_workflow_tasks,
    process_workflow_notifications
)

# Import transition handlers
from .transitions import (
    TransitionHandler,
    ApplicationTransitionHandler,
    DocumentTransitionHandler,
    FundingTransitionHandler,
    get_transition_handler,
    handle_automatic_transitions,
    handle_document_expiration,
    handle_sla_monitoring
)

# Import workflow models
from .models import (
    WorkflowState,
    WorkflowEntity,
    WorkflowTransitionHistory,
    WorkflowTask,
    AutomaticTransitionSchedule,
    WorkflowConfiguration
)

# Import workflow constants
from .constants import (
    WORKFLOW_TYPES,
    APPLICATION_STATE_TRANSITIONS,
    TERMINAL_STATES,
    INITIAL_STATES
)

# All components are available directly from the package
# E.g., from apps.workflow import StateMachine