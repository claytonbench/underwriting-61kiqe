"""
Implements generators for various disclosure forms required in the loan application process.
This module extends the BaseDocumentGenerator to create legally compliant disclosure documents
including Truth in Lending disclosures and other required regulatory forms. These documents
inform borrowers about the terms, conditions, and legal aspects of their loan agreement.
"""

import logging  # version standard library
from datetime import datetime  # version standard library

from .base import BaseDocumentGenerator, DocumentGenerationError  # src/backend/apps/documents/generators/base.py
from .base import DOCUMENT_TYPES  # src/backend/apps/documents/generators/base.py
from .base import DOCUMENT_STATUS  # src/backend/apps/documents/generators/base.py
from utils.formatters import format_currency  # src/backend/utils/formatters.py
from utils.formatters import format_date  # src/backend/utils/formatters.py

# Initialize logger
logger = logging.getLogger('document_generators')


class DisclosureFormGenerator(BaseDocumentGenerator):
    """
    Generator class for creating general disclosure forms for loan applications
    """

    document_type = DOCUMENT_TYPES['DISCLOSURE_FORM']

    def __init__(self):
        """
        Initialize the DisclosureFormGenerator with the disclosure form document type
        """
        super().__init__(DOCUMENT_TYPES['DISCLOSURE_FORM'])
        logger.info("Initialized DisclosureFormGenerator")

    def generate(self, application, generated_by, additional_context=None):
        """
        Generate a disclosure form for the given loan application

        Args:
            application (LoanApplication): The loan application to generate the document for
            generated_by (User): The user who initiated document generation
            additional_context (dict): Additional context data

        Returns:
            Document: Generated disclosure form Document object
        """
        logger.info(f"Starting disclosure form generation for application {application.id}")

        try:
            # Step 1: Get the template content
            template_content = self._get_template()

            # Step 2: Prepare the context data
            context = self._prepare_context(application, additional_context or {})

            # Step 3: Render the template
            html_content = self._render_template(template_content, context)

            # Step 4: Convert the HTML to PDF
            pdf_content = self._html_to_pdf(html_content)

            # Step 5: Generate a file name
            file_name = self._generate_file_name(application)

            # Step 6: Store the document
            document = self._store_document(pdf_content, file_name, application, generated_by)

            logger.info(f"Successfully generated disclosure form for application {application.id}")
            return document

        except DocumentGenerationError:
            # Re-raise DocumentGenerationError to preserve the error chain
            raise
        except Exception as e:
            # Wrap any other exceptions in DocumentGenerationError
            error_message = f"Failed to generate disclosure form for application {application.id}"
            logger.error(error_message, exc_info=True)
            raise DocumentGenerationError(error_message, e)

    def _prepare_context(self, application, additional_context):
        """
        Prepare the context data specific to disclosure forms

        Args:
            application (LoanApplication): The loan application to generate the document for
            additional_context (dict): Additional context data

        Returns:
            dict: Context dictionary for template rendering
        """
        # Call the parent _prepare_context method to get the base context
        context = super()._prepare_context(application, additional_context)

        # Get the loan details for the application
        loan_details = application.get_loan_details()

        # Add disclosure-specific data to the context
        if loan_details:
            context['requested_amount_formatted'] = format_currency(loan_details.requested_amount)

        # Add current date in the appropriate format
        context['generation_date'] = datetime.now().strftime('%B %d, %Y')

        # Add any additional context provided
        context.update(additional_context)

        return context

    def _generate_file_name(self, application):
        """
        Generate a file name for the disclosure form

        Args:
            application (LoanApplication): The loan application to generate a file name for

        Returns:
            str: Generated file name
        """
        # Get the borrower's name from the application
        borrower = application.borrower
        borrower_name = f"{borrower.first_name}_{borrower.last_name}"

        # Get the current date in YYYYMMDD format
        current_date = datetime.now().strftime('%Y%m%d')

        # Combine the borrower name, 'disclosure_form', and date with underscores
        file_name = f"{borrower_name}_disclosure_form_{current_date}"

        # Replace spaces with underscores and convert to lowercase
        file_name = file_name.replace(" ", "_").lower()

        # Add .pdf extension
        file_name += ".pdf"

        return file_name


class TruthInLendingGenerator(BaseDocumentGenerator):
    """
    Generator class for creating Truth in Lending disclosure forms required by regulation
    """

    document_type = DOCUMENT_TYPES['TRUTH_IN_LENDING']

    def __init__(self):
        """
        Initialize the TruthInLendingGenerator with the Truth in Lending document type
        """
        super().__init__(DOCUMENT_TYPES['TRUTH_IN_LENDING'])
        logger.info("Initialized TruthInLendingGenerator")

    def generate(self, application, generated_by, additional_context=None):
        """
        Generate a Truth in Lending disclosure for the given loan application

        Args:
            application (LoanApplication): The loan application to generate the document for
            generated_by (User): The user who initiated document generation
            additional_context (dict): Additional context data

        Returns:
            Document: Generated Truth in Lending Document object
        """
        logger.info(f"Starting Truth in Lending generation for application {application.id}")

        try:
            # Step 1: Verify that the application has an underwriting decision
            underwriting_decision = application.get_underwriting_decision()
            if not underwriting_decision:
                raise DocumentGenerationError("Application must have an underwriting decision to generate Truth in Lending disclosure")

            # Step 2: Get the template content
            template_content = self._get_template()

            # Step 3: Prepare the context data
            context = self._prepare_context(application, additional_context or {})

            # Step 4: Render the template
            html_content = self._render_template(template_content, context)

            # Step 5: Convert the HTML to PDF
            pdf_content = self._html_to_pdf(html_content)

            # Step 6: Generate a file name
            file_name = self._generate_file_name(application)

            # Step 7: Store the document
            document = self._store_document(pdf_content, file_name, application, generated_by)

            logger.info(f"Successfully generated Truth in Lending disclosure for application {application.id}")
            return document

        except DocumentGenerationError:
            # Re-raise DocumentGenerationError to preserve the error chain
            raise
        except Exception as e:
            # Wrap any other exceptions in DocumentGenerationError
            error_message = f"Failed to generate Truth in Lending disclosure for application {application.id}"
            logger.error(error_message, exc_info=True)
            raise DocumentGenerationError(error_message, e)

    def _prepare_context(self, application, additional_context):
        """
        Prepare the context data specific to Truth in Lending disclosures

        Args:
            application (LoanApplication): The loan application to generate the document for
            additional_context (dict): Additional context data

        Returns:
            dict: Context dictionary for template rendering
        """
        # Call the parent _prepare_context method to get the base context
        context = super()._prepare_context(application, additional_context)

        # Get the underwriting decision for the application
        underwriting_decision = application.get_underwriting_decision()

        # Add TILA-specific data to the context
        if underwriting_decision:
            context['approved_amount_formatted'] = format_currency(underwriting_decision.approved_amount)
            context['interest_rate_formatted'] = format_currency(underwriting_decision.interest_rate)

            # Calculate and add APR (Annual Percentage Rate)
            apr = self._calculate_apr(
                interest_rate=underwriting_decision.interest_rate,
                fees=0,  # Assuming no fees for now
                principal=underwriting_decision.approved_amount,
                term_months=underwriting_decision.term_months
            )
            context['apr'] = apr

            # Calculate and add finance charge
            finance_charge = underwriting_decision.approved_amount * underwriting_decision.interest_rate * (underwriting_decision.term_months / 12)
            context['finance_charge'] = format_currency(finance_charge)

            # Calculate and add total of payments
            total_of_payments = underwriting_decision.approved_amount + finance_charge
            context['total_of_payments'] = format_currency(total_of_payments)

            # Calculate and add payment schedule
            monthly_payment = total_of_payments / underwriting_decision.term_months
            context['payment_schedule'] = {
                'payment_amount': format_currency(monthly_payment),
                'payment_frequency': 'Monthly',
                'number_of_payments': underwriting_decision.term_months,
            }

        # Add current date in the appropriate format
        context['generation_date'] = datetime.now().strftime('%B %d, %Y')

        # Add any additional context provided
        context.update(additional_context)

        return context

    def _calculate_apr(self, interest_rate, fees, principal, term_months):
        """
        Calculate the Annual Percentage Rate (APR) for the loan

        Args:
            interest_rate (decimal.Decimal): The nominal interest rate
            fees (decimal.Decimal): Any upfront fees associated with the loan
            principal (decimal.Decimal): The loan principal amount
            term_months (int): The loan term in months

        Returns:
            decimal.Decimal: Calculated APR
        """
        # Calculate the APR based on interest rate and fees
        apr = interest_rate  # Placeholder: Implement APR calculation logic

        return round(apr, 3)

    def _generate_file_name(self, application):
        """
        Generate a file name for the Truth in Lending disclosure

        Args:
            application (LoanApplication): The loan application to generate a file name for

        Returns:
            str: Generated file name
        """
        # Get the borrower's name from the application
        borrower = application.borrower
        borrower_name = f"{borrower.first_name}_{borrower.last_name}"

        # Get the current date in YYYYMMDD format
        current_date = datetime.now().strftime('%Y%m%d')

        # Combine the borrower name, 'truth_in_lending', and date with underscores
        file_name = f"{borrower_name}_truth_in_lending_{current_date}"

        # Replace spaces with underscores and convert to lowercase
        file_name = file_name.replace(" ", "_").lower()

        # Add .pdf extension
        file_name += ".pdf"

        return file_name