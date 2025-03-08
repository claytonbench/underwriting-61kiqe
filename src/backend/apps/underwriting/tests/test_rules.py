import unittest
from decimal import Decimal

from ..rules import (
    evaluate_credit_score, evaluate_debt_to_income, evaluate_employment_history,
    evaluate_housing_payment_ratio, evaluate_income_to_loan_ratio,
    evaluate_citizenship_status, evaluate_program_eligibility,
    calculate_weighted_score, determine_required_stipulations,
    get_decision_reasons, evaluate_application, UnderwritingRuleEngine
)
from ..constants import (
    AUTOMATIC_APPROVAL_CRITERIA, AUTOMATIC_DENIAL_CRITERIA, CONSIDERATION_CRITERIA,
    DECISION_REASON_CODES, REQUIRED_STIPULATIONS_BY_DECISION,
    BORDERLINE_CREDIT_SCORE_RANGE, BORDERLINE_DTI_RANGE, BORDERLINE_EMPLOYMENT_RANGE,
    EMPLOYMENT_HISTORY_REQUIREMENTS, HOUSING_PAYMENT_RATIO_LIMITS,
    CREDIT_SCORE_WEIGHT, DEBT_TO_INCOME_WEIGHT, EMPLOYMENT_HISTORY_WEIGHT, HOUSING_PAYMENT_WEIGHT
)
from ../../../utils/constants import (
    UNDERWRITING_DECISION, CITIZENSHIP_STATUS
)
from ../../applications/models import LoanApplication, LoanDetails
from ../../users/models import BorrowerProfile
from ../models import CreditInformation
from ../../schools/models import Program


class TestCreditScoreEvaluation(unittest.TestCase):
    """Test cases for the credit score evaluation function"""
    
    def setUp(self):
        """Initialize the test case"""
        super().setUp()
    
    def test_excellent_credit_score(self):
        """Test that excellent credit scores result in automatic approval"""
        # Create a credit score above the automatic approval threshold
        credit_score = AUTOMATIC_APPROVAL_CRITERIA['MIN_CREDIT_SCORE'] + 20
        
        # Call evaluate_credit_score with the excellent score
        result = evaluate_credit_score(credit_score)
        
        # Assert that the result status is 'approved'
        self.assertEqual(result['status'], 'approved')
        # Assert that the score is 1.0
        self.assertEqual(result['score'], 1.0)
    
    def test_poor_credit_score(self):
        """Test that poor credit scores result in automatic denial"""
        # Create a credit score below the automatic denial threshold
        credit_score = AUTOMATIC_DENIAL_CRITERIA['MAX_CREDIT_SCORE'] - 20
        
        # Call evaluate_credit_score with the poor score
        result = evaluate_credit_score(credit_score)
        
        # Assert that the result status is 'denied'
        self.assertEqual(result['status'], 'denied')
        # Assert that the score is 0.0
        self.assertEqual(result['score'], 0.0)
        # Assert that the reason is DECISION_REASON_CODES['CREDIT_SCORE']
        self.assertEqual(result['reason'], DECISION_REASON_CODES['CREDIT_SCORE'])
    
    def test_borderline_credit_score(self):
        """Test that borderline credit scores result in consideration status"""
        # Create a credit score between approval and denial thresholds
        credit_score = (AUTOMATIC_APPROVAL_CRITERIA['MIN_CREDIT_SCORE'] + 
                       AUTOMATIC_DENIAL_CRITERIA['MAX_CREDIT_SCORE']) // 2
        
        # Call evaluate_credit_score with the borderline score
        result = evaluate_credit_score(credit_score)
        
        # Assert that the result status is 'consideration'
        self.assertEqual(result['status'], 'consideration')
        # Assert that the score is between 0.0 and 1.0
        self.assertTrue(0.0 < result['score'] < 1.0)
    
    def test_null_credit_score(self):
        """Test handling of null credit score values"""
        # Call evaluate_credit_score with None
        result = evaluate_credit_score(None)
        
        # Assert that the result status is 'consideration'
        self.assertEqual(result['status'], 'consideration')
        # Assert that the score is 0.5
        self.assertEqual(result['score'], 0.5)


class TestDebtToIncomeEvaluation(unittest.TestCase):
    """Test cases for the debt-to-income ratio evaluation function"""
    
    def setUp(self):
        """Initialize the test case"""
        super().setUp()
    
    def test_low_dti_ratio(self):
        """Test that low DTI ratios result in automatic approval"""
        # Create a DTI ratio below the automatic approval threshold
        dti_ratio = AUTOMATIC_APPROVAL_CRITERIA['MAX_DTI'] - Decimal('0.05')
        
        # Call evaluate_debt_to_income with the low ratio
        result = evaluate_debt_to_income(dti_ratio)
        
        # Assert that the result status is 'approved'
        self.assertEqual(result['status'], 'approved')
        # Assert that the score is 1.0
        self.assertEqual(result['score'], 1.0)
    
    def test_high_dti_ratio(self):
        """Test that high DTI ratios result in automatic denial"""
        # Create a DTI ratio above the automatic denial threshold
        dti_ratio = AUTOMATIC_DENIAL_CRITERIA['MIN_DTI'] + Decimal('0.05')
        
        # Call evaluate_debt_to_income with the high ratio
        result = evaluate_debt_to_income(dti_ratio)
        
        # Assert that the result status is 'denied'
        self.assertEqual(result['status'], 'denied')
        # Assert that the score is 0.0
        self.assertEqual(result['score'], 0.0)
        # Assert that the reason is DECISION_REASON_CODES['DEBT_TO_INCOME']
        self.assertEqual(result['reason'], DECISION_REASON_CODES['DEBT_TO_INCOME'])
    
    def test_borderline_dti_ratio(self):
        """Test that borderline DTI ratios result in consideration status"""
        # Create a DTI ratio between approval and denial thresholds
        dti_ratio = (AUTOMATIC_APPROVAL_CRITERIA['MAX_DTI'] + 
                     AUTOMATIC_DENIAL_CRITERIA['MIN_DTI']) / 2
        
        # Call evaluate_debt_to_income with the borderline ratio
        result = evaluate_debt_to_income(dti_ratio)
        
        # Assert that the result status is 'consideration'
        self.assertEqual(result['status'], 'consideration')
        # Assert that the score is between 0.0 and 1.0
        self.assertTrue(0.0 < result['score'] < 1.0)
    
    def test_null_dti_ratio(self):
        """Test handling of null DTI ratio values"""
        # Call evaluate_debt_to_income with None
        result = evaluate_debt_to_income(None)
        
        # Assert that the result status is 'consideration'
        self.assertEqual(result['status'], 'consideration')
        # Assert that the score is 0.5
        self.assertEqual(result['score'], 0.5)


class TestEmploymentHistoryEvaluation(unittest.TestCase):
    """Test cases for the employment history evaluation function"""
    
    def setUp(self):
        """Initialize the test case"""
        super().setUp()
    
    def test_long_employment_history(self):
        """Test that long employment history results in automatic approval"""
        # Create an employment duration above the automatic approval threshold
        employment_months = AUTOMATIC_APPROVAL_CRITERIA['MIN_EMPLOYMENT_MONTHS'] + 6
        
        # Call evaluate_employment_history with the long duration
        result = evaluate_employment_history(employment_months)
        
        # Assert that the result status is 'approved'
        self.assertEqual(result['status'], 'approved')
        # Assert that the score is 1.0
        self.assertEqual(result['score'], 1.0)
    
    def test_short_employment_history(self):
        """Test that very short employment history results in automatic denial"""
        # Create an employment duration below the minimum threshold
        employment_months = EMPLOYMENT_HISTORY_REQUIREMENTS['MINIMUM'] - 1
        
        # Call evaluate_employment_history with the short duration
        result = evaluate_employment_history(employment_months)
        
        # Assert that the result status is 'denied'
        self.assertEqual(result['status'], 'denied')
        # Assert that the score is 0.0
        self.assertEqual(result['score'], 0.0)
        # Assert that the reason is DECISION_REASON_CODES['EMPLOYMENT_HISTORY']
        self.assertEqual(result['reason'], DECISION_REASON_CODES['EMPLOYMENT_HISTORY'])
    
    def test_borderline_employment_history(self):
        """Test that borderline employment history results in consideration status"""
        # Create an employment duration between approval and denial thresholds
        employment_months = (AUTOMATIC_APPROVAL_CRITERIA['MIN_EMPLOYMENT_MONTHS'] + 
                            EMPLOYMENT_HISTORY_REQUIREMENTS['MINIMUM']) // 2
        
        # Call evaluate_employment_history with the borderline duration
        result = evaluate_employment_history(employment_months)
        
        # Assert that the result status is 'consideration'
        self.assertEqual(result['status'], 'consideration')
        # Assert that the score is between 0.0 and 1.0
        self.assertTrue(0.0 < result['score'] < 1.0)
    
    def test_null_employment_history(self):
        """Test handling of null employment history values"""
        # Call evaluate_employment_history with None
        result = evaluate_employment_history(None)
        
        # Assert that the result status is 'consideration'
        self.assertEqual(result['status'], 'consideration')
        # Assert that the score is 0.5
        self.assertEqual(result['score'], 0.5)


class TestHousingPaymentRatioEvaluation(unittest.TestCase):
    """Test cases for the housing payment ratio evaluation function"""
    
    def setUp(self):
        """Initialize the test case"""
        super().setUp()
    
    def test_low_housing_ratio(self):
        """Test that low housing payment ratios result in automatic approval"""
        # Create a housing ratio below the automatic approval threshold
        housing_ratio = HOUSING_PAYMENT_RATIO_LIMITS['LOW'] - Decimal('0.05')
        
        # Call evaluate_housing_payment_ratio with the low ratio
        result = evaluate_housing_payment_ratio(housing_ratio)
        
        # Assert that the result status is 'approved'
        self.assertEqual(result['status'], 'approved')
        # Assert that the score is 1.0
        self.assertEqual(result['score'], 1.0)
    
    def test_high_housing_ratio(self):
        """Test that high housing payment ratios result in automatic denial"""
        # Create a housing ratio above the automatic denial threshold
        housing_ratio = AUTOMATIC_DENIAL_CRITERIA['MAX_HOUSING_RATIO'] + Decimal('0.05')
        
        # Call evaluate_housing_payment_ratio with the high ratio
        result = evaluate_housing_payment_ratio(housing_ratio)
        
        # Assert that the result status is 'denied'
        self.assertEqual(result['status'], 'denied')
        # Assert that the score is 0.0
        self.assertEqual(result['score'], 0.0)
        # Assert that the reason is DECISION_REASON_CODES['HOUSING_PAYMENT']
        self.assertEqual(result['reason'], DECISION_REASON_CODES['HOUSING_PAYMENT'])
    
    def test_borderline_housing_ratio(self):
        """Test that borderline housing payment ratios result in consideration status"""
        # Create a housing ratio between approval and denial thresholds
        housing_ratio = (HOUSING_PAYMENT_RATIO_LIMITS['LOW'] + 
                        AUTOMATIC_DENIAL_CRITERIA['MAX_HOUSING_RATIO']) / 2
        
        # Call evaluate_housing_payment_ratio with the borderline ratio
        result = evaluate_housing_payment_ratio(housing_ratio)
        
        # Assert that the result status is 'consideration'
        self.assertEqual(result['status'], 'consideration')
        # Assert that the score is between 0.0 and 1.0
        self.assertTrue(0.0 < result['score'] < 1.0)
    
    def test_null_housing_ratio(self):
        """Test handling of null housing payment ratio values"""
        # Call evaluate_housing_payment_ratio with None
        result = evaluate_housing_payment_ratio(None)
        
        # Assert that the result status is 'consideration'
        self.assertEqual(result['status'], 'consideration')
        # Assert that the score is 0.5
        self.assertEqual(result['score'], 0.5)


class TestIncomeToLoanRatioEvaluation(unittest.TestCase):
    """Test cases for the income to loan ratio evaluation function"""
    
    def setUp(self):
        """Initialize the test case"""
        super().setUp()
    
    def test_sufficient_income(self):
        """Test that sufficient income to loan ratio results in approval"""
        # Create annual income and loan amount with ratio above minimum threshold
        annual_income = Decimal('50000')
        loan_amount = Decimal('20000')  # Ratio of 2.5, above MINIMUM_INCOME_TO_LOAN_RATIO (2.0)
        
        # Call evaluate_income_to_loan_ratio with the values
        result = evaluate_income_to_loan_ratio(annual_income, loan_amount)
        
        # Assert that the result status is 'approved'
        self.assertEqual(result['status'], 'approved')
    
    def test_insufficient_income(self):
        """Test that insufficient income to loan ratio results in denial"""
        # Create annual income and loan amount with ratio below minimum threshold
        annual_income = Decimal('30000')
        loan_amount = Decimal('20000')  # Ratio of 1.5, below MINIMUM_INCOME_TO_LOAN_RATIO (2.0)
        
        # Call evaluate_income_to_loan_ratio with the values
        result = evaluate_income_to_loan_ratio(annual_income, loan_amount)
        
        # Assert that the result status is 'denied'
        self.assertEqual(result['status'], 'denied')
        # Assert that the reason is DECISION_REASON_CODES['INCOME_INSUFFICIENT']
        self.assertEqual(result['reason'], DECISION_REASON_CODES['INCOME_INSUFFICIENT'])
    
    def test_null_income_or_loan(self):
        """Test handling of null income or loan amount values"""
        # Call evaluate_income_to_loan_ratio with None for income
        result = evaluate_income_to_loan_ratio(None, Decimal('10000'))
        
        # Assert that the result status is 'consideration'
        self.assertEqual(result['status'], 'consideration')
        
        # Call evaluate_income_to_loan_ratio with None for loan amount
        result = evaluate_income_to_loan_ratio(Decimal('50000'), None)
        
        # Assert that the result status is 'consideration'
        self.assertEqual(result['status'], 'consideration')


class TestCitizenshipStatusEvaluation(unittest.TestCase):
    """Test cases for the citizenship status evaluation function"""
    
    def setUp(self):
        """Initialize the test case"""
        super().setUp()
    
    def test_us_citizen(self):
        """Test that US citizen status results in approval"""
        # Call evaluate_citizenship_status with CITIZENSHIP_STATUS['US_CITIZEN']
        result = evaluate_citizenship_status(CITIZENSHIP_STATUS['US_CITIZEN'])
        
        # Assert that the result status is 'approved'
        self.assertEqual(result['status'], 'approved')
    
    def test_permanent_resident(self):
        """Test that permanent resident status results in approval"""
        # Call evaluate_citizenship_status with CITIZENSHIP_STATUS['PERMANENT_RESIDENT']
        result = evaluate_citizenship_status(CITIZENSHIP_STATUS['PERMANENT_RESIDENT'])
        
        # Assert that the result status is 'approved'
        self.assertEqual(result['status'], 'approved')
    
    def test_eligible_non_citizen(self):
        """Test that eligible non-citizen status results in approval"""
        # Call evaluate_citizenship_status with CITIZENSHIP_STATUS['ELIGIBLE_NON_CITIZEN']
        result = evaluate_citizenship_status(CITIZENSHIP_STATUS['ELIGIBLE_NON_CITIZEN'])
        
        # Assert that the result status is 'approved'
        self.assertEqual(result['status'], 'approved')
    
    def test_ineligible_non_citizen(self):
        """Test that ineligible non-citizen status results in denial"""
        # Call evaluate_citizenship_status with CITIZENSHIP_STATUS['INELIGIBLE_NON_CITIZEN']
        result = evaluate_citizenship_status(CITIZENSHIP_STATUS['INELIGIBLE_NON_CITIZEN'])
        
        # Assert that the result status is 'denied'
        self.assertEqual(result['status'], 'denied')
        # Assert that the reason is DECISION_REASON_CODES['CITIZENSHIP_STATUS']
        self.assertEqual(result['reason'], DECISION_REASON_CODES['CITIZENSHIP_STATUS'])
    
    def test_null_citizenship_status(self):
        """Test handling of null citizenship status values"""
        # Call evaluate_citizenship_status with None
        result = evaluate_citizenship_status(None)
        
        # Assert that the result status is 'consideration'
        self.assertEqual(result['status'], 'consideration')


class TestProgramEligibilityEvaluation(unittest.TestCase):
    """Test cases for the program eligibility evaluation function"""
    
    def setUp(self):
        """Initialize the test case"""
        super().setUp()
    
    def test_active_program(self):
        """Test that active program results in approval"""
        # Create a mock LoanApplication with active program
        application = unittest.mock.Mock(spec=LoanApplication)
        application.program = unittest.mock.Mock(spec=Program)
        application.program.status = 'active'
        
        # Call evaluate_program_eligibility with the application
        result = evaluate_program_eligibility(application)
        
        # Assert that the result status is 'approved'
        self.assertEqual(result['status'], 'approved')
    
    def test_inactive_program(self):
        """Test that inactive program results in denial"""
        # Create a mock LoanApplication with inactive program
        application = unittest.mock.Mock(spec=LoanApplication)
        application.program = unittest.mock.Mock(spec=Program)
        application.program.status = 'inactive'
        
        # Call evaluate_program_eligibility with the application
        result = evaluate_program_eligibility(application)
        
        # Assert that the result status is 'denied'
        self.assertEqual(result['status'], 'denied')
        # Assert that the reason is DECISION_REASON_CODES['PROGRAM_ELIGIBILITY']
        self.assertEqual(result['reason'], DECISION_REASON_CODES['PROGRAM_ELIGIBILITY'])
    
    def test_null_program(self):
        """Test handling of null program values"""
        # Create a mock LoanApplication with null program
        application = unittest.mock.Mock(spec=LoanApplication)
        application.program = None
        
        # Call evaluate_program_eligibility with the application
        result = evaluate_program_eligibility(application)
        
        # Assert that the result status is 'consideration'
        self.assertEqual(result['status'], 'consideration')


class TestWeightedScoreCalculation(unittest.TestCase):
    """Test cases for the weighted score calculation function"""
    
    def setUp(self):
        """Initialize the test case"""
        super().setUp()
    
    def test_all_approved_factors(self):
        """Test weighted score calculation with all factors approved"""
        # Create result dictionaries with status 'approved' and score 1.0 for all factors
        credit_score_result = {'status': 'approved', 'score': 1.0}
        dti_result = {'status': 'approved', 'score': 1.0}
        employment_result = {'status': 'approved', 'score': 1.0}
        housing_ratio_result = {'status': 'approved', 'score': 1.0}
        
        # Call calculate_weighted_score with the results
        weighted_score = calculate_weighted_score(
            credit_score_result, dti_result, employment_result, housing_ratio_result
        )
        
        # Assert that the weighted score is 1.0
        self.assertEqual(weighted_score, 1.0)
    
    def test_all_denied_factors(self):
        """Test weighted score calculation with all factors denied"""
        # Create result dictionaries with status 'denied' and score 0.0 for all factors
        credit_score_result = {'status': 'denied', 'score': 0.0}
        dti_result = {'status': 'denied', 'score': 0.0}
        employment_result = {'status': 'denied', 'score': 0.0}
        housing_ratio_result = {'status': 'denied', 'score': 0.0}
        
        # Call calculate_weighted_score with the results
        weighted_score = calculate_weighted_score(
            credit_score_result, dti_result, employment_result, housing_ratio_result
        )
        
        # Assert that the weighted score is 0.0
        self.assertEqual(weighted_score, 0.0)
    
    def test_mixed_factors(self):
        """Test weighted score calculation with mixed factor results"""
        # Create result dictionaries with mixed statuses and scores
        credit_score_result = {'status': 'approved', 'score': 1.0}
        dti_result = {'status': 'consideration', 'score': 0.5}
        employment_result = {'status': 'denied', 'score': 0.0}
        housing_ratio_result = {'status': 'consideration', 'score': 0.7}
        
        # Call calculate_weighted_score with the results
        weighted_score = calculate_weighted_score(
            credit_score_result, dti_result, employment_result, housing_ratio_result
        )
        
        # Assert that the weighted score is between 0.0 and 1.0
        self.assertTrue(0.0 < weighted_score < 1.0)
        
        # Verify the calculation matches expected value based on weights
        expected_score = (
            (1.0 * CREDIT_SCORE_WEIGHT) +
            (0.5 * DEBT_TO_INCOME_WEIGHT) +
            (0.0 * EMPLOYMENT_HISTORY_WEIGHT) +
            (0.7 * HOUSING_PAYMENT_WEIGHT)
        )
        self.assertAlmostEqual(weighted_score, expected_score, places=6)
    
    def test_missing_scores(self):
        """Test weighted score calculation with missing scores"""
        # Create result dictionaries with some missing score values
        credit_score_result = {'status': 'approved'}  # No score
        dti_result = {'status': 'consideration', 'score': 0.5}
        employment_result = {}  # No status or score
        housing_ratio_result = {'status': 'denied', 'score': 0.0}
        
        # Call calculate_weighted_score with the results
        weighted_score = calculate_weighted_score(
            credit_score_result, dti_result, employment_result, housing_ratio_result
        )
        
        # Assert that the function handles missing scores by using default value of 0.5
        expected_score = (
            (0.5 * CREDIT_SCORE_WEIGHT) +  # Default value used
            (0.5 * DEBT_TO_INCOME_WEIGHT) +
            (0.5 * EMPLOYMENT_HISTORY_WEIGHT) +  # Default value used
            (0.0 * HOUSING_PAYMENT_WEIGHT)
        )
        self.assertAlmostEqual(weighted_score, expected_score, places=6)


class TestRequiredStipulationsDetermination(unittest.TestCase):
    """Test cases for the required stipulations determination function"""
    
    def setUp(self):
        """Initialize the test case"""
        super().setUp()
    
    def test_approval_stipulations(self):
        """Test stipulations for approval decision"""
        # Create evaluation results with no borderline factors
        evaluation_results = {
            'credit_score': {'status': 'approved', 'score': 1.0},
            'dti_ratio': {'status': 'approved', 'score': 1.0},
            'employment_history': {'status': 'approved', 'score': 1.0}
        }
        
        # Call determine_required_stipulations with 'approve' decision and results
        stipulations = determine_required_stipulations('approve', evaluation_results)
        
        # Assert that the stipulations match REQUIRED_STIPULATIONS_BY_DECISION['approve']
        self.assertEqual(set(stipulations), set(REQUIRED_STIPULATIONS_BY_DECISION['approve']))
    
    def test_revision_stipulations(self):
        """Test stipulations for revision decision"""
        # Create evaluation results with no borderline factors
        evaluation_results = {
            'credit_score': {'status': 'consideration', 'score': 0.5},
            'dti_ratio': {'status': 'consideration', 'score': 0.5},
            'employment_history': {'status': 'consideration', 'score': 0.5}
        }
        
        # Call determine_required_stipulations with 'revise' decision and results
        stipulations = determine_required_stipulations('revise', evaluation_results)
        
        # Assert that the stipulations match REQUIRED_STIPULATIONS_BY_DECISION['revise']
        self.assertEqual(set(stipulations), set(REQUIRED_STIPULATIONS_BY_DECISION['revise']))
    
    def test_denial_stipulations(self):
        """Test stipulations for denial decision"""
        # Create evaluation results with no borderline factors
        evaluation_results = {
            'credit_score': {'status': 'denied', 'score': 0.0},
            'dti_ratio': {'status': 'denied', 'score': 0.0},
            'employment_history': {'status': 'denied', 'score': 0.0}
        }
        
        # Call determine_required_stipulations with 'deny' decision and results
        stipulations = determine_required_stipulations('deny', evaluation_results)
        
        # Assert that the stipulations match REQUIRED_STIPULATIONS_BY_DECISION['deny']
        self.assertEqual(set(stipulations), set(REQUIRED_STIPULATIONS_BY_DECISION['deny']))
    
    def test_borderline_credit_stipulations(self):
        """Test additional stipulations for borderline credit score"""
        # Create evaluation results with borderline credit score
        evaluation_results = {
            'credit_score': {'status': 'consideration', 'score': 0.5},
            'dti_ratio': {'status': 'approved', 'score': 1.0},
            'employment_history': {'status': 'approved', 'score': 1.0}
        }
        
        # Call determine_required_stipulations with 'approve' decision and results
        stipulations = determine_required_stipulations('approve', evaluation_results)
        
        # Assert that the stipulations include identity verification stipulation
        expected_stipulations = set(REQUIRED_STIPULATIONS_BY_DECISION['approve'] + ['PROOF_OF_IDENTITY'])
        self.assertEqual(set(stipulations), expected_stipulations)
    
    def test_borderline_dti_stipulations(self):
        """Test additional stipulations for borderline DTI ratio"""
        # Create evaluation results with borderline DTI ratio
        evaluation_results = {
            'credit_score': {'status': 'approved', 'score': 1.0},
            'dti_ratio': {'status': 'consideration', 'score': 0.5},
            'employment_history': {'status': 'approved', 'score': 1.0}
        }
        
        # Call determine_required_stipulations with 'approve' decision and results
        stipulations = determine_required_stipulations('approve', evaluation_results)
        
        # Assert that the stipulations include income verification stipulation
        expected_stipulations = set(REQUIRED_STIPULATIONS_BY_DECISION['approve'] + ['PROOF_OF_INCOME'])
        self.assertEqual(set(stipulations), expected_stipulations)
    
    def test_borderline_employment_stipulations(self):
        """Test additional stipulations for borderline employment history"""
        # Create evaluation results with borderline employment history
        evaluation_results = {
            'credit_score': {'status': 'approved', 'score': 1.0},
            'dti_ratio': {'status': 'approved', 'score': 1.0},
            'employment_history': {'status': 'consideration', 'score': 0.5}
        }
        
        # Call determine_required_stipulations with 'approve' decision and results
        stipulations = determine_required_stipulations('approve', evaluation_results)
        
        # Assert that the stipulations include additional documentation stipulation
        expected_stipulations = set(REQUIRED_STIPULATIONS_BY_DECISION['approve'] + ['ADDITIONAL_DOCUMENTATION'])
        self.assertEqual(set(stipulations), expected_stipulations)


class TestDecisionReasonsExtraction(unittest.TestCase):
    """Test cases for the decision reasons extraction function"""
    
    def setUp(self):
        """Initialize the test case"""
        super().setUp()
    
    def test_no_reasons(self):
        """Test extraction with no reasons in results"""
        # Create evaluation results with no reason fields
        evaluation_results = {
            'credit_score': {'status': 'approved', 'score': 1.0},
            'dti_ratio': {'status': 'approved', 'score': 1.0},
            'employment_history': {'status': 'approved', 'score': 1.0}
        }
        
        # Call get_decision_reasons with the results
        reasons = get_decision_reasons(evaluation_results)
        
        # Assert that an empty list is returned
        self.assertEqual(reasons, [])
    
    def test_single_reason(self):
        """Test extraction with a single reason in results"""
        # Create evaluation results with one reason field
        evaluation_results = {
            'credit_score': {'status': 'denied', 'score': 0.0, 
                             'reason': DECISION_REASON_CODES['CREDIT_SCORE']},
            'dti_ratio': {'status': 'approved', 'score': 1.0},
            'employment_history': {'status': 'approved', 'score': 1.0}
        }
        
        # Call get_decision_reasons with the results
        reasons = get_decision_reasons(evaluation_results)
        
        # Assert that a list with the single reason is returned
        self.assertEqual(reasons, [DECISION_REASON_CODES['CREDIT_SCORE']])
    
    def test_multiple_reasons(self):
        """Test extraction with multiple reasons in results"""
        # Create evaluation results with multiple reason fields
        evaluation_results = {
            'credit_score': {'status': 'denied', 'score': 0.0, 
                             'reason': DECISION_REASON_CODES['CREDIT_SCORE']},
            'dti_ratio': {'status': 'denied', 'score': 0.0, 
                          'reason': DECISION_REASON_CODES['DEBT_TO_INCOME']},
            'employment_history': {'status': 'denied', 'score': 0.0, 
                                  'reason': DECISION_REASON_CODES['EMPLOYMENT_HISTORY']}
        }
        
        # Call get_decision_reasons with the results
        reasons = get_decision_reasons(evaluation_results)
        
        # Assert that a list with all reasons is returned
        expected_reasons = [
            DECISION_REASON_CODES['CREDIT_SCORE'],
            DECISION_REASON_CODES['DEBT_TO_INCOME'],
            DECISION_REASON_CODES['EMPLOYMENT_HISTORY']
        ]
        self.assertEqual(set(reasons), set(expected_reasons))
    
    def test_duplicate_reasons(self):
        """Test extraction with duplicate reasons in results"""
        # Create evaluation results with duplicate reason fields
        evaluation_results = {
            'credit_score': {'status': 'denied', 'score': 0.0, 
                             'reason': DECISION_REASON_CODES['CREDIT_SCORE']},
            'credit_tier': {'status': 'denied', 'score': 0.0, 
                            'reason': DECISION_REASON_CODES['CREDIT_SCORE']},
            'employment_history': {'status': 'denied', 'score': 0.0, 
                                  'reason': DECISION_REASON_CODES['EMPLOYMENT_HISTORY']}
        }
        
        # Call get_decision_reasons with the results
        reasons = get_decision_reasons(evaluation_results)
        
        # Assert that a list with unique reasons is returned
        expected_reasons = [
            DECISION_REASON_CODES['CREDIT_SCORE'],
            DECISION_REASON_CODES['EMPLOYMENT_HISTORY']
        ]
        self.assertEqual(set(reasons), set(expected_reasons))


class TestApplicationEvaluation(unittest.TestCase):
    """Test cases for the main application evaluation function"""
    
    def setUp(self):
        """Set up test fixtures for application evaluation tests"""
        super().setUp()
        
        # Create mock LoanApplication
        self.application = unittest.mock.Mock(spec=LoanApplication)
        
        # Create mock LoanDetails
        self.loan_details = unittest.mock.Mock(spec=LoanDetails)
        self.application.get_loan_details.return_value = self.loan_details
        
        # Create mock BorrowerProfile
        self.borrower_profile = unittest.mock.Mock(spec=BorrowerProfile)
        self.application.borrower = unittest.mock.Mock()
        self.application.borrower.get_profile.return_value = self.borrower_profile
        
        # Create mock CreditInformation
        self.credit_info = unittest.mock.Mock(spec=CreditInformation)
        
        # Set up relationships between mocks
        self.application.program = unittest.mock.Mock(spec=Program)
        self.application.program.status = 'active'
        
        # Set up BorrowerProfile with EmploymentInfo
        self.employment_info = unittest.mock.Mock()
        self.borrower_profile.employment_info = unittest.mock.Mock()
        self.borrower_profile.employment_info.first.return_value = self.employment_info
        self.employment_info.get_total_employment_duration.return_value = 36  # 3 years
        self.employment_info.get_monthly_income.return_value = Decimal('5000')  # $5000/month
        self.employment_info.annual_income = Decimal('60000')  # $60,000/year
        
        # Set up borrower profile details
        self.borrower_profile.citizenship_status = CITIZENSHIP_STATUS['US_CITIZEN']
        self.borrower_profile.housing_payment = Decimal('1500')  # $1500/month
        
        # Set up loan details
        self.loan_details.requested_amount = Decimal('20000')  # $20,000 loan
        
        # Set up credit info
        self.credit_info.credit_score = 720  # Good credit score
        self.credit_info.debt_to_income_ratio = Decimal('0.35')  # 35% DTI
    
    def test_automatic_approval(self):
        """Test evaluation of application that meets all approval criteria"""
        # Configure mocks with values that meet all approval criteria
        self.credit_info.credit_score = 700  # Above auto approval threshold
        self.credit_info.debt_to_income_ratio = Decimal('0.35')  # Below auto approval threshold
        self.employment_info.get_total_employment_duration.return_value = 36  # 3 years, above threshold
        
        # Call evaluate_application with the application and credit info
        result = evaluate_application(self.application, self.credit_info)
        
        # Assert that the result decision is UNDERWRITING_DECISION['APPROVE']
        self.assertEqual(result['decision'], UNDERWRITING_DECISION['APPROVE'])
        # Assert that the result contains no denial reasons
        self.assertEqual(result['reasons'], [])
    
    def test_automatic_denial_credit_score(self):
        """Test evaluation of application with poor credit score"""
        # Configure mocks with poor credit score below denial threshold
        self.credit_info.credit_score = 550  # Below auto denial threshold
        
        # Call evaluate_application with the application and credit info
        result = evaluate_application(self.application, self.credit_info)
        
        # Assert that the result decision is UNDERWRITING_DECISION['DENY']
        self.assertEqual(result['decision'], UNDERWRITING_DECISION['DENY'])
        # Assert that the result contains DECISION_REASON_CODES['CREDIT_SCORE'] in reasons
        self.assertIn(DECISION_REASON_CODES['CREDIT_SCORE'], result['reasons'])
    
    def test_automatic_denial_dti(self):
        """Test evaluation of application with high DTI ratio"""
        # Configure mocks with high DTI ratio above denial threshold
        self.credit_info.debt_to_income_ratio = Decimal('0.60')  # Above auto denial threshold
        
        # Call evaluate_application with the application and credit info
        result = evaluate_application(self.application, self.credit_info)
        
        # Assert that the result decision is UNDERWRITING_DECISION['DENY']
        self.assertEqual(result['decision'], UNDERWRITING_DECISION['DENY'])
        # Assert that the result contains DECISION_REASON_CODES['DEBT_TO_INCOME'] in reasons
        self.assertIn(DECISION_REASON_CODES['DEBT_TO_INCOME'], result['reasons'])
    
    def test_automatic_denial_employment(self):
        """Test evaluation of application with insufficient employment history"""
        # Configure mocks with employment duration below minimum threshold
        self.employment_info.get_total_employment_duration.return_value = 2  # 2 months, below minimum
        
        # Call evaluate_application with the application and credit info
        result = evaluate_application(self.application, self.credit_info)
        
        # Assert that the result decision is UNDERWRITING_DECISION['DENY']
        self.assertEqual(result['decision'], UNDERWRITING_DECISION['DENY'])
        # Assert that the result contains DECISION_REASON_CODES['EMPLOYMENT_HISTORY'] in reasons
        self.assertIn(DECISION_REASON_CODES['EMPLOYMENT_HISTORY'], result['reasons'])
    
    def test_automatic_denial_housing_ratio(self):
        """Test evaluation of application with high housing payment ratio"""
        # Configure mocks with housing ratio above denial threshold
        self.borrower_profile.housing_payment = Decimal('2500')  # $2500/month
        self.employment_info.get_monthly_income.return_value = Decimal('5000')  # $5000/month
        # Housing ratio becomes 50%, above the denial threshold
        
        # Call evaluate_application with the application and credit info
        result = evaluate_application(self.application, self.credit_info)
        
        # Assert that the result decision is UNDERWRITING_DECISION['DENY']
        self.assertEqual(result['decision'], UNDERWRITING_DECISION['DENY'])
        # Assert that the result contains DECISION_REASON_CODES['HOUSING_PAYMENT'] in reasons
        self.assertIn(DECISION_REASON_CODES['HOUSING_PAYMENT'], result['reasons'])
    
    def test_automatic_denial_income_insufficient(self):
        """Test evaluation of application with insufficient income for loan amount"""
        # Configure mocks with income below required ratio to loan amount
        self.employment_info.annual_income = Decimal('30000')  # $30,000/year
        self.loan_details.requested_amount = Decimal('20000')  # $20,000 loan
        # Income-to-loan ratio is 1.5, below MINIMUM_INCOME_TO_LOAN_RATIO (2.0)
        
        # Call evaluate_application with the application and credit info
        result = evaluate_application(self.application, self.credit_info)
        
        # Assert that the result decision is UNDERWRITING_DECISION['DENY']
        self.assertEqual(result['decision'], UNDERWRITING_DECISION['DENY'])
        # Assert that the result contains DECISION_REASON_CODES['INCOME_INSUFFICIENT'] in reasons
        self.assertIn(DECISION_REASON_CODES['INCOME_INSUFFICIENT'], result['reasons'])
    
    def test_automatic_denial_citizenship(self):
        """Test evaluation of application with ineligible citizenship status"""
        # Configure mocks with ineligible citizenship status
        self.borrower_profile.citizenship_status = CITIZENSHIP_STATUS['INELIGIBLE_NON_CITIZEN']
        
        # Call evaluate_application with the application and credit info
        result = evaluate_application(self.application, self.credit_info)
        
        # Assert that the result decision is UNDERWRITING_DECISION['DENY']
        self.assertEqual(result['decision'], UNDERWRITING_DECISION['DENY'])
        # Assert that the result contains DECISION_REASON_CODES['CITIZENSHIP_STATUS'] in reasons
        self.assertIn(DECISION_REASON_CODES['CITIZENSHIP_STATUS'], result['reasons'])
    
    def test_automatic_denial_program(self):
        """Test evaluation of application with ineligible program"""
        # Configure mocks with inactive program
        self.application.program.status = 'inactive'
        
        # Call evaluate_application with the application and credit info
        result = evaluate_application(self.application, self.credit_info)
        
        # Assert that the result decision is UNDERWRITING_DECISION['DENY']
        self.assertEqual(result['decision'], UNDERWRITING_DECISION['DENY'])
        # Assert that the result contains DECISION_REASON_CODES['PROGRAM_ELIGIBILITY'] in reasons
        self.assertIn(DECISION_REASON_CODES['PROGRAM_ELIGIBILITY'], result['reasons'])
    
    def test_consideration_high_score(self):
        """Test evaluation of application with borderline factors but high weighted score"""
        # Configure mocks with borderline factors but overall good profile
        self.credit_info.credit_score = 650  # Borderline credit score
        self.credit_info.debt_to_income_ratio = Decimal('0.45')  # Borderline DTI
        self.employment_info.get_total_employment_duration.return_value = 18  # 18 months, borderline
        
        # Call evaluate_application with the application and credit info
        result = evaluate_application(self.application, self.credit_info)
        
        # Assert that the result decision is UNDERWRITING_DECISION['APPROVE']
        self.assertEqual(result['decision'], UNDERWRITING_DECISION['APPROVE'])
        # Assert that the result contains appropriate stipulations
        self.assertTrue(len(result['stipulations']) > 0)
    
    def test_consideration_low_score(self):
        """Test evaluation of application with borderline factors and low weighted score"""
        # Configure mocks with borderline factors and overall poor profile
        self.credit_info.credit_score = 600  # Low end of borderline
        self.credit_info.debt_to_income_ratio = Decimal('0.48')  # High end of borderline
        self.employment_info.get_total_employment_duration.return_value = 6  # 6 months, borderline
        
        # Call evaluate_application with the application and credit info
        result = evaluate_application(self.application, self.credit_info)
        
        # Assert that the result decision is UNDERWRITING_DECISION['DENY']
        self.assertEqual(result['decision'], UNDERWRITING_DECISION['DENY'])
        # Assert that the result contains appropriate reasons
        self.assertTrue(len(result['reasons']) > 0)
    
    def test_consideration_medium_score(self):
        """Test evaluation of application with borderline factors and medium weighted score"""
        # Configure mocks with borderline factors and mixed profile
        self.credit_info.credit_score = 640  # Middle of borderline
        self.credit_info.debt_to_income_ratio = Decimal('0.45')  # Middle of borderline
        self.employment_info.get_total_employment_duration.return_value = 15  # 15 months, middle of borderline
        
        # Call evaluate_application with the application and credit info
        result = evaluate_application(self.application, self.credit_info)
        
        # Assert that the result decision is UNDERWRITING_DECISION['REVISE']
        self.assertEqual(result['decision'], UNDERWRITING_DECISION['REVISE'])
        # Assert that the result contains appropriate stipulations
        self.assertTrue(len(result['stipulations']) > 0)


class TestUnderwritingRuleEngine(unittest.TestCase):
    """Test cases for the UnderwritingRuleEngine class"""
    
    def setUp(self):
        """Set up test fixtures for rule engine tests"""
        super().setUp()
        
        # Create mock LoanApplication
        self.application = unittest.mock.Mock(spec=LoanApplication)
        
        # Create mock LoanDetails
        self.loan_details = unittest.mock.Mock(spec=LoanDetails)
        self.application.get_loan_details.return_value = self.loan_details
        
        # Create mock BorrowerProfile
        self.borrower_profile = unittest.mock.Mock(spec=BorrowerProfile)
        self.application.borrower = unittest.mock.Mock()
        self.application.borrower.get_profile.return_value = self.borrower_profile
        
        # Create mock CreditInformation
        self.credit_info = unittest.mock.Mock(spec=CreditInformation)
        
        # Set up relationships between mocks
        self.application.program = unittest.mock.Mock(spec=Program)
        self.application.program.status = 'active'
        
        # Set up BorrowerProfile with EmploymentInfo
        self.employment_info = unittest.mock.Mock()
        self.borrower_profile.employment_info = unittest.mock.Mock()
        self.borrower_profile.employment_info.first.return_value = self.employment_info
        self.employment_info.get_total_employment_duration.return_value = 36  # 3 years
        self.employment_info.get_monthly_income.return_value = Decimal('5000')  # $5000/month
        self.employment_info.annual_income = Decimal('60000')  # $60,000/year
        
        # Set up borrower profile details
        self.borrower_profile.citizenship_status = CITIZENSHIP_STATUS['US_CITIZEN']
        self.borrower_profile.housing_payment = Decimal('1500')  # $1500/month
        
        # Set up loan details
        self.loan_details.requested_amount = Decimal('20000')  # $20,000 loan
        
        # Set up credit info
        self.credit_info.credit_score = 720  # Good credit score
        self.credit_info.debt_to_income_ratio = Decimal('0.35')  # 35% DTI
        
        # Create UnderwritingRuleEngine instance
        self.rule_engine = UnderwritingRuleEngine()
    
    def test_evaluate_application(self):
        """Test the evaluate_application method of the rule engine"""
        # Configure mocks with appropriate values
        self.credit_info.credit_score = 700  # Good credit score
        
        # Call rule_engine.evaluate_application with the application and credit info
        result = self.rule_engine.evaluate_application(self.application, self.credit_info)
        
        # Assert that the result contains expected decision, reasons, and stipulations
        self.assertIn('decision', result)
        self.assertIn('reasons', result)
        self.assertIn('stipulations', result)
        self.assertIn('score', result)
    
    def test_get_auto_decision_approval(self):
        """Test the get_auto_decision method with application that qualifies for auto-approval"""
        # Configure mocks with values that meet all auto-approval criteria
        self.credit_info.credit_score = 700  # Above auto approval threshold
        self.credit_info.debt_to_income_ratio = Decimal('0.35')  # Below auto approval threshold
        self.employment_info.get_total_employment_duration.return_value = 36  # 3 years, above threshold
        
        # Call rule_engine.get_auto_decision with the application and credit info
        result = self.rule_engine.get_auto_decision(self.application, self.credit_info)
        
        # Assert that the result decision is UNDERWRITING_DECISION['APPROVE']
        self.assertEqual(result['decision'], UNDERWRITING_DECISION['APPROVE'])
    
    def test_get_auto_decision_denial(self):
        """Test the get_auto_decision method with application that qualifies for auto-denial"""
        # Configure mocks with values that trigger auto-denial criteria
        self.credit_info.credit_score = 550  # Below auto denial threshold
        
        # Call rule_engine.get_auto_decision with the application and credit info
        result = self.rule_engine.get_auto_decision(self.application, self.credit_info)
        
        # Assert that the result decision is UNDERWRITING_DECISION['DENY']
        self.assertEqual(result['decision'], UNDERWRITING_DECISION['DENY'])
        # Assert that the result contains appropriate reasons
        self.assertTrue(len(result['reasons']) > 0)
    
    def test_get_auto_decision_manual_review(self):
        """Test the get_auto_decision method with application that requires manual review"""
        # Configure mocks with borderline values
        self.credit_info.credit_score = 630  # Between auto approval and auto denial
        self.credit_info.debt_to_income_ratio = Decimal('0.45')  # Between thresholds
        
        # Call rule_engine.get_auto_decision with the application and credit info
        result = self.rule_engine.get_auto_decision(self.application, self.credit_info)
        
        # Assert that the result is None, indicating manual review needed
        self.assertIsNone(result)
    
    def test_calculate_risk_score(self):
        """Test the calculate_risk_score method of the rule engine"""
        # Configure mocks with various risk profiles
        self.credit_info.credit_score = 650  # Moderate credit score
        self.credit_info.debt_to_income_ratio = Decimal('0.42')  # Moderate DTI
        
        # Call rule_engine.calculate_risk_score with the application and credit info
        risk_score = self.rule_engine.calculate_risk_score(self.application, self.credit_info)
        
        # Assert that the risk score is between 0 and 100
        self.assertTrue(0 <= risk_score <= 100)
        
        # Save the current risk score
        moderate_risk_score = risk_score
        
        # Test with better profile
        self.credit_info.credit_score = 750  # Better credit score
        self.credit_info.debt_to_income_ratio = Decimal('0.30')  # Better DTI
        better_risk_score = self.rule_engine.calculate_risk_score(self.application, self.credit_info)
        
        # Test with worse profile
        self.credit_info.credit_score = 580  # Worse credit score
        self.credit_info.debt_to_income_ratio = Decimal('0.52')  # Worse DTI
        worse_risk_score = self.rule_engine.calculate_risk_score(self.application, self.credit_info)
        
        # Assert that better profile has higher score than moderate profile
        self.assertTrue(better_risk_score > moderate_risk_score)
        # Assert that worse profile has lower score than moderate profile
        self.assertTrue(worse_risk_score < moderate_risk_score)