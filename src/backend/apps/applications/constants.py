"""
Constants specific to the loan application module.

This module defines application-specific constants including application types,
status groups, relationship types, validation requirements, and financial thresholds.
These constants are used throughout the application module to enforce business rules,
validate data, and control application flow.
"""

from decimal import Decimal  # standard library

from ...utils.constants import (  # v3.11+
    APPLICATION_STATUS,
    MINIMUM_LOAN_AMOUNT,
    MAXIMUM_LOAN_AMOUNT,
    MINIMUM_INCOME,
    MINIMUM_AGE
)

# Application type options
APPLICATION_TYPES = {
    "STANDARD": "standard",
    "REFINANCE": "refinance",
    "COSIGNED": "cosigned"
}

# Relationship type options for co-borrowers
RELATIONSHIP_TYPES = {
    "SPOUSE": "spouse",
    "PARENT": "parent",
    "SIBLING": "sibling",
    "RELATIVE": "relative",
    "FRIEND": "friend",
    "OTHER": "other"
}

# Status groupings for application workflow management
APPLICATION_EDITABLE_STATUSES = [
    APPLICATION_STATUS["DRAFT"],
    APPLICATION_STATUS["INCOMPLETE"],
    APPLICATION_STATUS["REVISION_REQUESTED"]
]

APPLICATION_REVIEWABLE_STATUSES = [
    APPLICATION_STATUS["SUBMITTED"],
    APPLICATION_STATUS["IN_REVIEW"]
]

APPLICATION_TERMINAL_STATUSES = [
    APPLICATION_STATUS["DENIED"],
    APPLICATION_STATUS["ABANDONED"],
    APPLICATION_STATUS["COMMITMENT_DECLINED"],
    APPLICATION_STATUS["DOCUMENTS_EXPIRED"],
    APPLICATION_STATUS["FUNDED"]
]

# Required fields for application validation
REQUIRED_BORROWER_FIELDS = [
    "first_name",
    "last_name",
    "email",
    "phone",
    "ssn",
    "dob",
    "citizenship_status",
    "address_line1",
    "city",
    "state",
    "zip_code",
    "housing_status",
    "housing_payment"
]

REQUIRED_EMPLOYMENT_FIELDS = [
    "employment_type",
    "employer_name",
    "occupation",
    "years_employed",
    "months_employed",
    "annual_income"
]

REQUIRED_LOAN_FIELDS = [
    "school_id",
    "program_id",
    "tuition_amount",
    "requested_amount",
    "start_date"
]

# Minimum employment duration for loan eligibility
MINIMUM_EMPLOYMENT_MONTHS = 3

# Mapping of application sections to required fields
APPLICATION_SUBMISSION_FIELDS_VALIDATION = {
    "borrower_info": REQUIRED_BORROWER_FIELDS,
    "employment_info": REQUIRED_EMPLOYMENT_FIELDS,
    "loan_details": REQUIRED_LOAN_FIELDS
}

# Document requirements for loan applications
DOCUMENT_REQUIREMENTS = {
    "PROOF_OF_IDENTITY": {
        "required": True,
        "description": "Government-issued photo ID (driver's license, passport, etc.)"
    },
    "PROOF_OF_INCOME": {
        "required": True,
        "description": "Recent pay stubs, W-2, or tax returns"
    },
    "PROOF_OF_RESIDENCE": {
        "required": False,
        "description": "Utility bill, lease agreement, or bank statement showing current address"
    },
    "ENROLLMENT_AGREEMENT": {
        "required": True,
        "description": "Signed enrollment agreement from the educational institution"
    }
}

# Maximum number of co-signers allowed per application
MAX_COSIGNERS = 1

# Loan term options in months
LOAN_TERM_OPTIONS = [12, 24, 36, 48, 60]

# Default loan term in months if not specified
DEFAULT_LOAN_TERM = 36

# Interest rate tiers based on credit quality
INTEREST_RATE_TIERS = {
    "EXCELLENT": Decimal('0.0475'),  # 4.75%
    "GOOD": Decimal('0.0525'),       # 5.25%
    "FAIR": Decimal('0.0625'),       # 6.25%
    "POOR": Decimal('0.0725'),       # 7.25%
    "BAD": Decimal('0.0825')         # 8.25%
}

# Credit score thresholds for interest rate tiers
CREDIT_SCORE_TIERS = {
    "EXCELLENT": 750,
    "GOOD": 700,
    "FAIR": 650,
    "POOR": 600,
    "BAD": 0
}

# Application form steps and flow
APPLICATION_FORM_STEPS = [
    "borrower_info",
    "employment_info",
    "co_borrower_info",
    "loan_details",
    "review_submit"
]

# Steps that are not required for all applications
OPTIONAL_FORM_STEPS = [
    "co_borrower_info"
]

# Income frequency types for income calculation
INCOME_FREQUENCY_TYPES = {
    "ANNUAL": "annual",
    "MONTHLY": "monthly",
    "BI_WEEKLY": "bi_weekly",
    "WEEKLY": "weekly"
}

# Multipliers to convert different income frequencies to annual income
INCOME_FREQUENCY_MULTIPLIERS = {
    "ANNUAL": Decimal('1.0'),
    "MONTHLY": Decimal('12.0'),
    "BI_WEEKLY": Decimal('26.0'),
    "WEEKLY": Decimal('52.0')
}

# Maximum loan amount as a percentage of tuition
MAX_LOAN_TO_TUITION_RATIO = Decimal('1.0')

# Minimum deposit percentage required (0% means no minimum deposit required)
MIN_DEPOSIT_PERCENTAGE = Decimal('0.0')

# Application statuses that require document uploads
APPLICATION_STATUSES_REQUIRING_DOCUMENTS = [
    APPLICATION_STATUS["SUBMITTED"],
    APPLICATION_STATUS["IN_REVIEW"],
    APPLICATION_STATUS["APPROVED"]
]

# Error messages for validation failures
ERROR_MESSAGES = {
    "INVALID_LOAN_AMOUNT": "Requested loan amount must be between {min_amount} and {max_amount}.",
    "LOAN_EXCEEDS_TUITION": "Requested loan amount cannot exceed tuition minus deposit and other funding.",
    "INVALID_START_DATE": "Start date must be in the future.",
    "INVALID_COMPLETION_DATE": "Completion date must be after start date.",
    "MISSING_REQUIRED_FIELDS": "The following required fields are missing: {fields}",
    "INVALID_SSN": "Invalid Social Security Number format.",
    "INVALID_EMAIL": "Invalid email address format.",
    "INVALID_PHONE": "Invalid phone number format.",
    "INVALID_ZIP": "Invalid ZIP code format.",
    "INVALID_STATE": "Invalid state code.",
    "INVALID_CITIZENSHIP": "Invalid citizenship status.",
    "MINIMUM_AGE_REQUIREMENT": "Applicant must be at least {min_age} years old.",
    "MINIMUM_INCOME_REQUIREMENT": "Annual income must be at least {min_income}.",
    "MINIMUM_EMPLOYMENT_REQUIREMENT": "Employment duration must be at least {min_months} months.",
    "APPLICATION_NOT_EDITABLE": "Application is not in an editable state.",
    "INVALID_DOCUMENT_TYPE": "Invalid document type.",
    "DOCUMENT_UPLOAD_FAILED": "Document upload failed. Please try again."
}