"""
Provides service functions for document management in the loan management system,
including document generation, e-signature integration, document package management,
and signature tracking. This module serves as the business logic layer between the
API views and the document-related models, implementing the core document management functionality.
"""

import logging  # Import logging utilities for error and activity logging
from datetime import datetime  # Date and time utilities for document expiration and timestamps
import uuid  # Generate unique identifiers for documents
import os  # Operating system interfaces for path handling
from django.db import transaction  # Database transaction management for document operations

from .models import Document  # Import Document model for document operations
from .models import DocumentTemplate  # Import DocumentTemplate model for template operations
from .models import DocumentPackage  # Import DocumentPackage model for package operations
from .models import SignatureRequest  # Import SignatureRequest model for signature operations
from .models import DocumentField  # Import DocumentField model for document field operations
from apps.applications.models import LoanApplication  # Import LoanApplication model for application data
from .storage import document_storage  # Import document storage singleton instance
from .docusign import DocuSignService  # Import DocuSign service for e-signature operations
from .docusign import docusign_service  # Import DocuSign service singleton instance
from .generators.base import BaseDocumentGenerator  # Import base document generator class
from .generators.base import DocumentGenerationError  # Import document generation error class
from .generators.commitment_letter import CommitmentLetterGenerator  # Import commitment letter generator class
from .generators.loan_agreement import LoanAgreementGenerator  # Import loan agreement generator class
from .generators.disclosure_forms import DisclosureFormsGenerator  # Import disclosure forms generator class
from .constants import DOCUMENT_TYPES  # Import document type constants
from .constants import DOCUMENT_STATUS  # Import document status constants
from .constants import DOCUMENT_PACKAGE_TYPES  # Import document package type constants
from .constants import SIGNATURE_STATUS  # Import signature status constants
from .constants import SIGNER_TYPES  # Import signer type constants
from .constants import DOCUMENT_SIGNING_SEQUENCE  # Import document signing sequence mappings
from .constants import DOCUMENT_REQUIRED_SIGNERS  # Import document required signers mappings

logger = logging.getLogger('document_services')

DOCUMENT_GENERATOR_MAPPING = {
    DOCUMENT_TYPES['COMMITMENT_LETTER']: CommitmentLetterGenerator,
    DOCUMENT_TYPES['LOAN_AGREEMENT']: LoanAgreementGenerator,
    DOCUMENT_TYPES['DISCLOSURE_FORM']: DisclosureFormsGenerator,
}


class DocumentServiceError(Exception):
    """Custom exception class for document service-related errors."""

    def __init__(self, message, original_exception=None):
        """Initializes the DocumentServiceError with a message and original exception"""
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception
        logger.error(f"Document service error: {message}", exc_info=original_exception)

    def __str__(self):
        """Returns a string representation of the error"""
        if self.original_exception:
            return f"{self.message} (Original error: {str(self.original_exception)})"
        return self.message


def generate_document(document_type, application, generated_by, additional_context=None):
    """Generates a document of the specified type for a loan application

    Args:
        document_type (str): Type of document to generate
        application (LoanApplication): Loan application object
        generated_by (User): User object generating the document
        additional_context (dict): Additional context for template rendering

    Returns:
        Document: Generated Document object
    """
    try:
        if document_type not in DOCUMENT_GENERATOR_MAPPING:
            raise ValueError(f"Unsupported document type: {document_type}")

        generator_class = DOCUMENT_GENERATOR_MAPPING[document_type]
        generator = generator_class()

        document = generator.generate(application, generated_by, additional_context)
        logger.info(f"Document generated successfully: {document.id}")
        return document
    except Exception as e:
        logger.error(f"Error generating document: {e}", exc_info=True)
        raise


@transaction.atomic
def generate_document_package(package_type, application, generated_by, additional_context=None):
    """Generates a package of related documents for a loan application

    Args:
        package_type (str): Type of document package to generate
        application (LoanApplication): Loan application object
        generated_by (User): User object generating the document package
        additional_context (dict): Additional context for template rendering

    Returns:
        DocumentPackage: Generated DocumentPackage object with associated documents
    """
    try:
        if package_type not in DOCUMENT_PACKAGE_TYPES:
            raise ValueError(f"Unsupported document package type: {package_type}")

        # Create or get an existing DocumentPackage for the application and package_type
        document_package, created = DocumentPackage.objects.get_or_create(
            application=application,
            package_type=package_type,
        )

        # Determine which document types should be included in the package
        document_types = []
        if package_type == DOCUMENT_PACKAGE_TYPES['APPLICATION']:
            document_types = [DOCUMENT_TYPES['DISCLOSURE_FORM']]
        elif package_type == DOCUMENT_PACKAGE_TYPES['APPROVAL']:
            document_types = [DOCUMENT_TYPES['COMMITMENT_LETTER']]
        elif package_type == DOCUMENT_PACKAGE_TYPES['LOAN_AGREEMENT']:
            document_types = [DOCUMENT_TYPES['LOAN_AGREEMENT'], DOCUMENT_TYPES['TRUTH_IN_LENDING']]
        elif package_type == DOCUMENT_PACKAGE_TYPES['FUNDING']:
            document_types = [DOCUMENT_TYPES['DISBURSEMENT_AUTHORIZATION']]

        # For each document type, generate the document
        documents = []
        for document_type in document_types:
            document = generate_document(document_type, application, generated_by, additional_context)
            documents.append(document)

        # Update the package status based on document statuses
        document_package.update_status()

        logger.info(f"Document package generated successfully: {document_package.id}")
        return document_package
    except Exception as e:
        logger.error(f"Error generating document package: {e}", exc_info=True)
        raise


def get_document_by_id(document_id):
    """Retrieves a document by its ID

    Args:
        document_id (str): ID of the document to retrieve

    Returns:
        Document: Document object if found, None otherwise
    """
    try:
        return Document.objects.get(id=document_id)
    except Document.DoesNotExist:
        return None
    except Exception as e:
        logger.error(f"Error retrieving document: {e}", exc_info=True)
        return None


def get_document_package_by_id(package_id):
    """Retrieves a document package by its ID

    Args:
        package_id (str): ID of the document package to retrieve

    Returns:
        DocumentPackage: DocumentPackage object if found, None otherwise
    """
    try:
        return DocumentPackage.objects.get(id=package_id)
    except DocumentPackage.DoesNotExist:
        return None
    except Exception as e:
        logger.error(f"Error retrieving document package: {e}", exc_info=True)
        return None


def get_document_content(document):
    """Retrieves the content of a document

    Args:
        document (Document): Document object

    Returns:
        bytes: Document content as bytes
    """
    try:
        return document.get_content()
    except Exception as e:
        logger.error(f"Error retrieving document content: {e}", exc_info=True)
        raise


def get_document_download_url(document, expiry_seconds=3600):
    """Generates a download URL for a document

    Args:
        document (Document): Document object
        expiry_seconds (int): Expiry time for the URL in seconds

    Returns:
        str: Presigned URL for downloading the document
    """
    try:
        return document.get_download_url(expiry_seconds)
    except Exception as e:
        logger.error(f"Error generating download URL: {e}", exc_info=True)
        raise


@transaction.atomic
def create_signature_request(document, signers, email_subject, email_body):
    """Creates a signature request for a document

    Args:
        document (Document): The document to send for signature
        signers (list): List of dictionaries containing signer information
                       Each signer must have: user_id, name, email, signer_type
        email_subject (str): Subject line for the email sent to signers
        email_body (str): Email body content for the email sent to signers

    Returns:
        dict: Dictionary with signature request details
    """
    try:
        # Validate document is in a signable state
        if document.status != DOCUMENT_STATUS['GENERATED']:
            raise ValueError(f"Document is not in a signable state: {document.status}")

        # Validate signers list contains required signers for the document type
        required_signers = DOCUMENT_REQUIRED_SIGNERS.get(document.document_type, [])
        signer_types = [signer['signer_type'] for signer in signers]
        for required_signer in required_signers:
            if required_signer not in signer_types:
                raise ValueError(f"Missing required signer: {required_signer}")

        # Use docusign_service to create the signature request
        result = docusign_service.create_signature_request(document, signers, email_subject, email_body)

        logger.info(f"Signature request created successfully for document {document.id}")
        return result
    except Exception as e:
        logger.error(f"Error creating signature request: {e}", exc_info=True)
        raise


@transaction.atomic
def create_package_signature_request(package, signers, email_subject, email_body):
    """Creates a signature request for a document package

    Args:
        package (DocumentPackage): The document package to send for signature
        signers (list): List of dictionaries containing signer information
                       Each signer must have: user_id, name, email, signer_type
        email_subject (str): Subject line for the email sent to signers
        email_body (str): Email body content for the email sent to signers

    Returns:
        dict: Dictionary with signature request details
    """
    try:
        # Validate package is in a signable state
        if package.status != DOCUMENT_STATUS['GENERATED']:
            raise ValueError(f"Document package is not in a signable state: {package.status}")

        # Get all documents in the package
        documents = package.get_documents()

        # Validate signers list contains required signers for all document types
        for document in documents:
            required_signers = DOCUMENT_REQUIRED_SIGNERS.get(document.document_type, [])
            signer_types = [signer['signer_type'] for signer in signers]
            for required_signer in required_signers:
                if required_signer not in signer_types:
                    raise ValueError(f"Missing required signer: {required_signer} for document type {document.document_type}")

        # Use docusign_service to create the signature request for the package
        result = docusign_service.create_signature_request_for_package(documents, signers, email_subject, email_body)

        logger.info(f"Signature request created successfully for document package {package.id}")
        return result
    except Exception as e:
        logger.error(f"Error creating signature request for package: {e}", exc_info=True)
        raise


def get_signature_status(document):
    """Gets the status of signatures for a document

    Args:
        document (Document): The document to check

    Returns:
        dict: Dictionary with signature status information
    """
    try:
        return docusign_service.get_signature_status(document)
    except Exception as e:
        logger.error(f"Error getting signature status: {e}", exc_info=True)
        raise


@transaction.atomic
def update_signature_status(document):
    """Updates the status of signatures for a document based on DocuSign status

    Args:
        document (Document): The document to update

    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        return docusign_service.update_signature_status(document)
    except Exception as e:
        logger.error(f"Error updating signature status: {e}", exc_info=True)
        raise


@transaction.atomic
def update_package_signature_status(package):
    """Updates the status of signatures for all documents in a package

    Args:
        package (DocumentPackage): The document package to update

    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        # Get all documents in the package
        documents = package.get_documents()

        # For each document, update signature status
        for document in documents:
            update_signature_status(document)

        # Update package status based on document statuses
        package.update_status()

        return True
    except Exception as e:
        logger.error(f"Error updating signature status for package: {e}", exc_info=True)
        raise


def send_signature_reminder(signature_request):
    """Sends a reminder for a pending signature request

    Args:
        signature_request (SignatureRequest): The signature request to send a reminder for

    Returns:
        bool: True if reminder was sent, False otherwise
    """
    try:
        return signature_request.send_reminder()
    except Exception as e:
        logger.error(f"Error sending signature reminder: {e}", exc_info=True)
        return False


@transaction.atomic
def process_signed_documents(document):
    """Processes documents after they have been signed

    Args:
        document (Document): The document to process

    Returns:
        bool: True if processing was successful, False otherwise
    """
    try:
        # Validate document status is SIGNED
        if document.status != DOCUMENT_STATUS['SIGNED']:
            raise ValueError(f"Document is not in a signed state: {document.status}")

        # Download signed documents from DocuSign
        envelope_id = document.signature_requests.first().external_reference.split(':')[0]
        documents = docusign_service.download_signed_documents(envelope_id)

        # Find the correct document in the downloaded documents
        signed_document = next((doc for doc in documents if doc['document_id'] == str(document.id)), None)
        if not signed_document:
            raise ValueError(f"Signed document not found in DocuSign envelope {envelope_id}")

        # Store the signed document
        storage_result = document_storage.store_document(
            content=signed_document['content'],
            document_type=document.document_type,
            file_name=document.file_name,
            content_type='application/pdf',
            metadata={
                'application_id': str(document.package.application_id),
                'document_type': document.document_type,
                'signed_at': datetime.now().isoformat(),
            }
        )

        # Update document status to COMPLETED
        document.status = DOCUMENT_STATUS['COMPLETED']
        document.file_path = storage_result['key']
        document.save()

        # Update package status
        document.package.update_status()

        logger.info(f"Successfully processed signed document {document.id}")
        return True
    except Exception as e:
        logger.error(f"Error processing signed document: {e}", exc_info=True)
        raise


@transaction.atomic
def process_package_signed_documents(package):
    """Processes all signed documents in a package

    Args:
        package (DocumentPackage): The document package to process

    Returns:
        bool: True if processing was successful, False otherwise
    """
    try:
        # Get all documents in the package
        documents = package.get_documents()

        # For each document with status SIGNED, process
        for document in documents:
            if document.status == DOCUMENT_STATUS['SIGNED']:
                process_signed_documents(document)

        # Update package status based on document statuses
        package.update_status()

        logger.info(f"Successfully processed signed documents in package {package.id}")
        return True
    except Exception as e:
        logger.error(f"Error processing signed documents in package: {e}", exc_info=True)
        raise


@transaction.atomic
def void_signature_request(document, void_reason):
    """Voids (cancels) a signature request

    Args:
        document (Document): The document to void
        void_reason (str): Reason for voiding the signature request

    Returns:
        bool: True if voiding was successful, False otherwise
    """
    try:
        # Get signature requests for the document
        signature_requests = SignatureRequest.objects.filter(document=document)

        # Group signature requests by envelope ID
        envelope_requests = {}
        for request in signature_requests:
            if request.external_reference:
                envelope_id, recipient_id = request.external_reference.split(':')
                if envelope_id not in envelope_requests:
                    envelope_requests[envelope_id] = []
                envelope_requests[envelope_id].append((request, recipient_id))

        # For each envelope, void
        for envelope_id, requests in envelope_requests.items():
            docusign_service.void_envelope(envelope_id, void_reason)

        # Update signature request statuses to VOIDED
        for request, recipient_id in requests:
            request.status = SIGNATURE_STATUS['VOIDED']
            request.save()

        # Update document status to VOIDED
        document.status = DOCUMENT_STATUS['VOIDED']
        document.save()

        # Update package status
        document.package.update_status()

        logger.info(f"Successfully voided signature request for document {document.id}")
        return True
    except Exception as e:
        logger.error(f"Error voiding signature request: {e}", exc_info=True)
        raise


def check_document_expiration():
    """Checks for and processes expired documents

    Returns:
        dict: Dictionary with expiration processing results
    """
    try:
        # Find documents with status SENT or SIGNED that have expired
        from .models import DocumentPackage
        expired_packages = DocumentPackage.objects.filter(
            status__in=[DOCUMENT_STATUS['SENT'], DOCUMENT_STATUS['SIGNED']],
            expiration_date__lte=datetime.now()
        )

        # For each expired document, update status to EXPIRED
        for package in expired_packages:
            package.status = DOCUMENT_STATUS['EXPIRED']
            package.save()

        logger.info(f"Successfully processed {expired_packages.count()} expired documents")
        return {
            'status': 'success',
            'message': f"Processed {expired_packages.count()} expired documents"
        }
    except Exception as e:
        logger.error(f"Error checking document expiration: {e}", exc_info=True)
        return {
            'status': 'error',
            'message': f"Error checking document expiration: {e}"
        }


def get_document_fields(document):
    """Gets all fields for a document

    Args:
        document (Document): The document to get fields for

    Returns:
        QuerySet: QuerySet of DocumentField objects
    """
    try:
        return document.get_fields()
    except Exception as e:
        logger.error(f"Error getting document fields: {e}", exc_info=True)
        raise


def create_document_field(document, field_name, field_type, field_value, x_position, y_position, page_number):
    """Creates a field in a document

    Args:
        document (Document): The document to create the field in
        field_name (str): Name of the field
        field_type (str): Type of the field
        field_value (str): Value of the field
        x_position (int): X position of the field
        y_position (int): Y position of the field
        page_number (int): Page number of the field

    Returns:
        DocumentField: Created DocumentField object
    """
    try:
        document_field = DocumentField.objects.create(
            document=document,
            field_name=field_name,
            field_type=field_type,
            field_value=field_value,
            x_position=x_position,
            y_position=y_position,
            page_number=page_number
        )
        logger.info(f"Document field created successfully: {document_field.id}")
        return document_field
    except Exception as e:
        logger.error(f"Error creating document field: {e}", exc_info=True)
        raise


def get_document_templates(document_type):
    """Gets all active document templates

    Args:
        document_type (str): Type of document template to retrieve

    Returns:
        QuerySet: QuerySet of DocumentTemplate objects
    """
    try:
        return DocumentTemplate.objects.filter(document_type=document_type, is_active=True)
    except Exception as e:
        logger.error(f"Error getting document templates: {e}", exc_info=True)
        raise


def get_document_template_by_id(template_id):
    """Gets a document template by its ID

    Args:
        template_id (str): ID of the document template to retrieve

    Returns:
        DocumentTemplate: DocumentTemplate object if found, None otherwise
    """
    try:
        return DocumentTemplate.objects.get(id=template_id)
    except DocumentTemplate.DoesNotExist:
        return None
    except Exception as e:
        logger.error(f"Error getting document template: {e}", exc_info=True)
        raise


def create_document_template(name, description, document_type, content, version, created_by):
    """Creates a new document template

    Args:
        name (str): Name of the document template
        description (str): Description of the document template
        document_type (str): Type of the document template
        content (bytes): Content of the document template
        version (str): Version of the document template
        created_by (User): User object creating the document template

    Returns:
        DocumentTemplate: Created DocumentTemplate object
    """
    try:
        # Store the template content
        storage_result = document_storage.store_template(
            content=content,
            template_type=document_type,
        )

        # Create a new DocumentTemplate object
        document_template = DocumentTemplate.objects.create(
            name=name,
            description=description,
            document_type=document_type,
            file_path=storage_result['key'],
            version=version,
            is_active=True,
            created_by=created_by
        )
        logger.info(f"Document template created successfully: {document_template.id}")
        return document_template
    except Exception as e:
        logger.error(f"Error creating document template: {e}", exc_info=True)
        raise


def update_document_template(template, name, description, content, version, is_active):
    """Updates an existing document template

    Args:
        template (DocumentTemplate): DocumentTemplate object to update
        name (str): Name of the document template
        description (str): Description of the document template
        content (bytes): Content of the document template
        version (str): Version of the document template
        is_active (bool): Whether the document template is active

    Returns:
        DocumentTemplate: Updated DocumentTemplate object
    """
    try:
        # Update the template fields
        template.name = name
        template.description = description
        template.version = version
        template.is_active = is_active

        # Store the new template content if provided
        if content:
            storage_result = document_storage.store_template(
                content=content,
                template_type=template.document_type,
            )
            template.file_path = storage_result['key']

        template.save()
        logger.info(f"Document template updated successfully: {template.id}")
        return template
    except Exception as e:
        logger.error(f"Error updating document template: {e}", exc_info=True)
        raise


def get_application_documents(application):
    """Gets all documents for a loan application

    Args:
        application (LoanApplication): The loan application to get documents for

    Returns:
        QuerySet: QuerySet of Document objects
    """
    try:
        # Get all DocumentPackage objects for the application
        document_packages = DocumentPackage.objects.filter(application=application)

        # Get all Document objects for these packages
        documents = Document.objects.filter(package__in=document_packages)

        return documents
    except Exception as e:
        logger.error(f"Error getting application documents: {e}", exc_info=True)
        raise


def get_application_document_packages(application):
    """Gets all document packages for a loan application

    Args:
        application (LoanApplication): The loan application to get document packages for

    Returns:
        QuerySet: QuerySet of DocumentPackage objects
    """
    try:
        return DocumentPackage.objects.filter(application=application)
    except Exception as e:
        logger.error(f"Error getting application document packages: {e}", exc_info=True)
        raise