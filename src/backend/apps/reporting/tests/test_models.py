"""
Unit tests for the reporting models in the loan management system.

This module contains tests for the ReportConfiguration, SavedReport, ReportSchedule,
ReportDelivery, and ReportPermission models to ensure proper functionality of the
reporting components.
"""

from django.test import TestCase
from unittest.mock import mock, patch
from django.utils import timezone
import json
from django.contrib.auth import get_user_model
from croniter import croniter  # croniter 1.0+

from apps.reporting.models import (
    ReportConfiguration, SavedReport, ReportSchedule, ReportDelivery, ReportPermission,
    REPORT_TYPES, REPORT_STATUS, SCHEDULE_FREQUENCY, DELIVERY_METHOD, DELIVERY_STATUS, EXPORT_FORMATS
)
from utils.storage import S3Storage
from apps.schools.models import School

# Test data for use in tests
TEST_REPORT_CONFIG_DATA = {
    'name': 'Test Report',
    'description': 'Test report configuration',
    'report_type': 'application_volume',
    'parameters': {'date_range': 'last_30_days', 'group_by': 'status'},
    'is_active': True,
}

TEST_SAVED_REPORT_DATA = {
    'report_type': 'application_volume',
    'parameters': {'date_range': 'last_30_days', 'group_by': 'status'},
    'results': {'total': 100, 'by_status': {'approved': 60, 'denied': 20, 'pending': 20}},
    'status': 'completed',
    'file_format': 'csv',
}

TEST_REPORT_SCHEDULE_DATA = {
    'name': 'Daily Application Report',
    'frequency': 'daily',
    'cron_expression': '0 8 * * *',  # 8am every day
    'parameters_override': {'date_range': 'yesterday'},
    'is_active': True,
    'delivery_method': 'email',
    'delivery_config': {
        'recipient_email': 'admin@example.com',
        'subject': 'Daily Application Report',
        'message': 'Please find attached the daily application report.'
    }
}

TEST_REPORT_DELIVERY_DATA = {
    'delivery_method': 'email',
    'delivery_config': {
        'recipient_email': 'admin@example.com',
        'subject': 'Test Report',
        'message': 'Please find attached the requested report.'
    },
    'status': 'pending',
    'retry_count': 0
}


class TestReportConfigurationModel(TestCase):
    """Test case for the ReportConfiguration model"""

    def setUp(self):
        """Set up test data before each test method runs"""
        # Create a test user for auditing
        self.test_user = get_user_model().objects.create(
            username='testuser',
            email='testuser@example.com'
        )
        
        # Create a test school instance
        self.test_school = School.objects.create(
            name='Test School',
            legal_name='Test School Legal Name',
            tax_id='12-3456789',
            address_line1='123 Test St',
            city='Test City',
            state='TX',
            zip_code='12345',
            phone='(123) 456-7890',
            status='active'
        )
        
        # Create a test report configuration instance
        self.report_config = ReportConfiguration.objects.create(
            name=TEST_REPORT_CONFIG_DATA['name'],
            description=TEST_REPORT_CONFIG_DATA['description'],
            report_type=TEST_REPORT_CONFIG_DATA['report_type'],
            parameters=TEST_REPORT_CONFIG_DATA['parameters'],
            is_active=TEST_REPORT_CONFIG_DATA['is_active'],
            school=self.test_school,
            created_by=self.test_user
        )

    def test_report_configuration_creation(self):
        """Test that a report configuration can be created with valid data"""
        # Create a new report configuration
        report_config = ReportConfiguration.objects.create(
            name='Another Test Report',
            report_type='underwriting_metrics',
            parameters={'date_range': 'last_year'},
            is_active=True,
            school=self.test_school,
            created_by=self.test_user
        )
        
        # Verify it was created
        self.assertIsNotNone(report_config.id)
        self.assertEqual(report_config.name, 'Another Test Report')
        self.assertEqual(report_config.report_type, 'underwriting_metrics')
        self.assertEqual(report_config.parameters, {'date_range': 'last_year'})
        self.assertTrue(report_config.is_active)
        self.assertEqual(report_config.school, self.test_school)
        self.assertEqual(report_config.created_by, self.test_user)
        
        # Verify default values
        self.assertIsNone(report_config.description)
        self.assertFalse(report_config.is_deleted)
        self.assertIsNone(report_config.deleted_at)

    def test_report_configuration_string_representation(self):
        """Test the string representation of a ReportConfiguration instance"""
        self.assertEqual(str(self.report_config), TEST_REPORT_CONFIG_DATA['name'])

    def test_get_parameter(self):
        """Test the get_parameter method"""
        # Test getting an existing parameter
        value = self.report_config.get_parameter('date_range')
        self.assertEqual(value, 'last_30_days')
        
        # Test getting a non-existent parameter with default
        value = self.report_config.get_parameter('non_existent', 'default_value')
        self.assertEqual(value, 'default_value')
        
        # Test getting a non-existent parameter without default
        value = self.report_config.get_parameter('non_existent')
        self.assertIsNone(value)
        
        # Test with empty parameters
        report_config = ReportConfiguration.objects.create(
            name='Empty Params Report',
            report_type='application_volume',
            parameters=None,
            created_by=self.test_user
        )
        value = report_config.get_parameter('anything', 'default')
        self.assertEqual(value, 'default')

    def test_set_parameter(self):
        """Test the set_parameter method"""
        # Set a new parameter
        self.report_config.set_parameter('new_param', 'new_value')
        
        # Verify it was added
        self.assertEqual(self.report_config.parameters['new_param'], 'new_value')
        
        # Update an existing parameter
        self.report_config.set_parameter('date_range', 'custom_range')
        
        # Verify it was updated
        self.assertEqual(self.report_config.parameters['date_range'], 'custom_range')
        
        # Test with empty parameters
        report_config = ReportConfiguration.objects.create(
            name='Empty Params Report',
            report_type='application_volume',
            parameters=None,
            created_by=self.test_user
        )
        report_config.set_parameter('param', 'value')
        self.assertEqual(report_config.parameters, {'param': 'value'})

    def test_generate_report(self):
        """Test the generate_report method"""
        # Generate a report without parameter overrides
        report = self.report_config.generate_report(user=self.test_user)
        
        # Verify the report was created correctly
        self.assertIsInstance(report, SavedReport)
        self.assertEqual(report.report_type, self.report_config.report_type)
        self.assertEqual(report.configuration, self.report_config)
        self.assertEqual(report.parameters, self.report_config.parameters)
        self.assertEqual(report.created_by, self.test_user)
        
        # Generate a report with parameter overrides
        overrides = {'date_range': 'custom', 'filter': 'approved'}
        report = self.report_config.generate_report(parameters_override=overrides, user=self.test_user)
        
        # Verify parameters were merged correctly
        self.assertEqual(report.parameters['date_range'], 'custom')  # Override
        self.assertEqual(report.parameters['group_by'], 'status')  # Original
        self.assertEqual(report.parameters['filter'], 'approved')  # New from override

    def test_get_display_name(self):
        """Test the get_display_name method"""
        # Test with known report type
        display_name = self.report_config.get_display_name()
        self.assertEqual(display_name, REPORT_TYPES['application_volume'])
        
        # Test with unknown report type
        report_config = ReportConfiguration.objects.create(
            name='Unknown Type Report',
            report_type='unknown_type',
            created_by=self.test_user
        )
        display_name = report_config.get_display_name()
        self.assertEqual(display_name, 'unknown_type')

    def test_report_configuration_soft_delete(self):
        """Test that soft deleting a report configuration works correctly"""
        # Soft delete the report configuration
        self.report_config.delete()
        
        # Verify it's marked as deleted
        self.assertTrue(self.report_config.is_deleted)
        self.assertIsNotNone(self.report_config.deleted_at)
        
        # Verify it's not in the default queryset
        self.assertFalse(ReportConfiguration.objects.filter(id=self.report_config.id).exists())
        
        # Verify it's still in the all_objects queryset
        self.assertTrue(ReportConfiguration.all_objects.filter(id=self.report_config.id).exists())


class TestSavedReportModel(TestCase):
    """Test case for the SavedReport model"""

    def setUp(self):
        """Set up test data before each test method runs"""
        # Create a test user for auditing
        self.test_user = get_user_model().objects.create(
            username='testuser',
            email='testuser@example.com'
        )
        
        # Create a test school instance
        self.test_school = School.objects.create(
            name='Test School',
            legal_name='Test School Legal Name',
            tax_id='12-3456789',
            address_line1='123 Test St',
            city='Test City',
            state='TX',
            zip_code='12345',
            phone='(123) 456-7890',
            status='active'
        )
        
        # Create a test report configuration instance
        self.report_config = ReportConfiguration.objects.create(
            name=TEST_REPORT_CONFIG_DATA['name'],
            description=TEST_REPORT_CONFIG_DATA['description'],
            report_type=TEST_REPORT_CONFIG_DATA['report_type'],
            parameters=TEST_REPORT_CONFIG_DATA['parameters'],
            is_active=TEST_REPORT_CONFIG_DATA['is_active'],
            school=self.test_school,
            created_by=self.test_user
        )
        
        # Create a test saved report instance
        self.saved_report = SavedReport.objects.create(
            report_type=TEST_SAVED_REPORT_DATA['report_type'],
            configuration=self.report_config,
            parameters=TEST_SAVED_REPORT_DATA['parameters'],
            results=TEST_SAVED_REPORT_DATA['results'],
            status=TEST_SAVED_REPORT_DATA['status'],
            file_format=TEST_SAVED_REPORT_DATA['file_format'],
            created_by=self.test_user
        )

    def test_saved_report_creation(self):
        """Test that a saved report can be created with valid data"""
        # Create a new saved report
        saved_report = SavedReport.objects.create(
            report_type='underwriting_metrics',
            configuration=self.report_config,
            parameters={'date_range': 'last_year'},
            status=REPORT_STATUS['PENDING'],
            created_by=self.test_user
        )
        
        # Verify it was created
        self.assertIsNotNone(saved_report.id)
        self.assertEqual(saved_report.report_type, 'underwriting_metrics')
        self.assertEqual(saved_report.configuration, self.report_config)
        self.assertEqual(saved_report.parameters, {'date_range': 'last_year'})
        self.assertEqual(saved_report.status, REPORT_STATUS['PENDING'])
        self.assertEqual(saved_report.created_by, self.test_user)
        
        # Verify default values
        self.assertIsNone(saved_report.results)
        self.assertIsNone(saved_report.error_message)
        self.assertIsNone(saved_report.file_path)
        self.assertIsNone(saved_report.file_format)
        self.assertIsNone(saved_report.generated_at)
        self.assertIsNone(saved_report.expires_at)

    def test_saved_report_string_representation(self):
        """Test the string representation of a SavedReport instance"""
        expected_string = f"{REPORT_TYPES[self.saved_report.report_type]} - {self.saved_report.status} - {self.saved_report.created_at.strftime('%Y-%m-%d')}"
        self.assertEqual(str(self.saved_report), expected_string)

    def test_update_status(self):
        """Test the update_status method"""
        # Update to a new status
        self.saved_report.update_status(REPORT_STATUS['GENERATING'])
        
        # Verify the status was updated
        self.assertEqual(self.saved_report.status, REPORT_STATUS['GENERATING'])
        self.assertIsNone(self.saved_report.generated_at)
        self.assertIsNone(self.saved_report.expires_at)
        
        # Update to COMPLETED status
        self.saved_report.update_status(REPORT_STATUS['COMPLETED'])
        
        # Verify generated_at and expires_at are set
        self.assertEqual(self.saved_report.status, REPORT_STATUS['COMPLETED'])
        self.assertIsNotNone(self.saved_report.generated_at)
        self.assertIsNotNone(self.saved_report.expires_at)
        
        # Verify expires_at is 30 days after generated_at
        expected_expiry = self.saved_report.generated_at + timezone.timedelta(days=30)
        # Allow for small differences in timestamp due to execution time
        self.assertLess(abs((expected_expiry - self.saved_report.expires_at).total_seconds()), 5)

    def test_set_results(self):
        """Test the set_results method"""
        # Create a report with no results
        report = SavedReport.objects.create(
            report_type='document_status',
            configuration=self.report_config,
            status=REPORT_STATUS['GENERATING'],
            created_by=self.test_user
        )
        
        # Set results and file information
        results = {'total_documents': 500, 'signed': 300, 'pending': 200}
        file_path = 'reports/document_status_123.csv'
        file_format = EXPORT_FORMATS['CSV']
        
        report.set_results(results, file_path, file_format)
        
        # Verify the results and file information were set
        self.assertEqual(report.results, results)
        self.assertEqual(report.file_path, file_path)
        self.assertEqual(report.file_format, file_format)
        
        # Verify status was updated to COMPLETED
        self.assertEqual(report.status, REPORT_STATUS['COMPLETED'])
        self.assertIsNotNone(report.generated_at)
        self.assertIsNotNone(report.expires_at)

    def test_set_error(self):
        """Test the set_error method"""
        # Create a report
        report = SavedReport.objects.create(
            report_type='funding_metrics',
            configuration=self.report_config,
            status=REPORT_STATUS['GENERATING'],
            created_by=self.test_user
        )
        
        # Set an error
        error_message = "Failed to generate report due to missing data"
        report.set_error(error_message)
        
        # Verify the error message was set
        self.assertEqual(report.error_message, error_message)
        
        # Verify status was updated to FAILED
        self.assertEqual(report.status, REPORT_STATUS['FAILED'])

    @patch('utils.storage.S3Storage.get_presigned_url')
    def test_get_download_url(self, mock_get_presigned_url):
        """Test the get_download_url method"""
        # Set up mock
        mock_get_presigned_url.return_value = "https://example.com/download/report.csv"
        
        # Create a report with a file path
        report = SavedReport.objects.create(
            report_type='application_volume',
            configuration=self.report_config,
            file_path='reports/application_volume_123.csv',
            created_by=self.test_user
        )
        
        # Get download URL
        url = report.get_download_url(expiry_seconds=1800)
        
        # Verify mock was called with correct parameters
        mock_get_presigned_url.assert_called_once_with(report.file_path, 1800)
        
        # Verify the returned URL
        self.assertEqual(url, "https://example.com/download/report.csv")
        
        # Test with a report without a file path
        report_no_file = SavedReport.objects.create(
            report_type='application_volume',
            configuration=self.report_config,
            created_by=self.test_user
        )
        
        # Verify exception is raised
        with self.assertRaises(ValueError):
            report_no_file.get_download_url()

    def test_is_expired(self):
        """Test the is_expired method"""
        # Create a report with expires_at in the past
        past_date = timezone.now() - timezone.timedelta(days=1)
        expired_report = SavedReport.objects.create(
            report_type='application_volume',
            configuration=self.report_config,
            status=REPORT_STATUS['COMPLETED'],
            expires_at=past_date,
            created_by=self.test_user
        )
        
        # Verify it's expired
        self.assertTrue(expired_report.is_expired())
        
        # Create a report with expires_at in the future
        future_date = timezone.now() + timezone.timedelta(days=1)
        active_report = SavedReport.objects.create(
            report_type='application_volume',
            configuration=self.report_config,
            status=REPORT_STATUS['COMPLETED'],
            expires_at=future_date,
            created_by=self.test_user
        )
        
        # Verify it's not expired
        self.assertFalse(active_report.is_expired())
        
        # Create a report without expires_at
        no_expiry_report = SavedReport.objects.create(
            report_type='application_volume',
            configuration=self.report_config,
            created_by=self.test_user
        )
        
        # Verify it's not considered expired
        self.assertFalse(no_expiry_report.is_expired())

    def test_saved_report_soft_delete(self):
        """Test that soft deleting a saved report works correctly"""
        # Soft delete the saved report
        self.saved_report.delete()
        
        # Verify it's marked as deleted
        self.assertTrue(self.saved_report.is_deleted)
        self.assertIsNotNone(self.saved_report.deleted_at)
        
        # Verify it's not in the default queryset
        self.assertFalse(SavedReport.objects.filter(id=self.saved_report.id).exists())
        
        # Verify it's still in the all_objects queryset
        self.assertTrue(SavedReport.all_objects.filter(id=self.saved_report.id).exists())


class TestReportScheduleModel(TestCase):
    """Test case for the ReportSchedule model"""

    def setUp(self):
        """Set up test data before each test method runs"""
        # Create a test user for auditing
        self.test_user = get_user_model().objects.create(
            username='testuser',
            email='testuser@example.com'
        )
        
        # Create a test school instance
        self.test_school = School.objects.create(
            name='Test School',
            legal_name='Test School Legal Name',
            tax_id='12-3456789',
            address_line1='123 Test St',
            city='Test City',
            state='TX',
            zip_code='12345',
            phone='(123) 456-7890',
            status='active'
        )
        
        # Create a test report configuration instance
        self.report_config = ReportConfiguration.objects.create(
            name=TEST_REPORT_CONFIG_DATA['name'],
            description=TEST_REPORT_CONFIG_DATA['description'],
            report_type=TEST_REPORT_CONFIG_DATA['report_type'],
            parameters=TEST_REPORT_CONFIG_DATA['parameters'],
            is_active=TEST_REPORT_CONFIG_DATA['is_active'],
            school=self.test_school,
            created_by=self.test_user
        )
        
        # Create a test report schedule instance
        self.report_schedule = ReportSchedule.objects.create(
            name=TEST_REPORT_SCHEDULE_DATA['name'],
            configuration=self.report_config,
            frequency=TEST_REPORT_SCHEDULE_DATA['frequency'],
            cron_expression=TEST_REPORT_SCHEDULE_DATA['cron_expression'],
            parameters_override=TEST_REPORT_SCHEDULE_DATA['parameters_override'],
            is_active=TEST_REPORT_SCHEDULE_DATA['is_active'],
            delivery_method=TEST_REPORT_SCHEDULE_DATA['delivery_method'],
            delivery_config=TEST_REPORT_SCHEDULE_DATA['delivery_config'],
            created_by=self.test_user
        )

    def test_report_schedule_creation(self):
        """Test that a report schedule can be created with valid data"""
        # Create a new report schedule
        report_schedule = ReportSchedule.objects.create(
            name='Weekly Underwriting Report',
            configuration=self.report_config,
            frequency=SCHEDULE_FREQUENCY['WEEKLY'],
            is_active=True,
            created_by=self.test_user
        )
        
        # Verify it was created
        self.assertIsNotNone(report_schedule.id)
        self.assertEqual(report_schedule.name, 'Weekly Underwriting Report')
        self.assertEqual(report_schedule.configuration, self.report_config)
        self.assertEqual(report_schedule.frequency, SCHEDULE_FREQUENCY['WEEKLY'])
        self.assertTrue(report_schedule.is_active)
        self.assertEqual(report_schedule.created_by, self.test_user)
        
        # Verify default values
        self.assertIsNone(report_schedule.cron_expression)
        self.assertIsNone(report_schedule.parameters_override)
        self.assertIsNone(report_schedule.next_run)
        self.assertIsNone(report_schedule.last_run)
        self.assertIsNone(report_schedule.delivery_method)
        self.assertIsNone(report_schedule.delivery_config)

    def test_report_schedule_string_representation(self):
        """Test the string representation of a ReportSchedule instance"""
        expected_string = f"{self.report_schedule.name} - {self.report_schedule.frequency}"
        self.assertEqual(str(self.report_schedule), expected_string)

    def test_calculate_next_run_daily(self):
        """Test the calculate_next_run method with daily frequency"""
        # Create a schedule with daily frequency
        schedule = ReportSchedule.objects.create(
            name='Daily Test Schedule',
            configuration=self.report_config,
            frequency=SCHEDULE_FREQUENCY['DAILY'],
            created_by=self.test_user
        )
        
        # Set a reference time
        reference_time = timezone.now()
        
        # Calculate the next run time
        next_run = schedule.calculate_next_run(reference_time)
        
        # Verify it's 24 hours after the reference time
        expected_time = reference_time + timezone.timedelta(days=1)
        # Allow for small differences in timestamp due to execution time
        self.assertLess(abs((expected_time - next_run).total_seconds()), 5)

    def test_calculate_next_run_weekly(self):
        """Test the calculate_next_run method with weekly frequency"""
        # Create a schedule with weekly frequency
        schedule = ReportSchedule.objects.create(
            name='Weekly Test Schedule',
            configuration=self.report_config,
            frequency=SCHEDULE_FREQUENCY['WEEKLY'],
            created_by=self.test_user
        )
        
        # Set a reference time
        reference_time = timezone.now()
        
        # Calculate the next run time
        next_run = schedule.calculate_next_run(reference_time)
        
        # Verify it's 7 days after the reference time
        expected_time = reference_time + timezone.timedelta(days=7)
        # Allow for small differences in timestamp due to execution time
        self.assertLess(abs((expected_time - next_run).total_seconds()), 5)

    def test_calculate_next_run_monthly(self):
        """Test the calculate_next_run method with monthly frequency"""
        # Create a schedule with monthly frequency
        schedule = ReportSchedule.objects.create(
            name='Monthly Test Schedule',
            configuration=self.report_config,
            frequency=SCHEDULE_FREQUENCY['MONTHLY'],
            created_by=self.test_user
        )
        
        # Set a reference time
        reference_time = timezone.now()
        
        # Calculate the next run time
        next_run = schedule.calculate_next_run(reference_time)
        
        # Verify it's in the next month on the same day
        # This is a bit more complex due to different month lengths
        if reference_time.month == 12:
            expected_month = 1
            expected_year = reference_time.year + 1
        else:
            expected_month = reference_time.month + 1
            expected_year = reference_time.year
            
        self.assertEqual(next_run.year, expected_year)
        self.assertEqual(next_run.month, expected_month)
        # Day might be adjusted for month length
        # (e.g., Jan 31 -> Feb 28/29)
        # so we don't assert exact day equality

    def test_calculate_next_run_custom(self):
        """Test the calculate_next_run method with custom frequency (cron expression)"""
        # Create a schedule with custom frequency and cron expression
        schedule = ReportSchedule.objects.create(
            name='Custom Test Schedule',
            configuration=self.report_config,
            frequency=SCHEDULE_FREQUENCY['CUSTOM'],
            cron_expression='0 9 * * 1',  # 9am every Monday
            created_by=self.test_user
        )
        
        # Set a reference time (assuming it's not Monday 9am)
        reference_time = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)
        
        # Calculate the next run time
        next_run = schedule.calculate_next_run(reference_time)
        
        # Verify using croniter
        expected_next_run = croniter(schedule.cron_expression, reference_time).get_next(timezone.datetime)
        # Allow for timezone differences
        self.assertEqual(next_run.strftime('%Y-%m-%d %H:%M'), expected_next_run.strftime('%Y-%m-%d %H:%M'))

    @patch('apps.reporting.models.ReportConfiguration.generate_report')
    def test_execute(self, mock_generate_report):
        """Test the execute method"""
        # Set up mock
        mock_report = mock.MagicMock()
        mock_generate_report.return_value = mock_report
        
        # Execute the schedule
        result = self.report_schedule.execute()
        
        # Verify generate_report was called with correct parameters
        mock_generate_report.assert_called_once_with(
            parameters_override=self.report_schedule.parameters_override,
            user=self.report_schedule.created_by
        )
        
        # Verify the report was returned
        self.assertEqual(result, mock_report)
        
        # Verify last_run and next_run were updated
        self.assertIsNotNone(self.report_schedule.last_run)
        self.assertIsNotNone(self.report_schedule.next_run)
        self.assertGreater(self.report_schedule.next_run, self.report_schedule.last_run)

    def test_is_due(self):
        """Test the is_due method"""
        # Create a schedule due for execution (active with next_run in the past)
        past_time = timezone.now() - timezone.timedelta(hours=1)
        due_schedule = ReportSchedule.objects.create(
            name='Due Schedule',
            configuration=self.report_config,
            frequency=SCHEDULE_FREQUENCY['DAILY'],
            is_active=True,
            next_run=past_time,
            created_by=self.test_user
        )
        
        # Verify it's due
        self.assertTrue(due_schedule.is_due())
        
        # Create a schedule not due yet (active with next_run in the future)
        future_time = timezone.now() + timezone.timedelta(hours=1)
        not_due_schedule = ReportSchedule.objects.create(
            name='Not Due Schedule',
            configuration=self.report_config,
            frequency=SCHEDULE_FREQUENCY['DAILY'],
            is_active=True,
            next_run=future_time,
            created_by=self.test_user
        )
        
        # Verify it's not due
        self.assertFalse(not_due_schedule.is_due())
        
        # Create an inactive schedule with next_run in the past
        inactive_schedule = ReportSchedule.objects.create(
            name='Inactive Schedule',
            configuration=self.report_config,
            frequency=SCHEDULE_FREQUENCY['DAILY'],
            is_active=False,
            next_run=past_time,
            created_by=self.test_user
        )
        
        # Verify it's not due because it's inactive
        self.assertFalse(inactive_schedule.is_due())
        
        # Test a schedule with no next_run set
        no_next_run_schedule = ReportSchedule.objects.create(
            name='No Next Run Schedule',
            configuration=self.report_config,
            frequency=SCHEDULE_FREQUENCY['DAILY'],
            is_active=True,
            created_by=self.test_user
        )
        
        # Verify it's not due because next_run is None
        self.assertFalse(no_next_run_schedule.is_due())

    def test_report_schedule_soft_delete(self):
        """Test that soft deleting a report schedule works correctly"""
        # Soft delete the report schedule
        self.report_schedule.delete()
        
        # Verify it's marked as deleted
        self.assertTrue(self.report_schedule.is_deleted)
        self.assertIsNotNone(self.report_schedule.deleted_at)
        
        # Verify it's not in the default queryset
        self.assertFalse(ReportSchedule.objects.filter(id=self.report_schedule.id).exists())
        
        # Verify it's still in the all_objects queryset
        self.assertTrue(ReportSchedule.all_objects.filter(id=self.report_schedule.id).exists())


class TestReportDeliveryModel(TestCase):
    """Test case for the ReportDelivery model"""

    def setUp(self):
        """Set up test data before each test method runs"""
        # Create a test user for auditing
        self.test_user = get_user_model().objects.create(
            username='testuser',
            email='testuser@example.com'
        )
        
        # Create a test school instance
        self.test_school = School.objects.create(
            name='Test School',
            legal_name='Test School Legal Name',
            tax_id='12-3456789',
            address_line1='123 Test St',
            city='Test City',
            state='TX',
            zip_code='12345',
            phone='(123) 456-7890',
            status='active'
        )
        
        # Create a test report configuration instance
        self.report_config = ReportConfiguration.objects.create(
            name=TEST_REPORT_CONFIG_DATA['name'],
            description=TEST_REPORT_CONFIG_DATA['description'],
            report_type=TEST_REPORT_CONFIG_DATA['report_type'],
            parameters=TEST_REPORT_CONFIG_DATA['parameters'],
            is_active=TEST_REPORT_CONFIG_DATA['is_active'],
            school=self.test_school,
            created_by=self.test_user
        )
        
        # Create a test saved report instance
        self.saved_report = SavedReport.objects.create(
            report_type=TEST_SAVED_REPORT_DATA['report_type'],
            configuration=self.report_config,
            parameters=TEST_SAVED_REPORT_DATA['parameters'],
            results=TEST_SAVED_REPORT_DATA['results'],
            status=REPORT_STATUS['COMPLETED'],
            file_path='reports/test_report.csv',
            file_format=TEST_SAVED_REPORT_DATA['file_format'],
            created_by=self.test_user
        )
        
        # Create a test report delivery instance
        self.report_delivery = ReportDelivery.objects.create(
            report=self.saved_report,
            delivery_method=TEST_REPORT_DELIVERY_DATA['delivery_method'],
            delivery_config=TEST_REPORT_DELIVERY_DATA['delivery_config'],
            status=TEST_REPORT_DELIVERY_DATA['status'],
            retry_count=TEST_REPORT_DELIVERY_DATA['retry_count'],
            created_by=self.test_user
        )

    def test_report_delivery_creation(self):
        """Test that a report delivery can be created with valid data"""
        # Create a new report delivery
        report_delivery = ReportDelivery.objects.create(
            report=self.saved_report,
            delivery_method=DELIVERY_METHOD['S3'],
            delivery_config={'bucket_name': 'reports-bucket', 'key_prefix': 'exports/'},
            status=DELIVERY_STATUS['PENDING'],
            created_by=self.test_user
        )
        
        # Verify it was created
        self.assertIsNotNone(report_delivery.id)
        self.assertEqual(report_delivery.report, self.saved_report)
        self.assertEqual(report_delivery.delivery_method, DELIVERY_METHOD['S3'])
        self.assertEqual(report_delivery.delivery_config, {'bucket_name': 'reports-bucket', 'key_prefix': 'exports/'})
        self.assertEqual(report_delivery.status, DELIVERY_STATUS['PENDING'])
        self.assertEqual(report_delivery.created_by, self.test_user)
        
        # Verify default values
        self.assertIsNone(report_delivery.error_message)
        self.assertIsNone(report_delivery.delivered_at)
        self.assertEqual(report_delivery.retry_count, 0)
        self.assertIsNone(report_delivery.last_retry_at)

    def test_report_delivery_string_representation(self):
        """Test the string representation of a ReportDelivery instance"""
        expected_string = f"Delivery of report {self.saved_report.id} via {self.report_delivery.delivery_method} - {self.report_delivery.status}"
        self.assertEqual(str(self.report_delivery), expected_string)

    @patch('apps.reporting.models.ReportDelivery._deliver_email')
    def test_deliver_email(self, mock_deliver_email):
        """Test the deliver method with email delivery method"""
        # Setup mock
        mock_deliver_email.return_value = True
        
        # Call deliver
        result = self.report_delivery.deliver()
        
        # Verify _deliver_email was called
        mock_deliver_email.assert_called_once()
        
        # Verify delivery status was updated
        self.assertEqual(self.report_delivery.status, DELIVERY_STATUS['DELIVERED'])
        self.assertIsNotNone(self.report_delivery.delivered_at)
        
        # Verify result
        self.assertTrue(result)

    @patch('apps.reporting.models.ReportDelivery._deliver_s3')
    def test_deliver_s3(self, mock_deliver_s3):
        """Test the deliver method with S3 delivery method"""
        # Create a report delivery with S3 method
        s3_delivery = ReportDelivery.objects.create(
            report=self.saved_report,
            delivery_method=DELIVERY_METHOD['S3'],
            delivery_config={'bucket_name': 'reports-bucket', 'key_prefix': 'exports/'},
            created_by=self.test_user
        )
        
        # Setup mock
        mock_deliver_s3.return_value = True
        
        # Call deliver
        result = s3_delivery.deliver()
        
        # Verify _deliver_s3 was called
        mock_deliver_s3.assert_called_once()
        
        # Verify delivery status was updated
        self.assertEqual(s3_delivery.status, DELIVERY_STATUS['DELIVERED'])
        self.assertIsNotNone(s3_delivery.delivered_at)
        
        # Verify result
        self.assertTrue(result)

    @patch('apps.reporting.models.ReportDelivery._deliver_sftp')
    def test_deliver_sftp(self, mock_deliver_sftp):
        """Test the deliver method with SFTP delivery method"""
        # Create a report delivery with SFTP method
        sftp_delivery = ReportDelivery.objects.create(
            report=self.saved_report,
            delivery_method=DELIVERY_METHOD['SFTP'],
            delivery_config={
                'host': 'sftp.example.com',
                'port': 22,
                'username': 'user',
                'password': 'pass',
                'path': '/reports/'
            },
            created_by=self.test_user
        )
        
        # Setup mock
        mock_deliver_sftp.return_value = True
        
        # Call deliver
        result = sftp_delivery.deliver()
        
        # Verify _deliver_sftp was called
        mock_deliver_sftp.assert_called_once()
        
        # Verify delivery status was updated
        self.assertEqual(sftp_delivery.status, DELIVERY_STATUS['DELIVERED'])
        self.assertIsNotNone(sftp_delivery.delivered_at)
        
        # Verify result
        self.assertTrue(result)

    @patch('apps.reporting.models.ReportDelivery._deliver_email')
    def test_deliver_failure(self, mock_deliver_email):
        """Test the deliver method when delivery fails"""
        # Setup mock to return False (delivery failure)
        mock_deliver_email.return_value = False
        
        # Call deliver
        result = self.report_delivery.deliver()
        
        # Verify _deliver_email was called
        mock_deliver_email.assert_called_once()
        
        # Verify delivery status was updated to FAILED
        self.assertEqual(self.report_delivery.status, DELIVERY_STATUS['FAILED'])
        self.assertIsNotNone(self.report_delivery.error_message)
        
        # Verify result
        self.assertFalse(result)

    @patch('apps.reporting.models.ReportDelivery.deliver')
    def test_retry(self, mock_deliver):
        """Test the retry method"""
        # Setup a failed delivery
        self.report_delivery.status = DELIVERY_STATUS['FAILED']
        self.report_delivery.error_message = "Previous delivery attempt failed"
        self.report_delivery.save()
        
        # Setup mock
        mock_deliver.return_value = True
        
        # Call retry
        result = self.report_delivery.retry()
        
        # Verify retry_count was incremented
        self.assertEqual(self.report_delivery.retry_count, 1)
        self.assertIsNotNone(self.report_delivery.last_retry_at)
        
        # Verify deliver was called
        mock_deliver.assert_called_once()
        
        # Verify result is the same as deliver result
        self.assertEqual(result, mock_deliver.return_value)
        
        # Test retry on a delivery that's not in FAILED status
        self.report_delivery.status = DELIVERY_STATUS['DELIVERED']
        self.report_delivery.save()
        mock_deliver.reset_mock()
        
        result = self.report_delivery.retry()
        
        # Verify deliver was not called
        mock_deliver.assert_not_called()
        
        # Verify result is False
        self.assertFalse(result)

    def test_deliver_email_implementation(self):
        """Test the _deliver_email method implementation"""
        # This is more complex to test since it involves email sending
        # For unit testing, we'll focus on the method's behavior with valid config
        
        # Mock actual email sending (since we don't want to send real emails in tests)
        with patch('apps.reporting.models.logger.info') as mock_logger:
            # Call _deliver_email
            result = self.report_delivery._deliver_email()
            
            # Verify that the logger was called (simulates successful email sending)
            mock_logger.assert_called()
            
            # Verify result
            self.assertTrue(result)
            
            # Test with invalid config (missing recipient)
            invalid_config_delivery = ReportDelivery.objects.create(
                report=self.saved_report,
                delivery_method=DELIVERY_METHOD['EMAIL'],
                delivery_config={
                    'subject': 'Test Report',
                    'message': 'Please find attached the requested report.'
                },
                created_by=self.test_user
            )
            
            result = invalid_config_delivery._deliver_email()
            
            # Verify result
            self.assertFalse(result)
            self.assertIsNotNone(invalid_config_delivery.error_message)

    def test_deliver_s3_implementation(self):
        """Test the _deliver_s3 method implementation"""
        # Create a delivery with S3 config
        s3_delivery = ReportDelivery.objects.create(
            report=self.saved_report,
            delivery_method=DELIVERY_METHOD['S3'],
            delivery_config={
                'bucket_name': 'reports-bucket',
                'key_prefix': 'exports/'
            },
            created_by=self.test_user
        )
        
        # Mock S3Storage.retrieve and actual S3 upload
        with patch('utils.storage.S3Storage.retrieve') as mock_retrieve, \
             patch('apps.reporting.models.logger.info') as mock_logger:
            
            # Setup mock
            mock_retrieve.return_value = (b'file content', 'text/csv', {})
            
            # Call _deliver_s3
            result = s3_delivery._deliver_s3()
            
            # Verify that the logger was called (simulates successful S3 upload)
            mock_logger.assert_called()
            
            # Verify result
            self.assertTrue(result)
            
            # Test with invalid config (missing bucket name)
            invalid_config_delivery = ReportDelivery.objects.create(
                report=self.saved_report,
                delivery_method=DELIVERY_METHOD['S3'],
                delivery_config={
                    'key_prefix': 'exports/'
                },
                created_by=self.test_user
            )
            
            result = invalid_config_delivery._deliver_s3()
            
            # Verify result
            self.assertFalse(result)
            self.assertIsNotNone(invalid_config_delivery.error_message)

    def test_deliver_sftp_implementation(self):
        """Test the _deliver_sftp method implementation"""
        # Create a delivery with SFTP config
        sftp_delivery = ReportDelivery.objects.create(
            report=self.saved_report,
            delivery_method=DELIVERY_METHOD['SFTP'],
            delivery_config={
                'host': 'sftp.example.com',
                'port': 22,
                'username': 'user',
                'password': 'pass',
                'path': '/reports/'
            },
            created_by=self.test_user
        )
        
        # Mock S3Storage.retrieve and actual SFTP connection/upload
        with patch('utils.storage.S3Storage.retrieve') as mock_retrieve, \
             patch('apps.reporting.models.logger.info') as mock_logger:
            
            # Setup mock
            mock_retrieve.return_value = (b'file content', 'text/csv', {})
            
            # Call _deliver_sftp
            result = sftp_delivery._deliver_sftp()
            
            # Verify that the logger was called (simulates successful SFTP upload)
            mock_logger.assert_called()
            
            # Verify result
            self.assertTrue(result)
            
            # Test with invalid config (missing host)
            invalid_config_delivery = ReportDelivery.objects.create(
                report=self.saved_report,
                delivery_method=DELIVERY_METHOD['SFTP'],
                delivery_config={
                    'port': 22,
                    'username': 'user',
                    'password': 'pass',
                    'path': '/reports/'
                },
                created_by=self.test_user
            )
            
            result = invalid_config_delivery._deliver_sftp()
            
            # Verify result
            self.assertFalse(result)
            self.assertIsNotNone(invalid_config_delivery.error_message)

    def test_report_delivery_soft_delete(self):
        """Test that soft deleting a report delivery works correctly"""
        # Soft delete the report delivery
        self.report_delivery.delete()
        
        # Verify it's marked as deleted
        self.assertTrue(self.report_delivery.is_deleted)
        self.assertIsNotNone(self.report_delivery.deleted_at)
        
        # Verify it's not in the default queryset
        self.assertFalse(ReportDelivery.objects.filter(id=self.report_delivery.id).exists())
        
        # Verify it's still in the all_objects queryset
        self.assertTrue(ReportDelivery.all_objects.filter(id=self.report_delivery.id).exists())


class TestReportPermissionModel(TestCase):
    """Test case for the ReportPermission model"""

    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test users for permission testing
        self.admin_user = get_user_model().objects.create(
            username='adminuser',
            email='admin@example.com'
        )
        
        self.regular_user = get_user_model().objects.create(
            username='regularuser',
            email='user@example.com'
        )
        
        # Create a test school instance
        self.test_school = School.objects.create(
            name='Test School',
            legal_name='Test School Legal Name',
            tax_id='12-3456789',
            address_line1='123 Test St',
            city='Test City',
            state='TX',
            zip_code='12345',
            phone='(123) 456-7890',
            status='active'
        )
        
        # Create a test report configuration instance
        self.report_config = ReportConfiguration.objects.create(
            name=TEST_REPORT_CONFIG_DATA['name'],
            description=TEST_REPORT_CONFIG_DATA['description'],
            report_type=TEST_REPORT_CONFIG_DATA['report_type'],
            parameters=TEST_REPORT_CONFIG_DATA['parameters'],
            is_active=TEST_REPORT_CONFIG_DATA['is_active'],
            school=self.test_school,
            created_by=self.admin_user
        )

    def test_report_permission_creation(self):
        """Test that a report permission can be created with valid data"""
        # Create a new report permission
        report_permission = ReportPermission.objects.create(
            configuration=self.report_config,
            user=self.regular_user,
            can_view=True,
            can_generate=True,
            can_schedule=False,
            can_export=True,
            granted_by=self.admin_user
        )
        
        # Verify it was created
        self.assertIsNotNone(report_permission.id)
        self.assertEqual(report_permission.configuration, self.report_config)
        self.assertEqual(report_permission.user, self.regular_user)
        self.assertTrue(report_permission.can_view)
        self.assertTrue(report_permission.can_generate)
        self.assertFalse(report_permission.can_schedule)
        self.assertTrue(report_permission.can_export)
        self.assertEqual(report_permission.granted_by, self.admin_user)
        
        # Verify granted_at is set
        self.assertIsNotNone(report_permission.granted_at)

    def test_report_permission_string_representation(self):
        """Test the string representation of a ReportPermission instance"""
        # Create a report permission
        report_permission = ReportPermission.objects.create(
            configuration=self.report_config,
            user=self.regular_user,
            granted_by=self.admin_user
        )
        
        expected_string = f"Permission for {self.regular_user} on {self.report_config.name}"
        self.assertEqual(str(report_permission), expected_string)

    def test_save_method_sets_granted_at(self):
        """Test that the save method sets granted_at for new instances"""
        # Create a new report permission
        report_permission = ReportPermission.objects.create(
            configuration=self.report_config,
            user=self.regular_user,
            granted_by=self.admin_user
        )
        
        # Verify granted_at is set
        self.assertIsNotNone(report_permission.granted_at)
        
        # Store the current granted_at value
        original_granted_at = report_permission.granted_at
        
        # Wait a moment to ensure any timestamp would be different
        import time
        time.sleep(0.1)
        
        # Update the permission
        report_permission.can_generate = True
        report_permission.save()
        
        # Verify granted_at is not changed
        self.assertEqual(report_permission.granted_at, original_granted_at)

    def test_report_permission_soft_delete(self):
        """Test that soft deleting a report permission works correctly"""
        # Create a report permission
        report_permission = ReportPermission.objects.create(
            configuration=self.report_config,
            user=self.regular_user,
            granted_by=self.admin_user
        )
        
        # Soft delete the report permission
        report_permission.delete()
        
        # Verify it's marked as deleted
        self.assertTrue(report_permission.is_deleted)
        self.assertIsNotNone(report_permission.deleted_at)
        
        # Verify it's not in the default queryset
        self.assertFalse(ReportPermission.objects.filter(id=report_permission.id).exists())
        
        # Verify it's still in the all_objects queryset
        self.assertTrue(ReportPermission.all_objects.filter(id=report_permission.id).exists())