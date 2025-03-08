"""
Unit tests for the state machine implementation that manages workflow transitions in the loan management system.

These tests validate the core functionality of the StateMachine class, including state transitions,
validation, and error handling.
"""

import uuid
from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from ..state_machine import (
    StateMachine,  
    create_transition_history,
    create_workflow_tasks,
    get_transition_event
)
from ..constants import (
    WORKFLOW_TYPES,
    APPLICATION_STATE_TRANSITIONS,
    DOCUMENT_STATE_TRANSITIONS,
    FUNDING_STATE_TRANSITIONS,
    INITIAL_STATES,
    TERMINAL_STATES,
    STATE_TRANSITION_PERMISSIONS,
)
from ...utils.constants import (
    APPLICATION_STATUS,
    DOCUMENT_STATUS,
    FUNDING_STATUS,
    USER_TYPES,
)
from ..models import (
    WorkflowTransitionHistory,
    WorkflowTask,
    WorkflowEntity
)


class MockWorkflowEntity:
    """Mock implementation of WorkflowEntity for testing."""
    
    def __init__(self, workflow_type, current_state):
        self.workflow_type = workflow_type
        self.current_state = current_state
        self.state_changed_at = timezone.now()
        self.state_changed_by = None
        self.is_terminal = False
        self.sla_due_at = None
        self.id = uuid.uuid4()
        
    def get_workflow_type(self):
        """Returns the workflow type of this entity."""
        return self.workflow_type
        
    def save(self):
        """Mock save method for testing."""
        # Update timestamp when current_state changes
        self.state_changed_at = timezone.now()
        # Mock save method - doesn't actually save to DB
        pass

    def update_sla_due_date(self):
        """Mock method to update SLA due date."""
        # This is a mock method that doesn't do anything in tests
        pass


class StateMachineTestCase(TestCase):
    """Test case for the StateMachine class."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Set up state machines for different workflow types
        self.app_state_machine = StateMachine(WORKFLOW_TYPES['APPLICATION'])
        self.doc_state_machine = StateMachine(WORKFLOW_TYPES['DOCUMENT'])
        self.funding_state_machine = StateMachine(WORKFLOW_TYPES['FUNDING'])
        
        # Set up mock entities
        self.app_entity = MockWorkflowEntity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['DRAFT'])
        self.doc_entity = MockWorkflowEntity(WORKFLOW_TYPES['DOCUMENT'], DOCUMENT_STATUS['DRAFT'])
        self.funding_entity = MockWorkflowEntity(WORKFLOW_TYPES['FUNDING'], FUNDING_STATUS['PENDING_ENROLLMENT'])
        
        # Common test data
        self.mock_user = MagicMock()
        self.mock_user.user_type = USER_TYPES['UNDERWRITER']
    
    def test_initialization(self):
        """Test that StateMachine initializes correctly with different workflow types."""
        # Check that state_transitions is set correctly
        self.assertEqual(self.app_state_machine.state_transitions, APPLICATION_STATE_TRANSITIONS)
        self.assertEqual(self.doc_state_machine.state_transitions, DOCUMENT_STATE_TRANSITIONS)
        self.assertEqual(self.funding_state_machine.state_transitions, FUNDING_STATE_TRANSITIONS)
        
        # Test invalid workflow type
        with self.assertRaises(ValueError):
            StateMachine("invalid_workflow_type")
    
    def test_get_allowed_transitions(self):
        """Test that get_allowed_transitions returns correct next states."""
        # Test for APPLICATION workflow
        allowed = self.app_state_machine.get_allowed_transitions(APPLICATION_STATUS['DRAFT'])
        self.assertEqual(allowed, [APPLICATION_STATUS['SUBMITTED'], APPLICATION_STATUS['ABANDONED']])
        
        # Test for DOCUMENT workflow
        allowed = self.doc_state_machine.get_allowed_transitions(DOCUMENT_STATUS['GENERATED'])
        self.assertEqual(allowed, [DOCUMENT_STATUS['SENT']])
        
        # Test for FUNDING workflow
        allowed = self.funding_state_machine.get_allowed_transitions(FUNDING_STATUS['ENROLLMENT_VERIFIED'])
        self.assertEqual(allowed, [FUNDING_STATUS['STIPULATION_REVIEW']])
        
        # Test with non-existent state
        allowed = self.app_state_machine.get_allowed_transitions("non-existent-state")
        self.assertEqual(allowed, [])
    
    def test_validate_transition(self):
        """Test that validate_transition correctly validates state transitions."""
        # Test valid transitions
        valid = self.app_state_machine.validate_transition(
            APPLICATION_STATUS['DRAFT'], 
            APPLICATION_STATUS['SUBMITTED']
        )
        self.assertTrue(valid)
        
        # Test invalid transitions
        invalid = self.app_state_machine.validate_transition(
            APPLICATION_STATUS['DRAFT'], 
            APPLICATION_STATUS['APPROVED']
        )
        self.assertFalse(invalid)
        
        # Test with user permissions
        # Underwriter has permission to transition to IN_REVIEW
        valid_with_user = self.app_state_machine.validate_transition(
            APPLICATION_STATUS['SUBMITTED'],
            APPLICATION_STATUS['IN_REVIEW'],
            self.mock_user
        )
        self.assertTrue(valid_with_user)
        
        # Change user type to one without permission
        self.mock_user.user_type = USER_TYPES['BORROWER']
        invalid_with_user = self.app_state_machine.validate_transition(
            APPLICATION_STATUS['SUBMITTED'],
            APPLICATION_STATUS['IN_REVIEW'],
            self.mock_user
        )
        self.assertFalse(invalid_with_user)
    
    @patch('src.backend.apps.workflow.state_machine.create_transition_history')
    @patch('src.backend.apps.workflow.state_machine.create_workflow_tasks')
    @patch('src.backend.apps.workflow.state_machine.process_workflow_notifications')
    @patch('src.backend.apps.workflow.state_machine.check_automatic_transitions')
    @patch('src.backend.apps.workflow.state_machine.get_transition_event')
    def test_transition(self, mock_get_event, mock_check_auto, mock_process_notif, mock_create_tasks, mock_create_history):
        """Test that transition correctly changes entity state."""
        # Set up mocks
        mock_create_history.return_value = MagicMock()
        mock_create_tasks.return_value = []
        mock_process_notif.return_value = True
        mock_check_auto.return_value = False
        mock_get_event.return_value = 'TEST_EVENT'
        
        # Test valid transition for APPLICATION
        result = self.app_state_machine.transition(
            self.app_entity,
            APPLICATION_STATUS['SUBMITTED'],
            self.mock_user,
            "Test transition"
        )
        
        # Verify entity state updated
        self.assertTrue(result)
        self.assertEqual(self.app_entity.current_state, APPLICATION_STATUS['SUBMITTED'])
        self.assertEqual(self.app_entity.state_changed_by, self.mock_user)
        
        # Verify mocks called
        mock_create_history.assert_called_once()
        mock_create_tasks.assert_called_once()
        
        # Test transition with null user
        mock_create_history.reset_mock()
        mock_create_tasks.reset_mock()
        mock_get_event.reset_mock()
        
        self.doc_entity.current_state = DOCUMENT_STATUS['DRAFT']
        result = self.doc_state_machine.transition(
            self.doc_entity,
            DOCUMENT_STATUS['GENERATED'],
            None,
            "Test transition"
        )
        
        self.assertTrue(result)
        self.assertEqual(self.doc_entity.current_state, DOCUMENT_STATUS['GENERATED'])
        self.assertIsNone(self.doc_entity.state_changed_by)
        
        # Verify mocks called
        mock_create_history.assert_called_once()
        mock_create_tasks.assert_called_once()
    
    def test_transition_validation_error(self):
        """Test that transition raises ValidationError for invalid transitions."""
        # Test APPLICATION invalid transition
        with self.assertRaises(ValidationError):
            self.app_state_machine.transition(
                self.app_entity,
                APPLICATION_STATUS['APPROVED'],  # Cannot go directly from DRAFT to APPROVED
                self.mock_user,
                "Invalid transition",
                validate=True
            )
        
        # Verify entity state not changed
        self.assertEqual(self.app_entity.current_state, APPLICATION_STATUS['DRAFT'])
        
        # Test DOCUMENT invalid transition
        with self.assertRaises(ValidationError):
            self.doc_state_machine.transition(
                self.doc_entity,
                DOCUMENT_STATUS['COMPLETED'],  # Cannot go directly from DRAFT to COMPLETED
                self.mock_user,
                "Invalid transition",
                validate=True
            )
        
        # Verify entity state not changed
        self.assertEqual(self.doc_entity.current_state, DOCUMENT_STATUS['DRAFT'])
    
    def test_get_initial_state(self):
        """Test that get_initial_state returns correct initial state."""
        # Test APPLICATION initial state
        self.assertEqual(
            self.app_state_machine.get_initial_state(),
            INITIAL_STATES[WORKFLOW_TYPES['APPLICATION']]
        )
        
        # Test DOCUMENT initial state
        self.assertEqual(
            self.doc_state_machine.get_initial_state(),
            INITIAL_STATES[WORKFLOW_TYPES['DOCUMENT']]
        )
        
        # Test FUNDING initial state
        self.assertEqual(
            self.funding_state_machine.get_initial_state(),
            INITIAL_STATES[WORKFLOW_TYPES['FUNDING']]
        )
    
    def test_is_terminal_state(self):
        """Test that is_terminal_state correctly identifies terminal states."""
        # Test APPLICATION terminal states
        self.assertTrue(self.app_state_machine.is_terminal_state(APPLICATION_STATUS['FUNDED']))
        self.assertTrue(self.app_state_machine.is_terminal_state(APPLICATION_STATUS['DENIED']))
        self.assertFalse(self.app_state_machine.is_terminal_state(APPLICATION_STATUS['DRAFT']))
        
        # Test DOCUMENT terminal states
        self.assertTrue(self.doc_state_machine.is_terminal_state(DOCUMENT_STATUS['COMPLETED']))
        self.assertFalse(self.doc_state_machine.is_terminal_state(DOCUMENT_STATUS['DRAFT']))
        
        # Test FUNDING terminal states
        self.assertTrue(self.funding_state_machine.is_terminal_state(FUNDING_STATUS['FUNDING_COMPLETE']))
        self.assertFalse(self.funding_state_machine.is_terminal_state(FUNDING_STATUS['PENDING_ENROLLMENT']))
    
    @patch('src.backend.apps.workflow.state_machine.create_transition_history')
    @patch('src.backend.apps.workflow.state_machine.create_workflow_tasks')
    @patch('src.backend.apps.workflow.state_machine.process_workflow_notifications')
    @patch('src.backend.apps.workflow.state_machine.check_automatic_transitions')
    @patch('src.backend.apps.workflow.state_machine.get_transition_event')
    def test_transition_to_terminal_state(self, mock_get_event, mock_check_auto, mock_process_notif, mock_create_tasks, mock_create_history):
        """Test that transitioning to a terminal state sets is_terminal flag."""
        # Set up mocks
        mock_create_history.return_value = MagicMock()
        mock_create_tasks.return_value = []
        mock_process_notif.return_value = True
        mock_check_auto.return_value = False
        mock_get_event.return_value = 'TEST_EVENT'
        
        # Test APPLICATION terminal state
        self.app_entity.current_state = APPLICATION_STATUS['READY_TO_FUND']
        self.app_state_machine.transition(
            self.app_entity,
            APPLICATION_STATUS['FUNDED'],
            self.mock_user,
            "Terminal transition"
        )
        
        # Verify is_terminal flag set
        self.assertTrue(self.app_entity.is_terminal)
        
        # Test DOCUMENT terminal state
        self.doc_entity.current_state = DOCUMENT_STATUS['PARTIALLY_SIGNED']
        self.doc_state_machine.transition(
            self.doc_entity,
            DOCUMENT_STATUS['COMPLETED'],
            self.mock_user,
            "Terminal transition"
        )
        
        # Verify is_terminal flag set
        self.assertTrue(self.doc_entity.is_terminal)
    
    @patch('src.backend.apps.workflow.state_machine.create_transition_history')
    @patch('src.backend.apps.workflow.state_machine.create_workflow_tasks')
    @patch('src.backend.apps.workflow.state_machine.process_workflow_notifications')
    @patch('src.backend.apps.workflow.state_machine.check_automatic_transitions')
    @patch('src.backend.apps.workflow.state_machine.get_transition_event')
    def test_transition_with_user(self, mock_get_event, mock_check_auto, mock_process_notif, mock_create_tasks, mock_create_history):
        """Test that transition correctly records the user who made the change."""
        # Set up mocks
        mock_create_history.return_value = MagicMock()
        mock_create_tasks.return_value = []
        mock_process_notif.return_value = True
        mock_check_auto.return_value = False
        mock_get_event.return_value = 'TEST_EVENT'
        
        # Create mock user
        user = MagicMock()
        
        # Test APPLICATION transition with user
        self.app_entity.current_state = APPLICATION_STATUS['DRAFT']
        self.app_state_machine.transition(
            self.app_entity,
            APPLICATION_STATUS['SUBMITTED'],
            user,
            "User transition"
        )
        
        # Verify user recorded
        self.assertEqual(self.app_entity.state_changed_by, user)
        
        # Test DOCUMENT transition with user
        self.doc_entity.current_state = DOCUMENT_STATUS['DRAFT']
        self.doc_state_machine.transition(
            self.doc_entity,
            DOCUMENT_STATUS['GENERATED'],
            user,
            "User transition"
        )
        
        # Verify user recorded
        self.assertEqual(self.doc_entity.state_changed_by, user)


class TransitionHistoryTestCase(TestCase):
    """Test case for transition history creation."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Set up mock entities and content types
        self.app_entity = MockWorkflowEntity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['DRAFT'])
        
        self.mock_content_type = MagicMock(spec=ContentType)
        self.mock_user = MagicMock()
    
    @patch('django.contrib.contenttypes.models.ContentType.objects.get_for_model')
    def test_create_transition_history(self, mock_get_for_model):
        """Test that create_transition_history creates history records correctly."""
        # Set up mocks
        mock_get_for_model.return_value = self.mock_content_type
        mock_history = MagicMock(spec=WorkflowTransitionHistory)
        
        with patch('src.backend.apps.workflow.models.WorkflowTransitionHistory.objects.create') as mock_create:
            mock_create.return_value = mock_history
            
            # Call the function
            result = create_transition_history(
                self.app_entity,
                APPLICATION_STATUS['DRAFT'],
                APPLICATION_STATUS['SUBMITTED'],
                self.mock_user,
                "Test reason",
                "TEST_EVENT"
            )
            
            # Verify create called with correct parameters
            mock_create.assert_called_once_with(
                workflow_type=WORKFLOW_TYPES['APPLICATION'],
                from_state=APPLICATION_STATUS['DRAFT'],
                to_state=APPLICATION_STATUS['SUBMITTED'],
                transitioned_by=self.mock_user,
                reason="Test reason",
                transition_event="TEST_EVENT",
                content_type=self.mock_content_type,
                object_id=self.app_entity.id
            )
            
            # Verify result is the created history record
            self.assertEqual(result, mock_history)


class WorkflowTasksTestCase(TestCase):
    """Test case for workflow task creation."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Set up mock entities and content types
        self.app_entity = MockWorkflowEntity(WORKFLOW_TYPES['APPLICATION'], APPLICATION_STATUS['DRAFT'])
        
        self.mock_content_type = MagicMock(spec=ContentType)
        
        # Test data for required actions
        self.test_required_actions = [
            {
                "task_type": "review_required",
                "description": "Test task"
            }
        ]
    
    @patch('django.contrib.contenttypes.models.ContentType.objects.get_for_model')
    @patch('src.backend.apps.workflow.state_machine.REQUIRED_ACTIONS', {
        'submitted': [  # Using the string value, not the constant
            {
                "task_type": "review_required",
                "description": "Test task"
            }
        ]
    })
    def test_create_workflow_tasks(self, mock_get_for_model):
        """Test that create_workflow_tasks creates tasks correctly."""
        # Set up mocks
        mock_get_for_model.return_value = self.mock_content_type
        mock_task = MagicMock(spec=WorkflowTask)
        
        with patch('src.backend.apps.workflow.models.WorkflowTask.objects.create') as mock_create:
            mock_create.return_value = mock_task
            
            # Call the function
            result = create_workflow_tasks(
                self.app_entity,
                'submitted'  # Using the string value, not the constant
            )
            
            # Verify create called with correct parameters
            mock_create.assert_called_once_with(
                task_type="review_required",
                description="Test task",
                content_type=self.mock_content_type,
                object_id=self.app_entity.id
            )
            
            # Verify result is list of created tasks
            self.assertEqual(result, [mock_task])
    
    @patch('django.contrib.contenttypes.models.ContentType.objects.get_for_model')
    @patch('src.backend.apps.workflow.state_machine.REQUIRED_ACTIONS', {})
    def test_create_workflow_tasks_no_actions(self, mock_get_for_model):
        """Test that create_workflow_tasks handles states with no required actions."""
        # Set up mocks
        mock_get_for_model.return_value = self.mock_content_type
        
        with patch('src.backend.apps.workflow.models.WorkflowTask.objects.create') as mock_create:
            # Call the function
            result = create_workflow_tasks(
                self.app_entity,
                APPLICATION_STATUS['DRAFT']  # No required actions for DRAFT
            )
            
            # Verify create not called
            mock_create.assert_not_called()
            
            # Verify result is empty list
            self.assertEqual(result, [])


class TransitionEventTestCase(TestCase):
    """Test case for transition event handling."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Set up test data
        self.test_events = {
            "TEST_EVENT": {
                "workflow_type": WORKFLOW_TYPES['APPLICATION'],
                "from_state": APPLICATION_STATUS['DRAFT'],
                "to_state": APPLICATION_STATUS['SUBMITTED']
            },
            "TEST_LIST_EVENT": {
                "workflow_type": WORKFLOW_TYPES['APPLICATION'],
                "from_state": [APPLICATION_STATUS['DRAFT'], APPLICATION_STATUS['INCOMPLETE']],
                "to_state": APPLICATION_STATUS['SUBMITTED']
            }
        }
    
    @patch('src.backend.apps.workflow.state_machine.WORKFLOW_TRANSITION_EVENTS', {
        "TEST_EVENT": {
            "workflow_type": "application",  # Using string constants
            "from_state": "draft",
            "to_state": "submitted"
        },
        "TEST_DOC_EVENT": {
            "workflow_type": "document",
            "from_state": "draft",
            "to_state": "generated"
        }
    })
    def test_get_transition_event(self):
        """Test that get_transition_event returns correct event names."""
        # Test simple direct mapping
        event = get_transition_event(
            "application",  # Using string constants
            "draft",
            "submitted"
        )
        self.assertEqual(event, "TEST_EVENT")
        
        # Test document event
        event = get_transition_event(
            "document",
            "draft",
            "generated"
        )
        self.assertEqual(event, "TEST_DOC_EVENT")
        
        # Test non-existent event
        event = get_transition_event(
            "funding",
            "pending_enrollment",
            "enrollment_verified"
        )
        self.assertIsNone(event)
    
    @patch('src.backend.apps.workflow.state_machine.WORKFLOW_TRANSITION_EVENTS', {
        "TEST_LIST_EVENT": {
            "workflow_type": "application",
            "from_state": ["draft", "incomplete"],
            "to_state": "submitted"
        }
    })
    def test_get_transition_event_with_list_from_state(self):
        """Test that get_transition_event handles from_state as a list."""
        # Test from_state in list
        event = get_transition_event(
            "application",
            "draft",
            "submitted"
        )
        self.assertEqual(event, "TEST_LIST_EVENT")
        
        # Test another from_state in list
        event = get_transition_event(
            "application",
            "incomplete",
            "submitted"
        )
        self.assertEqual(event, "TEST_LIST_EVENT")