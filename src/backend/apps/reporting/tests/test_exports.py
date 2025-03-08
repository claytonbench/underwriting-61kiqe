import unittest
from unittest.mock import patch, Mock, MagicMock
import tempfile
import os
import json
import datetime
import io
import pandas as pd

from ..exports import (
    ReportExporter, 
    ExportError, 
    EXPORT_FORMATS, 
    EXPORT_CONTENT_TYPES
)
from ..models import SavedReport, REPORT_TYPES, REPORT_STATUS
from ...utils.storage import S3Storage, StorageError

# Test constants
TEST_BUCKET_NAME = "test-loan-management-exports"
TEST_REGION = "us-east-1"

# Helper functions for test data creation
def create_test_report(report_type, results=None):
    """Helper function to create a test report with sample data"""
    report = Mock(spec=SavedReport)
    report.id = "test-report-id"
    report.report_type = report_type
    report.status = REPORT_STATUS['COMPLETED']
    
    if results is None:
        if report_type == 'application_volume':
            results = get_sample_application_volume_data()
        elif report_type == 'underwriting_metrics':
            results = get_sample_underwriting_metrics_data()
        elif report_type == 'document_status':
            results = get_sample_document_status_data()
        elif report_type == 'funding_metrics':
            results = get_sample_funding_metrics_data()
        else:
            results = {"sample": "data"}
    
    report.results = results
    return report

def get_sample_application_volume_data():
    """Helper function to generate sample application volume report data"""
    return {
        "status_distribution": {
            "Approved": 65,
            "Denied": 15,
            "Revised": 12,
            "Pending": 8
        },
        "daily_volume": {
            "2023-05-01": 8,
            "2023-05-02": 10,
            "2023-05-03": 13,
            "2023-05-04": 16
        },
        "results": [
            {"Date": "2023-05-01", "New Applications": 8, "Approved": 5, "Denied": 2, "Pending": 1},
            {"Date": "2023-05-02", "New Applications": 10, "Approved": 7, "Denied": 1, "Pending": 2},
            {"Date": "2023-05-03", "New Applications": 13, "Approved": 9, "Denied": 3, "Pending": 1},
            {"Date": "2023-05-04", "New Applications": 16, "Approved": 12, "Denied": 2, "Pending": 2}
        ]
    }

def get_sample_underwriting_metrics_data():
    """Helper function to generate sample underwriting metrics report data"""
    return {
        "approval_rate": 82,
        "average_decision_time": 1.2,
        "decisions_by_underwriter": {
            "Robert Taylor": 45,
            "Jane Smith": 38,
            "David Johnson": 42
        },
        "results": [
            {"Underwriter": "Robert Taylor", "Applications Processed": 45, "Approval Rate": 0.84, "Average Decision Time": 1.1},
            {"Underwriter": "Jane Smith", "Applications Processed": 38, "Approval Rate": 0.79, "Average Decision Time": 1.3},
            {"Underwriter": "David Johnson", "Applications Processed": 42, "Approval Rate": 0.83, "Average Decision Time": 1.2}
        ]
    }

def get_sample_document_status_data():
    """Helper function to generate sample document status report data"""
    return {
        "completion_rate": 78,
        "average_signing_time": 2.5,
        "documents_by_status": {
            "Completed": 78,
            "Partially Signed": 15,
            "Pending": 7
        },
        "results": [
            {"Document Type": "Loan Agreement", "Completed": 85, "Partially Signed": 10, "Pending": 5, "Completion Rate": 0.85},
            {"Document Type": "Disclosure Forms", "Completed": 90, "Partially Signed": 5, "Pending": 5, "Completion Rate": 0.90},
            {"Document Type": "Promissory Notes", "Completed": 75, "Partially Signed": 20, "Pending": 5, "Completion Rate": 0.75}
        ]
    }

def get_sample_funding_metrics_data():
    """Helper function to generate sample funding metrics report data"""
    return {
        "total_disbursement": 1250000,
        "average_funding_time": 1.5,
        "disbursements_by_school": {
            "ABC School": 500000,
            "XYZ Academy": 350000,
            "Tech Institute": 400000
        },
        "results": [
            {"School": "ABC School", "Disbursement Amount": 500000, "Applications Funded": 45, "Average Funding Time": 1.3},
            {"School": "XYZ Academy", "Disbursement Amount": 350000, "Applications Funded": 28, "Average Funding Time": 1.7},
            {"School": "Tech Institute", "Disbursement Amount": 400000, "Applications Funded": 32, "Average Funding Time": 1.5}
        ]
    }


class TestExportError(unittest.TestCase):
    """Test case for the ExportError class"""
    
    def test_export_error_initialization(self):
        """Test that ExportError is initialized correctly"""
        original_error = ValueError("Sample error")
        error = ExportError("Test error message", original_error)
        
        self.assertEqual(error.message, "Test error message")
        self.assertEqual(error.original_exception, original_error)
        self.assertIn("Test error message", str(error))
        self.assertIn("Sample error", str(error))


class TestReportExporter(unittest.TestCase):
    """Test case for the ReportExporter class"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.exporter = ReportExporter(bucket_name=TEST_BUCKET_NAME, region=TEST_REGION)
        
        # Sample reports
        self.application_report = create_test_report('application_volume')
        self.underwriting_report = create_test_report('underwriting_metrics')
        self.document_report = create_test_report('document_status')
        self.funding_report = create_test_report('funding_metrics')
        
        # Patch S3Storage
        self.s3_storage_patch = patch('src.backend.apps.reporting.exports.S3Storage')
        self.mock_s3_storage = self.s3_storage_patch.start()
        self.mock_s3_storage_instance = Mock()
        self.mock_s3_storage.return_value = self.mock_s3_storage_instance
        
        # Patch internal export methods
        self.export_csv_patch = patch.object(ReportExporter, '_export_to_csv')
        self.mock_export_csv = self.export_csv_patch.start()
        
        self.export_excel_patch = patch.object(ReportExporter, '_export_to_excel')
        self.mock_export_excel = self.export_excel_patch.start()
        
        self.export_pdf_patch = patch.object(ReportExporter, '_export_to_pdf')
        self.mock_export_pdf = self.export_pdf_patch.start()
        
        self.export_json_patch = patch.object(ReportExporter, '_export_to_json')
        self.mock_export_json = self.export_json_patch.start()
    
    def tearDown(self):
        """Clean up test environment after each test"""
        self.s3_storage_patch.stop()
        self.export_csv_patch.stop()
        self.export_excel_patch.stop()
        self.export_pdf_patch.stop()
        self.export_json_patch.stop()
    
    def test_initialization(self):
        """Test that ReportExporter initializes correctly"""
        # Test with custom bucket and region
        exporter = ReportExporter(bucket_name="custom-bucket", region="us-west-2")
        self.assertEqual(exporter._bucket_name, "custom-bucket")
        self.assertEqual(exporter._region, "us-west-2")
        self.mock_s3_storage.assert_called_with(bucket_name="custom-bucket", region_name="us-west-2")
        
        # Test with default values
        with patch('src.backend.apps.reporting.exports.EXPORT_BUCKET_NAME', 'default-bucket'):
            with patch('src.backend.apps.reporting.exports.EXPORT_REGION', 'default-region'):
                exporter = ReportExporter()
                self.assertEqual(exporter._bucket_name, "default-bucket")
                self.assertEqual(exporter._region, "default-region")
    
    def test_export_report_csv(self):
        """Test exporting a report to CSV format"""
        # Mock the internal methods
        csv_content = b"sample,csv,content"
        csv_filename = "test_report.csv"
        self.mock_export_csv.return_value = (csv_content, csv_filename)
        
        # Mock S3Storage.store
        self.mock_s3_storage_instance.store.return_value = {
            'key': 'reports/test-report-id/test_report.csv',
            'url': 's3://test-bucket/reports/test-report-id/test_report.csv',
            'version_id': '123'
        }
        
        # Call export_report
        result = self.exporter.export_report(self.application_report, 'csv')
        
        # Verify calls
        self.mock_export_csv.assert_called_once_with(self.application_report.results, 'application-volume')
        self.mock_s3_storage_instance.store.assert_called_once_with(
            csv_content,
            'reports/test-report-id/test_report.csv',
            content_type='text/csv',
            encrypt=True,
            metadata={
                'report_id': 'test-report-id',
                'report_type': 'application_volume',
                'export_format': 'csv',
                'exported_at': unittest.mock.ANY
            }
        )
        
        # Verify report was updated
        self.application_report.file_path = 'reports/test-report-id/test_report.csv'
        self.application_report.file_format = 'csv'
        self.application_report.save.assert_called_once()
        
        # Verify result
        self.assertEqual(result['file_path'], 'reports/test-report-id/test_report.csv')
        self.assertEqual(result['file_format'], 'csv')
        self.assertEqual(result['content_type'], 'text/csv')
        self.assertEqual(result['filename'], 'test_report.csv')
    
    def test_export_report_excel(self):
        """Test exporting a report to Excel format"""
        # Mock the internal methods
        excel_content = b"sample excel content"
        excel_filename = "test_report.xlsx"
        self.mock_export_excel.return_value = (excel_content, excel_filename)
        
        # Mock S3Storage.store
        self.mock_s3_storage_instance.store.return_value = {
            'key': 'reports/test-report-id/test_report.xlsx',
            'url': 's3://test-bucket/reports/test-report-id/test_report.xlsx',
            'version_id': '123'
        }
        
        # Call export_report
        result = self.exporter.export_report(self.application_report, 'xlsx')
        
        # Verify calls
        self.mock_export_excel.assert_called_once_with(self.application_report.results, 'application-volume')
        self.mock_s3_storage_instance.store.assert_called_once_with(
            excel_content,
            'reports/test-report-id/test_report.xlsx',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            encrypt=True,
            metadata={
                'report_id': 'test-report-id',
                'report_type': 'application_volume',
                'export_format': 'xlsx',
                'exported_at': unittest.mock.ANY
            }
        )
        
        # Verify report was updated
        self.application_report.file_path = 'reports/test-report-id/test_report.xlsx'
        self.application_report.file_format = 'xlsx'
        self.application_report.save.assert_called_once()
        
        # Verify result
        self.assertEqual(result['file_path'], 'reports/test-report-id/test_report.xlsx')
        self.assertEqual(result['file_format'], 'xlsx')
        self.assertEqual(result['content_type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertEqual(result['filename'], 'test_report.xlsx')
    
    def test_export_report_pdf(self):
        """Test exporting a report to PDF format"""
        # Mock the internal methods
        pdf_content = b"%PDF-1.4 sample pdf content"
        pdf_filename = "test_report.pdf"
        self.mock_export_pdf.return_value = (pdf_content, pdf_filename)
        
        # Mock S3Storage.store
        self.mock_s3_storage_instance.store.return_value = {
            'key': 'reports/test-report-id/test_report.pdf',
            'url': 's3://test-bucket/reports/test-report-id/test_report.pdf',
            'version_id': '123'
        }
        
        # Call export_report
        result = self.exporter.export_report(self.application_report, 'pdf')
        
        # Verify calls
        self.mock_export_pdf.assert_called_once_with(self.application_report.results, 'application-volume')
        self.mock_s3_storage_instance.store.assert_called_once_with(
            pdf_content,
            'reports/test-report-id/test_report.pdf',
            content_type='application/pdf',
            encrypt=True,
            metadata={
                'report_id': 'test-report-id',
                'report_type': 'application_volume',
                'export_format': 'pdf',
                'exported_at': unittest.mock.ANY
            }
        )
        
        # Verify report was updated
        self.application_report.file_path = 'reports/test-report-id/test_report.pdf'
        self.application_report.file_format = 'pdf'
        self.application_report.save.assert_called_once()
        
        # Verify result
        self.assertEqual(result['file_path'], 'reports/test-report-id/test_report.pdf')
        self.assertEqual(result['file_format'], 'pdf')
        self.assertEqual(result['content_type'], 'application/pdf')
        self.assertEqual(result['filename'], 'test_report.pdf')
    
    def test_export_report_json(self):
        """Test exporting a report to JSON format"""
        # Mock the internal methods
        json_content = b'{"sample": "json content"}'
        json_filename = "test_report.json"
        self.mock_export_json.return_value = (json_content, json_filename)
        
        # Mock S3Storage.store
        self.mock_s3_storage_instance.store.return_value = {
            'key': 'reports/test-report-id/test_report.json',
            'url': 's3://test-bucket/reports/test-report-id/test_report.json',
            'version_id': '123'
        }
        
        # Call export_report
        result = self.exporter.export_report(self.application_report, 'json')
        
        # Verify calls
        self.mock_export_json.assert_called_once_with(self.application_report.results, 'application-volume')
        self.mock_s3_storage_instance.store.assert_called_once_with(
            json_content,
            'reports/test-report-id/test_report.json',
            content_type='application/json',
            encrypt=True,
            metadata={
                'report_id': 'test-report-id',
                'report_type': 'application_volume',
                'export_format': 'json',
                'exported_at': unittest.mock.ANY
            }
        )
        
        # Verify report was updated
        self.application_report.file_path = 'reports/test-report-id/test_report.json'
        self.application_report.file_format = 'json'
        self.application_report.save.assert_called_once()
        
        # Verify result
        self.assertEqual(result['file_path'], 'reports/test-report-id/test_report.json')
        self.assertEqual(result['file_format'], 'json')
        self.assertEqual(result['content_type'], 'application/json')
        self.assertEqual(result['filename'], 'test_report.json')
    
    def test_export_report_invalid_format(self):
        """Test that exporting with an invalid format raises an error"""
        with self.assertRaises(ExportError) as context:
            self.exporter.export_report(self.application_report, 'invalid_format')
        
        self.assertIn("Invalid export format", str(context.exception))
    
    def test_export_report_invalid_status(self):
        """Test that exporting a report with invalid status raises an error"""
        report = create_test_report('application_volume')
        report.status = REPORT_STATUS['PENDING']
        
        with self.assertRaises(ExportError) as context:
            self.exporter.export_report(report, 'csv')
        
        self.assertIn("Cannot export report that is not in 'completed' status", str(context.exception))
    
    def test_export_report_storage_error(self):
        """Test handling of storage errors during export"""
        # Mock the internal methods
        csv_content = b"sample,csv,content"
        csv_filename = "test_report.csv"
        self.mock_export_csv.return_value = (csv_content, csv_filename)
        
        # Mock S3Storage.store to raise a StorageError
        storage_error = StorageError("Storage error occurred")
        self.mock_s3_storage_instance.store.side_effect = storage_error
        
        # Call export_report and verify exception
        with self.assertRaises(ExportError) as context:
            self.exporter.export_report(self.application_report, 'csv')
        
        # Verify exception details
        self.assertIn("Failed to store exported report", str(context.exception))
        self.assertEqual(context.exception.original_exception, storage_error)
    
    def test_get_download_url(self):
        """Test generating a download URL for a report file"""
        # Mock S3Storage.get_presigned_url
        expected_url = "https://loan-management-exports.s3.amazonaws.com/reports/test-report-id/test_report.csv"
        self.mock_s3_storage_instance.get_presigned_url.return_value = expected_url
        
        # Call get_download_url
        file_path = "reports/test-report-id/test_report.csv"
        url = self.exporter.get_download_url(file_path)
        
        # Verify calls
        self.mock_s3_storage_instance.get_presigned_url.assert_called_once_with(
            file_path, 
            expiration=3600
        )
        
        # Verify result
        self.assertEqual(url, expected_url)
    
    def test_get_download_url_with_expiry(self):
        """Test generating a download URL with custom expiry time"""
        # Mock S3Storage.get_presigned_url
        expected_url = "https://loan-management-exports.s3.amazonaws.com/reports/test-report-id/test_report.csv"
        self.mock_s3_storage_instance.get_presigned_url.return_value = expected_url
        
        # Call get_download_url with custom expiry
        file_path = "reports/test-report-id/test_report.csv"
        expiry_seconds = 7200  # 2 hours
        url = self.exporter.get_download_url(file_path, expiry_seconds)
        
        # Verify calls
        self.mock_s3_storage_instance.get_presigned_url.assert_called_once_with(
            file_path, 
            expiration=expiry_seconds
        )
        
        # Verify result
        self.assertEqual(url, expected_url)
    
    def test_get_download_url_empty_path(self):
        """Test that get_download_url with empty path raises an error"""
        with self.assertRaises(ExportError) as context:
            self.exporter.get_download_url("")
        
        self.assertIn("File path is required", str(context.exception))
    
    def test_get_download_url_storage_error(self):
        """Test handling of storage errors during URL generation"""
        # Mock S3Storage.get_presigned_url to raise a StorageError
        storage_error = StorageError("Storage error occurred")
        self.mock_s3_storage_instance.get_presigned_url.side_effect = storage_error
        
        # Call get_download_url and verify exception
        with self.assertRaises(ExportError) as context:
            self.exporter.get_download_url("reports/test-report-id/test_report.csv")
        
        # Verify exception details
        self.assertIn("Failed to generate download URL", str(context.exception))
        self.assertEqual(context.exception.original_exception, storage_error)
    
    def test_export_to_csv(self):
        """Test the internal _export_to_csv method"""
        self.export_csv_patch.stop()  # Stop the patch for this test
        
        # Create sample data
        data = get_sample_application_volume_data()
        
        # Call the method directly
        content, filename = self.exporter._export_to_csv(data, 'application-volume')
        
        # Verify the result
        self.assertIsInstance(content, bytes)
        self.assertTrue(filename.startswith('application-volume_'))
        self.assertTrue(filename.endswith('.csv'))
        
        # Check content can be parsed as a CSV
        csv_data = pd.read_csv(io.BytesIO(content))
        self.assertEqual(len(csv_data), len(data['results']))
        
        # Restart the patch
        self.mock_export_csv = self.export_csv_patch.start()
    
    def test_export_to_excel(self):
        """Test the internal _export_to_excel method"""
        self.export_excel_patch.stop()  # Stop the patch for this test
        
        # Create sample data
        data = get_sample_application_volume_data()
        
        # Call the method directly
        content, filename = self.exporter._export_to_excel(data, 'application-volume')
        
        # Verify the result
        self.assertIsInstance(content, bytes)
        self.assertTrue(filename.startswith('application-volume_'))
        self.assertTrue(filename.endswith('.xlsx'))
        
        # Check content can be parsed as an Excel file
        excel_data = pd.read_excel(io.BytesIO(content))
        self.assertEqual(len(excel_data), len(data['results']))
        
        # Restart the patch
        self.mock_export_excel = self.export_excel_patch.start()
    
    def test_export_to_pdf(self):
        """Test the internal _export_to_pdf method"""
        self.export_pdf_patch.stop()  # Stop the patch for this test
        
        # Create patches for dependencies
        with patch('src.backend.apps.reporting.exports.HTML') as mock_html, \
             patch('src.backend.apps.reporting.exports.Environment') as mock_env, \
             patch('src.backend.apps.reporting.exports.FileSystemLoader') as mock_loader, \
             patch('os.path.exists') as mock_exists, \
             patch('os.path.join', return_value='/path/to/templates') as mock_join:
            
            # Configure mocks
            mock_exists.return_value = True  # Template exists
            
            mock_template = Mock()
            mock_env_instance = Mock()
            mock_env.return_value = mock_env_instance
            mock_env_instance.get_template.return_value = mock_template
            mock_template.render.return_value = "<html><body>Test</body></html>"
            
            mock_html_instance = Mock()
            mock_html.return_value = mock_html_instance
            mock_html_instance.write_pdf.return_value = b"%PDF-1.4 test content"
            
            # Create sample data
            data = get_sample_application_volume_data()
            
            # Call the method directly
            content, filename = self.exporter._export_to_pdf(data, 'application-volume')
            
            # Verify the result
            self.assertIsInstance(content, bytes)
            self.assertTrue(filename.startswith('application-volume_'))
            self.assertTrue(filename.endswith('.pdf'))
            self.assertTrue(content.startswith(b"%PDF"))
            
            # Verify template selection
            mock_exists.assert_called_with('/path/to/templates/application-volume.html')
            
            # Verify the HTML rendering was called correctly
            mock_template.render.assert_called_once()
            mock_html.assert_called_once_with(string=unittest.mock.ANY)
            mock_html_instance.write_pdf.assert_called_once()
        
        # Restart the patch
        self.mock_export_pdf = self.export_pdf_patch.start()
    
    def test_export_to_json(self):
        """Test the internal _export_to_json method"""
        self.export_json_patch.stop()  # Stop the patch for this test
        
        # Create sample data
        data = get_sample_application_volume_data()
        
        # Call the method directly
        content, filename = self.exporter._export_to_json(data, 'application-volume')
        
        # Verify the result
        self.assertIsInstance(content, bytes)
        self.assertTrue(filename.startswith('application-volume_'))
        self.assertTrue(filename.endswith('.json'))
        
        # Check content can be parsed as JSON
        json_data = json.loads(content.decode('utf-8'))
        self.assertEqual(json_data['data'], data)
        self.assertEqual(json_data['report_type'], 'application-volume')
        
        # Restart the patch
        self.mock_export_json = self.export_json_patch.start()
    
    def test_prepare_dataframe(self):
        """Test the internal _prepare_dataframe method"""
        # Create sample data with tabular data
        data = get_sample_application_volume_data()
        
        # Call the method directly
        df = self.exporter._prepare_dataframe(data)
        
        # Verify the result
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), len(data['results']))
        
        # Check column names are properly formatted
        for col in df.columns:
            self.assertTrue(col.istitle())
            self.assertFalse('_' in col)
    
    def test_format_dataframe(self):
        """Test the internal _format_dataframe method"""
        # Create a sample DataFrame
        data = {
            'Amount': [1000.50, 2000.75, 3000.25],
            'Rate': [0.0525, 0.0625, 0.0725],
            'Date': ['2023-05-01', '2023-05-02', '2023-05-03']
        }
        df = pd.DataFrame(data)
        
        # Create format specifications
        format_specs = {
            'Amount': 'currency',
            'Rate': 'percentage',
            'Date': 'date'
        }
        
        # Call the method directly
        formatted_df = self.exporter._format_dataframe(df, format_specs)
        
        # Verify the result
        self.assertEqual(formatted_df['Amount'][0], '$1,000.50')
        self.assertEqual(formatted_df['Rate'][0], '5.25%')
        self.assertEqual(formatted_df['Date'][0], '2023-05-01')
    
    def test_format_dataframe_with_empty_values(self):
        """Test the internal _format_dataframe method with empty values"""
        # Create a sample DataFrame with None/NaN values
        data = {
            'Amount': [1000.50, None, 3000.25],
            'Rate': [0.0525, 0.0625, None],
            'Date': ['2023-05-01', None, '2023-05-03']
        }
        df = pd.DataFrame(data)
        
        # Create format specifications
        format_specs = {
            'Amount': 'currency',
            'Rate': 'percentage',
            'Date': 'date',
            'NonExistentColumn': 'currency'  # Column that doesn't exist
        }
        
        # Call the method directly
        formatted_df = self.exporter._format_dataframe(df, format_specs)
        
        # Verify the result
        self.assertEqual(formatted_df['Amount'][0], '$1,000.50')
        self.assertEqual(formatted_df['Amount'][1], '')  # None should be formatted as empty string
        self.assertEqual(formatted_df['Rate'][0], '5.25%')
        self.assertEqual(formatted_df['Rate'][2], '')  # None should be formatted as empty string
        self.assertEqual(formatted_df['Date'][0], '2023-05-01')
        self.assertEqual(formatted_df['Date'][1], '')  # None should be formatted as empty string
    
    def test_generate_filename(self):
        """Test the internal _generate_filename method"""
        # Call the method
        filename = self.exporter._generate_filename('application-volume', 'csv')
        
        # Verify the result
        self.assertTrue(filename.startswith('application-volume_'))
        self.assertTrue(filename.endswith('.csv'))
        
        # Check format
        parts = filename.split('_')
        self.assertEqual(len(parts), 3)
        
        # Check timestamp format
        timestamp = parts[1]
        self.assertEqual(len(timestamp), 15)  # YYYYMMDD_HHMMSS
        
        # Check UUID part
        uuid_part = parts[2].split('.')[0]
        self.assertEqual(len(uuid_part), 8)
    
    def test_get_report_title(self):
        """Test the internal _get_report_title method"""
        # Test known report types
        self.assertEqual(self.exporter._get_report_title('application-volume'), 'Application Volume Report')
        self.assertEqual(self.exporter._get_report_title('underwriting-metrics'), 'Underwriting Metrics Report')
        
        # Test unknown report type
        self.assertEqual(self.exporter._get_report_title('unknown-report'), 'Unknown Report Report')