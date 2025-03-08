"""
Defines serializers for the funding module that handle the conversion of funding-related models to and from JSON for API interactions. These serializers support the loan funding process from QC approval through disbursement to schools.
"""
# rest_framework version: 3.14+
from rest_framework import serializers
# rest_framework.exceptions version: 3.14+
from rest_framework.exceptions import ValidationError
# django.utils version: 4.2+
from django.utils import timezone
# standard library
from decimal import Decimal

# Import base serializer classes from core app
from core.serializers import BaseModelSerializer, ReadOnlyModelSerializer, AuditFieldsMixin

# Import Funding related models
from .models import FundingRequest, Disbursement, EnrollmentVerification, StipulationVerification, FundingNote

# Import Funding related constants
from .constants import FUNDING_REQUEST_STATUS, FUNDING_REQUEST_STATUS_CHOICES, DISBURSEMENT_METHOD_CHOICES, DISBURSEMENT_STATUS_CHOICES, ENROLLMENT_VERIFICATION_TYPE_CHOICES, VERIFICATION_STATUS_CHOICES, FUNDING_NOTE_TYPE_CHOICES

# Import serializers from other apps
from apps.applications.serializers import LoanApplicationSerializer
from apps.users.serializers import UserSerializer
from apps.underwriting.serializers import StipulationSerializer


class FundingRequestSerializer(BaseModelSerializer):
    """
    Serializer for creating and updating funding requests
    """
    application_id = serializers.UUIDField()
    requested_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField()
    comments = serializers.CharField()

    class Meta:
        model = FundingRequest
        fields = ['id', 'application_id', 'requested_amount', 'status', 'comments', 'created_at', 'updated_at']

    def validate_status(self, value: str) -> str:
        """
        Validates that the status is a valid choice

        Args:
            value (str): The status value

        Returns:
            str: Validated status value
        """
        # Check if value is in the valid status choices
        if value not in dict(FUNDING_REQUEST_STATUS_CHOICES):
            # If not, raise ValidationError
            raise ValidationError("Invalid status")
        # Return the validated value
        return value

    def validate_requested_amount(self, value: Decimal) -> Decimal:
        """
        Validates that the requested amount is positive

        Args:
            value (Decimal): The requested amount value

        Returns:
            Decimal: Validated amount value
        """
        # Check if value is greater than zero
        if value <= Decimal('0'):
            # If not, raise ValidationError
            raise ValidationError("Requested amount must be greater than zero")
        # Return the validated value
        return value

    def create(self, validated_data: dict) -> FundingRequest:
        """
        Creates a new funding request

        Args:
            validated_data (dict): Validated data for creating the funding request

        Returns:
            FundingRequest: Created funding request instance
        """
        # Extract application_id from validated_data
        application_id = validated_data.pop('application_id')
        # Get the application object
        application = LoanApplication.objects.get(pk=application_id)
        # Create a new FundingRequest with the application and other data
        funding_request = FundingRequest.objects.create(application=application, **validated_data)
        # Set initial status to PENDING if not provided
        if not funding_request.status:
            funding_request.status = FUNDING_REQUEST_STATUS['PENDING']
        # Save the funding request
        funding_request.save()
        # Return the created instance
        return funding_request

    def update(self, instance: FundingRequest, validated_data: dict) -> FundingRequest:
        """
        Updates an existing funding request

        Args:
            instance (FundingRequest): The funding request instance to update
            validated_data (dict): Validated data for updating the funding request

        Returns:
            FundingRequest: Updated funding request instance
        """
        # If status is in validated_data and different from current status
        if 'status' in validated_data and instance.status != validated_data['status']:
            # Get the current user from context
            request = self.context.get('request')
            user = request.user if request else None
            # Update status using instance.update_status()
            instance.update_status(validated_data['status'], user=user)
        # Extract comments if provided
        comments = validated_data.pop('comments', None)
        # Update other fields using parent update method
        instance = super().update(instance, validated_data)
        # Return the updated instance
        return instance


class FundingRequestListSerializer(ReadOnlyModelSerializer):
    """
    Serializer for listing funding requests with minimal information
    """
    id = serializers.UUIDField()
    application = serializers.SerializerMethodField()
    status = serializers.CharField()
    requested_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    approved_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    requested_at = serializers.DateTimeField()
    requested_by = serializers.SerializerMethodField()
    approved_at = serializers.DateTimeField()
    approved_by = serializers.SerializerMethodField()
    approval_level = serializers.CharField()

    class Meta:
        model = FundingRequest
        fields = ['id', 'application', 'status', 'requested_amount', 'approved_amount', 'requested_at', 'requested_by', 'approved_at', 'approved_by', 'approval_level']

    def get_application(self, obj: FundingRequest) -> dict:
        """
        Returns minimal application information

        Args:
            obj (FundingRequest): The FundingRequest instance

        Returns:
            dict: Application data with id, borrower name, and school
        """
        # Get the application from the funding request
        application = obj.application
        # Return a dictionary with application id, borrower name, and school name
        return {
            'id': str(application.id),
            'borrower_name': f"{application.borrower.first_name} {application.borrower.last_name}",
            'school': application.school.name
        }

    def get_requested_by(self, obj: FundingRequest) -> dict:
        """
        Returns the user who requested funding

        Args:
            obj (FundingRequest): The FundingRequest instance

        Returns:
            dict: User data with id and name
        """
        # Get the requested_by user from the funding request
        requested_by = obj.requested_by
        # Return a dictionary with user id and full name
        return {
            'id': str(requested_by.id),
            'name': requested_by.get_full_name()
        }

    def get_approved_by(self, obj: FundingRequest) -> dict:
        """
        Returns the user who approved funding

        Args:
            obj (FundingRequest): The FundingRequest instance

        Returns:
            dict: User data with id and name or None
        """
        # Get the approved_by user from the funding request
        approved_by = obj.approved_by
        # If not None, return a dictionary with user id and full name
        if approved_by:
            return {
                'id': str(approved_by.id),
                'name': approved_by.get_full_name()
            }
        # Otherwise return None
        return None


class FundingRequestDetailSerializer(ReadOnlyModelSerializer):
    """
    Serializer for detailed view of a funding request
    """
    id = serializers.UUIDField()
    application = LoanApplicationSerializer()
    status = serializers.CharField()
    requested_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    approved_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    requested_at = serializers.DateTimeField()
    requested_by = UserSerializer()
    approved_at = serializers.DateTimeField()
    approved_by = UserSerializer()
    approval_level = serializers.CharField()
    enrollment_verification = serializers.SerializerMethodField()
    disbursements = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()

    class Meta:
        model = FundingRequest
        fields = ['id', 'application', 'status', 'requested_amount', 'approved_amount', 'requested_at', 'requested_by', 'approved_at', 'approved_by', 'approval_level', 'enrollment_verification', 'disbursements', 'notes']

    def get_enrollment_verification(self, obj: FundingRequest) -> dict:
        """
        Returns the enrollment verification for this funding request

        Args:
            obj (FundingRequest): The FundingRequest instance

        Returns:
            dict: Enrollment verification data or None
        """
        # Get the enrollment verification from the funding request
        enrollment_verification = obj.get_enrollment_verification()
        # If it exists, serialize it using EnrollmentVerificationSerializer
        if enrollment_verification:
            return EnrollmentVerificationSerializer(enrollment_verification).data
        # Return the serialized data or None
        return None

    def get_disbursements(self, obj: FundingRequest) -> list:
        """
        Returns the disbursements for this funding request

        Args:
            obj (FundingRequest): The FundingRequest instance

        Returns:
            list: List of serialized disbursements
        """
        # Get the disbursements from the funding request
        disbursements = obj.get_disbursements()
        # Serialize them using DisbursementListSerializer
        return DisbursementListSerializer(disbursements, many=True).data

    def get_notes(self, obj: FundingRequest) -> list:
        """
        Returns the notes for this funding request

        Args:
            obj (FundingRequest): The FundingRequest instance

        Returns:
            list: List of serialized funding notes
        """
        # Get the notes from the funding request
        notes = obj.get_notes()
        # Serialize them using FundingNoteListSerializer
        return FundingNoteListSerializer(notes, many=True).data


class DisbursementSerializer(BaseModelSerializer):
    """
    Serializer for creating and updating disbursements
    """
    funding_request_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    disbursement_date = serializers.DateField()
    disbursement_method = serializers.CharField()
    reference_number = serializers.CharField()
    status = serializers.CharField()

    class Meta:
        model = Disbursement
        fields = ['id', 'funding_request_id', 'amount', 'disbursement_date', 'disbursement_method', 'reference_number', 'status', 'created_at', 'updated_at']

    def validate_amount(self, value: Decimal) -> Decimal:
        """
        Validates that the amount is positive

        Args:
            value (Decimal): The amount value

        Returns:
            Decimal: Validated amount value
        """
        # Check if value is greater than zero
        if value <= Decimal('0'):
            # If not, raise ValidationError
            raise ValidationError("Amount must be greater than zero")
        # Return the validated value
        return value

    def validate_disbursement_date(self, value: timezone.datetime) -> timezone.datetime:
        """
        Validates that the disbursement date is in the future and on a valid day

        Args:
            value (date): The disbursement date value

        Returns:
            date: Validated date value
        """
        # Check if date is in the future
        if value < timezone.now().date():
            # If not valid, raise ValidationError
            raise ValidationError("Disbursement date must be in the future")
        # Check if date is on a valid disbursement day
        if value.weekday() not in [0, 1, 2, 3, 4]:  # Monday through Friday
            # If not valid, raise ValidationError
            raise ValidationError("Disbursement date must be on a weekday (Monday - Friday)")
        # Return the validated value
        return value

    def validate_disbursement_method(self, value: str) -> str:
        """
        Validates that the disbursement method is valid

        Args:
            value (str): The disbursement method value

        Returns:
            str: Validated method value
        """
        # Check if value is in the valid method choices
        if value not in dict(DISBURSEMENT_METHOD_CHOICES):
            # If not, raise ValidationError
            raise ValidationError("Invalid disbursement method")
        # Return the validated value
        return value

    def create(self, validated_data: dict) -> Disbursement:
        """
        Creates a new disbursement

        Args:
            validated_data (dict): Validated data for creating the disbursement

        Returns:
            Disbursement: Created disbursement instance
        """
        # Extract funding_request_id from validated_data
        funding_request_id = validated_data.pop('funding_request_id')
        # Get the funding request object
        funding_request = FundingRequest.objects.get(pk=funding_request_id)
        # Create a new Disbursement with the funding request and other data
        disbursement = Disbursement.objects.create(funding_request=funding_request, **validated_data)
        # Set initial status to SCHEDULED if not provided
        if not disbursement.status:
            disbursement.status = FUNDING_REQUEST_STATUS['SCHEDULED_FOR_DISBURSEMENT']
        # Save the disbursement
        disbursement.save()
        # Return the created instance
        return disbursement

    def update(self, instance: Disbursement, validated_data: dict) -> Disbursement:
        """
        Updates an existing disbursement

        Args:
            instance (Disbursement): The disbursement instance to update
            validated_data (dict): Validated data for updating the disbursement

        Returns:
            Disbursement: Updated disbursement instance
        """
        # If status is in validated_data and different from current status
        if 'status' in validated_data and instance.status != validated_data['status']:
            # Handle status transition based on new status
            if validated_data['status'] == FUNDING_REQUEST_STATUS['PROCESSING']:
                instance.process()
            elif validated_data['status'] == FUNDING_REQUEST_STATUS['CANCELLED']:
                instance.cancel()
        # Update other fields using parent update method
        instance = super().update(instance, validated_data)
        # Return the updated instance
        return instance


class DisbursementListSerializer(ReadOnlyModelSerializer):
    """
    Serializer for listing disbursements with minimal information
    """
    id = serializers.UUIDField()
    funding_request_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    disbursement_date = serializers.DateField()
    disbursement_method = serializers.CharField()
    reference_number = serializers.CharField()
    status = serializers.CharField()
    processed_by = serializers.SerializerMethodField()
    processed_at = serializers.DateTimeField()

    class Meta:
        model = Disbursement
        fields = ['id', 'funding_request_id', 'amount', 'disbursement_date', 'disbursement_method', 'reference_number', 'status', 'processed_by', 'processed_at']

    def get_processed_by(self, obj: Disbursement) -> dict:
        """
        Returns the user who processed the disbursement

        Args:
            obj (Disbursement): The Disbursement instance

        Returns:
            dict: User data with id and name or None
        """
        # Get the processed_by user from the disbursement
        processed_by = obj.processed_by
        # If not None, return a dictionary with user id and full name
        if processed_by:
            return {
                'id': str(processed_by.id),
                'name': processed_by.get_full_name()
            }
        # Otherwise return None
        return None


class ProcessDisbursementSerializer(serializers.Serializer):
    """
    Serializer for processing a disbursement
    """
    reference_number = serializers.CharField()

    def validate_reference_number(self, value: str) -> str:
        """
        Validates that the reference number is provided

        Args:
            value (str): The reference number value

        Returns:
            str: Validated reference number
        """
        # Check if value is not empty
        if not value:
            # If empty, raise ValidationError
            raise ValidationError("Reference number is required")
        # Return the validated value
        return value


class CancelDisbursementSerializer(serializers.Serializer):
    """
    Serializer for cancelling a disbursement
    """
    reason = serializers.CharField()


class EnrollmentVerificationSerializer(BaseModelSerializer):
    """
    Serializer for creating enrollment verifications
    """
    funding_request_id = serializers.UUIDField()
    verification_type = serializers.CharField()
    document_id = serializers.UUIDField()
    start_date = serializers.DateField()
    comments = serializers.CharField()

    class Meta:
        model = EnrollmentVerification
        fields = ['id', 'funding_request_id', 'verification_type', 'document_id', 'start_date', 'comments', 'created_at', 'updated_at']

    def validate_verification_type(self, value: str) -> str:
        """
        Validates that the verification type is valid

        Args:
            value (str): The verification type value

        Returns:
            str: Validated verification type
        """
        # Check if value is in the valid verification type choices
        if value not in dict(ENROLLMENT_VERIFICATION_TYPE_CHOICES):
            # If not, raise ValidationError
            raise ValidationError("Invalid verification type")
        # Return the validated value
        return value

    def validate_start_date(self, value: timezone.datetime) -> timezone.datetime:
        """
        Validates that the start date is not in the past

        Args:
            value (date): The start date value

        Returns:
            date: Validated start date
        """
        # Check if date is not in the past
        if value < timezone.now().date():
            # If in the past, raise ValidationError
            raise ValidationError("Start date must be in the future")
        # Return the validated value
        return value

    def create(self, validated_data: dict) -> EnrollmentVerification:
        """
        Creates a new enrollment verification

        Args:
            validated_data (dict): Validated data for creating the enrollment verification

        Returns:
            EnrollmentVerification: Created enrollment verification instance
        """
        # Extract funding_request_id from validated_data
        funding_request_id = validated_data.pop('funding_request_id')
        # Get the funding request object
        funding_request = FundingRequest.objects.get(pk=funding_request_id)
        # Create a new EnrollmentVerification with the funding request and other data
        enrollment_verification = EnrollmentVerification.objects.create(funding_request=funding_request, **validated_data)
        # Save the enrollment verification
        enrollment_verification.save()
        # Return the created instance
        return enrollment_verification


class EnrollmentVerificationDetailSerializer(ReadOnlyModelSerializer):
    """
    Serializer for detailed view of an enrollment verification
    """
    id = serializers.UUIDField()
    funding_request_id = serializers.UUIDField()
    verification_type = serializers.CharField()
    verified_by = UserSerializer()
    verified_at = serializers.DateTimeField()
    start_date = serializers.DateField()
    comments = serializers.CharField()
    document_id = serializers.UUIDField()

    class Meta:
        model = EnrollmentVerification
        fields = ['id', 'funding_request_id', 'verification_type', 'verified_by', 'verified_at', 'start_date', 'comments', 'document_id']


class VerifyEnrollmentSerializer(serializers.Serializer):
    """
    Serializer for verifying enrollment
    """
    comments = serializers.CharField()


class StipulationVerificationSerializer(BaseModelSerializer):
    """
    Serializer for creating stipulation verifications
    """
    funding_request_id = serializers.UUIDField()
    stipulation_id = serializers.UUIDField()
    status = serializers.CharField()
    comments = serializers.CharField()

    class Meta:
        model = StipulationVerification
        fields = ['id', 'funding_request_id', 'stipulation_id', 'status', 'comments', 'created_at', 'updated_at']

    def validate_status(self, value: str) -> str:
        """
        Validates that the status is valid

        Args:
            value (str): The status value

        Returns:
            str: Validated status value
        """
        # Check if value is in the valid status choices
        if value not in dict(VERIFICATION_STATUS_CHOICES):
            # If not, raise ValidationError
            raise ValidationError("Invalid status")
        # Return the validated value
        return value

    def create(self, validated_data: dict) -> StipulationVerification:
        """
        Creates a new stipulation verification

        Args:
            validated_data (dict): Validated data for creating the stipulation verification

        Returns:
            StipulationVerification: Created stipulation verification instance
        """
        # Extract funding_request_id and stipulation_id from validated_data
        funding_request_id = validated_data.pop('funding_request_id')
        stipulation_id = validated_data.pop('stipulation_id')
        # Get the funding request and stipulation objects
        funding_request = FundingRequest.objects.get(pk=funding_request_id)
        stipulation = Stipulation.objects.get(pk=stipulation_id)
        # Create a new StipulationVerification with the funding request, stipulation, and other data
        stipulation_verification = StipulationVerification.objects.create(funding_request=funding_request, stipulation=stipulation, **validated_data)
        # Save the stipulation verification
        stipulation_verification.save()
        # Return the created instance
        return stipulation_verification


class StipulationVerificationDetailSerializer(ReadOnlyModelSerializer):
    """
    Serializer for detailed view of a stipulation verification
    """
    id = serializers.UUIDField()
    funding_request_id = serializers.UUIDField()
    stipulation = StipulationSerializer()
    status = serializers.CharField()
    verified_by = UserSerializer()
    verified_at = serializers.DateTimeField()
    comments = serializers.CharField()

    class Meta:
        model = StipulationVerification
        fields = ['id', 'funding_request_id', 'stipulation', 'status', 'verified_by', 'verified_at', 'comments']


class VerifyStipulationSerializer(serializers.Serializer):
    """
    Serializer for verifying a stipulation
    """
    comments = serializers.CharField()


class RejectStipulationSerializer(serializers.Serializer):
    """
    Serializer for rejecting a stipulation
    """
    comments = serializers.CharField()


class WaiveStipulationSerializer(serializers.Serializer):
    """
    Serializer for waiving a stipulation
    """
    comments = serializers.CharField()


class FundingNoteSerializer(BaseModelSerializer):
    """
    Serializer for creating funding notes
    """
    funding_request_id = serializers.UUIDField()
    note_type = serializers.CharField()
    note_text = serializers.CharField()

    class Meta:
        model = FundingNote
        fields = ['id', 'funding_request_id', 'note_type', 'note_text', 'created_at', 'created_by']

    def validate_note_type(self, value: str) -> str:
        """
        Validates that the note type is valid

        Args:
            value (str): The note type value

        Returns:
            str: Validated note type
        """
        # Check if value is in the valid note type choices
        if value not in dict(FUNDING_NOTE_TYPE_CHOICES):
            # If not, raise ValidationError
            raise ValidationError("Invalid note type")
        # Return the validated value
        return value

    def create(self, validated_data: dict) -> FundingNote:
        """
        Creates a new funding note

        Args:
            validated_data (dict): Validated data for creating the funding note

        Returns:
            FundingNote: Created funding note instance
        """
        # Extract funding_request_id from validated_data
        funding_request_id = validated_data.pop('funding_request_id')
        # Get the funding request object
        funding_request = FundingRequest.objects.get(pk=funding_request_id)
        # Create a new FundingNote with the funding request and other data
        funding_note = FundingNote.objects.create(funding_request=funding_request, **validated_data)
        # Set created_by to the current user from context
        request = self.context.get('request')
        funding_note.created_by = request.user if request else None
        # Save the funding note
        funding_note.save()
        # Return the created instance
        return funding_note


class FundingNoteListSerializer(ReadOnlyModelSerializer):
    """
    Serializer for listing funding notes
    """
    id = serializers.UUIDField()
    funding_request_id = serializers.UUIDField()
    note_type = serializers.CharField()
    note_text = serializers.CharField()
    created_at = serializers.DateTimeField()
    created_by = UserSerializer()

    class Meta:
        model = FundingNote
        fields = ['id', 'funding_request_id', 'note_type', 'note_text', 'created_at', 'created_by']


class FundingApprovalSerializer(serializers.Serializer):
    """
    Serializer for approving a funding request
    """
    approved_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    comments = serializers.CharField()

    def validate_approved_amount(self, value: Decimal) -> Decimal:
        """
        Validates that the approved amount is positive

        Args:
            value (Decimal): The approved amount value

        Returns:
            Decimal: Validated amount value
        """
        # Check if value is greater than zero
        if value <= Decimal('0'):
            # If not, raise ValidationError
            raise ValidationError("Approved amount must be greater than zero")
        # Return the validated value
        return value


class FundingStatusUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating the status of a funding request
    """
    status = serializers.CharField()
    comments = serializers.CharField()

    def validate_status(self, value: str) -> str:
        """
        Validates that the status is valid

        Args:
            value (str): The status value

        Returns:
            str: Validated status value
        """
        # Check if value is in the valid status choices
        if value not in dict(FUNDING_REQUEST_STATUS_CHOICES):
            # If not, raise ValidationError
            raise ValidationError("Invalid status")
        # Return the validated value
        return value