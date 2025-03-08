"""
Defines serializers for the underwriting module that handle the conversion of
underwriting-related models to and from JSON for API interactions. These
serializers support the underwriting workflow, including queue management,
credit information handling, decision recording, and stipulation management.
"""
from rest_framework import serializers  # rest_framework version: 3.14+
from rest_framework.exceptions import ValidationError  # rest_framework version: 3.14+
from django.utils import timezone  # django version: 4.2+
from decimal import Decimal  # standard library
from decimal import InvalidOperation

from core.serializers import BaseModelSerializer, ReadOnlyModelSerializer, AuditFieldsMixin, SensitiveDataMixin
from .models import (
    UnderwritingQueue,
    CreditInformation,
    UnderwritingDecision,
    DecisionReason,
    Stipulation,
    UnderwritingNote,
)
from apps.applications.models import LoanApplication
from apps.users.models import User
from .models import (
    UNDERWRITING_QUEUE_PRIORITY_CHOICES,
    UNDERWRITING_QUEUE_STATUS_CHOICES,
    UNDERWRITING_DECISION_CHOICES,
    DECISION_REASON_CHOICES,
    STIPULATION_TYPE_CHOICES,
    STIPULATION_STATUS_CHOICES,
)
from .services import (
    create_underwriting_decision,
    create_stipulation,
    update_stipulation_status,
    create_underwriting_note,
)


class UnderwritingQueueSerializer(BaseModelSerializer):
    """
    Serializer for the UnderwritingQueue model.
    """
    is_overdue = serializers.SerializerMethodField()
    application_details = serializers.SerializerMethodField()

    class Meta:
        model = UnderwritingQueue
        fields = '__all__'
        read_only_fields = ['application']

    def get_is_overdue(self, obj: UnderwritingQueue) -> bool:
        """
        Calculates whether the queue item is overdue.

        Args:
            obj (UnderwritingQueue): The UnderwritingQueue instance.

        Returns:
            bool: True if the queue item is overdue, False otherwise.
        """
        return obj.is_overdue()

    def get_application_details(self, obj: UnderwritingQueue) -> dict:
        """
        Retrieves basic details about the associated application.

        Args:
            obj (UnderwritingQueue): The UnderwritingQueue instance.

        Returns:
            dict: Dictionary with basic application details.
        """
        application = obj.application
        return {
            'borrower_name': f"{application.borrower.first_name} {application.borrower.last_name}",
            'application_id': str(application.id),
            'submission_date': application.submission_date,
            'program_name': application.program.name,
        }


class CreditInformationSerializer(SensitiveDataMixin, BaseModelSerializer):
    """
    Serializer for the CreditInformation model with sensitive data handling.
    """
    sensitive_fields = ['credit_score', 'monthly_debt', 'debt_to_income_ratio']
    credit_tier = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = CreditInformation
        fields = '__all__'
        read_only_fields = ['application', 'borrower', 'uploaded_by', 'uploaded_at']

    def get_credit_tier(self, obj: CreditInformation) -> str:
        """
        Gets the credit tier based on the credit score.

        Args:
            obj (CreditInformation): The CreditInformation instance.

        Returns:
            str: Credit tier (EXCELLENT, GOOD, FAIR, POOR, or BAD).
        """
        return obj.get_credit_tier()

    def get_download_url(self, obj: CreditInformation) -> str:
        """
        Generates a temporary download URL for the credit report.

        Args:
            obj (CreditInformation): The CreditInformation instance.

        Returns:
            str: Presigned URL for downloading the credit report.
        """
        return obj.get_download_url()


class UnderwritingDecisionSerializer(BaseModelSerializer):
    """
    Serializer for the UnderwritingDecision model.
    """
    reasons = serializers.SerializerMethodField()
    stipulations = serializers.SerializerMethodField()

    class Meta:
        model = UnderwritingDecision
        fields = '__all__'
        read_only_fields = ['application', 'underwriter', 'decision_date']

    def get_reasons(self, obj: UnderwritingDecision) -> list:
        """
        Gets the decision reasons associated with this decision.

        Args:
            obj (UnderwritingDecision): The UnderwritingDecision instance.

        Returns:
            list: List of decision reason dictionaries.
        """
        reasons = obj.get_reasons()
        return [
            {'code': reason.reason_code, 'description': reason.description, 'is_primary': reason.is_primary}
            for reason in reasons
        ]

    def get_stipulations(self, obj: UnderwritingDecision) -> list:
        """
        Gets the stipulations associated with this decision.

        Args:
            obj (UnderwritingDecision): The UnderwritingDecision instance.

        Returns:
            list: List of stipulation dictionaries.
        """
        stipulations = obj.get_stipulations()
        return StipulationSerializer(stipulations, many=True).data

    def create(self, validated_data: dict) -> UnderwritingDecision:
        """
        Creates an underwriting decision using the service layer.

        Args:
            validated_data (dict): Validated data for creating the decision.

        Returns:
            UnderwritingDecision: The created decision object.
        """
        application = validated_data.pop('application')
        decision = validated_data.pop('decision')
        comments = validated_data.pop('comments', '')
        approved_amount = validated_data.pop('approved_amount', None)
        interest_rate = validated_data.pop('interest_rate', None)
        term_months = validated_data.pop('term_months', None)
        reason_codes = validated_data.pop('reason_codes', [])

        request = self.context.get('request')
        user = request.user if request else None

        decision_obj = create_underwriting_decision(
            application=application,
            decision=decision,
            comments=comments,
            approved_amount=approved_amount,
            interest_rate=interest_rate,
            term_months=term_months,
            reason_codes=reason_codes,
            user=user
        )
        return decision_obj


class DecisionReasonSerializer(BaseModelSerializer):
    """
    Serializer for the DecisionReason model.
    """
    class Meta:
        model = DecisionReason
        fields = '__all__'


class StipulationSerializer(BaseModelSerializer):
    """
    Serializer for the Stipulation model.
    """
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Stipulation
        fields = '__all__'
        read_only_fields = ['application', 'created_by', 'created_at']

    def get_is_overdue(self, obj: Stipulation) -> bool:
        """
        Calculates whether the stipulation is overdue.

        Args:
            obj (Stipulation): The Stipulation instance.

        Returns:
            bool: True if the stipulation is overdue, False otherwise.
        """
        return obj.is_overdue()

    def create(self, validated_data: dict) -> Stipulation:
        """
        Creates a stipulation using the service layer.

        Args:
            validated_data (dict): Validated data for creating the stipulation.

        Returns:
            Stipulation: The created stipulation object.
        """
        application = validated_data.pop('application')
        stipulation_type = validated_data.pop('stipulation_type')
        description = validated_data.pop('description')
        required_by_date = validated_data.pop('required_by_date')

        request = self.context.get('request')
        user = request.user if request else None

        stipulation_obj = create_stipulation(
            application=application,
            stipulation_type=stipulation_type,
            description=description,
            required_by_date=required_by_date,
            user=user
        )
        return stipulation_obj

    def update(self, instance: Stipulation, validated_data: dict) -> Stipulation:
        """
        Updates a stipulation's status using the service layer.

        Args:
            instance (Stipulation): The Stipulation instance to update.
            validated_data (dict): Validated data for updating the stipulation.

        Returns:
            Stipulation: The updated stipulation object.
        """
        status = validated_data.pop('status')

        request = self.context.get('request')
        user = request.user if request else None

        stipulation_obj = update_stipulation_status(
            instance=instance,
            status=status,
            user=user
        )
        return stipulation_obj


class UnderwritingNoteSerializer(BaseModelSerializer):
    """
    Serializer for the UnderwritingNote model.
    """
    class Meta:
        model = UnderwritingNote
        fields = '__all__'
        read_only_fields = ['application', 'created_by', 'created_at']

    def create(self, validated_data: dict) -> UnderwritingNote:
        """
        Creates an underwriting note using the service layer.

        Args:
            validated_data (dict): Validated data for creating the note.

        Returns:
            UnderwritingNote: The created note object.
        """
        application = validated_data.pop('application')
        note_text = validated_data.pop('note_text')
        is_internal = validated_data.pop('is_internal', True)

        request = self.context.get('request')
        user = request.user if request else None

        note_obj = create_underwriting_note(
            application=application,
            note_text=note_text,
            is_internal=is_internal,
            user=user
        )
        return note_obj


class ApplicationUnderwritingSerializer(ReadOnlyModelSerializer):
    """
    Serializer for presenting a loan application in the underwriting context.
    """
    borrower_details = serializers.SerializerMethodField()
    co_borrower_details = serializers.SerializerMethodField()
    loan_details = serializers.SerializerMethodField()
    school_program_details = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    credit_information = serializers.SerializerMethodField()
    status_history = serializers.SerializerMethodField()

    class Meta:
        model = LoanApplication
        fields = [
            'id', 'borrower_details', 'co_borrower_details', 'loan_details',
            'school_program_details', 'documents', 'credit_information', 'status_history'
        ]

    def get_borrower_details(self, obj: LoanApplication) -> dict:
        """
        Gets detailed information about the primary borrower.

        Args:
            obj (LoanApplication): The LoanApplication instance.

        Returns:
            dict: Dictionary with borrower details.
        """
        borrower = obj.borrower
        borrower_profile = borrower.borrowerprofile
        employment_info = borrower_profile.employment_info

        return {
            'first_name': borrower.first_name,
            'last_name': borrower.last_name,
            'email': borrower.email,
            'phone': borrower.phone,
            'address': borrower_profile.get_full_address(),
            'employment_type': employment_info.employment_type,
            'employer_name': employment_info.employer_name,
            'occupation': employment_info.occupation,
            'annual_income': employment_info.annual_income,
        }

    def get_co_borrower_details(self, obj: LoanApplication) -> dict:
        """
        Gets detailed information about the co-borrower if present.

        Args:
            obj (LoanApplication): The LoanApplication instance.

        Returns:
            dict: Dictionary with co-borrower details or None.
        """
        if not obj.co_borrower:
            return None

        co_borrower = obj.co_borrower
        co_borrower_profile = co_borrower.borrowerprofile
        co_borrower_employment_info = co_borrower_profile.employment_info

        return {
            'first_name': co_borrower.first_name,
            'last_name': co_borrower.last_name,
            'email': co_borrower.email,
            'phone': co_borrower.phone,
            'address': co_borrower_profile.get_full_address(),
            'employment_type': co_borrower_employment_info.employment_type,
            'employer_name': co_borrower_employment_info.employer_name,
            'occupation': co_borrower_employment_info.occupation,
            'annual_income': co_borrower_employment_info.annual_income,
        }

    def get_loan_details(self, obj: LoanApplication) -> dict:
        """
        Gets financial details of the loan application.

        Args:
            obj (LoanApplication): The LoanApplication instance.

        Returns:
            dict: Dictionary with loan financial details.
        """
        loan_details = obj.get_loan_details()
        return {
            'tuition_amount': loan_details.tuition_amount,
            'deposit_amount': loan_details.deposit_amount,
            'other_funding': loan_details.other_funding,
            'requested_amount': loan_details.requested_amount,
        }

    def get_school_program_details(self, obj: LoanApplication) -> dict:
        """
        Gets details about the school and program.

        Args:
            obj (LoanApplication): The LoanApplication instance.

        Returns:
            dict: Dictionary with school and program details.
        """
        school = obj.school
        program = obj.program
        program_version = obj.program_version

        return {
            'school_name': school.name,
            'school_contact': school.phone,
            'program_name': program.name,
            'program_duration': program.duration_weeks,
            'program_cost': program_version.tuition_amount,
        }

    def get_documents(self, obj: LoanApplication) -> list:
        """
        Gets documents associated with the application.

        Args:
            obj (LoanApplication): The LoanApplication instance.

        Returns:
            list: List of document dictionaries.
        """
        documents = obj.get_documents()
        return [
            {'type': doc.document_type, 'name': doc.file_name, 'upload_date': doc.uploaded_at, 'status': doc.status}
            for doc in documents
        ]

    def get_credit_information(self, obj: LoanApplication) -> dict:
        """
        Gets credit information for borrower and co-borrower.

        Args:
            obj (LoanApplication): The LoanApplication instance.

        Returns:
            dict: Dictionary with borrower and co-borrower credit information.
        """
        borrower_credit_info = CreditInformation.objects.filter(application=obj, borrower=obj.borrower).first()
        borrower_credit_data = CreditInformationSerializer(borrower_credit_info).data if borrower_credit_info else None

        co_borrower = obj.co_borrower
        co_borrower_credit_info = None
        if co_borrower:
            co_borrower_credit_info = CreditInformation.objects.filter(application=obj, borrower=co_borrower).first()
        co_borrower_credit_data = CreditInformationSerializer(co_borrower_credit_info).data if co_borrower_credit_info else None

        return {
            'borrower': borrower_credit_data,
            'co_borrower': co_borrower_credit_data,
        }

    def get_status_history(self, obj: LoanApplication) -> list:
        """
        Gets the status change history for the application.

        Args:
            obj (LoanApplication): The LoanApplication instance.

        Returns:
            list: List of status change dictionaries.
        """
        status_history = obj.get_status_history()
        return [
            {'previous_status': history.previous_status, 'new_status': history.new_status,
             'timestamp': history.changed_at, 'user': str(history.changed_by)}
            for history in status_history
        ]


class UnderwritingDecisionCreateSerializer(BaseModelSerializer):
    """
    Serializer for creating underwriting decisions.
    """
    reason_codes = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = UnderwritingDecision
        fields = ['application', 'decision', 'comments', 'approved_amount', 'interest_rate', 'term_months', 'reason_codes']

    def validate(self, data: dict) -> dict:
        """
        Validates the decision data based on decision type.

        Args:
            data (dict): The data to validate.

        Returns:
            dict: Validated data.
        """
        decision = data.get('decision')

        if decision == UNDERWRITING_DECISION['APPROVE']:
            if not all([data.get('approved_amount'), data.get('interest_rate'), data.get('term_months')]):
                raise ValidationError("Approved amount, interest rate, and term months are required for approval.")

            if data['approved_amount'] <= Decimal('0'):
                raise ValidationError("Approved amount must be positive.")

            application = data.get('application')
            if data['approved_amount'] > application.get_loan_details().requested_amount:
                 raise ValidationError("Approved amount cannot exceed requested amount.")

            # Additional validation for interest_rate and term_months can be added here
        elif decision == UNDERWRITING_DECISION['DENY']:
            if not data.get('reason_codes'):
                raise ValidationError("At least one reason code is required for denial.")
        elif decision == UNDERWRITING_DECISION['REVISE']:
            if not data.get('comments'):
                raise ValidationError("Comments are required when requesting a revision.")

        return data

    def create(self, validated_data: dict) -> UnderwritingDecision:
        """
        Creates an underwriting decision using the service layer.

        Args:
            validated_data (dict): Validated data for creating the decision.

        Returns:
            UnderwritingDecision: The created decision object.
        """
        application = validated_data.pop('application')
        decision = validated_data.pop('decision')
        comments = validated_data.pop('comments', '')
        approved_amount = validated_data.pop('approved_amount', None)
        interest_rate = validated_data.pop('interest_rate', None)
        term_months = validated_data.pop('term_months', None)
        reason_codes = validated_data.pop('reason_codes', [])

        request = self.context.get('request')
        user = request.user if request else None

        decision_obj = create_underwriting_decision(
            application=application,
            decision=decision,
            comments=comments,
            approved_amount=approved_amount,
            interest_rate=interest_rate,
            term_months=term_months,
            reason_codes=reason_codes,
            user=user
        )
        return decision_obj


class StipulationCreateSerializer(BaseModelSerializer):
    """
    Serializer for creating stipulations.
    """
    class Meta:
        model = Stipulation
        fields = ['application', 'stipulation_type', 'description', 'required_by_date']

    def validate(self, data: dict) -> dict:
        """
        Validates the stipulation data.

        Args:
            data (dict): The data to validate.

        Returns:
            dict: Validated data.
        """
        if data['stipulation_type'] not in dict(STIPULATION_TYPE_CHOICES):
            raise ValidationError("Invalid stipulation type.")

        if data['required_by_date'] <= timezone.now().date():
            raise ValidationError("Required by date must be in the future.")

        if not data['description']:
            raise ValidationError("Description is required.")

        return data

    def create(self, validated_data: dict) -> Stipulation:
        """
        Creates a stipulation using the service layer.

        Args:
            validated_data (dict): Validated data for creating the stipulation.

        Returns:
            Stipulation: The created stipulation object.
        """
        application = validated_data.pop('application')
        stipulation_type = validated_data.pop('stipulation_type')
        description = validated_data.pop('description')
        required_by_date = validated_data.pop('required_by_date')

        request = self.context.get('request')
        user = request.user if request else None

        stipulation_obj = create_stipulation(
            application=application,
            stipulation_type=stipulation_type,
            description=description,
            required_by_date=required_by_date,
            user=user
        )
        return stipulation_obj


class StipulationUpdateSerializer(BaseModelSerializer):
    """
    Serializer for updating stipulation status.
    """
    class Meta:
        model = Stipulation
        fields = ['status']

    def validate_status(self, value: str) -> str:
        """
        Validates the stipulation status.

        Args:
            value (str): The status to validate.

        Returns:
            str: Validated status.
        """
        if value not in dict(STIPULATION_STATUS_CHOICES):
            raise ValidationError("Invalid status.")
        return value

    def update(self, instance: Stipulation, validated_data: dict) -> Stipulation:
        """
        Updates a stipulation's status using the service layer.

        Args:
            instance (Stipulation): The Stipulation instance to update.
            validated_data (dict): Validated data for updating the stipulation.

        Returns:
            Stipulation: The updated stipulation object.
        """
        status = validated_data.pop('status')

        request = self.context.get('request')
        user = request.user if request else None

        stipulation_obj = update_stipulation_status(
            instance=instance,
            status=status,
            user=user
        )
        return stipulation_obj


class UnderwritingNoteCreateSerializer(BaseModelSerializer):
    """
    Serializer for creating underwriting notes.
    """
    class Meta:
        model = UnderwritingNote
        fields = ['application', 'note_text', 'is_internal']

    def validate(self, data: dict) -> dict:
        """
        Validates the note data.

        Args:
            data (dict): The data to validate.

        Returns:
            dict: Validated data.
        """
        if not data.get('note_text'):
            raise ValidationError("Note text is required.")

        return data

    def create(self, validated_data: dict) -> UnderwritingNote:
        """
        Creates an underwriting note using the service layer.

        Args:
            validated_data (dict): Validated data for creating the note.

        Returns:
            UnderwritingNote: The created note object.
        """
        application = validated_data.pop('application')
        note_text = validated_data.pop('note_text')
        is_internal = validated_data.pop('is_internal', True)

        request = self.context.get('request')
        user = request.user if request else None

        note_obj = create_underwriting_note(
            application=application,
            note_text=note_text,
            is_internal=is_internal,
            user=user
        )
        return note_obj


class CreditInformationUploadSerializer(BaseModelSerializer):
    """
    Serializer for uploading credit information.
    """
    credit_file = serializers.FileField(required=True)

    class Meta:
        model = CreditInformation
        fields = ['application', 'borrower', 'is_co_borrower', 'credit_score', 'report_reference', 'credit_file', 'monthly_debt']

    def validate(self, data: dict) -> dict:
        """
        Validates the credit information data.

        Args:
            data (dict): The data to validate.

        Returns:
            dict: Validated data.
        """
        if not 300 <= data.get('credit_score', 0) <= 850:
            raise ValidationError("Credit score must be between 300 and 850.")
        
        if data.get('monthly_debt', 0) < 0:
            raise ValidationError("Monthly debt must be a non-negative number.")

        return data

    def create(self, validated_data: dict) -> CreditInformation:
        """
        Creates or updates credit information using the service layer.

        Args:
            validated_data (dict): Validated data for creating or updating the credit information.

        Returns:
            CreditInformation: The created or updated credit information object.
        """
        application = validated_data.pop('application')
        borrower = validated_data.pop('borrower')
        is_co_borrower = validated_data.pop('is_co_borrower')
        credit_score = validated_data.pop('credit_score')
        report_reference = validated_data.pop('report_reference')
        credit_file = validated_data.pop('credit_file')
        monthly_debt = validated_data.pop('monthly_debt')

        request = self.context.get('request')
        user = request.user if request else None

        # upload_credit_information function is not defined in the provided files
        # Assuming it exists and handles the file upload and credit information creation/update
        # credit_info_obj = upload_credit_information(
        #     application=application,
        #     borrower=borrower,
        #     is_co_borrower=is_co_borrower,
        #     credit_score=credit_score,
        #     report_reference=report_reference,
        #     credit_file=credit_file,
        #     monthly_debt=monthly_debt,
        #     user=user
        # )
        # return credit_info_obj
        raise NotImplementedError("upload_credit_information service function is not implemented")