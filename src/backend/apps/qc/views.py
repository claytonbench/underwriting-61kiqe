"""
Implements the API views for the Quality Control (QC) module of the loan management system.
These views handle HTTP requests related to QC reviews, document verification, stipulation
verification, and checklist management. The QC process is a critical step that occurs
after document completion and before funding approval to ensure all loan documents are
accurate, complete, and compliant.
"""
import logging  # standard library
from rest_framework.views import APIView  # rest_framework version: 3.14+
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, RetrieveUpdateAPIView, GenericAPIView  # rest_framework version: 3.14+
from rest_framework.response import Response  # rest_framework version: 3.14+
from rest_framework import status  # rest_framework version: 3.14+
from django.shortcuts import get_object_or_404  # django version: 4.2+
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound  # rest_framework version: 3.14+

from .models import QCReview, DocumentVerification, QCStipulationVerification, QCChecklistItem, QCNote  # Internal import
from .serializers import (  # Internal import
    QCReviewSerializer, QCReviewDetailSerializer, QCReviewListSerializer,
    DocumentVerificationSerializer, QCStipulationVerificationSerializer,
    QCChecklistItemSerializer, QCNoteSerializer, QCReviewAssignmentSerializer,
    QCReviewStatusUpdateSerializer, QCReviewSummarySerializer
)
from .permissions import (  # Internal import
    CanViewQCReviews, CanManageQCReviews, IsAssignedQCReviewer,
    CanAssignQCReviews, CanApproveQCReview, CanReturnQCReview,
    CanVerifyDocuments, CanVerifyStipulations, CanManageQCChecklist
)
from .services import QCReviewService, DocumentVerificationService, StipulationVerificationService, ChecklistItemService  # Internal import
from .constants import QC_STATUS  # Internal import
from apps.applications.models import LoanApplication  # Internal import

# Initialize logger
logger = logging.getLogger(__name__)


class QCReviewListView(ListAPIView):
    """
    API view for listing QC reviews with filtering options
    """
    serializer_class = QCReviewListSerializer
    permission_classes = [CanViewQCReviews]
    queryset = QCReview.objects.all()

    def get_queryset(self):
        """
        Returns filtered queryset based on request parameters

        Returns:
            QuerySet: Filtered QCReview queryset
        """
        queryset = super().get_queryset()  # Get base queryset from parent method

        # Apply status filter if provided in request
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Apply priority filter if provided in request
        priority_filter = self.request.query_params.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)

        # Apply reviewer filter if provided in request
        reviewer_filter = self.request.query_params.get('reviewer')
        if reviewer_filter:
            queryset = queryset.filter(assigned_to=reviewer_filter)

        # Apply date range filter if provided in request
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])

        return queryset  # Return the filtered queryset


class QCReviewDetailView(RetrieveAPIView):
    """
    API view for retrieving a single QC review with detailed information
    """
    serializer_class = QCReviewDetailSerializer
    permission_classes = [CanViewQCReviews]
    queryset = QCReview.objects.all()


class QCReviewCreateView(CreateAPIView):
    """
    API view for creating a new QC review
    """
    serializer_class = QCReviewSerializer
    permission_classes = [CanManageQCReviews]

    def perform_create(self, serializer):
        """
        Creates a QC review using the service layer

        Args:
            serializer (Serializer): serializer

        Returns:
            None: No return value
        """
        validated_data = serializer.validated_data  # Get validated data from serializer
        application = validated_data.pop('application')  # Extract application from validated data
        priority = validated_data.pop('priority', QC_STATUS['MEDIUM'])  # Extract priority from validated data

        qc_review_service = QCReviewService()  # Initialize QCReviewService
        qc_review_service.create_review(application=application, priority=priority, user=self.request.user)  # Call service.create_review with application, priority, and request.user

        logger.info(f"QC review created for application {application.id} by user {self.request.user.id}")  # Log the creation of the QC review


class QCReviewAssignView(APIView):
    """
    API view for assigning a QC review to a reviewer
    """
    serializer_class = QCReviewAssignmentSerializer
    permission_classes = [CanAssignQCReviews]

    def post(self, request, pk):
        """
        Handles POST request to assign a QC review

        Args:
            request (Request): request
            pk (UUID): pk

        Returns:
            Response: API response with assignment result
        """
        qc_review = get_object_or_404(QCReview, pk=pk)  # Get QC review by ID or return 404
        serializer = self.serializer_class(data=request.data)  # Create serializer with request data
        serializer.is_valid(raise_exception=True)  # Validate serializer data
        serializer.context['qc_review'] = qc_review  # Add qc_review to serializer context
        qc_review = serializer.save()  # Call serializer.save() to perform assignment
        return Response(QCReviewSerializer(qc_review).data, status=status.HTTP_200_OK)  # Return success response with updated QC review data


class QCReviewStatusUpdateView(APIView):
    """
    API view for updating the status of a QC review (approve or return)
    """
    serializer_class = QCReviewStatusUpdateSerializer
    permission_classes = [IsAssignedQCReviewer]

    def post(self, request, pk):
        """
        Handles POST request to update QC review status

        Args:
            request (Request): request
            pk (UUID): pk

        Returns:
            Response: API response with status update result
        """
        qc_review = get_object_or_404(QCReview, pk=pk)  # Get QC review by ID or return 404
        self.check_object_permissions(request, self, qc_review)  # Check object-level permissions
        serializer = self.serializer_class(data=request.data)  # Create serializer with request data
        serializer.is_valid(raise_exception=True)  # Validate serializer data
        serializer.context['qc_review'] = qc_review  # Add qc_review to serializer context
        serializer.context['request'] = request  # Add request.user to serializer context
        qc_review = serializer.save()  # Call serializer.save() to perform status update
        return Response(QCReviewSerializer(qc_review).data, status=status.HTTP_200_OK)  # Return success response with updated QC review data


class QCReviewReopenView(APIView):
    """
    API view for reopening a returned QC review
    """
    permission_classes = [CanManageQCReviews]

    def post(self, request, pk):
        """
        Handles POST request to reopen a QC review

        Args:
            request (Request): request
            pk (UUID): pk

        Returns:
            Response: API response with reopen result
        """
        qc_review = get_object_or_404(QCReview, pk=pk)  # Get QC review by ID or return 404
        qc_review_service = QCReviewService()  # Initialize QCReviewService
        qc_review_service.reopen_review(qc_review=qc_review, user=request.user)  # Call service.reopen_review with qc_review and request.user
        return Response(QCReviewSerializer(qc_review).data, status=status.HTTP_200_OK)  # Return success response with updated QC review data


class QCReviewSummaryView(APIView):
    """
    API view for retrieving summary statistics of QC reviews
    """
    permission_classes = [CanViewQCReviews]

    def get(self, request):
        """
        Handles GET request to retrieve QC review summary

        Args:
            request (Request): request

        Returns:
            Response: API response with QC review summary statistics
        """
        qc_review_service = QCReviewService()  # Initialize QCReviewService

        pending_count = qc_review_service.get_pending_reviews().count()  # Get pending reviews count
        in_review_count = qc_review_service.get_in_progress_reviews().count()  # Get in-progress reviews count
        approved_count = qc_review_service.get_approved_reviews().count()  # Get approved reviews count
        returned_count = qc_review_service.get_returned_reviews().count()  # Get returned reviews count
        overdue_count = 0  # TODO: Implement overdue reviews count
        assigned_to_me_count = 0  # TODO: Implement reviews assigned to current user count
        completed_today_count = 0  # TODO: Implement reviews completed today count
        average_completion_time = 0.0  # TODO: Implement average completion time

        summary_data = {  # Create summary data dictionary
            'pending_count': pending_count,
            'in_review_count': in_review_count,
            'approved_count': approved_count,
            'returned_count': returned_count,
            'overdue_count': overdue_count,
            'assigned_to_me_count': assigned_to_me_count,
            'completed_today_count': completed_today_count,
            'average_completion_time': average_completion_time,
        }

        serializer = QCReviewSummarySerializer(summary_data)  # Serialize summary data
        return Response(serializer.data, status=status.HTTP_200_OK)  # Return response with serialized data


class DocumentVerificationView(RetrieveUpdateAPIView):
    """
    API view for managing document verification in QC process
    """
    serializer_class = DocumentVerificationSerializer
    permission_classes = [CanVerifyDocuments]
    queryset = DocumentVerification.objects.all()

    def get_serializer_context(self):
        """
        Adds current user to serializer context

        Returns:
            dict: Serializer context with current user
        """
        context = super().get_serializer_context()  # Get context from parent method
        context['request'] = self.request  # Add request.user to context
        return context  # Return the updated context

    def perform_update(self, serializer):
        """
        Updates document verification using the service layer

        Args:
            serializer (Serializer): serializer

        Returns:
            None: No return value
        """
        validated_data = serializer.validated_data  # Get validated data from serializer
        status = validated_data.get('status')  # Extract status from validated data
        comments = validated_data.get('comments')  # Extract comments from validated data

        document_verification_service = DocumentVerificationService()  # Initialize DocumentVerificationService

        if status == QC_VERIFICATION_STATUS['VERIFIED']:  # If status is 'VERIFIED'
            document_verification_service.verify_document(serializer.instance, self.request.user, comments)  # Call service.verify_document
        elif status == QC_VERIFICATION_STATUS['REJECTED']:  # If status is 'REJECTED'
            document_verification_service.reject_document(serializer.instance, self.request.user, comments)  # Call service.reject_document
        elif status == QC_VERIFICATION_STATUS['WAIVED']:  # If status is 'WAIVED'
            document_verification_service.waive_document(serializer.instance, self.request.user, comments)  # Call service.waive_document
        else:
            super().perform_update(serializer)  # Otherwise, call parent perform_update method

        logger.info(f"Document verification updated for document {serializer.instance.document.id} by user {self.request.user.id}")  # Log the document verification update


class StipulationVerificationView(RetrieveUpdateAPIView):
    """
    API view for managing stipulation verification in QC process
    """
    serializer_class = QCStipulationVerificationSerializer
    permission_classes = [CanVerifyStipulations]
    queryset = QCStipulationVerification.objects.all()

    def get_serializer_context(self):
        """
        Adds current user to serializer context

        Returns:
            dict: Serializer context with current user
        """
        context = super().get_serializer_context()  # Get context from parent method
        context['request'] = self.request  # Add request.user to context
        return context  # Return the updated context

    def perform_update(self, serializer):
        """
        Updates stipulation verification using the service layer

        Args:
            serializer (Serializer): serializer

        Returns:
            None: No return value
        """
        validated_data = serializer.validated_data  # Get validated data from serializer
        status = validated_data.get('status')  # Extract status from validated data
        comments = validated_data.get('comments')  # Extract comments from validated data

        stipulation_verification_service = StipulationVerificationService()  # Initialize StipulationVerificationService

        if status == QC_VERIFICATION_STATUS['VERIFIED']:  # If status is 'VERIFIED'
            stipulation_verification_service.verify_stipulation(serializer.instance, self.request.user, comments)  # Call service.verify_stipulation
        elif status == QC_VERIFICATION_STATUS['REJECTED']:  # If status is 'REJECTED'
            stipulation_verification_service.reject_stipulation(serializer.instance, self.request.user, comments)  # Call service.reject_stipulation
        elif status == QC_VERIFICATION_STATUS['WAIVED']:  # If status is 'WAIVED'
            stipulation_verification_service.waive_stipulation(serializer.instance, self.request.user, comments)  # Call service.waive_stipulation
        else:
            super().perform_update(serializer)  # Otherwise, call parent perform_update method

        logger.info(f"Stipulation verification updated for stipulation {serializer.instance.stipulation.id} by user {self.request.user.id}")  # Log the stipulation verification update


class ChecklistItemView(RetrieveUpdateAPIView):
    """
    API view for managing checklist items in QC process
    """
    serializer_class = QCChecklistItemSerializer
    permission_classes = [CanManageQCChecklist]
    queryset = QCChecklistItem.objects.all()

    def get_serializer_context(self):
        """
        Adds current user to serializer context

        Returns:
            dict: Serializer context with current user
        """
        context = super().get_serializer_context()  # Get context from parent method
        context['request'] = self.request  # Add request.user to context
        return context  # Return the updated context

    def perform_update(self, serializer):
        """
        Updates checklist item using the service layer

        Args:
            serializer (Serializer): serializer

        Returns:
            None: No return value
        """
        validated_data = serializer.validated_data  # Get validated data from serializer
        status = validated_data.get('status')  # Extract status from validated data
        comments = validated_data.get('comments')  # Extract comments from validated data

        checklist_item_service = ChecklistItemService()  # Initialize ChecklistItemService

        if status == QC_VERIFICATION_STATUS['VERIFIED']:  # If status is 'VERIFIED'
            checklist_item_service.verify_checklist_item(serializer.instance, self.request.user, comments)  # Call service.verify_checklist_item
        elif status == QC_VERIFICATION_STATUS['REJECTED']:  # If status is 'REJECTED'
            checklist_item_service.reject_checklist_item(serializer.instance, self.request.user, comments)  # Call service.reject_checklist_item
        elif status == QC_VERIFICATION_STATUS['WAIVED']:  # If status is 'WAIVED'
            checklist_item_service.waive_checklist_item(serializer.instance, self.request.user, comments)  # Call service.waive_checklist_item
        else:
            super().perform_update(serializer)  # Otherwise, call parent perform_update method

        logger.info(f"Checklist item updated for item {serializer.instance.item_text} by user {self.request.user.id}")  # Log the checklist item update


class QCReviewByApplicationView(APIView):
    """
    API view for retrieving QC review for a specific loan application
    """
    permission_classes = [CanViewQCReviews]

    def get(self, request, application_id):
        """
        Handles GET request to retrieve QC review for an application

        Args:
            request (Request): request
            application_id (UUID): application_id

        Returns:
            Response: API response with QC review data or 404
        """
        loan_application = get_object_or_404(LoanApplication, pk=application_id)  # Get loan application by ID or return 404
        qc_review_service = QCReviewService()  # Initialize QCReviewService
        qc_review = qc_review_service.get_review_by_application(loan_application)  # Call service.get_review_by_application with application

        if not qc_review:  # If no QC review found, return 404
            raise NotFound("No QC review found for this application.")

        serializer = QCReviewDetailSerializer(qc_review)  # Serialize the QC review with QCReviewDetailSerializer
        return Response(serializer.data, status=status.HTTP_200_OK)  # Return response with serialized data


class QCReviewValidationView(APIView):
    """
    API view for validating a QC review before approval
    """
    permission_classes = [IsAssignedQCReviewer]

    def get(self, request, pk):
        """
        Handles GET request to validate a QC review

        Args:
            request (Request): request
            pk (UUID): pk

        Returns:
            Response: API response with validation results
        """
        qc_review = get_object_or_404(QCReview, pk=pk)  # Get QC review by ID or return 404
        self.check_object_permissions(request, self, qc_review)  # Check object-level permissions
        qc_review_service = QCReviewService()  # Initialize QCReviewService
        validation_results = qc_review_service.validate_review(qc_review)  # Call service.validate_review with qc_review
        return Response(validation_results, status=status.HTTP_200_OK)  # Return response with validation results