"""
Unit tests for the workflow services module.

This module contains tests for workflow state transitions, task management, and SLA monitoring.
It verifies the behavior of service functions for managing workflow operations across
different entity types in the loan management system.
"""

import datetime
import uuid
import pytest
from unittest.mock import MagicMock, patch, call
from django.test import TestCase
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from ..constants import (
    WORKFLOW_TYPES,
    WORKFLOW_TASK_TYPES,
    WORKFLOW_TASK_STATUS,
    WORKFLOW_SLA_DEFINITIONS,
)
from ...utils.constants import (
    APPLICATION_STATUS,
    DOCUMENT_STATUS,
    FUNDING_STATUS,
)
from ..models import (
    WorkflowTransitionHistory,
    WorkflowTask,
    AutomaticTransitionSchedule,
    WorkflowEntity
)
from ..services import (
    get_entity_workflow_type,
    get_allowed_transitions,
    validate_transition,
    perform_transition,
    initialize_entity_workflow,
    get_transition_history,
    create_workflow_task,
    get_entity_tasks,
    get_pending_tasks,
    complete_task,
    cancel_task,
    reassign_task,
    get_overdue_tasks,
    schedule_automatic_transition,
    process_automatic_transitions,
    check_for_automatic_transitions,
    check_sla_violations,
    get_sla_status,
    update_sla_due_dates,
    get_workflow_metrics,
    WorkflowService
)
from ..state_machine import StateMachine
from ..transitions import TransitionHandlerFactory


def setup_module():
    """Setup function that runs once before all tests in the module."""
    pass


def teardown_module():
    """Teardown function that runs once after all tests in the module."""
    pass


@pytest.fixture
def mock_entity(workflow_type, current_state):
    """
    Creates a mock entity for testing workflow services.
    
    Args:
        workflow_type: Workflow type string
        current_state: Current state string
        
    Returns:
        A mock entity with workflow-related attributes
    """
    entity = MagicMock()
    entity.id = uuid.uuid4()
    entity.current_state = current_state
    entity.state_changed_at = timezone.now()
    entity.is_terminal = False
    entity.get_workflow_type = MagicMock(return_value=workflow_type)
    entity.update_sla_due_date = MagicMock()
    return entity


@pytest.fixture
def mock_user(user_type="system_admin"):
    """
    Creates a mock user for testing workflow services.
    
    Args:
        user_type: User type string
        
    Returns:
        A mock user with necessary attributes
    """
    user = MagicMock()
    user.id = uuid.uuid4()
    user.user_type = user_type
    return user


@pytest.fixture
def mock_content_type():
    """
    Creates a mock content type for testing generic relations.
    
    Returns:
        A mock content type
    """
    content_type = MagicMock(spec=ContentType)
    content_type.id = 1
    return content_type


class TestGetEntityWorkflowType:
    """Tests for the get_entity_workflow_type function."""
    
    def test_get_entity_workflow_type_with_method(self):
        """Tests that get_entity_workflow_type uses the entity's get_workflow_type method if available."""
        # Create entity with get_workflow_type method
        entity = MagicMock()
        entity.get_workflow_type = MagicMock(return_value=WORKFLOW_TYPES['APPLICATION'])
        
        # Call the function
        result = get_entity_workflow_type(entity)
        
        # Verify result
        assert result == WORKFLOW_TYPES['APPLICATION']
        entity.get_workflow_type.assert_called_once()
    
    def test_get_entity_workflow_type_by_class_name(self):
        """Tests that get_entity_workflow_type determines workflow type based on class name."""
        # Test with Application in class name
        entity = MagicMock(__class__=MagicMock(__name__='LoanApplication'))
        delattr(entity, 'get_workflow_type')
        result = get_entity_workflow_type(entity)
        assert result == WORKFLOW_TYPES['APPLICATION']
        
        # Test with Document in class name
        entity = MagicMock(__class__=MagicMock(__name__='Document'))
        delattr(entity, 'get_workflow_type')
        result = get_entity_workflow_type(entity)
        assert result == WORKFLOW_TYPES['DOCUMENT']
        
        # Test with Funding in class name
        entity = MagicMock(__class__=MagicMock(__name__='FundingRequest'))
        delattr(entity, 'get_workflow_type')
        result = get_entity_workflow_type(entity)
        assert result == WORKFLOW_TYPES['FUNDING']
    
    def test_get_entity_workflow_type_unknown(self):
        """Tests that get_entity_workflow_type returns None for unknown entity types."""
        entity = MagicMock(__class__=MagicMock(__name__='UnknownEntity'))
        delattr(entity, 'get_workflow_type')
        result = get_entity_workflow_type(entity)
        assert result is None


class TestGetAllowedTransitions:
    """Tests for the get_allowed_transitions function."""
    
    @patch('src.backend.apps.workflow.services.StateMachine')
    def test_get_allowed_transitions_application(self, mock_state_machine_class):
        """Tests getting allowed transitions for an application entity."""
        # Setup
        mock_application = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['DRAFT'])
        mock_state_machine = mock_state_machine_class.return_value
        mock_state_machine.get_allowed_transitions.return_value = [
            APPLICATION_STATUS['SUBMITTED'], 
            APPLICATION_STATUS['ABANDONED']
        ]
        
        # Call function
        result = get_allowed_transitions(mock_application)
        
        # Verify
        mock_state_machine_class.assert_called_once_with(WORKFLOW_TYPES['APPLICATION'])
        mock_state_machine.get_allowed_transitions.assert_called_once_with(APPLICATION_STATUS['DRAFT'])
        assert result == [APPLICATION_STATUS['SUBMITTED'], APPLICATION_STATUS['ABANDONED']]
    
    @patch('src.backend.apps.workflow.services.StateMachine')
    def test_get_allowed_transitions_document(self, mock_state_machine_class):
        """Tests getting allowed transitions for a document entity."""
        # Setup
        mock_document = mock_entity(WORKFLOW_TYPES['DOCUMENT'], DOCUMENT_STATUS['DRAFT'])
        mock_state_machine = mock_state_machine_class.return_value
        mock_state_machine.get_allowed_transitions.return_value = [DOCUMENT_STATUS['GENERATED']]
        
        # Call function
        result = get_allowed_transitions(mock_document)
        
        # Verify
        mock_state_machine_class.assert_called_once_with(WORKFLOW_TYPES['DOCUMENT'])
        mock_state_machine.get_allowed_transitions.assert_called_once_with(DOCUMENT_STATUS['DRAFT'])
        assert result == [DOCUMENT_STATUS['GENERATED']]
    
    @patch('src.backend.apps.workflow.services.StateMachine')
    def test_get_allowed_transitions_funding(self, mock_state_machine_class):
        """Tests getting allowed transitions for a funding entity."""
        # Setup
        mock_funding = mock_entity(WORKFLOW_TYPES['FUNDING'], FUNDING_STATUS['PENDING_ENROLLMENT'])
        mock_state_machine = mock_state_machine_class.return_value
        mock_state_machine.get_allowed_transitions.return_value = [FUNDING_STATUS['ENROLLMENT_VERIFIED']]
        
        # Call function
        result = get_allowed_transitions(mock_funding)
        
        # Verify
        mock_state_machine_class.assert_called_once_with(WORKFLOW_TYPES['FUNDING'])
        mock_state_machine.get_allowed_transitions.assert_called_once_with(FUNDING_STATUS['PENDING_ENROLLMENT'])
        assert result == [FUNDING_STATUS['ENROLLMENT_VERIFIED']]
    
    def test_get_allowed_transitions_unknown_type(self):
        """Tests that get_allowed_transitions returns an empty list for unknown entity types."""
        # Setup
        mock_unknown = MagicMock()
        mock_unknown.get_workflow_type = MagicMock(return_value=None)
        
        # Call function
        result = get_allowed_transitions(mock_unknown)
        
        # Verify
        assert result == []


class TestValidateTransition:
    """Tests for the validate_transition function."""
    
    @patch('src.backend.apps.workflow.services.TransitionHandlerFactory')
    def test_validate_transition_valid(self, mock_factory):
        """Tests validation of a valid transition."""
        # Setup
        entity = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['DRAFT'])
        user = mock_user()
        mock_handler = MagicMock()
        mock_handler.validate_transition.return_value = True
        mock_factory.get_handler_for_entity.return_value = mock_handler
        
        # Call function
        result = validate_transition(entity, APPLICATION_STATUS['SUBMITTED'], user)
        
        # Verify
        mock_factory.get_handler_for_entity.assert_called_once_with(entity)
        mock_handler.validate_transition.assert_called_once_with(entity, APPLICATION_STATUS['SUBMITTED'], user)
        assert result is True
    
    @patch('src.backend.apps.workflow.services.TransitionHandlerFactory')
    def test_validate_transition_invalid(self, mock_factory):
        """Tests validation of an invalid transition."""
        # Setup
        entity = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['DRAFT'])
        user = mock_user()
        mock_handler = MagicMock()
        mock_handler.validate_transition.return_value = False
        mock_factory.get_handler_for_entity.return_value = mock_handler
        
        # Call function
        result = validate_transition(entity, APPLICATION_STATUS['IN_REVIEW'], user)
        
        # Verify
        mock_factory.get_handler_for_entity.assert_called_once_with(entity)
        mock_handler.validate_transition.assert_called_once_with(entity, APPLICATION_STATUS['IN_REVIEW'], user)
        assert result is False
    
    def test_validate_transition_unknown_type(self):
        """Tests validation with an unknown entity type."""
        # Setup
        entity = MagicMock()
        entity.get_workflow_type = MagicMock(return_value=None)
        user = mock_user()
        
        # Call function
        result = validate_transition(entity, "SOME_STATE", user)
        
        # Verify
        assert result is False


class TestPerformTransition:
    """Tests for the perform_transition function."""
    
    @patch('src.backend.apps.workflow.services.transition_entity')
    def test_perform_transition_success(self, mock_transition_entity):
        """Tests successful transition execution."""
        # Setup
        entity = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['DRAFT'])
        user = mock_user()
        reason = "Test transition"
        mock_transition_entity.return_value = True
        
        # Call function
        result = perform_transition(entity, APPLICATION_STATUS['SUBMITTED'], user, reason)
        
        # Verify
        mock_transition_entity.assert_called_once_with(entity, APPLICATION_STATUS['SUBMITTED'], user, reason)
        assert result is True
    
    @patch('src.backend.apps.workflow.services.transition_entity')
    @patch('src.backend.apps.workflow.services.validate_transition')
    def test_perform_transition_with_validation(self, mock_validate, mock_transition_entity):
        """Tests transition with validation."""
        # Setup
        entity = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['DRAFT'])
        user = mock_user()
        reason = "Test transition"
        mock_validate.return_value = True
        mock_transition_entity.return_value = True
        
        # Call function
        result = perform_transition(entity, APPLICATION_STATUS['SUBMITTED'], user, reason, validate=True)
        
        # Verify
        mock_validate.assert_called_once_with(entity, APPLICATION_STATUS['SUBMITTED'], user)
        mock_transition_entity.assert_called_once_with(entity, APPLICATION_STATUS['SUBMITTED'], user, reason)
        assert result is True
    
    @patch('src.backend.apps.workflow.services.transition_entity')
    @patch('src.backend.apps.workflow.services.validate_transition')
    def test_perform_transition_validation_fails(self, mock_validate, mock_transition_entity):
        """Tests transition when validation fails."""
        # Setup
        entity = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['DRAFT'])
        user = mock_user()
        reason = "Test transition"
        mock_validate.return_value = False
        
        # Call function
        result = perform_transition(entity, APPLICATION_STATUS['SUBMITTED'], user, reason, validate=True)
        
        # Verify
        mock_validate.assert_called_once_with(entity, APPLICATION_STATUS['SUBMITTED'], user)
        mock_transition_entity.assert_not_called()
        assert result is False
    
    @patch('src.backend.apps.workflow.services.transition_entity')
    def test_perform_transition_exception(self, mock_transition_entity):
        """Tests transition when an exception occurs."""
        # Setup
        entity = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['DRAFT'])
        user = mock_user()
        reason = "Test transition"
        mock_transition_entity.side_effect = Exception("Test exception")
        
        # Call function
        result = perform_transition(entity, APPLICATION_STATUS['SUBMITTED'], user, reason)
        
        # Verify
        mock_transition_entity.assert_called_once_with(entity, APPLICATION_STATUS['SUBMITTED'], user, reason)
        assert result is False


class TestInitializeEntityWorkflow:
    """Tests for the initialize_entity_workflow function."""
    
    @patch('src.backend.apps.workflow.services.initialize_workflow')
    def test_initialize_entity_workflow_success(self, mock_initialize_workflow):
        """Tests successful workflow initialization."""
        # Setup
        entity = mock_entity(WORKFLOW_TYPES['APPLICATION'], None)
        user = mock_user()
        mock_initialize_workflow.return_value = True
        
        # Call function
        result = initialize_entity_workflow(entity, user)
        
        # Verify
        mock_initialize_workflow.assert_called_once_with(entity)
        assert result is True
    
    @patch('src.backend.apps.workflow.services.initialize_workflow')
    def test_initialize_entity_workflow_exception(self, mock_initialize_workflow):
        """Tests workflow initialization when an exception occurs."""
        # Setup
        entity = mock_entity(WORKFLOW_TYPES['APPLICATION'], None)
        user = mock_user()
        mock_initialize_workflow.side_effect = Exception("Test exception")
        
        # Call function
        result = initialize_entity_workflow(entity, user)
        
        # Verify
        mock_initialize_workflow.assert_called_once_with(entity)
        assert result is False


class TestGetTransitionHistory:
    """Tests for the get_transition_history function."""
    
    @patch('src.backend.apps.workflow.services.ContentType.objects.get_for_model')
    @patch('src.backend.apps.workflow.services.WorkflowTransitionHistory.objects.filter')
    def test_get_transition_history(self, mock_filter, mock_get_for_model):
        """Tests retrieving transition history for an entity."""
        # Setup
        entity = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['DRAFT'])
        mock_content_type = mock_content_type()
        mock_get_for_model.return_value = mock_content_type
        mock_queryset = MagicMock()
        mock_filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        
        # Call function
        result = get_transition_history(entity)
        
        # Verify
        mock_get_for_model.assert_called_once_with(entity.__class__)
        mock_filter.assert_called_once_with(content_type=mock_content_type, object_id=entity.id)
        mock_queryset.order_by.assert_called_once_with('-transition_date')
        assert result == mock_queryset
    
    @patch('src.backend.apps.workflow.services.ContentType.objects.get_for_model')
    @patch('src.backend.apps.workflow.services.WorkflowTransitionHistory.objects.filter')
    def test_get_transition_history_with_limit(self, mock_filter, mock_get_for_model):
        """Tests retrieving transition history with a limit."""
        # Setup
        entity = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['DRAFT'])
        mock_content_type = mock_content_type()
        mock_get_for_model.return_value = mock_content_type
        mock_queryset = MagicMock()
        mock_filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        limited_queryset = MagicMock()
        mock_queryset.__getitem__.return_value = limited_queryset
        
        # Call function
        result = get_transition_history(entity, limit=5)
        
        # Verify
        mock_get_for_model.assert_called_once_with(entity.__class__)
        mock_filter.assert_called_once_with(content_type=mock_content_type, object_id=entity.id)
        mock_queryset.order_by.assert_called_once_with('-transition_date')
        mock_queryset.__getitem__.assert_called_once_with(slice(None, 5, None))
        assert result == limited_queryset


class TestWorkflowTaskFunctions:
    """Tests for workflow task-related functions."""
    
    @patch('src.backend.apps.workflow.services.ContentType.objects.get_for_model')
    @patch('src.backend.apps.workflow.services.WorkflowTask.objects.create')
    def test_create_workflow_task(self, mock_create, mock_get_for_model):
        """Tests creating a workflow task."""
        # Setup
        entity = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['DRAFT'])
        task_type = WORKFLOW_TASK_TYPES['DOCUMENT_UPLOAD']
        description = "Upload required documents"
        assigned_to = mock_user()
        due_date = timezone.now() + timezone.timedelta(days=7)
        mock_content_type = mock_content_type()
        mock_get_for_model.return_value = mock_content_type
        mock_task = MagicMock()
        mock_create.return_value = mock_task
        
        # Call function
        result = create_workflow_task(entity, task_type, description, assigned_to, due_date)
        
        # Verify
        mock_get_for_model.assert_called_once_with(entity)
        mock_create.assert_called_once_with(
            task_type=task_type,
            description=description,
            status=WORKFLOW_TASK_STATUS['PENDING'],
            assigned_to=assigned_to,
            due_date=due_date,
            created_at=timezone.now(),
            content_type=mock_content_type,
            object_id=entity.id
        )
        assert result == mock_task
    
    @patch('src.backend.apps.workflow.services.ContentType.objects.get_for_model')
    @patch('src.backend.apps.workflow.services.WorkflowTask.objects.filter')
    def test_get_entity_tasks(self, mock_filter, mock_get_for_model):
        """Tests retrieving tasks for an entity."""
        # Setup
        entity = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['DRAFT'])
        mock_content_type = mock_content_type()
        mock_get_for_model.return_value = mock_content_type
        mock_queryset = MagicMock()
        mock_filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        
        # Call function
        result = get_entity_tasks(entity)
        
        # Verify
        mock_get_for_model.assert_called_once_with(entity)
        mock_filter.assert_called_once_with(content_type=mock_content_type, object_id=entity.id)
        mock_queryset.order_by.assert_called_once_with('due_date')
        assert result == mock_queryset
    
    @patch('src.backend.apps.workflow.services.ContentType.objects.get_for_model')
    @patch('src.backend.apps.workflow.services.WorkflowTask.objects.filter')
    def test_get_entity_tasks_with_status(self, mock_filter, mock_get_for_model):
        """Tests retrieving tasks for an entity with a specific status."""
        # Setup
        entity = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['DRAFT'])
        status = WORKFLOW_TASK_STATUS['PENDING']
        mock_content_type = mock_content_type()
        mock_get_for_model.return_value = mock_content_type
        mock_queryset = MagicMock()
        mock_filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        
        # Call function
        result = get_entity_tasks(entity, status)
        
        # Verify
        mock_get_for_model.assert_called_once_with(entity)
        mock_filter.assert_called_once_with(
            content_type=mock_content_type, 
            object_id=entity.id,
            status=status
        )
        mock_queryset.order_by.assert_called_once_with('due_date')
        assert result == mock_queryset
    
    @patch('src.backend.apps.workflow.services.get_entity_tasks')
    def test_get_pending_tasks(self, mock_get_entity_tasks):
        """Tests retrieving pending tasks for an entity."""
        # Setup
        entity = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['DRAFT'])
        mock_tasks = MagicMock()
        mock_get_entity_tasks.return_value = mock_tasks
        
        # Call function
        result = get_pending_tasks(entity)
        
        # Verify
        mock_get_entity_tasks.assert_called_once_with(entity, WORKFLOW_TASK_STATUS['PENDING'])
        assert result == mock_tasks
    
    @patch('src.backend.apps.workflow.services.WorkflowTask.objects.get')
    def test_complete_task(self, mock_get):
        """Tests completing a workflow task."""
        # Setup
        task_id = uuid.uuid4()
        user = mock_user()
        notes = "Task completed successfully"
        mock_task = MagicMock()
        mock_get.return_value = mock_task
        
        # Call function
        result = complete_task(task_id, user, notes)
        
        # Verify
        mock_get.assert_called_once_with(id=task_id)
        mock_task.complete.assert_called_once_with(user, notes)
        assert result is True
    
    @patch('src.backend.apps.workflow.services.WorkflowTask.objects.get')
    def test_complete_task_not_found(self, mock_get):
        """Tests completing a task that doesn't exist."""
        # Setup
        task_id = uuid.uuid4()
        user = mock_user()
        notes = "Task completed successfully"
        mock_get.side_effect = WorkflowTask.DoesNotExist()
        
        # Call function
        result = complete_task(task_id, user, notes)
        
        # Verify
        mock_get.assert_called_once_with(id=task_id)
        assert result is False
    
    @patch('src.backend.apps.workflow.services.WorkflowTask.objects.get')
    def test_cancel_task(self, mock_get):
        """Tests cancelling a workflow task."""
        # Setup
        task_id = uuid.uuid4()
        user = mock_user()
        reason = "Task no longer needed"
        mock_task = MagicMock()
        mock_get.return_value = mock_task
        
        # Call function
        result = cancel_task(task_id, user, reason)
        
        # Verify
        mock_get.assert_called_once_with(id=task_id)
        mock_task.cancel.assert_called_once_with(user, reason)
        assert result is True
    
    @patch('src.backend.apps.workflow.services.WorkflowTask.objects.get')
    def test_cancel_task_not_found(self, mock_get):
        """Tests cancelling a task that doesn't exist."""
        # Setup
        task_id = uuid.uuid4()
        user = mock_user()
        reason = "Task no longer needed"
        mock_get.side_effect = WorkflowTask.DoesNotExist()
        
        # Call function
        result = cancel_task(task_id, user, reason)
        
        # Verify
        mock_get.assert_called_once_with(id=task_id)
        assert result is False
    
    @patch('src.backend.apps.workflow.services.WorkflowTask.objects.get')
    def test_reassign_task(self, mock_get):
        """Tests reassigning a workflow task."""
        # Setup
        task_id = uuid.uuid4()
        new_assignee = mock_user("underwriter")
        reassigned_by = mock_user("system_admin")
        reason = "Workload balancing"
        mock_task = MagicMock()
        mock_get.return_value = mock_task
        
        # Call function
        result = reassign_task(task_id, new_assignee, reassigned_by, reason)
        
        # Verify
        mock_get.assert_called_once_with(id=task_id)
        mock_task.reassign.assert_called_once_with(new_assignee, reassigned_by, reason)
        assert result is True
    
    @patch('src.backend.apps.workflow.services.WorkflowTask.objects.get')
    def test_reassign_task_not_found(self, mock_get):
        """Tests reassigning a task that doesn't exist."""
        # Setup
        task_id = uuid.uuid4()
        new_assignee = mock_user("underwriter")
        reassigned_by = mock_user("system_admin")
        reason = "Workload balancing"
        mock_get.side_effect = WorkflowTask.DoesNotExist()
        
        # Call function
        result = reassign_task(task_id, new_assignee, reassigned_by, reason)
        
        # Verify
        mock_get.assert_called_once_with(id=task_id)
        assert result is False
    
    @patch('src.backend.apps.workflow.services.timezone.now')
    @patch('src.backend.apps.workflow.services.WorkflowTask.objects.filter')
    def test_get_overdue_tasks(self, mock_filter, mock_now):
        """Tests retrieving overdue tasks."""
        # Setup
        now = timezone.now()
        mock_now.return_value = now
        mock_queryset = MagicMock()
        mock_filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        
        # Call function
        result = get_overdue_tasks()
        
        # Verify
        mock_filter.assert_called_once()
        mock_queryset.order_by.assert_called_once_with('due_date')
        assert result == mock_queryset
    
    @patch('src.backend.apps.workflow.services.timezone.now')
    @patch('src.backend.apps.workflow.services.ContentType.objects.filter')
    @patch('src.backend.apps.workflow.services.WorkflowTask.objects.filter')
    def test_get_overdue_tasks_with_workflow_type(self, mock_task_filter, mock_ct_filter, mock_now):
        """Tests retrieving overdue tasks for a specific workflow type."""
        # Setup
        workflow_type = WORKFLOW_TYPES['APPLICATION']
        now = timezone.now()
        mock_now.return_value = now
        mock_content_types = MagicMock()
        mock_ct_filter.return_value = mock_content_types
        mock_queryset = MagicMock()
        mock_task_filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        
        # Call function
        result = get_overdue_tasks(workflow_type)
        
        # Verify
        mock_task_filter.assert_called_once()
        mock_queryset.order_by.assert_called_once_with('due_date')
        assert result == mock_queryset


class TestAutomaticTransitionFunctions:
    """Tests for automatic transition-related functions."""
    
    @patch('src.backend.apps.workflow.services.get_entity_workflow_type')
    @patch('src.backend.apps.workflow.services.ContentType.objects.get_for_model')
    @patch('src.backend.apps.workflow.services.timezone.now')
    @patch('src.backend.apps.workflow.services.AutomaticTransitionSchedule.objects.create')
    def test_schedule_automatic_transition(self, mock_create, mock_now, mock_get_for_model, mock_get_workflow_type):
        """Tests scheduling an automatic transition."""
        # Setup
        entity = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['DRAFT'])
        to_state = APPLICATION_STATUS['SUBMITTED']
        reason = "Test transition"
        delay_hours = 24
        workflow_type = WORKFLOW_TYPES['APPLICATION']
        mock_get_workflow_type.return_value = workflow_type
        mock_content_type = mock_content_type()
        mock_get_for_model.return_value = mock_content_type
        now = timezone.now()
        mock_now.return_value = now
        scheduled_date = now + timezone.timedelta(hours=delay_hours)
        mock_schedule = MagicMock()
        mock_create.return_value = mock_schedule
        
        # Call function
        result = schedule_automatic_transition(entity, to_state, reason, delay_hours)
        
        # Verify
        mock_get_workflow_type.assert_called_once_with(entity)
        mock_get_for_model.assert_called_once_with(entity)
        mock_create.assert_called_once_with(
            workflow_type=workflow_type,
            from_state=entity.current_state,
            to_state=to_state,
            scheduled_date=scheduled_date,
            reason=reason,
            content_type=mock_content_type,
            object_id=entity.id
        )
        assert result == mock_schedule
    
    @patch('src.backend.apps.workflow.services.get_entity_workflow_type')
    def test_schedule_automatic_transition_unknown_type(self, mock_get_workflow_type):
        """Tests scheduling an automatic transition for an unknown entity type."""
        # Setup
        entity = MagicMock()
        to_state = "SOME_STATE"
        reason = "Test transition"
        delay_hours = 24
        mock_get_workflow_type.return_value = None
        
        # Call function
        result = schedule_automatic_transition(entity, to_state, reason, delay_hours)
        
        # Verify
        mock_get_workflow_type.assert_called_once_with(entity)
        assert result is None
    
    @patch('src.backend.apps.workflow.services.timezone.now')
    @patch('src.backend.apps.workflow.services.AutomaticTransitionSchedule.objects.filter')
    @patch('src.backend.apps.workflow.services.perform_transition')
    def test_process_automatic_transitions(self, mock_perform_transition, mock_filter, mock_now):
        """Tests processing scheduled automatic transitions."""
        # Setup
        now = timezone.now()
        mock_now.return_value = now
        
        # Create mock scheduled transitions
        schedule1 = MagicMock()
        schedule1.content_object = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['DRAFT'])
        schedule1.to_state = APPLICATION_STATUS['SUBMITTED']
        schedule1.reason = "Test transition 1"
        
        schedule2 = MagicMock()
        schedule2.content_object = mock_entity(WORKFLOW_TYPES['DOCUMENT'], DOCUMENT_STATUS['DRAFT'])
        schedule2.to_state = DOCUMENT_STATUS['GENERATED']
        schedule2.reason = "Test transition 2"
        
        mock_filter.return_value = [schedule1, schedule2]
        mock_perform_transition.return_value = True
        
        # Call function
        result = process_automatic_transitions()
        
        # Verify
        mock_filter.assert_called_once_with(
            scheduled_date__lte=now,
            is_executed=False
        )
        
        assert mock_perform_transition.call_count == 2
        mock_perform_transition.assert_has_calls([
            call(entity=schedule1.content_object, to_state=schedule1.to_state, user=None, reason=schedule1.reason),
            call(entity=schedule2.content_object, to_state=schedule2.to_state, user=None, reason=schedule2.reason)
        ])
        
        assert schedule1.is_executed is True
        assert schedule2.is_executed is True
        assert result == 2
    
    @patch('src.backend.apps.workflow.services.timezone.now')
    @patch('src.backend.apps.workflow.services.AutomaticTransitionSchedule.objects.filter')
    @patch('src.backend.apps.workflow.services.perform_transition')
    def test_process_automatic_transitions_with_errors(self, mock_perform_transition, mock_filter, mock_now):
        """Tests processing automatic transitions when errors occur."""
        # Setup
        now = timezone.now()
        mock_now.return_value = now
        
        # Create mock scheduled transitions
        schedule1 = MagicMock()
        schedule1.content_object = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['DRAFT'])
        schedule1.to_state = APPLICATION_STATUS['SUBMITTED']
        schedule1.reason = "Test transition 1"
        
        schedule2 = MagicMock()
        schedule2.content_object = mock_entity(WORKFLOW_TYPES['DOCUMENT'], DOCUMENT_STATUS['DRAFT'])
        schedule2.to_state = DOCUMENT_STATUS['GENERATED']
        schedule2.reason = "Test transition 2"
        
        mock_filter.return_value = [schedule1, schedule2]
        
        # First transition succeeds, second fails
        mock_perform_transition.side_effect = [True, Exception("Test exception")]
        
        # Call function
        result = process_automatic_transitions()
        
        # Verify
        mock_filter.assert_called_once_with(
            scheduled_date__lte=now,
            is_executed=False
        )
        
        assert mock_perform_transition.call_count == 2
        
        # Only first schedule should be marked as executed
        assert schedule1.is_executed is True
        assert schedule2.is_executed is False
        assert result == 1
    
    @patch('src.backend.apps.workflow.services.schedule_automatic_transition')
    def test_check_for_automatic_transitions(self, mock_schedule_transition):
        """Tests checking if a state should trigger an automatic transition."""
        # Setup from constants.py: AUTOMATIC_TRANSITIONS
        # For testing, we'll use APPLICATION_STATUS['APPROVED'] which has an automatic transition
        entity = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['APPROVED'])
        mock_schedule = MagicMock()
        mock_schedule_transition.return_value = mock_schedule
        
        # Call function
        result = check_for_automatic_transitions(entity)
        
        # Verify
        mock_schedule_transition.assert_called_once()
        assert result is True
    
    @patch('src.backend.apps.workflow.services.schedule_automatic_transition')
    def test_check_for_automatic_transitions_no_transition(self, mock_schedule_transition):
        """Tests checking for automatic transitions when none are defined."""
        # Setup with a state that doesn't have an automatic transition defined
        entity = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['SUBMITTED'])
        
        # Call function
        result = check_for_automatic_transitions(entity)
        
        # Verify
        mock_schedule_transition.assert_not_called()
        assert result is False


class TestSLAFunctions:
    """Tests for SLA-related functions."""
    
    @patch('src.backend.apps.workflow.services.timezone.now')
    def test_check_sla_violations(self, mock_now):
        """Tests checking for SLA violations."""
        # Setup
        now = timezone.now()
        mock_now.return_value = now
        
        # Since check_sla_violations is implemented as a placeholder that avoids circular imports,
        # we're primarily testing that it returns the expected structure
        result = check_sla_violations()
        
        # Verify structure
        assert isinstance(result, dict)
        assert WORKFLOW_TYPES['APPLICATION'] in result
        assert WORKFLOW_TYPES['DOCUMENT'] in result
        assert WORKFLOW_TYPES['FUNDING'] in result
    
    def test_get_sla_status_on_track(self):
        """Tests getting SLA status for an entity that is on track."""
        # Setup
        entity = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['SUBMITTED'])
        # SLA for this state is 24 hours
        entity.state_changed_at = timezone.now() - timezone.timedelta(hours=1)  # Changed 1 hour ago
        entity.sla_due_at = entity.state_changed_at + timezone.timedelta(hours=24)  # Due in 23 hours
        
        # Call function
        result = get_sla_status(entity)
        
        # Verify
        assert result['has_sla'] is True
        assert result['status'] == 'on_track'
        assert result['is_breached'] is False
    
    def test_get_sla_status_at_risk(self):
        """Tests getting SLA status for an entity that is at risk of breaching."""
        # Setup
        entity = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['SUBMITTED'])
        # SLA for this state is 24 hours
        entity.state_changed_at = timezone.now() - timezone.timedelta(hours=20)  # Changed 20 hours ago
        entity.sla_due_at = entity.state_changed_at + timezone.timedelta(hours=24)  # Due in 4 hours
        
        # Call function
        result = get_sla_status(entity)
        
        # Verify
        assert result['has_sla'] is True
        assert result['status'] == 'at_risk'
        assert result['is_breached'] is False
    
    def test_get_sla_status_breached(self):
        """Tests getting SLA status for an entity that has breached its SLA."""
        # Setup
        entity = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['SUBMITTED'])
        # SLA for this state is 24 hours
        entity.state_changed_at = timezone.now() - timezone.timedelta(hours=25)  # Changed 25 hours ago
        entity.sla_due_at = entity.state_changed_at + timezone.timedelta(hours=24)  # Overdue by 1 hour
        
        # Call function
        result = get_sla_status(entity)
        
        # Verify
        assert result['has_sla'] is True
        assert result['status'] == 'breached'
        assert result['is_breached'] is True
    
    def test_get_sla_status_no_sla(self):
        """Tests getting SLA status for an entity with no SLA defined."""
        # Setup
        # Use a state that doesn't have an SLA definition
        entity = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['DRAFT'])
        
        # Call function
        result = get_sla_status(entity)
        
        # Verify
        assert result['has_sla'] is False
    
    def test_update_sla_due_dates(self):
        """Tests updating SLA due dates for entities."""
        # Since update_sla_due_dates is implemented as a placeholder that avoids circular imports,
        # we're primarily testing that it returns an integer
        result = update_sla_due_dates()
        
        # Verify
        assert isinstance(result, int)


class TestWorkflowMetrics:
    """Tests for workflow metrics functions."""
    
    @patch('src.backend.apps.workflow.services.WorkflowTransitionHistory.objects.filter')
    def test_get_workflow_metrics(self, mock_filter):
        """Tests retrieving workflow metrics."""
        # Setup
        workflow_type = WORKFLOW_TYPES['APPLICATION']
        start_date = timezone.now() - timezone.timedelta(days=30)
        end_date = timezone.now()
        mock_transitions = MagicMock()
        mock_filter.return_value = mock_transitions
        
        # Call function
        result = get_workflow_metrics(workflow_type, start_date, end_date)
        
        # Verify
        assert isinstance(result, dict)
        mock_filter.assert_called_once()
    
    @patch('src.backend.apps.workflow.services.WorkflowTransitionHistory.objects.filter')
    def test_get_workflow_metrics_all_types(self, mock_filter):
        """Tests retrieving workflow metrics for all workflow types."""
        # Setup
        start_date = timezone.now() - timezone.timedelta(days=30)
        end_date = timezone.now()
        mock_transitions = MagicMock()
        mock_filter.return_value = mock_transitions
        
        # Call function
        result = get_workflow_metrics(start_date=start_date, end_date=end_date)
        
        # Verify
        assert isinstance(result, dict)
        assert mock_filter.call_count == 3  # Once for each workflow type


class TestWorkflowService:
    """Tests for the WorkflowService class."""
    
    def test_service_methods_delegate_to_functions(self):
        """Tests that WorkflowService methods delegate to the corresponding standalone functions."""
        # Setup - Create mock parameters
        entity = mock_entity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['DRAFT'])
        to_state = APPLICATION_STATUS['SUBMITTED']
        user = mock_user()
        reason = "Test transition"
        task_id = uuid.uuid4()
        task_type = WORKFLOW_TASK_TYPES['DOCUMENT_UPLOAD']
        description = "Upload documents"
        assigned_to = mock_user("underwriter")
        status = WORKFLOW_TASK_STATUS['PENDING']
        notes = "Task completed"
        new_assignee = mock_user("qc")
        reassigned_by = mock_user("system_admin")
        delay_hours = 24
        workflow_type = WORKFLOW_TYPES['APPLICATION']
        start_date = timezone.now() - timezone.timedelta(days=30)
        end_date = timezone.now()
        
        # Mock all the standalone functions that the service methods call
        with patch('src.backend.apps.workflow.services.get_allowed_transitions') as mock_get_allowed_transitions, \
             patch('src.backend.apps.workflow.services.validate_transition') as mock_validate_transition, \
             patch('src.backend.apps.workflow.services.perform_transition') as mock_perform_transition, \
             patch('src.backend.apps.workflow.services.initialize_entity_workflow') as mock_initialize_entity_workflow, \
             patch('src.backend.apps.workflow.services.get_transition_history') as mock_get_transition_history, \
             patch('src.backend.apps.workflow.services.create_workflow_task') as mock_create_workflow_task, \
             patch('src.backend.apps.workflow.services.get_entity_tasks') as mock_get_entity_tasks, \
             patch('src.backend.apps.workflow.services.get_pending_tasks') as mock_get_pending_tasks, \
             patch('src.backend.apps.workflow.services.complete_task') as mock_complete_task, \
             patch('src.backend.apps.workflow.services.cancel_task') as mock_cancel_task, \
             patch('src.backend.apps.workflow.services.reassign_task') as mock_reassign_task, \
             patch('src.backend.apps.workflow.services.get_overdue_tasks') as mock_get_overdue_tasks, \
             patch('src.backend.apps.workflow.services.schedule_automatic_transition') as mock_schedule_automatic_transition, \
             patch('src.backend.apps.workflow.services.process_automatic_transitions') as mock_process_automatic_transitions, \
             patch('src.backend.apps.workflow.services.check_for_automatic_transitions') as mock_check_for_automatic_transitions, \
             patch('src.backend.apps.workflow.services.check_sla_violations') as mock_check_sla_violations, \
             patch('src.backend.apps.workflow.services.get_sla_status') as mock_get_sla_status, \
             patch('src.backend.apps.workflow.services.update_sla_due_dates') as mock_update_sla_due_dates, \
             patch('src.backend.apps.workflow.services.get_workflow_metrics') as mock_get_workflow_metrics:
            
            # Create service instance
            service = WorkflowService()
            
            # Test each service method
            service.get_allowed_transitions(entity)
            mock_get_allowed_transitions.assert_called_once_with(entity)
            
            service.validate_transition(entity, to_state, user)
            mock_validate_transition.assert_called_once_with(entity, to_state, user)
            
            service.perform_transition(entity, to_state, user, reason, True)
            mock_perform_transition.assert_called_once_with(entity, to_state, user, reason, True)
            
            service.initialize_entity_workflow(entity, user)
            mock_initialize_entity_workflow.assert_called_once_with(entity, user)
            
            service.get_transition_history(entity, 5)
            mock_get_transition_history.assert_called_once_with(entity, 5)
            
            service.create_workflow_task(entity, task_type, description, assigned_to, None)
            mock_create_workflow_task.assert_called_once_with(entity, task_type, description, assigned_to, None)
            
            service.get_entity_tasks(entity, status)
            mock_get_entity_tasks.assert_called_once_with(entity, status)
            
            service.get_pending_tasks(entity)
            mock_get_pending_tasks.assert_called_once_with(entity)
            
            service.complete_task(task_id, user, notes)
            mock_complete_task.assert_called_once_with(task_id, user, notes)
            
            service.cancel_task(task_id, user, reason)
            mock_cancel_task.assert_called_once_with(task_id, user, reason)
            
            service.reassign_task(task_id, new_assignee, reassigned_by, reason)
            mock_reassign_task.assert_called_once_with(task_id, new_assignee, reassigned_by, reason)
            
            service.get_overdue_tasks(workflow_type)
            mock_get_overdue_tasks.assert_called_once_with(workflow_type)
            
            service.schedule_automatic_transition(entity, to_state, reason, delay_hours)
            mock_schedule_automatic_transition.assert_called_once_with(entity, to_state, reason, delay_hours)
            
            service.process_automatic_transitions()
            mock_process_automatic_transitions.assert_called_once()
            
            service.check_for_automatic_transitions(entity)
            mock_check_for_automatic_transitions.assert_called_once_with(entity)
            
            service.check_sla_violations()
            mock_check_sla_violations.assert_called_once()
            
            service.get_sla_status(entity)
            mock_get_sla_status.assert_called_once_with(entity)
            
            service.update_sla_due_dates()
            mock_update_sla_due_dates.assert_called_once()
            
            service.get_workflow_metrics(workflow_type, start_date, end_date)
            mock_get_workflow_metrics.assert_called_once_with(workflow_type, start_date, end_date)