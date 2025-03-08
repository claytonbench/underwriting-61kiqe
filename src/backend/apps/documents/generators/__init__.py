"""
Initialization module for document generators in the loan management system.
This module exports the document generator classes for different document types, making them available for import from the generators package. It serves as the entry point for accessing document generation functionality throughout the application.
"""
import logging  # version standard library

from .base import BaseDocumentGenerator, DocumentGenerationError  # src/backend/apps/documents/generators/base.py
from .commitment_letter import CommitmentLetterGenerator  # src/backend/apps/documents/generators/commitment_letter.py
from .loan_agreement import LoanAgreementGenerator  # src/backend/apps/documents/generators/loan_agreement.py
from .disclosure_forms import DisclosureFormGenerator  # src/backend/apps/documents/generators/disclosure_forms.py
# Get logger for this module
logger = logging.getLogger('document_generators')


__all__ = [
    'BaseDocumentGenerator',
    'DocumentGenerationError',
    'CommitmentLetterGenerator',
    'LoanAgreementGenerator',
    'DisclosureFormGenerator',
]