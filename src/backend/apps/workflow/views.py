"""
Implements API views and viewsets for the workflow module that handle state transitions,
workflow history, and workflow tasks. This file provides the interface for managing the
loan application lifecycle, document processing, and funding workflows through RESTful API endpoints.
"""
import logging  # standard library
from rest_framework import viewsets  # version 3.14+
from rest_framework import generics  # version 3.14+
from rest_framework import views  # version 3.14+
from rest_framework import status  # version 3.14+
from rest_framework.response import Response  # version 3.14+
from rest_framework.decorators import api_view, permission_classes  # version 3.14+
from django.contrib.contenttypes.models import ContentType  # Django 4.2+
from django.shortcuts import get_object_or_404  # Django 4.2+
from django.utils import timezone  # Django 4.2+
from rest_framework.exceptions import ValidationError, PermissionDenied  # version 3.14+

from .models import (  # src/backend/apps/workflow/models.py
    WorkflowTransitionHistory,
    WorkflowTask,
    AutomaticTransitionSchedule,
)
from .serializers import (  # src/backend/apps/workflow/serializers.py
    WorkflowTransitionHistorySerializer,
    WorkflowTaskSerializer,
    AutomaticTransitionScheduleSerializer,
    WorkflowConfigurationSerializer,
    WorkflowStateSerializer,
    WorkflowTransitionSerializer,
    ApplicationTransitionSerializer,
    UnderwritingDecisionSerializer,
    CommitmentResponseSerializer,
    QCDecisionSerializer,
    DocumentTransitionSerializer,
    DocumentSignatureEventSerializer,
    FundingTransitionSerializer,
    EnrollmentVerificationSerializer,
    StipulationVerificationSerializer,
    DisbursementSerializer,
)
from .constants import (  # src/backend/apps/workflow/constants.py
    WORKFLOW_TYPES,
    APPLICATION_STATE_TRANSITIONS,
    DOCUMENT_STATE_TRANSITIONS,
    FUNDING_STATE_TRANSITIONS,
    WORKFLOW_SLA_DEFINITIONS,
)
from .transitions import transition_entity  # src/backend/apps/workflow/transitions.py
from .transitions import process_automatic_transitions  # src/backend/apps/workflow/transitions.py
from .transitions import handle_document_expiration  # src/backend/apps/workflow/transitions.py
from .transitions import check_sla_violations  # src/backend/apps/workflow/transitions.py
from ...core.permissions import IsAuthenticated, IsSystemAdmin, IsInternalUser, IsOwnerOrInternalUser  # src/backend/core/permissions.py

# Get an instance of a logger
logger = logging.getLogger(__name__)


def get_entity_from_content_type(content_type_id, object_id):
    """
    Retrieves an entity object based on content type and object ID

    Args:
        content_type_id (str): The ID of the content type
        object_id (str): The ID of the object

    Returns:
        object: The retrieved entity object
    """
    try:
        # Get the ContentType object using the content_type_id
        content_type = ContentType.objects.get(pk=content_type_id)
    except ContentType.DoesNotExist:
        # If ContentType not found, raise 404
        raise ValidationError({"content_type_id": "Invalid content type ID"})

    # Get the model class from the ContentType
    model_class = content_type.model_class()

    try:
        # Retrieve the object using the model class and object_id
        obj = model_class.objects.get(pk=object_id)
    except model_class.DoesNotExist:
        # If object not found, raise 404
        raise ValidationError({"object_id": "Object not found"})

    # Return the retrieved object
    return obj


@api_view(['POST'])
@permission_classes([IsSystemAdmin])
def process_automatic_transitions_view(request):
    """
    API view function to process scheduled automatic transitions

    Args:
        request (object): The request object

    Returns:
        Response: API response with transition results
    """
    # Call process_automatic_transitions() to process due transitions
    transition_count = process_automatic_transitions()

    # Log the number of transitions processed
    logger.info(f"Processed {transition_count} automatic transitions")

    # Return Response with success status and count of processed transitions
    return Response({"status": "success", "transitions_processed": transition_count}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsSystemAdmin])
def process_document_expiration_view(request):
    """
    API view function to process document expiration

    Args:
        request (object): The request object

    Returns:
        Response: API response with expiration results
    """
    # Call handle_document_expiration() to process expired documents
    expired_count = handle_document_expiration()

    # Log the number of documents expired
    logger.info(f"Expired {expired_count} documents")

    # Return Response with success status and count of expired documents
    return Response({"status": "success", "documents_expired": expired_count}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsSystemAdmin])
def process_sla_monitoring_view(request):
    """
    API view function to check for SLA violations

    Args:
        request (object): The request object

    Returns:
        Response: API response with SLA violation results
    """
    # Call check_sla_violations() to identify SLA violations
    violations = check_sla_violations()

    # Log the violations by workflow type and state
    logger.warning(f"SLA violations: {violations}")

    # Return Response with success status and violation details
    return Response({"status": "success", "sla_violations": violations}, status=status.HTTP_200_OK)


class WorkflowTransitionHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for workflow transition history records
    """
    queryset = WorkflowTransitionHistory.objects.all().order_by('-transition_date')
    serializer_class = WorkflowTransitionHistorySerializer
    permission_classes = [IsInternalUser]
    filterset_fields = ['workflow_type', 'from_state', 'to_state', 'transitioned_by', 'transition_event', 'content_type', 'object_id']

    def get_queryset(self):
        """
        Returns filtered queryset based on user permissions

        Returns:
            QuerySet: Filtered queryset of transition history records
        """
        # Get the base queryset from parent
        queryset = super().get_queryset()

        # If user is a system admin, return all records
        if self.request.user.is_superuser:
            return queryset

        # Otherwise, filter based on user's role and permissions
        # (Add more specific filtering logic here based on user roles)
        return queryset

    @action(detail=False, methods=['get'], url_path='entity/(?P<content_type_id>[^/.]+)/(?P<object_id>[^/.]+)')
    def get_entity_history(self, request, content_type_id, object_id):
        """
        Returns transition history for a specific entity

        Args:
            request (object): The request object
            content_type_id (str): The ID of the content type
            object_id (str): The ID of the object

        Returns:
            Response: API response with entity transition history
        """
        # Get the ContentType object using content_type_id
        try:
            content_type = ContentType.objects.get(pk=content_type_id)
        except ContentType.DoesNotExist:
            return Response({"error": "Invalid content type ID"}, status=status.HTTP_400_BAD_REQUEST)

        # Filter queryset by content_type and object_id
        queryset = self.get_queryset().filter(content_type=content_type, object_id=object_id)

        # Paginate the results if needed
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Serialize the filtered queryset
        serializer = self.get_serializer(queryset, many=True)

        # Return Response with serialized data
        return Response(serializer.data)


class WorkflowTaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for workflow tasks
    """
    queryset = WorkflowTask.objects.all().order_by('-created_at')
    serializer_class = WorkflowTaskSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['task_type', 'status', 'assigned_to', 'content_type', 'object_id']

    def get_queryset(self):
        """
        Returns filtered queryset based on user permissions

        Returns:
            QuerySet: Filtered queryset of workflow tasks
        """
        # Get the base queryset from parent
        queryset = super().get_queryset()

        # If user is a system admin, return all tasks
        if self.request.user.is_superuser:
            return queryset

        # If user is internal, filter by assigned_to=user or null
        if self.request.user.role in ['underwriter', 'qc']:
            return queryset.filter(assigned_to=self.request.user)

        # If user is school admin, filter by school's applications
        # (Add more specific filtering logic here based on user roles)
        # If user is borrower/co-borrower, filter by user's applications
        return queryset

    @action(detail=False, methods=['get'], url_path='entity/(?P<content_type_id>[^/.]+)/(?P<object_id>[^/.]+)')
    def get_entity_tasks(self, request, content_type_id, object_id):
        """
        Returns tasks for a specific entity

        Args:
            request (object): The request object
            content_type_id (str): The ID of the content type
            object_id (str): The ID of the object

        Returns:
            Response: API response with entity tasks
        """
        # Get the ContentType object using content_type_id
        try:
            content_type = ContentType.objects.get(pk=content_type_id)
        except ContentType.DoesNotExist:
            return Response({"error": "Invalid content type ID"}, status=status.HTTP_400_BAD_REQUEST)

        # Filter queryset by content_type and object_id
        queryset = self.get_queryset().filter(content_type=content_type, object_id=object_id)

        # Check if user has permission to view these tasks
        # (Add permission check logic here based on user roles)

        # Paginate the results if needed
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Serialize the filtered queryset
        serializer = self.get_serializer(queryset, many=True)

        # Return Response with serialized data
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def get_user_tasks(self, request):
        """
        Returns tasks assigned to the current user

        Args:
            request (object): The request object

        Returns:
            Response: API response with user's tasks
        """
        # Filter queryset by assigned_to=request.user
        queryset = self.get_queryset().filter(assigned_to=request.user)

        # Paginate the results if needed
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Serialize the filtered queryset
        serializer = self.get_serializer(queryset, many=True)

        # Return Response with serialized data
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete_task(self, request, pk=None):
        """
        Marks a task as completed

        Args:
            request (object): The request object
            pk (str): The primary key of the task

        Returns:
            Response: API response with updated task
        """
        # Get the task object using pk
        task = self.get_object()

        # Check if user has permission to complete this task
        # (Add permission check logic here based on user roles)

        # Get notes from request data
        notes = request.data.get('notes')

        try:
            # Call task.complete() with user and notes
            self.serializer_class().complete(task, request.user, notes)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        # Serialize the updated task
        serializer = self.get_serializer(task)

        # Return Response with serialized data
        return Response(serializer.data)


class AutomaticTransitionScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for automatic transition schedules
    """
    queryset = AutomaticTransitionSchedule.objects.all().order_by('-scheduled_date')
    serializer_class = AutomaticTransitionScheduleSerializer
    permission_classes = [IsInternalUser]
    filterset_fields = ['workflow_type', 'from_state', 'to_state', 'is_executed', 'content_type', 'object_id']

    @action(detail=True, methods=['post'])
    def execute_transition(self, request, pk=None):
        """
        Manually executes a scheduled transition

        Args:
            request (object): The request object
            pk (str): The primary key of the schedule

        Returns:
            Response: API response with execution result
        """
        # Get the schedule object using pk
        schedule = self.get_object()

        # Check if schedule is already executed
        if schedule.is_executed:
            return Response({"error": "Schedule already executed"}, status=status.HTTP_400_BAD_REQUEST)

        # Call schedule.execute() to perform the transition
        success = schedule.execute()

        # Return Response with success status and result
        if success:
            return Response({"status": "success", "result": "Transition executed"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Transition failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='entity/(?P<content_type_id>[^/.]+)/(?P<object_id>[^/.]+)')
    def get_entity_schedules(self, request, content_type_id, object_id):
        """
        Returns transition schedules for a specific entity

        Args:
            request (object): The request object
            content_type_id (str): The ID of the content type
            object_id (str): The ID of the object

        Returns:
            Response: API response with entity schedules
        """
        # Get the ContentType object using content_type_id
        try:
            content_type = ContentType.objects.get(pk=content_type_id)
        except ContentType.DoesNotExist:
            return Response({"error": "Invalid content type ID"}, status=status.HTTP_400_BAD_REQUEST)

        # Filter queryset by content_type and object_id
        queryset = self.get_queryset().filter(content_type=content_type, object_id=object_id)

        # Paginate the results if needed
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Serialize the filtered queryset
        serializer = self.get_serializer(queryset, many=True)

        # Return Response with serialized data
        return Response(serializer.data)


class WorkflowConfigurationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for workflow configuration settings
    """
    queryset = WorkflowConfiguration.objects.all().order_by('workflow_type', 'config_key')
    serializer_class = WorkflowConfigurationSerializer
    permission_classes = [IsSystemAdmin]
    filterset_fields = ['workflow_type', 'config_key', 'is_active']


class WorkflowStateView(views.APIView):
    """
    API view for retrieving workflow state information
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, content_type_id, object_id):
        """
        Handles GET requests for workflow state information

        Args:
            request (object): The request object
            content_type_id (str): The ID of the content type
            object_id (str): The ID of the object

        Returns:
            Response: API response with workflow state information
        """
        try:
            # Get the entity using get_entity_from_content_type()
            entity = get_entity_from_content_type(content_type_id, object_id)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        # Check if user has permission to view this entity
        # (Add permission check logic here based on user roles)

        # Create a WorkflowStateSerializer instance with the entity
        serializer = WorkflowStateSerializer(instance=entity)

        # Return Response with serialized workflow state data
        return Response(serializer.data)


class WorkflowTransitionView(views.APIView):
    """
    Base API view for workflow transitions
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, content_type_id, object_id):
        """
        Handles POST requests for workflow transitions

        Args:
            request (object): The request object
            content_type_id (str): The ID of the content type
            object_id (str): The ID of the object

        Returns:
            Response: API response with transition result
        """
        try:
            # Get the entity using get_entity_from_content_type()
            entity = get_entity_from_content_type(content_type_id, object_id)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        # Check if user has permission to transition this entity
        # (Add permission check logic here based on user roles)

        # Create a WorkflowTransitionSerializer with request data and entity context
        serializer_class = self.get_serializer_class(entity)
        serializer = serializer_class(data=request.data, context={'entity': entity, 'user': request.user})

        # Validate the serializer data
        if serializer.is_valid():
            # If valid, call serializer.save() to perform the transition
            entity = serializer.save()

            # Return Response with success status and updated entity state
            state_serializer = WorkflowStateSerializer(instance=entity)
            return Response(state_serializer.data, status=status.HTTP_200_OK)
        else:
            # If invalid, return Response with error details
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self, entity):
        """
        Returns the appropriate serializer class based on workflow type

        Args:
            entity (object): The entity being transitioned

        Returns:
            class: Serializer class for the entity's workflow type
        """
        # Get the workflow type from entity.get_workflow_type()
        workflow_type = entity.get_workflow_type()

        # Return the appropriate serializer class based on workflow type:
        if workflow_type == WORKFLOW_TYPES['APPLICATION']:
            return ApplicationTransitionSerializer
        elif workflow_type == WORKFLOW_TYPES['DOCUMENT']:
            return DocumentTransitionSerializer
        elif workflow_type == WORKFLOW_TYPES['FUNDING']:
            return FundingTransitionSerializer
        else:
            return WorkflowTransitionSerializer


class ApplicationTransitionView(WorkflowTransitionView):
    """
    API view for application-specific transitions
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, content_type_id, object_id, transition_type):
        """
        Handles POST requests for application transitions

        Args:
            request (object): The request object
            content_type_id (str): The ID of the content type
            object_id (str): The ID of the object
            transition_type (str): The type of application transition

        Returns:
            Response: API response with transition result
        """
        try:
            # Get the entity using get_entity_from_content_type()
            entity = get_entity_from_content_type(content_type_id, object_id)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        # Check if entity workflow type is APPLICATION
        if entity.get_workflow_type() != WORKFLOW_TYPES['APPLICATION']:
            return Response({"error": "Invalid workflow type for this view"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user has permission for this transition type
        # (Add permission check logic here based on user roles and transition_type)

        # Get the appropriate serializer class based on transition_type:
        if transition_type == 'underwriting_decision':
            serializer_class = UnderwritingDecisionSerializer
        elif transition_type == 'commitment_response':
            serializer_class = CommitmentResponseSerializer
        elif transition_type == 'qc_decision':
            serializer_class = QCDecisionSerializer
        else:
            serializer_class = ApplicationTransitionSerializer

        # Create serializer with request data and entity context
        serializer = serializer_class(data=request.data, context={'entity': entity, 'user': request.user})

        # Validate the serializer data
        if serializer.is_valid():
            # If valid, call serializer.save() to perform the transition
            entity = serializer.save()

            # Return Response with success status and updated entity state
            state_serializer = WorkflowStateSerializer(instance=entity)
            return Response(state_serializer.data, status=status.HTTP_200_OK)
        else:
            # If invalid, return Response with error details
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DocumentTransitionView(WorkflowTransitionView):
    """
    API view for document-specific transitions
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, content_type_id, object_id, transition_type):
        """
        Handles POST requests for document transitions

        Args:
            request (object): The request object
            content_type_id (str): The ID of the content type
            object_id (str): The ID of the object
            transition_type (str): The type of document transition

        Returns:
            Response: API response with transition result
        """
        try:
            # Get the entity using get_entity_from_content_type()
            entity = get_entity_from_content_type(content_type_id, object_id)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        # Check if entity workflow type is DOCUMENT
        if entity.get_workflow_type() != WORKFLOW_TYPES['DOCUMENT']:
            return Response({"error": "Invalid workflow type for this view"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user has permission for this transition type
        # (Add permission check logic here based on user roles and transition_type)

        # Get the appropriate serializer class based on transition_type:
        if transition_type == 'signature_event':
            serializer_class = DocumentSignatureEventSerializer
        else:
            serializer_class = DocumentTransitionSerializer

        # Create serializer with request data and entity context
        serializer = serializer_class(data=request.data, context={'entity': entity, 'user': request.user})

        # Validate the serializer data
        if serializer.is_valid():
            # If valid, call serializer.save() to perform the transition
            entity = serializer.save()

            # Return Response with success status and updated entity state
            state_serializer = WorkflowStateSerializer(instance=entity)
            return Response(state_serializer.data, status=status.HTTP_200_OK)
        else:
            # If invalid, return Response with error details
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FundingTransitionView(WorkflowTransitionView):
    """
    API view for funding-specific transitions
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, content_type_id, object_id, transition_type):
        """
        Handles POST requests for funding transitions

        Args:
            request (object): The request object
            content_type_id (str): The ID of the content type
            object_id (str): The ID of the object
            transition_type (str): The type of funding transition

        Returns:
            Response: API response with transition result
        """
        try:
            # Get the entity using get_entity_from_content_type()
            entity = get_entity_from_content_type(content_type_id, object_id)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        # Check if entity workflow type is FUNDING
        if entity.get_workflow_type() != WORKFLOW_TYPES['FUNDING']:
            return Response({"error": "Invalid workflow type for this view"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user has permission for this transition type
        # (Add permission check logic here based on user roles and transition_type)

        # Get the appropriate serializer class based on transition_type:
        if transition_type == 'enrollment_verification':
            serializer_class = EnrollmentVerificationSerializer
        elif transition_type == 'stipulation_verification':
            serializer_class = StipulationVerificationSerializer
        elif transition_type == 'disbursement':
            serializer_class = DisbursementSerializer
        else:
            serializer_class = FundingTransitionSerializer

        # Create serializer with request data and entity context
        serializer = serializer_class(data=request.data, context={'entity': entity, 'user': request.user})

        # Validate the serializer data
        if serializer.is_valid():
            # If valid, call serializer.save() to perform the transition
            entity = serializer.save()

            # Return Response with success status and updated entity state
            state_serializer = WorkflowStateSerializer(instance=entity)
            return Response(state_serializer.data, status=status.HTTP_200_OK)
        else:
            # If invalid, return Response with error details
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)