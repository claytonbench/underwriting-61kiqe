"""
Constants for the Quality Control (QC) module.

This module defines various constants used throughout the QC process, including
status codes, verification statuses, checklist categories, and other configuration values.
The QC process is a critical step after document completion and before funding approval.
"""

from ...utils.constants import APPLICATION_STATUS, FUNDING_STATUS

# QC Status Constants
QC_STATUS = {
    "PENDING": "pending",          # Initial status when application enters QC queue
    "IN_REVIEW": "in_review",      # QC reviewer has started the review process
    "APPROVED": "approved",        # QC review approved, application can move to funding
    "RETURNED": "returned"         # QC review returned for corrections
}

# Verification Status Constants
QC_VERIFICATION_STATUS = {
    "UNVERIFIED": "unverified",    # Item has not been verified yet
    "VERIFIED": "verified",        # Item has been verified as correct
    "REJECTED": "rejected",        # Item has been rejected as incorrect or incomplete
    "WAIVED": "waived"             # Verification requirement has been waived
}

# QC Return Reason Constants
QC_RETURN_REASON = {
    "INCOMPLETE_DOCUMENTATION": "incomplete_documentation",
    "INCORRECT_INFORMATION": "incorrect_information",
    "MISSING_SIGNATURES": "missing_signatures",
    "STIPULATION_NOT_MET": "stipulation_not_met",
    "COMPLIANCE_ISSUE": "compliance_issue",
    "OTHER": "other"
}

# QC Checklist Category Constants
QC_CHECKLIST_CATEGORY = {
    "DOCUMENT_COMPLETENESS": "document_completeness",
    "LOAN_INFORMATION": "loan_information",
    "BORROWER_INFORMATION": "borrower_information",
    "SCHOOL_INFORMATION": "school_information",
    "STIPULATIONS": "stipulations",
    "COMPLIANCE": "compliance"
}

# QC Priority Constants
QC_PRIORITY = {
    "HIGH": "high",
    "MEDIUM": "medium",
    "LOW": "low"
}

# QC Assignment Type Constants
QC_ASSIGNMENT_TYPE = {
    "AUTOMATIC": "automatic",
    "MANUAL": "manual"
}

# QC Review SLA in hours
QC_REVIEW_SLA_HOURS = 24

# Mapping QC status to application status
QC_STATUS_TO_APPLICATION_STATUS = {
    QC_STATUS["PENDING"]: APPLICATION_STATUS["QC_REVIEW"],
    QC_STATUS["IN_REVIEW"]: APPLICATION_STATUS["QC_REVIEW"],
    QC_STATUS["APPROVED"]: APPLICATION_STATUS["QC_APPROVED"],
    QC_STATUS["RETURNED"]: APPLICATION_STATUS["QC_REJECTED"]
}

# Mapping QC approval to funding status
QC_APPROVAL_TO_FUNDING_STATUS = {
    QC_STATUS["APPROVED"]: FUNDING_STATUS["PENDING_ENROLLMENT"]
}

# QC Verification Checklist Items for Document Completeness
QC_DOCUMENT_VERIFICATION_ITEMS = [
    "All required documents are present and signed",
    "Document signatures are valid and complete",
    "No expired documents",
    "Document package is complete"
]

# QC Verification Checklist Items for Loan Information
QC_LOAN_VERIFICATION_ITEMS = [
    "Loan amount matches approval",
    "Term and rate match approval",
    "Program details consistent across documents",
    "Payment schedule is accurate"
]

# QC Verification Checklist Items for Borrower Information
QC_BORROWER_VERIFICATION_ITEMS = [
    "Personal information consistent across documents",
    "Identity verification complete",
    "Contact information is valid",
    "Employment information verified"
]

# QC Verification Checklist Items for School Information
QC_SCHOOL_VERIFICATION_ITEMS = [
    "Enrollment agreement matches loan details",
    "Start date confirmed",
    "Program cost matches loan amount",
    "School information consistent across documents"
]

# QC Verification Checklist Items for Stipulations
QC_STIPULATION_VERIFICATION_ITEMS = [
    "All required stipulations satisfied",
    "Stipulation documents verified",
    "Waived stipulations properly documented"
]

# QC Verification Checklist Items for Compliance
QC_COMPLIANCE_VERIFICATION_ITEMS = [
    "All required disclosures provided and signed",
    "Cooling-off periods observed",
    "Regulatory requirements met",
    "Compliance checklist complete"
]