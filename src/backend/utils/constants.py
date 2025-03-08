"""
Constants module for the loan management system.

This module defines system-wide constants used across the loan management application,
including enumerations, status codes, configuration values, and other constants that
need to be referenced consistently throughout the system.
"""

from decimal import Decimal  # standard library
import os  # standard library

# User Type Constants
USER_TYPES = {
    "BORROWER": "borrower",
    "CO_BORROWER": "co_borrower",
    "SCHOOL_ADMIN": "school_admin",
    "UNDERWRITER": "underwriter",
    "QC": "qc",
    "SYSTEM_ADMIN": "system_admin"
}

# Application Status Constants - Tracks the loan application through its lifecycle
APPLICATION_STATUS = {
    "DRAFT": "draft",
    "SUBMITTED": "submitted",
    "INCOMPLETE": "incomplete",
    "IN_REVIEW": "in_review",
    "APPROVED": "approved",
    "DENIED": "denied",
    "REVISION_REQUESTED": "revision_requested",
    "ABANDONED": "abandoned",
    "COMMITMENT_SENT": "commitment_sent",
    "COMMITMENT_ACCEPTED": "commitment_accepted",
    "COMMITMENT_DECLINED": "commitment_declined",
    "COUNTER_OFFER_MADE": "counter_offer_made",
    "DOCUMENTS_SENT": "documents_sent",
    "PARTIALLY_EXECUTED": "partially_executed",
    "FULLY_EXECUTED": "fully_executed",
    "DOCUMENTS_EXPIRED": "documents_expired",
    "QC_REVIEW": "qc_review",
    "QC_APPROVED": "qc_approved",
    "QC_REJECTED": "qc_rejected",
    "READY_TO_FUND": "ready_to_fund",
    "FUNDED": "funded"
}

# Document Status Constants
DOCUMENT_STATUS = {
    "DRAFT": "draft",
    "GENERATED": "generated",
    "SENT": "sent",
    "PARTIALLY_SIGNED": "partially_signed",
    "COMPLETED": "completed", 
    "REJECTED": "rejected",
    "EXPIRED": "expired"
}

# Signature Status Constants
SIGNATURE_STATUS = {
    "PENDING": "pending",
    "SENT": "sent",
    "SIGNED": "signed",
    "DECLINED": "declined",
    "EXPIRED": "expired"
}

# Funding Status Constants
FUNDING_STATUS = {
    "PENDING_ENROLLMENT": "pending_enrollment",
    "ENROLLMENT_VERIFIED": "enrollment_verified",
    "STIPULATION_REVIEW": "stipulation_review",
    "STIPULATIONS_COMPLETE": "stipulations_complete",
    "PENDING_STIPULATIONS": "pending_stipulations",
    "FUNDING_APPROVAL": "funding_approval",
    "APPROVED_FOR_FUNDING": "approved_for_funding",
    "SCHEDULED_FOR_DISBURSEMENT": "scheduled_for_disbursement",
    "DISBURSED": "disbursed",
    "FUNDING_COMPLETE": "funding_complete"
}

# Underwriting Decision Constants
UNDERWRITING_DECISION = {
    "APPROVE": "approve",
    "DENY": "deny",
    "REVISE": "revise"
}

# Quality Control Decision Constants
QC_DECISION = {
    "APPROVE": "approve",
    "RETURN": "return"
}

# Document Type Constants
DOCUMENT_TYPES = {
    "COMMITMENT_LETTER": "commitment_letter",
    "LOAN_AGREEMENT": "loan_agreement",
    "TRUTH_IN_LENDING": "truth_in_lending",
    "PROMISSORY_NOTE": "promissory_note",
    "DISCLOSURE_FORM": "disclosure_form",
    "DISBURSEMENT_AUTHORIZATION": "disbursement_authorization",
    "ENROLLMENT_AGREEMENT": "enrollment_agreement",
    "PROOF_OF_INCOME": "proof_of_income",
    "PROOF_OF_IDENTITY": "proof_of_identity",
    "PROOF_OF_RESIDENCE": "proof_of_residence",
    "ADDITIONAL_DOCUMENTATION": "additional_documentation"
}

# Stipulation Type Constants
STIPULATION_TYPES = {
    "ENROLLMENT_AGREEMENT": "enrollment_agreement",
    "PROOF_OF_INCOME": "proof_of_income",
    "PROOF_OF_IDENTITY": "proof_of_identity",
    "PROOF_OF_RESIDENCE": "proof_of_residence",
    "ADDITIONAL_DOCUMENTATION": "additional_documentation"
}

# Stipulation Status Constants
STIPULATION_STATUS = {
    "PENDING": "pending",
    "SATISFIED": "satisfied",
    "WAIVED": "waived",
    "EXPIRED": "expired"
}

# Employment Type Constants
EMPLOYMENT_TYPES = {
    "FULL_TIME": "full_time",
    "PART_TIME": "part_time",
    "SELF_EMPLOYED": "self_employed",
    "UNEMPLOYED": "unemployed",
    "RETIRED": "retired",
    "STUDENT": "student"
}

# Housing Status Constants
HOUSING_STATUS = {
    "OWN": "own",
    "RENT": "rent",
    "LIVE_WITH_FAMILY": "live_with_family",
    "OTHER": "other"
}

# Citizenship Status Constants
CITIZENSHIP_STATUS = {
    "US_CITIZEN": "us_citizen",
    "PERMANENT_RESIDENT": "permanent_resident",
    "ELIGIBLE_NON_CITIZEN": "eligible_non_citizen",
    "INELIGIBLE_NON_CITIZEN": "ineligible_non_citizen"
}

# Underwriting Thresholds and Criteria - Based on 6.4.3 Underwriting Decision Rules
MIN_CREDIT_SCORE_APPROVAL = 680
MIN_CREDIT_SCORE_CONSIDERATION = 620
MAX_DEBT_TO_INCOME_RATIO = 0.50  # 50%
MAX_HOUSING_PAYMENT_RATIO = 0.40  # 40%
MIN_EMPLOYMENT_DURATION_MONTHS = 3

# Document Management Constants
DOCUMENT_EXPIRATION_DAYS = 90  # Documents expire after 90 days if not signed
SIGNATURE_REMINDER_DAYS = [30, 15, 7, 3, 1]  # Days before expiration to send reminders
MAX_UPLOAD_SIZE_MB = 10
ALLOWED_DOCUMENT_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png"]

# Storage Paths
S3_DOCUMENT_PATH = "documents"
S3_TEMPLATE_PATH = "templates"

# Loan Constants
DEFAULT_INTEREST_RATE = Decimal('0.0525')  # 5.25%
DEFAULT_LOAN_TERM_MONTHS = 36
MINIMUM_LOAN_AMOUNT = Decimal('1000.00')
MAXIMUM_LOAN_AMOUNT = Decimal('50000.00')
MINIMUM_INCOME = Decimal('24000.00')  # $24,000 annual income
MINIMUM_AGE = 18

# Formatting Constants
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
CURRENCY_FORMAT = "${:,.2f}"
PERCENTAGE_FORMAT = "{:.2f}%"
PHONE_FORMAT = "({}{}{}) {}{}{}-{}{}{}{}"
SSN_FORMAT = "{}{}{}-{}{}-{}{}{}{}"
SSN_DISPLAY_FORMAT = "XXX-XX-{}{}{}{}"  # Masked SSN showing only last 4 digits

# Validation Regular Expressions
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
PHONE_REGEX = r"^\(\d{3}\) \d{3}-\d{4}$"
ZIP_CODE_REGEX = r"^\d{5}(-\d{4})?$"
SSN_REGEX = r"^\d{3}-\d{2}-\d{4}$"

# US States Dictionary
US_STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", 
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", 
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", 
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", 
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", 
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", 
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", 
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", 
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", 
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", 
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", 
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", 
    "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia", 
    "PR": "Puerto Rico", "VI": "Virgin Islands", "GU": "Guam",
    "AS": "American Samoa", "MP": "Northern Mariana Islands"
}

# API Constants
API_PAGINATION_DEFAULT_LIMIT = 20
API_PAGINATION_MAX_LIMIT = 100

# Authentication and Security Constants
JWT_EXPIRATION_HOURS = 1
REFRESH_TOKEN_EXPIRATION_DAYS = 14
PASSWORD_RESET_EXPIRATION_HOURS = 24
PASSWORD_MIN_LENGTH = 12
PASSWORD_COMPLEXITY_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$"
MAX_LOGIN_ATTEMPTS = 5
ACCOUNT_LOCKOUT_MINUTES = 30
SESSION_TIMEOUT_MINUTES = 60

# Compliance and Retention Constants
AUDIT_LOG_RETENTION_DAYS = 730  # 2 years
DOCUMENT_RETENTION_YEARS = 7  # Required retention period for loan documents