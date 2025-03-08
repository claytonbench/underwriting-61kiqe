"""
Implements the core service layer for the reporting functionality in the loan management system.
This file provides services for report generation, scheduling, delivery, and permission management.
It acts as a bridge between the API views and the underlying report implementations, handling business logic and orchestrating the reporting workflow.
"""

import uuid  # standard library
from datetime import datetime  # standard library

from django.utils import timezone  # Django 4.2+
from django.db import transaction  # Django 4.2+
from django.db.models import Q  # Django 4.2+
from config.celery import app  # celery 5.3+

from .models import (  # Import the ReportConfiguration model for managing report configurations
    ReportConfiguration,  # Import the ReportConfiguration model for managing report configurations
    SavedReport,  # Import the SavedReport model for storing and retrieving report results
    ReportSchedule,  # Import the ReportSchedule model for scheduling recurring reports
    ReportDelivery,  # Import the ReportDelivery model for tracking report delivery
    ReportPermission,
    REPORT_TYPES,  # Import report type constants for validation
    REPORT_STATUS,  # Import report status constants for status tracking
    EXPORT_FORMATS,
)
from .reports.application_volume import ApplicationVolumeReport  # Import the ApplicationVolumeReport class for generating application volume reports
from .reports.underwriting_metrics import UnderwritingMetricsReport  # Import the UnderwritingMetricsReport class for generating underwriting metrics reports
from .reports.document_status import DocumentStatusReport  # Import the DocumentStatusReport class for generating document status reports
from .reports.funding_metrics import FundingMetricsReport  # Import the FundingMetricsReport class for generating funding metrics reports
from .exports import ReportExporter  # Import the ReportExporter class for exporting reports to various formats
from core.exceptions import ValidationException, ResourceNotFoundException  # Import exception class for validation errors
from utils.logging import logger  # Import logging utility for tracking service operations


REPORT_GENERATORS = {
    'application_volume': ApplicationVolumeReport,
    'underwriting_metrics': UnderwritingMetricsReport,
    'document_status': DocumentStatusReport,
    'funding_metrics': FundingMetricsReport
}

DEFAULT_EXPIRY_SECONDS = 3600


def get_report_generator(report_type):
    """
    Gets the appropriate report generator class for a given report type

    Args:
        report_type (str): The type of report to generate

    Returns:
        class: Report generator class for the specified report type
    """
    if report_type in REPORT_GENERATORS:
        return REPORT_GENERATORS[report_type]()
    else:
        raise ValidationException(f"Invalid report type: {report_type}")


class ReportService:
    """
    Service class that provides methods for report generation, scheduling, delivery, and permission management
    """

    def __init__(self, export_bucket_name, export_region):
        """
        Initialize the ReportService with required dependencies

        Args:
            export_bucket_name (str): The name of the S3 bucket for report exports
            export_region (str): The AWS region of the S3 bucket
        """
        self._exporter = ReportExporter(bucket_name=export_bucket_name, region=export_region)
        logger.info(f"ReportService initialized with bucket: {export_bucket_name}, region: {export_region}")

    def generate_report(self, configuration, parameters_override, user):
        """
        Generates a report based on a configuration and parameters

        Args:
            configuration (ReportConfiguration): The report configuration
            parameters_override (dict): Optional parameters to override the defaults
            user (User): The user generating the report

        Returns:
            SavedReport: The generated report
        """
        try:
            # Create a new SavedReport instance using configuration.generate_report()
            report = configuration.generate_report(parameters_override=parameters_override, user=user)

            # Get the appropriate report generator for the report type
            generator = get_report_generator(configuration.report_type)

            # Call the generator's generate method with the report and parameters
            success = generator.generate(report, report.parameters)

            if success:
                # If generation is successful, return the report
                return report
            else:
                # If generation fails, log the error and raise an exception
                logger.error(f"Report generation failed for report {report.id}")
                raise Exception("Report generation failed")

        except Exception as e:
            # Handle any exceptions during the process
            logger.error(f"Error generating report: {str(e)}")
            raise

    def generate_report_async(self, configuration, parameters_override, user):
        """
        Asynchronously generates a report based on a configuration and parameters

        Args:
            configuration (ReportConfiguration): The report configuration
            parameters_override (dict): Optional parameters to override the defaults
            user (User): The user generating the report

        Returns:
            dict: Task information including task_id and report_id
        """
        try:
            # Create a new SavedReport instance using configuration.generate_report()
            report = configuration.generate_report(parameters_override=parameters_override, user=user)

            # Set the report status to PENDING
            report.update_status(REPORT_STATUS['PENDING'])

            # Submit a task to ReportTaskManager.generate_report_task
            task = ReportTaskManager.generate_report_task.delay(str(report.id), configuration.report_type, report.parameters)

            # Return a dictionary with task_id and report_id
            return {'task_id': task.id, 'report_id': str(report.id)}

        except Exception as e:
            # Handle any exceptions during the process
            logger.error(f"Error generating report asynchronously: {str(e)}")
            raise

    def get_report(self, report_id):
        """
        Retrieves a saved report by ID

        Args:
            report_id (str): The ID of the report to retrieve

        Returns:
            SavedReport: The retrieved report
        """
        try:
            # Query the SavedReport model for the report with the given ID
            report = SavedReport.objects.get(id=report_id)

            # If found, return the report
            return report

        except SavedReport.DoesNotExist:
            # If not found, raise ResourceNotFoundException
            raise ResourceNotFoundException(f"Report with ID {report_id} not found")

        except Exception as e:
            # Handle any exceptions during the process
            logger.error(f"Error retrieving report: {str(e)}")
            raise

    def list_reports(self, filters, user):
        """
        Lists saved reports based on filter criteria

        Args:
            filters (dict): Filter criteria
            user (User): The user requesting the list

        Returns:
            QuerySet: QuerySet of SavedReport objects matching the filters
        """
        try:
            # Start with a base query for SavedReport objects
            queryset = SavedReport.objects.all()

            # Apply filters for report_type if provided
            report_type = filters.get('report_type')
            if report_type:
                queryset = queryset.filter(report_type=report_type)

            # Apply filters for configuration_id if provided
            configuration_id = filters.get('configuration_id')
            if configuration_id:
                queryset = queryset.filter(configuration_id=configuration_id)

            # Apply filters for status if provided
            status = filters.get('status')
            if status:
                queryset = queryset.filter(status=status)

            # Apply filters for date range if provided
            start_date = filters.get('start_date')
            end_date = filters.get('end_date')
            if start_date and end_date:
                queryset = queryset.filter(created_at__range=[start_date, end_date])

            # Apply user-specific filters based on permissions
            # TODO: Implement permission-based filtering

            # Return the filtered QuerySet
            return queryset

        except Exception as e:
            # Handle any exceptions during the process
            logger.error(f"Error listing reports: {str(e)}")
            raise

    def export_report(self, report, export_format, user):
        """
        Exports a report to a specified format

        Args:
            report (SavedReport): The report to export
            export_format (str): The format to export the report to
            user (User): The user requesting the export

        Returns:
            dict: Export details including file path and download URL
        """
        try:
            # Validate that the report is in COMPLETED status
            if report.status != REPORT_STATUS['COMPLETED']:
                raise ValidationException("Report must be in COMPLETED status to be exported.")

            # Validate that the export_format is supported
            if export_format not in EXPORT_FORMATS.values():
                raise ValidationException(f"Invalid export format: {export_format}. Supported formats are: {', '.join(EXPORT_FORMATS.values())}")

            # Call the ReportExporter to export the report
            export_details = self._exporter.export_report(report, export_format)

            # Generate a download URL for the exported file
            download_url = self.get_report_download_url(report, user)

            # Return export details including file path and download URL
            return {
                'file_path': export_details['file_path'],
                'download_url': download_url,
                'content_type': export_details['content_type'],
                'filename': export_details['filename']
            }

        except Exception as e:
            # Handle any exceptions during the process
            logger.error(f"Error exporting report: {str(e)}")
            raise

    def get_report_download_url(self, report, user, expiry_seconds=None):
        """
        Generates a download URL for a report file

        Args:
            report (SavedReport): The report to generate the URL for
            user (User): The user requesting the download URL
            expiry_seconds (int): The expiration time for the URL in seconds

        Returns:
            str: Presigned URL for downloading the report
        """
        try:
            # Validate that the report has a file_path
            if not report.file_path:
                raise ValidationException("Report does not have a file path.")

            # Set expiry_seconds to provided value or DEFAULT_EXPIRY_SECONDS
            if expiry_seconds is None:
                expiry_seconds = DEFAULT_EXPIRY_SECONDS

            # Call report.get_download_url() with expiry_seconds
            download_url = report.get_download_url(expiry_seconds=expiry_seconds)

            # Return the generated URL
            return download_url

        except Exception as e:
            # Handle any exceptions during the process
            logger.error(f"Error generating download URL: {str(e)}")
            raise

    def schedule_report(self, configuration, schedule_data, user):
        """
        Creates a schedule for recurring report generation

        Args:
            configuration (ReportConfiguration): The report configuration
            schedule_data (dict): Schedule data
            user (User): The user creating the schedule

        Returns:
            ReportSchedule: The created schedule
        """
        try:
            # Create a new ReportSchedule instance with the provided data
            schedule = ReportSchedule(
                name=schedule_data['name'],
                configuration=configuration,
                frequency=schedule_data['frequency'],
                cron_expression=schedule_data.get('cron_expression'),
                parameters_override=schedule_data.get('parameters_override'),
                is_active=schedule_data.get('is_active', True),
                delivery_method=schedule_data.get('delivery_method'),
                delivery_config=schedule_data.get('delivery_config'),
                created_by=user
            )

            # Calculate the next run time based on frequency and cron expression
            schedule.next_run = schedule.calculate_next_run()

            # Save the schedule
            schedule.save()

            # Return the created schedule
            return schedule

        except Exception as e:
            # Handle any exceptions during the process
            logger.error(f"Error scheduling report: {str(e)}")
            raise

    def list_schedules(self, filters, user):
        """
        Lists report schedules based on filter criteria

        Args:
            filters (dict): Filter criteria
            user (User): The user requesting the list

        Returns:
            QuerySet: QuerySet of ReportSchedule objects matching the filters
        """
        try:
            # Start with a base query for ReportSchedule objects
            queryset = ReportSchedule.objects.all()

            # Apply filters for configuration_id if provided
            configuration_id = filters.get('configuration_id')
            if configuration_id:
                queryset = queryset.filter(configuration_id=configuration_id)

            # Apply filters for frequency if provided
            frequency = filters.get('frequency')
            if frequency:
                queryset = queryset.filter(frequency=frequency)

            # Apply filters for is_active if provided
            is_active = filters.get('is_active')
            if is_active is not None:
                queryset = queryset.filter(is_active=is_active)

            # Apply user-specific filters based on permissions
            # TODO: Implement permission-based filtering

            # Return the filtered QuerySet
            return queryset

        except Exception as e:
            # Handle any exceptions during the process
            logger.error(f"Error listing report schedules: {str(e)}")
            raise

    def execute_schedule(self, schedule, user):
        """
        Executes a report schedule to generate a report

        Args:
            schedule (ReportSchedule): The schedule to execute
            user (User): The user executing the schedule

        Returns:
            SavedReport: The generated report
        """
        try:
            # Call schedule.execute() to generate a report
            report = schedule.execute()

            # If delivery_method is set, create a ReportDelivery for the report
            if schedule.delivery_method:
                self.deliver_report(report, schedule.delivery_method, schedule.delivery_config, user)

            # Return the generated report
            return report

        except Exception as e:
            # Handle any exceptions during the process
            logger.error(f"Error executing report schedule: {str(e)}")
            raise

    def process_due_schedules(self):
        """
        Processes all schedules that are due for execution

        Returns:
            list: List of generated reports
        """
        try:
            # Query for all active ReportSchedule objects
            schedules = ReportSchedule.objects.filter(is_active=True)

            # Filter for schedules that are due (is_due() returns True)
            due_schedules = [schedule for schedule in schedules if schedule.is_due()]

            # For each due schedule, call execute_schedule()
            generated_reports = []
            for schedule in due_schedules:
                try:
                    report = self.execute_schedule(schedule, schedule.created_by)
                    generated_reports.append(report)
                except Exception as e:
                    logger.error(f"Failed to execute schedule {schedule.id}: {str(e)}")

            # Return the list of generated reports
            return generated_reports

        except Exception as e:
            # Handle any exceptions during the process
            logger.error(f"Error processing due schedules: {str(e)}")
            raise

    def deliver_report(self, report, delivery_method, delivery_config, user):
        """
        Delivers a report using the specified delivery method

        Args:
            report (SavedReport): The report to deliver
            delivery_method (str): The delivery method to use
            delivery_config (dict): Delivery configuration
            user (User): The user initiating the delivery

        Returns:
            ReportDelivery: The created delivery record
        """
        try:
            # Create a new ReportDelivery instance with the provided data
            delivery = ReportDelivery(
                report=report,
                delivery_method=delivery_method,
                delivery_config=delivery_config,
                created_by=user
            )

            # Call delivery.deliver() to attempt delivery
            delivery.deliver()

            # Return the delivery record
            return delivery

        except Exception as e:
            # Handle any exceptions during the process
            logger.error(f"Error delivering report: {str(e)}")
            raise

    def retry_delivery(self, delivery, user):
        """
        Retries a failed report delivery

        Args:
            delivery (ReportDelivery): The delivery to retry
            user (User): The user initiating the retry

        Returns:
            bool: True if retry was successful, False otherwise
        """
        try:
            # Call delivery.retry() to attempt delivery again
            success = delivery.retry()

            # Return the result of the retry attempt
            return success

        except Exception as e:
            # Handle any exceptions during the process
            logger.error(f"Error retrying delivery: {str(e)}")
            raise

    @transaction.atomic
    def create_report_configuration(self, config_data, user):
        """
        Creates a new report configuration

        Args:
            config_data (dict): Configuration data
            user (User): The user creating the configuration

        Returns:
            ReportConfiguration: The created configuration
        """
        try:
            # Extract parameters from config_data
            parameters = config_data.pop('parameters', None)

            # Create a new ReportConfiguration instance with the provided data
            configuration = ReportConfiguration(
                name=config_data['name'],
                description=config_data.get('description'),
                report_type=config_data['report_type'],
                is_active=config_data.get('is_active', True),
                school_id=config_data.get('school_id'),
                created_by=user
            )

            # If parameters provided, set them using set_parameter method
            if parameters:
                configuration.parameters = parameters

            # Save the configuration
            configuration.save()

            # Return the created configuration
            return configuration

        except Exception as e:
            # Handle any exceptions during the process
            logger.error(f"Error creating report configuration: {str(e)}")
            raise

    @transaction.atomic
    def update_report_configuration(self, configuration, config_data, user):
        """
        Updates an existing report configuration

        Args:
            configuration (ReportConfiguration): The report configuration to update
            config_data (dict): Configuration data
            user (User): The user updating the configuration

        Returns:
            ReportConfiguration: The updated configuration
        """
        try:
            # Extract parameters from config_data
            parameters = config_data.pop('parameters', None)

            # Update configuration fields from config_data
            configuration.name = config_data.get('name', configuration.name)
            configuration.description = config_data.get('description', configuration.description)
            configuration.report_type = config_data.get('report_type', configuration.report_type)
            configuration.is_active = config_data.get('is_active', configuration.is_active)
            configuration.school_id = config_data.get('school_id', configuration.school_id)

            # Set updated_by to the provided user
            configuration.updated_by = user

            # If parameters provided, update them using set_parameter method
            if parameters:
                configuration.parameters = parameters

            # Save the configuration
            configuration.save()

            # Return the updated configuration
            return configuration

        except Exception as e:
            # Handle any exceptions during the process
            logger.error(f"Error updating report configuration: {str(e)}")
            raise

    def list_configurations(self, filters, user):
        """
        Lists report configurations based on filter criteria

        Args:
            filters (dict): Filter criteria
            user (User): The user requesting the list

        Returns:
            QuerySet: QuerySet of ReportConfiguration objects matching the filters
        """
        try:
            # Start with a base query for ReportConfiguration objects
            queryset = ReportConfiguration.objects.all()

            # Apply filters for report_type if provided
            report_type = filters.get('report_type')
            if report_type:
                queryset = queryset.filter(report_type=report_type)

            # Apply filters for school_id if provided
            school_id = filters.get('school_id')
            if school_id:
                queryset = queryset.filter(school_id=school_id)

            # Apply filters for is_active if provided
            is_active = filters.get('is_active')
            if is_active is not None:
                queryset = queryset.filter(is_active=is_active)

            # Apply user-specific filters based on permissions
            # TODO: Implement permission-based filtering

            # Return the filtered QuerySet
            return queryset

        except Exception as e:
            # Handle any exceptions during the process
            logger.error(f"Error listing report configurations: {str(e)}")
            raise

    def get_configuration(self, config_id):
        """
        Retrieves a report configuration by ID

        Args:
            config_id (str): The ID of the configuration to retrieve

        Returns:
            ReportConfiguration: The retrieved configuration
        """
        try:
            # Query the ReportConfiguration model for the configuration with the given ID
            configuration = ReportConfiguration.objects.get(id=config_id)

            # If found, return the configuration
            return configuration

        except ReportConfiguration.DoesNotExist:
            # If not found, raise ResourceNotFoundException
            raise ResourceNotFoundException(f"Report configuration with ID {config_id} not found")

        except Exception as e:
            # Handle any exceptions during the process
            logger.error(f"Error retrieving report configuration: {str(e)}")
            raise

    @transaction.atomic
    def set_report_permission(self, configuration, target_user, permissions, granting_user):
        """
        Sets permissions for a user on a report configuration

        Args:
            configuration (ReportConfiguration): The report configuration
            target_user (User): The user to grant permissions to
            permissions (dict): Permissions to set
            granting_user (User): The user granting the permissions

        Returns:
            ReportPermission: The created or updated permission
        """
        try:
            # Try to get existing permission for the user and configuration
            try:
                permission = ReportPermission.objects.get(configuration=configuration, user=target_user)
            except ReportPermission.DoesNotExist:
                permission = None

            # If not found, create a new ReportPermission instance
            if not permission:
                permission = ReportPermission(configuration=configuration, user=target_user)

            # Update permission fields from permissions dict
            permission.can_view = permissions.get('can_view', False)
            permission.can_generate = permissions.get('can_generate', False)
            permission.can_schedule = permissions.get('can_schedule', False)
            permission.can_export = permissions.get('can_export', False)

            # Set granted_by to the granting_user
            permission.granted_by = granting_user

            # Save the permission
            permission.save()

            # Return the permission
            return permission

        except Exception as e:
            # Handle any exceptions during the process
            logger.error(f"Error setting report permission: {str(e)}")
            raise

    def check_report_permission(self, configuration, user, permission_type):
        """
        Checks if a user has a specific permission on a report configuration

        Args:
            configuration (ReportConfiguration): The report configuration
            user (User): The user to check permissions for
            permission_type (str): The permission type to check (can_view, can_generate, etc.)

        Returns:
            bool: True if user has the permission, False otherwise
        """
        try:
            # If user is a system administrator, return True
            if user.user_type == 'system_admin':
                return True

            # If configuration.school matches user's school and user is a school admin, return True
            if configuration.school and user.user_type == 'school_admin' and configuration.school == user.school:
                return True

            # Try to get permission for the user and configuration
            try:
                permission = ReportPermission.objects.get(configuration=configuration, user=user)
            except ReportPermission.DoesNotExist:
                return False

            # If found, check the specified permission type (can_view, can_generate, etc.)
            if permission_type == 'can_view':
                return permission.can_view
            elif permission_type == 'can_generate':
                return permission.can_generate
            elif permission_type == 'can_schedule':
                return permission.can_schedule
            elif permission_type == 'can_export':
                return permission.can_export
            else:
                return False

        except Exception as e:
            # Handle any exceptions during the process
            logger.error(f"Error checking report permission: {str(e)}")
            raise


class ReportTaskManager:
    """
    Manager class for asynchronous report tasks using Celery
    """

    def __init__(self):
        """Default constructor"""
        pass

    @staticmethod
    @app.task
    def generate_report_task(report_id, report_type, parameters):
        """
        Celery task for asynchronous report generation

        Args:
            report_id (str): The ID of the report to generate
            report_type (str): The type of report to generate
            parameters (dict): Report parameters

        Returns:
            bool: True if report generation was successful, False otherwise
        """
        try:
            # Get the SavedReport with the given report_id
            report = SavedReport.objects.get(id=report_id)

            # Get the appropriate report generator for the report_type
            generator = get_report_generator(report_type)

            # Call the generator's generate method with the report and parameters
            success = generator.generate(report, parameters)

            # Return True if generation is successful, False otherwise
            return success

        except Exception as e:
            # Handle any exceptions during the process
            logger.error(f"Error generating report asynchronously: {str(e)}")
            return False

        finally:
            # Log the result of the task
            logger.info(f"Report generation task completed for report {report_id}")

    @staticmethod
    @app.task
    def export_report_task(report_id, export_format, bucket_name, region):
        """
        Celery task for asynchronous report export

        Args:
            report_id (str): The ID of the report to export
            export_format (str): The format to export the report to
            bucket_name (str): The name of the S3 bucket for report exports
            region (str): The AWS region of the S3 bucket

        Returns:
            dict: Export details including file path and content type
        """
        try:
            # Get the SavedReport with the given report_id
            report = SavedReport.objects.get(id=report_id)

            # Initialize a ReportExporter with the provided bucket_name and region
            exporter = ReportExporter(bucket_name=bucket_name, region=region)

            # Call the exporter's export_report method with the report and export_format
            export_details = exporter.export_report(report, export_format)

            # Return the export details
            return export_details

        except Exception as e:
            # Handle any exceptions during the process
            logger.error(f"Error exporting report asynchronously: {str(e)}")
            return None

        finally:
            # Log the result of the task
            logger.info(f"Report export task completed for report {report_id}")

    @staticmethod
    @app.task(bind=True)
    def process_scheduled_reports_task(self):  # Added self parameter
        """
        Celery task for processing scheduled reports

        Returns:
            int: Number of reports generated
        """
        try:
            # Initialize a ReportService
            service = ReportService(EXPORT_BUCKET_NAME, EXPORT_REGION)

            # Call service.process_due_schedules() to process all due schedules
            generated_reports = service.process_due_schedules()

            # Count the number of reports generated
            report_count = len(generated_reports)

            # Return the count
            return report_count

        except Exception as e:
            # Handle any exceptions during the process
            logger.error(f"Error processing scheduled reports: {str(e)}")
            return 0

        finally:
            # Log the result of the task
            logger.info(f"Scheduled reports task completed, {self.request.id} reports generated")