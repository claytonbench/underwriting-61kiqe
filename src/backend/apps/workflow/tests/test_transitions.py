"""
Unit tests for the transition handlers that implement business logic for workflow state transitions
in the loan management system.
"""

from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.core.exceptions import ValidationError
from django.utils import timezone

# Import the transition handlers we're testing
from ..transitions import (
    ApplicationTransitionHandler,
    DocumentTransitionHandler,
    FundingTransitionHandler,
    TransitionHandlerFactory,
    initialize_workflow,
    transition_application,
    transition_document,
    transition_funding,
    transition_entity,
    handle_document_expiration,
    process_automatic_transitions,
    send_signature_reminders,
    check_sla_violations
)

# Import the state machine
from ..state_machine import StateMachine

# Import constants
from ..constants import WORKFLOW_TYPES
from ...utils.constants import (
    APPLICATION_STATUS,
    DOCUMENT_STATUS,
    FUNDING_STATUS,
    USER_TYPES
)

import uuid


# Mock classes for testing
class MockWorkflowEntity:
    """Mock implementation of WorkflowEntity for testing transition handlers."""
    
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
        # Just update the state_changed_at to simulate a real save
        self.state_changed_at = timezone.now()
    
    def update_sla_due_date(self):
        """Mock method to update SLA due date."""
        # In a real implementation, this would calculate the SLA based on state
        self.sla_due_at = timezone.now() + timezone.timedelta(hours=24)


class MockApplication(MockWorkflowEntity):
    """Mock implementation of a loan application for testing application transitions."""
    
    def __init__(self, current_state, is_complete=True):
        self.current_state = current_state
        self.state_changed_at = timezone.now()
        self.state_changed_by = None
        self.is_terminal = False
        self.sla_due_at = None
        self.underwriting_decision = None
        self.is_complete = is_complete
        self.id = uuid.uuid4()
    
    def get_workflow_type(self):
        """Returns the workflow type of this entity."""
        return WORKFLOW_TYPES['APPLICATION']
    
    def save(self):
        """Mock save method for testing."""
        # Just update the state_changed_at to simulate a real save
        self.state_changed_at = timezone.now()
    
    def update_sla_due_date(self):
        """Mock method to update SLA due date."""
        # In a real implementation, this would calculate the SLA based on state
        self.sla_due_at = timezone.now() + timezone.timedelta(hours=24)


class MockDocument(MockWorkflowEntity):
    """Mock implementation of a document for testing document transitions."""
    
    def __init__(self, current_state, has_content=True, all_signatures_collected=False):
        self.current_state = current_state
        self.state_changed_at = timezone.now()
        self.state_changed_by = None
        self.is_terminal = False
        self.sla_due_at = None
        self.has_content = has_content
        self.all_signatures_collected = all_signatures_collected
        self.id = uuid.uuid4()
    
    def get_workflow_type(self):
        """Returns the workflow type of this entity."""
        return WORKFLOW_TYPES['DOCUMENT']
    
    def save(self):
        """Mock save method for testing."""
        # Just update the state_changed_at to simulate a real save
        self.state_changed_at = timezone.now()
    
    def update_sla_due_date(self):
        """Mock method to update SLA due date."""
        # In a real implementation, this would calculate the SLA based on state
        self.sla_due_at = timezone.now() + timezone.timedelta(hours=24)


class MockFundingRequest(MockWorkflowEntity):
    """Mock implementation of a funding request for testing funding transitions."""
    
    def __init__(self, current_state):
        self.current_state = current_state
        self.state_changed_at = timezone.now()
        self.state_changed_by = None
        self.is_terminal = False
        self.sla_due_at = None
        self.enrollment_verified = False
        self.stipulations_satisfied = False
        self.approval_complete = False
        self.disbursement_scheduled = False
        self.disbursement_processed = False
        self.id = uuid.uuid4()
    
    def get_workflow_type(self):
        """Returns the workflow type of this entity."""
        return WORKFLOW_TYPES['FUNDING']
    
    def save(self):
        """Mock save method for testing."""
        # Just update the state_changed_at to simulate a real save
        self.state_changed_at = timezone.now()
    
    def update_sla_due_date(self):
        """Mock method to update SLA due date."""
        # In a real implementation, this would calculate the SLA based on state
        self.sla_due_at = timezone.now() + timezone.timedelta(hours=24)


class MockUser:
    """Mock implementation of a user for testing transitions."""
    
    def __init__(self, user_type):
        self.id = uuid.uuid4()
        self.username = "testuser"
        self.user_type = user_type


class ApplicationTransitionHandlerTestCase(TestCase):
    """Test case for the ApplicationTransitionHandler class."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.handler = ApplicationTransitionHandler()
        
        # Create mock users
        self.borrower = MockUser(USER_TYPES['BORROWER'])
        self.school_admin = MockUser(USER_TYPES['SCHOOL_ADMIN'])
        self.underwriter = MockUser(USER_TYPES['UNDERWRITER'])
        self.qc_user = MockUser(USER_TYPES['QC'])
        self.system_admin = MockUser(USER_TYPES['SYSTEM_ADMIN'])
        
        # Create mock applications in different states
        self.draft_app = MockApplication(APPLICATION_STATUS['DRAFT'], is_complete=True)
        self.submitted_app = MockApplication(APPLICATION_STATUS['SUBMITTED'], is_complete=True)
        self.in_review_app = MockApplication(APPLICATION_STATUS['IN_REVIEW'], is_complete=True)
    
    def test_validate_transition_valid(self):
        """Test that validate_transition returns True for valid transitions."""
        # Mock the StateMachine.validate_transition to return True
        with patch.object(StateMachine, 'validate_transition', return_value=True):
            # Test various valid transitions
            self.assertTrue(self.handler.validate_transition(
                self.draft_app, APPLICATION_STATUS['SUBMITTED'], self.underwriter
            ))
            self.assertTrue(self.handler.validate_transition(
                self.submitted_app, APPLICATION_STATUS['IN_REVIEW'], self.underwriter
            ))
            self.assertTrue(self.handler.validate_transition(
                self.in_review_app, APPLICATION_STATUS['APPROVED'], self.underwriter
            ))
    
    def test_validate_transition_invalid(self):
        """Test that validate_transition returns False for invalid transitions."""
        # Mock the StateMachine.validate_transition to return False
        with patch.object(StateMachine, 'validate_transition', return_value=False):
            # Test invalid transition
            self.assertFalse(self.handler.validate_transition(
                self.draft_app, APPLICATION_STATUS['APPROVED'], self.borrower
            ))
    
    def test_validate_transition_application_specific(self):
        """Test application-specific validation rules."""
        # Mock the StateMachine.validate_transition to return True to isolate our rules
        with patch.object(StateMachine, 'validate_transition', return_value=True):
            # Test SUBMITTED requires complete application
            incomplete_app = MockApplication(APPLICATION_STATUS['DRAFT'], is_complete=False)
            self.assertFalse(self.handler.validate_transition(
                incomplete_app, APPLICATION_STATUS['SUBMITTED'], self.underwriter
            ))
            
            # Test APPROVED requires underwriting decision
            app_without_decision = MockApplication(APPLICATION_STATUS['IN_REVIEW'])
            self.assertFalse(self.handler.validate_transition(
                app_without_decision, APPLICATION_STATUS['APPROVED'], self.underwriter
            ))
            
            # Test COMMITMENT_ACCEPTED requires school admin
            app_for_commitment = MockApplication(APPLICATION_STATUS['COMMITMENT_SENT'])
            self.assertFalse(self.handler.validate_transition(
                app_for_commitment, APPLICATION_STATUS['COMMITMENT_ACCEPTED'], self.borrower
            ))
            self.assertTrue(self.handler.validate_transition(
                app_for_commitment, APPLICATION_STATUS['COMMITMENT_ACCEPTED'], self.school_admin
            ))
            
            # Test FULLY_EXECUTED requires all documents signed
            app_with_docs = MockApplication(APPLICATION_STATUS['PARTIALLY_EXECUTED'])
            doc_package = MagicMock()
            doc_package.is_fully_executed.return_value = True
            app_with_docs.document_package = doc_package
            self.assertTrue(self.handler.validate_transition(
                app_with_docs, APPLICATION_STATUS['FULLY_EXECUTED'], self.system_admin
            ))
            
            # Test QC_APPROVED requires QC user
            app_in_qc = MockApplication(APPLICATION_STATUS['QC_REVIEW'])
            self.assertFalse(self.handler.validate_transition(
                app_in_qc, APPLICATION_STATUS['QC_APPROVED'], self.borrower
            ))
            self.assertTrue(self.handler.validate_transition(
                app_in_qc, APPLICATION_STATUS['QC_APPROVED'], self.qc_user
            ))
    
    def test_pre_transition_actions(self):
        """Test pre-transition actions for application transitions."""
        # Test SUBMITTED validation
        with patch.object(self.draft_app, 'validate_for_submission', return_value=True):
            self.assertTrue(self.handler.pre_transition_actions(
                self.draft_app, APPLICATION_STATUS['SUBMITTED'], self.underwriter
            ))
        
        # Test IN_REVIEW assignment
        with patch('apps.underwriting.services.assign_underwriter', return_value=True):
            self.submitted_app.assigned_underwriter = None
            self.assertTrue(self.handler.pre_transition_actions(
                self.submitted_app, APPLICATION_STATUS['IN_REVIEW'], self.underwriter
            ))
        
        # Test APPROVED validation
        app_with_decision = MockApplication(APPLICATION_STATUS['IN_REVIEW'])
        decision = MagicMock()
        decision.approved_amount = 10000
        decision.interest_rate = 5.25
        decision.term_months = 36
        app_with_decision.underwriting_decision = decision
        self.assertTrue(self.handler.pre_transition_actions(
            app_with_decision, APPLICATION_STATUS['APPROVED'], self.underwriter
        ))
        
        # Test COMMITMENT_SENT preparation
        with patch('apps.documents.services.generate_commitment_letter', return_value=MagicMock()):
            self.assertTrue(self.handler.pre_transition_actions(
                app_with_decision, APPLICATION_STATUS['COMMITMENT_SENT'], self.system_admin
            ))
        
        # Test DOCUMENTS_SENT preparation
        with patch('apps.documents.services.generate_document_package', return_value=MagicMock()):
            self.assertTrue(self.handler.pre_transition_actions(
                app_with_decision, APPLICATION_STATUS['DOCUMENTS_SENT'], self.system_admin
            ))
    
    def test_post_transition_actions(self):
        """Test post-transition actions for application transitions."""
        # Test SUBMITTED creates underwriting queue entry
        with patch('apps.underwriting.services.create_underwriting_queue_entry', return_value=True):
            self.assertTrue(self.handler.post_transition_actions(
                self.draft_app, APPLICATION_STATUS['DRAFT'], APPLICATION_STATUS['SUBMITTED'], self.underwriter
            ))
        
        # Test APPROVED schedules automatic transition
        with patch('apps.workflow.transitions.schedule_automatic_transition', return_value=True):
            self.assertTrue(self.handler.post_transition_actions(
                self.in_review_app, APPLICATION_STATUS['IN_REVIEW'], APPLICATION_STATUS['APPROVED'], self.underwriter
            ))
        
        # Test COMMITMENT_ACCEPTED schedules document package transition
        with patch('apps.workflow.transitions.schedule_automatic_transition', return_value=True):
            app = MockApplication(APPLICATION_STATUS['COMMITMENT_ACCEPTED'])
            self.assertTrue(self.handler.post_transition_actions(
                app, APPLICATION_STATUS['COMMITMENT_SENT'], APPLICATION_STATUS['COMMITMENT_ACCEPTED'], self.school_admin
            ))
        
        # Test QC_APPROVED creates funding request
        with patch('apps.funding.services.create_funding_request', return_value=MagicMock()):
            with patch('apps.workflow.transitions.schedule_automatic_transition', return_value=True):
                app = MockApplication(APPLICATION_STATUS['QC_APPROVED'])
                self.assertTrue(self.handler.post_transition_actions(
                    app, APPLICATION_STATUS['QC_REVIEW'], APPLICATION_STATUS['QC_APPROVED'], self.qc_user
                ))
    
    def test_transition(self):
        """Test the complete transition process for applications."""
        # Mock the necessary methods
        with patch.object(self.handler, 'validate_transition', return_value=True), \
             patch.object(self.handler, 'pre_transition_actions', return_value=True), \
             patch.object(self.handler, 'post_transition_actions', return_value=True), \
             patch.object(StateMachine, 'transition', return_value=True):
            
            # Test a successful transition
            self.assertTrue(self.handler.transition(
                self.draft_app, APPLICATION_STATUS['SUBMITTED'], self.underwriter, "Test reason"
            ))
        
        # Test failure cases
        with patch.object(self.handler, 'validate_transition', return_value=False):
            self.assertFalse(self.handler.transition(
                self.draft_app, APPLICATION_STATUS['APPROVED'], self.underwriter, "Test reason"
            ))
        
        with patch.object(self.handler, 'validate_transition', return_value=True), \
             patch.object(self.handler, 'pre_transition_actions', return_value=False):
            self.assertFalse(self.handler.transition(
                self.draft_app, APPLICATION_STATUS['SUBMITTED'], self.underwriter, "Test reason"
            ))
        
        with patch.object(self.handler, 'validate_transition', return_value=True), \
             patch.object(self.handler, 'pre_transition_actions', return_value=True), \
             patch.object(StateMachine, 'transition', side_effect=ValidationError("Test error")):
            self.assertFalse(self.handler.transition(
                self.draft_app, APPLICATION_STATUS['SUBMITTED'], self.underwriter, "Test reason"
            ))


class DocumentTransitionHandlerTestCase(TestCase):
    """Test case for the DocumentTransitionHandler class."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.handler = DocumentTransitionHandler()
        
        # Create mock users
        self.borrower = MockUser(USER_TYPES['BORROWER'])
        self.school_admin = MockUser(USER_TYPES['SCHOOL_ADMIN'])
        self.system_admin = MockUser(USER_TYPES['SYSTEM_ADMIN'])
        
        # Create mock documents in different states
        self.draft_doc = MockDocument(DOCUMENT_STATUS['DRAFT'], has_content=True)
        self.generated_doc = MockDocument(DOCUMENT_STATUS['GENERATED'], has_content=True)
        self.sent_doc = MockDocument(DOCUMENT_STATUS['SENT'], has_content=True)
        self.partially_signed_doc = MockDocument(
            DOCUMENT_STATUS['PARTIALLY_SIGNED'], 
            has_content=True, 
            all_signatures_collected=False
        )
        self.fully_signed_doc = MockDocument(
            DOCUMENT_STATUS['PARTIALLY_SIGNED'], 
            has_content=True, 
            all_signatures_collected=True
        )
    
    def test_validate_transition_valid(self):
        """Test that validate_transition returns True for valid transitions."""
        # Mock the StateMachine.validate_transition to return True
        with patch.object(StateMachine, 'validate_transition', return_value=True):
            # Test various valid transitions
            self.assertTrue(self.handler.validate_transition(
                self.draft_doc, DOCUMENT_STATUS['GENERATED'], self.system_admin
            ))
            self.assertTrue(self.handler.validate_transition(
                self.generated_doc, DOCUMENT_STATUS['SENT'], self.system_admin
            ))
            self.assertTrue(self.handler.validate_transition(
                self.sent_doc, DOCUMENT_STATUS['PARTIALLY_SIGNED'], self.system_admin
            ))
    
    def test_validate_transition_invalid(self):
        """Test that validate_transition returns False for invalid transitions."""
        # Mock the StateMachine.validate_transition to return False
        with patch.object(StateMachine, 'validate_transition', return_value=False):
            # Test invalid transition
            self.assertFalse(self.handler.validate_transition(
                self.draft_doc, DOCUMENT_STATUS['COMPLETED'], self.borrower
            ))
    
    def test_validate_transition_document_specific(self):
        """Test document-specific validation rules."""
        # Mock the StateMachine.validate_transition to return True to isolate our rules
        with patch.object(StateMachine, 'validate_transition', return_value=True):
            # Test GENERATED requires document content
            doc_without_content = MockDocument(DOCUMENT_STATUS['DRAFT'], has_content=False)
            self.assertFalse(self.handler.validate_transition(
                doc_without_content, DOCUMENT_STATUS['GENERATED'], self.system_admin
            ))
            
            # Test SENT requires document to be ready for signatures
            with patch.object(self.draft_doc, 'is_ready_for_signatures', return_value=False):
                self.assertFalse(self.handler.validate_transition(
                    self.draft_doc, DOCUMENT_STATUS['SENT'], self.system_admin
                ))
            
            with patch.object(self.generated_doc, 'is_ready_for_signatures', return_value=True):
                self.assertTrue(self.handler.validate_transition(
                    self.generated_doc, DOCUMENT_STATUS['SENT'], self.system_admin
                ))
            
            # Test COMPLETED requires all signatures collected
            with patch.object(self.partially_signed_doc, 'are_all_signatures_collected', return_value=False):
                self.assertFalse(self.handler.validate_transition(
                    self.partially_signed_doc, DOCUMENT_STATUS['COMPLETED'], self.system_admin
                ))
            
            with patch.object(self.fully_signed_doc, 'are_all_signatures_collected', return_value=True):
                self.assertTrue(self.handler.validate_transition(
                    self.fully_signed_doc, DOCUMENT_STATUS['COMPLETED'], self.system_admin
                ))
    
    def test_pre_transition_actions(self):
        """Test pre-transition actions for document transitions."""
        # Test SENT preparation
        self.generated_doc.file_path = "/path/to/document"
        self.generated_doc.content = "document content"
        
        with patch.object(self.generated_doc, 'is_ready_for_signatures', return_value=True):
            # Add document package
            package = MagicMock()
            package.expiration_date = None
            self.generated_doc.document_package = package
            
            self.assertTrue(self.handler.pre_transition_actions(
                self.generated_doc, DOCUMENT_STATUS['SENT'], self.system_admin
            ))
            
            # Verify expiration date was set
            self.assertIsNotNone(package.expiration_date)
        
        # Test COMPLETED validation
        with patch.object(self.fully_signed_doc, 'are_all_signatures_collected', return_value=True):
            self.assertTrue(self.handler.pre_transition_actions(
                self.fully_signed_doc, DOCUMENT_STATUS['COMPLETED'], self.system_admin
            ))
    
    def test_post_transition_actions(self):
        """Test post-transition actions for document transitions."""
        # Test GENERATED schedules automatic transition
        with patch('apps.workflow.transitions.schedule_automatic_transition', return_value=True):
            self.assertTrue(self.handler.post_transition_actions(
                self.draft_doc, DOCUMENT_STATUS['DRAFT'], DOCUMENT_STATUS['GENERATED'], self.system_admin
            ))
        
        # Test SENT creates signature requests
        with patch('apps.documents.services.create_signature_requests', return_value=True):
            self.assertTrue(self.handler.post_transition_actions(
                self.generated_doc, DOCUMENT_STATUS['GENERATED'], DOCUMENT_STATUS['SENT'], self.system_admin
            ))
        
        # Test COMPLETED updates document package and application
        package = MagicMock()
        package.check_if_fully_executed.return_value = True
        
        app = MockApplication(APPLICATION_STATUS['PARTIALLY_EXECUTED'])
        package.application = app
        
        self.fully_signed_doc.document_package = package
        
        with patch('apps.loan.services.transition_application_state', return_value=True):
            self.assertTrue(self.handler.post_transition_actions(
                self.fully_signed_doc, DOCUMENT_STATUS['PARTIALLY_SIGNED'], DOCUMENT_STATUS['COMPLETED'], self.system_admin
            ))
    
    def test_transition(self):
        """Test the complete transition process for documents."""
        # Mock the necessary methods
        with patch.object(self.handler, 'validate_transition', return_value=True), \
             patch.object(self.handler, 'pre_transition_actions', return_value=True), \
             patch.object(self.handler, 'post_transition_actions', return_value=True), \
             patch.object(StateMachine, 'transition', return_value=True):
            
            # Test a successful transition
            self.assertTrue(self.handler.transition(
                self.draft_doc, DOCUMENT_STATUS['GENERATED'], self.system_admin, "Test reason"
            ))
        
        # Test failure cases
        with patch.object(self.handler, 'validate_transition', return_value=False):
            self.assertFalse(self.handler.transition(
                self.draft_doc, DOCUMENT_STATUS['COMPLETED'], self.system_admin, "Test reason"
            ))
        
        with patch.object(self.handler, 'validate_transition', return_value=True), \
             patch.object(self.handler, 'pre_transition_actions', return_value=False):
            self.assertFalse(self.handler.transition(
                self.draft_doc, DOCUMENT_STATUS['GENERATED'], self.system_admin, "Test reason"
            ))
        
        with patch.object(self.handler, 'validate_transition', return_value=True), \
             patch.object(self.handler, 'pre_transition_actions', return_value=True), \
             patch.object(StateMachine, 'transition', side_effect=ValidationError("Test error")):
            self.assertFalse(self.handler.transition(
                self.draft_doc, DOCUMENT_STATUS['GENERATED'], self.system_admin, "Test reason"
            ))


class FundingTransitionHandlerTestCase(TestCase):
    """Test case for the FundingTransitionHandler class."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.handler = FundingTransitionHandler()
        
        # Create mock users
        self.borrower = MockUser(USER_TYPES['BORROWER'])
        self.school_admin = MockUser(USER_TYPES['SCHOOL_ADMIN'])
        self.system_admin = MockUser(USER_TYPES['SYSTEM_ADMIN'])
        
        # Create mock funding requests in different states
        self.pending_enrollment = MockFundingRequest(FUNDING_STATUS['PENDING_ENROLLMENT'])
        self.enrollment_verified = MockFundingRequest(FUNDING_STATUS['ENROLLMENT_VERIFIED'])
        self.stipulation_review = MockFundingRequest(FUNDING_STATUS['STIPULATION_REVIEW'])
    
    def test_validate_transition_valid(self):
        """Test that validate_transition returns True for valid transitions."""
        # Mock the StateMachine.validate_transition to return True
        with patch.object(StateMachine, 'validate_transition', return_value=True):
            # Test various valid transitions
            self.assertTrue(self.handler.validate_transition(
                self.pending_enrollment, FUNDING_STATUS['ENROLLMENT_VERIFIED'], self.system_admin
            ))
            self.assertTrue(self.handler.validate_transition(
                self.enrollment_verified, FUNDING_STATUS['STIPULATION_REVIEW'], self.system_admin
            ))
    
    def test_validate_transition_invalid(self):
        """Test that validate_transition returns False for invalid transitions."""
        # Mock the StateMachine.validate_transition to return False
        with patch.object(StateMachine, 'validate_transition', return_value=False):
            # Test invalid transition
            self.assertFalse(self.handler.validate_transition(
                self.pending_enrollment, FUNDING_STATUS['FUNDING_COMPLETE'], self.borrower
            ))
    
    def test_validate_transition_funding_specific(self):
        """Test funding-specific validation rules."""
        # Mock the StateMachine.validate_transition to return True to isolate our rules
        with patch.object(StateMachine, 'validate_transition', return_value=True):
            # Test ENROLLMENT_VERIFIED requires enrollment verification
            self.assertFalse(self.handler.validate_transition(
                self.pending_enrollment, FUNDING_STATUS['ENROLLMENT_VERIFIED'], self.system_admin
            ))
            
            # Setup enrollment verification
            self.pending_enrollment.enrollment_verification = MagicMock()
            self.assertTrue(self.handler.validate_transition(
                self.pending_enrollment, FUNDING_STATUS['ENROLLMENT_VERIFIED'], self.system_admin
            ))
            
            # Test STIPULATIONS_COMPLETE requires all stipulations satisfied
            with patch.object(self.stipulation_review, 'are_all_stipulations_satisfied', return_value=False):
                self.assertFalse(self.handler.validate_transition(
                    self.stipulation_review, FUNDING_STATUS['STIPULATIONS_COMPLETE'], self.system_admin
                ))
            
            with patch.object(self.stipulation_review, 'are_all_stipulations_satisfied', return_value=True):
                self.assertTrue(self.handler.validate_transition(
                    self.stipulation_review, FUNDING_STATUS['STIPULATIONS_COMPLETE'], self.system_admin
                ))
            
            # Test APPROVED_FOR_FUNDING requires approval
            funding_approval = MockFundingRequest(FUNDING_STATUS['FUNDING_APPROVAL'])
            self.assertFalse(self.handler.validate_transition(
                funding_approval, FUNDING_STATUS['APPROVED_FOR_FUNDING'], self.system_admin
            ))
            
            funding_approval.approved_by = self.system_admin
            funding_approval.approved_at = timezone.now()
            self.assertTrue(self.handler.validate_transition(
                funding_approval, FUNDING_STATUS['APPROVED_FOR_FUNDING'], self.system_admin
            ))
    
    def test_pre_transition_actions(self):
        """Test pre-transition actions for funding transitions."""
        # Test STIPULATION_REVIEW preparation
        with patch('apps.funding.services.copy_stipulations_to_funding', return_value=True):
            # Mock stipulations.exists() to return False to trigger copy
            self.enrollment_verified.stipulations = MagicMock()
            self.enrollment_verified.stipulations.exists.return_value = False
            
            self.assertTrue(self.handler.pre_transition_actions(
                self.enrollment_verified, FUNDING_STATUS['STIPULATION_REVIEW'], self.system_admin
            ))
        
        # Test FUNDING_APPROVAL validation
        with patch.object(self.stipulation_review, 'are_all_stipulations_satisfied', return_value=True):
            self.assertTrue(self.handler.pre_transition_actions(
                self.stipulation_review, FUNDING_STATUS['FUNDING_APPROVAL'], self.system_admin
            ))
    
    def test_post_transition_actions(self):
        """Test post-transition actions for funding transitions."""
        # Test ENROLLMENT_VERIFIED schedules automatic transition
        with patch('apps.workflow.transitions.schedule_automatic_transition', return_value=True):
            self.assertTrue(self.handler.post_transition_actions(
                self.pending_enrollment, FUNDING_STATUS['PENDING_ENROLLMENT'], 
                FUNDING_STATUS['ENROLLMENT_VERIFIED'], self.system_admin
            ))
        
        # Test FUNDING_COMPLETE updates application status
        funding_complete = MockFundingRequest(FUNDING_STATUS['DISBURSED'])
        funding_complete.application = MagicMock()
        funding_complete.application.current_state = APPLICATION_STATUS['READY_TO_FUND']
        
        with patch('apps.loan.services.transition_application_state', return_value=True):
            self.assertTrue(self.handler.post_transition_actions(
                funding_complete, FUNDING_STATUS['DISBURSED'], 
                FUNDING_STATUS['FUNDING_COMPLETE'], self.system_admin
            ))
    
    def test_transition(self):
        """Test the complete transition process for funding."""
        # Mock the necessary methods
        with patch.object(self.handler, 'validate_transition', return_value=True), \
             patch.object(self.handler, 'pre_transition_actions', return_value=True), \
             patch.object(self.handler, 'post_transition_actions', return_value=True), \
             patch.object(StateMachine, 'transition', return_value=True):
            
            # Test a successful transition
            self.assertTrue(self.handler.transition(
                self.pending_enrollment, FUNDING_STATUS['ENROLLMENT_VERIFIED'], 
                self.system_admin, "Test reason"
            ))
        
        # Test failure cases
        with patch.object(self.handler, 'validate_transition', return_value=False):
            self.assertFalse(self.handler.transition(
                self.pending_enrollment, FUNDING_STATUS['FUNDING_COMPLETE'], 
                self.system_admin, "Test reason"
            ))
        
        with patch.object(self.handler, 'validate_transition', return_value=True), \
             patch.object(self.handler, 'pre_transition_actions', return_value=False):
            self.assertFalse(self.handler.transition(
                self.pending_enrollment, FUNDING_STATUS['ENROLLMENT_VERIFIED'], 
                self.system_admin, "Test reason"
            ))
        
        with patch.object(self.handler, 'validate_transition', return_value=True), \
             patch.object(self.handler, 'pre_transition_actions', return_value=True), \
             patch.object(StateMachine, 'transition', side_effect=ValidationError("Test error")):
            self.assertFalse(self.handler.transition(
                self.pending_enrollment, FUNDING_STATUS['ENROLLMENT_VERIFIED'], 
                self.system_admin, "Test reason"
            ))


class TransitionHandlerFactoryTestCase(TestCase):
    """Test case for the TransitionHandlerFactory class."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.factory = TransitionHandlerFactory()
        
        # Create mock entities
        self.application = MockApplication(APPLICATION_STATUS['DRAFT'])
        self.document = MockDocument(DOCUMENT_STATUS['DRAFT'])
        self.funding = MockFundingRequest(FUNDING_STATUS['PENDING_ENROLLMENT'])
    
    def test_get_handler(self):
        """Test that get_handler returns the correct handler for each workflow type."""
        # Test application handler
        handler = self.factory.get_handler(WORKFLOW_TYPES['APPLICATION'])
        self.assertIsInstance(handler, ApplicationTransitionHandler)
        
        # Test document handler
        handler = self.factory.get_handler(WORKFLOW_TYPES['DOCUMENT'])
        self.assertIsInstance(handler, DocumentTransitionHandler)
        
        # Test funding handler
        handler = self.factory.get_handler(WORKFLOW_TYPES['FUNDING'])
        self.assertIsInstance(handler, FundingTransitionHandler)
        
        # Test invalid workflow type
        with self.assertRaises(ValueError):
            self.factory.get_handler("invalid_type")
    
    def test_get_handler_for_entity(self):
        """Test that get_handler_for_entity returns the correct handler based on entity type."""
        # Test application entity
        handler = self.factory.get_handler_for_entity(self.application)
        self.assertIsInstance(handler, ApplicationTransitionHandler)
        
        # Test document entity
        handler = self.factory.get_handler_for_entity(self.document)
        self.assertIsInstance(handler, DocumentTransitionHandler)
        
        # Test funding entity
        handler = self.factory.get_handler_for_entity(self.funding)
        self.assertIsInstance(handler, FundingTransitionHandler)


class TransitionFunctionsTestCase(TestCase):
    """Test case for the transition functions that use the handlers."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create mock entities
        self.application = MockApplication(APPLICATION_STATUS['DRAFT'])
        self.document = MockDocument(DOCUMENT_STATUS['DRAFT'])
        self.funding = MockFundingRequest(FUNDING_STATUS['PENDING_ENROLLMENT'])
        
        # Create mock users
        self.system_admin = MockUser(USER_TYPES['SYSTEM_ADMIN'])
    
    def test_initialize_workflow(self):
        """Test that initialize_workflow correctly sets up a new workflow entity."""
        # Mock StateMachine.get_initial_state
        with patch.object(StateMachine, 'get_initial_state') as mock_get_initial_state, \
             patch('apps.workflow.transitions.create_workflow_tasks') as mock_create_tasks:
            
            # Configure mock to return different initial states for different workflow types
            mock_get_initial_state.return_value = APPLICATION_STATUS['DRAFT']
            
            # Test initializing an application
            result = initialize_workflow(self.application)
            self.assertTrue(result)
            self.assertEqual(self.application.current_state, APPLICATION_STATUS['DRAFT'])
            self.assertFalse(self.application.is_terminal)
            mock_create_tasks.assert_called_once()
            
            # Reset mocks
            mock_get_initial_state.reset_mock()
            mock_create_tasks.reset_mock()
            
            # Test with document
            mock_get_initial_state.return_value = DOCUMENT_STATUS['DRAFT']
            result = initialize_workflow(self.document)
            self.assertTrue(result)
            self.assertEqual(self.document.current_state, DOCUMENT_STATUS['DRAFT'])
            
            # Reset mocks
            mock_get_initial_state.reset_mock()
            mock_create_tasks.reset_mock()
            
            # Test with funding
            mock_get_initial_state.return_value = FUNDING_STATUS['PENDING_ENROLLMENT']
            result = initialize_workflow(self.funding)
            self.assertTrue(result)
            self.assertEqual(self.funding.current_state, FUNDING_STATUS['PENDING_ENROLLMENT'])
    
    def test_transition_application(self):
        """Test that transition_application correctly delegates to ApplicationTransitionHandler."""
        with patch.object(ApplicationTransitionHandler, 'transition') as mock_transition:
            mock_transition.return_value = True
            
            result = transition_application(
                self.application, APPLICATION_STATUS['SUBMITTED'], self.system_admin, "Test reason"
            )
            
            self.assertTrue(result)
            mock_transition.assert_called_once_with(
                self.application, APPLICATION_STATUS['SUBMITTED'], self.system_admin, "Test reason"
            )
    
    def test_transition_document(self):
        """Test that transition_document correctly delegates to DocumentTransitionHandler."""
        with patch.object(DocumentTransitionHandler, 'transition') as mock_transition:
            mock_transition.return_value = True
            
            result = transition_document(
                self.document, DOCUMENT_STATUS['GENERATED'], self.system_admin, "Test reason"
            )
            
            self.assertTrue(result)
            mock_transition.assert_called_once_with(
                self.document, DOCUMENT_STATUS['GENERATED'], self.system_admin, "Test reason"
            )
    
    def test_transition_funding(self):
        """Test that transition_funding correctly delegates to FundingTransitionHandler."""
        with patch.object(FundingTransitionHandler, 'transition') as mock_transition:
            mock_transition.return_value = True
            
            result = transition_funding(
                self.funding, FUNDING_STATUS['ENROLLMENT_VERIFIED'], self.system_admin, "Test reason"
            )
            
            self.assertTrue(result)
            mock_transition.assert_called_once_with(
                self.funding, FUNDING_STATUS['ENROLLMENT_VERIFIED'], self.system_admin, "Test reason"
            )
    
    def test_transition_entity(self):
        """Test that transition_entity correctly routes to the appropriate transition function."""
        with patch('apps.workflow.transitions.transition_application') as mock_app_transition, \
             patch('apps.workflow.transitions.transition_document') as mock_doc_transition, \
             patch('apps.workflow.transitions.transition_funding') as mock_fund_transition:
            
            mock_app_transition.return_value = True
            mock_doc_transition.return_value = True
            mock_fund_transition.return_value = True
            
            # Test with application
            result = transition_entity(
                self.application, APPLICATION_STATUS['SUBMITTED'], self.system_admin, "Test reason"
            )
            self.assertTrue(result)
            mock_app_transition.assert_called_once_with(
                self.application, APPLICATION_STATUS['SUBMITTED'], self.system_admin, "Test reason"
            )
            
            # Test with document
            result = transition_entity(
                self.document, DOCUMENT_STATUS['GENERATED'], self.system_admin, "Test reason"
            )
            self.assertTrue(result)
            mock_doc_transition.assert_called_once_with(
                self.document, DOCUMENT_STATUS['GENERATED'], self.system_admin, "Test reason"
            )
            
            # Test with funding
            result = transition_entity(
                self.funding, FUNDING_STATUS['ENROLLMENT_VERIFIED'], self.system_admin, "Test reason"
            )
            self.assertTrue(result)
            mock_fund_transition.assert_called_once_with(
                self.funding, FUNDING_STATUS['ENROLLMENT_VERIFIED'], self.system_admin, "Test reason"
            )
            
            # Test with invalid entity type
            invalid_entity = MockWorkflowEntity("invalid_type", "some_state")
            result = transition_entity(
                invalid_entity, "new_state", self.system_admin, "Test reason"
            )
            self.assertFalse(result)
    
    def test_handle_document_expiration(self):
        """Test that handle_document_expiration correctly processes expired documents."""
        with patch('apps.documents.models.Document.objects.filter') as mock_filter, \
             patch('apps.workflow.transitions.transition_document') as mock_transition:
            
            # Create mock documents
            mock_docs = [
                MockDocument(DOCUMENT_STATUS['SENT']),
                MockDocument(DOCUMENT_STATUS['PARTIALLY_SIGNED'])
            ]
            mock_filter.return_value = mock_docs
            mock_transition.return_value = True
            
            result = handle_document_expiration()
            
            self.assertEqual(result, 2)  # 2 documents were expired
            self.assertEqual(mock_transition.call_count, 2)
            
            # Check that transition was called with correct arguments
            for doc in mock_docs:
                mock_transition.assert_any_call(
                    document=doc,
                    to_state=DOCUMENT_STATUS['EXPIRED'],
                    user=None,
                    reason="Document expired due to package expiration date"
                )
    
    def test_process_automatic_transitions(self):
        """Test that process_automatic_transitions correctly processes scheduled transitions."""
        with patch('apps.workflow.models.AutomaticTransitionSchedule.objects.filter') as mock_filter, \
             patch('apps.workflow.transitions.transition_entity') as mock_transition:
            
            # Create mock schedules
            mock_schedule1 = MagicMock()
            mock_schedule1.content_object = self.application
            mock_schedule1.to_state = APPLICATION_STATUS['SUBMITTED']
            mock_schedule1.reason = "Auto transition"
            
            mock_schedule2 = MagicMock()
            mock_schedule2.content_object = self.document
            mock_schedule2.to_state = DOCUMENT_STATUS['GENERATED']
            mock_schedule2.reason = "Auto transition"
            
            mock_filter.return_value = [mock_schedule1, mock_schedule2]
            mock_transition.return_value = True
            
            result = process_automatic_transitions()
            
            self.assertEqual(result, 2)  # 2 transitions were processed
            self.assertEqual(mock_transition.call_count, 2)
            
            # Check that schedules were marked as executed
            self.assertTrue(mock_schedule1.is_executed)
            self.assertIsNotNone(mock_schedule1.executed_at)
            self.assertTrue(mock_schedule2.is_executed)
            self.assertIsNotNone(mock_schedule2.executed_at)
    
    def test_send_signature_reminders(self):
        """Test that send_signature_reminders correctly sends reminders for pending signatures."""
        with patch('apps.documents.models.SignatureRequest.objects.filter') as mock_filter:
            # Create mock signature requests
            mock_sig1 = MagicMock()
            mock_sig1.should_send_reminder.return_value = True
            
            mock_sig2 = MagicMock()
            mock_sig2.should_send_reminder.return_value = True
            
            mock_sig3 = MagicMock()
            mock_sig3.should_send_reminder.return_value = False
            
            mock_filter.return_value = [mock_sig1, mock_sig2, mock_sig3]
            
            result = send_signature_reminders()
            
            self.assertEqual(result, 2)  # 2 reminders were sent
            mock_sig1.send_reminder.assert_called_once()
            mock_sig2.send_reminder.assert_called_once()
            mock_sig3.send_reminder.assert_not_called()
    
    def test_check_sla_violations(self):
        """Test that check_sla_violations correctly identifies SLA violations."""
        with patch('apps.loan.models.LoanApplication.objects.filter') as mock_app_filter, \
             patch('apps.documents.models.Document.objects.filter') as mock_doc_filter, \
             patch('apps.funding.models.FundingRequest.objects.filter') as mock_fund_filter:
            
            # Create mock violated applications
            app1 = MockApplication(APPLICATION_STATUS['SUBMITTED'])
            app1.is_terminal = False
            app1.sla_due_at = timezone.now() - timezone.timedelta(hours=1)  # past due
            
            app2 = MockApplication(APPLICATION_STATUS['IN_REVIEW'])
            app2.is_terminal = False
            app2.sla_due_at = timezone.now() - timezone.timedelta(hours=2)  # past due
            
            app3 = MockApplication(APPLICATION_STATUS['APPROVED'])
            app3.is_terminal = False
            app3.sla_due_at = timezone.now() + timezone.timedelta(hours=1)  # not due yet
            
            mock_app_filter.return_value = [app1, app2]
            
            # Create mock violated documents
            doc1 = MockDocument(DOCUMENT_STATUS['SENT'])
            doc1.is_terminal = False
            doc1.sla_due_at = timezone.now() - timezone.timedelta(hours=1)  # past due
            
            mock_doc_filter.return_value = [doc1]
            
            # Create mock violated funding requests
            fund1 = MockFundingRequest(FUNDING_STATUS['STIPULATION_REVIEW'])
            fund1.is_terminal = False
            fund1.sla_due_at = timezone.now() - timezone.timedelta(hours=1)  # past due
            
            mock_fund_filter.return_value = [fund1]
            
            result = check_sla_violations()
            
            # Verify results
            self.assertEqual(len(result), 3)  # 3 workflow types
            self.assertEqual(len(result[WORKFLOW_TYPES['APPLICATION']]), 2)  # 2 states with violations
            self.assertEqual(result[WORKFLOW_TYPES['APPLICATION']][APPLICATION_STATUS['SUBMITTED']], 1)
            self.assertEqual(result[WORKFLOW_TYPES['APPLICATION']][APPLICATION_STATUS['IN_REVIEW']], 1)
            self.assertEqual(len(result[WORKFLOW_TYPES['DOCUMENT']]), 1)  # 1 state with violations
            self.assertEqual(result[WORKFLOW_TYPES['DOCUMENT']][DOCUMENT_STATUS['SENT']], 1)
            self.assertEqual(len(result[WORKFLOW_TYPES['FUNDING']]), 1)  # 1 state with violations
            self.assertEqual(result[WORKFLOW_TYPES['FUNDING']][FUNDING_STATUS['STIPULATION_REVIEW']], 1)