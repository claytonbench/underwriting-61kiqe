"""
Initializes the reporting module for the loan management system, exposing key report generators,
export functionality, and report types. This file serves as the entry point for the reporting
package, making essential components available to other parts of the application.
"""

from .reports.application_volume import ApplicationVolumeReport  # Import the report generator for application volume metrics
from .reports.document_status import DocumentStatusReport  # Import the report generator for document status metrics
from .reports.funding_metrics import FundingMetricsReport  # Import the report generator for funding metrics
from .reports.underwriting_metrics import UnderwritingMetricsReport  # Import the report generator for underwriting metrics
from .exports import ReportExporter, EXPORT_FORMATS  # Import the report exporter class for exporting reports to various formats
from .models import ReportConfiguration, SavedReport, ReportSchedule, ReportDelivery  # Import the model for report configurations

# Define report type constants
REPORT_TYPES = {
    'APPLICATION_VOLUME': 'application_volume',
    'DOCUMENT_STATUS': 'document_status',
    'FUNDING_METRICS': 'funding_metrics',
    'UNDERWRITING_METRICS': 'underwriting_metrics'
}

# Registry mapping report types to their generator classes
REPORT_REGISTRY = {
    'application_volume': ApplicationVolumeReport,
    'document_status': DocumentStatusReport,
    'funding_metrics': FundingMetricsReport,
    'underwriting_metrics': UnderwritingMetricsReport
}


def get_report_generator(report_type: str):
    """
    Returns the appropriate report generator class based on the report type

    Args:
        report_type (str): The report type

    Returns:
        class: Report generator class or None if not found
    """
    if report_type in REPORT_REGISTRY:
        return REPORT_REGISTRY[report_type]
    else:
        return None


def get_available_report_types() -> list:
    """
    Returns a list of all available report types

    Returns:
        list: List of available report type identifiers
    """
    return list(REPORT_REGISTRY.keys())