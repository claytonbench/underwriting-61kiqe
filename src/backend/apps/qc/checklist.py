"""
Implements the quality control checklist functionality for the loan management system.
This module provides utilities for generating, managing, and validating QC checklists based on application data, document verification, and stipulation requirements. The QC checklist is a critical component of the loan approval process that ensures all documentation is complete, accurate, and compliant before funding.
"""

import logging  # version: standard library

from .models import (  # Importing QCReview, QCChecklistItem, DocumentVerification, QCStipulationVerification
    QCReview,
    QCChecklistItem,
    DocumentVerification,
    QCStipulationVerification
)
from .constants import (  # Importing QC constants
    QC_CHECKLIST_CATEGORY,
    QC_DOCUMENT_VERIFICATION_ITEMS,
    QC_LOAN_VERIFICATION_ITEMS,
    QC_BORROWER_VERIFICATION_ITEMS,
    QC_SCHOOL_VERIFICATION_ITEMS,
    QC_STIPULATION_VERIFICATION_ITEMS,
    QC_COMPLIANCE_VERIFICATION_ITEMS,
    QC_VERIFICATION_STATUS
)
from apps.documents.models import Document  # Importing Document model
from apps.underwriting.models import Stipulation  # Importing Stipulation model
from apps.applications.models import LoanApplication  # Importing LoanApplication model

# Initialize logger
logger = logging.getLogger(__name__)


def generate_checklist_for_qc_review(qc_review: QCReview) -> bool:
    """
    Generates a complete checklist for a QC review based on application data.

    Args:
        qc_review (QCReview): The QCReview object for which to generate the checklist.

    Returns:
        bool: True if checklist was generated successfully, False otherwise.
    """
    try:
        # Get the application from qc_review
        application = qc_review.application

        # Generate document verification items
        generate_document_verification_items(qc_review)

        # Generate loan information verification items
        generate_loan_verification_items(qc_review)

        # Generate borrower information verification items
        generate_borrower_verification_items(qc_review)

        # Generate school information verification items
        generate_school_verification_items(qc_review)

        # Generate stipulation verification items
        generate_stipulation_verification_items(qc_review)

        # Generate compliance verification items
        generate_compliance_verification_items(qc_review)

        return True  # Return True if all items were generated successfully
    except Exception as e:
        logger.error(f"Failed to generate checklist for QC review {qc_review.id}: {e}")
        return False  # Return False if any item generation fails


def generate_document_verification_items(qc_review: QCReview) -> list:
    """
    Creates checklist items for document verification.

    Args:
        qc_review (QCReview): The QCReview object for which to generate document verification items.

    Returns:
        list: List of created QCChecklistItem objects.
    """
    try:
        # Get the application from qc_review
        application = qc_review.application

        # Get all documents associated with the application
        documents = application.get_documents()

        # Create document verification records for each document
        create_document_verifications(qc_review, documents)

        checklist_items = []
        # Create checklist items for each document verification item in QC_DOCUMENT_VERIFICATION_ITEMS
        for item_text in QC_DOCUMENT_VERIFICATION_ITEMS:
            checklist_item = create_checklist_item(qc_review, QC_CHECKLIST_CATEGORY['DOCUMENT_COMPLETENESS'], item_text)
            checklist_items.append(checklist_item)

        return checklist_items  # Return the list of created checklist items
    except Exception as e:
        logger.error(f"Failed to generate document verification items for QC review {qc_review.id}: {e}")
        return []


def generate_loan_verification_items(qc_review: QCReview) -> list:
    """
    Creates checklist items for loan information verification.

    Args:
        qc_review (QCReview): The QCReview object for which to generate loan verification items.

    Returns:
        list: List of created QCChecklistItem objects.
    """
    try:
        # Get the application from qc_review
        application = qc_review.application

        # Get loan details from the application
        loan_details = application.get_loan_details()

        # Get underwriting decision from the application
        underwriting_decision = application.get_underwriting_decision()

        checklist_items = []
        # Create checklist items for each loan verification item in QC_LOAN_VERIFICATION_ITEMS
        for item_text in QC_LOAN_VERIFICATION_ITEMS:
            checklist_item = create_checklist_item(qc_review, QC_CHECKLIST_CATEGORY['LOAN_INFORMATION'], item_text)
            checklist_items.append(checklist_item)

        return checklist_items  # Return the list of created checklist items
    except Exception as e:
        logger.error(f"Failed to generate loan verification items for QC review {qc_review.id}: {e}")
        return []


def generate_borrower_verification_items(qc_review: QCReview) -> list:
    """
    Creates checklist items for borrower information verification.

    Args:
        qc_review (QCReview): The QCReview object for which to generate borrower verification items.

    Returns:
        list: List of created QCChecklistItem objects.
    """
    try:
        # Get the application from qc_review
        application = qc_review.application

        # Get borrower and co-borrower profiles from the application
        borrower = application.borrower
        co_borrower = application.co_borrower

        checklist_items = []
        # Create checklist items for each borrower verification item in QC_BORROWER_VERIFICATION_ITEMS
        for item_text in QC_BORROWER_VERIFICATION_ITEMS:
            checklist_item = create_checklist_item(qc_review, QC_CHECKLIST_CATEGORY['BORROWER_INFORMATION'], item_text)
            checklist_items.append(checklist_item)

        return checklist_items  # Return the list of created checklist items
    except Exception as e:
        logger.error(f"Failed to generate borrower verification items for QC review {qc_review.id}: {e}")
        return []


def generate_school_verification_items(qc_review: QCReview) -> list:
    """
    Creates checklist items for school information verification.

    Args:
        qc_review (QCReview): The QCReview object for which to generate school verification items.

    Returns:
        list: List of created QCChecklistItem objects.
    """
    try:
        # Get the application from qc_review
        application = qc_review.application

        # Get school and program information from the application
        school = application.school
        program = application.program

        checklist_items = []
        # Create checklist items for each school verification item in QC_SCHOOL_VERIFICATION_ITEMS
        for item_text in QC_SCHOOL_VERIFICATION_ITEMS:
            checklist_item = create_checklist_item(qc_review, QC_CHECKLIST_CATEGORY['SCHOOL_INFORMATION'], item_text)
            checklist_items.append(checklist_item)

        return checklist_items  # Return the list of created checklist items
    except Exception as e:
        logger.error(f"Failed to generate school verification items for QC review {qc_review.id}: {e}")
        return []


def generate_stipulation_verification_items(qc_review: QCReview) -> list:
    """
    Creates checklist items for stipulation verification.

    Args:
        qc_review (QCReview): The QCReview object for which to generate stipulation verification items.

    Returns:
        list: List of created QCChecklistItem objects.
    """
    try:
        # Get the application from qc_review
        application = qc_review.application

        # Get underwriting decision from the application
        underwriting_decision = application.get_underwriting_decision()

        # Get stipulations from the underwriting decision
        stipulations = underwriting_decision.get_stipulations() if underwriting_decision else []

        # Create stipulation verification records for each stipulation
        create_stipulation_verifications(qc_review, stipulations)

        checklist_items = []
        # Create checklist items for each stipulation verification item in QC_STIPULATION_VERIFICATION_ITEMS
        for item_text in QC_STIPULATION_VERIFICATION_ITEMS:
            checklist_item = create_checklist_item(qc_review, QC_CHECKLIST_CATEGORY['STIPULATIONS'], item_text)
            checklist_items.append(checklist_item)

        return checklist_items  # Return the list of created checklist items
    except Exception as e:
        logger.error(f"Failed to generate stipulation verification items for QC review {qc_review.id}: {e}")
        return []


def generate_compliance_verification_items(qc_review: QCReview) -> list:
    """
    Creates checklist items for compliance verification.

    Args:
        qc_review (QCReview): The QCReview object for which to generate compliance verification items.

    Returns:
        list: List of created QCChecklistItem objects.
    """
    try:
        # Get the application from qc_review
        application = qc_review.application

        checklist_items = []
        # Create checklist items for each compliance verification item in QC_COMPLIANCE_VERIFICATION_ITEMS
        for item_text in QC_COMPLIANCE_VERIFICATION_ITEMS:
            checklist_item = create_checklist_item(qc_review, QC_CHECKLIST_CATEGORY['COMPLIANCE'], item_text)
            checklist_items.append(checklist_item)

        return checklist_items  # Return the list of created checklist items
    except Exception as e:
        logger.error(f"Failed to generate compliance verification items for QC review {qc_review.id}: {e}")
        return []


def create_document_verifications(qc_review: QCReview, documents: list) -> list:
    """
    Creates document verification records for all documents in an application.

    Args:
        qc_review (QCReview): The QCReview object to associate with the verifications.
        documents (list): List of Document objects to create verifications for.

    Returns:
        list: List of created DocumentVerification objects.
    """
    verification_records = []  # Initialize an empty list for verification records

    # For each document in documents:
    for document in documents:
        # Create a DocumentVerification object linking the document to the QC review
        verification_record = DocumentVerification(qc_review=qc_review, document=document)
        verification_records.append(verification_record)  # Add the verification record to the list

    # Bulk create all verification records in the database
    DocumentVerification.objects.bulk_create(verification_records)

    return verification_records  # Return the list of created verification records


def create_stipulation_verifications(qc_review: QCReview, stipulations: list) -> list:
    """
    Creates stipulation verification records for all stipulations in an application.

    Args:
        qc_review (QCReview): The QCReview object to associate with the verifications.
        stipulations (list): List of Stipulation objects to create verifications for.

    Returns:
        list: List of created QCStipulationVerification objects.
    """
    verification_records = []  # Initialize an empty list for verification records

    # For each stipulation in stipulations:
    for stipulation in stipulations:
        # Create a QCStipulationVerification object linking the stipulation to the QC review
        verification_record = QCStipulationVerification(qc_review=qc_review, stipulation=stipulation)
        verification_records.append(verification_record)  # Add the verification record to the list

    # Bulk create all verification records in the database
    QCStipulationVerification.objects.bulk_create(verification_records)

    return verification_records  # Return the list of created verification records


def create_checklist_item(qc_review: QCReview, category: str, item_text: str) -> QCChecklistItem:
    """
    Creates a single checklist item for a QC review.

    Args:
        qc_review (QCReview): The QCReview object to associate with the checklist item.
        category (str): The category of the checklist item.
        item_text (str): The text of the checklist item.

    Returns:
        QCChecklistItem: The created QCChecklistItem object.
    """
    # Create a new QCChecklistItem with the provided qc_review, category, and item_text
    checklist_item = QCChecklistItem(qc_review=qc_review, category=category, item_text=item_text)
    checklist_item.save()  # Save the checklist item to the database
    return checklist_item  # Return the created checklist item


def verify_checklist_item(checklist_item: QCChecklistItem, user: User, comments: str) -> bool:
    """
    Verifies a checklist item as part of the QC process.

    Args:
        checklist_item (QCChecklistItem): The checklist item to verify.
        user (User): The user verifying the checklist item.
        comments (str): Comments for the verification.

    Returns:
        bool: True if verification was successful, False otherwise.
    """
    return checklist_item.verify(user, comments)  # Call the verify method on the checklist_item with the user and comments


def reject_checklist_item(checklist_item: QCChecklistItem, user: User, comments: str) -> bool:
    """
    Rejects a checklist item as part of the QC process.

    Args:
        checklist_item (QCChecklistItem): The checklist item to reject.
        user (User): The user rejecting the checklist item.
        comments (str): Comments for the rejection.

    Returns:
        bool: True if rejection was successful, False otherwise.
    """
    return checklist_item.reject(user, comments)  # Call the reject method on the checklist_item with the user and comments


def waive_checklist_item(checklist_item: QCChecklistItem, user: User, comments: str) -> bool:
    """
    Waives a checklist item as part of the QC process.

    Args:
        checklist_item (QCChecklistItem): The checklist item to waive.
        user (User): The user waiving the checklist item.
        comments (str): Comments for the waiver.

    Returns:
        bool: True if waiver was successful, False otherwise.
    """
    return checklist_item.waive(user, comments)  # Call the waive method on the checklist_item with the user and comments


def verify_document(document_verification: DocumentVerification, user: User, comments: str) -> bool:
    """
    Verifies a document as part of the QC process.

    Args:
        document_verification (DocumentVerification): The document verification to verify.
        user (User): The user verifying the document.
        comments (str): Comments for the verification.

    Returns:
        bool: True if verification was successful, False otherwise.
    """
    return document_verification.verify(user, comments)  # Call the verify method on the document_verification with the user and comments


def reject_document(document_verification: DocumentVerification, user: User, comments: str) -> bool:
    """
    Rejects a document as part of the QC process.

    Args:
        document_verification (DocumentVerification): The document verification to reject.
        user (User): The user rejecting the document.
        comments (str): Comments for the rejection.

    Returns:
        bool: True if rejection was successful, False otherwise.
    """
    return document_verification.reject(user, comments)  # Call the reject method on the document_verification with the user and comments


def waive_document(document_verification: DocumentVerification, user: User, comments: str) -> bool:
    """
    Waives a document verification as part of the QC process.

    Args:
        document_verification (DocumentVerification): The document verification to waive.
        user (User): The user waiving the document.
        comments (str): Comments for the waiver.

    Returns:
        bool: True if waiver was successful, False otherwise.
    """
    return document_verification.waive(user, comments)  # Call the waive method on the document_verification with the user and comments


def verify_stipulation(stipulation_verification: QCStipulationVerification, user: User, comments: str) -> bool:
    """
    Verifies a stipulation as part of the QC process.

    Args:
        stipulation_verification (QCStipulationVerification): The stipulation verification to verify.
        user (User): The user verifying the stipulation.
        comments (str): Comments for the verification.

    Returns:
        bool: True if verification was successful, False otherwise.
    """
    return stipulation_verification.verify(user, comments)  # Call the verify method on the stipulation_verification with the user and comments


def reject_stipulation(stipulation_verification: QCStipulationVerification, user: User, comments: str) -> bool:
    """
    Rejects a stipulation as part of the QC process.

    Args:
        stipulation_verification (QCStipulationVerification): The stipulation verification to reject.
        user (User): The user rejecting the stipulation.
        comments (str): Comments for the rejection.

    Returns:
        bool: True if rejection was successful, False otherwise.
    """
    return stipulation_verification.reject(user, comments)  # Call the reject method on the stipulation_verification with the user and comments


def waive_stipulation(stipulation_verification: QCStipulationVerification, user: User, comments: str) -> bool:
    """
    Waives a stipulation verification as part of the QC process.

    Args:
        stipulation_verification (QCStipulationVerification): The stipulation verification to waive.
        user (User): The user waiving the stipulation.
        comments (str): Comments for the waiver.

    Returns:
        bool: True if waiver was successful, False otherwise.
    """
    return stipulation_verification.waive(user, comments)  # Call the waive method on the stipulation_verification with the user and comments


def get_checklist_completion_status(qc_review: QCReview) -> dict:
    """
    Gets the completion status of a QC review checklist.

    Args:
        qc_review (QCReview): The QCReview object to get the completion status for.

    Returns:
        dict: Dictionary with completion statistics by category.
    """
    # Initialize a dictionary for completion statistics
    completion_status = {}

    # Get all checklist items for the QC review
    checklist_items = qc_review.get_checklist_items()

    # Group checklist items by category
    items_by_category = {}
    for item in checklist_items:
        if item.category not in items_by_category:
            items_by_category[item.category] = []
        items_by_category[item.category].append(item)

    # For each category, calculate:
    for category, items in items_by_category.items():
        # Total items
        total_items = len(items)

        # Verified items
        verified_items = sum(1 for item in items if item.status == QC_VERIFICATION_STATUS['VERIFIED'])

        # Rejected items
        rejected_items = sum(1 for item in items if item.status == QC_VERIFICATION_STATUS['REJECTED'])

        # Waived items
        waived_items = sum(1 for item in items if item.status == QC_VERIFICATION_STATUS['WAIVED'])

        # Completion percentage
        completed_items = verified_items + rejected_items + waived_items
        completion_percentage = (completed_items / total_items) * 100 if total_items > 0 else 0

        completion_status[category] = {
            'total': total_items,
            'verified': verified_items,
            'rejected': rejected_items,
            'waived': waived_items,
            'completion_percentage': completion_percentage
        }

    # Add overall completion statistics
    total_checklist_items = checklist_items.count()
    total_document_verifications = qc_review.get_document_verifications().count()
    total_stipulation_verifications = qc_review.get_stipulation_verifications().count()

    completed_checklist_items = checklist_items.filter(status=QC_VERIFICATION_STATUS['VERIFIED']).count()
    completed_document_verifications = qc_review.get_document_verifications().filter(status=QC_VERIFICATION_STATUS['VERIFIED']).count()
    completed_stipulation_verifications = qc_review.get_stipulation_verifications().filter(status=QC_VERIFICATION_STATUS['VERIFIED']).count()

    total_items = total_checklist_items + total_document_verifications + total_stipulation_verifications
    total_completed = completed_checklist_items + completed_document_verifications + completed_stipulation_verifications

    overall_completion_percentage = (total_completed / total_items) * 100 if total_items > 0 else 0

    completion_status['overall'] = {
        'total': total_items,
        'completed': total_completed,
        'completion_percentage': overall_completion_percentage
    }

    return completion_status  # Return the completion statistics dictionary


class ChecklistValidator:
    """
    Utility class for validating QC checklists and determining if a QC review is ready for approval.
    """

    def __init__(self, qc_review: QCReview):
        """
        Initializes a new ChecklistValidator instance.

        Args:
            qc_review (QCReview): The QCReview object to validate.
        """
        self.qc_review = qc_review  # Store the qc_review reference
        self.validation_results = {}  # Initialize validation results dictionary

    def validate(self) -> dict:
        """
        Performs a complete validation of the QC checklist.

        Returns:
            dict: Validation results with issues found.
        """
        self.validation_results['document_verifications'] = self.validate_document_verifications()
        self.validation_results['checklist_items'] = self.validate_checklist_items()
        self.validation_results['stipulation_verifications'] = self.validate_stipulation_verifications()
        self.validation_results['ready_for_approval'] = self.is_ready_for_approval()
        return self.validation_results

    def validate_document_verifications(self) -> list:
        """
        Validates that all document verifications are complete.

        Returns:
            list: List of incomplete document verifications.
        """
        document_verifications = self.qc_review.get_document_verifications()
        incomplete_verifications = [
            verification for verification in document_verifications
            if verification.status == QC_VERIFICATION_STATUS['UNVERIFIED']
        ]
        return incomplete_verifications

    def validate_checklist_items(self) -> list:
        """
        Validates that all checklist items are complete.

        Returns:
            list: List of incomplete checklist items.
        """
        checklist_items = self.qc_review.get_checklist_items()
        incomplete_items = [
            item for item in checklist_items
            if item.status == QC_VERIFICATION_STATUS['UNVERIFIED']
        ]
        return incomplete_items

    def validate_stipulation_verifications(self) -> list:
        """
        Validates that all stipulation verifications are complete.

        Returns:
            list: List of incomplete stipulation verifications.
        """
        stipulation_verifications = self.qc_review.get_stipulation_verifications()
        incomplete_verifications = [
            verification for verification in stipulation_verifications
            if verification.status == QC_VERIFICATION_STATUS['UNVERIFIED']
        ]
        return incomplete_verifications

    def is_ready_for_approval(self) -> bool:
        """
        Determines if the QC review is ready for approval.

        Returns:
            bool: True if ready for approval, False otherwise.
        """
        if self.validate_document_verifications():
            return False
        if self.validate_checklist_items():
            return False
        if self.validate_stipulation_verifications():
            return False
        return True

    def get_validation_summary(self) -> dict:
        """
        Gets a summary of validation results.

        Returns:
            dict: Summary of validation results.
        """
        if not self.validation_results:
            self.validate()

        summary = {
            'document_verifications_incomplete': len(self.validation_results.get('document_verifications', [])),
            'checklist_items_incomplete': len(self.validation_results.get('checklist_items', [])),
            'stipulation_verifications_incomplete': len(self.validation_results.get('stipulation_verifications', [])),
            'ready_for_approval': self.validation_results.get('ready_for_approval', False)
        }
        return summary