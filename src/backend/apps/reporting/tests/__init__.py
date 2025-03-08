"""
Test package for the reporting application.

This package contains tests for the reporting functionality, including
report generation, data export capabilities, and dashboard components.

It also provides shared test utilities and fixtures for creating test data
and validating report outputs.
"""

# Shared test utilities and fixtures can be defined here and imported in test modules

def create_test_report_data(report_type="application_status", num_records=10):
    """
    Create sample data for testing reports.
    
    This utility function generates predictable test data for various report types,
    making it easier to write assertions in tests.
    
    Args:
        report_type (str): Type of report data to generate. Options include:
            - "application_status": Application status distribution data
            - "funding_timeline": Loan funding timeline data
            - "school_performance": School performance metrics
        num_records (int): Number of records to generate
        
    Returns:
        dict: Dictionary containing test data structured for the specified report type
    """
    if report_type == "application_status":
        return {
            "submitted": int(num_records * 0.3),
            "in_review": int(num_records * 0.2),
            "approved": int(num_records * 0.3),
            "denied": int(num_records * 0.1),
            "funded": int(num_records * 0.1),
        }
    elif report_type == "funding_timeline":
        return {
            "avg_days_to_decision": 2.5,
            "avg_days_to_documents": 1.2,
            "avg_days_to_funding": 3.8,
            "total_applications": num_records,
        }
    elif report_type == "school_performance":
        return {
            "schools": [
                {
                    "name": f"Test School {i}",
                    "applications": int(num_records / 5),
                    "approval_rate": 0.7 + (i / 10),
                    "funding_volume": 10000 * (i + 1),
                }
                for i in range(5)
            ]
        }
    
    return {}

def assert_report_format(report_data, expected_keys):
    """
    Helper function to assert that a report contains the expected keys/structure.
    
    Args:
        report_data (dict): The report data to validate
        expected_keys (list): List of keys that should be present in the report
        
    Returns:
        bool: True if report has all expected keys
        
    Raises:
        AssertionError: If any expected keys are missing
    """
    for key in expected_keys:
        assert key in report_data, f"Report missing expected key: {key}"
    return True