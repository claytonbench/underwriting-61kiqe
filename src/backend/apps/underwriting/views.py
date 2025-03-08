# rest_framework version: 3.14+
from rest_framework import generics, viewsets, mixins
from rest_framework.response import Response
# rest_framework version: 3.14+
from rest_framework import status
# rest_framework version: 3.14+
from rest_framework.permissions import IsAuthenticated
# django version: 4.2+
from django.shortcuts import get_object_or_404
# standard library
import logging

# Import internal modules and classes
from core.views import BaseAPIView, BaseGenericAPIView, TransactionMixin, AuditLogMixin
from .models import UnderwritingQueue, CreditInformation, UnderwritingDecision, Stipulation, UnderwritingNote
from .serializers import (
    UnderwritingQueueSerializer, CreditInformationSerializer, UnderwritingDecisionSerializer,
    StipulationSerializer, UnderwritingNoteSerializer, ApplicationUnderwritingSerializer,
    UnderwritingDecisionCreateSerializer, StipulationCreateSerializer, StipulationUpdateSerializer,
    UnderwritingNoteCreateSerializer, CreditInformationUploadSerializer
)
from .permissions import (
    CanViewUnderwritingQueue, CanManageUnderwritingQueue, CanAssignUnderwritingQueue,
    CanReviewApplication, CanMakeUnderwritingDecision, CanViewUnderwritingDecision,
    CanManageStipulations, CanSatisfyStipulations, CanAddUnderwritingNote,
    CanViewUnderwritingNotes, CanViewCreditInformation, CanUploadCreditInformation
)
from .services import UnderwritingService
from apps.applications.models import LoanApplication
from .constants import UNDERWRITING_QUEUE_STATUS, UNDERWRITING_QUEUE_PRIORITY
# Import constants from utils
from utils.constants import UNDERWRITING_DECISION

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize underwriting service
underwriting_service = UnderwritingService()


class UnderwritingQueueViewSet(viewsets.ModelViewSet):  # rest_framework version: 3.14+
    """
    ViewSet for managing the underwriting queue.
    """
    serializer_class = UnderwritingQueueSerializer
    queryset = UnderwritingQueue.objects.all()
    permission_classes = [IsAuthenticated, CanViewUnderwritingQueue]

    def get_queryset(self):
        """
        Returns the queryset of underwriting queue items filtered by permissions.

        Returns:
            QuerySet: Filtered queryset of UnderwritingQueue objects
        """
        # Get the base queryset from underwriting_service.get_queue()
        queryset = underwriting_service.get_queue()

        # If user is not a system admin, filter to show only items assigned to the user
        if not self.request.user.is_superuser:
            queryset = queryset.filter(assigned_to=self.request.user)

        # Return the filtered queryset
        return queryset

    def list(self, request):
        """
        List underwriting queue items with optional filtering.

        Args:
            request (object): The request object

        Returns:
            Response: Response with serialized queue items
        """
        # Extract status, priority, and assigned_to filters from query parameters
        status_filter = request.query_params.get('status')
        priority_filter = request.query_params.get('priority')
        assigned_to_filter = request.query_params.get('assigned_to')

        # Get filtered queryset from underwriting_service.get_queue()
        queryset = underwriting_service.get_queue(
            status=status_filter,
            priority=priority_filter,
            assigned_to=assigned_to_filter
        )

        # Paginate the queryset if pagination is configured
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Serialize the queryset
        serializer = self.get_serializer(queryset, many=True)

        # Return Response with serialized data
        return Response(serializer.data)

    def assign(self, request, pk=None):
        """
        Assigns an application in the queue to an underwriter.

        Args:
            request (object): The request object
            pk (int): The primary key of the UnderwritingQueue object

        Returns:
            Response: Response indicating success or failure
        """
        # Get the queue item by primary key
        queue_item = self.get_object()

        # Extract underwriter_id from request data
        underwriter_id = request.data.get('underwriter_id')
        if not underwriter_id:
            return Response({'error': 'underwriter_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the underwriter user object
        try:
            underwriter = User.objects.get(pk=underwriter_id)
        except User.DoesNotExist:
            return Response({'error': 'Underwriter not found'}, status=status.HTTP_404_NOT_FOUND)

        # Call underwriting_service.assign_application(queue_item, underwriter)
        if underwriting_service.assign_application(queue_item, underwriter):
            return Response({'status': 'success', 'message': 'Application assigned successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to assign application'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def start_review(self, request, pk=None):
        """
        Marks an application as in review by the underwriter.

        Args:
            request (object): The request object
            pk (int): The primary key of the UnderwritingQueue object

        Returns:
            Response: Response indicating success or failure
        """
        # Get the queue item by primary key
        queue_item = self.get_object()

        # Call underwriting_service.start_review(queue_item, request.user)
        if underwriting_service.start_review(queue_item, request.user):
            return Response({'status': 'success', 'message': 'Application review started'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to start application review'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_overdue(self, request):
        """
        Lists applications that are past their due date.

        Args:
            request (object): The request object

        Returns:
            Response: Response with serialized overdue queue items
        """
        # Get overdue applications from underwriting_service
        queryset = underwriting_service.get_queue(status='overdue')

        # Serialize the queryset
        serializer = self.get_serializer(queryset, many=True)

        # Return Response with serialized data
        return Response(serializer.data)


class ApplicationReviewView(BaseGenericAPIView):  # rest_framework version: 3.14+
    """
    View for retrieving comprehensive application data for underwriting review.
    """
    serializer_class = ApplicationUnderwritingSerializer
    permission_classes = [IsAuthenticated, CanReviewApplication]

    def get(self, request, application_id):
        """
        Retrieves comprehensive application data for underwriting review.

        Args:
            request (object): The request object
            application_id (int): The ID of the loan application

        Returns:
            Response: Response with comprehensive application data
        """
        # Get the application object by application_id
        application = get_object_or_404(LoanApplication, pk=application_id)

        # Check if user has permission to review this application
        self.check_object_permissions(request, application)

        # Get comprehensive application data from underwriting_service.get_application_data()
        application_data = underwriting_service.get_application_data(application)

        # Return Response with application data
        serializer = self.get_serializer(application)
        return Response(serializer.data)


class ApplicationEvaluationView(BaseGenericAPIView):  # rest_framework version: 3.14+
    """
    View for evaluating an application against underwriting criteria.
    """
    permission_classes = [IsAuthenticated, CanReviewApplication]

    def get(self, request, application_id):
        """
        Evaluates an application against underwriting criteria.

        Args:
            request (object): The request object
            application_id (int): The ID of the loan application

        Returns:
            Response: Response with evaluation results
        """
        # Get the application object by application_id
        application = get_object_or_404(LoanApplication, pk=application_id)

        # Check if user has permission to review this application
        self.check_object_permissions(request, application)

        # Call underwriting_service.evaluate_application(application)
        evaluation_results = underwriting_service.evaluate_application(application)

        # Return Response with evaluation results
        return Response(evaluation_results)


class UnderwritingDecisionView(BaseGenericAPIView):  # rest_framework version: 3.14+
    """
    View for creating and retrieving underwriting decisions.
    """
    serializer_class = UnderwritingDecisionSerializer
    permission_classes = [IsAuthenticated, CanMakeUnderwritingDecision, CanViewUnderwritingDecision]

    def get(self, request, application_id):
        """
        Retrieves the underwriting decision for an application.

        Args:
            request (object): The request object
            application_id (int): The ID of the loan application

        Returns:
            Response: Response with serialized decision data
        """
        # Get the application object by application_id
        application = get_object_or_404(LoanApplication, pk=application_id)

        # Get the underwriting decision for the application
        decision = underwriting_service.get_decision(application)

        # If decision doesn't exist, return 404
        if not decision:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Serialize the decision
        serializer = self.get_serializer(decision)

        # Return Response with serialized data
        return Response(serializer.data)

    def post(self, request, application_id):
        """
        Creates an underwriting decision for an application.

        Args:
            request (object): The request object
            application_id (int): The ID of the loan application

        Returns:
            Response: Response with serialized decision data
        """
        # Get the application object by application_id
        application = get_object_or_404(LoanApplication, pk=application_id)

        # Check if user has permission to make decisions for this application
        self.check_object_permissions(request, application)

        # Validate request data using UnderwritingDecisionCreateSerializer
        serializer = UnderwritingDecisionCreateSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)

        # Extract decision parameters from validated data
        decision = serializer.validated_data['decision']
        comments = serializer.validated_data.get('comments', '')
        approved_amount = serializer.validated_data.get('approved_amount')
        interest_rate = serializer.validated_data.get('interest_rate')
        term_months = serializer.validated_data.get('term_months')
        reason_codes = serializer.validated_data.get('reason_codes', [])

        # Call underwriting_service.record_decision() with parameters
        decision_obj = underwriting_service.record_decision(
            application=application,
            decision=decision,
            comments=comments,
            approved_amount=approved_amount,
            interest_rate=interest_rate,
            term_months=term_months,
            reason_codes=reason_codes,
            user=request.user
        )

        # Serialize the created decision
        serializer = self.get_serializer(decision_obj)

        # Return Response with serialized data
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StipulationViewSet(viewsets.ModelViewSet):  # rest_framework version: 3.14+
    """
    ViewSet for managing stipulations.
    """
    serializer_class = StipulationSerializer
    queryset = Stipulation.objects.all()
    permission_classes = [IsAuthenticated, CanManageStipulations, CanSatisfyStipulations]

    def get_queryset(self):
        """
        Returns the queryset of stipulations filtered by permissions.

        Returns:
            QuerySet: Filtered queryset of Stipulation objects
        """
        queryset = Stipulation.objects.all()

        # If 'application_id' is in request query parameters, filter by application
        application_id = self.request.query_params.get('application_id')
        if application_id:
            queryset = queryset.filter(application_id=application_id)

        # If 'status' is in request query parameters, filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Return the filtered queryset
        return queryset

    def create(self, request):
        """
        Creates a new stipulation.

        Args:
            request (object): The request object

        Returns:
            Response: Response with serialized stipulation data
        """
        # Validate request data using StipulationCreateSerializer
        serializer = StipulationCreateSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)

        # Extract stipulation parameters from validated data
        application = serializer.validated_data['application']
        stipulation_type = serializer.validated_data['stipulation_type']
        description = serializer.validated_data['description']
        required_by_date = serializer.validated_data['required_by_date']

        # Check if user has permission to manage stipulations for this application
        self.check_object_permissions(request, application)

        # Call underwriting_service.create_stipulation() with parameters
        stipulation_obj = underwriting_service.create_stipulation(
            application=application,
            stipulation_type=stipulation_type,
            description=description,
            required_by_date=required_by_date,
            user=request.user
        )

        # Serialize the created stipulation
        serializer = self.get_serializer(stipulation_obj)

        # Return Response with serialized data
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        """
        Updates a stipulation (typically to mark as satisfied).

        Args:
            request (object): The request object
            pk (int): The primary key of the Stipulation object

        Returns:
            Response: Response with serialized stipulation data
        """
        # Get the stipulation object by primary key
        stipulation = self.get_object()

        # Check if user has permission to satisfy this stipulation
        self.check_object_permissions(request, stipulation)

        # Validate request data using StipulationUpdateSerializer
        serializer = StipulationUpdateSerializer(stipulation, data=request.data, partial=True, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)

        # Extract status from validated data
        status_value = serializer.validated_data.get('status')

        # Call underwriting_service.satisfy_stipulation() if status is 'satisfied'
        stipulation_obj = underwriting_service.satisfy_stipulation(
            instance=stipulation,
            status=status_value,
            user=request.user
        )

        # Serialize the updated stipulation
        serializer = self.get_serializer(stipulation_obj)

        # Return Response with serialized data
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        """
        Partially updates a stipulation.

        Args:
            request (object): The request object
            pk (int): The primary key of the Stipulation object

        Returns:
            Response: Response with serialized stipulation data
        """
        return self.update(request, pk=pk, partial=True)


class UnderwritingNoteViewSet(viewsets.ModelViewSet):  # rest_framework version: 3.14+
    """
    ViewSet for managing underwriting notes.
    """
    serializer_class = UnderwritingNoteSerializer
    queryset = UnderwritingNote.objects.all()
    permission_classes = [IsAuthenticated, CanAddUnderwritingNote, CanViewUnderwritingNotes]

    def get_queryset(self):
        """
        Returns the queryset of underwriting notes filtered by permissions.

        Returns:
            QuerySet: Filtered queryset of UnderwritingNote objects
        """
        queryset = UnderwritingNote.objects.all()

        # If 'application_id' is in request query parameters, filter by application
        application_id = self.request.query_params.get('application_id')
        if application_id:
            queryset = queryset.filter(application_id=application_id)

        # If user is not an internal user, exclude internal notes
        if not self.request.user.is_superuser and self.request.user.role not in ['underwriter', 'qc']:
            queryset = queryset.filter(is_internal=False)

        # Return the filtered queryset
        return queryset

    def create(self, request):
        """
        Creates a new underwriting note.

        Args:
            request (object): The request object

        Returns:
            Response: Response with serialized note data
        """
        # Validate request data using UnderwritingNoteCreateSerializer
        serializer = UnderwritingNoteCreateSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)

        # Extract note parameters from validated data
        application = serializer.validated_data['application']
        note_text = serializer.validated_data['note_text']
        is_internal = serializer.validated_data.get('is_internal', True)

        # Check if user has permission to add notes for this application
        self.check_object_permissions(request, application)

        # Call underwriting_service.add_note() with parameters
        note_obj = underwriting_service.add_note(
            application=application,
            note_text=note_text,
            is_internal=is_internal,
            user=request.user
        )

        # Serialize the created note
        serializer = self.get_serializer(note_obj)

        # Return Response with serialized data
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CreditInformationView(BaseGenericAPIView):  # rest_framework version: 3.14+
    """
    View for managing credit information.
    """
    serializer_class = CreditInformationSerializer
    permission_classes = [IsAuthenticated, CanViewCreditInformation, CanUploadCreditInformation]

    def get(self, request, application_id):
        """
        Retrieves credit information for an application.

        Args:
            request (object): The request object
            application_id (int): The ID of the loan application

        Returns:
            Response: Response with serialized credit information
        """
        # Get the application object by application_id
        application = get_object_or_404(LoanApplication, pk=application_id)

        # Check if user has permission to view credit information for this application
        self.check_object_permissions(request, application)

        # Get is_co_borrower parameter from query string
        is_co_borrower = request.query_params.get('is_co_borrower', False)

        # Get credit information from underwriting_service.get_credit_information()
        credit_info = underwriting_service.get_credit_information(application, is_co_borrower=is_co_borrower)

        # If credit information doesn't exist, return 404
        if not credit_info:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Serialize the credit information
        serializer = self.get_serializer(credit_info)

        # Return Response with serialized data
        return Response(serializer.data)

    def post(self, request, application_id):
        """
        Uploads credit information for an application.

        Args:
            request (object): The request object
            application_id (int): The ID of the loan application

        Returns:
            Response: Response with serialized credit information
        """
        # Get the application object by application_id
        application = get_object_or_404(LoanApplication, pk=application_id)

        # Check if user has permission to upload credit information for this application
        self.check_object_permissions(request, application)

        # Validate request data using CreditInformationUploadSerializer
        serializer = CreditInformationUploadSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)

        # Extract credit information parameters from validated data
        borrower = serializer.validated_data['borrower']
        is_co_borrower = serializer.validated_data['is_co_borrower']
        credit_score = serializer.validated_data['credit_score']
        report_reference = serializer.validated_data['report_reference']
        credit_file = serializer.validated_data['credit_file']
        monthly_debt = serializer.validated_data['monthly_debt']

        # Call underwriting_service.add_credit_information() with parameters
        credit_info = underwriting_service.add_credit_information(
            application=application,
            borrower=borrower,
            is_co_borrower=is_co_borrower,
            credit_score=credit_score,
            report_reference=report_reference,
            credit_file=credit_file,
            monthly_debt=monthly_debt,
            user=request.user
        )

        # Serialize the created/updated credit information
        serializer = self.get_serializer(credit_info)

        # Return Response with serialized data
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UnderwritingStatisticsView(BaseAPIView):  # rest_framework version: 3.14+
    """
    View for retrieving underwriting statistics.
    """
    permission_classes = [IsAuthenticated, IsInternalUser]

    def get(self, request):
        """
        Retrieves statistics about the underwriting process.

        Args:
            request (object): The request object

        Returns:
            Response: Response with underwriting statistics
        """
        # Extract start_date and end_date from query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Call underwriting_service.get_statistics() with date parameters
        statistics = underwriting_service.get_statistics(start_date, end_date)

        # Return Response with statistics data
        return Response(statistics)


class UnderwriterWorkloadView(BaseAPIView):  # rest_framework version: 3.14+
    """
    View for retrieving underwriter workload statistics.
    """
    permission_classes = [IsAuthenticated, IsInternalUser]

    def get(self, request, underwriter_id=None):
        """
        Retrieves workload statistics for an underwriter.

        Args:
            request (object): The request object
            underwriter_id (int): The ID of the underwriter user

        Returns:
            Response: Response with workload statistics
        """
        # Get the underwriter user object by underwriter_id
        if underwriter_id:
            underwriter = get_object_or_404(User, pk=underwriter_id)
        else:
            underwriter = request.user

        # Call underwriting_service.get_underwriter_workload() with underwriter
        workload = underwriting_service.get_underwriter_workload(underwriter)

        # Return Response with workload statistics
        return Response(workload)