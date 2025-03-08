"""
Implements API views for the funding module that handle loan disbursement processes after QC approval.
These views provide endpoints for managing funding requests, enrollment verification, stipulation verification,
disbursements, and funding notes.
"""
# rest_framework version: 3.14+
from rest_framework import generics, status
# rest_framework.response version: 3.14+
from rest_framework.response import Response
# rest_framework.views version: 3.14+
from rest_framework.views import APIView
# django.shortcuts version: 4.2+
from django.shortcuts import get_object_or_404
# rest_framework.exceptions version: 3.14+
from rest_framework.exceptions import ValidationError
# datetime version: standard library
from datetime import date
# logging version: standard library
import logging

# Import base view classes from core app
from core.views import BaseGenericAPIView, TransactionMixin, AuditLogMixin, get_object_or_exception
# Import permission classes from core app
from core.permissions import IsAuthenticated, IsInternalUser, IsQC, IsSchoolAdmin
# Import Funding related models
from .models import FundingRequest, Disbursement, EnrollmentVerification, StipulationVerification, FundingNote
# Import Funding related serializers
from .serializers import (
    FundingRequestSerializer, FundingRequestListSerializer, FundingRequestDetailSerializer,
    FundingStatusUpdateSerializer, FundingApprovalSerializer, DisbursementSerializer,
    DisbursementListSerializer, ProcessDisbursementSerializer, CancelDisbursementSerializer,
    EnrollmentVerificationSerializer, EnrollmentVerificationDetailSerializer, VerifyEnrollmentSerializer,
    StipulationVerificationSerializer, StipulationVerificationDetailSerializer, VerifyStipulationSerializer,
    RejectStipulationSerializer, WaiveStipulationSerializer, FundingNoteSerializer, FundingNoteListSerializer
)
# Import Funding related services
from .services import FundingService, DisbursementService
# Import LoanApplication model from applications app
from apps.applications.models import LoanApplication
# Import Stipulation model from underwriting app
from apps.underwriting.models import Stipulation

# Configure logger
logger = logging.getLogger(__name__)

# Initialize FundingService and DisbursementService
funding_service = FundingService()
disbursement_service = DisbursementService()


class FundingRequestListView(BaseGenericAPIView, generics.ListCreateAPIView):
    """
    API view for listing and creating funding requests
    """
    # Define queryset for listing funding requests
    queryset = FundingRequest.objects.all()
    # Define serializer class for creating funding requests
    serializer_class = FundingRequestSerializer
    # Define serializer class for listing funding requests
    list_serializer_class = FundingRequestListSerializer
    # Define permission classes for this view
    permission_classes = [IsAuthenticated, IsInternalUser]

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the request method
        """
        # If request method is GET, return list_serializer_class
        if self.request.method == 'GET':
            return self.list_serializer_class
        # Otherwise return the default serializer_class
        return self.serializer_class

    def get_queryset(self):
        """
        Returns the queryset filtered by status if specified in query parameters
        """
        # Get the base queryset from the queryset property
        queryset = super().get_queryset()
        # Get status parameter from request query parameters
        status = self.request.query_params.get('status')
        # If status parameter is provided, filter queryset by status
        if status:
            queryset = queryset.filter(status=status)
        # Return the filtered queryset
        return queryset

    def perform_create(self, serializer):
        """
        Sets the request user as the creator of the funding request
        """
        # Call serializer.save() with request.user as the user parameter
        serializer.save(user=self.request.user)
        # Log the creation of the funding request
        self.logger.info(f"Funding request created for application {serializer.instance.application.id}")

    def post(self, request, *args, **kwargs):
        """
        Creates a new funding request for a loan application
        """
        # Get application_id from request data
        application_id = request.data.get('application_id')
        # Get the LoanApplication object or return 404
        application = get_object_or_404(LoanApplication, pk=application_id)
        # Create a funding request using funding_service.create_funding_request
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # Serialize the created funding request
        headers = self.get_success_headers(serializer.data)
        # Return Response with serialized data and 201 Created status
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class FundingRequestDetailView(BaseGenericAPIView, generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a specific funding request
    """
    # Define queryset for retrieving funding requests
    queryset = FundingRequest.objects.all()
    # Define serializer class for detailed view of a funding request
    serializer_class = FundingRequestDetailSerializer
    # Define permission classes for this view
    permission_classes = [IsAuthenticated, IsInternalUser]


class FundingRequestStatusUpdateView(BaseGenericAPIView):
    """
    API view for updating the status of a funding request
    """
    # Define queryset for retrieving funding requests
    queryset = FundingRequest.objects.all()
    # Define serializer class for updating the status of a funding request
    serializer_class = FundingStatusUpdateSerializer
    # Define permission classes for this view
    permission_classes = [IsAuthenticated, IsInternalUser]

    def post(self, request, *args, **kwargs):
        """
        Updates the status of a funding request
        """
        # Get the funding request object
        funding_request = self.get_object()
        # Validate the request data using the serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Get status and comments from validated data
        status_value = serializer.validated_data.get('status')
        comments = serializer.validated_data.get('comments')
        # Update the funding request status using funding_request.update_status
        funding_request.status = status_value
        funding_request.comments = comments
        funding_request.save()
        # Return Response with success message and 200 OK status
        return Response({'status': 'success', 'message': 'Funding request status updated successfully'}, status=status.HTTP_200_OK)


class FundingRequestApprovalView(BaseGenericAPIView):
    """
    API view for approving a funding request
    """
    # Define queryset for retrieving funding requests
    queryset = FundingRequest.objects.all()
    # Define serializer class for approving a funding request
    serializer_class = FundingApprovalSerializer
    # Define permission classes for this view
    permission_classes = [IsAuthenticated, IsInternalUser, IsQC]

    def post(self, request, *args, **kwargs):
        """
        Approves a funding request
        """
        # Get the funding request object
        funding_request = self.get_object()
        # Validate the request data using the serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Get approved_amount and comments from validated data
        approved_amount = serializer.validated_data.get('approved_amount')
        comments = serializer.validated_data.get('comments')
        # Approve the funding request using funding_service.approve_funding
        funding_request.approved_amount = approved_amount
        funding_request.comments = comments
        funding_request.save()
        # Return Response with success message and 200 OK status
        return Response({'status': 'success', 'message': 'Funding request approved successfully'}, status=status.HTTP_200_OK)


class EnrollmentVerificationListView(BaseGenericAPIView, generics.ListCreateAPIView):
    """
    API view for listing and creating enrollment verifications
    """
    # Define queryset for listing enrollment verifications
    queryset = EnrollmentVerification.objects.all()
    # Define serializer class for creating enrollment verifications
    serializer_class = EnrollmentVerificationSerializer
    # Define serializer class for detailed view of an enrollment verification
    list_serializer_class = EnrollmentVerificationDetailSerializer
    # Define permission classes for this view
    permission_classes = [IsAuthenticated, IsSchoolAdmin]

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the request method
        """
        # If request method is GET, return list_serializer_class
        if self.request.method == 'GET':
            return self.list_serializer_class
        # Otherwise return the default serializer_class
        return self.serializer_class

    def perform_create(self, serializer):
        """
        Sets the request user as the verifier of the enrollment verification
        """
        # Call serializer.save() with verified_by=request.user
        serializer.save(verified_by=self.request.user)
        # Log the creation of the enrollment verification
        self.logger.info(f"Enrollment verification created for funding request {serializer.instance.funding_request.id}")


class EnrollmentVerificationDetailView(BaseGenericAPIView, generics.RetrieveAPIView):
    """
    API view for retrieving a specific enrollment verification
    """
    # Define queryset for retrieving enrollment verifications
    queryset = EnrollmentVerification.objects.all()
    # Define serializer class for detailed view of an enrollment verification
    serializer_class = EnrollmentVerificationDetailSerializer
    # Define permission classes for this view
    permission_classes = [IsAuthenticated, IsSchoolAdmin]


class VerifyEnrollmentView(BaseGenericAPIView):
    """
    API view for verifying enrollment for a funding request
    """
    # Define queryset for retrieving funding requests
    queryset = FundingRequest.objects.all()
    # Define serializer class for verifying enrollment
    serializer_class = VerifyEnrollmentSerializer
    # Define permission classes for this view
    permission_classes = [IsAuthenticated, IsSchoolAdmin]

    def post(self, request, *args, **kwargs):
        """
        Verifies enrollment for a funding request
        """
        # Get the funding request object
        funding_request = self.get_object()
        # Validate the request data using the serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Get verification_type, start_date, comments, and document_id from request data
        verification_type = request.data.get('verification_type')
        start_date = request.data.get('start_date')
        comments = serializer.validated_data.get('comments')
        document_id = request.data.get('document_id')
        # Verify enrollment using funding_service.verify_enrollment
        funding_service.verify_enrollment(funding_request, verification_type, start_date, comments, document_id)
        # Return Response with success message and 200 OK status
        return Response({'status': 'success', 'message': 'Enrollment verified successfully'}, status=status.HTTP_200_OK)


class StipulationVerificationListView(BaseGenericAPIView, generics.ListCreateAPIView):
    """
    API view for listing and creating stipulation verifications
    """
    # Define queryset for listing stipulation verifications
    queryset = StipulationVerification.objects.all()
    # Define serializer class for creating stipulation verifications
    serializer_class = StipulationVerificationSerializer
    # Define serializer class for detailed view of a stipulation verification
    list_serializer_class = StipulationVerificationDetailSerializer
    # Define permission classes for this view
    permission_classes = [IsAuthenticated, IsInternalUser]

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the request method
        """
        # If request method is GET, return list_serializer_class
        if self.request.method == 'GET':
            return self.list_serializer_class
        # Otherwise return the default serializer_class
        return self.serializer_class

    def perform_create(self, serializer):
        """
        Sets the request user as the verifier of the stipulation verification
        """
        # Call serializer.save() with verified_by=request.user
        serializer.save(verified_by=self.request.user)
        # Log the creation of the stipulation verification
        self.logger.info(f"Stipulation verification created for stipulation {serializer.instance.stipulation.id}")


class StipulationVerificationDetailView(BaseGenericAPIView, generics.RetrieveAPIView):
    """
    API view for retrieving a specific stipulation verification
    """
    # Define queryset for retrieving stipulation verifications
    queryset = StipulationVerification.objects.all()
    # Define serializer class for detailed view of a stipulation verification
    serializer_class = StipulationVerificationDetailSerializer
    # Define permission classes for this view
    permission_classes = [IsAuthenticated, IsInternalUser]


class VerifyStipulationView(BaseGenericAPIView):
    """
    API view for verifying a stipulation
    """
    # Define queryset for retrieving stipulation verifications
    queryset = StipulationVerification.objects.all()
    # Define serializer class for verifying a stipulation
    serializer_class = VerifyStipulationSerializer
    # Define permission classes for this view
    permission_classes = [IsAuthenticated, IsInternalUser]

    def post(self, request, *args, **kwargs):
        """
        Verifies a stipulation
        """
        # Get the stipulation verification object
        stipulation_verification = self.get_object()
        # Validate the request data using the serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Get comments from validated data
        comments = serializer.validated_data.get('comments')
        # Get the funding request and stipulation from the stipulation verification
        funding_request = stipulation_verification.funding_request
        stipulation = stipulation_verification.stipulation
        # Verify the stipulation using funding_service.verify_stipulation
        funding_service.verify_stipulation(funding_request, stipulation, comments)
        # Return Response with success message and 200 OK status
        return Response({'status': 'success', 'message': 'Stipulation verified successfully'}, status=status.HTTP_200_OK)


class RejectStipulationView(BaseGenericAPIView):
    """
    API view for rejecting a stipulation
    """
    # Define queryset for retrieving stipulation verifications
    queryset = StipulationVerification.objects.all()
    # Define serializer class for rejecting a stipulation
    serializer_class = RejectStipulationSerializer
    # Define permission classes for this view
    permission_classes = [IsAuthenticated, IsInternalUser]

    def post(self, request, *args, **kwargs):
        """
        Rejects a stipulation
        """
        # Get the stipulation verification object
        stipulation_verification = self.get_object()
        # Validate the request data using the serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Get comments from validated data
        comments = serializer.validated_data.get('comments')
        # Get the funding request and stipulation from the stipulation verification
        funding_request = stipulation_verification.funding_request
        stipulation = stipulation_verification.stipulation
        # Reject the stipulation using funding_service.reject_stipulation
        funding_service.reject_stipulation(funding_request, stipulation, comments)
        # Return Response with success message and 200 OK status
        return Response({'status': 'success', 'message': 'Stipulation rejected successfully'}, status=status.HTTP_200_OK)


class WaiveStipulationView(BaseGenericAPIView):
    """
    API view for waiving a stipulation
    """
    # Define queryset for retrieving stipulation verifications
    queryset = StipulationVerification.objects.all()
    # Define serializer class for waiving a stipulation
    serializer_class = WaiveStipulationSerializer
    # Define permission classes for this view
    permission_classes = [IsAuthenticated, IsInternalUser]

    def post(self, request, *args, **kwargs):
        """
        Waives a stipulation
        """
        # Get the stipulation verification object
        stipulation_verification = self.get_object()
        # Validate the request data using the serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Get comments from validated data
        comments = serializer.validated_data.get('comments')
        # Get the funding request and stipulation from the stipulation verification
        funding_request = stipulation_verification.funding_request
        stipulation = stipulation_verification.stipulation
        # Waive the stipulation using funding_service.waive_stipulation
        funding_service.waive_stipulation(funding_request, stipulation, comments)
        # Return Response with success message and 200 OK status
        return Response({'status': 'success', 'message': 'Stipulation waived successfully'}, status=status.HTTP_200_OK)


class DisbursementListView(BaseGenericAPIView, generics.ListCreateAPIView):
    """
    API view for listing and creating disbursements
    """
    # Define queryset for listing disbursements
    queryset = Disbursement.objects.all()
    # Define serializer class for creating disbursements
    serializer_class = DisbursementSerializer
    # Define serializer class for listing disbursements
    list_serializer_class = DisbursementListSerializer
    # Define permission classes for this view
    permission_classes = [IsAuthenticated, IsInternalUser]

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the request method
        """
        # If request method is GET, return list_serializer_class
        if self.request.method == 'GET':
            return self.list_serializer_class
        # Otherwise return the default serializer_class
        return self.serializer_class

    def post(self, request, *args, **kwargs):
        """
        Creates a new disbursement for a funding request
        """
        # Validate the request data using the serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Get funding_request_id, disbursement_date, disbursement_method, and comments from validated data
        funding_request_id = request.data.get('funding_request_id')
        disbursement_date = request.data.get('disbursement_date')
        disbursement_method = request.data.get('disbursement_method')
        comments = serializer.validated_data.get('comments')
        # Get the funding request object
        funding_request = get_object_or_404(FundingRequest, pk=funding_request_id)
        # Schedule the disbursement using disbursement_service.schedule_disbursement
        disbursement_service.schedule_disbursement(funding_request, disbursement_date, disbursement_method, comments)
        # Return Response with success message and 201 Created status
        return Response({'status': 'success', 'message': 'Disbursement scheduled successfully'}, status=status.HTTP_201_CREATED)


class DisbursementDetailView(BaseGenericAPIView, generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a specific disbursement
    """
    # Define queryset for retrieving disbursements
    queryset = Disbursement.objects.all()
    # Define serializer class for detailed view of a disbursement
    serializer_class = DisbursementListSerializer
    # Define permission classes for this view
    permission_classes = [IsAuthenticated, IsInternalUser]


class ProcessDisbursementView(BaseGenericAPIView):
    """
    API view for processing a disbursement
    """
    # Define queryset for retrieving disbursements
    queryset = Disbursement.objects.all()
    # Define serializer class for processing a disbursement
    serializer_class = ProcessDisbursementSerializer
    # Define permission classes for this view
    permission_classes = [IsAuthenticated, IsInternalUser]

    def post(self, request, *args, **kwargs):
        """
        Processes a disbursement
        """
        # Get the disbursement object
        disbursement = self.get_object()
        # Validate the request data using the serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Get reference_number from validated data
        reference_number = serializer.validated_data.get('reference_number')
        # Get the funding request from the disbursement
        funding_request = disbursement.funding_request
        # Process the disbursement using disbursement_service.process_disbursement
        disbursement_service.process_disbursement(funding_request, disbursement, reference_number)
        # Return Response with success message and 200 OK status
        return Response({'status': 'success', 'message': 'Disbursement processed successfully'}, status=status.HTTP_200_OK)


class CancelDisbursementView(BaseGenericAPIView):
    """
    API view for cancelling a disbursement
    """
    # Define queryset for retrieving disbursements
    queryset = Disbursement.objects.all()
    # Define serializer class for cancelling a disbursement
    serializer_class = CancelDisbursementSerializer
    # Define permission classes for this view
    permission_classes = [IsAuthenticated, IsInternalUser]

    def post(self, request, *args, **kwargs):
        """
        Cancels a disbursement
        """
        # Get the disbursement object
        disbursement = self.get_object()
        # Validate the request data using the serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Cancel the disbursement using disbursement_service.cancel_disbursement
        disbursement_service.cancel_disbursement(disbursement)
        # Return Response with success message and 200 OK status
        return Response({'status': 'success', 'message': 'Disbursement cancelled successfully'}, status=status.HTTP_200_OK)


class FundingNoteListView(BaseGenericAPIView, generics.ListCreateAPIView):
    """
    API view for listing and creating funding notes
    """
    # Define queryset for listing funding notes
    queryset = FundingNote.objects.all()
    # Define serializer class for creating funding notes
    serializer_class = FundingNoteSerializer
    # Define serializer class for listing funding notes
    list_serializer_class = FundingNoteListSerializer
    # Define permission classes for this view
    permission_classes = [IsAuthenticated, IsInternalUser]

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the request method
        """
        # If request method is GET, return list_serializer_class
        if self.request.method == 'GET':
            return self.list_serializer_class
        # Otherwise return the default serializer_class
        return self.serializer_class

    def perform_create(self, serializer):
        """
        Sets the request user as the creator of the funding note
        """
        # Call serializer.save() with created_by=request.user
        serializer.save(created_by=self.request.user)
        # Log the creation of the funding note
        self.logger.info(f"Funding note created for funding request {serializer.instance.funding_request.id}")

    def post(self, request, *args, **kwargs):
        """
        Creates a new funding note
        """
        # Validate the request data using the serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Get funding_request_id, note_type, and note_text from validated data
        funding_request_id = request.data.get('funding_request_id')
        note_type = request.data.get('note_type')
        note_text = request.data.get('note_text')
        # Get the funding request object
        funding_request = get_object_or_404(FundingRequest, pk=funding_request_id)
        # Add the funding note using funding_service.add_funding_note
        funding_service.add_funding_note(funding_request, note_type, note_text)
        # Return Response with success message and 201 Created status
        return Response({'status': 'success', 'message': 'Funding note added successfully'}, status=status.HTTP_201_CREATED)


class NextDisbursementDateView(APIView):
    """
    API view for getting the next available disbursement date
    """
    # Define permission classes for this view
    permission_classes = [IsAuthenticated, IsInternalUser]

    def get(self, request, *args, **kwargs):
        """
        Returns the next available disbursement date
        """
        # Get from_date parameter from request query parameters or use today's date
        from_date_str = request.query_params.get('from_date')
        from_date = date.fromisoformat(from_date_str) if from_date_str else date.today()
        # Calculate the next disbursement date using disbursement_service.get_next_disbursement_date
        next_date = disbursement_service.get_next_disbursement_date(from_date)
        # Return Response with the next disbursement date
        return Response({'next_disbursement_date': next_date.isoformat()}, status=status.HTTP_200_OK)


class FundingDashboardView(APIView):
    """
    API view for the funding dashboard with summary statistics
    """
    # Define permission classes for this view
    permission_classes = [IsAuthenticated, IsInternalUser]

    def get(self, request, *args, **kwargs):
        """
        Returns funding dashboard statistics
        """
        # Get pending enrollment verifications count
        pending_enrollment_count = funding_service.get_pending_enrollment_verifications().count()
        # Get pending stipulations count
        pending_stipulations_count = funding_service.get_pending_stipulations().count()
        # Get ready for approval count
        ready_for_approval_count = funding_service.get_ready_for_approval().count()
        # Get approved requests count
        approved_requests_count = funding_service.get_approved_requests().count()
        # Get scheduled disbursements count
        scheduled_disbursements_count = funding_service.get_scheduled_disbursements().count()
        # Get disbursed requests count
        disbursed_requests_count = funding_service.get_disbursed_requests().count()
        # Compile statistics into a dashboard data dictionary
        dashboard_data = {
            'pending_enrollment_verifications': pending_enrollment_count,
            'pending_stipulations': pending_stipulations_count,
            'ready_for_approval': ready_for_approval_count,
            'approved_requests': approved_requests_count,
            'scheduled_disbursements': scheduled_disbursements_count,
            'disbursed_requests': disbursed_requests_count,
        }
        # Return Response with the dashboard data
        return Response(dashboard_data, status=status.HTTP_200_OK)