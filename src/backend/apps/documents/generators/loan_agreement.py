"""
Implements a document generator for loan agreements, extending the BaseDocumentGenerator
class to provide specific functionality for generating loan agreement documents.
This includes customized context preparation, file naming, and any loan agreement-specific
document generation logic.
"""

import logging
from datetime import datetime

from .base import BaseDocumentGenerator  # version 3.1+
from ..constants import DOCUMENT_TYPES  # version 3.1+
from apps.underwriting.models import UnderwritingDecision  # version 3.1+

# Configure logger
logger = logging.getLogger('document_generators')


class LoanAgreementGenerator(BaseDocumentGenerator):
    """
    Generator for loan agreement documents based on application and underwriting data.
    """

    @property
    def document_type(self):
        """
        Document type identifier for this generator.
        """
        return DOCUMENT_TYPES['LOAN_AGREEMENT']

    def __init__(self):
        """
        Initialize the loan agreement generator with the appropriate document type.
        """
        super().__init__(DOCUMENT_TYPES['LOAN_AGREEMENT'])
        logger.info("Initialized LoanAgreementGenerator")

    def _prepare_context(self, application, additional_context):
        """
        Prepares the context data specific to loan agreements.

        Args:
            application (LoanApplication): The loan application to generate the document for
            additional_context (dict): Additional context data

        Returns:
            dict: Enhanced context dictionary for loan agreement template rendering
        """
        # Call parent _prepare_context to get base context
        context = super()._prepare_context(application, additional_context)

        # Get underwriting decision for the application
        underwriting_decision = application.get_underwriting_decision()

        # Add approved amount, interest rate, and term from underwriting decision
        if underwriting_decision:
            context['approved_amount'] = underwriting_decision.approved_amount
            context['interest_rate'] = underwriting_decision.interest_rate
            context['term_months'] = underwriting_decision.term_months

            # Calculate and add payment schedule based on loan terms
            principal = underwriting_decision.approved_amount
            interest_rate = underwriting_decision.interest_rate
            term_months = underwriting_decision.term_months
            context['payment_schedule'] = self._calculate_payment_schedule(principal, interest_rate, term_months)

        # Add loan agreement specific dates (issue date, first payment date)
        context['issue_date'] = datetime.now().strftime('%B %d, %Y')
        loan_details = application.get_loan_details()
        if loan_details and loan_details.start_date:
            context['first_payment_date'] = self._get_payment_dates(loan_details.start_date, term_months)[0] if term_months else None

        # Add stipulations from underwriting decision
        if underwriting_decision:
            stipulations = underwriting_decision.get_stipulations()
            context['stipulations'] = [
                {'type': stipulation.stipulation_type, 'description': stipulation.description}
                for stipulation in stipulations
            ]

        # Return the enhanced context dictionary
        return context

    def _generate_file_name(self, application):
        """
        Generates a file name for the loan agreement document.

        Args:
            application (LoanApplication): The loan application

        Returns:
            str: Generated file name
        """
        # Get borrower name from application
        borrower_name = f"{application.borrower.last_name}_{application.borrower.first_name}"

        # Get current date in YYYYMMDD format
        current_date = datetime.now().strftime('%Y%m%d')

        # Combine borrower name, 'loan_agreement', and date with underscores
        file_name = f"{borrower_name}_loan_agreement_{current_date}"

        # Replace spaces with underscores and convert to lowercase
        file_name = file_name.replace(" ", "_").lower()

        # Add .pdf extension
        file_name = f"{file_name}.pdf"

        # Return the formatted file name
        return file_name

    def _calculate_payment_schedule(self, principal, interest_rate, term_months):
        """
        Calculates the payment schedule based on loan terms.

        Args:
            principal (float): The loan principal amount
            interest_rate (float): The annual interest rate
            term_months (int): The loan term in months

        Returns:
            list: List of payment details including payment amount, dates, and balances
        """
        # Convert annual interest rate to monthly rate
        monthly_interest_rate = interest_rate / 12

        # Calculate monthly payment using amortization formula
        monthly_payment = (principal * monthly_interest_rate) / (1 - (1 + monthly_interest_rate)**(-term_months))

        # Generate payment schedule with payment number, date, amount, principal, interest, and remaining balance
        payment_schedule = []
        remaining_balance = principal
        payment_dates = self._get_payment_dates(datetime.now().date(), term_months)
        for i in range(term_months):
            interest_payment = remaining_balance * monthly_interest_rate
            principal_payment = monthly_payment - interest_payment
            remaining_balance -= principal_payment

            payment_schedule.append({
                'payment_number': i + 1,
                'payment_date': payment_dates[i],
                'payment_amount': monthly_payment,
                'principal_payment': principal_payment,
                'interest_payment': interest_payment,
                'remaining_balance': remaining_balance
            })

        # Return the complete payment schedule as a list of dictionaries
        return payment_schedule

    def _get_payment_dates(self, start_date, term_months):
        """
        Generates payment dates based on loan start date and term.

        Args:
            start_date (datetime.date): The loan start date
            term_months (int): The loan term in months

        Returns:
            list: List of payment dates
        """
        # Calculate first payment date (typically 30 days after start date)
        first_payment_date = start_date + datetime.timedelta(days=30)
        payment_dates = [first_payment_date.strftime('%B %d, %Y')]

        # Generate subsequent payment dates at 30-day intervals
        for i in range(1, term_months):
            next_payment_date = first_payment_date + datetime.timedelta(days=30 * i)
            payment_dates.append(next_payment_date.strftime('%B %d, %Y'))

        # Return the list of payment dates
        return payment_dates