"""
Defines serializers for the reporting functionality in the loan management system.
These serializers handle the conversion between Python objects and JSON representations for report configurations, saved reports, report schedules, report deliveries, and report permissions. They also implement validation logic for report parameters and scheduling options.
"""

from rest_framework import serializers  # rest_framework 3.14+
from rest_framework.exceptions import ValidationError  # rest_framework 3.14+
from django.contrib.auth import get_user_model  # django.contrib.auth 4.2+
from croniter import croniter  # croniter 1.0+

from ...core.serializers import BaseModelSerializer, BaseSerializer  # src/backend/core/serializers.py
from ..models import (  # src/backend/apps/reporting/models.py
    ReportConfiguration, SavedReport, ReportSchedule, ReportDelivery, ReportPermission,
    REPORT_TYPES, SCHEDULE_FREQUENCY, DELIVERY_METHOD, EXPORT_FORMATS
)
from ..services import get_report_generator  # src/backend/apps/reporting/services.py
from ...core.exceptions import ValidationException  # src/backend/core/exceptions.py
from ...utils.logging import logger  # src/backend/utils/logging.py


class ReportConfigurationSerializer(BaseModelSerializer):
    """
    Serializer for the ReportConfiguration model
    """
    class Meta:
        model = ReportConfiguration
        fields = '__all__'

    def validate(self, data):
        """
        Validates the report configuration data
        Args:
            data (dict):
        Returns:
            dict: Validated data
        """
        logger.info(f"Validating ReportConfiguration data: {data}")

        # LD1: Validate that report_type is a valid type from REPORT_TYPES
        report_type = data.get('report_type')
        if report_type not in REPORT_TYPES:
            raise serializers.ValidationError(f"Invalid report type: {report_type}. Must be one of {', '.join(REPORT_TYPES.keys())}")

        # LD1: Get the report generator for the specified report_type
        generator = get_report_generator(report_type)

        # LD1: Validate parameters using the generator's validate_parameters method
        parameters = data.get('parameters', {})
        is_valid, error_message = generator.validate_parameters(parameters)
        if not is_valid:
            raise serializers.ValidationError(error_message)

        # LD1: Return the validated data
        logger.info("ReportConfiguration data is valid")
        return data

    def create(self, validated_data):
        """
        Creates a new ReportConfiguration instance
        Args:
            validated_data (dict):
        Returns:
            ReportConfiguration: The created configuration instance
        """
        logger.info(f"Creating ReportConfiguration with validated data: {validated_data}")

        # LD1: Extract parameters from validated_data
        parameters = validated_data.pop('parameters', {})

        # LD1: Create a new ReportConfiguration instance without parameters
        instance = ReportConfiguration.objects.create(**validated_data)

        # LD1: Set parameters using set_parameter method
        instance.parameters = parameters
        instance.save()

        # LD1: Return the created instance
        logger.info(f"ReportConfiguration created with ID: {instance.id}")
        return instance

    def update(self, instance, validated_data):
        """
        Updates an existing ReportConfiguration instance
        Args:
            instance (ReportConfiguration):
            validated_data (dict):
        Returns:
            ReportConfiguration: The updated configuration instance
        """
        logger.info(f"Updating ReportConfiguration {instance.id} with validated data: {validated_data}")

        # LD1: Extract parameters from validated_data
        parameters = validated_data.pop('parameters', None)

        # LD1: Update instance fields from validated_data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # LD1: If parameters provided, update using set_parameter method
        if parameters is not None:
            instance.parameters = parameters

        # LD1: Save the instance
        instance.save()

        # LD1: Return the updated instance
        logger.info(f"ReportConfiguration {instance.id} updated successfully")
        return instance

    def to_representation(self, instance):
        """
        Converts the ReportConfiguration instance to a dictionary
        Args:
            instance (ReportConfiguration):
        Returns:
            dict: Dictionary representation of the instance
        """
        # LD1: Call parent to_representation method
        representation = super().to_representation(instance)

        # LD1: Add report_type_display field using get_display_name
        representation['report_type_display'] = instance.get_display_name()

        # LD1: Return the representation
        return representation


class SavedReportSerializer(BaseModelSerializer):
    """
    Serializer for the SavedReport model
    """
    class Meta:
        model = SavedReport
        fields = '__all__'

    def to_representation(self, instance):
        """
        Converts the SavedReport instance to a dictionary
        Args:
            instance (SavedReport):
        Returns:
            dict: Dictionary representation of the instance
        """
        # LD1: Call parent to_representation method
        representation = super().to_representation(instance)

        # LD1: Add configuration_name field if configuration exists
        if instance.configuration:
            representation['configuration_name'] = instance.configuration.name

        # LD1: Add report_type_display field using REPORT_TYPES
        representation['report_type_display'] = REPORT_TYPES.get(instance.report_type)

        # LD1: Return the representation
        return representation

    def get_download_url(self, obj):
        """
        Serializer method field to get the download URL for the report
        Args:
            obj (SavedReport):
        Returns:
            str: Download URL or None if not available
        """
        # LD1: Check if the report has a file_path
        if obj.file_path:
            # LD1: If file_path exists, call get_download_url with default expiry
            return obj.get_download_url()
        else:
            # LD1: Return None if no file_path
            return None


class ReportScheduleSerializer(BaseModelSerializer):
    """
    Serializer for the ReportSchedule model
    """
    class Meta:
        model = ReportSchedule
        fields = '__all__'

    def validate_cron_expression(self, cron_expression):
        """
        Validates the cron expression for custom schedules
        Args:
            cron_expression (str):
        Returns:
            str: Validated cron expression
        """
        # LD1: Check if cron_expression is provided
        if not cron_expression:
            return None  # Allow null for non-custom schedules

        # LD1: Try to parse the cron expression using croniter
        try:
            croniter(cron_expression)
        except ValueError as e:
            # LD1: If parsing fails, raise ValidationError
            raise serializers.ValidationError(f"Invalid cron expression: {str(e)}")

        # LD1: Return the validated cron expression
        return cron_expression

    def validate(self, data):
        """
        Validates the report schedule data
        Args:
            data (dict):
        Returns:
            dict: Validated data
        """
        logger.info(f"Validating ReportSchedule data: {data}")

        # LD1: Validate that frequency is a valid value from SCHEDULE_FREQUENCY
        frequency = data.get('frequency')
        if frequency not in SCHEDULE_FREQUENCY:
            raise serializers.ValidationError(f"Invalid frequency: {frequency}. Must be one of {', '.join(SCHEDULE_FREQUENCY.keys())}")

        # LD1: If frequency is CUSTOM, validate cron_expression is provided
        if frequency == SCHEDULE_FREQUENCY['CUSTOM']:
            cron_expression = data.get('cron_expression')
            if not cron_expression:
                raise serializers.ValidationError("Cron expression is required for custom schedules")
            try:
                self.validate_cron_expression(cron_expression)
            except serializers.ValidationError as e:
                raise e

        # LD1: If delivery_method is provided, validate it's a valid value from DELIVERY_METHOD
        delivery_method = data.get('delivery_method')
        if delivery_method and delivery_method not in DELIVERY_METHOD:
            raise serializers.ValidationError(f"Invalid delivery method: {delivery_method}. Must be one of {', '.join(DELIVERY_METHOD.keys())}")

        # LD1: If delivery_method is provided, validate delivery_config is also provided
        if delivery_method and not data.get('delivery_config'):
            raise serializers.ValidationError("Delivery configuration is required when delivery method is specified")

        # LD1: Return the validated data
        logger.info("ReportSchedule data is valid")
        return data

    def to_representation(self, instance):
        """
        Converts the ReportSchedule instance to a dictionary
        Args:
            instance (ReportSchedule):
        Returns:
            dict: Dictionary representation of the instance
        """
        # LD1: Call parent to_representation method
        representation = super().to_representation(instance)

        # LD1: Add configuration_name field if configuration exists
        if instance.configuration:
            representation['configuration_name'] = instance.configuration.name

        # LD1: Add frequency_display field using SCHEDULE_FREQUENCY
        representation['frequency_display'] = SCHEDULE_FREQUENCY.get(instance.frequency)

        # LD1: Add delivery_method_display field using DELIVERY_METHOD if applicable
        if instance.delivery_method:
            representation['delivery_method_display'] = DELIVERY_METHOD.get(instance.delivery_method)

        # LD1: Return the representation
        return representation


class ReportDeliverySerializer(BaseModelSerializer):
    """
    Serializer for the ReportDelivery model
    """
    class Meta:
        model = ReportDelivery
        fields = '__all__'

    def validate(self, data):
        """
        Validates the report delivery data
        Args:
            data (dict):
        Returns:
            dict: Validated data
        """
        logger.info(f"Validating ReportDelivery data: {data}")

        # LD1: Validate that delivery_method is a valid value from DELIVERY_METHOD
        delivery_method = data.get('delivery_method')
        if delivery_method not in DELIVERY_METHOD:
            raise serializers.ValidationError(f"Invalid delivery method: {delivery_method}. Must be one of {', '.join(DELIVERY_METHOD.keys())}")

        # LD1: Validate delivery_config based on delivery_method
        delivery_config = data.get('delivery_config', {})
        if delivery_method == DELIVERY_METHOD['EMAIL']:
            # LD1: For EMAIL, validate recipient_email, subject
            if not delivery_config.get('recipient_email'):
                raise serializers.ValidationError("Recipient email is required for EMAIL delivery method")
            if not delivery_config.get('subject'):
                raise serializers.ValidationError("Subject is required for EMAIL delivery method")
        elif delivery_method == DELIVERY_METHOD['S3']:
            # LD1: For S3, validate bucket_name, key_prefix
            if not delivery_config.get('bucket_name'):
                raise serializers.ValidationError("Bucket name is required for S3 delivery method")
            if not delivery_config.get('key_prefix'):
                raise serializers.ValidationError("Key prefix is required for S3 delivery method")
        elif delivery_method == DELIVERY_METHOD['SFTP']:
            # LD1: For SFTP, validate host, port, username, password, path
            if not all([delivery_config.get('host'), delivery_config.get('username'), delivery_config.get('password'), delivery_config.get('path')]):
                raise serializers.ValidationError("Host, username, password, and path are required for SFTP delivery method")

        # LD1: Return the validated data
        logger.info("ReportDelivery data is valid")
        return data

    def to_representation(self, instance):
        """
        Converts the ReportDelivery instance to a dictionary
        Args:
            instance (ReportDelivery):
        Returns:
            dict: Dictionary representation of the instance
        """
        # LD1: Call parent to_representation method
        representation = super().to_representation(instance)

        # LD1: Add report_id and report_type if report exists
        if instance.report:
            representation['report_id'] = str(instance.report.id)
            representation['report_type'] = instance.report.report_type

        # LD1: Add delivery_method_display field using DELIVERY_METHOD
        representation['delivery_method_display'] = DELIVERY_METHOD.get(instance.delivery_method)

        # LD1: Return the representation
        return representation


class ReportPermissionSerializer(BaseModelSerializer):
    """
    Serializer for the ReportPermission model
    """
    class Meta:
        model = ReportPermission
        fields = '__all__'

    def to_representation(self, instance):
        """
        Converts the ReportPermission instance to a dictionary
        Args:
            instance (ReportPermission):
        Returns:
            dict: Dictionary representation of the instance
        """
        # LD1: Call parent to_representation method
        representation = super().to_representation(instance)

        # LD1: Add configuration_name if configuration exists
        if instance.configuration:
            representation['configuration_name'] = instance.configuration.name

        # LD1: Add user_email and user_name if user exists
        if instance.user:
            representation['user_email'] = instance.user.email
            representation['user_name'] = instance.user.get_full_name()

        # LD1: Add granted_by_name if granted_by exists
        if instance.granted_by:
            representation['granted_by_name'] = instance.granted_by.get_full_name()

        # LD1: Return the representation
        return representation


class ReportGenerateSerializer(BaseSerializer):
    """
    Serializer for report generation requests
    """
    configuration_id = serializers.UUIDField(required=True)
    parameters_override = serializers.JSONField(required=False, allow_null=True)
    async = serializers.BooleanField(required=False, default=False)

    def validate(self, data):
        """
        Validates the report generation request data
        Args:
            data (dict):
        Returns:
            dict: Validated data
        """
        logger.info(f"Validating ReportGenerate data: {data}")

        # LD1: Validate that configuration_id is provided
        if not data.get('configuration_id'):
            raise serializers.ValidationError("Configuration ID is required")

        # LD1: If parameters_override is provided, validate it's a dictionary
        if data.get('parameters_override') and not isinstance(data['parameters_override'], dict):
            raise serializers.ValidationError("Parameters override must be a dictionary")

        # LD1: If async is provided, validate it's a boolean
        if data.get('async') and not isinstance(data['async'], bool):
            raise serializers.ValidationError("Async must be a boolean")

        # LD1: Return the validated data
        logger.info("ReportGenerate data is valid")
        return data


class ReportExportSerializer(BaseSerializer):
    """
    Serializer for report export requests
    """
    export_format = serializers.CharField(required=True)
    async = serializers.BooleanField(required=False, default=False)

    def validate(self, data):
        """
        Validates the report export request data
        Args:
            data (dict):
        Returns:
            dict: Validated data
        """
        logger.info(f"Validating ReportExport data: {data}")

        # LD1: Validate that export_format is provided and is a valid value from EXPORT_FORMATS
        export_format = data.get('export_format')
        if export_format not in EXPORT_FORMATS:
            raise serializers.ValidationError(f"Invalid export format: {export_format}. Must be one of {', '.join(EXPORT_FORMATS.keys())}")

        # LD1: If async is provided, validate it's a boolean
        if data.get('async') and not isinstance(data['async'], bool):
            raise serializers.ValidationError("Async must be a boolean")

        # LD1: Return the validated data
        logger.info("ReportExport data is valid")
        return data

class UserSerializer(BaseModelSerializer):
    """
    Minimal serializer for User model in report contexts
    """
    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'first_name', 'last_name']