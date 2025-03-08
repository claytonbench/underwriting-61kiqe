"""
Implements a specialized document generator for creating commitment letters that are sent to schools after loan approval.
The commitment letter contains details about the approved loan terms, stipulations, and requires school acknowledgment
before proceeding to the loan agreement phase.
"""

from datetime import datetime  # version 3.11+
from .base import BaseDocumentGenerator, DocumentGenerationError  # Implements a specialized document generator for creating commitment letters that are sent to schools after loan approval.
from .constants import DOCUMENT_TYPES  # Implements a specialized document generator for creating commitment letters that are sent to schools after loan approval.
from utils.logging import getLogger  # Implements a specialized document generator for creating commitment letters that are sent to schools after loan approval.
from apps.underwriting.models import UnderwritingDecision  # Implements a specialized document generator for creating commitment letters that are sent to schools after loan approval.

# Initialize logger for this module
logger = getLogger('document_generators')


class CommitmentLetterGenerator(BaseDocumentGenerator):
    """
    Specialized document generator for creating commitment letters after loan approval.

    This class extends the BaseDocumentGenerator to provide specific functionality
    for generating commitment letters, including preparing the context data and
    generating the file name.
    """

    @property
    def document_type(self):
        """
        Document type identifier for this generator.

        This property returns the document type identifier for commitment letters,
        which is used to retrieve the correct template and configure the
        generation process.

        Returns:
            str: Document type identifier for commitment letters
        """
        return DOCUMENT_TYPES['COMMITMENT_LETTER']

    def __init__(self):
        """
        Initialize the commitment letter generator.

        Calls the parent constructor with DOCUMENT_TYPES['COMMITMENT_LETTER']
        and logs initialization of the commitment letter generator.
        """
        super().__init__(DOCUMENT_TYPES['COMMITMENT_LETTER'])
        logger.info("Initialized CommitmentLetterGenerator")

    def _prepare_context(self, application, additional_context):
        """
        Prepares the context data for commitment letter template rendering.

        This method overrides the base class implementation to add commitment-letter-specific
        data to the context, including approved loan amount, interest rate, term months,
        and any stipulations associated with the loan.

        Args:
            application (LoanApplication): The loan application to generate the document for
            additional_context (dict): Additional context data for template rendering

        Returns:
            dict: Context dictionary for template rendering

        Raises:
            DocumentGenerationError: If underwriting decision retrieval fails
        """
        try:
            # Call the parent _prepare_context method to get the base context
            context = super()._prepare_context(application, additional_context)

            # Try to retrieve the underwriting decision for the application
            decision = application.get_underwriting_decision()

            # Add approved_amount, interest_rate, and term_months from the decision to the context
            if decision:
                context['approved_amount'] = decision.approved_amount
                context['interest_rate'] = decision.interest_rate
                context['term_months'] = decision.term_months
                context['comments'] = decision.comments

                # Retrieve stipulations using decision.get_stipulations() and add to context
                stipulations = decision.get_stipulations()
                context['stipulations'] = []
                for stipulation in stipulations:
                    context['stipulations'].append({
                        'type': stipulation.stipulation_type,
                        'description': stipulation.description,
                        'required_by': stipulation.required_by_date.strftime('%B %d, %Y') if stipulation.required_by_date else None,
                        'status': stipulation.status,
                    })

                # Format currency values and percentages for display
                context['approved_amount_formatted'] = "${:,.2f}".format(decision.approved_amount) if decision.approved_amount else ""
                context['interest_rate_formatted'] = "{:.2f}%".format(decision.interest_rate) if decision.interest_rate else ""

            # Return the enhanced context dictionary
            return context

        except Exception as e:
            # Handle any exceptions, log error, and raise DocumentGenerationError
            error_message = f"Failed to prepare context for commitment letter: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocumentGenerationError(error_message, e)

    def _generate_file_name(self, application):
        """
        Generates a file name for the commitment letter.

        This method constructs a file name based on the borrower's last name,
        the school's name, and the current date.

        Args:
            application (LoanApplication): The loan application to generate a file name for

        Returns:
            str: Generated file name

        Raises:
            DocumentGenerationError: If borrower or school information is missing
        """
        try:
            # Get the borrower's name from the application
            borrower = application.borrower
            borrower_last_name = borrower.last_name

            # Get the school's name from the application
            school = application.school
            school_name = school.name

            # Format the current date as YYYYMMDD
            current_date = datetime.now().strftime('%Y%m%d')

            # Return a formatted string like 'commitment_letter_LASTNAME_SCHOOLNAME_YYYYMMDD.pdf'
            file_name = f"commitment_letter_{borrower_last_name}_{school_name}_{current_date}.pdf"
            return file_name

        except Exception as e:
            # Handle any exceptions, log error, and raise DocumentGenerationError
            error_message = f"Failed to generate file name for commitment letter: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise DocumentGenerationError(error_message, e)