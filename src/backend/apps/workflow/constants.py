"""
Constants related to the workflow state machine.

This module defines constants for the workflow state machine that manages transitions 
between different states in the loan application lifecycle. This includes workflow types, 
state transition rules, permissions, SLA definitions, and event mappings.
"""

from ...utils.constants import (
    APPLICATION_STATUS,
    DOCUMENT_STATUS,
    FUNDING_STATUS,
    USER_TYPES,
)

# Workflow types
WORKFLOW_TYPES = {
    "APPLICATION": "application",
    "DOCUMENT": "document",
    "FUNDING": "funding"
}

# Application state transitions (from state -> list of possible next states)
APPLICATION_STATE_TRANSITIONS = {
    APPLICATION_STATUS['DRAFT']: [APPLICATION_STATUS['SUBMITTED'], APPLICATION_STATUS['ABANDONED']],
    APPLICATION_STATUS['SUBMITTED']: [APPLICATION_STATUS['IN_REVIEW'], APPLICATION_STATUS['INCOMPLETE'], APPLICATION_STATUS['ABANDONED']],
    APPLICATION_STATUS['INCOMPLETE']: [APPLICATION_STATUS['SUBMITTED'], APPLICATION_STATUS['ABANDONED']],
    APPLICATION_STATUS['IN_REVIEW']: [APPLICATION_STATUS['APPROVED'], APPLICATION_STATUS['DENIED'], APPLICATION_STATUS['REVISION_REQUESTED']],
    APPLICATION_STATUS['REVISION_REQUESTED']: [APPLICATION_STATUS['IN_REVIEW'], APPLICATION_STATUS['ABANDONED']],
    APPLICATION_STATUS['APPROVED']: [APPLICATION_STATUS['COMMITMENT_SENT']],
    APPLICATION_STATUS['COMMITMENT_SENT']: [APPLICATION_STATUS['COMMITMENT_ACCEPTED'], APPLICATION_STATUS['COMMITMENT_DECLINED'], APPLICATION_STATUS['COUNTER_OFFER_MADE']],
    APPLICATION_STATUS['COUNTER_OFFER_MADE']: [APPLICATION_STATUS['IN_REVIEW']],
    APPLICATION_STATUS['COMMITMENT_ACCEPTED']: [APPLICATION_STATUS['DOCUMENTS_SENT']],
    APPLICATION_STATUS['DOCUMENTS_SENT']: [APPLICATION_STATUS['PARTIALLY_EXECUTED'], APPLICATION_STATUS['DOCUMENTS_EXPIRED']],
    APPLICATION_STATUS['PARTIALLY_EXECUTED']: [APPLICATION_STATUS['FULLY_EXECUTED'], APPLICATION_STATUS['DOCUMENTS_EXPIRED']],
    APPLICATION_STATUS['FULLY_EXECUTED']: [APPLICATION_STATUS['QC_REVIEW']],
    APPLICATION_STATUS['QC_REVIEW']: [APPLICATION_STATUS['QC_APPROVED'], APPLICATION_STATUS['QC_REJECTED']],
    APPLICATION_STATUS['QC_REJECTED']: [APPLICATION_STATUS['QC_REVIEW']],
    APPLICATION_STATUS['QC_APPROVED']: [APPLICATION_STATUS['READY_TO_FUND']],
    APPLICATION_STATUS['READY_TO_FUND']: [APPLICATION_STATUS['FUNDED']],
}

# Document state transitions
DOCUMENT_STATE_TRANSITIONS = {
    DOCUMENT_STATUS['DRAFT']: [DOCUMENT_STATUS['GENERATED']],
    DOCUMENT_STATUS['GENERATED']: [DOCUMENT_STATUS['SENT']],
    DOCUMENT_STATUS['SENT']: [DOCUMENT_STATUS['PARTIALLY_SIGNED'], DOCUMENT_STATUS['REJECTED'], DOCUMENT_STATUS['EXPIRED']],
    DOCUMENT_STATUS['PARTIALLY_SIGNED']: [DOCUMENT_STATUS['COMPLETED'], DOCUMENT_STATUS['REJECTED'], DOCUMENT_STATUS['EXPIRED']]
}

# Funding state transitions
FUNDING_STATE_TRANSITIONS = {
    FUNDING_STATUS['PENDING_ENROLLMENT']: [FUNDING_STATUS['ENROLLMENT_VERIFIED']],
    FUNDING_STATUS['ENROLLMENT_VERIFIED']: [FUNDING_STATUS['STIPULATION_REVIEW']],
    FUNDING_STATUS['STIPULATION_REVIEW']: [FUNDING_STATUS['STIPULATIONS_COMPLETE'], FUNDING_STATUS['PENDING_STIPULATIONS']],
    FUNDING_STATUS['PENDING_STIPULATIONS']: [FUNDING_STATUS['STIPULATION_REVIEW']],
    FUNDING_STATUS['STIPULATIONS_COMPLETE']: [FUNDING_STATUS['FUNDING_APPROVAL']],
    FUNDING_STATUS['FUNDING_APPROVAL']: [FUNDING_STATUS['APPROVED_FOR_FUNDING']],
    FUNDING_STATUS['APPROVED_FOR_FUNDING']: [FUNDING_STATUS['SCHEDULED_FOR_DISBURSEMENT']],
    FUNDING_STATUS['SCHEDULED_FOR_DISBURSEMENT']: [FUNDING_STATUS['DISBURSED']],
    FUNDING_STATUS['DISBURSED']: [FUNDING_STATUS['FUNDING_COMPLETE']],
}

# Initial states for each workflow type
INITIAL_STATES = {
    WORKFLOW_TYPES['APPLICATION']: APPLICATION_STATUS['DRAFT'],
    WORKFLOW_TYPES['DOCUMENT']: DOCUMENT_STATUS['DRAFT'],
    WORKFLOW_TYPES['FUNDING']: FUNDING_STATUS['PENDING_ENROLLMENT'],
}

# Terminal states for each workflow type
TERMINAL_STATES = {
    WORKFLOW_TYPES['APPLICATION']: [
        APPLICATION_STATUS['FUNDED'],
        APPLICATION_STATUS['DENIED'],
        APPLICATION_STATUS['ABANDONED'],
        APPLICATION_STATUS['COMMITMENT_DECLINED'],
        APPLICATION_STATUS['DOCUMENTS_EXPIRED'],
    ],
    WORKFLOW_TYPES['DOCUMENT']: [
        DOCUMENT_STATUS['COMPLETED'],
        DOCUMENT_STATUS['REJECTED'],
        DOCUMENT_STATUS['EXPIRED'],
    ],
    WORKFLOW_TYPES['FUNDING']: [
        FUNDING_STATUS['FUNDING_COMPLETE'],
    ],
}

# Mapping of states to user types that can initiate transitions to those states
STATE_TRANSITION_PERMISSIONS = {
    APPLICATION_STATUS['SUBMITTED']: [USER_TYPES['UNDERWRITER'], USER_TYPES['SYSTEM_ADMIN']],
    APPLICATION_STATUS['IN_REVIEW']: [USER_TYPES['UNDERWRITER'], USER_TYPES['SYSTEM_ADMIN']],
    APPLICATION_STATUS['APPROVED']: [USER_TYPES['UNDERWRITER'], USER_TYPES['SYSTEM_ADMIN']],
    APPLICATION_STATUS['DENIED']: [USER_TYPES['UNDERWRITER'], USER_TYPES['SYSTEM_ADMIN']],
    APPLICATION_STATUS['REVISION_REQUESTED']: [USER_TYPES['UNDERWRITER'], USER_TYPES['SYSTEM_ADMIN']],
    APPLICATION_STATUS['COMMITMENT_SENT']: [USER_TYPES['SCHOOL_ADMIN'], USER_TYPES['SYSTEM_ADMIN']],
    APPLICATION_STATUS['COMMITMENT_ACCEPTED']: [USER_TYPES['SCHOOL_ADMIN'], USER_TYPES['SYSTEM_ADMIN']],
    APPLICATION_STATUS['COMMITMENT_DECLINED']: [USER_TYPES['SCHOOL_ADMIN'], USER_TYPES['SYSTEM_ADMIN']],
    APPLICATION_STATUS['COUNTER_OFFER_MADE']: [USER_TYPES['SCHOOL_ADMIN'], USER_TYPES['SYSTEM_ADMIN']],
    APPLICATION_STATUS['QC_REVIEW']: [USER_TYPES['QC'], USER_TYPES['SYSTEM_ADMIN']],
    APPLICATION_STATUS['QC_APPROVED']: [USER_TYPES['QC'], USER_TYPES['SYSTEM_ADMIN']],
    APPLICATION_STATUS['QC_REJECTED']: [USER_TYPES['QC'], USER_TYPES['SYSTEM_ADMIN']],
    APPLICATION_STATUS['READY_TO_FUND']: [USER_TYPES['SYSTEM_ADMIN']],
    APPLICATION_STATUS['FUNDED']: [USER_TYPES['SYSTEM_ADMIN']],
}

# Named events for state transitions with workflow type, from state, and to state
WORKFLOW_TRANSITION_EVENTS = {
    # Application workflow events
    "APPLICATION_SUBMITTED": {
        "workflow_type": WORKFLOW_TYPES['APPLICATION'],
        "from_state": APPLICATION_STATUS['DRAFT'],
        "to_state": APPLICATION_STATUS['SUBMITTED']
    },
    "APPLICATION_ASSIGNED": {
        "workflow_type": WORKFLOW_TYPES['APPLICATION'],
        "from_state": APPLICATION_STATUS['SUBMITTED'],
        "to_state": APPLICATION_STATUS['IN_REVIEW']
    },
    "APPLICATION_APPROVED": {
        "workflow_type": WORKFLOW_TYPES['APPLICATION'],
        "from_state": APPLICATION_STATUS['IN_REVIEW'],
        "to_state": APPLICATION_STATUS['APPROVED']
    },
    "APPLICATION_DENIED": {
        "workflow_type": WORKFLOW_TYPES['APPLICATION'],
        "from_state": APPLICATION_STATUS['IN_REVIEW'],
        "to_state": APPLICATION_STATUS['DENIED']
    },
    "APPLICATION_REVISION_REQUESTED": {
        "workflow_type": WORKFLOW_TYPES['APPLICATION'],
        "from_state": APPLICATION_STATUS['IN_REVIEW'],
        "to_state": APPLICATION_STATUS['REVISION_REQUESTED']
    },
    "COMMITMENT_LETTER_SENT": {
        "workflow_type": WORKFLOW_TYPES['APPLICATION'],
        "from_state": APPLICATION_STATUS['APPROVED'],
        "to_state": APPLICATION_STATUS['COMMITMENT_SENT']
    },
    "COMMITMENT_LETTER_ACCEPTED": {
        "workflow_type": WORKFLOW_TYPES['APPLICATION'],
        "from_state": APPLICATION_STATUS['COMMITMENT_SENT'],
        "to_state": APPLICATION_STATUS['COMMITMENT_ACCEPTED']
    },
    "COMMITMENT_LETTER_DECLINED": {
        "workflow_type": WORKFLOW_TYPES['APPLICATION'],
        "from_state": APPLICATION_STATUS['COMMITMENT_SENT'],
        "to_state": APPLICATION_STATUS['COMMITMENT_DECLINED']
    },
    "COUNTER_OFFER_MADE": {
        "workflow_type": WORKFLOW_TYPES['APPLICATION'],
        "from_state": APPLICATION_STATUS['COMMITMENT_SENT'],
        "to_state": APPLICATION_STATUS['COUNTER_OFFER_MADE']
    },
    "DOCUMENTS_SENT": {
        "workflow_type": WORKFLOW_TYPES['APPLICATION'],
        "from_state": APPLICATION_STATUS['COMMITMENT_ACCEPTED'],
        "to_state": APPLICATION_STATUS['DOCUMENTS_SENT']
    },
    "DOCUMENTS_PARTIALLY_EXECUTED": {
        "workflow_type": WORKFLOW_TYPES['APPLICATION'],
        "from_state": APPLICATION_STATUS['DOCUMENTS_SENT'],
        "to_state": APPLICATION_STATUS['PARTIALLY_EXECUTED']
    },
    "DOCUMENTS_FULLY_EXECUTED": {
        "workflow_type": WORKFLOW_TYPES['APPLICATION'],
        "from_state": APPLICATION_STATUS['PARTIALLY_EXECUTED'],
        "to_state": APPLICATION_STATUS['FULLY_EXECUTED']
    },
    "DOCUMENTS_EXPIRED": {
        "workflow_type": WORKFLOW_TYPES['APPLICATION'],
        "from_state": [APPLICATION_STATUS['DOCUMENTS_SENT'], APPLICATION_STATUS['PARTIALLY_EXECUTED']],
        "to_state": APPLICATION_STATUS['DOCUMENTS_EXPIRED']
    },
    "QC_REVIEW_STARTED": {
        "workflow_type": WORKFLOW_TYPES['APPLICATION'],
        "from_state": APPLICATION_STATUS['FULLY_EXECUTED'],
        "to_state": APPLICATION_STATUS['QC_REVIEW']
    },
    "QC_APPROVED": {
        "workflow_type": WORKFLOW_TYPES['APPLICATION'],
        "from_state": APPLICATION_STATUS['QC_REVIEW'],
        "to_state": APPLICATION_STATUS['QC_APPROVED']
    },
    "QC_REJECTED": {
        "workflow_type": WORKFLOW_TYPES['APPLICATION'],
        "from_state": APPLICATION_STATUS['QC_REVIEW'],
        "to_state": APPLICATION_STATUS['QC_REJECTED']
    },
    "READY_TO_FUND": {
        "workflow_type": WORKFLOW_TYPES['APPLICATION'],
        "from_state": APPLICATION_STATUS['QC_APPROVED'],
        "to_state": APPLICATION_STATUS['READY_TO_FUND']
    },
    "FUNDING_COMPLETE": {
        "workflow_type": WORKFLOW_TYPES['APPLICATION'],
        "from_state": APPLICATION_STATUS['READY_TO_FUND'],
        "to_state": APPLICATION_STATUS['FUNDED']
    },
    
    # Document workflow events
    "DOCUMENT_GENERATED": {
        "workflow_type": WORKFLOW_TYPES['DOCUMENT'],
        "from_state": DOCUMENT_STATUS['DRAFT'],
        "to_state": DOCUMENT_STATUS['GENERATED']
    },
    "DOCUMENT_SENT": {
        "workflow_type": WORKFLOW_TYPES['DOCUMENT'],
        "from_state": DOCUMENT_STATUS['GENERATED'],
        "to_state": DOCUMENT_STATUS['SENT']
    },
    "DOCUMENT_PARTIALLY_SIGNED": {
        "workflow_type": WORKFLOW_TYPES['DOCUMENT'],
        "from_state": DOCUMENT_STATUS['SENT'],
        "to_state": DOCUMENT_STATUS['PARTIALLY_SIGNED']
    },
    "DOCUMENT_COMPLETED": {
        "workflow_type": WORKFLOW_TYPES['DOCUMENT'],
        "from_state": DOCUMENT_STATUS['PARTIALLY_SIGNED'],
        "to_state": DOCUMENT_STATUS['COMPLETED']
    },
    "DOCUMENT_REJECTED": {
        "workflow_type": WORKFLOW_TYPES['DOCUMENT'],
        "from_state": [DOCUMENT_STATUS['SENT'], DOCUMENT_STATUS['PARTIALLY_SIGNED']],
        "to_state": DOCUMENT_STATUS['REJECTED']
    },
    "DOCUMENT_EXPIRED": {
        "workflow_type": WORKFLOW_TYPES['DOCUMENT'],
        "from_state": [DOCUMENT_STATUS['SENT'], DOCUMENT_STATUS['PARTIALLY_SIGNED']],
        "to_state": DOCUMENT_STATUS['EXPIRED']
    },
    
    # Funding workflow events
    "ENROLLMENT_VERIFIED": {
        "workflow_type": WORKFLOW_TYPES['FUNDING'],
        "from_state": FUNDING_STATUS['PENDING_ENROLLMENT'],
        "to_state": FUNDING_STATUS['ENROLLMENT_VERIFIED']
    },
    "STIPULATION_REVIEW_STARTED": {
        "workflow_type": WORKFLOW_TYPES['FUNDING'],
        "from_state": FUNDING_STATUS['ENROLLMENT_VERIFIED'],
        "to_state": FUNDING_STATUS['STIPULATION_REVIEW']
    },
    "STIPULATIONS_COMPLETE": {
        "workflow_type": WORKFLOW_TYPES['FUNDING'],
        "from_state": FUNDING_STATUS['STIPULATION_REVIEW'],
        "to_state": FUNDING_STATUS['STIPULATIONS_COMPLETE']
    },
    "PENDING_STIPULATIONS": {
        "workflow_type": WORKFLOW_TYPES['FUNDING'],
        "from_state": FUNDING_STATUS['STIPULATION_REVIEW'],
        "to_state": FUNDING_STATUS['PENDING_STIPULATIONS']
    },
    "FUNDING_APPROVAL_STARTED": {
        "workflow_type": WORKFLOW_TYPES['FUNDING'],
        "from_state": FUNDING_STATUS['STIPULATIONS_COMPLETE'],
        "to_state": FUNDING_STATUS['FUNDING_APPROVAL']
    },
    "APPROVED_FOR_FUNDING": {
        "workflow_type": WORKFLOW_TYPES['FUNDING'],
        "from_state": FUNDING_STATUS['FUNDING_APPROVAL'],
        "to_state": FUNDING_STATUS['APPROVED_FOR_FUNDING']
    },
    "SCHEDULED_FOR_DISBURSEMENT": {
        "workflow_type": WORKFLOW_TYPES['FUNDING'],
        "from_state": FUNDING_STATUS['APPROVED_FOR_FUNDING'],
        "to_state": FUNDING_STATUS['SCHEDULED_FOR_DISBURSEMENT']
    },
    "DISBURSED": {
        "workflow_type": WORKFLOW_TYPES['FUNDING'],
        "from_state": FUNDING_STATUS['SCHEDULED_FOR_DISBURSEMENT'],
        "to_state": FUNDING_STATUS['DISBURSED']
    },
    "FUNDING_COMPLETE": {
        "workflow_type": WORKFLOW_TYPES['FUNDING'],
        "from_state": FUNDING_STATUS['DISBURSED'],
        "to_state": FUNDING_STATUS['FUNDING_COMPLETE']
    },
}

# Automatic transitions after a defined period in certain states
AUTOMATIC_TRANSITIONS = {
    APPLICATION_STATUS['APPROVED']: {
        "to_state": APPLICATION_STATUS['COMMITMENT_SENT'],
        "delay_hours": 1,
        "reason": "Automatic transition to send commitment letter"
    },
    DOCUMENT_STATUS['GENERATED']: {
        "to_state": DOCUMENT_STATUS['SENT'],
        "delay_hours": 0.5,
        "reason": "Automatic transition to send document for signature"
    }
}

# Workflow events that trigger notifications
WORKFLOW_NOTIFICATION_EVENTS = [
    "APPLICATION_SUBMITTED",
    "APPLICATION_APPROVED",
    "APPLICATION_DENIED",
    "APPLICATION_REVISION_REQUESTED",
    "COMMITMENT_LETTER_SENT",
    "COMMITMENT_LETTER_ACCEPTED",
    "COMMITMENT_LETTER_DECLINED",
    "COUNTER_OFFER_MADE",
    "DOCUMENTS_SENT",
    "DOCUMENTS_FULLY_EXECUTED",
    "DOCUMENTS_EXPIRED",
    "QC_APPROVED",
    "FUNDING_COMPLETE",
    "DOCUMENT_SENT",
    "DOCUMENT_COMPLETED",
    "DOCUMENT_REJECTED",
    "DOCUMENT_EXPIRED",
    "ENROLLMENT_VERIFIED",
    "STIPULATIONS_COMPLETE",
    "PENDING_STIPULATIONS",
    "APPROVED_FOR_FUNDING",
    "DISBURSED"
]

# Workflow events that are logged for audit purposes
WORKFLOW_AUDIT_EVENTS = [
    "APPLICATION_SUBMITTED",
    "APPLICATION_ASSIGNED",
    "APPLICATION_APPROVED",
    "APPLICATION_DENIED",
    "APPLICATION_REVISION_REQUESTED",
    "COMMITMENT_LETTER_SENT",
    "COMMITMENT_LETTER_ACCEPTED",
    "COMMITMENT_LETTER_DECLINED",
    "COUNTER_OFFER_MADE",
    "DOCUMENTS_SENT",
    "DOCUMENTS_PARTIALLY_EXECUTED",
    "DOCUMENTS_FULLY_EXECUTED",
    "DOCUMENTS_EXPIRED",
    "QC_REVIEW_STARTED",
    "QC_APPROVED",
    "QC_REJECTED",
    "READY_TO_FUND",
    "FUNDING_COMPLETE",
    "DOCUMENT_GENERATED",
    "DOCUMENT_SENT",
    "DOCUMENT_PARTIALLY_SIGNED",
    "DOCUMENT_COMPLETED",
    "DOCUMENT_REJECTED",
    "DOCUMENT_EXPIRED",
    "ENROLLMENT_VERIFIED",
    "STIPULATION_REVIEW_STARTED",
    "STIPULATIONS_COMPLETE",
    "PENDING_STIPULATIONS",
    "FUNDING_APPROVAL_STARTED",
    "APPROVED_FOR_FUNDING",
    "SCHEDULED_FOR_DISBURSEMENT",
    "DISBURSED",
    "FUNDING_COMPLETE"
]

# SLA definitions for workflow states
WORKFLOW_SLA_DEFINITIONS = {
    WORKFLOW_TYPES['APPLICATION']: {
        APPLICATION_STATUS['SUBMITTED']: {
            "hours": 24,
            "description": "Application should be reviewed within 24 hours of submission"
        },
        APPLICATION_STATUS['IN_REVIEW']: {
            "hours": 48,
            "description": "Underwriting decision should be made within 48 hours of review start"
        },
        APPLICATION_STATUS['DOCUMENTS_SENT']: {
            "hours": 168,  # 7 days
            "description": "Documents should be signed within 7 days of being sent"
        },
        APPLICATION_STATUS['QC_REVIEW']: {
            "hours": 24,
            "description": "QC review should be completed within 24 hours"
        }
    },
    WORKFLOW_TYPES['DOCUMENT']: {
        DOCUMENT_STATUS['SENT']: {
            "hours": 168,  # 7 days
            "description": "Documents should be signed within 7 days of being sent"
        }
    },
    WORKFLOW_TYPES['FUNDING']: {
        FUNDING_STATUS['STIPULATION_REVIEW']: {
            "hours": 24,
            "description": "Stipulation review should be completed within 24 hours"
        },
        FUNDING_STATUS['APPROVED_FOR_FUNDING']: {
            "hours": 24,
            "description": "Approved loans should be disbursed within 24 hours"
        }
    }
}

# Workflow task types
WORKFLOW_TASK_TYPES = {
    "DOCUMENT_UPLOAD": "document_upload",
    "SIGNATURE_REQUIRED": "signature_required",
    "VERIFICATION_REQUIRED": "verification_required",
    "REVIEW_REQUIRED": "review_required",
    "APPROVAL_REQUIRED": "approval_required"
}

# Workflow task statuses
WORKFLOW_TASK_STATUS = {
    "PENDING": "pending", 
    "IN_PROGRESS": "in_progress",
    "COMPLETED": "completed",
    "CANCELLED": "cancelled"
}

# Required actions for different workflow states
REQUIRED_ACTIONS = {
    APPLICATION_STATUS['SUBMITTED']: [
        {
            "task_type": WORKFLOW_TASK_TYPES['REVIEW_REQUIRED'],
            "description": "Review application"
        }
    ],
    APPLICATION_STATUS['APPROVED']: [
        {
            "task_type": WORKFLOW_TASK_TYPES['APPROVAL_REQUIRED'],
            "description": "Review and approve commitment letter"
        }
    ],
    APPLICATION_STATUS['DOCUMENTS_SENT']: [
        {
            "task_type": WORKFLOW_TASK_TYPES['SIGNATURE_REQUIRED'],
            "description": "Sign loan documents"
        }
    ],
    APPLICATION_STATUS['FULLY_EXECUTED']: [
        {
            "task_type": WORKFLOW_TASK_TYPES['REVIEW_REQUIRED'],
            "description": "Perform QC review"
        }
    ],
    APPLICATION_STATUS['QC_APPROVED']: [
        {
            "task_type": WORKFLOW_TASK_TYPES['VERIFICATION_REQUIRED'],
            "description": "Verify enrollment"
        }
    ],
    DOCUMENT_STATUS['SENT']: [
        {
            "task_type": WORKFLOW_TASK_TYPES['SIGNATURE_REQUIRED'],
            "description": "Sign document"
        }
    ],
    FUNDING_STATUS['PENDING_ENROLLMENT']: [
        {
            "task_type": WORKFLOW_TASK_TYPES['VERIFICATION_REQUIRED'],
            "description": "Verify student enrollment"
        }
    ],
    FUNDING_STATUS['STIPULATION_REVIEW']: [
        {
            "task_type": WORKFLOW_TASK_TYPES['VERIFICATION_REQUIRED'],
            "description": "Verify stipulations are met"
        }
    ],
    FUNDING_STATUS['FUNDING_APPROVAL']: [
        {
            "task_type": WORKFLOW_TASK_TYPES['APPROVAL_REQUIRED'],
            "description": "Approve for funding"
        }
    ]
}