"""
Module for exporting report data to various formats in the loan management system.

This module provides functionality for exporting report data to CSV, Excel, PDF, and JSON formats,
as well as managing the export process, storing exported files, and generating download URLs.
"""

import os  # standard library
import tempfile  # standard library
import json  # standard library
import csv  # standard library
import datetime  # standard library
import uuid  # standard library

import pandas as pd  # pandas 2.1+
from openpyxl.utils import get_column_letter  # openpyxl 3.1+
from weasyprint import HTML  # weasyprint 59.0+
from jinja2 import Environment, FileSystemLoader  # jinja2 3.1+

from ...utils.storage import S3Storage, StorageError
from ...utils.logging import logger
from ...utils.formatters import format_currency, format_date, format_percentage
from ..reporting.models import EXPORT_FORMATS, SavedReport

# Content types for exported files
EXPORT_CONTENT_TYPES = {
    'csv': 'text/csv',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'pdf': 'application/pdf',
    'json': 'application/json'
}

# S3 bucket configuration for export storage
EXPORT_BUCKET_NAME = os.environ.get('EXPORT_BUCKET_NAME', 'loan-management-exports')
EXPORT_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Default URL expiry time in seconds (1 hour)
DEFAULT_EXPIRY_SECONDS = 3600


class ExportError(Exception):
    """
    Custom exception class for export-related errors.
    
    This exception provides context about export failures, including references to
    the original exception that caused the error.
    """
    
    def __init__(self, message, original_exception=None):
        """
        Initialize the ExportError with a message and original exception.
        
        Args:
            message: Human-readable error message
            original_exception: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception
        logger.error(f"Export error: {message}", exc_info=original_exception)
    
    def __str__(self):
        """Returns a string representation of the error."""
        if self.original_exception:
            return f"{self.message} (Original error: {str(self.original_exception)})"
        return self.message


class ReportExporter:
    """
    Class that handles exporting report data to various formats.
    
    This class provides methods for exporting report data to CSV, Excel, PDF, and JSON formats,
    as well as storing the exported files and generating download URLs.
    """
    
    def __init__(self, bucket_name=None, region=None):
        """
        Initialize the ReportExporter with storage configuration.
        
        Args:
            bucket_name: S3 bucket name for storing exports (default: from environment)
            region: AWS region for the S3 bucket (default: from environment)
        """
        self._bucket_name = bucket_name or EXPORT_BUCKET_NAME
        self._region = region or EXPORT_REGION
        self._storage = S3Storage(bucket_name=self._bucket_name, region_name=self._region)
        logger.info(f"Initialized ReportExporter with bucket: {self._bucket_name}, region: {self._region}")
    
    def export_report(self, report, export_format):
        """
        Exports a report to the specified format.
        
        Args:
            report: The report to export
            export_format: Format to export the report to (csv, xlsx, pdf, json)
            
        Returns:
            Dictionary containing export details including file path and content type
            
        Raises:
            ExportError: If export fails for any reason
        """
        try:
            # Validate report status
            if report.status != 'completed':
                raise ExportError(f"Cannot export report that is not in 'completed' status (current: {report.status})")
            
            # Validate export format
            if export_format not in EXPORT_FORMATS.values():
                valid_formats = ", ".join(EXPORT_FORMATS.values())
                raise ExportError(f"Invalid export format: {export_format}. Valid formats: {valid_formats}")
            
            # Get report results
            results = report.results
            if not results:
                raise ExportError("Report has no results to export")
            
            # Determine report type for filename and template selection
            report_type = report.report_type.replace("_", "-")
            
            # Export to specified format
            if export_format == 'csv':
                content, filename = self._export_to_csv(results, report_type)
            elif export_format == 'xlsx':
                content, filename = self._export_to_excel(results, report_type)
            elif export_format == 'pdf':
                content, filename = self._export_to_pdf(results, report_type)
            elif export_format == 'json':
                content, filename = self._export_to_json(results, report_type)
            else:
                # This should not happen due to validation above, but as a safeguard
                raise ExportError(f"Unsupported export format: {export_format}")
            
            # Store file in S3
            file_path = f"reports/{report.id}/{filename}"
            
            # Store the file in S3
            result = self._storage.store(
                content,
                file_path,
                content_type=EXPORT_CONTENT_TYPES.get(export_format),
                encrypt=True,
                metadata={
                    'report_id': str(report.id),
                    'report_type': report.report_type,
                    'export_format': export_format,
                    'exported_at': datetime.datetime.now().isoformat()
                }
            )
            
            # Update report with file path and format
            report.file_path = file_path
            report.file_format = export_format
            report.save()
            
            logger.info(f"Successfully exported report {report.id} to {export_format} format")
            
            # Return export details
            return {
                'file_path': file_path,
                'file_format': export_format,
                'content_type': EXPORT_CONTENT_TYPES.get(export_format),
                'filename': filename
            }
        
        except StorageError as e:
            # Wrap storage errors
            raise ExportError(f"Failed to store exported report: {str(e)}", e)
        except Exception as e:
            # Catch all other exceptions
            raise ExportError(f"Failed to export report: {str(e)}", e)
    
    def get_download_url(self, file_path, expiry_seconds=None):
        """
        Generates a download URL for a previously exported report.
        
        Args:
            file_path: Path to the exported file in S3
            expiry_seconds: URL expiration time in seconds (default: DEFAULT_EXPIRY_SECONDS)
            
        Returns:
            Presigned URL for downloading the report
            
        Raises:
            ExportError: If URL generation fails
        """
        try:
            if not file_path:
                raise ExportError("File path is required to generate download URL")
            
            # Use default expiry if not specified
            if expiry_seconds is None:
                expiry_seconds = DEFAULT_EXPIRY_SECONDS
            
            # Generate presigned URL
            url = self._storage.get_presigned_url(file_path, expiration=expiry_seconds)
            logger.info(f"Generated download URL for {file_path} with expiration {expiry_seconds}s")
            
            return url
        
        except StorageError as e:
            # Wrap storage errors
            raise ExportError(f"Failed to generate download URL: {str(e)}", e)
        except Exception as e:
            # Catch all other exceptions
            raise ExportError(f"Failed to generate download URL: {str(e)}", e)
    
    def _export_to_csv(self, data, report_type):
        """
        Exports report data to CSV format.
        
        Args:
            data: Report data to export
            report_type: Type of report for filename generation
            
        Returns:
            Tuple containing file content (bytes) and filename
            
        Raises:
            ExportError: If CSV export fails
        """
        try:
            # Prepare data as DataFrame
            df = self._prepare_dataframe(data)
            
            # Apply appropriate formatting
            format_specs = self._get_format_specifications(report_type)
            df = self._format_dataframe(df, format_specs)
            
            # Create a temporary file to write the CSV
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
                try:
                    # Write DataFrame to CSV
                    df.to_csv(temp_file.name, index=False, quoting=csv.QUOTE_MINIMAL)
                    
                    # Read the file content
                    with open(temp_file.name, 'rb') as f:
                        content = f.read()
                    
                    # Generate filename
                    filename = self._generate_filename(report_type, 'csv')
                    
                    return content, filename
                
                finally:
                    # Ensure the temporary file is removed
                    try:
                        os.unlink(temp_file.name)
                    except Exception as e:
                        logger.warning(f"Failed to remove temporary file {temp_file.name}: {str(e)}")
        
        except Exception as e:
            raise ExportError(f"Failed to export to CSV: {str(e)}", e)
    
    def _export_to_excel(self, data, report_type):
        """
        Exports report data to Excel format.
        
        Args:
            data: Report data to export
            report_type: Type of report for filename generation
            
        Returns:
            Tuple containing file content (bytes) and filename
            
        Raises:
            ExportError: If Excel export fails
        """
        try:
            # Prepare data as DataFrame
            df = self._prepare_dataframe(data)
            
            # Apply appropriate formatting
            format_specs = self._get_format_specifications(report_type)
            df = self._format_dataframe(df, format_specs)
            
            # Create a temporary file to write the Excel
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
                try:
                    # Create Excel writer
                    with pd.ExcelWriter(temp_file.name, engine='openpyxl') as writer:
                        # Write DataFrame to Excel
                        df.to_excel(writer, sheet_name=self._get_report_title(report_type), index=False)
                        
                        # Get the worksheet
                        worksheet = writer.sheets[self._get_report_title(report_type)]
                        
                        # Format column widths (auto-adjust based on content)
                        for column in worksheet.columns:
                            max_length = 0
                            column_letter = get_column_letter(column[0].column)
                            for cell in column:
                                if cell.value:
                                    cell_length = len(str(cell.value))
                                    max_length = max(max_length, cell_length)
                            adjusted_width = max_length + 2  # Add some padding
                            worksheet.column_dimensions[column_letter].width = adjusted_width
                        
                        # Add header formatting
                        for cell in worksheet[1]:
                            cell.font = cell.font.copy(bold=True)
                    
                    # Read the file content
                    with open(temp_file.name, 'rb') as f:
                        content = f.read()
                    
                    # Generate filename
                    filename = self._generate_filename(report_type, 'xlsx')
                    
                    return content, filename
                
                finally:
                    # Ensure the temporary file is removed
                    try:
                        os.unlink(temp_file.name)
                    except Exception as e:
                        logger.warning(f"Failed to remove temporary file {temp_file.name}: {str(e)}")
        
        except Exception as e:
            raise ExportError(f"Failed to export to Excel: {str(e)}", e)
    
    def _export_to_pdf(self, data, report_type):
        """
        Exports report data to PDF format.
        
        Args:
            data: Report data to export
            report_type: Type of report for filename generation and template selection
            
        Returns:
            Tuple containing file content (bytes) and filename
            
        Raises:
            ExportError: If PDF export fails
        """
        try:
            # Get the base directory for templates
            template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'pdf')
            
            # Set up Jinja2 environment
            env = Environment(loader=FileSystemLoader(template_dir))
            
            # Select appropriate template based on report type
            template_name = f"{report_type}.html"
            if not os.path.exists(os.path.join(template_dir, template_name)):
                # Fallback to generic template if specific one doesn't exist
                template_name = "generic_report.html"
            
            # Get the template
            template = env.get_template(template_name)
            
            # Prepare data for template
            template_data = {
                'report_title': self._get_report_title(report_type),
                'generated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data': data
            }
            
            # Render the template
            html_content = template.render(**template_data)
            
            # Convert HTML to PDF
            pdf_content = HTML(string=html_content).write_pdf()
            
            # Generate filename
            filename = self._generate_filename(report_type, 'pdf')
            
            return pdf_content, filename
        
        except Exception as e:
            raise ExportError(f"Failed to export to PDF: {str(e)}", e)
    
    def _export_to_json(self, data, report_type):
        """
        Exports report data to JSON format.
        
        Args:
            data: Report data to export
            report_type: Type of report for filename generation
            
        Returns:
            Tuple containing file content (bytes) and filename
            
        Raises:
            ExportError: If JSON export fails
        """
        try:
            # Prepare data for JSON serialization
            json_data = {
                'report_type': report_type,
                'generated_at': datetime.datetime.now().isoformat(),
                'data': data
            }
            
            # Convert to JSON string with proper formatting
            json_content = json.dumps(json_data, indent=2, sort_keys=True, default=str)
            
            # Convert to bytes
            content = json_content.encode('utf-8')
            
            # Generate filename
            filename = self._generate_filename(report_type, 'json')
            
            return content, filename
        
        except Exception as e:
            raise ExportError(f"Failed to export to JSON: {str(e)}", e)
    
    def _prepare_dataframe(self, data):
        """
        Prepares a pandas DataFrame from report data.
        
        Args:
            data: Report data
            
        Returns:
            DataFrame prepared from report data
            
        Raises:
            ExportError: If DataFrame preparation fails
        """
        try:
            # Extract data for DataFrame based on report structure
            if 'results' in data:
                df_data = data['results']
            elif 'items' in data:
                df_data = data['items']
            elif 'data' in data:
                df_data = data['data']
            else:
                # If no clear data structure, use the entire data
                df_data = data
            
            # Convert to DataFrame
            if isinstance(df_data, list):
                df = pd.DataFrame(df_data)
            elif isinstance(df_data, dict):
                # Handle various dictionary structures
                if any(isinstance(v, list) for v in df_data.values()):
                    # Find the first list value and use it
                    for key, value in df_data.items():
                        if isinstance(value, list):
                            df = pd.DataFrame(value)
                            break
                    else:
                        # Fallback if no list found
                        df = pd.DataFrame([df_data])
                else:
                    # Simple key-value pairs
                    df = pd.DataFrame([df_data])
            else:
                # Fallback for other data types
                df = pd.DataFrame([df_data])
            
            # Apply column renaming for readability if needed
            # This would typically be customized based on the report type
            df.columns = [col.replace('_', ' ').title() for col in df.columns]
            
            return df
        
        except Exception as e:
            raise ExportError(f"Failed to prepare DataFrame: {str(e)}", e)
    
    def _format_dataframe(self, df, format_specs):
        """
        Applies formatting to DataFrame columns based on data types.
        
        Args:
            df: DataFrame to format
            format_specs: Dictionary mapping column names to format types
            
        Returns:
            Formatted DataFrame
        """
        # Create a copy to avoid modifying the original
        formatted_df = df.copy()
        
        # Apply formatting based on format specifications
        for column, format_type in format_specs.items():
            if column in formatted_df.columns:
                if format_type == 'currency':
                    formatted_df[column] = formatted_df[column].apply(
                        lambda x: format_currency(x) if pd.notna(x) else '')
                elif format_type == 'date':
                    formatted_df[column] = formatted_df[column].apply(
                        lambda x: format_date(x) if pd.notna(x) else '')
                elif format_type == 'percentage':
                    formatted_df[column] = formatted_df[column].apply(
                        lambda x: format_percentage(x) if pd.notna(x) else '')
        
        return formatted_df
    
    def _get_format_specifications(self, report_type):
        """
        Gets format specifications for a specific report type.
        
        Args:
            report_type: Type of report
            
        Returns:
            Dictionary mapping column names to format types
        """
        # Define formatting specifications for different report types
        # This would be customized based on the report types in your system
        common_formats = {
            'Amount': 'currency',
            'Balance': 'currency',
            'Total': 'currency',
            'Average': 'currency',
            'Rate': 'percentage',
            'Date': 'date',
            'Created At': 'date',
            'Updated At': 'date',
            'Submission Date': 'date',
            'Approval Date': 'date',
            'Funding Date': 'date'
        }
        
        # Add report-specific format specifications
        if report_type == 'application-volume':
            return {
                **common_formats,
                'Approval Rate': 'percentage',
                'Conversion Rate': 'percentage'
            }
        elif report_type == 'underwriting-metrics':
            return {
                **common_formats,
                'Approval Rate': 'percentage',
                'Denial Rate': 'percentage',
                'Average Credit Score': 'integer'
            }
        elif report_type == 'funding-metrics':
            return {
                **common_formats,
                'Disbursement Amount': 'currency',
                'Average Funding Time': 'number'
            }
        elif report_type == 'document-status':
            return {
                **common_formats,
                'Completion Rate': 'percentage'
            }
        
        # Default format specifications
        return common_formats
    
    def _generate_filename(self, report_type, extension):
        """
        Generates a unique filename for an exported report.
        
        Args:
            report_type: Type of report
            extension: File extension
            
        Returns:
            Generated filename
        """
        # Get current timestamp in a file-friendly format
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Generate a UUID for uniqueness
        unique_id = str(uuid.uuid4())[:8]
        
        # Generate the filename
        filename = f"{report_type}_{timestamp}_{unique_id}.{extension}"
        
        return filename
    
    def _get_report_title(self, report_type):
        """
        Gets a human-readable title for a report type.
        
        Args:
            report_type: Type of report
            
        Returns:
            Human-readable report title
        """
        # Convert hyphenated report type to title case with spaces
        report_title = report_type.replace('-', ' ').title()
        
        # Add "Report" suffix if not already present
        if not report_title.endswith(' Report'):
            report_title += ' Report'
        
        return report_title