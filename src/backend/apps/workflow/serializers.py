"""
Defines serializers for the workflow module that handle the serialization and deserialization
of workflow-related data, including transition history, workflow tasks, state transitions,
and specialized transition types for applications, documents, and funding processes.
"""

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from rest_framework.relations import GenericRelatedField
from django.utils import timezone

from ../../../core/serializers import BaseModelSerializer, ReadOnlyModelSerializer
from .models import (
    WorkflowTransitionHistory, 
    WorkflowTask,
    AutomaticTransitionSchedule,
)
from .constants import (
    WORKFLOW_TYPES,
    APPLICATION_STATE_TRANSITIONS,
    DOCUMENT_STATE_TRANSITIONS,
    FUNDING_STATE_TRANSITIONS,
    WORKFLOW_TASK_STATUS,
    WORKFLOW_TASK_TYPES,
)
from ../../../utils/constants import (
    APPLICATION_STATUS,
    DOCUMENT_STATUS,
    FUNDING_STATUS,
)
from .transitions import transition_entity, TransitionHandlerFactory

User = get_user_model()


class WorkflowTransitionHistorySerializer(ReadOnlyModelSerializer):
    """
    Serializer for workflow transition history records.
    """
    class Meta:
        model = WorkflowTransitionHistory
        fields = ['id', 'workflow_type', 'from_state', 'to_state', 'transition_date', 
                  'transitioned_by', 'reason', 'transition_event', 'content_type', 'object_id']
        read_only_fields = ['id', 'transition_date']
    
    def to_representation(self, instance):
        """
        Customizes the serialized representation of transition history.
        
        Args:
            instance: The history record instance
            
        Returns:
            dict: Serialized representation with human-readable state names
        """
        representation = super().to_representation(instance)
        
        # Add human-readable state names
        if instance.workflow_type == WORKFLOW_TYPES['APPLICATION']:
            # Find display names for states in APPLICATION_STATUS
            for status_key, status_value in APPLICATION_STATUS.items():
                if status_value == instance.from_state:
                    representation['from_state_display'] = status_key
                if status_value == instance.to_state:
                    representation['to_state_display'] = status_key
        
        elif instance.workflow_type == WORKFLOW_TYPES['DOCUMENT']:
            # Find display names for states in DOCUMENT_STATUS
            for status_key, status_value in DOCUMENT_STATUS.items():
                if status_value == instance.from_state:
                    representation['from_state_display'] = status_key
                if status_value == instance.to_state:
                    representation['to_state_display'] = status_key
        
        elif instance.workflow_type == WORKFLOW_TYPES['FUNDING']:
            # Find display names for states in FUNDING_STATUS
            for status_key, status_value in FUNDING_STATUS.items():
                if status_value == instance.from_state:
                    representation['from_state_display'] = status_key
                if status_value == instance.to_state:
                    representation['to_state_display'] = status_key
        
        # Add transitioned_by user details (name, email)
        if instance.transitioned_by:
            representation['transitioned_by_name'] = f"{instance.transitioned_by.first_name} {instance.transitioned_by.last_name}"
            representation['transitioned_by_email'] = instance.transitioned_by.email
        
        return representation


class WorkflowTaskSerializer(BaseModelSerializer):
    """
    Serializer for workflow tasks.
    """
    class Meta:
        model = WorkflowTask
        fields = ['id', 'task_type', 'description', 'status', 'created_at', 'due_date',
                  'completed_at', 'assigned_to', 'completed_by', 'notes', 'content_type', 'object_id']
        read_only_fields = ['id', 'created_at', 'completed_at', 'completed_by']
    
    def to_representation(self, instance):
        """
        Customizes the serialized representation of workflow tasks.
        
        Args:
            instance: The workflow task instance
            
        Returns:
            dict: Serialized representation with additional task information
        """
        representation = super().to_representation(instance)
        
        # Add human-readable task type and status labels
        for task_type_key, task_type_value in WORKFLOW_TASK_TYPES.items():
            if task_type_value == instance.task_type:
                representation['task_type_display'] = task_type_key
                break
        
        for status_key, status_value in WORKFLOW_TASK_STATUS.items():
            if status_value == instance.status:
                representation['status_display'] = status_key
                break
        
        # Add assigned_to user details
        if instance.assigned_to:
            representation['assigned_to_name'] = f"{instance.assigned_to.first_name} {instance.assigned_to.last_name}"
            representation['assigned_to_email'] = instance.assigned_to.email
        
        # Add completed_by user details if task is completed
        if instance.completed_by:
            representation['completed_by_name'] = f"{instance.completed_by.first_name} {instance.completed_by.last_name}"
            representation['completed_by_email'] = instance.completed_by.email
        
        # Add is_overdue flag
        representation['is_overdue'] = instance.is_overdue()
        
        return representation
    
    def complete(self, instance, user, notes=None):
        """
        Completes a workflow task.
        
        Args:
            instance: The task instance to complete
            user: The user completing the task
            notes: Optional notes about the completion
            
        Returns:
            object: The updated task instance
        """
        if instance.status == WORKFLOW_TASK_STATUS['COMPLETED']:
            raise ValidationError("Task is already completed")
        
        instance.complete(user, notes)
        return instance
    
    def validate(self, data):
        """
        Validates task data.
        
        Args:
            data: The task data to validate
            
        Returns:
            dict: Validated data
        """
        # Validate task_type is a valid value from WORKFLOW_TASK_TYPES
        if 'task_type' in data and data['task_type'] not in WORKFLOW_TASK_TYPES.values():
            raise ValidationError({'task_type': f"Invalid task type. Must be one of: {', '.join(WORKFLOW_TASK_TYPES.values())}"})
        
        # Validate status is a valid value from WORKFLOW_TASK_STATUS
        if 'status' in data and data['status'] not in WORKFLOW_TASK_STATUS.values():
            raise ValidationError({'status': f"Invalid status. Must be one of: {', '.join(WORKFLOW_TASK_STATUS.values())}"})
        
        # Validate due_date is in the future if provided
        if 'due_date' in data and data['due_date'] and data['due_date'] < timezone.now():
            raise ValidationError({'due_date': "Due date must be in the future"})
        
        return data


class AutomaticTransitionScheduleSerializer(BaseModelSerializer):
    """
    Serializer for automatic transition schedules.
    """
    class Meta:
        model = AutomaticTransitionSchedule
        fields = ['id', 'workflow_type', 'from_state', 'to_state', 'scheduled_date',
                  'is_executed', 'executed_at', 'reason', 'content_type', 'object_id']
        read_only_fields = ['id', 'is_executed', 'executed_at']
    
    def to_representation(self, instance):
        """
        Customizes the serialized representation of transition schedules.
        
        Args:
            instance: The schedule instance
            
        Returns:
            dict: Serialized representation with human-readable state names
        """
        representation = super().to_representation(instance)
        
        # Add human-readable state names based on workflow type
        if instance.workflow_type == WORKFLOW_TYPES['APPLICATION']:
            # Find display names for states in APPLICATION_STATUS
            for status_key, status_value in APPLICATION_STATUS.items():
                if status_value == instance.from_state:
                    representation['from_state_display'] = status_key
                if status_value == instance.to_state:
                    representation['to_state_display'] = status_key
        
        elif instance.workflow_type == WORKFLOW_TYPES['DOCUMENT']:
            # Find display names for states in DOCUMENT_STATUS
            for status_key, status_value in DOCUMENT_STATUS.items():
                if status_value == instance.from_state:
                    representation['from_state_display'] = status_key
                if status_value == instance.to_state:
                    representation['to_state_display'] = status_key
        
        elif instance.workflow_type == WORKFLOW_TYPES['FUNDING']:
            # Find display names for states in FUNDING_STATUS
            for status_key, status_value in FUNDING_STATUS.items():
                if status_value == instance.from_state:
                    representation['from_state_display'] = status_key
                if status_value == instance.to_state:
                    representation['to_state_display'] = status_key
        
        # Add entity_type and entity_id for easier reference
        if instance.content_type and instance.object_id:
            representation['entity_type'] = instance.content_type.model
            representation['entity_id'] = str(instance.object_id)
        
        return representation
    
    def validate(self, data):
        """
        Validates schedule data.
        
        Args:
            data: The schedule data to validate
            
        Returns:
            dict: Validated data
        """
        # Validate workflow_type is a valid value from WORKFLOW_TYPES
        if 'workflow_type' in data and data['workflow_type'] not in WORKFLOW_TYPES.values():
            raise ValidationError({
                'workflow_type': f"Invalid workflow type. Must be one of: {', '.join(WORKFLOW_TYPES.values())}"
            })
        
        # Validate from_state and to_state are valid for the workflow_type
        if all(key in data for key in ['workflow_type', 'from_state', 'to_state']):
            workflow_type = data['workflow_type']
            from_state = data['from_state']
            to_state = data['to_state']
            
            # Get the appropriate state transition map
            if workflow_type == WORKFLOW_TYPES['APPLICATION']:
                transitions = APPLICATION_STATE_TRANSITIONS
            elif workflow_type == WORKFLOW_TYPES['DOCUMENT']:
                transitions = DOCUMENT_STATE_TRANSITIONS
            elif workflow_type == WORKFLOW_TYPES['FUNDING']:
                transitions = FUNDING_STATE_TRANSITIONS
            else:
                transitions = {}
            
            # Validate the transition is allowed
            if from_state not in transitions or to_state not in transitions.get(from_state, []):
                raise ValidationError({
                    'to_state': f"Invalid state transition from '{from_state}' to '{to_state}' for workflow type '{workflow_type}'"
                })
        
        # Validate scheduled_date is in the future
        if 'scheduled_date' in data and data['scheduled_date'] and data['scheduled_date'] < timezone.now():
            raise ValidationError({'scheduled_date': "Scheduled date must be in the future"})
        
        return data


class WorkflowConfigurationSerializer(BaseModelSerializer):
    """
    Serializer for workflow configuration settings.
    """
    class Meta:
        model = WorkflowConfiguration
        fields = ['id', 'workflow_type', 'config_key', 'config_value', 'description', 
                  'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """
        Validates configuration data.
        
        Args:
            data: The configuration data to validate
            
        Returns:
            dict: Validated data
        """
        # Validate workflow_type is a valid value from WORKFLOW_TYPES
        if 'workflow_type' in data and data['workflow_type'] not in WORKFLOW_TYPES.values():
            raise ValidationError({
                'workflow_type': f"Invalid workflow type. Must be one of: {', '.join(WORKFLOW_TYPES.values())}"
            })
        
        # Validate config_key is not empty
        if 'config_key' in data and not data['config_key'].strip():
            raise ValidationError({'config_key': "Configuration key cannot be empty"})
        
        # Validate config_value is not empty
        if 'config_value' in data and not data['config_value'].strip():
            raise ValidationError({'config_value': "Configuration value cannot be empty"})
        
        return data


class WorkflowStateSerializer(serializers.Serializer):
    """
    Serializer for workflow state information.
    """
    
    def to_representation(self, instance):
        """
        Creates a representation of an entity's workflow state.
        
        Args:
            instance: The entity whose workflow state to represent
            
        Returns:
            dict: Serialized workflow state information
        """
        # Get the workflow type from instance.get_workflow_type()
        workflow_type = instance.get_workflow_type()
        
        # Get the current state from instance.current_state
        current_state = instance.current_state
        
        # Get the state_changed_at timestamp
        state_changed_at = instance.state_changed_at
        
        # Get the state_changed_by user details
        state_changed_by = None
        if hasattr(instance, 'state_changed_by') and instance.state_changed_by:
            state_changed_by = {
                'id': str(instance.state_changed_by.id),
                'name': f"{instance.state_changed_by.first_name} {instance.state_changed_by.last_name}",
                'email': instance.state_changed_by.email
            }
        
        # Get the appropriate state transition map
        if workflow_type == WORKFLOW_TYPES['APPLICATION']:
            transitions = APPLICATION_STATE_TRANSITIONS
            status_map = APPLICATION_STATUS
        elif workflow_type == WORKFLOW_TYPES['DOCUMENT']:
            transitions = DOCUMENT_STATE_TRANSITIONS
            status_map = DOCUMENT_STATUS
        elif workflow_type == WORKFLOW_TYPES['FUNDING']:
            transitions = FUNDING_STATE_TRANSITIONS
            status_map = FUNDING_STATUS
        else:
            transitions = {}
            status_map = {}
        
        # Determine if the current state is terminal
        is_terminal = instance.is_terminal
        
        # Get human-readable current state
        current_state_display = next(
            (key for key, value in status_map.items() if value == current_state),
            current_state
        )
        
        # Get the allowed next states based on the workflow type and current state
        allowed_next_states = transitions.get(current_state, [])
        allowed_next_states_display = [
            next((key for key, value in status_map.items() if value == state), state)
            for state in allowed_next_states
        ]
        
        # Get pending tasks for the entity
        pending_tasks = []
        for task in instance.get_pending_tasks():
            task_serializer = WorkflowTaskSerializer(task)
            pending_tasks.append(task_serializer.data)
        
        # Get SLA information (due_date, is_breached)
        sla_due_date = instance.sla_due_at if hasattr(instance, 'sla_due_at') else None
        is_sla_breached = instance.is_sla_breached() if hasattr(instance, 'is_sla_breached') else False
        
        # Return a dictionary with all the workflow state information
        return {
            'workflow_type': workflow_type,
            'current_state': current_state,
            'current_state_display': current_state_display,
            'is_terminal': is_terminal,
            'allowed_next_states': allowed_next_states,
            'allowed_next_states_display': allowed_next_states_display,
            'state_changed_at': state_changed_at,
            'state_changed_by': state_changed_by,
            'pending_tasks': pending_tasks,
            'sla_due_date': sla_due_date,
            'is_sla_breached': is_sla_breached
        }


class WorkflowTransitionSerializer(serializers.Serializer):
    """
    Base serializer for workflow transitions.
    """
    
    def validate(self, data):
        """
        Validates transition data.
        
        Args:
            data: The transition data to validate
            
        Returns:
            dict: Validated data
        """
        # Get the entity from context
        entity = self.context.get('entity')
        if not entity:
            raise ValidationError({"entity": "No entity provided in context"})
        
        # Get the to_state from data
        to_state = data.get('to_state')
        if not to_state:
            raise ValidationError({"to_state": "Target state is required"})
        
        # Get the workflow type from entity.get_workflow_type()
        workflow_type = entity.get_workflow_type()
        
        # Get the transition handler for the entity
        try:
            handler = TransitionHandlerFactory.get_handler_for_entity(entity)
        except ValueError as e:
            raise ValidationError({"workflow_type": str(e)})
        
        # Validate the transition is allowed using handler.validate_transition()
        user = self.context.get('user')
        if not handler.validate_transition(entity, to_state, user):
            raise ValidationError({
                "to_state": f"Invalid transition from '{entity.current_state}' to '{to_state}'"
            })
        
        return data
    
    def save(self):
        """
        Executes the workflow transition.
        
        Returns:
            object: The transitioned entity
        """
        # Get the entity from context
        entity = self.context.get('entity')
        
        # Get the validated to_state
        to_state = self.validated_data.get('to_state')
        
        # Get the reason from validated data
        reason = self.validated_data.get('reason', '')
        
        # Get the current user from context
        user = self.context.get('user')
        
        # Call transition_entity() to perform the transition
        success = transition_entity(entity, to_state, user, reason)
        if not success:
            raise ValidationError({"transition": "Failed to execute transition"})
        
        return entity


class ApplicationTransitionSerializer(WorkflowTransitionSerializer):
    """
    Serializer for application workflow transitions.
    """
    to_state = serializers.CharField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """
        Validates application transition data.
        
        Args:
            data: The transition data to validate
            
        Returns:
            dict: Validated data
        """
        # Call parent validate method for basic validation
        data = super().validate(data)
        
        # Get the entity from context
        entity = self.context.get('entity')
        
        # Get the to_state from data
        to_state = data.get('to_state')
        
        # Perform application-specific validation based on to_state
        if to_state == APPLICATION_STATUS['APPROVED']:
            # For approval, reason is required
            if not data.get('reason'):
                raise ValidationError({"reason": "Reason is required for approval"})
        
        elif to_state == APPLICATION_STATUS['DENIED']:
            # For denial, reason is required
            if not data.get('reason'):
                raise ValidationError({"reason": "Reason is required for denial"})
        
        elif to_state == APPLICATION_STATUS['REVISION_REQUESTED']:
            # For revision, reason is required
            if not data.get('reason'):
                raise ValidationError({"reason": "Reason is required for revision request"})
        
        return data


class UnderwritingDecisionSerializer(ApplicationTransitionSerializer):
    """
    Serializer for underwriting decisions.
    """
    to_state = serializers.CharField(required=True)
    reason = serializers.CharField(required=True)
    approved_amount = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    interest_rate = serializers.DecimalField(required=False, max_digits=5, decimal_places=2)
    term_months = serializers.IntegerField(required=False, min_value=1, max_value=120)
    stipulations = serializers.ListField(required=False, child=serializers.CharField())
    
    def validate(self, data):
        """
        Validates underwriting decision data.
        
        Args:
            data: The decision data to validate
            
        Returns:
            dict: Validated data
        """
        # Call parent validate method for basic validation
        data = super().validate(data)
        
        # Get the to_state from data
        to_state = data.get('to_state')
        
        # If to_state is APPROVED, validate approved_amount, interest_rate, and term_months are provided
        if to_state == APPLICATION_STATUS['APPROVED']:
            if not data.get('approved_amount'):
                raise ValidationError({"approved_amount": "Approved amount is required for approval"})
            
            if not data.get('interest_rate'):
                raise ValidationError({"interest_rate": "Interest rate is required for approval"})
            
            if not data.get('term_months'):
                raise ValidationError({"term_months": "Term is required for approval"})
        
        # If to_state is DENIED, validate reason is provided
        elif to_state == APPLICATION_STATUS['DENIED']:
            # Reason validation is already handled by parent class
            pass
        
        return data
    
    def save(self):
        """
        Executes the underwriting decision transition.
        
        Args:
            None
            
        Returns:
            object: The transitioned application
        """
        # Get the application from context
        application = self.context.get('entity')
        
        # Get the validated data
        to_state = self.validated_data.get('to_state')
        
        # If to_state is APPROVED, create or update UnderwritingDecision record
        if to_state == APPLICATION_STATUS['APPROVED']:
            from ..loan.models import UnderwritingDecision
            
            decision, created = UnderwritingDecision.objects.get_or_create(
                application=application,
                defaults={
                    'decision': 'approve',
                    'decision_date': timezone.now(),
                    'underwriter': self.context.get('user'),
                    'approved_amount': self.validated_data.get('approved_amount'),
                    'interest_rate': self.validated_data.get('interest_rate'),
                    'term_months': self.validated_data.get('term_months'),
                    'comments': self.validated_data.get('reason')
                }
            )
            
            if not created:
                # Update existing decision
                decision.decision = 'approve'
                decision.decision_date = timezone.now()
                decision.underwriter = self.context.get('user')
                decision.approved_amount = self.validated_data.get('approved_amount')
                decision.interest_rate = self.validated_data.get('interest_rate')
                decision.term_months = self.validated_data.get('term_months')
                decision.comments = self.validated_data.get('reason')
                decision.save()
            
            # If stipulations provided, create Stipulation records
            if 'stipulations' in self.validated_data and self.validated_data['stipulations']:
                from ..loan.models import Stipulation
                
                for stipulation_text in self.validated_data['stipulations']:
                    Stipulation.objects.create(
                        application=application,
                        stipulation_type='other',
                        description=stipulation_text,
                        status='pending',
                        created_by=self.context.get('user')
                    )
        
        # If to_state is DENIED, create or update UnderwritingDecision record
        elif to_state == APPLICATION_STATUS['DENIED']:
            from ..loan.models import UnderwritingDecision
            
            decision, created = UnderwritingDecision.objects.get_or_create(
                application=application,
                defaults={
                    'decision': 'deny',
                    'decision_date': timezone.now(),
                    'underwriter': self.context.get('user'),
                    'comments': self.validated_data.get('reason')
                }
            )
            
            if not created:
                # Update existing decision
                decision.decision = 'deny'
                decision.decision_date = timezone.now()
                decision.underwriter = self.context.get('user')
                decision.comments = self.validated_data.get('reason')
                decision.save()
        
        # Call parent save method to perform the transition
        return super().save()


class CommitmentResponseSerializer(ApplicationTransitionSerializer):
    """
    Serializer for school responses to commitment letters.
    """
    to_state = serializers.CharField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)
    counter_offer_amount = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    
    def validate(self, data):
        """
        Validates commitment response data.
        
        Args:
            data: The response data to validate
            
        Returns:
            dict: Validated data
        """
        # Call parent validate method for basic validation
        data = super().validate(data)
        
        # Get the to_state from data
        to_state = data.get('to_state')
        
        # If to_state is COUNTER_OFFER_MADE, validate counter_offer_amount is provided
        if to_state == APPLICATION_STATUS['COUNTER_OFFER_MADE']:
            if not data.get('counter_offer_amount'):
                raise ValidationError({"counter_offer_amount": "Counter offer amount is required"})
        
        # If to_state is COMMITMENT_DECLINED, validate reason is provided
        elif to_state == APPLICATION_STATUS['COMMITMENT_DECLINED']:
            if not data.get('reason'):
                raise ValidationError({"reason": "Reason is required when declining commitment"})
        
        return data
    
    def save(self):
        """
        Executes the commitment response transition.
        
        Returns:
            object: The transitioned application
        """
        # Get the application from context
        application = self.context.get('entity')
        
        # Get the validated data
        to_state = self.validated_data.get('to_state')
        
        # If to_state is COUNTER_OFFER_MADE, store counter offer details
        if to_state == APPLICATION_STATUS['COUNTER_OFFER_MADE']:
            from ..loan.models import CommitmentResponse
            
            response = CommitmentResponse.objects.create(
                application=application,
                response_type='counter_offer',
                counter_offer_amount=self.validated_data.get('counter_offer_amount'),
                reason=self.validated_data.get('reason'),
                responded_by=self.context.get('user'),
                responded_at=timezone.now()
            )
        
        # If to_state is COMMITMENT_DECLINED, store decline reason
        elif to_state == APPLICATION_STATUS['COMMITMENT_DECLINED']:
            from ..loan.models import CommitmentResponse
            
            response = CommitmentResponse.objects.create(
                application=application,
                response_type='decline',
                reason=self.validated_data.get('reason'),
                responded_by=self.context.get('user'),
                responded_at=timezone.now()
            )
        
        # Call parent save method to perform the transition
        return super().save()


class QCDecisionSerializer(ApplicationTransitionSerializer):
    """
    Serializer for quality control decisions.
    """
    to_state = serializers.CharField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)
    checklist_items = serializers.ListField(required=False, child=serializers.CharField())
    
    def validate(self, data):
        """
        Validates QC decision data.
        
        Args:
            data: The decision data to validate
            
        Returns:
            dict: Validated data
        """
        # Call parent validate method for basic validation
        data = super().validate(data)
        
        # Get the to_state from data
        to_state = data.get('to_state')
        
        # If to_state is QC_REJECTED, validate reason is provided
        if to_state == APPLICATION_STATUS['QC_REJECTED']:
            if not data.get('reason'):
                raise ValidationError({"reason": "Reason is required when rejecting QC"})
        
        return data
    
    def save(self):
        """
        Executes the QC decision transition.
        
        Returns:
            object: The transitioned application
        """
        # Get the application from context
        application = self.context.get('entity')
        
        # Get the validated data
        to_state = self.validated_data.get('to_state')
        
        # If to_state is QC_APPROVED, record checklist completion
        if to_state == APPLICATION_STATUS['QC_APPROVED']:
            if 'checklist_items' in self.validated_data and self.validated_data['checklist_items']:
                from ..loan.models import QCReview
                
                review = QCReview.objects.create(
                    application=application,
                    reviewer=self.context.get('user'),
                    review_date=timezone.now(),
                    decision='approve',
                    checklist_items=self.validated_data['checklist_items'],
                    comments=self.validated_data.get('reason', '')
                )
        
        # Call parent save method to perform the transition
        return super().save()


class DocumentTransitionSerializer(WorkflowTransitionSerializer):
    """
    Serializer for document workflow transitions.
    """
    to_state = serializers.CharField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """
        Validates document transition data.
        
        Args:
            data: The transition data to validate
            
        Returns:
            dict: Validated data
        """
        # Call parent validate method for basic validation
        data = super().validate(data)
        
        # Get the entity from context
        entity = self.context.get('entity')
        
        # Get the to_state from data
        to_state = data.get('to_state')
        
        # Perform document-specific validation based on to_state
        if to_state == DOCUMENT_STATUS['REJECTED']:
            # For rejection, reason is required
            if not data.get('reason'):
                raise ValidationError({"reason": "Reason is required for rejection"})
        
        return data


class DocumentSignatureEventSerializer(DocumentTransitionSerializer):
    """
    Serializer for document signature events.
    """
    to_state = serializers.CharField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)
    signer_id = serializers.UUIDField(required=True)
    signature_date = serializers.DateTimeField(required=True)
    
    def validate(self, data):
        """
        Validates signature event data.
        
        Args:
            data: The event data to validate
            
        Returns:
            dict: Validated data
        """
        # Call parent validate method for basic validation
        data = super().validate(data)
        
        # Get the document from context
        document = self.context.get('entity')
        
        # Validate signer_id corresponds to a valid signer for the document
        if not document.signature_requests.filter(signer_id=data['signer_id']).exists():
            raise ValidationError({"signer_id": "Invalid signer for this document"})
        
        return data
    
    def save(self):
        """
        Executes the signature event transition.
        
        Returns:
            object: The transitioned document
        """
        # Get the document from context
        document = self.context.get('entity')
        
        # Get the validated data
        signer_id = self.validated_data['signer_id']
        signature_date = self.validated_data['signature_date']
        
        # Record the signature event with signer and date
        signature_request = document.signature_requests.get(signer_id=signer_id)
        signature_request.status = 'signed'
        signature_request.completed_at = signature_date
        signature_request.save()
        
        # Call parent save method to perform the transition
        return super().save()


class FundingTransitionSerializer(WorkflowTransitionSerializer):
    """
    Serializer for funding workflow transitions.
    """
    to_state = serializers.CharField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """
        Validates funding transition data.
        
        Args:
            data: The transition data to validate
            
        Returns:
            dict: Validated data
        """
        # Call parent validate method for basic validation
        data = super().validate(data)
        
        # Get the entity from context
        entity = self.context.get('entity')
        
        # Get the to_state from data
        to_state = data.get('to_state')
        
        # Perform funding-specific validation based on to_state
        if to_state == FUNDING_STATUS['PENDING_STIPULATIONS']:
            # For pending stipulations, reason is required
            if not data.get('reason'):
                raise ValidationError({"reason": "Reason is required when marking stipulations as pending"})
        
        return data


class EnrollmentVerificationSerializer(FundingTransitionSerializer):
    """
    Serializer for enrollment verification.
    """
    to_state = serializers.CharField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)
    start_date = serializers.DateField(required=True)
    document_id = serializers.UUIDField(required=False)
    
    def validate(self, data):
        """
        Validates enrollment verification data.
        
        Args:
            data: The verification data to validate
            
        Returns:
            dict: Validated data
        """
        # Call parent validate method for basic validation
        data = super().validate(data)
        
        # Validate start_date is not in the past
        if data.get('start_date') and data['start_date'] < timezone.now().date():
            raise ValidationError({"start_date": "Start date cannot be in the past"})
        
        # If document_id provided, validate it exists
        if data.get('document_id'):
            from ..documents.models import Document
            
            try:
                document = Document.objects.get(id=data['document_id'])
            except Document.DoesNotExist:
                raise ValidationError({"document_id": "Document does not exist"})
        
        return data
    
    def save(self):
        """
        Executes the enrollment verification transition.
        
        Returns:
            object: The transitioned funding request
        """
        # Get the funding request from context
        funding_request = self.context.get('entity')
        
        # Get the validated data
        start_date = self.validated_data['start_date']
        document_id = self.validated_data.get('document_id')
        
        # Create EnrollmentVerification record with start_date and document_id
        from ..funding.models import EnrollmentVerification
        
        verification = EnrollmentVerification.objects.create(
            funding_request=funding_request,
            verification_type='school_confirmation',
            verified_by=self.context.get('user'),
            verified_at=timezone.now(),
            start_date=start_date,
            document_id=document_id,
            comments=self.validated_data.get('reason', '')
        )
        
        # Call parent save method to perform the transition
        return super().save()


class StipulationVerificationSerializer(FundingTransitionSerializer):
    """
    Serializer for stipulation verification.
    """
    to_state = serializers.CharField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)
    stipulation_ids = serializers.ListField(child=serializers.UUIDField(), required=True)
    comments = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """
        Validates stipulation verification data.
        
        Args:
            data: The verification data to validate
            
        Returns:
            dict: Validated data
        """
        # Call parent validate method for basic validation
        data = super().validate(data)
        
        # Validate all stipulation_ids exist and belong to the application
        if data.get('stipulation_ids'):
            from ..loan.models import Stipulation
            
            # Get funding request from context
            funding_request = self.context.get('entity')
            
            # Get application_id from funding_request
            application_id = funding_request.application_id
            
            # Check that all stipulations exist and belong to this application
            for stipulation_id in data['stipulation_ids']:
                try:
                    stipulation = Stipulation.objects.get(id=stipulation_id, application_id=application_id)
                except Stipulation.DoesNotExist:
                    raise ValidationError({
                        "stipulation_ids": f"Stipulation {stipulation_id} does not exist or does not belong to this application"
                    })
        
        return data
    
    def save(self):
        """
        Executes the stipulation verification transition.
        
        Returns:
            object: The transitioned funding request
        """
        # Get the funding request from context
        funding_request = self.context.get('entity')
        
        # Get the validated data
        stipulation_ids = self.validated_data['stipulation_ids']
        
        # Create StipulationVerification records for each stipulation
        from ..funding.models import StipulationVerification
        from ..loan.models import Stipulation
        
        for stipulation_id in stipulation_ids:
            # Get the stipulation
            stipulation = Stipulation.objects.get(id=stipulation_id)
            
            # Create verification record
            verification = StipulationVerification.objects.create(
                funding_request=funding_request,
                stipulation=stipulation,
                verified_by=self.context.get('user'),
                verified_at=timezone.now(),
                status='satisfied',
                comments=self.validated_data.get('comments', '')
            )
            
            # Update stipulation status
            stipulation.status = 'satisfied'
            stipulation.satisfied_at = timezone.now()
            stipulation.satisfied_by = self.context.get('user')
            stipulation.save()
        
        # Call parent save method to perform the transition
        return super().save()


class DisbursementSerializer(FundingTransitionSerializer):
    """
    Serializer for disbursement processing.
    """
    to_state = serializers.CharField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    disbursement_date = serializers.DateField(required=True)
    disbursement_method = serializers.CharField(required=True)
    reference_number = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """
        Validates disbursement data.
        
        Args:
            data: The disbursement data to validate
            
        Returns:
            dict: Validated data
        """
        # Call parent validate method for basic validation
        data = super().validate(data)
        
        # Get the funding request from context
        funding_request = self.context.get('entity')
        
        # Validate amount matches the approved amount
        application = funding_request.application
        if application.underwriting_decision:
            approved_amount = application.underwriting_decision.approved_amount
            if data.get('amount') != approved_amount:
                raise ValidationError({
                    "amount": f"Disbursement amount must match approved amount of {approved_amount}"
                })
        
        # Validate disbursement_date is not in the past
        if data.get('disbursement_date') and data['disbursement_date'] < timezone.now().date():
            raise ValidationError({"disbursement_date": "Disbursement date cannot be in the past"})
        
        # Validate disbursement_method is valid
        valid_methods = ['ach', 'wire', 'check']
        if data.get('disbursement_method') and data['disbursement_method'] not in valid_methods:
            raise ValidationError({
                "disbursement_method": f"Invalid disbursement method. Must be one of: {', '.join(valid_methods)}"
            })
        
        return data
    
    def save(self):
        """
        Executes the disbursement transition.
        
        Returns:
            object: The transitioned funding request
        """
        # Get the funding request from context
        funding_request = self.context.get('entity')
        
        # Get the validated data
        amount = self.validated_data['amount']
        disbursement_date = self.validated_data['disbursement_date']
        disbursement_method = self.validated_data['disbursement_method']
        reference_number = self.validated_data.get('reference_number', '')
        
        # Create Disbursement record with disbursement details
        from ..funding.models import Disbursement
        
        disbursement = Disbursement.objects.create(
            funding_request=funding_request,
            amount=amount,
            disbursement_date=disbursement_date,
            disbursement_method=disbursement_method,
            reference_number=reference_number,
            status='processed',
            processed_by=self.context.get('user')
        )
        
        # Call parent save method to perform the transition
        return super().save()