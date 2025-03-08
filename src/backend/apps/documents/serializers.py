"""
Defines serializers for the document management system, providing data validation, transformation, and serialization for document-related models. These serializers support API endpoints for document templates, document packages, individual documents, signature requests, and document fields.
"""

from rest_framework import serializers  # version 3.14+
from rest_framework.exceptions import ValidationError  # version 3.14+

from core.serializers import BaseModelSerializer, ReadOnlyModelSerializer, AuditFieldsMixin  # Internal import
from .models import (  # Internal import
    DocumentTemplate, DocumentPackage, Document, SignatureRequest, DocumentField,
    DOCUMENT_TYPE_CHOICES, DOCUMENT_STATUS_CHOICES, DOCUMENT_PACKAGE_TYPE_CHOICES,
    SIGNATURE_STATUS_CHOICES, SIGNER_TYPE_CHOICES, DOCUMENT_FIELD_TYPE_CHOICES
)
from apps.applications.models import LoanApplication  # Internal import
from apps.users.models import User, UserSerializer  # Internal import


class DocumentTemplateSerializer(BaseModelSerializer):
    """
    Serializer for document templates
    """
    name = serializers.CharField()
    description = serializers.CharField()
    document_type = serializers.ChoiceField(choices=DOCUMENT_TYPE_CHOICES)
    file_path = serializers.CharField()
    version = serializers.CharField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def get_fields(self):
        """
        Override get_fields to make certain fields read-only

        Returns:
            dict: Dictionary of serializer fields
        """
        fields = super().get_fields()
        fields['created_at'].read_only = True
        fields['created_by'].read_only = True
        return fields

    def validate_document_type(self, value):
        """
        Validate that document_type is a valid choice

        Args:
            value (str): The document_type value to validate

        Returns:
            str: Validated document_type value
        """
        if value not in dict(DOCUMENT_TYPE_CHOICES):
            raise ValidationError("Invalid document type")
        return value

    class Meta:
        """
        Meta class for DocumentTemplateSerializer
        """
        model = DocumentTemplate
        fields = ['id', 'name', 'description', 'document_type', 'file_path', 'version', 'is_active', 'created_at', 'created_by']
        read_only_fields = ['id']


class DocumentPackageSerializer(BaseModelSerializer):
    """
    Serializer for document packages
    """
    application = serializers.PrimaryKeyRelatedField(queryset=LoanApplication.objects.all())
    package_type = serializers.ChoiceField(choices=DOCUMENT_PACKAGE_TYPE_CHOICES)
    status = serializers.ChoiceField(choices=DOCUMENT_STATUS_CHOICES)
    created_at = serializers.DateTimeField()
    expiration_date = serializers.DateTimeField()

    def get_fields(self):
        """
        Override get_fields to make certain fields read-only

        Returns:
            dict: Dictionary of serializer fields
        """
        fields = super().get_fields()
        fields['created_at'].read_only = True
        fields['expiration_date'].read_only = True
        return fields

    def to_representation(self, instance):
        """
        Override to_representation to include documents in the package

        Args:
            instance (DocumentPackage): The DocumentPackage instance

        Returns:
            dict: Serialized data with documents included
        """
        representation = super().to_representation(instance)
        documents = instance.get_documents()
        document_serializer = DocumentSerializer(documents, many=True, read_only=True)
        representation['documents'] = document_serializer.data
        return representation

    def validate_package_type(self, value):
        """
        Validate that package_type is a valid choice

        Args:
            value (str): The package_type value to validate

        Returns:
            str: Validated package_type value
        """
        if value not in dict(DOCUMENT_PACKAGE_TYPE_CHOICES):
            raise ValidationError("Invalid package type")
        return value

    def validate_status(self, value):
        """
        Validate that status is a valid choice

        Args:
            value (str): The status value to validate

        Returns:
            str: Validated status value
        """
        if value not in dict(DOCUMENT_STATUS_CHOICES):
            raise ValidationError("Invalid status")
        return value

    class Meta:
        """
        Meta class for DocumentPackageSerializer
        """
        model = DocumentPackage
        fields = ['id', 'application', 'package_type', 'status', 'created_at', 'expiration_date']
        read_only_fields = ['id']


class DocumentPackageCreateSerializer(serializers.Serializer):
    """
    Serializer for creating document packages
    """
    application_id = serializers.UUIDField()
    package_type = serializers.ChoiceField(choices=DOCUMENT_PACKAGE_TYPE_CHOICES)

    def validate_application_id(self, value):
        """
        Validate that application_id refers to an existing application

        Args:
            value (uuid.UUID): The application_id value to validate

        Returns:
            uuid.UUID: Validated application_id value
        """
        try:
            LoanApplication.objects.get(pk=value)
        except LoanApplication.DoesNotExist:
            raise ValidationError("Invalid application ID")
        return value

    def validate_package_type(self, value):
        """
        Validate that package_type is a valid choice

        Args:
            value (str): The package_type value to validate

        Returns:
            str: Validated package_type value
        """
        if value not in dict(DOCUMENT_PACKAGE_TYPE_CHOICES):
            raise ValidationError("Invalid package type")
        return value


class DocumentSerializer(BaseModelSerializer):
    """
    Serializer for documents
    """
    package = serializers.PrimaryKeyRelatedField(queryset=DocumentPackage.objects.all())
    document_type = serializers.ChoiceField(choices=DOCUMENT_TYPE_CHOICES)
    file_name = serializers.CharField()
    file_path = serializers.CharField()
    version = serializers.CharField()
    status = serializers.ChoiceField(choices=DOCUMENT_STATUS_CHOICES)
    generated_at = serializers.DateTimeField()
    generated_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def get_fields(self):
        """
        Override get_fields to make certain fields read-only

        Returns:
            dict: Dictionary of serializer fields
        """
        fields = super().get_fields()
        fields['generated_at'].read_only = True
        fields['generated_by'].read_only = True
        return fields

    def validate_document_type(self, value):
        """
        Validate that document_type is a valid choice

        Args:
            value (str): The document_type value to validate

        Returns:
            str: Validated document_type value
        """
        if value not in dict(DOCUMENT_TYPE_CHOICES):
            raise ValidationError("Invalid document type")
        return value

    def validate_status(self, value):
        """
        Validate that status is a valid choice

        Args:
            value (str): The status value to validate

        Returns:
            str: Validated status value
        """
        if value not in dict(DOCUMENT_STATUS_CHOICES):
            raise ValidationError("Invalid status")
        return value

    class Meta:
        """
        Meta class for DocumentSerializer
        """
        model = Document
        fields = ['id', 'package', 'document_type', 'file_name', 'file_path', 'version', 'status', 'generated_at', 'generated_by']
        read_only_fields = ['id']


class DocumentDetailSerializer(DocumentSerializer):
    """
    Detailed serializer for documents including signature requests and fields
    """
    def to_representation(self, instance):
        """
        Override to_representation to include signature requests and fields

        Args:
            instance (Document): The Document instance

        Returns:
            dict: Serialized data with signature requests and fields included
        """
        representation = super().to_representation(instance)
        signature_requests = instance.get_signature_requests()
        signature_request_serializer = SignatureRequestSerializer(signature_requests, many=True, read_only=True)
        representation['signature_requests'] = signature_request_serializer.data

        document_fields = instance.get_fields()
        document_field_serializer = DocumentFieldSerializer(document_fields, many=True, read_only=True)
        representation['document_fields'] = document_field_serializer.data
        return representation

    class Meta:
        """
        Meta class for DocumentDetailSerializer
        """
        model = Document
        fields = DocumentSerializer.Meta.fields
        read_only_fields = DocumentSerializer.Meta.read_only_fields


class DocumentUploadSerializer(serializers.Serializer):
    """
    Serializer for document uploads
    """
    file = serializers.FileField()
    document_type = serializers.ChoiceField(choices=DOCUMENT_TYPE_CHOICES)
    application_id = serializers.UUIDField()

    def validate_file(self, value):
        """
        Validate that the file is of an allowed type and size

        Args:
            value (File): The file value to validate

        Returns:
            File: Validated file value
        """
        # Implement file type and size validation here
        return value

    def validate_document_type(self, value):
        """
        Validate that document_type is a valid choice

        Args:
            value (str): The document_type value to validate

        Returns:
            str: Validated document_type value
        """
        if value not in dict(DOCUMENT_TYPE_CHOICES):
            raise ValidationError("Invalid document type")
        return value

    def validate_application_id(self, value):
        """
        Validate that application_id refers to an existing application

        Args:
            value (uuid.UUID): The application_id value to validate

        Returns:
            uuid.UUID: Validated application_id value
        """
        try:
            LoanApplication.objects.get(pk=value)
        except LoanApplication.DoesNotExist:
            raise ValidationError("Invalid application ID")
        return value


class SignatureRequestSerializer(BaseModelSerializer):
    """
    Serializer for signature requests
    """
    document = serializers.PrimaryKeyRelatedField(queryset=Document.objects.all())
    signer = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    signer_type = serializers.ChoiceField(choices=SIGNER_TYPE_CHOICES)
    status = serializers.ChoiceField(choices=SIGNATURE_STATUS_CHOICES)
    requested_at = serializers.DateTimeField()
    completed_at = serializers.DateTimeField()
    reminder_count = serializers.IntegerField()
    last_reminder_at = serializers.DateTimeField()
    external_reference = serializers.CharField()

    def get_fields(self):
        """
        Override get_fields to make certain fields read-only

        Returns:
            dict: Dictionary of serializer fields
        """
        fields = super().get_fields()
        fields['requested_at'].read_only = True
        fields['completed_at'].read_only = True
        fields['reminder_count'].read_only = True
        fields['last_reminder_at'].read_only = True
        return fields

    def validate_signer_type(self, value):
        """
        Validate that signer_type is a valid choice

        Args:
            value (str): The signer_type value to validate

        Returns:
            str: Validated signer_type value
        """
        if value not in dict(SIGNER_TYPE_CHOICES):
            raise ValidationError("Invalid signer type")
        return value

    def validate_status(self, value):
        """
        Validate that status is a valid choice

        Args:
            value (str): The status value to validate

        Returns:
            str: Validated status value
        """
        if value not in dict(SIGNATURE_STATUS_CHOICES):
            raise ValidationError("Invalid status")
        return value

    class Meta:
        """
        Meta class for SignatureRequestSerializer
        """
        model = SignatureRequest
        fields = ['id', 'document', 'signer', 'signer_type', 'status', 'requested_at', 'completed_at', 'reminder_count', 'last_reminder_at', 'external_reference']
        read_only_fields = ['id']


class SignatureRequestDetailSerializer(SignatureRequestSerializer):
    """
    Detailed serializer for signature requests including document and signer details
    """
    def to_representation(self, instance):
        """
        Override to_representation to include document and signer details

        Args:
            instance (SignatureRequest): The SignatureRequest instance

        Returns:
            dict: Serialized data with document and signer details included
        """
        representation = super().to_representation(instance)
        document = instance.document
        document_serializer = DocumentSerializer(document, read_only=True)
        representation['document'] = document_serializer.data

        signer = instance.signer
        signer_serializer = UserSerializer(signer, read_only=True)
        representation['signer'] = signer_serializer.data
        return representation

    class Meta:
        """
        Meta class for SignatureRequestDetailSerializer
        """
        model = SignatureRequest
        fields = SignatureRequestSerializer.Meta.fields
        read_only_fields = SignatureRequestSerializer.Meta.read_only_fields


class SignatureRequestCreateSerializer(serializers.Serializer):
    """
    Serializer for creating signature requests
    """
    signers = serializers.ListField()
    email_subject = serializers.CharField()
    email_body = serializers.CharField()

    def validate_signers(self, value):
        """
        Validate that signers list contains valid signer information

        Args:
            value (list): The signers list to validate

        Returns:
            list: Validated signers list
        """
        # Implement signers list validation here
        return value


class DocumentFieldSerializer(BaseModelSerializer):
    """
    Serializer for document fields
    """
    document = serializers.PrimaryKeyRelatedField(queryset=Document.objects.all())
    field_name = serializers.CharField()
    field_type = serializers.ChoiceField(choices=DOCUMENT_FIELD_TYPE_CHOICES)
    field_value = serializers.CharField()
    x_position = serializers.IntegerField()
    y_position = serializers.IntegerField()
    page_number = serializers.IntegerField()

    def validate_field_type(self, value):
        """
        Validate that field_type is a valid choice

        Args:
            value (str): The field_type value to validate

        Returns:
            str: Validated field_type value
        """
        if value not in dict(DOCUMENT_FIELD_TYPE_CHOICES):
            raise ValidationError("Invalid field type")
        return value

    def validate_page_number(self, value):
        """
        Validate that page_number is positive

        Args:
            value (int): The page_number value to validate

        Returns:
            int: Validated page_number value
        """
        if value <= 0:
            raise ValidationError("Page number must be positive")
        return value

    class Meta:
        """
        Meta class for DocumentFieldSerializer
        """
        model = DocumentField
        fields = ['id', 'document', 'field_name', 'field_type', 'field_value', 'x_position', 'y_position', 'page_number']