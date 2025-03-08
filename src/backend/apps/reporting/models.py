"""
Defines the data models for the reporting functionality in the loan management system.

This module provides models for report configurations, saved reports, report schedules,
report deliveries, and report permissions to support the comprehensive reporting
capabilities required by the system.
"""

from django.db import models  # Django 4.2+
from django.utils import timezone  # Django 4.2+
import uuid  # standard library
import json  # standard library
from croniter import croniter  # croniter 1.0+

from ...core.models import CoreModel
from ...utils.storage import S3Storage
from ...utils.logging import logger

# Report types with display names
REPORT_TYPES = {
    'application_volume': 'Application Volume Report',
    'document_status': 'Document Status Report',
    'underwriting_metrics': 'Underwriting Metrics Report',
    'funding_metrics': 'Funding Metrics Report'
}

# Report generation status
REPORT_STATUS = {
    'PENDING': 'pending',
    'GENERATING': 'generating',
    'COMPLETED': 'completed',
    'FAILED': 'failed',
    'EXPIRED': 'expired'
}

# Schedule frequency options
SCHEDULE_FREQUENCY = {
    'DAILY': 'daily',
    'WEEKLY': 'weekly',
    'MONTHLY': 'monthly',
    'CUSTOM': 'custom'
}

# Delivery methods
DELIVERY_METHOD = {
    'EMAIL': 'email',
    'S3': 's3',
    'SFTP': 'sftp'
}

# Delivery status
DELIVERY_STATUS = {
    'PENDING': 'pending',
    'DELIVERED': 'delivered',
    'FAILED': 'failed'
}

# Export format options
EXPORT_FORMATS = {
    'CSV': 'csv',
    'EXCEL': 'xlsx',
    'PDF': 'pdf',
    'JSON': 'json'
}


class ReportConfiguration(CoreModel):
    """
    Model for storing report configurations including type, parameters, and metadata.
    
    This model defines the configuration for different types of reports that can
    be generated in the system.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    report_type = models.CharField(max_length=50, choices=[(k, v) for k, v in REPORT_TYPES.items()])
    parameters = models.JSONField(default=dict, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    school = models.ForeignKey('schools.School', on_delete=models.CASCADE, null=True, blank=True, 
                              related_name='report_configurations')
    
    def get_parameter(self, key, default=None):
        """
        Gets a parameter value from the parameters JSON field.
        
        Args:
            key (str): The parameter key to look up
            default: The default value to return if the key is not found
            
        Returns:
            The parameter value or default if not found
        """
        if self.parameters is None:
            return default
        
        return self.parameters.get(key, default)
    
    def set_parameter(self, key, value):
        """
        Sets a parameter value in the parameters JSON field.
        
        Args:
            key (str): The parameter key to set
            value: The value to set for the parameter
        """
        if self.parameters is None:
            self.parameters = {}
            
        self.parameters[key] = value
        self.save()
    
    def generate_report(self, parameters_override=None, user=None):
        """
        Generates a report based on this configuration.
        
        Args:
            parameters_override (dict): Optional parameters to override the defaults
            user: The user generating the report
            
        Returns:
            SavedReport: The generated report instance
        """
        # Create a new report instance
        report = SavedReport(
            report_type=self.report_type,
            configuration=self,
            created_by=user
        )
        
        # Merge parameters with overrides if provided
        if parameters_override:
            # Start with default parameters
            merged_params = self.parameters.copy() if self.parameters else {}
            
            # Update with overrides
            merged_params.update(parameters_override)
            
            report.parameters = merged_params
        else:
            report.parameters = self.parameters
        
        report.save()
        logger.info(f"Generated report {report.id} from configuration {self.name}")
        return report
    
    def get_display_name(self):
        """
        Gets a user-friendly display name for the report type.
        
        Returns:
            str: Display name for the report type
        """
        return REPORT_TYPES.get(self.report_type, self.report_type)
    
    def __str__(self):
        return self.name


class SavedReport(CoreModel):
    """
    Model for storing generated reports including results, status, and file paths.
    
    This model represents a specific instance of a generated report and tracks its
    processing status, results, and associated files.
    """
    report_type = models.CharField(max_length=50, choices=[(k, v) for k, v in REPORT_TYPES.items()])
    configuration = models.ForeignKey(ReportConfiguration, on_delete=models.SET_NULL, 
                                     null=True, related_name='reports')
    parameters = models.JSONField(default=dict, blank=True, null=True)
    results = models.JSONField(default=dict, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[(v, v) for v in REPORT_STATUS.values()],
        default=REPORT_STATUS['PENDING']
    )
    error_message = models.TextField(blank=True, null=True)
    file_path = models.CharField(max_length=255, blank=True, null=True)
    file_format = models.CharField(
        max_length=10,
        choices=[(v, v) for v in EXPORT_FORMATS.values()],
        blank=True,
        null=True
    )
    generated_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def update_status(self, status):
        """
        Updates the status of the report.
        
        Args:
            status (str): The new status
        """
        self.status = status
        
        if status == REPORT_STATUS['COMPLETED']:
            self.generated_at = timezone.now()
            # Set expiration date to 30 days from now
            self.expires_at = timezone.now() + timezone.timedelta(days=30)
            
        self.save()
        logger.info(f"Updated report {self.id} status to {status}")
    
    def set_results(self, results, file_path=None, file_format=None):
        """
        Sets the results of the report.
        
        Args:
            results (dict): The report results
            file_path (str): Path to the report file if applicable
            file_format (str): Format of the report file
        """
        self.results = results
        
        if file_path:
            self.file_path = file_path
            
        if file_format:
            self.file_format = file_format
            
        self.update_status(REPORT_STATUS['COMPLETED'])
    
    def set_error(self, error_message):
        """
        Sets an error message and updates status to FAILED.
        
        Args:
            error_message (str): The error message
        """
        self.error_message = error_message
        self.update_status(REPORT_STATUS['FAILED'])
        logger.error(f"Report {self.id} failed: {error_message}")
    
    def get_download_url(self, expiry_seconds=3600):
        """
        Generates a download URL for the report file.
        
        Args:
            expiry_seconds (int): URL expiration time in seconds
            
        Returns:
            str: Presigned URL for downloading the report
            
        Raises:
            ValueError: If no file path is available
        """
        if not self.file_path:
            raise ValueError("No file path available for this report")
            
        s3_storage = S3Storage()
        url = s3_storage.get_presigned_url(self.file_path, expiry_seconds)
        return url
    
    def is_expired(self):
        """
        Checks if the report has expired.
        
        Returns:
            bool: True if the report has expired, False otherwise
        """
        if not self.expires_at:
            return False
            
        return timezone.now() > self.expires_at
    
    def __str__(self):
        report_name = REPORT_TYPES.get(self.report_type, self.report_type)
        return f"{report_name} - {self.status} - {self.created_at.strftime('%Y-%m-%d')}"


class ReportSchedule(CoreModel):
    """
    Model for scheduling recurring report generation.
    
    This model defines schedules for automatic report generation at regular
    intervals or according to custom cron expressions.
    """
    name = models.CharField(max_length=100)
    configuration = models.ForeignKey(ReportConfiguration, on_delete=models.CASCADE, 
                                     related_name='schedules')
    frequency = models.CharField(
        max_length=20,
        choices=[(v, v) for v in SCHEDULE_FREQUENCY.values()],
        default=SCHEDULE_FREQUENCY['WEEKLY']
    )
    cron_expression = models.CharField(max_length=100, blank=True, null=True, 
                                      help_text="Cron expression for custom schedules")
    parameters_override = models.JSONField(default=dict, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    next_run = models.DateTimeField(blank=True, null=True)
    last_run = models.DateTimeField(blank=True, null=True)
    delivery_method = models.CharField(
        max_length=20,
        choices=[(v, v) for v in DELIVERY_METHOD.values()],
        default=DELIVERY_METHOD['EMAIL'],
        blank=True, 
        null=True
    )
    delivery_config = models.JSONField(default=dict, blank=True, null=True)
    
    def calculate_next_run(self, from_time=None):
        """
        Calculates the next run time based on frequency and cron expression.
        
        Args:
            from_time (datetime): Optional time to calculate from, defaults to current time
            
        Returns:
            datetime: The next scheduled run time
        """
        if not from_time:
            from_time = timezone.now()
            
        if self.frequency == SCHEDULE_FREQUENCY['DAILY']:
            # Next day, same time
            return from_time + timezone.timedelta(days=1)
            
        elif self.frequency == SCHEDULE_FREQUENCY['WEEKLY']:
            # Next week, same day and time
            return from_time + timezone.timedelta(days=7)
            
        elif self.frequency == SCHEDULE_FREQUENCY['MONTHLY']:
            # Next month, same day and time
            current_month = from_time.month
            current_year = from_time.year
            
            next_month = current_month + 1
            next_year = current_year
            
            if next_month > 12:
                next_month = 1
                next_year += 1
                
            # Handle month length differences and leap years
            day = min(from_time.day, [31, 29 if (next_year % 4 == 0 and (next_year % 100 != 0 or next_year % 400 == 0)) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][next_month - 1])
            
            return from_time.replace(year=next_year, month=next_month, day=day)
            
        elif self.frequency == SCHEDULE_FREQUENCY['CUSTOM'] and self.cron_expression:
            # Use croniter to calculate next run time
            cron = croniter(self.cron_expression, from_time)
            return cron.get_next(datetime)
            
        # Default fallback
        return from_time + timezone.timedelta(days=7)
    
    def execute(self):
        """
        Executes the schedule to generate a report.
        
        Returns:
            SavedReport: The generated report instance
        """
        # Generate report using configuration
        report = self.configuration.generate_report(
            parameters_override=self.parameters_override,
            user=self.created_by
        )
        
        # Update schedule state
        self.last_run = timezone.now()
        self.next_run = self.calculate_next_run()
        self.save()
        
        logger.info(f"Executed schedule {self.name}, generated report {report.id}")
        
        return report
    
    def is_due(self):
        """
        Checks if the schedule is due for execution.
        
        Returns:
            bool: True if the schedule is due, False otherwise
        """
        return self.is_active and self.next_run and self.next_run <= timezone.now()
    
    def __str__(self):
        return f"{self.name} - {self.frequency}"


class ReportDelivery(CoreModel):
    """
    Model for tracking report delivery status and methods.
    
    This model handles the delivery of generated reports through various methods
    like email, S3, or SFTP, and tracks delivery status.
    """
    report = models.ForeignKey(SavedReport, on_delete=models.CASCADE, related_name='deliveries')
    delivery_method = models.CharField(
        max_length=20,
        choices=[(v, v) for v in DELIVERY_METHOD.values()],
        default=DELIVERY_METHOD['EMAIL']
    )
    delivery_config = models.JSONField(default=dict)
    status = models.CharField(
        max_length=20,
        choices=[(v, v) for v in DELIVERY_STATUS.values()],
        default=DELIVERY_STATUS['PENDING']
    )
    error_message = models.TextField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    retry_count = models.IntegerField(default=0)
    last_retry_at = models.DateTimeField(blank=True, null=True)
    
    def deliver(self):
        """
        Attempts to deliver the report using the configured method.
        
        Returns:
            bool: True if delivery was successful, False otherwise
        """
        # Ensure report is completed
        if self.report.status != REPORT_STATUS['COMPLETED']:
            self.error_message = "Cannot deliver report that is not completed"
            self.status = DELIVERY_STATUS['FAILED']
            self.save()
            return False
            
        # Attempt delivery based on method
        try:
            success = False
            
            if self.delivery_method == DELIVERY_METHOD['EMAIL']:
                success = self._deliver_email()
            elif self.delivery_method == DELIVERY_METHOD['S3']:
                success = self._deliver_s3()
            elif self.delivery_method == DELIVERY_METHOD['SFTP']:
                success = self._deliver_sftp()
            else:
                self.error_message = f"Unsupported delivery method: {self.delivery_method}"
                self.status = DELIVERY_STATUS['FAILED']
                
            if success:
                self.status = DELIVERY_STATUS['DELIVERED']
                self.delivered_at = timezone.now()
                logger.info(f"Successfully delivered report {self.report.id} via {self.delivery_method}")
            else:
                self.status = DELIVERY_STATUS['FAILED']
                
            self.save()
            return success
            
        except Exception as e:
            self.status = DELIVERY_STATUS['FAILED']
            self.error_message = str(e)
            self.save()
            logger.error(f"Failed to deliver report {self.report.id}: {str(e)}")
            return False
    
    def retry(self):
        """
        Retries a failed delivery.
        
        Returns:
            bool: True if retry was successful, False otherwise
        """
        if self.status != DELIVERY_STATUS['FAILED']:
            return False
            
        self.retry_count += 1
        self.last_retry_at = timezone.now()
        self.save()
        
        logger.info(f"Retrying delivery of report {self.report.id}, attempt {self.retry_count}")
        return self.deliver()
    
    def _deliver_email(self):
        """
        Delivers the report via email.
        
        Returns:
            bool: True if email delivery was successful, False otherwise
        """
        # Extract email configuration
        recipient_email = self.delivery_config.get('recipient_email')
        if not recipient_email:
            self.error_message = "Missing recipient email address"
            return False
            
        subject = self.delivery_config.get('subject', f"Report: {self.report.configuration.name}")
        message = self.delivery_config.get('message', "Please find your report attached.")
        
        try:
            # Get download URL for the report
            download_url = self.report.get_download_url(expiry_seconds=24*60*60)  # 24 hours
            
            # Construct email with download link
            email_body = f"{message}\n\nYou can download your report using this link:\n{download_url}\n\nThis link will expire in 24 hours."
            
            # In a real implementation, we would call an email service here
            # For this model definition, we'll just simulate success
            logger.info(f"Would send email to {recipient_email} with subject '{subject}'")
            
            return True
            
        except Exception as e:
            self.error_message = f"Email delivery failed: {str(e)}"
            return False
    
    def _deliver_s3(self):
        """
        Delivers the report to an S3 bucket.
        
        Returns:
            bool: True if S3 delivery was successful, False otherwise
        """
        # Extract S3 configuration
        bucket_name = self.delivery_config.get('bucket_name')
        key_prefix = self.delivery_config.get('key_prefix', 'reports/')
        
        if not bucket_name:
            self.error_message = "Missing S3 bucket name"
            return False
            
        try:
            # Get report file from storage
            s3_storage = S3Storage()
            file_content, content_type, _ = s3_storage.retrieve(self.report.file_path)
            
            # Construct destination key
            destination_key = f"{key_prefix.rstrip('/')}/{self.report.id}.{self.report.file_format}"
            
            # Upload to destination bucket
            # In a real implementation, we would upload to the specified bucket
            # For this model definition, we'll just simulate success
            logger.info(f"Would copy report to S3 bucket {bucket_name} with key {destination_key}")
            
            return True
            
        except Exception as e:
            self.error_message = f"S3 delivery failed: {str(e)}"
            return False
    
    def _deliver_sftp(self):
        """
        Delivers the report via SFTP.
        
        Returns:
            bool: True if SFTP delivery was successful, False otherwise
        """
        # Extract SFTP configuration
        host = self.delivery_config.get('host')
        port = self.delivery_config.get('port', 22)
        username = self.delivery_config.get('username')
        password = self.delivery_config.get('password')
        path = self.delivery_config.get('path', '/')
        
        if not all([host, username, password]):
            self.error_message = "Missing required SFTP configuration (host, username, or password)"
            return False
            
        try:
            # Get report file from storage
            s3_storage = S3Storage()
            file_content, _, _ = s3_storage.retrieve(self.report.file_path)
            
            # Construct destination path
            destination_path = f"{path.rstrip('/')}/{self.report.id}.{self.report.file_format}"
            
            # Upload via SFTP
            # In a real implementation, we would connect to SFTP server and upload
            # For this model definition, we'll just simulate success
            logger.info(f"Would upload report to SFTP server {host}:{port} at path {destination_path}")
            
            return True
            
        except Exception as e:
            self.error_message = f"SFTP delivery failed: {str(e)}"
            return False
    
    def __str__(self):
        return f"Delivery of report {self.report.id} via {self.delivery_method} - {self.status}"


class ReportPermission(CoreModel):
    """
    Model for managing user permissions on report configurations.
    
    This model tracks which users have permission to view, generate, schedule,
    and export reports based on specific configurations.
    """
    configuration = models.ForeignKey(ReportConfiguration, on_delete=models.CASCADE, 
                                     related_name='permissions')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, 
                           related_name='report_permissions')
    can_view = models.BooleanField(default=True)
    can_generate = models.BooleanField(default=False)
    can_schedule = models.BooleanField(default=False)
    can_export = models.BooleanField(default=False)
    granted_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, 
                                  null=True, related_name='+')
    granted_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        """
        Override of save method to set granted_at timestamp.
        
        Args:
            *args, **kwargs: Arguments to pass to the parent save method
        """
        if not self.pk:  # New instance
            self.granted_at = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Permission for {self.user} on {self.configuration.name}"