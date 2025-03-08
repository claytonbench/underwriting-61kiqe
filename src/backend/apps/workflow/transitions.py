"""
Implements transition handlers for workflow state changes in the loan management system.

This module provides specialized transition handlers for different entity types 
(applications, documents, funding) and handles side effects of state transitions 
such as task creation, notifications, and automatic transitions.
"""

import logging
from django.db import transaction  # Django 4.2+
from django.utils import timezone  # Django 4.2+
from django.core.exceptions import ValidationError  # Django 4.2+

from .state_machine import (
    StateMachine, 
    create_transition_history, 
    create_workflow_tasks,
    process_workflow_notifications,
    schedule_automatic_transition,
    get_transition_event
)
from .constants import (
    WORKFLOW_TYPES,
    WORKFLOW_TRANSITION_EVENTS
)
from ...utils.constants import (
    APPLICATION_STATUS,
    DOCUMENT_STATUS,
    FUNDING_STATUS
)

# Setup logger
logger = logging.getLogger(__name__)


def initialize_workflow(entity):
    """
    Initializes a workflow for an entity by setting its initial state.
    
    Args:
        entity: The entity to initialize workflow for
        
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    try:
        workflow_type = entity.get_workflow_type()
        state_machine = StateMachine(workflow_type)
        
        # Get the initial state for this workflow type
        initial_state = state_machine.get_initial_state()
        
        # Set the initial state on the entity
        entity.current_state = initial_state
        entity.state_changed_at = timezone.now()
        entity.is_terminal = False
        entity.save()
        
        # Create any required workflow tasks for the initial state
        create_workflow_tasks(entity, initial_state)
        
        return True
    except Exception as e:
        logger.error(f"Error initializing workflow for entity {entity}: {str(e)}", exc_info=True)
        return False


class ApplicationTransitionHandler:
    """
    Specialized handler for application state transitions with business logic.
    """
    
    def __init__(self):
        """
        Initializes the handler with a state machine for applications.
        """
        self.state_machine = StateMachine(WORKFLOW_TYPES['APPLICATION'])
    
    def validate_transition(self, application, to_state, user):
        """
        Validates if a transition is allowed with application-specific rules.
        
        Args:
            application: The application to validate transition for
            to_state: The target state
            user: The user initiating the transition
            
        Returns:
            bool: True if transition is valid, False otherwise
        """
        # First check if the basic transition is allowed by the state machine
        if not self.state_machine.validate_transition(application.current_state, to_state, user):
            logger.warning(f"Invalid transition from {application.current_state} to {to_state} for application {application.id}")
            return False
        
        # Application-specific validation
        try:
            # Submitted state requires application to be complete
            if to_state == APPLICATION_STATUS['SUBMITTED']:
                if not application.is_complete():
                    logger.warning(f"Application {application.id} is not complete, cannot transition to SUBMITTED")
                    return False
            
            # Approved state requires an underwriting decision
            elif to_state == APPLICATION_STATUS['APPROVED']:
                if not hasattr(application, 'underwriting_decision') or not application.underwriting_decision:
                    logger.warning(f"Application {application.id} has no underwriting decision, cannot transition to APPROVED")
                    return False
            
            # Commitment acceptance requires school admin
            elif to_state == APPLICATION_STATUS['COMMITMENT_ACCEPTED']:
                if not user or user.user_type != 'school_admin':
                    logger.warning(f"User {user} is not authorized to accept commitment for application {application.id}")
                    return False
            
            # Fully executed state requires all documents to be signed
            elif to_state == APPLICATION_STATUS['FULLY_EXECUTED']:
                document_package = getattr(application, 'document_package', None)
                if not document_package or not document_package.is_fully_executed():
                    logger.warning(f"Document package for application {application.id} is not fully executed")
                    return False
            
            # QC approval requires QC user
            elif to_state == APPLICATION_STATUS['QC_APPROVED']:
                if not user or user.user_type != 'qc':
                    logger.warning(f"User {user} is not authorized to approve QC for application {application.id}")
                    return False
            
            # Funded state requires funding to be complete
            elif to_state == APPLICATION_STATUS['FUNDED']:
                funding_request = getattr(application, 'funding_request', None)
                if not funding_request or funding_request.current_state != FUNDING_STATUS['FUNDING_COMPLETE']:
                    logger.warning(f"Funding for application {application.id} is not complete")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error validating application transition: {str(e)}", exc_info=True)
            return False
    
    def pre_transition_actions(self, application, to_state, user):
        """
        Performs actions required before transitioning an application.
        
        Args:
            application: The application to transition
            to_state: The target state
            user: The user initiating the transition
            
        Returns:
            bool: True if pre-transition actions were successful, False otherwise
        """
        try:
            # Submitted state: validate application data
            if to_state == APPLICATION_STATUS['SUBMITTED']:
                # Perform final validation checks
                if not application.validate_for_submission():
                    logger.warning(f"Application {application.id} failed validation for submission")
                    return False
            
            # In Review state: prepare for underwriting
            elif to_state == APPLICATION_STATUS['IN_REVIEW']:
                # If the application is not already assigned to an underwriter, assign one
                if not application.assigned_underwriter:
                    from ..underwriting.services import assign_underwriter
                    success = assign_underwriter(application)
                    if not success:
                        logger.warning(f"Failed to assign underwriter for application {application.id}")
                        return False
            
            # Approved state: validate underwriting decision
            elif to_state == APPLICATION_STATUS['APPROVED']:
                # Ensure there's a valid underwriting decision with approval details
                if not hasattr(application, 'underwriting_decision'):
                    logger.warning(f"Application {application.id} has no underwriting decision")
                    return False
                
                decision = application.underwriting_decision
                if not decision.approved_amount or not decision.interest_rate or not decision.term_months:
                    logger.warning(f"Application {application.id} underwriting decision missing required approval details")
                    return False
            
            # Commitment Sent state: prepare commitment letter
            elif to_state == APPLICATION_STATUS['COMMITMENT_SENT']:
                # Generate commitment letter document
                from ..documents.services import generate_commitment_letter
                commitment_letter = generate_commitment_letter(application, user)
                if not commitment_letter:
                    logger.warning(f"Failed to generate commitment letter for application {application.id}")
                    return False
            
            # Documents Sent state: prepare document package
            elif to_state == APPLICATION_STATUS['DOCUMENTS_SENT']:
                # Generate loan document package
                from ..documents.services import generate_document_package
                document_package = generate_document_package(application, user)
                if not document_package:
                    logger.warning(f"Failed to generate document package for application {application.id}")
                    return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error in pre-transition actions for application {application.id}: {str(e)}", exc_info=True)
            return False
    
    def post_transition_actions(self, application, from_state, to_state, user):
        """
        Performs actions required after transitioning an application.
        
        Args:
            application: The application that was transitioned
            from_state: The original state
            to_state: The new state
            user: The user who initiated the transition
            
        Returns:
            bool: True if post-transition actions were successful, False otherwise
        """
        try:
            # Submitted state: create underwriting queue entry
            if to_state == APPLICATION_STATUS['SUBMITTED']:
                from ..underwriting.services import create_underwriting_queue_entry
                success = create_underwriting_queue_entry(application)
                if not success:
                    logger.warning(f"Failed to create underwriting queue entry for application {application.id}")
                    return False
            
            # Approved state: schedule automatic transition to COMMITMENT_SENT
            elif to_state == APPLICATION_STATUS['APPROVED']:
                # Schedule automatic transition to send commitment letter
                # This typically happens with a small delay to allow for any system processing
                schedule_automatic_transition(
                    entity=application,
                    from_state=APPLICATION_STATUS['APPROVED'],
                    to_state=APPLICATION_STATUS['COMMITMENT_SENT'],
                    reason="Automatic transition to send commitment letter after approval",
                    delay_hours=1
                )
            
            # Commitment Accepted state: prepare document package
            elif to_state == APPLICATION_STATUS['COMMITMENT_ACCEPTED']:
                # Transition to the next state (DOCUMENTS_SENT) with a delay
                # to allow for document package preparation
                schedule_automatic_transition(
                    entity=application,
                    from_state=APPLICATION_STATUS['COMMITMENT_ACCEPTED'],
                    to_state=APPLICATION_STATUS['DOCUMENTS_SENT'],
                    reason="Automatic transition to send document package after commitment acceptance",
                    delay_hours=1
                )
            
            # QC Approved state: create funding request
            elif to_state == APPLICATION_STATUS['QC_APPROVED']:
                from ..funding.services import create_funding_request
                funding_request = create_funding_request(application, user)
                if not funding_request:
                    logger.warning(f"Failed to create funding request for application {application.id}")
                    return False
                
                # Schedule transition to READY_TO_FUND
                schedule_automatic_transition(
                    entity=application,
                    from_state=APPLICATION_STATUS['QC_APPROVED'],
                    to_state=APPLICATION_STATUS['READY_TO_FUND'],
                    reason="Automatic transition to ready to fund after QC approval",
                    delay_hours=0.5
                )
                
            return True
            
        except Exception as e:
            logger.error(f"Error in post-transition actions for application {application.id}: {str(e)}", exc_info=True)
            # We'll return True anyway since the transition itself was successful
            # and post-transition errors should be logged but not revert the transition
            return True
    
    def transition(self, application, to_state, user, reason=None):
        """
        Executes a state transition for an application with business logic.
        
        Args:
            application: The application to transition
            to_state: The target state
            user: The user initiating the transition
            reason: The reason for the transition
            
        Returns:
            bool: True if transition was successful, False otherwise
        """
        # Validate the transition first
        if not self.validate_transition(application, to_state, user):
            logger.error(f"Invalid transition from {application.current_state} to {to_state} for application {application.id}")
            return False
        
        # Use a transaction to ensure data integrity
        with transaction.atomic():
            # Perform pre-transition actions
            if not self.pre_transition_actions(application, to_state, user):
                logger.error(f"Pre-transition actions failed for application {application.id} to state {to_state}")
                return False
            
            # Store the original state for history and post-transition actions
            from_state = application.current_state
            
            # Perform the actual state transition
            try:
                self.state_machine.transition(application, to_state, user, reason)
            except ValidationError as e:
                logger.error(f"State machine transition failed for application {application.id}: {str(e)}")
                return False
            
            # Perform post-transition actions
            post_result = self.post_transition_actions(application, from_state, to_state, user)
            if not post_result:
                logger.warning(f"Post-transition actions failed for application {application.id}, but state change was successful")
                # We don't return False here as the transition itself was successful
                
            return True


class DocumentTransitionHandler:
    """
    Specialized handler for document state transitions with business logic.
    """
    
    def __init__(self):
        """
        Initializes the handler with a state machine for documents.
        """
        self.state_machine = StateMachine(WORKFLOW_TYPES['DOCUMENT'])
    
    def validate_transition(self, document, to_state, user):
        """
        Validates if a transition is allowed with document-specific rules.
        
        Args:
            document: The document to validate transition for
            to_state: The target state
            user: The user initiating the transition
            
        Returns:
            bool: True if transition is valid, False otherwise
        """
        # First check if the basic transition is allowed by the state machine
        if not self.state_machine.validate_transition(document.current_state, to_state, user):
            logger.warning(f"Invalid transition from {document.current_state} to {to_state} for document {document.id}")
            return False
        
        # Document-specific validation
        try:
            # Generated state requires document content
            if to_state == DOCUMENT_STATUS['GENERATED']:
                if not document.content or not document.file_path:
                    logger.warning(f"Document {document.id} has no content, cannot transition to GENERATED")
                    return False
            
            # Sent state requires document to be ready for signatures
            elif to_state == DOCUMENT_STATUS['SENT']:
                if not document.is_ready_for_signatures():
                    logger.warning(f"Document {document.id} is not ready for signatures, cannot transition to SENT")
                    return False
            
            # Completed state requires all signatures
            elif to_state == DOCUMENT_STATUS['COMPLETED']:
                if not document.are_all_signatures_collected():
                    logger.warning(f"Document {document.id} is missing signatures, cannot transition to COMPLETED")
                    return False
            
            # Expired state requires document to have reached expiration date
            elif to_state == DOCUMENT_STATUS['EXPIRED']:
                package = getattr(document, 'document_package', None)
                if not package or not package.expiration_date or package.expiration_date > timezone.now():
                    logger.warning(f"Document {document.id} has not expired, cannot transition to EXPIRED")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error validating document transition: {str(e)}", exc_info=True)
            return False
    
    def pre_transition_actions(self, document, to_state, user):
        """
        Performs actions required before transitioning a document.
        
        Args:
            document: The document to transition
            to_state: The target state
            user: The user initiating the transition
            
        Returns:
            bool: True if pre-transition actions were successful, False otherwise
        """
        try:
            # Sent state: prepare for signature requests
            if to_state == DOCUMENT_STATUS['SENT']:
                # Ensure document is properly generated
                if not document.file_path or not document.content:
                    logger.warning(f"Document {document.id} content not available for sending")
                    return False
                
                # Validate document package
                package = getattr(document, 'document_package', None)
                if not package:
                    logger.warning(f"Document {document.id} has no associated package")
                    return False
                
                # Ensure package has an expiration date
                if not package.expiration_date:
                    # Set expiration date 90 days from now by default
                    package.expiration_date = timezone.now() + timezone.timedelta(days=90)
                    package.save()
            
            # Completed state: validate all signatures
            elif to_state == DOCUMENT_STATUS['COMPLETED']:
                # Double-check that all required signatures are present
                if not document.are_all_signatures_collected():
                    logger.warning(f"Document {document.id} is missing signatures, cannot transition to COMPLETED")
                    return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error in pre-transition actions for document {document.id}: {str(e)}", exc_info=True)
            return False
    
    def post_transition_actions(self, document, from_state, to_state, user):
        """
        Performs actions required after transitioning a document.
        
        Args:
            document: The document that was transitioned
            from_state: The original state
            to_state: The new state
            user: The user who initiated the transition
            
        Returns:
            bool: True if post-transition actions were successful, False otherwise
        """
        try:
            # Generated state: schedule automatic transition to SENT
            if to_state == DOCUMENT_STATUS['GENERATED']:
                # Schedule automatic transition to send document for signatures
                schedule_automatic_transition(
                    entity=document,
                    from_state=DOCUMENT_STATUS['GENERATED'],
                    to_state=DOCUMENT_STATUS['SENT'],
                    reason="Automatic transition to send document for signatures",
                    delay_hours=0.5
                )
            
            # Sent state: create signature requests
            elif to_state == DOCUMENT_STATUS['SENT']:
                from ..documents.services import create_signature_requests
                success = create_signature_requests(document, user)
                if not success:
                    logger.warning(f"Failed to create signature requests for document {document.id}")
                    return False
            
            # Completed state: update document package status
            elif to_state == DOCUMENT_STATUS['COMPLETED']:
                # Update the document package if all documents are complete
                package = getattr(document, 'document_package', None)
                if package and package.check_if_fully_executed():
                    # If all documents in the package are complete, update application status
                    application = getattr(package, 'application', None)
                    if application and application.current_state == APPLICATION_STATUS['PARTIALLY_EXECUTED']:
                        # Transition application to FULLY_EXECUTED
                        from ..loan.services import transition_application_state
                        success = transition_application_state(
                            application=application,
                            to_state=APPLICATION_STATUS['FULLY_EXECUTED'],
                            user=user,
                            reason="Document package fully executed"
                        )
                        if not success:
                            logger.warning(f"Failed to transition application {application.id} to FULLY_EXECUTED")
                            # We don't return False here as the document transition itself was successful
            
            # Expired state: update document package and application
            elif to_state == DOCUMENT_STATUS['EXPIRED']:
                package = getattr(document, 'document_package', None)
                if package:
                    # If any document in the package expires, the entire package is considered expired
                    # Check if application needs to be updated
                    application = getattr(package, 'application', None)
                    if application and application.current_state in [
                        APPLICATION_STATUS['DOCUMENTS_SENT'], 
                        APPLICATION_STATUS['PARTIALLY_EXECUTED']
                    ]:
                        # Transition application to DOCUMENTS_EXPIRED
                        from ..loan.services import transition_application_state
                        success = transition_application_state(
                            application=application,
                            to_state=APPLICATION_STATUS['DOCUMENTS_EXPIRED'],
                            user=user,
                            reason="Document package expired"
                        )
                        if not success:
                            logger.warning(f"Failed to transition application {application.id} to DOCUMENTS_EXPIRED")
                            # We don't return False here as the document transition itself was successful
                
            return True
            
        except Exception as e:
            logger.error(f"Error in post-transition actions for document {document.id}: {str(e)}", exc_info=True)
            # We'll return True anyway since the transition itself was successful
            # and post-transition errors should be logged but not revert the transition
            return True
    
    def transition(self, document, to_state, user, reason=None):
        """
        Executes a state transition for a document with business logic.
        
        Args:
            document: The document to transition
            to_state: The target state
            user: The user initiating the transition
            reason: The reason for the transition
            
        Returns:
            bool: True if transition was successful, False otherwise
        """
        # Validate the transition first
        if not self.validate_transition(document, to_state, user):
            logger.error(f"Invalid transition from {document.current_state} to {to_state} for document {document.id}")
            return False
        
        # Use a transaction to ensure data integrity
        with transaction.atomic():
            # Perform pre-transition actions
            if not self.pre_transition_actions(document, to_state, user):
                logger.error(f"Pre-transition actions failed for document {document.id} to state {to_state}")
                return False
            
            # Store the original state for history and post-transition actions
            from_state = document.current_state
            
            # Perform the actual state transition
            try:
                self.state_machine.transition(document, to_state, user, reason)
            except ValidationError as e:
                logger.error(f"State machine transition failed for document {document.id}: {str(e)}")
                return False
            
            # Perform post-transition actions
            post_result = self.post_transition_actions(document, from_state, to_state, user)
            if not post_result:
                logger.warning(f"Post-transition actions failed for document {document.id}, but state change was successful")
                # We don't return False here as the transition itself was successful
                
            return True


class FundingTransitionHandler:
    """
    Specialized handler for funding state transitions with business logic.
    """
    
    def __init__(self):
        """
        Initializes the handler with a state machine for funding.
        """
        self.state_machine = StateMachine(WORKFLOW_TYPES['FUNDING'])
    
    def validate_transition(self, funding_request, to_state, user):
        """
        Validates if a transition is allowed with funding-specific rules.
        
        Args:
            funding_request: The funding request to validate transition for
            to_state: The target state
            user: The user initiating the transition
            
        Returns:
            bool: True if transition is valid, False otherwise
        """
        # First check if the basic transition is allowed by the state machine
        if not self.state_machine.validate_transition(funding_request.current_state, to_state, user):
            logger.warning(f"Invalid transition from {funding_request.current_state} to {to_state} for funding request {funding_request.id}")
            return False
        
        # Funding-specific validation
        try:
            # Enrollment verified state requires enrollment verification
            if to_state == FUNDING_STATUS['ENROLLMENT_VERIFIED']:
                if not hasattr(funding_request, 'enrollment_verification') or not funding_request.enrollment_verification:
                    logger.warning(f"Funding request {funding_request.id} has no enrollment verification")
                    return False
            
            # Stipulations complete state requires all stipulations to be satisfied
            elif to_state == FUNDING_STATUS['STIPULATIONS_COMPLETE']:
                if not funding_request.are_all_stipulations_satisfied():
                    logger.warning(f"Funding request {funding_request.id} has unsatisfied stipulations")
                    return False
            
            # Approved for funding state requires approval information
            elif to_state == FUNDING_STATUS['APPROVED_FOR_FUNDING']:
                if not funding_request.approved_by or not funding_request.approved_at:
                    logger.warning(f"Funding request {funding_request.id} missing approval information")
                    return False
            
            # Scheduled for disbursement state requires disbursement to be scheduled
            elif to_state == FUNDING_STATUS['SCHEDULED_FOR_DISBURSEMENT']:
                if not funding_request.disbursements.exists():
                    logger.warning(f"Funding request {funding_request.id} has no scheduled disbursements")
                    return False
            
            # Disbursed state requires disbursement to be processed
            elif to_state == FUNDING_STATUS['DISBURSED']:
                if not funding_request.disbursements.filter(status='processed').exists():
                    logger.warning(f"Funding request {funding_request.id} has no processed disbursements")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error validating funding transition: {str(e)}", exc_info=True)
            return False
    
    def pre_transition_actions(self, funding_request, to_state, user):
        """
        Performs actions required before transitioning a funding request.
        
        Args:
            funding_request: The funding request to transition
            to_state: The target state
            user: The user initiating the transition
            
        Returns:
            bool: True if pre-transition actions were successful, False otherwise
        """
        try:
            # Stipulation review state: prepare for stipulation review
            if to_state == FUNDING_STATUS['STIPULATION_REVIEW']:
                # Ensure stipulations are defined for this request
                if not funding_request.stipulations.exists():
                    # Copy stipulations from the application
                    application = getattr(funding_request, 'application', None)
                    if application and hasattr(application, 'stipulations'):
                        from ..funding.services import copy_stipulations_to_funding
                        success = copy_stipulations_to_funding(application, funding_request)
                        if not success:
                            logger.warning(f"Failed to copy stipulations for funding request {funding_request.id}")
                            return False
            
            # Funding approval state: validate stipulations are complete
            elif to_state == FUNDING_STATUS['FUNDING_APPROVAL']:
                # Ensure all stipulations are satisfied
                if not funding_request.are_all_stipulations_satisfied():
                    logger.warning(f"Funding request {funding_request.id} has unsatisfied stipulations")
                    return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error in pre-transition actions for funding request {funding_request.id}: {str(e)}", exc_info=True)
            return False
    
    def post_transition_actions(self, funding_request, from_state, to_state, user):
        """
        Performs actions required after transitioning a funding request.
        
        Args:
            funding_request: The funding request that was transitioned
            from_state: The original state
            to_state: The new state
            user: The user who initiated the transition
            
        Returns:
            bool: True if post-transition actions were successful, False otherwise
        """
        try:
            # Enrollment verified state: transition to stipulation review
            if to_state == FUNDING_STATUS['ENROLLMENT_VERIFIED']:
                # Schedule automatic transition to stipulation review
                schedule_automatic_transition(
                    entity=funding_request,
                    from_state=FUNDING_STATUS['ENROLLMENT_VERIFIED'],
                    to_state=FUNDING_STATUS['STIPULATION_REVIEW'],
                    reason="Automatic transition to review stipulations after enrollment verification",
                    delay_hours=0.5
                )
            
            # Funding complete state: update application status
            elif to_state == FUNDING_STATUS['FUNDING_COMPLETE']:
                # Update the application status to FUNDED
                application = getattr(funding_request, 'application', None)
                if application and application.current_state == APPLICATION_STATUS['READY_TO_FUND']:
                    # Transition application to FUNDED
                    from ..loan.services import transition_application_state
                    success = transition_application_state(
                        application=application,
                        to_state=APPLICATION_STATUS['FUNDED'],
                        user=user,
                        reason="Funding complete"
                    )
                    if not success:
                        logger.warning(f"Failed to transition application {application.id} to FUNDED")
                        return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error in post-transition actions for funding request {funding_request.id}: {str(e)}", exc_info=True)
            # We'll return True anyway since the transition itself was successful
            # and post-transition errors should be logged but not revert the transition
            return True
    
    def transition(self, funding_request, to_state, user, reason=None):
        """
        Executes a state transition for a funding request with business logic.
        
        Args:
            funding_request: The funding request to transition
            to_state: The target state
            user: The user initiating the transition
            reason: The reason for the transition
            
        Returns:
            bool: True if transition was successful, False otherwise
        """
        # Validate the transition first
        if not self.validate_transition(funding_request, to_state, user):
            logger.error(f"Invalid transition from {funding_request.current_state} to {to_state} for funding request {funding_request.id}")
            return False
        
        # Use a transaction to ensure data integrity
        with transaction.atomic():
            # Perform pre-transition actions
            if not self.pre_transition_actions(funding_request, to_state, user):
                logger.error(f"Pre-transition actions failed for funding request {funding_request.id} to state {to_state}")
                return False
            
            # Store the original state for history and post-transition actions
            from_state = funding_request.current_state
            
            # Perform the actual state transition
            try:
                self.state_machine.transition(funding_request, to_state, user, reason)
            except ValidationError as e:
                logger.error(f"State machine transition failed for funding request {funding_request.id}: {str(e)}")
                return False
            
            # Perform post-transition actions
            post_result = self.post_transition_actions(funding_request, from_state, to_state, user)
            if not post_result:
                logger.warning(f"Post-transition actions failed for funding request {funding_request.id}, but state change was successful")
                # We don't return False here as the transition itself was successful
                
            return True


class TransitionHandlerFactory:
    """
    Factory class for creating appropriate transition handlers based on workflow type.
    """
    
    @staticmethod
    def get_handler(workflow_type):
        """
        Returns the appropriate transition handler for a workflow type.
        
        Args:
            workflow_type: The workflow type to get a handler for
            
        Returns:
            The appropriate transition handler instance
            
        Raises:
            ValueError: If an invalid workflow type is provided
        """
        if workflow_type == WORKFLOW_TYPES['APPLICATION']:
            return ApplicationTransitionHandler()
        elif workflow_type == WORKFLOW_TYPES['DOCUMENT']:
            return DocumentTransitionHandler()
        elif workflow_type == WORKFLOW_TYPES['FUNDING']:
            return FundingTransitionHandler()
        else:
            raise ValueError(f"Unsupported workflow type: {workflow_type}")
    
    @staticmethod
    def get_handler_for_entity(entity):
        """
        Returns the appropriate transition handler for an entity.
        
        Args:
            entity: The entity to get a handler for
            
        Returns:
            The appropriate transition handler instance
        """
        workflow_type = entity.get_workflow_type()
        return TransitionHandlerFactory.get_handler(workflow_type)


def transition_application(application, to_state, user, reason=None):
    """
    Handles application-specific transition logic.
    
    Args:
        application: The application to transition
        to_state: The target state
        user: The user initiating the transition
        reason: The reason for the transition
        
    Returns:
        bool: True if transition was successful, False otherwise
    """
    handler = ApplicationTransitionHandler()
    return handler.transition(application, to_state, user, reason)


def transition_document(document, to_state, user, reason=None):
    """
    Handles document-specific transition logic.
    
    Args:
        document: The document to transition
        to_state: The target state
        user: The user initiating the transition
        reason: The reason for the transition
        
    Returns:
        bool: True if transition was successful, False otherwise
    """
    handler = DocumentTransitionHandler()
    return handler.transition(document, to_state, user, reason)


def transition_funding(funding_request, to_state, user, reason=None):
    """
    Handles funding-specific transition logic.
    
    Args:
        funding_request: The funding request to transition
        to_state: The target state
        user: The user initiating the transition
        reason: The reason for the transition
        
    Returns:
        bool: True if transition was successful, False otherwise
    """
    handler = FundingTransitionHandler()
    return handler.transition(funding_request, to_state, user, reason)


def transition_entity(entity, to_state, user, reason=None):
    """
    Generic function to transition any workflow entity to a new state.
    
    Args:
        entity: The entity to transition
        to_state: The target state
        user: The user initiating the transition
        reason: The reason for the transition
        
    Returns:
        bool: True if transition was successful, False otherwise
    """
    try:
        workflow_type = entity.get_workflow_type()
        
        if workflow_type == WORKFLOW_TYPES['APPLICATION']:
            return transition_application(entity, to_state, user, reason)
        elif workflow_type == WORKFLOW_TYPES['DOCUMENT']:
            return transition_document(entity, to_state, user, reason)
        elif workflow_type == WORKFLOW_TYPES['FUNDING']:
            return transition_funding(entity, to_state, user, reason)
        else:
            logger.error(f"Unknown workflow type: {workflow_type}")
            return False
    except Exception as e:
        logger.error(f"Error transitioning entity: {str(e)}", exc_info=True)
        return False


def handle_document_expiration():
    """
    Handles the expiration of documents that have passed their expiration date.
    
    Returns:
        int: Number of documents expired
    """
    from ..documents.models import Document, DocumentPackage
    
    now = timezone.now()
    expired_count = 0
    
    try:
        # Find document packages that have expired
        expired_packages = DocumentPackage.objects.filter(
            expiration_date__lt=now,
            is_deleted=False
        )
        
        # Find documents from those packages that are in SENT or PARTIALLY_SIGNED state
        documents = Document.objects.filter(
            document_package__in=expired_packages,
            current_state__in=[DOCUMENT_STATUS['SENT'], DOCUMENT_STATUS['PARTIALLY_SIGNED']],
            is_deleted=False
        )
        
        # Transition each document to EXPIRED state
        for document in documents:
            if transition_document(
                document=document,
                to_state=DOCUMENT_STATUS['EXPIRED'],
                user=None,
                reason="Document expired due to package expiration date"
            ):
                expired_count += 1
                logger.info(f"Document {document.id} expired")
        
        return expired_count
    except Exception as e:
        logger.error(f"Error handling document expiration: {str(e)}", exc_info=True)
        return expired_count


def process_automatic_transitions():
    """
    Processes all scheduled automatic transitions that are due.
    
    Returns:
        int: Number of transitions processed
    """
    from .models import AutomaticTransitionSchedule
    
    now = timezone.now()
    success_count = 0
    
    try:
        # Find scheduled transitions that are due and not yet executed
        scheduled_transitions = AutomaticTransitionSchedule.objects.filter(
            scheduled_date__lte=now,
            is_executed=False,
            is_deleted=False
        )
        
        # Process each scheduled transition
        for schedule in scheduled_transitions:
            try:
                entity = schedule.content_object
                if entity:
                    # Use transition_entity to perform the transition
                    if transition_entity(
                        entity=entity,
                        to_state=schedule.to_state,
                        user=None,
                        reason=schedule.reason
                    ):
                        success_count += 1
                        # Mark schedule as executed
                        schedule.is_executed = True
                        schedule.executed_at = timezone.now()
                        schedule.save()
                        logger.info(f"Automatic transition executed: {schedule}")
                    else:
                        logger.warning(f"Automatic transition failed: {schedule}")
                else:
                    logger.warning(f"Entity not found for scheduled transition: {schedule}")
                    # Mark as executed to prevent repeated attempts
                    schedule.is_executed = True
                    schedule.executed_at = timezone.now()
                    schedule.save()
            except Exception as e:
                logger.error(f"Error processing scheduled transition {schedule.id}: {str(e)}", exc_info=True)
        
        return success_count
    except Exception as e:
        logger.error(f"Error processing automatic transitions: {str(e)}", exc_info=True)
        return success_count


def send_signature_reminders():
    """
    Sends reminders for pending signatures.
    
    Returns:
        int: Number of reminders sent
    """
    from ..documents.models import SignatureRequest
    from ...utils.constants import SIGNATURE_STATUS
    
    reminder_count = 0
    
    try:
        # Find signature requests in PENDING status that are eligible for reminders
        pending_signatures = SignatureRequest.objects.filter(
            status=SIGNATURE_STATUS['PENDING'],
            is_deleted=False
        )
        
        # Send reminder for each eligible signature request
        for signature_request in pending_signatures:
            # Check if a reminder should be sent based on time since last reminder
            # and proximity to expiration date
            if signature_request.should_send_reminder():
                try:
                    signature_request.send_reminder()
                    reminder_count += 1
                    logger.info(f"Signature reminder sent for request {signature_request.id}")
                except Exception as e:
                    logger.error(f"Error sending signature reminder for request {signature_request.id}: {str(e)}", exc_info=True)
        
        return reminder_count
    except Exception as e:
        logger.error(f"Error sending signature reminders: {str(e)}", exc_info=True)
        return reminder_count


def check_sla_violations():
    """
    Checks for SLA violations across all workflow entities.
    
    Returns:
        dict: Dictionary of SLA violations by workflow type
    """
    from ..loan.models import LoanApplication
    from ..documents.models import Document
    from ..funding.models import FundingRequest
    
    now = timezone.now()
    results = {
        WORKFLOW_TYPES['APPLICATION']: {},
        WORKFLOW_TYPES['DOCUMENT']: {},
        WORKFLOW_TYPES['FUNDING']: {}
    }
    
    try:
        # Check application SLA violations
        violated_applications = LoanApplication.objects.filter(
            sla_due_at__lt=now,
            is_terminal=False,
            is_deleted=False
        )
        
        # Group by current state
        for app in violated_applications:
            state = app.current_state
            if state not in results[WORKFLOW_TYPES['APPLICATION']]:
                results[WORKFLOW_TYPES['APPLICATION']][state] = 0
            results[WORKFLOW_TYPES['APPLICATION']][state] += 1
        
        # Check document SLA violations
        violated_documents = Document.objects.filter(
            sla_due_at__lt=now,
            is_terminal=False,
            is_deleted=False
        )
        
        # Group by current state
        for doc in violated_documents:
            state = doc.current_state
            if state not in results[WORKFLOW_TYPES['DOCUMENT']]:
                results[WORKFLOW_TYPES['DOCUMENT']][state] = 0
            results[WORKFLOW_TYPES['DOCUMENT']][state] += 1
        
        # Check funding SLA violations
        violated_funding = FundingRequest.objects.filter(
            sla_due_at__lt=now,
            is_terminal=False,
            is_deleted=False
        )
        
        # Group by current state
        for fund in violated_funding:
            state = fund.current_state
            if state not in results[WORKFLOW_TYPES['FUNDING']]:
                results[WORKFLOW_TYPES['FUNDING']][state] = 0
            results[WORKFLOW_TYPES['FUNDING']][state] += 1
        
        # Log SLA violations
        total_violations = sum(len(violations) for violations in results.values())
        if total_violations > 0:
            logger.warning(f"Found {total_violations} SLA violations: {results}")
        
        return results
    except Exception as e:
        logger.error(f"Error checking SLA violations: {str(e)}", exc_info=True)
        return results