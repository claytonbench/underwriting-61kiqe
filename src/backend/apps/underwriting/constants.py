"""
Constants module for the loan underwriting process.

This module defines constants specific to the underwriting workflow, decision criteria,
evaluation metrics, stipulation requirements, and queue management. These constants
are used throughout the underwriting component to ensure consistent application of
business rules and underwriting standards.
"""

from decimal import Decimal  # standard library v3.11+

from ...utils.constants import (
    UNDERWRITING_DECISION,
    APPLICATION_STATUS,
    STIPULATION_TYPES,
    STIPULATION_STATUS,
)

# Underwriting Queue Management Constants
UNDERWRITING_QUEUE_PRIORITY = {
    "HIGH": "high",
    "MEDIUM": "medium",
    "LOW": "low",
}

UNDERWRITING_QUEUE_STATUS = {
    "PENDING": "pending",
    "ASSIGNED": "assigned",
    "IN_PROGRESS": "in_progress",
    "COMPLETED": "completed",
    "RETURNED": "returned",
}

# Service Level Agreement timeframes (hours) for application processing based on priority
UNDERWRITING_QUEUE_SLA_HOURS = {
    "HIGH": 24,    # High priority applications should be processed within 24 hours
    "MEDIUM": 48,  # Medium priority applications should be processed within 48 hours
    "LOW": 72,     # Low priority applications should be processed within 72 hours
}

# Credit Score Classification Thresholds
CREDIT_SCORE_TIERS = {
    "EXCELLENT": 750,  # 750+ considered excellent credit
    "GOOD": 700,       # 700-749 considered good credit
    "FAIR": 650,       # 650-699 considered fair credit
    "POOR": 600,       # 600-649 considered poor credit
    "BAD": 550,        # 550-599 considered bad credit
                      # Below 550 considered very bad credit
}

# Debt-to-Income Ratio Risk Thresholds
DEBT_TO_INCOME_TIERS = {
    "LOW": Decimal('0.30'),     # Less than 30% considered low risk
    "MEDIUM": Decimal('0.40'),  # 30-40% considered medium risk
    "HIGH": Decimal('0.50'),    # 40-50% considered high risk
                               # Above 50% considered very high risk
}

# Employment History Requirements (in months)
EMPLOYMENT_HISTORY_REQUIREMENTS = {
    "PREFERRED": 24,   # 2+ years of stable employment is preferred
    "ACCEPTABLE": 12,  # 1-2 years is acceptable
    "MINIMUM": 3,      # Less than 3 months is below minimum
}

# Housing Payment to Income Ratio Limits
HOUSING_PAYMENT_RATIO_LIMITS = {
    "LOW": Decimal('0.30'),     # Housing payment less than 30% of income is low risk
    "MEDIUM": Decimal('0.35'),  # 30-35% is medium risk
    "HIGH": Decimal('0.40'),    # 35-40% is high risk
                               # Above 40% is very high risk
}

# Automatic Approval Criteria Thresholds
AUTOMATIC_APPROVAL_CRITERIA = {
    "MIN_CREDIT_SCORE": 680,                # Minimum credit score for automatic approval
    "MAX_DTI": Decimal('0.40'),             # Maximum debt-to-income ratio for automatic approval
    "MIN_EMPLOYMENT_MONTHS": 24,            # Minimum employment duration for automatic approval
}

# Automatic Denial Criteria Thresholds
AUTOMATIC_DENIAL_CRITERIA = {
    "MAX_CREDIT_SCORE": 580,                # Maximum credit score for automatic denial
    "MIN_DTI": Decimal('0.55'),             # Minimum debt-to-income ratio for automatic denial
    "MAX_HOUSING_RATIO": Decimal('0.45'),   # Maximum housing payment ratio for automatic denial
}

# Manual Review/Consideration Criteria Thresholds
CONSIDERATION_CRITERIA = {
    "MIN_CREDIT_SCORE": 620,                # Minimum credit score for consideration
    "MAX_DTI": Decimal('0.50'),             # Maximum debt-to-income ratio for consideration
    "MIN_EMPLOYMENT_MONTHS": 12,            # Minimum employment duration for consideration
}

# Decision Reason Codes
DECISION_REASON_CODES = {
    "CREDIT_SCORE": "credit_score",
    "DEBT_TO_INCOME": "debt_to_income",
    "EMPLOYMENT_HISTORY": "employment_history",
    "HOUSING_PAYMENT": "housing_payment",
    "INCOME_INSUFFICIENT": "income_insufficient",
    "CITIZENSHIP_STATUS": "citizenship_status",
    "PROGRAM_ELIGIBILITY": "program_eligibility",
    "DOCUMENTATION_ISSUES": "documentation_issues",
    "IDENTITY_VERIFICATION": "identity_verification",
    "OTHER": "other",
}

# Human-readable descriptions for decision reason codes
DECISION_REASON_DESCRIPTIONS = {
    "credit_score": "Credit score below required threshold",
    "debt_to_income": "Debt-to-income ratio exceeds maximum limit",
    "employment_history": "Insufficient employment history",
    "housing_payment": "Housing payment ratio exceeds maximum limit",
    "income_insufficient": "Income insufficient for requested loan amount",
    "citizenship_status": "Ineligible citizenship status",
    "program_eligibility": "Selected program not eligible for financing",
    "documentation_issues": "Issues with submitted documentation",
    "identity_verification": "Unable to verify identity",
    "other": "Other reason",
}

# Stipulation Categories for grouping related requirements
STIPULATION_CATEGORIES = {
    "IDENTITY_VERIFICATION": "identity_verification",
    "INCOME_VERIFICATION": "income_verification",
    "CITIZENSHIP_RESIDENCY": "citizenship_residency",
    "EDUCATION_DOCUMENTATION": "education_documentation",
    "FINANCIAL": "financial",
}

# Mapping of stipulation categories to specific stipulation types
STIPULATION_CATEGORY_MAPPING = {
    "identity_verification": ["PROOF_OF_IDENTITY"],
    "income_verification": ["PROOF_OF_INCOME"],
    "citizenship_residency": ["PROOF_OF_RESIDENCE"],
    "education_documentation": ["ENROLLMENT_AGREEMENT"],
    "financial": ["ADDITIONAL_DOCUMENTATION"],
}

# Required stipulations based on underwriting decision
REQUIRED_STIPULATIONS_BY_DECISION = {
    "approve": ["ENROLLMENT_AGREEMENT", "PROOF_OF_INCOME"],
    "revise": ["PROOF_OF_INCOME", "ADDITIONAL_DOCUMENTATION"],
    "deny": [],
}

# Mapping of underwriting decisions to application status transitions
UNDERWRITING_DECISION_TRANSITIONS = {
    "approve": "APPROVED",
    "deny": "DENIED",
    "revise": "REVISION_REQUESTED",
}

# Workload management constants
MAX_UNDERWRITER_QUEUE_SIZE = 15  # Maximum number of applications an underwriter can have in their queue
UNDERWRITER_DAILY_TARGET = 10    # Target number of applications an underwriter should process daily

# Weighting factors for risk assessment algorithm
CREDIT_SCORE_WEIGHT = 0.35       # Credit score accounts for 35% of overall evaluation
DEBT_TO_INCOME_WEIGHT = 0.30     # Debt-to-income ratio accounts for 30% of overall evaluation
EMPLOYMENT_HISTORY_WEIGHT = 0.20 # Employment history accounts for 20% of overall evaluation
HOUSING_PAYMENT_WEIGHT = 0.15    # Housing payment ratio accounts for 15% of overall evaluation

# Additional underwriting thresholds
MINIMUM_INCOME_TO_LOAN_RATIO = 2.0  # Annual income should be at least 2x the loan amount

# Ranges for borderline cases requiring additional scrutiny
BORDERLINE_CREDIT_SCORE_RANGE = [620, 650]  # Credit scores in this range require additional review
BORDERLINE_DTI_RANGE = [Decimal('0.45'), Decimal('0.50')]  # DTI ratios in this range require additional review  
BORDERLINE_EMPLOYMENT_RANGE = [12, 18]  # Employment duration in this range requires additional review