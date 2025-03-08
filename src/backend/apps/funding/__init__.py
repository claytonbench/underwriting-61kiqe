from .apps import FundingConfig  # Import the Django app configuration class for the funding app
from .models import FundingRequest, Disbursement, EnrollmentVerification, StipulationVerification, FundingNote  # Import the FundingRequest model for direct access from the app package
from .services import FundingService  # Import the FundingService class for direct access from the app package


default_app_config = "src.backend.apps.funding.apps.FundingConfig"  # Define the default Django app configuration path for automatic discovery


__all__ = [  # Define the public API of the funding app
    'FundingConfig',  # Export the Django app configuration for the funding app
    'FundingRequest',  # Export the FundingRequest model for direct import by other modules
    'Disbursement',  # Export the Disbursement model for direct import by other modules
    'EnrollmentVerification',  # Export the EnrollmentVerification model for direct import by other modules
    'StipulationVerification',  # Export the StipulationVerification model for direct import by other modules
    'FundingNote',  # Export the FundingNote model for direct import by other modules
    'FundingService',  # Export the FundingService class for direct import by other modules
    'default_app_config'  # Define the default Django app configuration path for automatic discovery
]