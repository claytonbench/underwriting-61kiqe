"""
Defines serializers for the loan application module, handling the conversion of application models to and from JSON representations for API interactions. These serializers include validation logic, field transformations, and nested relationships for comprehensive loan application processing.
"""

from rest_framework import serializers  # version 3.14+
from rest_framework.exceptions import ValidationError  # version 3.14+
from django.db import transaction  # version 4.2+

from core.serializers import BaseModelSerializer, SensitiveDataMixin, ReadOnlyModelSerializer
from apps.users.serializers import BorrowerProfileSerializer, EmploymentInfoSerializer
from apps.schools.serializers import SchoolSerializer, ProgramSerializer
from .models import (
    LoanApplication, LoanDetails, ApplicationDocument, ApplicationStatusHistory, ApplicationNote
)
from .constants import (
    APPLICATION_STATUS, APPLICATION_TYPES, RELATIONSHIP_TYPES,
    APPLICATION_EDITABLE_STATUSES, APPLICATION_FORM_STEPS, DOCUMENT_REQUIREMENTS
)
from .validators import (
    validate_application_editable, validate_application_submission,
    validate_loan_details, validate_borrower_info
)

# Define choice tuples for serializer fields
APPLICATION_TYPE_CHOICES = ([(APPLICATION_TYPES['STANDARD'], 'Standard'),
                            (APPLICATION_TYPES['REFINANCE'], 'Refinance'),
                            (APPLICATION_TYPES['COSIGNED'], 'Co-signed')])

RELATIONSHIP_TYPE_CHOICES = ([(RELATIONSHIP_TYPES['SPOUSE'], 'Spouse'),
                             (RELATIONSHIP_TYPES['PARENT'], 'Parent'),
                             (RELATIONSHIP_TYPES['SIBLING'], 'Sibling'),
                             (RELATIONSHIP_TYPES['RELATIVE'], 'Relative'),
                             (RELATIONSHIP_TYPES['FRIEND'], 'Friend'),
                             (RELATIONSHIP_TYPES['OTHER'], 'Other')])

APPLICATION_STATUS_CHOICES = ([status for status in APPLICATION_STATUS.items()])


class LoanApplicationSerializer(BaseModelSerializer):
    """
    Basic serializer for LoanApplication model with minimal fields
    """
    id = serializers.UUIDField(read_only=True)
    application_type = serializers.CharField(source='get_application_type_display', read_only=True)
    status = serializers.CharField(source='get_status_display', read_only=True)
    submission_date = serializers.DateTimeField(read_only=True)
    borrower = serializers.PrimaryKeyRelatedField(read_only=True)
    co_borrower = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    school = serializers.PrimaryKeyRelatedField(read_only=True)
    program = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = LoanApplication
        fields = [
            'id', 'application_type', 'status', 'submission_date',
            'borrower', 'co_borrower', 'school', 'program'
        ]

    def get_status_display(self, obj):
        """
        Returns the human-readable status display name

        Args:
            obj (LoanApplication): The LoanApplication instance

        Returns:
            str: Human-readable status name
        """
        return obj.get_status_display()

    def get_application_type_display(self, obj):
        """
        Returns the human-readable application type display name

        Args:
            obj (LoanApplication): The LoanApplication instance

        Returns:
            str: Human-readable application type name
        """
        return obj.get_application_type_display()

    def get_is_editable(self, obj):
        """
        Returns whether the application is in an editable state

        Args:
            obj (LoanApplication): The LoanApplication instance

        Returns:
            bool: True if application is editable, False otherwise
        """
        return obj.is_editable()


class LoanApplicationDetailSerializer(LoanApplicationSerializer):
    """
    Detailed serializer for LoanApplication model with related information
    """

    class Meta(LoanApplicationSerializer.Meta):
        fields = LoanApplicationSerializer.Meta.fields + [
            'loan_details', 'documents', 'status_history', 'notes'
        ]
        read_only_fields = LoanApplicationSerializer.Meta.fields + [
            'loan_details', 'documents', 'status_history', 'notes'
        ]

    def to_representation(self, instance):
        """
        Customizes the representation to include related data

        Args:
            instance (LoanApplication): The LoanApplication instance

        Returns:
            dict: Serialized application data with related information
        """
        representation = super().to_representation(instance)
        representation['borrower_profile'] = BorrowerProfileSerializer(instance.borrower.borrowerprofile).data
        if instance.co_borrower:
            representation['co_borrower_profile'] = BorrowerProfileSerializer(instance.co_borrower.borrowerprofile).data
        representation['school'] = SchoolSerializer(instance.school).data
        representation['program'] = ProgramSerializer(instance.program).data
        representation['loan_details'] = self.get_loan_details(instance)
        representation['documents'] = self.get_documents(instance)
        representation['status_history'] = self.get_status_history(instance)
        representation['notes'] = self.get_notes(instance)
        return representation

    def get_loan_details(self, obj):
        """
        Returns serialized loan details for the application

        Args:
            obj (LoanApplication): The LoanApplication instance

        Returns:
            dict: Serialized loan details data
        """
        loan_details = obj.get_loan_details()
        return LoanDetailsSerializer(loan_details).data if loan_details else None

    def get_documents(self, obj):
        """
        Returns serialized documents for the application

        Args:
            obj (LoanApplication): The LoanApplication instance

        Returns:
            list: List of serialized document data
        """
        documents = obj.get_documents()
        return ApplicationDocumentSerializer(documents, many=True).data

    def get_status_history(self, obj):
        """
        Returns serialized status history for the application

        Args:
            obj (LoanApplication): The LoanApplication instance

        Returns:
            list: List of serialized status history data
        """
        status_history = obj.get_status_history()
        return ApplicationStatusHistorySerializer(status_history, many=True).data

    def get_notes(self, obj):
        """
        Returns serialized notes for the application

        Args:
            obj (LoanApplication): The LoanApplication instance

        Returns:
            list: List of serialized note data
        """
        # TODO: Implement permission-based filtering of notes (internal vs. external)
        notes = obj.notes.all()
        return ApplicationNoteSerializer(notes, many=True).data


class LoanApplicationCreateSerializer(BaseModelSerializer):
    """
    Serializer for creating new LoanApplication instances
    """
    application_type = serializers.ChoiceField(choices=APPLICATION_TYPE_CHOICES, required=True)
    borrower = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    co_borrower = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    relationship_type = serializers.ChoiceField(choices=RELATIONSHIP_TYPE_CHOICES, required=False, allow_null=True)
    school = serializers.PrimaryKeyRelatedField(queryset=School.objects.all(), required=True)
    program = serializers.PrimaryKeyRelatedField(queryset=Program.objects.all(), required=True)
    borrower_info = serializers.JSONField(required=True)
    co_borrower_info = serializers.JSONField(required=False, allow_null=True)
    loan_details = serializers.JSONField(required=True)

    class Meta:
        model = LoanApplication
        fields = [
            'application_type', 'borrower', 'co_borrower', 'relationship_type',
            'school', 'program', 'borrower_info', 'co_borrower_info', 'loan_details'
        ]

    def validate(self, data):
        """
        Validates the application creation data

        Args:
            data (dict): The data to validate

        Returns:
            dict: Validated data
        """
        # Validate relationship type is valid
        if data.get('co_borrower') and not data.get('relationship_type'):
            raise ValidationError("Relationship type is required when a co-borrower is specified.")

        # Validate borrower information
        try:
            validate_borrower_info(data.get('borrower_info'))
        except ValidationError as e:
            raise ValidationError({'borrower_info': str(e)})

        # Validate co-borrower information if provided
        if data.get('co_borrower_info'):
            try:
                # TODO: Implement co-borrower info validation
                pass
            except ValidationError as e:
                raise ValidationError({'co_borrower_info': str(e)})

        # Validate loan details
        try:
            validate_loan_details(data.get('loan_details'))
        except ValidationError as e:
            raise ValidationError({'loan_details': str(e)})

        return data

    def create(self, validated_data):
        """
        Creates a new loan application with related data

        Args:
            validated_data (dict): The validated data

        Returns:
            LoanApplication: Created application instance
        """
        borrower_info = validated_data.pop('borrower_info', {})
        co_borrower_info = validated_data.pop('co_borrower_info', {})
        loan_details = validated_data.pop('loan_details', {})

        with transaction.atomic():
            application = LoanApplication.objects.create(**validated_data)

            # TODO: Create or update BorrowerProfile with borrower_info
            # TODO: Create or update co-borrower profile if co_borrower_info provided
            # TODO: Create LoanDetails with loan_details

        return application


class LoanApplicationUpdateSerializer(BaseModelSerializer):
    """
    Serializer for updating existing LoanApplication instances
    """
    application_type = serializers.ChoiceField(choices=APPLICATION_TYPE_CHOICES, required=False)
    co_borrower = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    relationship_type = serializers.ChoiceField(choices=RELATIONSHIP_TYPE_CHOICES, required=False, allow_null=True)
    borrower_info = serializers.JSONField(required=False)
    co_borrower_info = serializers.JSONField(required=False, allow_null=True)
    loan_details = serializers.JSONField(required=False)

    class Meta:
        model = LoanApplication
        fields = [
            'application_type', 'co_borrower', 'relationship_type',
            'borrower_info', 'co_borrower_info', 'loan_details'
        ]

    def validate(self, data):
        """
        Validates the application update data

        Args:
            data (dict): The data to validate

        Returns:
            dict: Validated data
        """
        application = self.context.get('application')
        if not application:
            raise ValidationError("Application instance is required in context.")

        # Validate application is in an editable state
        validate_application_editable(application)

        # Validate relationship type is valid
        if data.get('co_borrower') and not data.get('relationship_type'):
            raise ValidationError("Relationship type is required when a co-borrower is specified.")

        # Validate borrower information
        if data.get('borrower_info'):
            try:
                # TODO: Implement borrower info validation
                pass
            except ValidationError as e:
                raise ValidationError({'borrower_info': str(e)})

        # Validate co-borrower information if provided
        if data.get('co_borrower_info'):
            try:
                # TODO: Implement co-borrower info validation
                pass
            except ValidationError as e:
                raise ValidationError({'co_borrower_info': str(e)})

        # Validate loan details
        if data.get('loan_details'):
            try:
                validate_loan_details(data.get('loan_details'))
            except ValidationError as e:
                raise ValidationError({'loan_details': str(e)})

        return data

    def update(self, instance, validated_data):
        """
        Updates an existing loan application with related data

        Args:
            instance (LoanApplication): The application instance to update
            validated_data (dict): The validated data

        Returns:
            LoanApplication: Updated application instance
        """
        borrower_info = validated_data.pop('borrower_info', None)
        co_borrower_info = validated_data.pop('co_borrower_info', None)
        loan_details = validated_data.pop('loan_details', None)

        with transaction.atomic():
            # Update the LoanApplication instance with remaining validated_data
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # TODO: Update BorrowerProfile with borrower_info if provided
            # TODO: Update co-borrower profile with co_borrower_info if provided
            # TODO: Update LoanDetails with loan_details if provided

        return instance


class LoanApplicationSubmitSerializer(BaseModelSerializer):
    """
    Serializer for submitting a loan application for review
    """

    class Meta:
        model = LoanApplication
        fields = []  # No fields to update directly

    def validate(self, data):
        """
        Validates the application submission

        Args:
            data (dict): The data to validate

        Returns:
            dict: Validated data
        """
        application = self.context.get('application')
        if not application:
            raise ValidationError("Application instance is required in context.")

        # Validate application is in an editable state
        validate_application_editable(application)

        return data

    def update(self, instance, validated_data):
        """
        Submits the application for review

        Args:
            instance (LoanApplication): The application instance to update
            validated_data (dict): The validated data

        Returns:
            LoanApplication: Submitted application instance
        """
        instance.submit()
        return instance


class LoanDetailsSerializer(BaseModelSerializer):
    """
    Serializer for LoanDetails model
    """
    id = serializers.UUIDField(read_only=True)
    tuition_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    other_funding = serializers.DecimalField(max_digits=10, decimal_places=2)
    requested_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    approved_amount = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    start_date = serializers.DateField()
    completion_date = serializers.DateField(allow_null=True)

    class Meta:
        model = LoanDetails
        fields = [
            'id', 'tuition_amount', 'deposit_amount', 'other_funding',
            'requested_amount', 'approved_amount', 'start_date', 'completion_date'
        ]

    def get_net_tuition(self, obj):
        """
        Calculates the net tuition after deposit and other funding

        Args:
            obj (LoanDetails): The LoanDetails instance

        Returns:
            Decimal: Net tuition amount
        """
        return obj.get_net_tuition()

    def validate(self, data):
        """
        Validates the loan details data

        Args:
            data (dict): The data to validate

        Returns:
            dict: Validated data
        """
        # TODO: Implement loan details validation
        return data


class ApplicationDocumentSerializer(BaseModelSerializer):
    """
    Serializer for ApplicationDocument model
    """
    id = serializers.UUIDField(read_only=True)
    document_type = serializers.CharField(source='get_document_type_display', read_only=True)
    file_name = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    uploaded_at = serializers.DateTimeField(read_only=True)
    uploaded_by = serializers.CharField(source='get_uploaded_by_name', read_only=True)
    download_url = serializers.CharField(source='get_download_url', read_only=True)

    class Meta:
        model = ApplicationDocument
        fields = [
            'id', 'document_type', 'file_name', 'file_path',
            'status', 'uploaded_at', 'uploaded_by', 'download_url'
        ]

    def get_download_url(self, obj):
        """
        Generates a download URL for the document

        Args:
            obj (ApplicationDocument): The ApplicationDocument instance

        Returns:
            str: Presigned download URL
        """
        return obj.get_download_url()

    def get_document_type_display(self, obj):
        """
        Returns the human-readable document type display name

        Args:
            obj (ApplicationDocument): The ApplicationDocument instance

        Returns:
            str: Human-readable document type name
        """
        return obj.get_document_type_display()

    def get_uploaded_by_name(self, obj):
        """
        Returns the name of the user who uploaded the document

        Args:
            obj (ApplicationDocument): The ApplicationDocument instance

        Returns:
            str: Uploader's full name
        """
        if obj.uploaded_by:
            return obj.uploaded_by.get_full_name()
        return None


class ApplicationDocumentCreateSerializer(BaseModelSerializer):
    """
    Serializer for creating new ApplicationDocument instances
    """
    application = serializers.PrimaryKeyRelatedField(queryset=LoanApplication.objects.all(), required=True)
    document_type = serializers.ChoiceField(choices=DOCUMENT_TYPE_CHOICES, required=True)
    file = serializers.FileField(required=True)

    class Meta:
        model = ApplicationDocument
        fields = ['application', 'document_type', 'file']

    def validate(self, data):
        """
        Validates the document creation data

        Args:
            data (dict): The data to validate

        Returns:
            dict: Validated data
        """
        # TODO: Implement document creation validation
        return data

    def create(self, validated_data):
        """
        Creates a new application document

        Args:
            validated_data (dict): The validated data

        Returns:
            ApplicationDocument: Created document instance
        """
        # TODO: Implement document creation logic
        return ApplicationDocument.objects.create(**validated_data)


class ApplicationStatusHistorySerializer(BaseModelSerializer):
    """
    Serializer for ApplicationStatusHistory model
    """
    id = serializers.UUIDField(read_only=True)
    previous_status = serializers.CharField(source='get_previous_status_display', read_only=True)
    new_status = serializers.CharField(source='get_new_status_display', read_only=True)
    changed_at = serializers.DateTimeField(read_only=True)
    changed_by = serializers.CharField(source='get_changed_by_name', read_only=True)
    comments = serializers.CharField(read_only=True)

    class Meta:
        model = ApplicationStatusHistory
        fields = [
            'id', 'previous_status', 'new_status', 'changed_at', 'changed_by', 'comments'
        ]

    def get_previous_status_display(self, obj):
        """
        Returns the human-readable previous status display name

        Args:
            obj (ApplicationStatusHistory): The ApplicationStatusHistory instance

        Returns:
            str: Human-readable previous status name
        """
        return obj.get_previous_status_display()

    def get_new_status_display(self, obj):
        """
        Returns the human-readable new status display name

        Args:
            obj (ApplicationStatusHistory): The ApplicationStatusHistory instance

        Returns:
            str: Human-readable new status name
        """
        return obj.get_new_status_display()

    def get_changed_by_name(self, obj):
        """
        Returns the name of the user who changed the status

        Args:
            obj (ApplicationStatusHistory): The ApplicationStatusHistory instance

        Returns:
            str: User's full name
        """
        if obj.changed_by:
            return obj.changed_by.get_full_name()
        return None


class ApplicationNoteSerializer(BaseModelSerializer):
    """
    Serializer for ApplicationNote model
    """
    id = serializers.UUIDField(read_only=True)
    application = serializers.PrimaryKeyRelatedField(queryset=LoanApplication.objects.all(), required=True)
    note_text = serializers.CharField(required=True)
    created_at = serializers.DateTimeField(read_only=True)
    created_by = serializers.CharField(source='get_created_by_name', read_only=True)
    is_internal = serializers.BooleanField(default=True)

    class Meta:
        model = ApplicationNote
        fields = [
            'id', 'application', 'note_text', 'created_at', 'created_by', 'is_internal'
        ]

    def get_created_by_name(self, obj):
        """
        Returns the name of the user who created the note

        Args:
            obj (ApplicationNote): The ApplicationNote instance

        Returns:
            str: User's full name
        """
        if obj.created_by:
            return obj.created_by.get_full_name()
        return None

    def validate(self, data):
        """
        Validates the note creation data

        Args:
            data (dict): The data to validate

        Returns:
            dict: Validated data
        """
        if not data.get('note_text'):
            raise ValidationError("Note text cannot be empty.")
        return data


class ApplicationFormStepSerializer(serializers.Serializer):
    """
    Serializer for tracking application form completion steps
    """
    step = serializers.CharField()
    completed = serializers.BooleanField()
    current = serializers.BooleanField()
    enabled = serializers.BooleanField()


class ApplicationFormProgressSerializer(serializers.Serializer):
    """
    Serializer for tracking overall application form progress
    """
    application = serializers.PrimaryKeyRelatedField(queryset=LoanApplication.objects.all())
    steps = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()
    current_step = serializers.SerializerMethodField()

    def get_steps(self, obj):
        """
        Returns the serialized form steps with completion status

        Args:
            obj (dict): The object containing application data

        Returns:
            list: List of serialized form steps
        """
        # TODO: Implement logic to determine completed steps based on application data
        # For now, return a static list
        steps = []
        for step in APPLICATION_FORM_STEPS:
            steps.append({
                'step': step,
                'completed': False,
                'current': False,
                'enabled': True
            })
        return ApplicationFormStepSerializer(steps, many=True).data

    def get_completion_percentage(self, obj):
        """
        Calculates the overall form completion percentage

        Args:
            obj (dict): The object containing application data

        Returns:
            int: Completion percentage (0-100)
        """
        # TODO: Implement logic to calculate completion percentage
        return 0

    def get_current_step(self, obj):
        """
        Determines the current active step in the form process

        Args:
            obj (dict): The object containing application data

        Returns:
            str: Current step identifier
        """
        # TODO: Implement logic to determine current step
        return APPLICATION_FORM_STEPS[0]

# Exported constants for use in other modules
APPLICATION_TYPE_CHOICES = ([(APPLICATION_TYPES['STANDARD'], 'Standard'),
                            (APPLICATION_TYPES['REFINANCE'], 'Refinance'),
                            (APPLICATION_TYPES['COSIGNED'], 'Co-signed')])

RELATIONSHIP_TYPE_CHOICES = ([(RELATIONSHIP_TYPES['SPOUSE'], 'Spouse'),
                             (RELATIONSHIP_TYPES['PARENT'], 'Parent'),
                             (RELATIONSHIP_TYPES['SIBLING'], 'Sibling'),
                             (RELATIONSHIP_TYPES['RELATIVE'], 'Relative'),
                             (RELATIONSHIP_TYPES['FRIEND'], 'Friend'),
                             (RELATIONSHIP_TYPES['OTHER'], 'Other')])

APPLICATION_STATUS_CHOICES = ([status for status in APPLICATION_STATUS.items()])