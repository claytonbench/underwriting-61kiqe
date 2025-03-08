"""
Constants for the document management system.

This module defines constants used throughout the document management system,
including document types, statuses, signature statuses, and various mappings
for document generation and e-signature integration.
"""

# Document types used in the system
DOCUMENT_TYPES = {
    'COMMITMENT_LETTER': 'commitment_letter',
    'LOAN_AGREEMENT': 'loan_agreement',
    'DISCLOSURE_FORM': 'disclosure_form',
    'TRUTH_IN_LENDING': 'truth_in_lending',
    'PROMISSORY_NOTE': 'promissory_note',
    'ENROLLMENT_AGREEMENT': 'enrollment_agreement',
    'INCOME_VERIFICATION': 'income_verification',
    'IDENTITY_VERIFICATION': 'identity_verification',
    'DISBURSEMENT_AUTHORIZATION': 'disbursement_authorization',
}

# Document status tracking throughout the document lifecycle
DOCUMENT_STATUS = {
    'DRAFT': 'draft',
    'GENERATED': 'generated',
    'SENT': 'sent',
    'SIGNED': 'signed',
    'COMPLETED': 'completed',
    'EXPIRED': 'expired',
    'VOIDED': 'voided',
    'DECLINED': 'declined',
    'ERROR': 'error',
}

# Document package types for grouping related documents
DOCUMENT_PACKAGE_TYPES = {
    'APPLICATION': 'application',
    'APPROVAL': 'approval',
    'LOAN_AGREEMENT': 'loan_agreement',
    'DISCLOSURE': 'disclosure',
    'FUNDING': 'funding',
}

# Signature status tracking throughout the e-signature process
SIGNATURE_STATUS = {
    'PENDING': 'pending',
    'SENT': 'sent',
    'DELIVERED': 'delivered',
    'SIGNED': 'signed',
    'COMPLETED': 'completed',
    'DECLINED': 'declined',
    'VOIDED': 'voided',
    'EXPIRED': 'expired',
    'ERROR': 'error',
}

# Signer types identifying different roles in the signing process
SIGNER_TYPES = {
    'BORROWER': 'borrower',
    'CO_BORROWER': 'co_borrower',
    'SCHOOL': 'school',
    'LENDER': 'lender',
}

# Document field types for form fields in documents
DOCUMENT_FIELD_TYPES = {
    'SIGNATURE': 'signature',
    'DATE': 'date',
    'TEXT': 'text',
    'CHECKBOX': 'checkbox',
    'RADIO': 'radio',
    'DROPDOWN': 'dropdown',
    'INITIAL': 'initial',
    'ATTACHMENT': 'attachment',
}

# Number of days before document packages expire if not completed
DOCUMENT_EXPIRATION_DAYS = 90

# Mapping document types to their template file paths
DOCUMENT_TEMPLATE_PATHS = {
    'commitment_letter': 'templates/documents/commitment_letter.html',
    'loan_agreement': 'templates/documents/loan_agreement.html',
    'disclosure_form': 'templates/documents/disclosure_form.html',
    'truth_in_lending': 'templates/documents/truth_in_lending.html',
    'promissory_note': 'templates/documents/promissory_note.html',
    'enrollment_agreement': 'templates/documents/enrollment_agreement.html',
    'disbursement_authorization': 'templates/documents/disbursement_authorization.html',
}

# Mapping document types to their output storage paths
DOCUMENT_OUTPUT_PATHS = {
    'commitment_letter': 'documents/commitment_letters/',
    'loan_agreement': 'documents/loan_agreements/',
    'disclosure_form': 'documents/disclosures/',
    'truth_in_lending': 'documents/disclosures/',
    'promissory_note': 'documents/notes/',
    'enrollment_agreement': 'documents/enrollment/',
    'disbursement_authorization': 'documents/funding/',
}

# Mapping document types to their required template variables
DOCUMENT_TEMPLATE_VARIABLES = {
    'commitment_letter': [
        'borrower', 'co_borrower', 'school', 'program', 'loan',
        'approved_amount', 'interest_rate', 'term_months', 
        'stipulations', 'current_date'
    ],
    'loan_agreement': [
        'borrower', 'co_borrower', 'school', 'program', 'loan',
        'approved_amount', 'interest_rate', 'term_months', 
        'payment_schedule', 'current_date'
    ],
    'disclosure_form': [
        'borrower', 'co_borrower', 'school', 'program', 'loan', 'current_date'
    ],
    'truth_in_lending': [
        'borrower', 'co_borrower', 'school', 'program', 'loan',
        'approved_amount', 'interest_rate', 'term_months', 
        'payment_schedule', 'current_date'
    ],
    'promissory_note': [
        'borrower', 'co_borrower', 'school', 'program', 'loan',
        'approved_amount', 'interest_rate', 'term_months', 
        'payment_schedule', 'current_date'
    ],
}

# Defining the signing sequence for different document types
DOCUMENT_SIGNING_SEQUENCE = {
    'commitment_letter': ['SCHOOL'],
    'loan_agreement': ['BORROWER', 'CO_BORROWER', 'SCHOOL', 'LENDER'],
    'disclosure_form': ['BORROWER', 'CO_BORROWER'],
    'truth_in_lending': ['BORROWER', 'CO_BORROWER'],
    'promissory_note': ['BORROWER', 'CO_BORROWER', 'LENDER'],
    'enrollment_agreement': ['BORROWER', 'SCHOOL'],
    'disbursement_authorization': ['SCHOOL', 'LENDER'],
}

# Defining the required signers for different document types
DOCUMENT_REQUIRED_SIGNERS = {
    'commitment_letter': ['SCHOOL'],
    'loan_agreement': ['BORROWER', 'SCHOOL', 'LENDER'],
    'disclosure_form': ['BORROWER'],
    'truth_in_lending': ['BORROWER'],
    'promissory_note': ['BORROWER', 'LENDER'],
    'enrollment_agreement': ['BORROWER', 'SCHOOL'],
    'disbursement_authorization': ['SCHOOL', 'LENDER'],
}

# Mapping DocuSign envelope statuses to internal signature statuses
DOCUSIGN_ENVELOPE_STATUS_MAPPING = {
    'created': 'PENDING',
    'sent': 'SENT',
    'delivered': 'DELIVERED',
    'completed': 'COMPLETED',
    'declined': 'DECLINED',
    'voided': 'VOIDED',
    'expired': 'EXPIRED',
}

# Mapping DocuSign recipient statuses to internal signature statuses
DOCUSIGN_RECIPIENT_STATUS_MAPPING = {
    'created': 'PENDING',
    'sent': 'SENT',
    'delivered': 'DELIVERED',
    'signed': 'SIGNED',
    'completed': 'COMPLETED',
    'declined': 'DECLINED',
    'voided': 'VOIDED',
    'expired': 'EXPIRED',
}

# Number of days between signature reminder notifications
REMINDER_INTERVAL_DAYS = 3

# Maximum number of signature reminders to send before escalation
MAX_REMINDERS = 5