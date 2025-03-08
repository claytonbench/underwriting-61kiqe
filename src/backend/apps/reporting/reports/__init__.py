"""
Initializes the reporting reports package and exports the report classes for the loan management system.
This file serves as the entry point for all report generators, making them accessible throughout the application.
"""

from .application_volume import ApplicationVolumeReport  # Import the ApplicationVolumeReport class for generating application volume reports
from .document_status import DocumentStatusReport  # Import the DocumentStatusReport class for generating document status reports
from .funding_metrics import FundingMetricsReport  # Import the FundingMetricsReport class for generating funding metrics reports
from .underwriting_metrics import UnderwritingMetricsReport  # Import the UnderwritingMetricsReport class for generating underwriting metrics reports


REPORT_GENERATORS = {
    'application_volume': ApplicationVolumeReport,
    'document_status': DocumentStatusReport,
    'funding_metrics': FundingMetricsReport,
    'underwriting_metrics': UnderwritingMetricsReport
}


def get_report_generator(report_type: str):
    """
    Factory function that returns the appropriate report generator class based on report type

    Args:
        report_type (str): Report type identifier

    Returns:
        class: Report generator class or None if not found
    """
    return REPORT_GENERATORS.get(report_type)