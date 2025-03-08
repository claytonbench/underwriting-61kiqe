# src/backend/apps/applications/services.py
"""
Service layer for loan application management in the loan management system. Provides high-level business logic for creating, updating, submitting, and managing loan applications throughout their lifecycle. Acts as an intermediary between API views and data models, implementing core application workflows and business rules.
"""

import logging  # Import logging utilities for error and activity logging
from datetime import datetime  # For date and time operations in application processing
from django.db import transaction  # For database transaction management in application operations
from django.core.exceptions import ValidationError  # For raising validation errors in service methods
from decimal import Decimal  # For precise decimal calculations in financial operations

from .models import LoanApplication  # Import LoanApplication model for application operations
from .models import LoanDetails  # Import LoanDetails model for financial details operations
from .models import ApplicationDocument  # Import ApplicationDocument model for document operations
from .models import ApplicationStatusHistory  # Import ApplicationStatusHistory model for status tracking
from .models import ApplicationNote  # Import ApplicationNote model for note management
from ..users.models import User  # Import User model for borrower and co-borrower relationships
from ..users.models import BorrowerProfile  # Import BorrowerProfile model for borrower information
from ..users.models import EmploymentInfo  # Import EmploymentInfo model for employment information
from ..schools.models import School  # Import School model for school relationships
from ..schools.models import Program  # Import Program model for program relationships
from .validators import validate_application_editable  # Import function to validate if application is in editable state
from .validators import validate_application_submission  # Import function to validate application submission data
from .validators import validate_borrower_info  # Import function to validate borrower information
from .validators import validate_loan_details  # Import function to validate loan details
from utils.constants import APPLICATION_STATUS  # Import application status constants
from .constants import APPLICATION_EDITABLE_STATUSES  # Import list of application statuses that allow editing
from utils.constants import DOCUMENT_TYPES  # Import document type constants
from ..notifications.services import NotificationService  # Import notification service for sending application-related notifications
from ..notifications.services import EventNotificationManager  # Import notification manager for handling application events
from ..underwriting.services import UnderwritingService  # Import underwriting service for adding applications to the underwriting queue
from ..documents.services import DocumentService  # Import document service for handling application documents

logger = logging.getLogger(__name__)
notification_service = NotificationService()
event_notification_manager = EventNotificationManager(notification_service)
underwriting_service = UnderwritingService()
document_service = DocumentService()


def get_application_by_id(application_id):
    """Retrieves a loan application by its ID

    Args:
        application_id (uuid.UUID): application_id

    Returns:
        LoanApplication: Application object if found, None otherwise
    """
    try:
        application = LoanApplication.objects.get(id=application_id)
        return application
    except LoanApplication.DoesNotExist:
        return None
    except Exception as e:
        logger.error(f"Error retrieving application: {e}")
        return None


def get_applications_for_borrower(borrower):
    """Retrieves all applications for a specific borrower

    Args:
        borrower (User): borrower

    Returns:
        QuerySet: QuerySet of LoanApplication objects
    """
    try:
        applications = LoanApplication.objects.filter(borrower=borrower)
        return applications
    except Exception as e:
        logger.error(f"Error retrieving applications for borrower: {e}")
        return LoanApplication.objects.none()


def get_applications_for_school(school):
    """Retrieves all applications for a specific school

    Args:
        school (School): school

    Returns:
        QuerySet: QuerySet of LoanApplication objects
    """
    try:
        applications = LoanApplication.objects.filter(school=school)
        return applications
    except Exception as e:
        logger.error(f"Error retrieving applications for school: {e}")
        return LoanApplication.objects.none()


def get_applications_by_status(status):
    """Retrieves applications filtered by status

    Args:
        status (str): status

    Returns:
        QuerySet: QuerySet of LoanApplication objects
    """
    try:
        if status not in APPLICATION_STATUS.values():
            raise ValueError(f"Invalid application status: {status}")
        applications = LoanApplication.objects.filter(status=status)
        return applications
    except Exception as e:
        logger.error(f"Error retrieving applications by status: {e}")
        return LoanApplication.objects.none()


@transaction.atomic
def create_application(borrower, co_borrower, school, program, application_type, relationship_type, created_by):
    """Creates a new loan application

    Args:
        borrower (User): borrower
        co_borrower (User): co_borrower
        school (School): school
        program (Program): program
        application_type (str): application_type
        relationship_type (str): relationship_type
        created_by (User): created_by

    Returns:
        LoanApplication: The created application object
    """
    try:
        application = LoanApplication.objects.create(
            borrower=borrower,
            co_borrower=co_borrower,
            school=school,
            program=program,
            application_type=application_type,
            relationship_type=relationship_type,
            created_by=created_by
        )
        logger.info(f"Created application {application.id} for borrower {borrower.email}")
        return application
    except Exception as e:
        logger.error(f"Error creating application: {e}")
        raise


@transaction.atomic
def update_application(application, update_data, updated_by):
    """Updates an existing loan application

    Args:
        application (LoanApplication): application
        update_data (dict): update_data
        updated_by (User): updated_by

    Returns:
        LoanApplication: The updated application object
    """
    try:
        validate_application_editable(application)

        for key, value in update_data.items():
            setattr(application, key, value)

        application.save(user=updated_by)
        logger.info(f"Updated application {application.id} by user {updated_by.email}")
        return application
    except Exception as e:
        logger.error(f"Error updating application: {e}")
        raise


@transaction.atomic
def submit_application(application, submitted_by):
    """Submits a loan application for review

    Args:
        application (LoanApplication): application
        submitted_by (User): submitted_by

    Returns:
        bool: True if submission was successful, False otherwise
    """
    try:
        validate_application_editable(application)
        loan_details = application.get_loan_details()
        borrower_profile = BorrowerProfile.objects.get(user=application.borrower)
        validate_application_submission(application, borrower_profile, loan_details)

        application.submit()
        event_notification_manager.handle_application_submitted(application)
        underwriting_service.add_to_queue(application)

        logger.info(f"Submitted application {application.id} by user {submitted_by.email}")
        return True
    except Exception as e:
        logger.error(f"Error submitting application: {e}")
        raise


@transaction.atomic
def create_loan_details(application, tuition_amount, deposit_amount, other_funding, requested_amount, start_date, completion_date):
    """Creates or updates loan details for an application

    Args:
        application (LoanApplication): application
        tuition_amount (Decimal): tuition_amount
        deposit_amount (Decimal): deposit_amount
        other_funding (Decimal): other_funding
        requested_amount (Decimal): requested_amount
        start_date (date): start_date
        completion_date (date): completion_date

    Returns:
        LoanDetails: The created or updated LoanDetails object
    """
    try:
        loan_details = application.get_loan_details()
        if loan_details:
            loan_details.tuition_amount = tuition_amount
            loan_details.deposit_amount = deposit_amount
            loan_details.other_funding = other_funding
            loan_details.requested_amount = requested_amount
            loan_details.start_date = start_date
            loan_details.completion_date = completion_date
            loan_details.save()
            logger.info(f"Updated loan details for application {application.id}")
        else:
            loan_details = LoanDetails.objects.create(
                application=application,
                tuition_amount=tuition_amount,
                deposit_amount=deposit_amount,
                other_funding=other_funding,
                requested_amount=requested_amount,
                start_date=start_date,
                completion_date=completion_date
            )
            logger.info(f"Created loan details for application {application.id}")
        return loan_details
    except Exception as e:
        logger.error(f"Error creating/updating loan details: {e}")
        raise


@transaction.atomic
def update_application_status(application, new_status, updated_by, comments):
    """Updates the status of a loan application

    Args:
        application (LoanApplication): application
        new_status (str): new_status
        updated_by (User): updated_by
        comments (str): comments

    Returns:
        bool: True if status was updated, False otherwise
    """
    try:
        if new_status not in APPLICATION_STATUS.values():
            raise ValueError(f"Invalid application status: {new_status}")

        if application.status == new_status:
            return True

        application.status = new_status
        application.save(user=updated_by, status_comment=comments)
        document_service.handle_application_status_change(application)

        logger.info(f"Updated application {application.id} status to {new_status} by user {updated_by.email}")
        return True
    except Exception as e:
        logger.error(f"Error updating application status: {e}")
        raise


@transaction.atomic
def upload_application_document(application, document_type, document_file, uploaded_by):
    """Uploads a document for a loan application

    Args:
        application (LoanApplication): application
        document_type (str): document_type
        document_file (file): document_file
        uploaded_by (User): uploaded_by

    Returns:
        ApplicationDocument: The created ApplicationDocument object
    """
    try:
        if document_type not in DOCUMENT_TYPES.values():
            raise ValueError(f"Invalid document type: {document_type}")

        # Generate a unique file name for the document
        file_name = f"{application.id}_{document_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

        # Upload the document file to storage and get the file path
        file_path = document_file.name

        document = ApplicationDocument.objects.create(
            application=application,
            document_type=document_type,
            file_name=file_name,
            file_path=file_path,
            uploaded_by=uploaded_by,
            status='uploaded'
        )

        logger.info(f"Uploaded document {document.id} for application {application.id} by user {uploaded_by.email}")
        return document
    except Exception as e:
        logger.error(f"Error uploading application document: {e}")
        raise


def get_application_documents(application, document_type):
    """Retrieves all documents for a loan application

    Args:
        application (LoanApplication): application
        document_type (str): document_type

    Returns:
        QuerySet: QuerySet of ApplicationDocument objects
    """
    try:
        documents = ApplicationDocument.objects.filter(application=application)
        if document_type:
            documents = documents.filter(document_type=document_type)
        return documents
    except Exception as e:
        logger.error(f"Error retrieving application documents: {e}")
        return ApplicationDocument.objects.none()


def create_application_note(application, note_text, created_by, is_internal):
    """Creates a note for a loan application

    Args:
        application (LoanApplication): application
        note_text (str): note_text
        created_by (User): created_by
        is_internal (bool): is_internal

    Returns:
        ApplicationNote: The created ApplicationNote object
    """
    try:
        note = ApplicationNote.objects.create(
            application=application,
            note_text=note_text,
            created_by=created_by,
            is_internal=is_internal
        )
        logger.info(f"Created note {note.id} for application {application.id} by user {created_by.email}")
        return note
    except Exception as e:
        logger.error(f"Error creating application note: {e}")
        raise


def get_application_notes(application, include_internal):
    """Retrieves notes for a loan application

    Args:
        application (LoanApplication): application
        include_internal (bool): include_internal

    Returns:
        QuerySet: QuerySet of ApplicationNote objects
    """
    try:
        notes = ApplicationNote.objects.filter(application=application)
        if not include_internal:
            notes = notes.filter(is_internal=False)
        notes = notes.order_by('-created_at')
        return notes
    except Exception as e:
        logger.error(f"Error retrieving application notes: {e}")
        return ApplicationNote.objects.none()


def get_application_status_history(application):
    """Retrieves status history for a loan application

    Args:
        application (LoanApplication): application

    Returns:
        QuerySet: QuerySet of ApplicationStatusHistory objects
    """
    try:
        status_history = ApplicationStatusHistory.objects.filter(application=application).order_by('-changed_at')
        return status_history
    except Exception as e:
        logger.error(f"Error retrieving application status history: {e}")
        return ApplicationStatusHistory.objects.none()


def calculate_loan_amount(tuition_amount, deposit_amount, other_funding):
    """Calculates the available loan amount based on tuition and other factors

    Args:
        tuition_amount (Decimal): tuition_amount
        deposit_amount (Decimal): deposit_amount
        other_funding (Decimal): other_funding

    Returns:
        Decimal: The calculated available loan amount
    """
    try:
        available_loan_amount = tuition_amount - deposit_amount - other_funding
        return max(available_loan_amount, Decimal('0.00'))
    except Exception as e:
        logger.error(f"Error calculating loan amount: {e}")
        return Decimal('0.00')


def get_application_form_progress(application):
    """Calculates the completion progress of an application form

    Args:
        application (LoanApplication): application

    Returns:
        dict: Dictionary with progress information
    """
    try:
        return {}
    except Exception as e:
        logger.error(f"Error calculating application form progress: {e}")
        return {}


class ApplicationService:
    """
    Service class that encapsulates loan application business logic
    """

    def __init__(self):
        """
        Initializes the application service with required dependencies
        """
        self.logger = logging.getLogger(__name__)
        self.notification_service = NotificationService()
        self.event_notification_manager = EventNotificationManager(self.notification_service)
        self.underwriting_service = UnderwritingService()
        self.document_service = DocumentService()
        self.logger.info("ApplicationService initialized")

    def get_application(self, application_id):
        """Retrieves an application by ID

        Args:
            application_id (uuid.UUID): application_id

        Returns:
            LoanApplication: Application object if found, None otherwise
        """
        return get_application_by_id(application_id)

    def get_borrower_applications(self, borrower):
        """Gets applications for a borrower

        Args:
            borrower (User): borrower

        Returns:
            QuerySet: QuerySet of LoanApplication objects
        """
        return get_applications_for_borrower(borrower)

    def get_school_applications(self, school):
        """Gets applications for a school

        Args:
            school (School): school

        Returns:
            QuerySet: QuerySet of LoanApplication objects
        """
        return get_applications_for_school(school)

    def filter_by_status(self, status):
        """Filters applications by status

        Args:
            status (str): status

        Returns:
            QuerySet: QuerySet of LoanApplication objects
        """
        return get_applications_by_status(status)

    def create_application(self, borrower, co_borrower, school, program, application_type, relationship_type, created_by):
        """Creates a new application

        Args:
            borrower (User): borrower
            co_borrower (User): co_borrower
            school (School): school
            program (Program): program
            application_type (str): application_type
            relationship_type (str): relationship_type
            created_by (User): created_by

        Returns:
            LoanApplication: The created application object
        """
        return create_application(borrower, co_borrower, school, program, application_type, relationship_type, created_by)

    def update_application(self, application, update_data, updated_by):
        """Updates an existing application

        Args:
            application (LoanApplication): application
            update_data (dict): update_data
            updated_by (User): updated_by

        Returns:
            LoanApplication: The updated application object
        """
        return update_application(application, update_data, updated_by)

    def submit_application(self, application, submitted_by):
        """Submits an application for review

        Args:
            application (LoanApplication): application
            submitted_by (User): submitted_by

        Returns:
            bool: True if submission was successful, False otherwise
        """
        return submit_application(application, submitted_by)

    def create_loan_details(self, application, tuition_amount, deposit_amount, other_funding, requested_amount, start_date, completion_date):
        """Creates or updates loan details

        Args:
            application (LoanApplication): application
            tuition_amount (Decimal): tuition_amount
            deposit_amount (Decimal): deposit_amount
            other_funding (Decimal): other_funding
            requested_amount (Decimal): requested_amount
            start_date (date): start_date
            completion_date (date): completion_date

        Returns:
            LoanDetails: The created or updated LoanDetails object
        """
        return create_loan_details(application, tuition_amount, deposit_amount, other_funding, requested_amount, start_date, completion_date)

    def update_status(self, application, new_status, updated_by, comments):
        """Updates application status

        Args:
            application (LoanApplication): application
            new_status (str): new_status
            updated_by (User): updated_by
            comments (str): comments

        Returns:
            bool: True if status was updated, False otherwise
        """
        return update_application_status(application, new_status, updated_by, comments)

    def upload_document(self, application, document_type, document_file, uploaded_by):
        """Uploads a document for an application

        Args:
            application (LoanApplication): application
            document_type (str): document_type
            document_file (file): document_file
            uploaded_by (User): uploaded_by

        Returns:
            ApplicationDocument: The created ApplicationDocument object
        """
        return upload_application_document(application, document_type, document_file, uploaded_by)

    def get_documents(self, application, document_type):
        """Gets documents for an application

        Args:
            application (LoanApplication): application
            document_type (str): document_type

        Returns:
            QuerySet: QuerySet of ApplicationDocument objects
        """
        return get_application_documents(application, document_type)

    def create_note(self, application, note_text, created_by, is_internal):
        """Creates a note for an application

        Args:
            application (LoanApplication): application
            note_text (str): note_text
            created_by (User): created_by
            is_internal (bool): is_internal

        Returns:
            ApplicationNote: The created ApplicationNote object
        """
        return create_application_note(application, note_text, created_by, is_internal)

    def get_notes(self, application, include_internal):
        """Gets notes for an application

        Args:
            application (LoanApplication): application
            include_internal (bool): include_internal

        Returns:
            QuerySet: QuerySet of ApplicationNote objects
        """
        return get_application_notes(application, include_internal)

    def get_status_history(self, application):
        """Gets status history for an application

        Args:
            application (LoanApplication): application

        Returns:
            QuerySet: QuerySet of ApplicationStatusHistory objects
        """
        return get_application_status_history(application)

    def calculate_loan_amount(self, tuition_amount, deposit_amount, other_funding):
        """Calculates available loan amount

        Args:
            tuition_amount (Decimal): tuition_amount
            deposit_amount (Decimal): deposit_amount
            other_funding (Decimal): other_funding

        Returns:
            Decimal: The calculated available loan amount
        """
        return calculate_loan_amount(tuition_amount, deposit_amount, other_funding)

    def get_form_progress(self, application):
        """Gets application form completion progress

        Args:
            application (LoanApplication): application

        Returns:
            dict: Dictionary with progress information
        """
        return get_application_form_progress(application)


class ApplicationServiceError(Exception):
    """Custom exception class for application service errors"""

    def __init__(self, message, original_exception=None):
        """Initializes the ApplicationServiceError with a message and original exception"""
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception
        logger.error(f"Application service error: {message}", exc_info=original_exception)

    def __str__(self):
        """Returns a string representation of the error"""
        if self.original_exception:
            return f"{self.message} (Original error: {str(self.original_exception)})"
        return self.message


application_service = ApplicationService()