"""
Implements the business rules and decision logic for loan underwriting.

This module provides functions to evaluate loan applications based on credit scores,
debt-to-income ratios, employment history, and other factors to determine approval,
denial, or revision recommendations.
"""

from decimal import Decimal
import logging

# Import application models
from ...apps.applications.models import LoanApplication

# Import underwriting models
from .models import CreditInformation

# Import user models
from ...apps.users.models import BorrowerProfile

# Import constants
from .constants import (
    AUTOMATIC_APPROVAL_CRITERIA,
    AUTOMATIC_DENIAL_CRITERIA,
    CONSIDERATION_CRITERIA,
    CREDIT_SCORE_TIERS,
    DEBT_TO_INCOME_TIERS,
    EMPLOYMENT_HISTORY_REQUIREMENTS,
    HOUSING_PAYMENT_RATIO_LIMITS,
    DECISION_REASON_CODES,
    REQUIRED_STIPULATIONS_BY_DECISION,
    CREDIT_SCORE_WEIGHT,
    DEBT_TO_INCOME_WEIGHT,
    EMPLOYMENT_HISTORY_WEIGHT,
    HOUSING_PAYMENT_WEIGHT,
    MINIMUM_INCOME_TO_LOAN_RATIO,
    BORDERLINE_CREDIT_SCORE_RANGE,
    BORDERLINE_DTI_RANGE,
    BORDERLINE_EMPLOYMENT_RANGE
)

from ...utils.constants import (
    UNDERWRITING_DECISION,
    CITIZENSHIP_STATUS
)

from ...utils.validators import ValidationError

# Set up logging
logger = logging.getLogger(__name__)


def evaluate_credit_score(credit_score):
    """
    Evaluates the credit score against approval criteria.
    
    Args:
        credit_score (int): The credit score to evaluate
        
    Returns:
        dict: Evaluation result with score, status, and reason
    """
    if credit_score is None:
        return {'status': 'consideration', 'score': 0.5}
    
    # Check for automatic approval
    if credit_score >= AUTOMATIC_APPROVAL_CRITERIA['MIN_CREDIT_SCORE']:
        return {'status': 'approved', 'score': 1.0}
    
    # Check for automatic denial
    if credit_score <= AUTOMATIC_DENIAL_CRITERIA['MAX_CREDIT_SCORE']:
        return {
            'status': 'denied', 
            'score': 0.0, 
            'reason': DECISION_REASON_CODES['CREDIT_SCORE']
        }
    
    # Score is in consideration range, calculate normalized score
    min_score = AUTOMATIC_DENIAL_CRITERIA['MAX_CREDIT_SCORE']
    max_score = AUTOMATIC_APPROVAL_CRITERIA['MIN_CREDIT_SCORE']
    range_size = max_score - min_score
    
    # Normalize to 0-1 scale
    if range_size > 0:
        normalized_score = (credit_score - min_score) / range_size
    else:
        normalized_score = 0.5
    
    return {
        'status': 'consideration',
        'score': normalized_score
    }


def evaluate_debt_to_income(dti_ratio):
    """
    Evaluates the debt-to-income ratio against approval criteria.
    
    Args:
        dti_ratio (Decimal): The debt-to-income ratio to evaluate
        
    Returns:
        dict: Evaluation result with score, status, and reason
    """
    if dti_ratio is None:
        return {'status': 'consideration', 'score': 0.5}
    
    # Check for automatic approval
    if dti_ratio <= AUTOMATIC_APPROVAL_CRITERIA['MAX_DTI']:
        return {'status': 'approved', 'score': 1.0}
    
    # Check for automatic denial
    if dti_ratio >= AUTOMATIC_DENIAL_CRITERIA['MIN_DTI']:
        return {
            'status': 'denied', 
            'score': 0.0, 
            'reason': DECISION_REASON_CODES['DEBT_TO_INCOME']
        }
    
    # DTI is in consideration range, calculate normalized score
    min_dti = AUTOMATIC_APPROVAL_CRITERIA['MAX_DTI']
    max_dti = AUTOMATIC_DENIAL_CRITERIA['MIN_DTI']
    range_size = max_dti - min_dti
    
    # Normalize to 0-1 scale (inverted because lower DTI is better)
    if range_size > 0:
        normalized_score = 1 - ((dti_ratio - min_dti) / range_size)
    else:
        normalized_score = 0.5
    
    return {
        'status': 'consideration',
        'score': normalized_score
    }


def evaluate_employment_history(employment_months):
    """
    Evaluates the employment history duration against approval criteria.
    
    Args:
        employment_months (int): The employment duration in months
        
    Returns:
        dict: Evaluation result with score, status, and reason
    """
    if employment_months is None:
        return {'status': 'consideration', 'score': 0.5}
    
    # Check for automatic approval
    if employment_months >= AUTOMATIC_APPROVAL_CRITERIA['MIN_EMPLOYMENT_MONTHS']:
        return {'status': 'approved', 'score': 1.0}
    
    # Check for automatic denial
    if employment_months < EMPLOYMENT_HISTORY_REQUIREMENTS['MINIMUM']:
        return {
            'status': 'denied', 
            'score': 0.0, 
            'reason': DECISION_REASON_CODES['EMPLOYMENT_HISTORY']
        }
    
    # Employment is in consideration range, calculate normalized score
    min_months = EMPLOYMENT_HISTORY_REQUIREMENTS['MINIMUM']
    max_months = AUTOMATIC_APPROVAL_CRITERIA['MIN_EMPLOYMENT_MONTHS']
    range_size = max_months - min_months
    
    # Normalize to 0-1 scale
    if range_size > 0:
        normalized_score = (employment_months - min_months) / range_size
    else:
        normalized_score = 0.5
    
    return {
        'status': 'consideration',
        'score': normalized_score
    }


def evaluate_housing_payment_ratio(housing_ratio):
    """
    Evaluates the housing payment to income ratio against approval criteria.
    
    Args:
        housing_ratio (Decimal): The housing payment to income ratio
        
    Returns:
        dict: Evaluation result with score, status, and reason
    """
    if housing_ratio is None:
        return {'status': 'consideration', 'score': 0.5}
    
    # Check for automatic approval
    if housing_ratio <= HOUSING_PAYMENT_RATIO_LIMITS['LOW']:
        return {'status': 'approved', 'score': 1.0}
    
    # Check for automatic denial
    if housing_ratio >= AUTOMATIC_DENIAL_CRITERIA['MAX_HOUSING_RATIO']:
        return {
            'status': 'denied', 
            'score': 0.0, 
            'reason': DECISION_REASON_CODES['HOUSING_PAYMENT']
        }
    
    # Housing ratio is in consideration range, calculate normalized score
    min_ratio = HOUSING_PAYMENT_RATIO_LIMITS['LOW']
    max_ratio = AUTOMATIC_DENIAL_CRITERIA['MAX_HOUSING_RATIO']
    range_size = max_ratio - min_ratio
    
    # Normalize to 0-1 scale (inverted because lower ratio is better)
    if range_size > 0:
        normalized_score = 1 - ((housing_ratio - min_ratio) / range_size)
    else:
        normalized_score = 0.5
    
    return {
        'status': 'consideration',
        'score': normalized_score
    }


def evaluate_income_to_loan_ratio(annual_income, loan_amount):
    """
    Evaluates the income to loan amount ratio against approval criteria.
    
    Args:
        annual_income (Decimal): The annual income amount
        loan_amount (Decimal): The requested loan amount
        
    Returns:
        dict: Evaluation result with status and reason
    """
    if annual_income is None or loan_amount is None:
        return {'status': 'consideration'}
    
    if loan_amount <= 0:
        return {'status': 'approved'}
    
    income_to_loan_ratio = annual_income / loan_amount
    
    if income_to_loan_ratio >= MINIMUM_INCOME_TO_LOAN_RATIO:
        return {'status': 'approved'}
    
    return {
        'status': 'denied',
        'reason': DECISION_REASON_CODES['INCOME_INSUFFICIENT']
    }


def evaluate_citizenship_status(citizenship_status):
    """
    Evaluates the citizenship status against approval criteria.
    
    Args:
        citizenship_status (str): The citizenship status
        
    Returns:
        dict: Evaluation result with status and reason
    """
    if citizenship_status is None:
        return {'status': 'consideration'}
    
    eligible_statuses = [
        CITIZENSHIP_STATUS['US_CITIZEN'],
        CITIZENSHIP_STATUS['PERMANENT_RESIDENT'],
        CITIZENSHIP_STATUS['ELIGIBLE_NON_CITIZEN']
    ]
    
    if citizenship_status in eligible_statuses:
        return {'status': 'approved'}
    
    return {
        'status': 'denied',
        'reason': DECISION_REASON_CODES['CITIZENSHIP_STATUS']
    }


def evaluate_program_eligibility(application):
    """
    Evaluates if the selected program is eligible for financing.
    
    Args:
        application (LoanApplication): The loan application
        
    Returns:
        dict: Evaluation result with status and reason
    """
    if not application.program:
        return {'status': 'consideration'}
    
    if application.program.status == 'active':
        return {'status': 'approved'}
    
    return {
        'status': 'denied',
        'reason': DECISION_REASON_CODES['PROGRAM_ELIGIBILITY']
    }


def calculate_weighted_score(credit_score_result, dti_result, employment_result, housing_ratio_result):
    """
    Calculates the weighted score based on individual factor evaluations.
    
    Args:
        credit_score_result (dict): Credit score evaluation result
        dti_result (dict): Debt-to-income evaluation result
        employment_result (dict): Employment history evaluation result
        housing_ratio_result (dict): Housing payment ratio evaluation result
        
    Returns:
        float: Weighted score between 0 and 1
    """
    # Extract scores from evaluation results, defaulting to 0.5 if not present
    credit_score = credit_score_result.get('score', 0.5)
    dti = dti_result.get('score', 0.5)
    employment = employment_result.get('score', 0.5)
    housing = housing_ratio_result.get('score', 0.5)
    
    # Calculate weighted score
    weighted_score = (
        (credit_score * CREDIT_SCORE_WEIGHT) +
        (dti * DEBT_TO_INCOME_WEIGHT) +
        (employment * EMPLOYMENT_HISTORY_WEIGHT) +
        (housing * HOUSING_PAYMENT_WEIGHT)
    )
    
    return weighted_score


def determine_required_stipulations(decision, evaluation_results):
    """
    Determines the required stipulations based on decision and risk factors.
    
    Args:
        decision (str): The underwriting decision
        evaluation_results (dict): Evaluation results for all factors
        
    Returns:
        list: List of required stipulation types
    """
    stipulations = []
    
    # Add base stipulations for the decision type
    base_stipulations = REQUIRED_STIPULATIONS_BY_DECISION.get(decision, [])
    stipulations.extend(base_stipulations)
    
    # Add additional stipulations based on risk factors
    credit_result = evaluation_results.get('credit_score', {})
    dti_result = evaluation_results.get('dti_ratio', {})
    employment_result = evaluation_results.get('employment_history', {})
    
    # If credit score is borderline, add identity verification
    if credit_result.get('status') == 'consideration':
        if 'PROOF_OF_IDENTITY' not in stipulations:
            stipulations.append('PROOF_OF_IDENTITY')
    
    # If DTI is borderline, add income verification
    if dti_result.get('status') == 'consideration':
        if 'PROOF_OF_INCOME' not in stipulations:
            stipulations.append('PROOF_OF_INCOME')
    
    # If employment history is borderline, add additional documentation
    if employment_result.get('status') == 'consideration':
        if 'ADDITIONAL_DOCUMENTATION' not in stipulations:
            stipulations.append('ADDITIONAL_DOCUMENTATION')
    
    return stipulations


def get_decision_reasons(evaluation_results):
    """
    Extracts decision reasons from evaluation results.
    
    Args:
        evaluation_results (dict): Evaluation results for all factors
        
    Returns:
        list: List of reason codes for the decision
    """
    reasons = []
    
    # Iterate through all evaluation results
    for factor, result in evaluation_results.items():
        if 'reason' in result and result['reason'] not in reasons:
            reasons.append(result['reason'])
    
    return reasons


def evaluate_application(application, credit_info):
    """
    Performs comprehensive evaluation of a loan application.
    
    Args:
        application (LoanApplication): The loan application to evaluate
        credit_info (CreditInformation): Credit information for the borrower
        
    Returns:
        dict: Complete evaluation result with decision, reasons, and stipulations
    """
    logger.info(f"Evaluating application {application.id}")
    
    # Get loan details
    loan_details = application.get_loan_details()
    
    # Get borrower profile
    borrower_profile = application.borrower.get_profile()
    
    # Initialize evaluation results dictionary
    evaluation_results = {}
    
    # Evaluate credit score
    credit_score_result = evaluate_credit_score(credit_info.credit_score)
    evaluation_results['credit_score'] = credit_score_result
    
    # Evaluate debt-to-income ratio
    dti_ratio = credit_info.debt_to_income_ratio
    dti_result = evaluate_debt_to_income(dti_ratio)
    evaluation_results['dti_ratio'] = dti_result
    
    # Get employment info and evaluate
    try:
        employment_info = borrower_profile.employment_info.first()
        employment_months = employment_info.get_total_employment_duration()
    except (AttributeError, IndexError):
        employment_months = None
    
    employment_result = evaluate_employment_history(employment_months)
    evaluation_results['employment_history'] = employment_result
    
    # Calculate and evaluate housing payment ratio
    try:
        monthly_income = employment_info.get_monthly_income()
        housing_payment = borrower_profile.housing_payment
        housing_ratio = housing_payment / monthly_income
    except (AttributeError, ZeroDivisionError):
        housing_ratio = None
    
    housing_ratio_result = evaluate_housing_payment_ratio(housing_ratio)
    evaluation_results['housing_ratio'] = housing_ratio_result
    
    # Evaluate income to loan ratio
    try:
        annual_income = employment_info.annual_income
        loan_amount = loan_details.requested_amount
    except AttributeError:
        annual_income = None
        loan_amount = None
    
    income_ratio_result = evaluate_income_to_loan_ratio(annual_income, loan_amount)
    evaluation_results['income_ratio'] = income_ratio_result
    
    # Evaluate citizenship status
    citizenship_result = evaluate_citizenship_status(borrower_profile.citizenship_status)
    evaluation_results['citizenship'] = citizenship_result
    
    # Evaluate program eligibility
    program_result = evaluate_program_eligibility(application)
    evaluation_results['program'] = program_result
    
    # Check for any automatic denials
    for factor, result in evaluation_results.items():
        if result.get('status') == 'denied':
            decision = UNDERWRITING_DECISION['DENY']
            reasons = get_decision_reasons(evaluation_results)
            stipulations = []
            
            logger.info(f"Application {application.id} denied: {reasons}")
            
            return {
                'decision': decision,
                'reasons': reasons,
                'stipulations': stipulations,
                'evaluation_results': evaluation_results,
                'score': 0.0
            }
    
    # Calculate weighted score for consideration
    weighted_score = calculate_weighted_score(
        credit_score_result,
        dti_result,
        employment_result,
        housing_ratio_result
    )
    
    # Determine decision based on weighted score
    if weighted_score >= 0.7:
        decision = UNDERWRITING_DECISION['APPROVE']
    elif weighted_score < 0.4:
        decision = UNDERWRITING_DECISION['DENY']
    else:
        decision = UNDERWRITING_DECISION['REVISE']
    
    # Get decision reasons
    reasons = get_decision_reasons(evaluation_results)
    
    # Determine required stipulations
    stipulations = determine_required_stipulations(decision, evaluation_results)
    
    logger.info(f"Application {application.id} evaluated: {decision} with score {weighted_score}")
    
    return {
        'decision': decision,
        'reasons': reasons,
        'stipulations': stipulations,
        'evaluation_results': evaluation_results,
        'score': weighted_score
    }


class UnderwritingRuleEngine:
    """
    Engine for applying underwriting rules to loan applications.
    """
    
    def __init__(self):
        """
        Initialize the rule engine.
        """
        self.logger = logging.getLogger(__name__)
    
    def evaluate_application(self, application, credit_info):
        """
        Evaluates a loan application against underwriting rules.
        
        Args:
            application (LoanApplication): The loan application to evaluate
            credit_info (CreditInformation): Credit information for the borrower
            
        Returns:
            dict: Evaluation result with decision, reasons, and stipulations
        """
        return evaluate_application(application, credit_info)
    
    def get_auto_decision(self, application, credit_info):
        """
        Attempts to make an automatic decision based on clear criteria.
        
        Args:
            application (LoanApplication): The loan application to evaluate
            credit_info (CreditInformation): Credit information for the borrower
            
        Returns:
            dict: Automatic decision result or None if manual review needed
        """
        # Get borrower profile
        borrower_profile = application.borrower.get_profile()
        
        # Get loan details
        loan_details = application.get_loan_details()
        
        # Check for automatic approval criteria
        if (credit_info.credit_score >= AUTOMATIC_APPROVAL_CRITERIA['MIN_CREDIT_SCORE'] and
            credit_info.debt_to_income_ratio <= AUTOMATIC_APPROVAL_CRITERIA['MAX_DTI']):
            
            # Get employment info
            try:
                employment_info = borrower_profile.employment_info.first()
                employment_months = employment_info.get_total_employment_duration()
                
                # If employment meets criteria, approve
                if employment_months >= AUTOMATIC_APPROVAL_CRITERIA['MIN_EMPLOYMENT_MONTHS']:
                    return {
                        'decision': UNDERWRITING_DECISION['APPROVE'],
                        'reasons': [],
                        'stipulations': determine_required_stipulations(
                            UNDERWRITING_DECISION['APPROVE'], {}
                        ),
                        'auto_approved': True
                    }
            except (AttributeError, IndexError):
                pass
        
        # Check for automatic denial criteria
        if (credit_info.credit_score <= AUTOMATIC_DENIAL_CRITERIA['MAX_CREDIT_SCORE'] or
            credit_info.debt_to_income_ratio >= AUTOMATIC_DENIAL_CRITERIA['MIN_DTI']):
            
            reasons = []
            
            if credit_info.credit_score <= AUTOMATIC_DENIAL_CRITERIA['MAX_CREDIT_SCORE']:
                reasons.append(DECISION_REASON_CODES['CREDIT_SCORE'])
                
            if credit_info.debt_to_income_ratio >= AUTOMATIC_DENIAL_CRITERIA['MIN_DTI']:
                reasons.append(DECISION_REASON_CODES['DEBT_TO_INCOME'])
            
            return {
                'decision': UNDERWRITING_DECISION['DENY'],
                'reasons': reasons,
                'stipulations': [],
                'auto_denied': True
            }
        
        # If neither auto-approve nor auto-deny, return None to indicate manual review needed
        return None
    
    def calculate_risk_score(self, application, credit_info):
        """
        Calculates a risk score for the application.
        
        Args:
            application (LoanApplication): The loan application to evaluate
            credit_info (CreditInformation): Credit information for the borrower
            
        Returns:
            float: Risk score between 0 (highest risk) and 100 (lowest risk)
        """
        # Get borrower profile
        borrower_profile = application.borrower.get_profile()
        
        # Evaluate individual factors
        credit_score_result = evaluate_credit_score(credit_info.credit_score)
        dti_result = evaluate_debt_to_income(credit_info.debt_to_income_ratio)
        
        # Get employment info and evaluate
        try:
            employment_info = borrower_profile.employment_info.first()
            employment_months = employment_info.get_total_employment_duration()
        except (AttributeError, IndexError):
            employment_months = None
        
        employment_result = evaluate_employment_history(employment_months)
        
        # Calculate and evaluate housing payment ratio
        try:
            monthly_income = employment_info.get_monthly_income()
            housing_payment = borrower_profile.housing_payment
            housing_ratio = housing_payment / monthly_income
        except (AttributeError, ZeroDivisionError):
            housing_ratio = None
        
        housing_ratio_result = evaluate_housing_payment_ratio(housing_ratio)
        
        # Calculate weighted score
        weighted_score = calculate_weighted_score(
            credit_score_result,
            dti_result,
            employment_result,
            housing_ratio_result
        )
        
        # Scale to 0-100 range (higher is better/less risky)
        risk_score = weighted_score * 100
        
        return risk_score