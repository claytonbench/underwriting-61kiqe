"""
Base document generator module for the loan management system.

This module defines an abstract base class for document generators using the template method
pattern, providing a framework for document generation while allowing specific document
types to customize certain steps in the process.
"""

import os
import datetime
import jinja2  # version 3.1+
import weasyprint  # version 57.0+

from utils.logging import getLogger
from ..models import Document, DocumentTemplate
from ..storage import document_storage
from ..constants import DOCUMENT_TYPES, DOCUMENT_STATUS, DOCUMENT_TEMPLATE_PATHS

# Configure logger
logger = getLogger('document_generators')


class DocumentGenerationError(Exception):
    """
    Custom exception class for document generation errors.
    
    This exception encapsulates the original error to provide better context
    while preserving the original exception information.
    """
    
    def __init__(self, message, original_exception=None):
        """
        Initialize the DocumentGenerationError with a message and original exception.
        
        Args:
            message (str): Human-readable error message
            original_exception (Exception, optional): Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception
        logger.error(f"Document generation error: {message}", exc_info=original_exception)
    
    def __str__(self):
        """
        Returns a string representation of the error.
        
        Returns:
            str: String representation of the error
        """
        if self.original_exception:
            return f"{self.message} (Original error: {str(self.original_exception)})"
        return self.message


class BaseDocumentGenerator:
    """
    Abstract base class for document generators that implements the template method pattern.
    
    This class provides a common structure for document generation, with extension points
    that allow specific document type generators to customize the behavior while reusing
    the overall generation workflow.
    """
    
    @property
    def document_type(self):
        """
        Document type identifier for this generator.
        
        This property should be overridden by subclasses to specify the type
        of document being generated.
        
        Raises:
            NotImplementedError: If not implemented by a subclass
        """
        raise NotImplementedError("Subclasses must define document_type")
    
    def __init__(self, document_type):
        """
        Initialize the document generator with a specific document type.
        
        Args:
            document_type (str): Type of document to generate
        """
        self._document_type = document_type
        logger.info(f"Initialized document generator for {document_type}")
    
    def generate(self, application, generated_by, additional_context=None):
        """
        Template method that orchestrates the document generation process.
        
        This method implements the template method pattern, defining the sequence
        of steps for document generation while allowing subclasses to customize
        specific steps.
        
        Args:
            application (LoanApplication): The loan application to generate the document for
            generated_by (User): The user who initiated document generation
            additional_context (dict, optional): Additional context data for template rendering
        
        Returns:
            Document: Generated Document object
            
        Raises:
            DocumentGenerationError: If document generation fails at any step
        """
        logger.info(f"Starting document generation for application {application.id}, type: {self._document_type}")
        
        try:
            # Step 1: Get the template content
            template_content = self._get_template()
            
            # Step 2: Prepare the context data
            context = self._prepare_context(application, additional_context or {})
            
            # Step 3: Render the template
            html_content = self._render_template(template_content, context)
            
            # Step 4: Convert HTML to PDF
            pdf_content = self._html_to_pdf(html_content)
            
            # Step 5: Generate a file name
            file_name = self._generate_file_name(application)
            
            # Step 6: Store the document
            document = self._store_document(pdf_content, file_name, application, generated_by)
            
            logger.info(f"Successfully generated {self._document_type} document for application {application.id}")
            return document
            
        except DocumentGenerationError:
            # Re-raise DocumentGenerationError to preserve the error chain
            raise
        except Exception as e:
            # Wrap any other exceptions in DocumentGenerationError
            error_message = f"Failed to generate {self._document_type} document for application {application.id}"
            logger.error(error_message, exc_info=True)
            raise DocumentGenerationError(error_message, e)
    
    def _get_template(self):
        """
        Retrieves the template content for the document type.
        
        Returns:
            str: Template content as HTML string
            
        Raises:
            DocumentGenerationError: If template retrieval fails
        """
        try:
            # Get the template path for this document type
            if self._document_type not in DOCUMENT_TEMPLATE_PATHS:
                raise ValueError(f"Unknown document type: {self._document_type}")
                
            template_path = DOCUMENT_TEMPLATE_PATHS[self._document_type]
            
            # Retrieve the template content from storage
            template_content, _, _ = document_storage.retrieve_template(template_path)
            
            if not template_content:
                raise ValueError(f"Template content is empty for {self._document_type}")
                
            return template_content.decode('utf-8')
            
        except ValueError as e:
            error_message = f"Failed to get template for {self._document_type}: {str(e)}"
            logger.error(error_message)
            raise DocumentGenerationError(error_message, e)
        except Exception as e:
            error_message = f"Unexpected error retrieving template for {self._document_type}: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocumentGenerationError(error_message, e)
    
    def _prepare_context(self, application, additional_context):
        """
        Prepares the context data for template rendering.
        
        This method builds a dictionary of context variables that will be used to render
        the template, including data from the application, borrower, co-borrower,
        school, program, and loan details.
        
        Args:
            application (LoanApplication): The loan application to generate the document for
            additional_context (dict): Additional context data for template rendering
            
        Returns:
            dict: Context dictionary for template rendering
        """
        # Start with a base context
        context = {
            'current_date': datetime.datetime.now().strftime('%B %d, %Y'),
            'application_id': str(application.id)
        }
        
        # Add borrower information
        borrower = application.borrower
        borrower_profile = borrower.get_profile()
        if borrower_profile:
            context['borrower'] = {
                'id': str(borrower.id),
                'first_name': borrower.first_name,
                'last_name': borrower.last_name,
                'full_name': borrower.get_full_name(),
                'email': borrower.email,
                'phone': borrower.phone,
                'ssn': borrower_profile.get_ssn() if hasattr(borrower_profile, 'get_ssn') else None,
                'dob': borrower_profile.dob.strftime('%B %d, %Y') if hasattr(borrower_profile, 'dob') else None,
                'address': {
                    'line1': borrower_profile.address_line1 if hasattr(borrower_profile, 'address_line1') else None,
                    'line2': borrower_profile.address_line2 if hasattr(borrower_profile, 'address_line2') else None,
                    'city': borrower_profile.city if hasattr(borrower_profile, 'city') else None,
                    'state': borrower_profile.state if hasattr(borrower_profile, 'state') else None,
                    'zip': borrower_profile.zip_code if hasattr(borrower_profile, 'zip_code') else None,
                    'full': borrower_profile.get_full_address() if hasattr(borrower_profile, 'get_full_address') else None,
                },
            }
            
            # Add employment information if available
            if hasattr(borrower_profile, 'employment_info') and borrower_profile.employment_info.exists():
                employment = borrower_profile.employment_info.first()
                context['borrower']['employment'] = {
                    'employer': employment.employer_name,
                    'occupation': employment.occupation,
                    'phone': employment.employer_phone,
                    'annual_income': employment.annual_income,
                    'monthly_income': employment.get_monthly_income() if hasattr(employment, 'get_monthly_income') else None,
                }
        
        # Add co-borrower information if available
        if application.co_borrower:
            co_borrower = application.co_borrower
            co_borrower_profile = co_borrower.get_profile()
            if co_borrower_profile:
                context['co_borrower'] = {
                    'id': str(co_borrower.id),
                    'first_name': co_borrower.first_name,
                    'last_name': co_borrower.last_name,
                    'full_name': co_borrower.get_full_name(),
                    'email': co_borrower.email,
                    'phone': co_borrower.phone,
                    'ssn': co_borrower_profile.get_ssn() if hasattr(co_borrower_profile, 'get_ssn') else None,
                    'dob': co_borrower_profile.dob.strftime('%B %d, %Y') if hasattr(co_borrower_profile, 'dob') else None,
                    'relationship': application.relationship_type,
                    'address': {
                        'line1': co_borrower_profile.address_line1 if hasattr(co_borrower_profile, 'address_line1') else None,
                        'line2': co_borrower_profile.address_line2 if hasattr(co_borrower_profile, 'address_line2') else None,
                        'city': co_borrower_profile.city if hasattr(co_borrower_profile, 'city') else None,
                        'state': co_borrower_profile.state if hasattr(co_borrower_profile, 'state') else None,
                        'zip': co_borrower_profile.zip_code if hasattr(co_borrower_profile, 'zip_code') else None,
                        'full': co_borrower_profile.get_full_address() if hasattr(co_borrower_profile, 'get_full_address') else None,
                    },
                }
                
                # Add co-borrower employment information if available
                if hasattr(co_borrower_profile, 'employment_info') and co_borrower_profile.employment_info.exists():
                    employment = co_borrower_profile.employment_info.first()
                    context['co_borrower']['employment'] = {
                        'employer': employment.employer_name,
                        'occupation': employment.occupation,
                        'phone': employment.employer_phone,
                        'annual_income': employment.annual_income,
                        'monthly_income': employment.get_monthly_income() if hasattr(employment, 'get_monthly_income') else None,
                    }
        
        # Add school information
        school = application.school
        context['school'] = {
            'id': str(school.id),
            'name': school.name,
            'legal_name': school.legal_name,
            'address': {
                'line1': school.address_line1,
                'line2': school.address_line2,
                'city': school.city,
                'state': school.state,
                'zip': school.zip_code,
                'full': school.get_full_address() if hasattr(school, 'get_full_address') else None,
            },
            'phone': school.phone,
            'website': school.website,
        }
        
        # Add primary contact information if available
        primary_contact = school.get_primary_contact() if hasattr(school, 'get_primary_contact') else None
        if primary_contact:
            context['school']['contact'] = {
                'name': primary_contact.get_full_name() if hasattr(primary_contact, 'get_full_name') else None,
                'title': primary_contact.title if hasattr(primary_contact, 'title') else None,
                'email': primary_contact.email if hasattr(primary_contact, 'email') else None,
                'phone': primary_contact.phone if hasattr(primary_contact, 'phone') else None,
            }
        
        # Add program information
        program = application.program
        context['program'] = {
            'id': str(program.id),
            'name': program.name,
            'description': program.description,
            'duration_hours': program.duration_hours,
            'duration_weeks': program.duration_weeks,
            'tuition': program.get_current_tuition() if hasattr(program, 'get_current_tuition') else None,
        }
        
        # Add loan details
        loan_details = application.get_loan_details()
        if loan_details:
            context['loan'] = {
                'tuition_amount': loan_details.tuition_amount,
                'deposit_amount': loan_details.deposit_amount,
                'other_funding': loan_details.other_funding,
                'requested_amount': loan_details.requested_amount,
                'approved_amount': loan_details.approved_amount,
                'net_tuition': loan_details.get_net_tuition() if hasattr(loan_details, 'get_net_tuition') else None,
                'start_date': loan_details.start_date.strftime('%B %d, %Y'),
                'completion_date': loan_details.completion_date.strftime('%B %d, %Y') if loan_details.completion_date else None,
            }
        
        # Add underwriting decision information if available
        underwriting_decision = application.get_underwriting_decision()
        if underwriting_decision:
            context['underwriting'] = {
                'decision': underwriting_decision.decision,
                'decision_date': underwriting_decision.decision_date.strftime('%B %d, %Y'),
                'approved_amount': underwriting_decision.approved_amount,
                'interest_rate': underwriting_decision.interest_rate,
                'term_months': underwriting_decision.term_months,
                'comments': underwriting_decision.comments,
            }
            
            # Add stipulations if available
            try:
                from apps.underwriting.models import Stipulation
                stipulations = Stipulation.objects.filter(application=application)
                if stipulations.exists():
                    context['stipulations'] = [
                        {
                            'type': stipulation.stipulation_type,
                            'description': stipulation.description,
                            'required_by': stipulation.required_by_date.strftime('%B %d, %Y') if stipulation.required_by_date else None,
                            'status': stipulation.status,
                        } for stipulation in stipulations
                    ]
            except ImportError:
                # Underwriting app may not be available yet
                pass
        
        # Add any additional context
        context.update(additional_context)
        
        return context
    
    def _render_template(self, template_content, context):
        """
        Renders the template with the provided context.
        
        Args:
            template_content (str): Template content as HTML string
            context (dict): Context dictionary for template rendering
            
        Returns:
            str: Rendered HTML content
            
        Raises:
            DocumentGenerationError: If template rendering fails
        """
        try:
            # Create a Jinja2 environment with appropriate settings
            env = jinja2.Environment(
                loader=jinja2.BaseLoader(),
                autoescape=jinja2.select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True
            )
            
            # Add custom filters if needed
            env.filters['currency'] = lambda value: f"${value:,.2f}" if value is not None else ""
            env.filters['percentage'] = lambda value: f"{value:.2f}%" if value is not None else ""
            
            # Load the template from the content string
            template = env.from_string(template_content)
            
            # Render the template with the context
            rendered_html = template.render(**context)
            
            return rendered_html
            
        except jinja2.exceptions.TemplateError as e:
            error_message = f"Failed to render template for {self._document_type}: {str(e)}"
            logger.error(error_message)
            raise DocumentGenerationError(error_message, e)
        except Exception as e:
            error_message = f"Unexpected error rendering template for {self._document_type}: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocumentGenerationError(error_message, e)
    
    def _html_to_pdf(self, html_content):
        """
        Converts HTML content to PDF.
        
        Args:
            html_content (str): HTML content to convert
            
        Returns:
            bytes: PDF content as bytes
            
        Raises:
            DocumentGenerationError: If PDF conversion fails
        """
        try:
            # Convert HTML to PDF using WeasyPrint
            pdf = weasyprint.HTML(string=html_content).write_pdf()
            return pdf
            
        except Exception as e:
            error_message = f"Failed to convert HTML to PDF for {self._document_type}: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocumentGenerationError(error_message, e)
    
    def _store_document(self, pdf_content, file_name, application, generated_by):
        """
        Stores the generated document and creates a Document record.
        
        Args:
            pdf_content (bytes): PDF content to store
            file_name (str): File name for the document
            application (LoanApplication): The loan application the document is for
            generated_by (User): The user who generated the document
            
        Returns:
            Document: Created Document object
            
        Raises:
            DocumentGenerationError: If document storage fails
        """
        try:
            # Store the PDF document in the document storage
            storage_result = document_storage.store_document(
                content=pdf_content,
                document_type=self._document_type,
                file_name=file_name,
                content_type='application/pdf',
                metadata={
                    'application_id': str(application.id),
                    'document_type': self._document_type,
                    'generated_by': str(generated_by.id),
                    'generated_at': datetime.datetime.now().isoformat(),
                }
            )
            
            # Get or create a document package for this application
            from ..models import DocumentPackage
            
            # Determine the package type based on document type
            package_type = self._get_package_type()
            
            # Try to find an existing package of this type for the application
            document_package = None
            try:
                document_package = DocumentPackage.objects.filter(
                    application=application,
                    package_type=package_type,
                    status__in=[DOCUMENT_STATUS['DRAFT'], DOCUMENT_STATUS['GENERATED']]
                ).first()
            except Exception as e:
                logger.warning(f"Error finding document package: {e}")
            
            # Create a new package if none exists
            if not document_package:
                document_package = DocumentPackage.objects.create(
                    application=application,
                    package_type=package_type,
                    status=DOCUMENT_STATUS['GENERATED'],
                    created_by=generated_by
                )
            
            # Create a Document record
            document = Document.objects.create(
                package=document_package,
                document_type=self._document_type,
                file_name=file_name,
                file_path=storage_result['key'],
                version=storage_result.get('version_id', '1.0'),
                status=DOCUMENT_STATUS['GENERATED'],
                generated_at=datetime.datetime.now(),
                generated_by=generated_by
            )
            
            return document
            
        except Exception as e:
            error_message = f"Failed to store document for {self._document_type}: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocumentGenerationError(error_message, e)
    
    def _get_package_type(self):
        """
        Determines the document package type based on the document type.
        
        Returns:
            str: Document package type
        """
        from ..constants import DOCUMENT_PACKAGE_TYPES
        
        # Map document types to package types
        package_type_mapping = {
            DOCUMENT_TYPES['COMMITMENT_LETTER']: DOCUMENT_PACKAGE_TYPES['APPROVAL'],
            DOCUMENT_TYPES['LOAN_AGREEMENT']: DOCUMENT_PACKAGE_TYPES['LOAN_AGREEMENT'],
            DOCUMENT_TYPES['DISCLOSURE_FORM']: DOCUMENT_PACKAGE_TYPES['DISCLOSURE'],
            DOCUMENT_TYPES['TRUTH_IN_LENDING']: DOCUMENT_PACKAGE_TYPES['DISCLOSURE'],
            DOCUMENT_TYPES['PROMISSORY_NOTE']: DOCUMENT_PACKAGE_TYPES['LOAN_AGREEMENT'],
            DOCUMENT_TYPES['DISBURSEMENT_AUTHORIZATION']: DOCUMENT_PACKAGE_TYPES['FUNDING'],
        }
        
        # Return the mapped package type or default to application
        return package_type_mapping.get(self._document_type, DOCUMENT_PACKAGE_TYPES['APPLICATION'])
    
    def _generate_file_name(self, application):
        """
        Generates a file name for the document.
        
        This method should be implemented by subclasses to generate a file name
        appropriate for the specific document type.
        
        Args:
            application (LoanApplication): The loan application to generate a file name for
            
        Returns:
            str: Generated file name
            
        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement _generate_file_name method")