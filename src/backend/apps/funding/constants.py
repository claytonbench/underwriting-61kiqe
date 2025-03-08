"""
Constants related to the loan funding process.

This module defines constants used throughout the funding module to maintain
consistency in status tracking, workflow transitions, and business rules.
"""

from decimal import Decimal  # standard library

from ...utils.constants import FUNDING_STATUS, APPLICATION_STATUS

# Funding request status constants
FUNDING_REQUEST_STATUS = {
    "PENDING": "pending",
    "ENROLLMENT_VERIFIED": "enrollment_verified",
    "PENDING_STIPULATIONS": "pending_stipulations",
    "STIPULATIONS_COMPLETE": "stipulations_complete",
    "APPROVED": "approved",
    "REJECTED": "rejected",
    "SCHEDULED_FOR_DISBURSEMENT": "scheduled_for_disbursement",
    "DISBURSED": "disbursed",
    "CANCELLED": "cancelled"
}

# Disbursement method constants
DISBURSEMENT_METHOD = {
    "ACH": "ach",
    "WIRE": "wire",
    "CHECK": "check",
    "INTERNAL_TRANSFER": "internal_transfer"
}

# Disbursement status constants
DISBURSEMENT_STATUS = {
    "SCHEDULED": "scheduled",
    "PROCESSING": "processing",
    "COMPLETED": "completed",
    "FAILED": "failed",
    "CANCELLED": "cancelled"
}

# Enrollment verification type constants
ENROLLMENT_VERIFICATION_TYPE = {
    "ENROLLMENT_AGREEMENT": "enrollment_agreement",
    "SCHOOL_CONFIRMATION": "school_confirmation",
    "ATTENDANCE_VERIFICATION": "attendance_verification"
}

# Verification status constants
VERIFICATION_STATUS = {
    "PENDING": "pending",
    "VERIFIED": "verified",
    "REJECTED": "rejected",
    "WAIVED": "waived"
}

# Funding note type constants
FUNDING_NOTE_TYPE = {
    "GENERAL": "general",
    "APPROVAL": "approval",
    "REJECTION": "rejection",
    "STIPULATION": "stipulation",
    "DISBURSEMENT": "disbursement",
    "CANCELLATION": "cancellation"
}

# Funding approval level constants
FUNDING_APPROVAL_LEVELS = {
    "LEVEL_1": "level_1",
    "LEVEL_2": "level_2"
}

# Funding approval threshold constants
FUNDING_APPROVAL_THRESHOLDS = {
    "LEVEL_1": Decimal('10000.00'),  # Loans up to $10,000 require Level 1 approval
    "LEVEL_2": Decimal('25000.00')   # Loans up to $25,000 require Level 2 approval
}

# Minimum days required before disbursement can be processed
MINIMUM_DAYS_BEFORE_DISBURSEMENT = 3

# Days of the week when disbursements can be scheduled (0=Monday, 6=Sunday)
DISBURSEMENT_SCHEDULE_DAYS = [0, 1, 2, 3, 4]  # Monday through Friday

# Funding statuses that require notifications to be sent
FUNDING_STATUS_REQUIRING_NOTIFICATION = [
    FUNDING_REQUEST_STATUS['APPROVED'],
    FUNDING_REQUEST_STATUS['REJECTED'],
    FUNDING_REQUEST_STATUS['DISBURSED']
]

# Mapping of funding statuses to allowed next statuses for workflow transitions
FUNDING_WORKFLOW_TRANSITIONS = {
    FUNDING_REQUEST_STATUS['PENDING']: [
        FUNDING_REQUEST_STATUS['ENROLLMENT_VERIFIED'],
        FUNDING_REQUEST_STATUS['REJECTED']
    ],
    FUNDING_REQUEST_STATUS['ENROLLMENT_VERIFIED']: [
        FUNDING_REQUEST_STATUS['PENDING_STIPULATIONS'],
        FUNDING_REQUEST_STATUS['STIPULATIONS_COMPLETE'],
        FUNDING_REQUEST_STATUS['REJECTED']
    ],
    FUNDING_REQUEST_STATUS['PENDING_STIPULATIONS']: [
        FUNDING_REQUEST_STATUS['STIPULATIONS_COMPLETE'],
        FUNDING_REQUEST_STATUS['REJECTED']
    ],
    FUNDING_REQUEST_STATUS['STIPULATIONS_COMPLETE']: [
        FUNDING_REQUEST_STATUS['APPROVED'],
        FUNDING_REQUEST_STATUS['REJECTED']
    ],
    FUNDING_REQUEST_STATUS['APPROVED']: [
        FUNDING_REQUEST_STATUS['SCHEDULED_FOR_DISBURSEMENT'],
        FUNDING_REQUEST_STATUS['CANCELLED']
    ],
    FUNDING_REQUEST_STATUS['SCHEDULED_FOR_DISBURSEMENT']: [
        FUNDING_REQUEST_STATUS['DISBURSED'],
        FUNDING_REQUEST_STATUS['CANCELLED']
    ],
    FUNDING_REQUEST_STATUS['DISBURSED']: [],  # Terminal state
    FUNDING_REQUEST_STATUS['REJECTED']: [],   # Terminal state
    FUNDING_REQUEST_STATUS['CANCELLED']: [
        FUNDING_REQUEST_STATUS['APPROVED']  # Can reactivate a cancelled request
    ]
}

# Mapping of funding statuses to corresponding application statuses
FUNDING_STATUS_TRANSITIONS_TO_APPLICATION_STATUS = {
    FUNDING_REQUEST_STATUS['PENDING']: APPLICATION_STATUS['READY_TO_FUND'],
    FUNDING_REQUEST_STATUS['APPROVED']: APPLICATION_STATUS['READY_TO_FUND'],
    FUNDING_REQUEST_STATUS['DISBURSED']: APPLICATION_STATUS['FUNDED'],
    FUNDING_REQUEST_STATUS['REJECTED']: APPLICATION_STATUS['QC_APPROVED']
}