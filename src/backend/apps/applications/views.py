"""
Implements the API views for the loan application module, providing endpoints for creating, retrieving, updating, and managing loan applications. These views handle the HTTP requests and responses for application-related operations, applying appropriate permissions, serialization, and business logic through the service layer.
"""

import logging  # version standard library
import uuid  # For handling UUID fields

from rest_framework import generics, viewsets, mixins, status  # rest_framework 3.14+
from rest_framework.response import Response  # rest_framework 3.14+
from rest_framework.decorators import action  # rest_framework 3.14+
from rest_framework.permissions import IsAuthenticated  # rest_framework 3.14+

from core.views import BaseGenericAPIView, BaseAPIView, TransactionMixin, AuditLogMixin, format_success_response, get_object_or_exception  # src/backend/core/views.py
from .models import LoanApplication, LoanDetails, ApplicationDocument  # src/backend/apps/applications/models.py
from .serializers import LoanApplicationSerializer, LoanApplicationDetailSerializer, LoanApplicationCreateSerializer, LoanApplicationUpdateSerializer, LoanApplicationSubmitSerializer, LoanDetailsSerializer, ApplicationDocumentSerializer, ApplicationDocumentCreateSerializer, ApplicationFormProgressSerializer  # src/backend/apps/applications/serializers.py
from .permissions import CanViewApplication, CanCreateApplication, CanEditApplication, CanSubmitApplication, CanDeleteApplication, CanUploadDocuments, CanViewApplicationDocuments, CanDeleteApplicationDocument  # src/backend/apps/applications/permissions.py
from .services import ApplicationService, ApplicationServiceError, application_service  # src/backend/apps/applications/services.py
from utils.logging import get_request_logger  # src/backend/utils/logging.py

# Get logger with request context
logger = logging.getLogger(__name__)


class ApplicationViewSet(BaseGenericAPIView, AuditLogMixin, TransactionMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing loan applications with CRUD operations and custom actions
    """
    queryset = LoanApplication.objects.all()
    serializer_class = LoanApplicationSerializer
    permission_classes = [IsAuthenticated, CanViewApplication]

    def __init__(self, *args, **kwargs):
        """
        Default constructor inherited from viewsets.ModelViewSet
        """
        super().__init__(*args, **kwargs)
        self.application_service = ApplicationService()

    def get_queryset(self):
        """
        Returns the queryset filtered based on user role

        Returns:
            QuerySet: Filtered queryset of LoanApplication objects
        """
        # Get the base queryset from LoanApplication.objects.all()
        queryset = LoanApplication.objects.all()
        user = self.request.user

        # If user is a system admin, return all applications
        if user.role == 'system_admin':
            return queryset

        # If user is an underwriter or QC, return all applications
        if user.role in ['underwriter', 'qc']:
            return queryset

        # If user is a school admin, return applications for their school
        if user.role == 'school_admin':
            return queryset.filter(school_id=user.school_id)

        # If user is a borrower, return their applications
        if user.role == 'borrower':
            return queryset.filter(borrower_id=user.id)

        # If user is a co-borrower, return applications where they are co-borrower
        if user.role == 'co_borrower':
            return queryset.filter(co_borrower_id=user.id)

        # Otherwise, return an empty queryset
        return LoanApplication.objects.none()

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the action

        Returns:
            Serializer: Appropriate serializer class for the current action
        """
        # If action is 'create', return LoanApplicationCreateSerializer
        if self.action == 'create':
            return LoanApplicationCreateSerializer

        # If action is 'update' or 'partial_update', return LoanApplicationUpdateSerializer
        if self.action in ['update', 'partial_update']:
            return LoanApplicationUpdateSerializer

        # If action is 'retrieve', return LoanApplicationDetailSerializer
        if self.action == 'retrieve':
            return LoanApplicationDetailSerializer

        # Otherwise, return the default LoanApplicationSerializer
        return LoanApplicationSerializer

    def get_permissions(self):
        """
        Returns the appropriate permission classes based on the action

        Returns:
            list: List of permission instances for the current action
        """
        # If action is 'create', use CanCreateApplication
        if self.action == 'create':
            permission_classes = [IsAuthenticated, CanCreateApplication]

        # If action is 'update' or 'partial_update', use CanEditApplication
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, CanEditApplication]

        # If action is 'destroy', use CanDeleteApplication
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, CanDeleteApplication]

        # Otherwise, use CanViewApplication
        else:
            permission_classes = [IsAuthenticated, CanViewApplication]

        # Return instantiated permission classes
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Performs the creation of a loan application

        Args:
            serializer (Serializer): serializer

        Returns:
            LoanApplication: Created application instance
        """
        # Extract validated data from serializer
        borrower = serializer.validated_data['borrower']
        co_borrower = serializer.validated_data.get('co_borrower')
        school = serializer.validated_data['school']
        program = serializer.validated_data['program']
        application_type = serializer.validated_data['application_type']
        relationship_type = serializer.validated_data.get('relationship_type')
        created_by = self.request.user

        # Call application_service.create_application with appropriate parameters
        application = application_service.create_application(
            borrower=borrower,
            co_borrower=co_borrower,
            school=school,
            program=program,
            application_type=application_type,
            relationship_type=relationship_type,
            created_by=created_by
        )

        # Return the created application instance
        return application

    def perform_update(self, serializer):
        """
        Performs the update of a loan application

        Args:
            serializer (Serializer): serializer

        Returns:
            LoanApplication: Updated application instance
        """
        # Get the application instance
        application = self.get_object()

        # Extract validated data from serializer
        update_data = serializer.validated_data
        updated_by = self.request.user

        # Call application_service.update_application with instance and data
        application = application_service.update_application(
            application=application,
            update_data=update_data,
            updated_by=updated_by
        )

        # Return the updated application instance
        return application

    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated, CanSubmitApplication])
    def submit(self, request, pk=None):
        """
        Custom action to submit an application for review

        Args:
            request (Request): request
            pk (uuid.UUID): pk

        Returns:
            Response: API response indicating success or failure
        """
        # Get the application instance
        application = self.get_object()

        # Call application_service.submit_application with instance and user
        try:
            application_service.submit_application(
                application=application,
                submitted_by=request.user
            )
            # Return success response if submission was successful
            return Response(format_success_response({'message': 'Application submitted successfully'}), status=status.HTTP_200_OK)
        except ApplicationServiceError as e:
            # Return error response if submission failed
            return self.handle_exception(e)

    @action(methods=['get', 'post', 'put'], detail=True, permission_classes=[IsAuthenticated, CanEditApplication])
    def loan_details(self, request, pk=None):
        """
        Custom action to create or update loan details

        Args:
            request (Request): request
            pk (uuid.UUID): pk

        Returns:
            Response: API response with loan details data
        """
        # Get the application instance
        application = self.get_object()

        # If GET request, return existing loan details if any
        if request.method == 'GET':
            loan_details = application.get_loan_details()
            if loan_details:
                serializer = LoanDetailsSerializer(loan_details)
                return Response(format_success_response(serializer.data), status=status.HTTP_200_OK)
            else:
                return Response(format_success_response(None), status=status.HTTP_200_OK)

        # If POST/PUT request, validate and save loan details data
        serializer = LoanDetailsSerializer(data=request.data)
        if serializer.is_valid():
            # Call application_service.create_loan_details with appropriate parameters
            try:
                loan_details = application_service.create_loan_details(
                    application=application,
                    tuition_amount=serializer.validated_data['tuition_amount'],
                    deposit_amount=serializer.validated_data['deposit_amount'],
                    other_funding=serializer.validated_data['other_funding'],
                    requested_amount=serializer.validated_data['requested_amount'],
                    start_date=serializer.validated_data['start_date'],
                    completion_date=serializer.validated_data.get('completion_date')
                )
                # Return response with serialized loan details
                serializer = LoanDetailsSerializer(loan_details)
                return Response(format_success_response(serializer.data), status=status.HTTP_201_CREATED)
            except ApplicationServiceError as e:
                return self.handle_exception(e)
        else:
            return Response(format_success_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get', 'post'], detail=True, permission_classes=[IsAuthenticated, CanUploadDocuments])
    def documents(self, request, pk=None):
        """
        Custom action to manage application documents

        Args:
            request (Request): request
            pk (uuid.UUID): pk

        Returns:
            Response: API response with documents data
        """
        # Get the application instance
        application = self.get_object()

        # If GET request, return list of application documents
        if request.method == 'GET':
            documents = application_service.get_documents(application=application, document_type=request.query_params.get('document_type'))
            serializer = ApplicationDocumentSerializer(documents, many=True)
            return Response(format_success_response(serializer.data), status=status.HTTP_200_OK)

        # If POST request, validate document upload data
        serializer = ApplicationDocumentCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Call application_service.upload_document with appropriate parameters
            try:
                document = application_service.upload_document(
                    application=application,
                    document_type=serializer.validated_data['document_type'],
                    document_file=request.FILES['file'],
                    uploaded_by=request.user
                )
                # Return response with serialized document data
                serializer = ApplicationDocumentSerializer(document)
                return Response(format_success_response(serializer.data), status=status.HTTP_201_CREATED)
            except ApplicationServiceError as e:
                return self.handle_exception(e)
        else:
            return Response(format_success_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True, url_path='documents/(?P<document_id>[^/.]+)/download', permission_classes=[IsAuthenticated, CanViewApplicationDocuments])
    def document_download(self, request, pk=None, document_id=None):
        """
        Custom action to get a download URL for a document

        Args:
            request (Request): request
            pk (uuid.UUID): pk
            document_id (uuid.UUID): document_id

        Returns:
            Response: API response with document download URL
        """
        # Get the application instance
        application = self.get_object()

        # Get the document instance by document_id
        document = get_object_or_exception(
            queryset=ApplicationDocument.objects.all(),
            filter_kwargs={'id': document_id},
            exception_class=ApplicationServiceError,
            message='Document not found'
        )

        # Verify document belongs to the application
        if document.application_id != application.id:
            return Response(format_success_response({'message': 'Document does not belong to this application'}), status=status.HTTP_400_BAD_REQUEST)

        # Generate download URL with appropriate expiry time
        try:
            download_url = document.get_download_url()
            # Return response with download URL
            return Response(format_success_response({'download_url': download_url}), status=status.HTTP_200_OK)
        except ApplicationServiceError as e:
            return self.handle_exception(e)

    @action(methods=['delete'], detail=True, url_path='documents/(?P<document_id>[^/.]+)', permission_classes=[IsAuthenticated, CanDeleteApplicationDocument])
    def delete_document(self, request, pk=None, document_id=None):
        """
        Custom action to delete an application document

        Args:
            request (Request): request
            pk (uuid.UUID): pk
            document_id (uuid.UUID): document_id

        Returns:
            Response: API response indicating success or failure
        """
        # Get the application instance
        application = self.get_object()

        # Get the document instance by document_id
        document = get_object_or_exception(
            queryset=ApplicationDocument.objects.all(),
            filter_kwargs={'id': document_id},
            exception_class=ApplicationServiceError,
            message='Document not found'
        )

        # Verify document belongs to the application
        if document.application_id != application.id:
            return Response(format_success_response({'message': 'Document does not belong to this application'}), status=status.HTTP_400_BAD_REQUEST)

        # Delete the document
        document.delete()

        # Return success response
        return Response(format_success_response({'message': 'Document deleted successfully'}), status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, permission_classes=[IsAuthenticated, CanViewApplication])
    def form_progress(self, request, pk=None):
        """
        Custom action to get application form completion progress

        Args:
            request (Request): request
            pk (uuid.UUID): pk

        Returns:
            Response: API response with form progress data
        """
        # Get the application instance
        application = self.get_object()

        # Call application_service.get_form_progress with instance
        progress_data = application_service.get_form_progress(application=application)

        # Serialize the progress data with ApplicationFormProgressSerializer
        serializer = ApplicationFormProgressSerializer(data=progress_data)
        if serializer.is_valid():
            # Return response with serialized progress data
            return Response(format_success_response(serializer.data), status=status.HTTP_200_OK)
        else:
            return Response(format_success_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)


class ApplicationDocumentViewSet(BaseGenericAPIView, AuditLogMixin, viewsets.ModelViewSet):  # Fixed: Added AuditLogMixin
    """
    ViewSet for managing application documents
    """
    queryset = ApplicationDocument.objects.all()
    serializer_class = ApplicationDocumentSerializer
    permission_classes = [IsAuthenticated, CanViewApplicationDocuments]

    def get_queryset(self):
        """
        Returns the queryset filtered based on user role

        Returns:
            QuerySet: Filtered queryset of ApplicationDocument objects
        """
        # Get the base queryset from ApplicationDocument.objects.all()
        queryset = ApplicationDocument.objects.all()
        user = self.request.user

        # If user is a system admin, return all documents
        if user.role == 'system_admin':
            return queryset

        # If user is an underwriter or QC, return all documents
        if user.role in ['underwriter', 'qc']:
            return queryset

        # If user is a school admin, return documents for their school's applications
        if user.role == 'school_admin':
            return queryset.filter(application__school_id=user.school_id)

        # If user is a borrower, return documents for their applications
        if user.role == 'borrower':
            return queryset.filter(application__borrower_id=user.id)

        # If user is a co-borrower, return documents for applications where they are co-borrower
        if user.role == 'co_borrower':
            return queryset.filter(application__co_borrower_id=user.id)

        # Otherwise, return an empty queryset
        return ApplicationDocument.objects.none()

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the action

        Returns:
            Serializer: Appropriate serializer class for the current action
        """
        # If action is 'create', return ApplicationDocumentCreateSerializer
        if self.action == 'create':
            return ApplicationDocumentCreateSerializer

        # Otherwise, return the default ApplicationDocumentSerializer
        return ApplicationDocumentSerializer

    def get_permissions(self):
        """
        Returns the appropriate permission classes based on the action

        Returns:
            list: List of permission instances for the current action
        """
        # If action is 'create', use CanUploadDocuments
        if self.action == 'create':
            permission_classes = [IsAuthenticated, CanUploadDocuments]

        # If action is 'destroy', use CanDeleteApplicationDocument
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, CanDeleteApplicationDocument]

        # Otherwise, use CanViewApplicationDocuments
        else:
            permission_classes = [IsAuthenticated, CanViewApplicationDocuments]

        # Return instantiated permission classes
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Performs the creation of an application document

        Args:
            serializer (Serializer): serializer

        Returns:
            ApplicationDocument: Created document instance
        """
        # Extract validated data from serializer
        application = serializer.validated_data['application']
        document_type = serializer.validated_data['document_type']
        document_file = self.request.FILES['file']
        uploaded_by = self.request.user

        # Call application_service.upload_document with appropriate parameters
        document = application_service.upload_document(
            application=application,
            document_type=document_type,
            document_file=document_file,
            uploaded_by=uploaded_by
        )

        # Return the created document instance
        return document

    @action(methods=['get'], detail=True, permission_classes=[IsAuthenticated, CanViewApplicationDocuments])
    def download(self, request, pk=None):
        """
        Custom action to get a download URL for a document

        Args:
            request (Request): request
            pk (uuid.UUID): pk

        Returns:
            Response: API response with document download URL
        """
        # Get the document instance
        document = self.get_object()

        # Generate download URL with appropriate expiry time
        try:
            download_url = document.get_download_url()
            # Return response with download URL
            return Response(format_success_response({'download_url': download_url}), status=status.HTTP_200_OK)
        except ApplicationServiceError as e:
            return self.handle_exception(e)


class ApplicationCalculatorView(BaseAPIView):
    """
    API view for calculating loan amounts based on tuition and other factors
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handles POST requests to calculate loan amount

        Args:
            request (Request): request

        Returns:
            Response: API response with calculated loan amount
        """
        # Extract tuition_amount, deposit_amount, and other_funding from request data
        tuition_amount = request.data.get('tuition_amount')
        deposit_amount = request.data.get('deposit_amount')
        other_funding = request.data.get('other_funding')

        # Validate that all required parameters are provided
        if not all([tuition_amount, deposit_amount, other_funding]):
            return Response(format_success_response({'message': 'Missing required parameters'}), status=status.HTTP_400_BAD_REQUEST)

        # Call application_service.calculate_loan_amount with parameters
        try:
            loan_amount = application_service.calculate_loan_amount(
                tuition_amount=Decimal(tuition_amount),
                deposit_amount=Decimal(deposit_amount),
                other_funding=Decimal(other_funding)
            )
            # Return response with calculated loan amount
            return Response(format_success_response({'loan_amount': str(loan_amount)}), status=status.HTTP_200_OK)
        except ApplicationServiceError as e:
            return self.handle_exception(e)