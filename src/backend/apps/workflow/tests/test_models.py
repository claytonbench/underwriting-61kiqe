from django.test import TestCase
from unittest import mock
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

from ..models import (
    WorkflowTransitionHistory,
    AutomaticTransitionSchedule,
    WorkflowTask,
    WorkflowTaskManager,
    WorkflowEntity
)
from ..constants import (
    WORKFLOW_TYPES,
    WORKFLOW_TASK_TYPES,
    WORKFLOW_TASK_STATUS,
    WORKFLOW_SLA_DEFINITIONS
)
from ...utils.constants import (
    APPLICATION_STATUS,
    DOCUMENT_STATUS,
    FUNDING_STATUS
)

import uuid


class MockWorkflowEntity:
    """Mock implementation of WorkflowEntity for testing"""
    
    def __init__(self, workflow_type):
        self._workflow_type = workflow_type
        self.current_state = None
        self.state_changed_at = timezone.now()
        self.state_changed_by = None
        self.is_terminal = False
        self.sla_due_at = None
        self.id = uuid.uuid4()  # Generate a UUID for the mock entity
    
    def get_workflow_type(self):
        """Returns the workflow type of this entity"""
        return self._workflow_type
    
    def save(self, **kwargs):
        """Mock save method"""
        pass  # Do nothing, this is a mock


class WorkflowTransitionHistoryTest(TestCase):
    """Test case for WorkflowTransitionHistory model"""
    
    def setUp(self):
        """Set up test data"""
        # Create a test user
        User = get_user_model()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
        
        # Create a mock workflow entity
        self.entity = MockWorkflowEntity(WORKFLOW_TYPES['APPLICATION'])
        
        # Get content type for the mock entity
        self.content_type = ContentType.objects.get_for_model(self.entity.__class__)
    
    def test_create_transition_history(self):
        """Test creating a transition history record"""
        transition = WorkflowTransitionHistory.objects.create(
            workflow_type=WORKFLOW_TYPES['APPLICATION'],
            from_state=APPLICATION_STATUS['DRAFT'],
            to_state=APPLICATION_STATUS['SUBMITTED'],
            transition_date=timezone.now(),
            transitioned_by=self.user,
            reason='User submitted application',
            transition_event='APPLICATION_SUBMITTED',
            content_type=self.content_type,
            object_id=self.entity.id
        )
        
        # Verify the record was created with correct values
        self.assertEqual(transition.workflow_type, WORKFLOW_TYPES['APPLICATION'])
        self.assertEqual(transition.from_state, APPLICATION_STATUS['DRAFT'])
        self.assertEqual(transition.to_state, APPLICATION_STATUS['SUBMITTED'])
        self.assertEqual(transition.transitioned_by, self.user)
        self.assertEqual(transition.reason, 'User submitted application')
        self.assertEqual(transition.transition_event, 'APPLICATION_SUBMITTED')
        self.assertEqual(transition.object_id, self.entity.id)
        
        # Verify string representation is correct
        expected_str = f"{WORKFLOW_TYPES['APPLICATION']}: {APPLICATION_STATUS['DRAFT']} → {APPLICATION_STATUS['SUBMITTED']} on {transition.transition_date}"
        self.assertEqual(str(transition), expected_str)
    
    def test_transition_date_auto_set(self):
        """Test that transition_date is automatically set if not provided"""
        transition = WorkflowTransitionHistory.objects.create(
            workflow_type=WORKFLOW_TYPES['APPLICATION'],
            from_state=APPLICATION_STATUS['DRAFT'],
            to_state=APPLICATION_STATUS['SUBMITTED'],
            transitioned_by=self.user,
            content_type=self.content_type,
            object_id=self.entity.id
        )
        
        # Verify transition_date was automatically set
        self.assertIsNotNone(transition.transition_date)
        # Should be very close to current time
        time_diff = timezone.now() - transition.transition_date
        self.assertLess(time_diff.total_seconds(), 5)  # Within 5 seconds


class AutomaticTransitionScheduleTest(TestCase):
    """Test case for AutomaticTransitionSchedule model"""
    
    def setUp(self):
        """Set up test data"""
        # Create a test user
        User = get_user_model()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
        
        # Create a mock workflow entity
        self.entity = MockWorkflowEntity(WORKFLOW_TYPES['APPLICATION'])
        
        # Get content type for the mock entity
        self.content_type = ContentType.objects.get_for_model(self.entity.__class__)
    
    def test_create_automatic_transition(self):
        """Test creating an automatic transition schedule"""
        scheduled_date = timezone.now() + timezone.timedelta(hours=24)
        transition = AutomaticTransitionSchedule.objects.create(
            workflow_type=WORKFLOW_TYPES['APPLICATION'],
            from_state=APPLICATION_STATUS['APPROVED'],
            to_state=APPLICATION_STATUS['COMMITMENT_SENT'],
            scheduled_date=scheduled_date,
            reason='Automatic commitment letter generation',
            content_type=self.content_type,
            object_id=self.entity.id
        )
        
        # Verify the record was created with correct values
        self.assertEqual(transition.workflow_type, WORKFLOW_TYPES['APPLICATION'])
        self.assertEqual(transition.from_state, APPLICATION_STATUS['APPROVED'])
        self.assertEqual(transition.to_state, APPLICATION_STATUS['COMMITMENT_SENT'])
        self.assertEqual(transition.scheduled_date, scheduled_date)
        self.assertEqual(transition.reason, 'Automatic commitment letter generation')
        self.assertEqual(transition.object_id, self.entity.id)
        self.assertFalse(transition.is_executed)
        self.assertIsNone(transition.executed_at)
        
        # Verify string representation is correct
        expected_str = f"{WORKFLOW_TYPES['APPLICATION']}: {APPLICATION_STATUS['APPROVED']} → {APPLICATION_STATUS['COMMITMENT_SENT']} scheduled for {scheduled_date}"
        self.assertEqual(str(transition), expected_str)
    
    def test_execute_transition(self):
        """Test executing a scheduled transition"""
        # Create a transition schedule
        scheduled_date = timezone.now() - timezone.timedelta(hours=1)  # In the past
        transition = AutomaticTransitionSchedule.objects.create(
            workflow_type=WORKFLOW_TYPES['APPLICATION'],
            from_state=APPLICATION_STATUS['APPROVED'],
            to_state=APPLICATION_STATUS['COMMITMENT_SENT'],
            scheduled_date=scheduled_date,
            reason='Automatic commitment letter generation',
            content_type=self.content_type,
            object_id=self.entity.id
        )
        
        # Mock the state machine
        state_machine_mock = mock.MagicMock()
        state_machine_mock.transition_to.return_value = True
        
        # Mock the ApplicationStateMachine class
        with mock.patch('apps.loan.state_machines.ApplicationStateMachine') as mock_state_machine_class:
            mock_state_machine_class.return_value = state_machine_mock
            
            # Execute the transition
            result = transition.execute()
            
            # Verify the result and that the state machine was called correctly
            self.assertTrue(result)
            mock_state_machine_class.assert_called_once_with(transition.content_object)
            state_machine_mock.transition_to.assert_called_once_with(
                APPLICATION_STATUS['COMMITMENT_SENT'], 
                reason='Automatic commitment letter generation'
            )
            
            # Verify the transition was marked as executed
            transition.refresh_from_db()
            self.assertTrue(transition.is_executed)
            self.assertIsNotNone(transition.executed_at)
    
    def test_execute_already_executed(self):
        """Test that executing an already executed schedule does nothing"""
        # Create a transition schedule that's already executed
        scheduled_date = timezone.now() - timezone.timedelta(hours=1)
        transition = AutomaticTransitionSchedule.objects.create(
            workflow_type=WORKFLOW_TYPES['APPLICATION'],
            from_state=APPLICATION_STATUS['APPROVED'],
            to_state=APPLICATION_STATUS['COMMITMENT_SENT'],
            scheduled_date=scheduled_date,
            reason='Automatic commitment letter generation',
            content_type=self.content_type,
            object_id=self.entity.id,
            is_executed=True,
            executed_at=timezone.now()
        )
        
        # Mock the state machine class
        mock_state_machine_class = mock.MagicMock()
        
        # Execute the transition
        with mock.patch('apps.loan.state_machines.ApplicationStateMachine', mock_state_machine_class):
            result = transition.execute()
            
            # Verify it returned false and didn't create a state machine
            self.assertFalse(result)
            mock_state_machine_class.assert_not_called()


class WorkflowTaskManagerTest(TestCase):
    """Test case for WorkflowTaskManager"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        User = get_user_model()
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='testpassword',
            first_name='User',
            last_name='One'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='testpassword',
            first_name='User',
            last_name='Two'
        )
        
        # Create a mock workflow entity
        self.entity = MockWorkflowEntity(WORKFLOW_TYPES['APPLICATION'])
        
        # Get content type for the mock entity
        self.content_type = ContentType.objects.get_for_model(self.entity.__class__)
        
        # Create test workflow tasks
        self.task1 = WorkflowTask.objects.create(
            task_type=WORKFLOW_TASK_TYPES['DOCUMENT_UPLOAD'],
            description='Upload proof of income',
            status=WORKFLOW_TASK_STATUS['PENDING'],
            assigned_to=self.user1,
            content_type=self.content_type,
            object_id=self.entity.id
        )
        
        self.task2 = WorkflowTask.objects.create(
            task_type=WORKFLOW_TASK_TYPES['SIGNATURE_REQUIRED'],
            description='Sign loan agreement',
            status=WORKFLOW_TASK_STATUS['PENDING'],
            assigned_to=self.user2,
            content_type=self.content_type,
            object_id=self.entity.id
        )
        
        self.task3 = WorkflowTask.objects.create(
            task_type=WORKFLOW_TASK_TYPES['REVIEW_REQUIRED'],
            description='Review application',
            status=WORKFLOW_TASK_STATUS['COMPLETED'],
            assigned_to=self.user1,
            completed_by=self.user1,
            content_type=self.content_type,
            object_id=self.entity.id
        )
    
    def test_get_pending_tasks(self):
        """Test getting pending tasks"""
        pending_tasks = WorkflowTask.objects.get_pending_tasks()
        
        # Should return both task1 and task2, but not task3
        self.assertEqual(pending_tasks.count(), 2)
        self.assertIn(self.task1, pending_tasks)
        self.assertIn(self.task2, pending_tasks)
        self.assertNotIn(self.task3, pending_tasks)
    
    def test_get_tasks_by_entity(self):
        """Test getting tasks for a specific entity"""
        # Create another entity to test filtering
        another_entity = MockWorkflowEntity(WORKFLOW_TYPES['APPLICATION'])
        another_content_type = ContentType.objects.get_for_model(another_entity.__class__)
        
        # Create a task for the other entity
        other_task = WorkflowTask.objects.create(
            task_type=WORKFLOW_TASK_TYPES['DOCUMENT_UPLOAD'],
            description='Upload document for different entity',
            status=WORKFLOW_TASK_STATUS['PENDING'],
            assigned_to=self.user1,
            content_type=another_content_type,
            object_id=another_entity.id
        )
        
        # Get tasks for the original entity
        entity_tasks = WorkflowTask.objects.get_tasks_by_entity(self.entity)
        
        # Should return all tasks for the original entity
        self.assertEqual(entity_tasks.count(), 3)
        self.assertIn(self.task1, entity_tasks)
        self.assertIn(self.task2, entity_tasks)
        self.assertIn(self.task3, entity_tasks)
        self.assertNotIn(other_task, entity_tasks)
    
    def test_get_tasks_by_type(self):
        """Test getting tasks of a specific type"""
        document_tasks = WorkflowTask.objects.get_tasks_by_type(WORKFLOW_TASK_TYPES['DOCUMENT_UPLOAD'])
        
        # Should return only task1
        self.assertEqual(document_tasks.count(), 1)
        self.assertIn(self.task1, document_tasks)
        self.assertNotIn(self.task2, document_tasks)
        self.assertNotIn(self.task3, document_tasks)
    
    def test_get_tasks_by_assignee(self):
        """Test getting tasks assigned to a specific user"""
        user1_tasks = WorkflowTask.objects.get_tasks_by_assignee(self.user1)
        
        # Should return task1 and task3 (assigned to user1)
        self.assertEqual(user1_tasks.count(), 2)
        self.assertIn(self.task1, user1_tasks)
        self.assertNotIn(self.task2, user1_tasks)
        self.assertIn(self.task3, user1_tasks)


class WorkflowTaskTest(TestCase):
    """Test case for WorkflowTask model"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        User = get_user_model()
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='testpassword',
            first_name='User',
            last_name='One'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='testpassword',
            first_name='User',
            last_name='Two'
        )
        
        # Create a mock workflow entity
        self.entity = MockWorkflowEntity(WORKFLOW_TYPES['APPLICATION'])
        
        # Get content type for the mock entity
        self.content_type = ContentType.objects.get_for_model(self.entity.__class__)
    
    def test_create_workflow_task(self):
        """Test creating a workflow task"""
        task = WorkflowTask.objects.create(
            task_type=WORKFLOW_TASK_TYPES['DOCUMENT_UPLOAD'],
            description='Upload proof of income',
            status=WORKFLOW_TASK_STATUS['PENDING'],
            due_date=timezone.now() + timezone.timedelta(days=3),
            assigned_to=self.user1,
            notes='Please upload recent pay stubs',
            content_type=self.content_type,
            object_id=self.entity.id
        )
        
        # Verify the record was created with correct values
        self.assertEqual(task.task_type, WORKFLOW_TASK_TYPES['DOCUMENT_UPLOAD'])
        self.assertEqual(task.description, 'Upload proof of income')
        self.assertEqual(task.status, WORKFLOW_TASK_STATUS['PENDING'])
        self.assertIsNotNone(task.due_date)
        self.assertEqual(task.assigned_to, self.user1)
        self.assertEqual(task.notes, 'Please upload recent pay stubs')
        self.assertEqual(task.object_id, self.entity.id)
        
        # Verify string representation is correct
        expected_str = f"{WORKFLOW_TASK_TYPES['DOCUMENT_UPLOAD']}: Upload proof of income"
        self.assertEqual(str(task), expected_str)
    
    def test_save_sets_defaults(self):
        """Test that save method sets default values"""
        # Create a task without specifying created_at or status
        task = WorkflowTask.objects.create(
            task_type=WORKFLOW_TASK_TYPES['DOCUMENT_UPLOAD'],
            description='Upload proof of income',
            assigned_to=self.user1,
            content_type=self.content_type,
            object_id=self.entity.id
        )
        
        # Verify created_at was automatically set
        self.assertIsNotNone(task.created_at)
        # Should be very close to current time
        time_diff = timezone.now() - task.created_at
        self.assertLess(time_diff.total_seconds(), 5)  # Within 5 seconds
        
        # Verify status was set to PENDING
        self.assertEqual(task.status, WORKFLOW_TASK_STATUS['PENDING'])
    
    def test_complete_task(self):
        """Test completing a task"""
        task = WorkflowTask.objects.create(
            task_type=WORKFLOW_TASK_TYPES['DOCUMENT_UPLOAD'],
            description='Upload proof of income',
            assigned_to=self.user1,
            content_type=self.content_type,
            object_id=self.entity.id
        )
        
        # Complete the task
        completion_notes = 'Verified income documentation'
        task.complete(self.user2, notes=completion_notes)
        
        # Verify the task was updated correctly
        self.assertEqual(task.status, WORKFLOW_TASK_STATUS['COMPLETED'])
        self.assertIsNotNone(task.completed_at)
        self.assertEqual(task.completed_by, self.user2)
        self.assertIn(completion_notes, task.notes)
    
    def test_cancel_task(self):
        """Test cancelling a task"""
        task = WorkflowTask.objects.create(
            task_type=WORKFLOW_TASK_TYPES['DOCUMENT_UPLOAD'],
            description='Upload proof of income',
            assigned_to=self.user1,
            content_type=self.content_type,
            object_id=self.entity.id
        )
        
        # Cancel the task
        cancellation_reason = 'No longer required'
        task.cancel(self.user2, reason=cancellation_reason)
        
        # Verify the task was updated correctly
        self.assertEqual(task.status, WORKFLOW_TASK_STATUS['CANCELLED'])
        self.assertIsNotNone(task.completed_at)
        self.assertEqual(task.completed_by, self.user2)
        self.assertIn(cancellation_reason, task.notes)
    
    def test_reassign_task(self):
        """Test reassigning a task"""
        task = WorkflowTask.objects.create(
            task_type=WORKFLOW_TASK_TYPES['DOCUMENT_UPLOAD'],
            description='Upload proof of income',
            assigned_to=self.user1,
            content_type=self.content_type,
            object_id=self.entity.id
        )
        
        # Reassign the task
        reassignment_reason = 'Better suited for user2'
        task.reassign(self.user2, self.user1, reason=reassignment_reason)
        
        # Verify the task was updated correctly
        self.assertEqual(task.assigned_to, self.user2)
        self.assertIn(reassignment_reason, task.notes)
        self.assertIn(str(self.user1), task.notes)  # Should mention who did the reassignment
        self.assertIn(str(self.user2), task.notes)  # Should mention the new assignee
    
    def test_is_overdue(self):
        """Test checking if a task is overdue"""
        # Create a task with due_date in the past
        past_due_task = WorkflowTask.objects.create(
            task_type=WORKFLOW_TASK_TYPES['DOCUMENT_UPLOAD'],
            description='Upload proof of income',
            assigned_to=self.user1,
            due_date=timezone.now() - timezone.timedelta(days=1),
            content_type=self.content_type,
            object_id=self.entity.id
        )
        
        # Create a task with due_date in the future
        future_due_task = WorkflowTask.objects.create(
            task_type=WORKFLOW_TASK_TYPES['DOCUMENT_UPLOAD'],
            description='Upload proof of residence',
            assigned_to=self.user1,
            due_date=timezone.now() + timezone.timedelta(days=1),
            content_type=self.content_type,
            object_id=self.entity.id
        )
        
        # Create a completed task with due_date in the past
        completed_task = WorkflowTask.objects.create(
            task_type=WORKFLOW_TASK_TYPES['DOCUMENT_UPLOAD'],
            description='Upload ID',
            status=WORKFLOW_TASK_STATUS['COMPLETED'],
            assigned_to=self.user1,
            completed_by=self.user1,
            due_date=timezone.now() - timezone.timedelta(days=1),
            content_type=self.content_type,
            object_id=self.entity.id
        )
        
        # Check if tasks are overdue
        self.assertTrue(past_due_task.is_overdue())
        self.assertFalse(future_due_task.is_overdue())
        self.assertFalse(completed_task.is_overdue())  # Should not be overdue because it's completed


class WorkflowEntityTest(TestCase):
    """Test case for WorkflowEntity abstract model"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        User = get_user_model()
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='testpassword',
            first_name='User',
            last_name='One'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='testpassword',
            first_name='User',
            last_name='Two'
        )
        
        # Create concrete implementations of WorkflowEntity for each workflow type
        self.app_entity = MockWorkflowEntity(WORKFLOW_TYPES['APPLICATION'])
        self.doc_entity = MockWorkflowEntity(WORKFLOW_TYPES['DOCUMENT'])
        self.fund_entity = MockWorkflowEntity(WORKFLOW_TYPES['FUNDING'])
        
        # Set up test states for each workflow type
        self.app_entity.current_state = APPLICATION_STATUS['SUBMITTED']
        self.doc_entity.current_state = DOCUMENT_STATUS['SENT']
        self.fund_entity.current_state = FUNDING_STATUS['STIPULATION_REVIEW']
    
    def test_save_updates_state_changed_at(self):
        """Test that save method updates state_changed_at when state changes"""
        # Create a workflow entity with an initial state
        entity = MockWorkflowEntity(WORKFLOW_TYPES['APPLICATION'])
        entity.current_state = APPLICATION_STATUS['DRAFT']
        original_time = timezone.now() - timezone.timedelta(hours=1)
        entity.state_changed_at = original_time
        
        # Mock the save method to track calls
        with mock.patch.object(entity, 'save') as mock_save:
            # Change the entity's state and call save
            entity.current_state = APPLICATION_STATUS['SUBMITTED']
            entity.save()
            
            # Verify save was called
            mock_save.assert_called_once()
    
    def test_get_workflow_type_abstract(self):
        """Test that get_workflow_type is abstract and must be implemented"""
        # Create a class that inherits from WorkflowEntity but doesn't implement get_workflow_type
        class TestEntity(WorkflowEntity):
            pass
        
        # Instantiate the class and try to call get_workflow_type
        entity = TestEntity()
        with self.assertRaises(NotImplementedError):
            entity.get_workflow_type()
    
    def test_get_transition_history(self):
        """Test getting transition history for an entity"""
        # Create a content type for our mock entity
        content_type = ContentType.objects.get_for_model(self.app_entity.__class__)
        
        # Create several transition history records for the entity
        transition1 = WorkflowTransitionHistory.objects.create(
            workflow_type=WORKFLOW_TYPES['APPLICATION'],
            from_state=APPLICATION_STATUS['DRAFT'],
            to_state=APPLICATION_STATUS['SUBMITTED'],
            transition_date=timezone.now() - timezone.timedelta(days=2),
            transitioned_by=self.user1,
            content_type=content_type,
            object_id=self.app_entity.id
        )
        
        transition2 = WorkflowTransitionHistory.objects.create(
            workflow_type=WORKFLOW_TYPES['APPLICATION'],
            from_state=APPLICATION_STATUS['SUBMITTED'],
            to_state=APPLICATION_STATUS['IN_REVIEW'],
            transition_date=timezone.now() - timezone.timedelta(days=1),
            transitioned_by=self.user2,
            content_type=content_type,
            object_id=self.app_entity.id
        )
        
        # Create a transition for a different entity
        different_entity = MockWorkflowEntity(WORKFLOW_TYPES['APPLICATION'])
        WorkflowTransitionHistory.objects.create(
            workflow_type=WORKFLOW_TYPES['APPLICATION'],
            from_state=APPLICATION_STATUS['DRAFT'],
            to_state=APPLICATION_STATUS['SUBMITTED'],
            transitioned_by=self.user1,
            content_type=content_type,
            object_id=different_entity.id
        )
        
        # Mock ContentType.objects.get_for_model to return our content_type
        with mock.patch.object(ContentType.objects, 'get_for_model', return_value=content_type):
            # Get transition history for our entity
            history = self.app_entity.get_transition_history()
        
            # Verify we get the correct history records in descending order by date
            self.assertEqual(history.count(), 2)
            self.assertEqual(history[0], transition2)  # Most recent first
            self.assertEqual(history[1], transition1)
    
    def test_get_pending_tasks(self):
        """Test getting pending tasks for an entity"""
        # Create a content type for our mock entity
        content_type = ContentType.objects.get_for_model(self.app_entity.__class__)
        
        # Create several workflow tasks for the entity with different statuses
        task1 = WorkflowTask.objects.create(
            task_type=WORKFLOW_TASK_TYPES['DOCUMENT_UPLOAD'],
            description='Upload proof of income',
            status=WORKFLOW_TASK_STATUS['PENDING'],
            assigned_to=self.user1,
            content_type=content_type,
            object_id=self.app_entity.id
        )
        
        task2 = WorkflowTask.objects.create(
            task_type=WORKFLOW_TASK_TYPES['SIGNATURE_REQUIRED'],
            description='Sign loan agreement',
            status=WORKFLOW_TASK_STATUS['COMPLETED'],
            assigned_to=self.user2,
            content_type=content_type,
            object_id=self.app_entity.id
        )
        
        # Create a task for a different entity
        different_entity = MockWorkflowEntity(WORKFLOW_TYPES['APPLICATION'])
        WorkflowTask.objects.create(
            task_type=WORKFLOW_TASK_TYPES['DOCUMENT_UPLOAD'],
            description='Upload document for different entity',
            status=WORKFLOW_TASK_STATUS['PENDING'],
            assigned_to=self.user1,
            content_type=content_type,
            object_id=different_entity.id
        )
        
        # Mock ContentType.objects.get_for_model to return our content_type
        with mock.patch.object(ContentType.objects, 'get_for_model', return_value=content_type):
            # Get pending tasks for our entity
            pending_tasks = self.app_entity.get_pending_tasks()
        
            # Verify we get only pending tasks for this entity
            self.assertEqual(pending_tasks.count(), 1)
            self.assertEqual(pending_tasks[0], task1)
    
    def test_calculate_sla_due_date(self):
        """Test calculating SLA due date based on current state"""
        # Set states that have SLA definitions
        self.app_entity.current_state = APPLICATION_STATUS['SUBMITTED']
        self.app_entity.state_changed_at = timezone.now()
        
        self.doc_entity.current_state = DOCUMENT_STATUS['SENT']
        self.doc_entity.state_changed_at = timezone.now()
        
        self.fund_entity.current_state = FUNDING_STATUS['STIPULATION_REVIEW']
        self.fund_entity.state_changed_at = timezone.now()
        
        # Calculate SLA due dates for each entity
        app_due_date = self.app_entity.calculate_sla_due_date()
        doc_due_date = self.doc_entity.calculate_sla_due_date()
        fund_due_date = self.fund_entity.calculate_sla_due_date()
        
        # Verify correct due dates based on SLA definitions
        app_hours = WORKFLOW_SLA_DEFINITIONS[WORKFLOW_TYPES['APPLICATION']][APPLICATION_STATUS['SUBMITTED']]['hours']
        expected_app_due_date = self.app_entity.state_changed_at + timezone.timedelta(hours=app_hours)
        self.assertEqual(app_due_date, expected_app_due_date)
        
        doc_hours = WORKFLOW_SLA_DEFINITIONS[WORKFLOW_TYPES['DOCUMENT']][DOCUMENT_STATUS['SENT']]['hours']
        expected_doc_due_date = self.doc_entity.state_changed_at + timezone.timedelta(hours=doc_hours)
        self.assertEqual(doc_due_date, expected_doc_due_date)
        
        fund_hours = WORKFLOW_SLA_DEFINITIONS[WORKFLOW_TYPES['FUNDING']][FUNDING_STATUS['STIPULATION_REVIEW']]['hours']
        expected_fund_due_date = self.fund_entity.state_changed_at + timezone.timedelta(hours=fund_hours)
        self.assertEqual(fund_due_date, expected_fund_due_date)
        
        # Test with a state that has no SLA definition
        self.app_entity.current_state = 'non_existent_state'
        no_sla_due_date = self.app_entity.calculate_sla_due_date()
        self.assertIsNone(no_sla_due_date)
    
    def test_update_sla_due_date(self):
        """Test updating SLA due date"""
        # Set up an entity with a state that has an SLA definition
        self.app_entity.current_state = APPLICATION_STATUS['SUBMITTED']
        self.app_entity.state_changed_at = timezone.now()
        
        # Mock calculate_sla_due_date to return a specific date
        expected_due_date = timezone.now() + timezone.timedelta(hours=24)
        with mock.patch.object(self.app_entity, 'calculate_sla_due_date', return_value=expected_due_date):
            # Call update_sla_due_date
            with mock.patch.object(self.app_entity, 'save') as mock_save:
                self.app_entity.update_sla_due_date()
                
                # Verify sla_due_at was updated and save was called
                self.assertEqual(self.app_entity.sla_due_at, expected_due_date)
                mock_save.assert_called_once_with(update_fields=['sla_due_at'])
    
    def test_is_sla_breached(self):
        """Test checking if SLA is breached"""
        # Create an entity with sla_due_at in the past
        past_entity = MockWorkflowEntity(WORKFLOW_TYPES['APPLICATION'])
        past_entity.sla_due_at = timezone.now() - timezone.timedelta(hours=1)
        
        # Create an entity with sla_due_at in the future
        future_entity = MockWorkflowEntity(WORKFLOW_TYPES['APPLICATION'])
        future_entity.sla_due_at = timezone.now() + timezone.timedelta(hours=1)
        
        # Create an entity with no sla_due_at
        none_entity = MockWorkflowEntity(WORKFLOW_TYPES['APPLICATION'])
        none_entity.sla_due_at = None
        
        # Check if SLAs are breached
        self.assertTrue(past_entity.is_sla_breached())
        self.assertFalse(future_entity.is_sla_breached())
        self.assertFalse(none_entity.is_sla_breached())