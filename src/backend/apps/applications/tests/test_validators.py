import unittest
from unittest import mock
from datetime import datetime, date, timedelta
from decimal import Decimal

from ...utils.validators import ValidationError
from ..validators import (
    validate_application_editable,
    validate_application_submission,
    validate_borrower_info,
    validate_co_borrower_info,
    validate_employment_info,
    validate_loan_details,
    validate_required_documents,
    validate_citizenship_eligibility,
    validate_borrower_age,
    validate_missing_fields
)
from ..constants import (
    APPLICATION_EDITABLE_STATUSES,
    REQUIRED_BORROWER_FIELDS,
    REQUIRED_EMPLOYMENT_FIELDS,
    REQUIRED_LOAN_FIELDS,
    DOCUMENT_REQUIREMENTS,
    MINIMUM_EMPLOYMENT_MONTHS
)
from ...utils.constants import (
    CITIZENSHIP_STATUS,
    MINIMUM_AGE,
    MINIMUM_INCOME,
    MINIMUM_LOAN_AMOUNT,
    MAXIMUM_LOAN_AMOUNT
)


class TestValidateApplicationEditable(unittest.TestCase):
    def test_application_editable(self):
        """Test that applications with editable statuses pass validation"""
        for status in APPLICATION_EDITABLE_STATUSES:
            mock_application = mock.Mock()
            mock_application.status = status
            
            self.assertTrue(validate_application_editable(mock_application))
    
    def test_application_not_editable(self):
        """Test that applications with non-editable statuses fail validation"""
        non_editable_statuses = ["submitted", "approved", "funded", "denied"]
        
        for status in non_editable_statuses:
            mock_application = mock.Mock()
            mock_application.status = status
            
            with self.assertRaises(ValidationError):
                validate_application_editable(mock_application)


class TestValidateBorrowerInfo(unittest.TestCase):
    def setUp(self):
        """Set up test data before each test"""
        # Create a valid borrower profile
        self.valid_borrower = mock.Mock()
        
        # Set attributes with valid values
        self.valid_borrower.first_name = "John"
        self.valid_borrower.last_name = "Doe"
        self.valid_borrower.email = "john.doe@example.com"
        self.valid_borrower.phone = "(555) 123-4567"
        self.valid_borrower.ssn = "123-45-6789"
        self.valid_borrower.dob = date(1990, 1, 1)  # 33 years old (if current year is 2023)
        self.valid_borrower.citizenship_status = CITIZENSHIP_STATUS["US_CITIZEN"]
        self.valid_borrower.address_line1 = "123 Main St"
        self.valid_borrower.city = "Anytown"
        self.valid_borrower.state = "CA"
        self.valid_borrower.zip_code = "12345"
        self.valid_borrower.housing_status = "OWN"
        self.valid_borrower.housing_payment = Decimal("1000.00")
    
    def test_valid_borrower_info(self):
        """Test that valid borrower information passes validation"""
        self.assertTrue(validate_borrower_info(self.valid_borrower))
    
    def test_missing_required_fields(self):
        """Test that missing required fields fail validation"""
        for field in REQUIRED_BORROWER_FIELDS:
            # Create a copy of the valid borrower
            invalid_borrower = mock.Mock()
            # Copy all attributes from valid_borrower
            for attr in REQUIRED_BORROWER_FIELDS:
                if attr != field:  # Skip the field we want to test as missing
                    setattr(invalid_borrower, attr, getattr(self.valid_borrower, attr))
            
            # Set the field we're testing to None
            setattr(invalid_borrower, field, None)
            
            # Test validation
            with self.assertRaises(ValidationError):
                validate_borrower_info(invalid_borrower)
    
    def test_invalid_email(self):
        """Test that invalid email format fails validation"""
        invalid_borrower = mock.Mock()
        # Copy all attributes from valid_borrower
        for attr in REQUIRED_BORROWER_FIELDS:
            setattr(invalid_borrower, attr, getattr(self.valid_borrower, attr))
        
        # Set invalid email
        invalid_borrower.email = "invalid-email"
        
        with self.assertRaises(ValidationError):
            validate_borrower_info(invalid_borrower)
    
    def test_invalid_phone(self):
        """Test that invalid phone format fails validation"""
        invalid_borrower = mock.Mock()
        # Copy all attributes from valid_borrower
        for attr in REQUIRED_BORROWER_FIELDS:
            setattr(invalid_borrower, attr, getattr(self.valid_borrower, attr))
        
        # Set invalid phone
        invalid_borrower.phone = "555-123-4567"  # Missing parentheses
        
        with self.assertRaises(ValidationError):
            validate_borrower_info(invalid_borrower)
    
    def test_invalid_ssn(self):
        """Test that invalid SSN format fails validation"""
        invalid_borrower = mock.Mock()
        # Copy all attributes from valid_borrower
        for attr in REQUIRED_BORROWER_FIELDS:
            setattr(invalid_borrower, attr, getattr(self.valid_borrower, attr))
        
        # Set invalid SSN
        invalid_borrower.ssn = "12345-6789"  # Incorrect format
        
        with self.assertRaises(ValidationError):
            validate_borrower_info(invalid_borrower)
    
    def test_invalid_zip_code(self):
        """Test that invalid ZIP code format fails validation"""
        invalid_borrower = mock.Mock()
        # Copy all attributes from valid_borrower
        for attr in REQUIRED_BORROWER_FIELDS:
            setattr(invalid_borrower, attr, getattr(self.valid_borrower, attr))
        
        # Set invalid ZIP code
        invalid_borrower.zip_code = "1234"  # Too short
        
        with self.assertRaises(ValidationError):
            validate_borrower_info(invalid_borrower)
    
    def test_invalid_state_code(self):
        """Test that invalid state code fails validation"""
        invalid_borrower = mock.Mock()
        # Copy all attributes from valid_borrower
        for attr in REQUIRED_BORROWER_FIELDS:
            setattr(invalid_borrower, attr, getattr(self.valid_borrower, attr))
        
        # Set invalid state code
        invalid_borrower.state = "XX"  # Non-existent state
        
        with self.assertRaises(ValidationError):
            validate_borrower_info(invalid_borrower)
    
    def test_ineligible_citizenship(self):
        """Test that ineligible citizenship status fails validation"""
        invalid_borrower = mock.Mock()
        # Copy all attributes from valid_borrower
        for attr in REQUIRED_BORROWER_FIELDS:
            setattr(invalid_borrower, attr, getattr(self.valid_borrower, attr))
        
        # Set ineligible citizenship status
        invalid_borrower.citizenship_status = CITIZENSHIP_STATUS["INELIGIBLE_NON_CITIZEN"]
        
        with self.assertRaises(ValidationError):
            validate_borrower_info(invalid_borrower)
    
    def test_underage_borrower(self):
        """Test that underage borrower fails validation"""
        invalid_borrower = mock.Mock()
        # Copy all attributes from valid_borrower
        for attr in REQUIRED_BORROWER_FIELDS:
            setattr(invalid_borrower, attr, getattr(self.valid_borrower, attr))
        
        # Set underage DOB (today - 17 years)
        today = date.today()
        underage_dob = date(today.year - 17, today.month, today.day)
        invalid_borrower.dob = underage_dob
        
        with self.assertRaises(ValidationError):
            validate_borrower_info(invalid_borrower)
    
    def test_negative_housing_payment(self):
        """Test that negative housing payment fails validation"""
        invalid_borrower = mock.Mock()
        # Copy all attributes from valid_borrower
        for attr in REQUIRED_BORROWER_FIELDS:
            setattr(invalid_borrower, attr, getattr(self.valid_borrower, attr))
        
        # Set negative housing payment
        invalid_borrower.housing_payment = Decimal("-1000.00")
        
        with self.assertRaises(ValidationError):
            validate_borrower_info(invalid_borrower)


class TestValidateCoBorrowerInfo(unittest.TestCase):
    def setUp(self):
        """Set up test data before each test"""
        # Create a valid co-borrower profile
        self.valid_co_borrower = mock.Mock()
        
        # Set attributes with valid values (same as borrower)
        self.valid_co_borrower.first_name = "Jane"
        self.valid_co_borrower.last_name = "Doe"
        self.valid_co_borrower.email = "jane.doe@example.com"
        self.valid_co_borrower.phone = "(555) 987-6543"
        self.valid_co_borrower.ssn = "987-65-4321"
        self.valid_co_borrower.dob = date(1992, 2, 2)  # 31 years old (if current year is 2023)
        self.valid_co_borrower.citizenship_status = CITIZENSHIP_STATUS["US_CITIZEN"]
        self.valid_co_borrower.address_line1 = "123 Main St"
        self.valid_co_borrower.city = "Anytown"
        self.valid_co_borrower.state = "CA"
        self.valid_co_borrower.zip_code = "12345"
        self.valid_co_borrower.housing_status = "OWN"
        self.valid_co_borrower.housing_payment = Decimal("1000.00")
    
    def test_valid_co_borrower_info(self):
        """Test that valid co-borrower information passes validation"""
        self.assertTrue(validate_co_borrower_info(self.valid_co_borrower))
    
    def test_none_co_borrower(self):
        """Test that None co-borrower passes validation (co-borrower is optional)"""
        self.assertTrue(validate_co_borrower_info(None))
    
    def test_missing_required_fields(self):
        """Test that missing required fields fail validation"""
        for field in REQUIRED_BORROWER_FIELDS:
            # Create a copy of the valid co-borrower
            invalid_co_borrower = mock.Mock()
            # Copy all attributes from valid_co_borrower
            for attr in REQUIRED_BORROWER_FIELDS:
                if attr != field:  # Skip the field we want to test as missing
                    setattr(invalid_co_borrower, attr, getattr(self.valid_co_borrower, attr))
            
            # Set the field we're testing to None
            setattr(invalid_co_borrower, field, None)
            
            # Test validation
            with self.assertRaises(ValidationError):
                validate_co_borrower_info(invalid_co_borrower)
    
    def test_invalid_fields(self):
        """Test that invalid field values fail validation"""
        # Test various invalid field scenarios
        test_cases = [
            ('email', 'invalid-email'),
            ('phone', '555-123-4567'),  # Missing parentheses
            ('ssn', '12345-6789'),  # Incorrect format
            ('zip_code', '1234'),  # Too short
            ('state', 'XX'),  # Non-existent state
            ('citizenship_status', CITIZENSHIP_STATUS["INELIGIBLE_NON_CITIZEN"]),
            ('housing_payment', Decimal("-1000.00"))  # Negative payment
        ]
        
        for field, invalid_value in test_cases:
            invalid_co_borrower = mock.Mock()
            # Copy all attributes from valid_co_borrower
            for attr in REQUIRED_BORROWER_FIELDS:
                setattr(invalid_co_borrower, attr, getattr(self.valid_co_borrower, attr))
            
            # Set the invalid field value
            setattr(invalid_co_borrower, field, invalid_value)
            
            # Test validation
            with self.assertRaises(ValidationError):
                validate_co_borrower_info(invalid_co_borrower)


class TestValidateEmploymentInfo(unittest.TestCase):
    def setUp(self):
        """Set up test data before each test"""
        # Create a valid employment info
        self.valid_employment = mock.Mock()
        
        # Set attributes with valid values
        self.valid_employment.employment_type = "FULL_TIME"
        self.valid_employment.employer_name = "ACME Corporation"
        self.valid_employment.occupation = "Software Developer"
        self.valid_employment.years_employed = 2
        self.valid_employment.months_employed = 6  # 30 months total > MINIMUM_EMPLOYMENT_MONTHS
        self.valid_employment.annual_income = Decimal("75000.00")  # > MINIMUM_INCOME
    
    def test_valid_employment_info(self):
        """Test that valid employment information passes validation"""
        self.assertTrue(validate_employment_info(self.valid_employment))
    
    def test_missing_required_fields(self):
        """Test that missing required fields fail validation"""
        for field in REQUIRED_EMPLOYMENT_FIELDS:
            # Create a copy of the valid employment info
            invalid_employment = mock.Mock()
            # Copy all attributes from valid_employment
            for attr in REQUIRED_EMPLOYMENT_FIELDS:
                if attr != field:  # Skip the field we want to test as missing
                    setattr(invalid_employment, attr, getattr(self.valid_employment, attr))
            
            # Set the field we're testing to None
            setattr(invalid_employment, field, None)
            
            # Test validation
            with self.assertRaises(ValidationError):
                validate_employment_info(invalid_employment)
    
    def test_insufficient_employment_duration(self):
        """Test that employment duration below minimum fails validation"""
        invalid_employment = mock.Mock()
        # Copy all attributes from valid_employment
        for attr in REQUIRED_EMPLOYMENT_FIELDS:
            setattr(invalid_employment, attr, getattr(self.valid_employment, attr))
        
        # Set insufficient employment duration
        invalid_employment.years_employed = 0
        invalid_employment.months_employed = MINIMUM_EMPLOYMENT_MONTHS - 1
        
        with self.assertRaises(ValidationError):
            validate_employment_info(invalid_employment)
    
    def test_insufficient_income(self):
        """Test that income below minimum fails validation"""
        invalid_employment = mock.Mock()
        # Copy all attributes from valid_employment
        for attr in REQUIRED_EMPLOYMENT_FIELDS:
            setattr(invalid_employment, attr, getattr(self.valid_employment, attr))
        
        # Set insufficient income
        invalid_employment.annual_income = MINIMUM_INCOME - Decimal("0.01")
        
        with self.assertRaises(ValidationError):
            validate_employment_info(invalid_employment)
    
    def test_negative_income(self):
        """Test that negative income fails validation"""
        invalid_employment = mock.Mock()
        # Copy all attributes from valid_employment
        for attr in REQUIRED_EMPLOYMENT_FIELDS:
            setattr(invalid_employment, attr, getattr(self.valid_employment, attr))
        
        # Set negative income
        invalid_employment.annual_income = Decimal("-1.00")
        
        with self.assertRaises(ValidationError):
            validate_employment_info(invalid_employment)


class TestValidateLoanDetails(unittest.TestCase):
    def setUp(self):
        """Set up test data before each test"""
        # Create a valid loan details object
        self.valid_loan_details = mock.Mock()
        
        # Set attributes with valid values
        self.valid_loan_details.school_id = "school-123"
        self.valid_loan_details.program_id = "program-456"
        self.valid_loan_details.tuition_amount = Decimal("10000.00")
        self.valid_loan_details.deposit_amount = Decimal("1000.00")
        self.valid_loan_details.other_funding = Decimal("500.00")
        self.valid_loan_details.requested_amount = Decimal("8500.00")  # Tuition - deposit - other_funding
        
        # Set future dates
        tomorrow = date.today() + timedelta(days=1)
        future = tomorrow + timedelta(days=90)
        self.valid_loan_details.start_date = tomorrow
        self.valid_loan_details.completion_date = future
    
    def test_valid_loan_details(self):
        """Test that valid loan details pass validation"""
        self.assertTrue(validate_loan_details(self.valid_loan_details))
    
    def test_missing_required_fields(self):
        """Test that missing required fields fail validation"""
        for field in REQUIRED_LOAN_FIELDS:
            # Create a copy of the valid loan details
            invalid_loan_details = mock.Mock()
            # Copy all attributes from valid_loan_details
            for attr in REQUIRED_LOAN_FIELDS:
                if attr != field:  # Skip the field we want to test as missing
                    setattr(invalid_loan_details, attr, getattr(self.valid_loan_details, attr))
            
            # Set non-required fields
            invalid_loan_details.deposit_amount = self.valid_loan_details.deposit_amount
            invalid_loan_details.other_funding = self.valid_loan_details.other_funding
            invalid_loan_details.completion_date = self.valid_loan_details.completion_date
            
            # Set the field we're testing to None
            setattr(invalid_loan_details, field, None)
            
            # Test validation
            with self.assertRaises(ValidationError):
                validate_loan_details(invalid_loan_details)
    
    def test_negative_tuition(self):
        """Test that negative tuition amount fails validation"""
        invalid_loan_details = mock.Mock()
        # Copy all attributes from valid_loan_details
        for attr in REQUIRED_LOAN_FIELDS:
            setattr(invalid_loan_details, attr, getattr(self.valid_loan_details, attr))
        
        # Copy non-required fields
        invalid_loan_details.deposit_amount = self.valid_loan_details.deposit_amount
        invalid_loan_details.other_funding = self.valid_loan_details.other_funding
        invalid_loan_details.completion_date = self.valid_loan_details.completion_date
        
        # Set negative tuition
        invalid_loan_details.tuition_amount = Decimal("-1.00")
        
        with self.assertRaises(ValidationError):
            validate_loan_details(invalid_loan_details)
    
    def test_negative_deposit(self):
        """Test that negative deposit amount fails validation"""
        invalid_loan_details = mock.Mock()
        # Copy all attributes from valid_loan_details
        for attr in REQUIRED_LOAN_FIELDS:
            setattr(invalid_loan_details, attr, getattr(self.valid_loan_details, attr))
        
        # Copy non-required fields
        invalid_loan_details.completion_date = self.valid_loan_details.completion_date
        invalid_loan_details.other_funding = self.valid_loan_details.other_funding
        
        # Set negative deposit
        invalid_loan_details.deposit_amount = Decimal("-1.00")
        
        with self.assertRaises(ValidationError):
            validate_loan_details(invalid_loan_details)
    
    def test_negative_other_funding(self):
        """Test that negative other funding amount fails validation"""
        invalid_loan_details = mock.Mock()
        # Copy all attributes from valid_loan_details
        for attr in REQUIRED_LOAN_FIELDS:
            setattr(invalid_loan_details, attr, getattr(self.valid_loan_details, attr))
        
        # Copy non-required fields
        invalid_loan_details.deposit_amount = self.valid_loan_details.deposit_amount
        invalid_loan_details.completion_date = self.valid_loan_details.completion_date
        
        # Set negative other funding
        invalid_loan_details.other_funding = Decimal("-1.00")
        
        with self.assertRaises(ValidationError):
            validate_loan_details(invalid_loan_details)
    
    def test_loan_amount_below_minimum(self):
        """Test that loan amount below minimum fails validation"""
        invalid_loan_details = mock.Mock()
        # Copy all attributes from valid_loan_details
        for attr in REQUIRED_LOAN_FIELDS:
            setattr(invalid_loan_details, attr, getattr(self.valid_loan_details, attr))
        
        # Copy non-required fields
        invalid_loan_details.deposit_amount = self.valid_loan_details.deposit_amount
        invalid_loan_details.other_funding = self.valid_loan_details.other_funding
        invalid_loan_details.completion_date = self.valid_loan_details.completion_date
        
        # Set loan amount below minimum
        invalid_loan_details.requested_amount = MINIMUM_LOAN_AMOUNT - Decimal("0.01")
        
        with self.assertRaises(ValidationError):
            validate_loan_details(invalid_loan_details)
    
    def test_loan_amount_above_maximum(self):
        """Test that loan amount above maximum fails validation"""
        invalid_loan_details = mock.Mock()
        # Copy all attributes from valid_loan_details
        for attr in REQUIRED_LOAN_FIELDS:
            setattr(invalid_loan_details, attr, getattr(self.valid_loan_details, attr))
        
        # Copy non-required fields
        invalid_loan_details.deposit_amount = self.valid_loan_details.deposit_amount
        invalid_loan_details.other_funding = self.valid_loan_details.other_funding
        invalid_loan_details.completion_date = self.valid_loan_details.completion_date
        
        # Set loan amount above maximum
        invalid_loan_details.requested_amount = MAXIMUM_LOAN_AMOUNT + Decimal("0.01")
        
        with self.assertRaises(ValidationError):
            validate_loan_details(invalid_loan_details)
    
    def test_loan_exceeds_available_tuition(self):
        """Test that loan amount exceeding available tuition fails validation"""
        invalid_loan_details = mock.Mock()
        # Copy all attributes from valid_loan_details
        for attr in REQUIRED_LOAN_FIELDS:
            setattr(invalid_loan_details, attr, getattr(self.valid_loan_details, attr))
        
        # Copy non-required fields
        invalid_loan_details.deposit_amount = self.valid_loan_details.deposit_amount
        invalid_loan_details.other_funding = self.valid_loan_details.other_funding
        invalid_loan_details.completion_date = self.valid_loan_details.completion_date
        
        # Set loan amount to exceed available tuition
        available = invalid_loan_details.tuition_amount - invalid_loan_details.deposit_amount - invalid_loan_details.other_funding
        invalid_loan_details.requested_amount = available + Decimal("0.01")
        
        with self.assertRaises(ValidationError):
            validate_loan_details(invalid_loan_details)
    
    def test_past_start_date(self):
        """Test that past start date fails validation"""
        invalid_loan_details = mock.Mock()
        # Copy all attributes from valid_loan_details
        for attr in REQUIRED_LOAN_FIELDS:
            setattr(invalid_loan_details, attr, getattr(self.valid_loan_details, attr))
        
        # Copy non-required fields
        invalid_loan_details.deposit_amount = self.valid_loan_details.deposit_amount
        invalid_loan_details.other_funding = self.valid_loan_details.other_funding
        invalid_loan_details.completion_date = self.valid_loan_details.completion_date
        
        # Set start date to yesterday
        yesterday = date.today() - timedelta(days=1)
        invalid_loan_details.start_date = yesterday
        
        with self.assertRaises(ValidationError):
            validate_loan_details(invalid_loan_details)
    
    def test_completion_date_before_start_date(self):
        """Test that completion date before start date fails validation"""
        invalid_loan_details = mock.Mock()
        # Copy all attributes from valid_loan_details
        for attr in REQUIRED_LOAN_FIELDS:
            setattr(invalid_loan_details, attr, getattr(self.valid_loan_details, attr))
        
        # Copy non-required fields
        invalid_loan_details.deposit_amount = self.valid_loan_details.deposit_amount
        invalid_loan_details.other_funding = self.valid_loan_details.other_funding
        
        # Set completion date before start date
        tomorrow = date.today() + timedelta(days=1)
        day_after_tomorrow = tomorrow + timedelta(days=1)
        
        invalid_loan_details.start_date = day_after_tomorrow
        invalid_loan_details.completion_date = tomorrow
        
        with self.assertRaises(ValidationError):
            validate_loan_details(invalid_loan_details)


class TestValidateRequiredDocuments(unittest.TestCase):
    def setUp(self):
        """Set up test data before each test"""
        # Create a mock application with document collection
        self.application = mock.Mock()
        
        # Create documents for each required document type
        self.documents = []
        for doc_type, config in DOCUMENT_REQUIREMENTS.items():
            if config['required']:
                document = mock.Mock()
                document.document_type = doc_type
                self.documents.append(document)
        
        self.application.documents = self.documents
    
    def test_all_required_documents_present(self):
        """Test that application with all required documents passes validation"""
        self.assertTrue(validate_required_documents(self.application))
    
    def test_missing_required_documents(self):
        """Test that missing required documents fail validation"""
        for doc_type, config in DOCUMENT_REQUIREMENTS.items():
            if config['required']:
                # Create a copy of documents without this required document
                filtered_documents = [doc for doc in self.documents if doc.document_type != doc_type]
                
                # Create a new application with filtered documents
                application_missing_doc = mock.Mock()
                application_missing_doc.documents = filtered_documents
                
                # Test validation
                with self.assertRaises(ValidationError):
                    validate_required_documents(application_missing_doc)
    
    def test_optional_documents_not_required(self):
        """Test that missing optional documents pass validation"""
        # Only include required documents
        required_documents = [doc for doc in self.documents]
        
        # Create a new application with only required documents
        application_with_required = mock.Mock()
        application_with_required.documents = required_documents
        
        # Test validation
        self.assertTrue(validate_required_documents(application_with_required))


class TestValidateCitizenshipEligibility(unittest.TestCase):
    def test_eligible_citizenship_statuses(self):
        """Test that eligible citizenship statuses pass validation"""
        eligible_statuses = [
            CITIZENSHIP_STATUS["US_CITIZEN"],
            CITIZENSHIP_STATUS["PERMANENT_RESIDENT"],
            CITIZENSHIP_STATUS["ELIGIBLE_NON_CITIZEN"]
        ]
        
        for status in eligible_statuses:
            self.assertTrue(validate_citizenship_eligibility(status))
    
    def test_ineligible_citizenship_status(self):
        """Test that ineligible citizenship status fails validation"""
        with self.assertRaises(ValidationError):
            validate_citizenship_eligibility(CITIZENSHIP_STATUS["INELIGIBLE_NON_CITIZEN"])
    
    def test_invalid_citizenship_status(self):
        """Test that invalid citizenship status fails validation"""
        with self.assertRaises(ValidationError):
            validate_citizenship_eligibility("INVALID_STATUS")


class TestValidateBorrowerAge(unittest.TestCase):
    def test_borrower_meets_minimum_age(self):
        """Test that borrower meeting minimum age passes validation"""
        today = date.today()
        exactly_minimum_age = date(today.year - MINIMUM_AGE, today.month, today.day)
        
        self.assertTrue(validate_borrower_age(exactly_minimum_age))
    
    def test_borrower_above_minimum_age(self):
        """Test that borrower above minimum age passes validation"""
        today = date.today()
        above_minimum_age = date(today.year - MINIMUM_AGE - 1, today.month, today.day)
        
        self.assertTrue(validate_borrower_age(above_minimum_age))
    
    def test_borrower_below_minimum_age(self):
        """Test that borrower below minimum age fails validation"""
        today = date.today()
        below_minimum_age = date(today.year - MINIMUM_AGE + 1, today.month, today.day)
        
        with self.assertRaises(ValidationError):
            validate_borrower_age(below_minimum_age)


class TestValidateMissingFields(unittest.TestCase):
    def test_no_missing_fields(self):
        """Test that data with all required fields returns empty list"""
        required_fields = ["field1", "field2", "field3"]
        data = {"field1": "value1", "field2": "value2", "field3": "value3"}
        
        missing_fields = validate_missing_fields(data, required_fields)
        self.assertEqual(missing_fields, [])
    
    def test_missing_fields(self):
        """Test that data with missing fields returns list of missing fields"""
        required_fields = ["field1", "field2", "field3"]
        data = {"field1": "value1"}  # field2 and field3 are missing
        
        missing_fields = validate_missing_fields(data, required_fields)
        self.assertEqual(set(missing_fields), {"field2", "field3"})
    
    def test_empty_fields(self):
        """Test that data with empty fields returns list of empty fields"""
        required_fields = ["field1", "field2", "field3"]
        data = {"field1": "value1", "field2": "", "field3": "value3"}
        
        missing_fields = validate_missing_fields(data, required_fields)
        self.assertEqual(missing_fields, ["field2"])
    
    def test_none_fields(self):
        """Test that data with None fields returns list of None fields"""
        required_fields = ["field1", "field2", "field3"]
        data = {"field1": "value1", "field2": None, "field3": "value3"}
        
        missing_fields = validate_missing_fields(data, required_fields)
        self.assertEqual(missing_fields, ["field2"])


class TestValidateApplicationSubmission(unittest.TestCase):
    def setUp(self):
        """Set up test data before each test"""
        # Create mock application in editable state
        self.application = mock.Mock()
        self.application.status = APPLICATION_EDITABLE_STATUSES[0]
        
        # Create valid borrower profile
        self.borrower_profile = mock.Mock()
        
        # Create valid employment info
        self.employment_info = mock.Mock()
        self.borrower_profile.employment_info = self.employment_info
        
        # Create valid loan details
        self.loan_details = mock.Mock()
        
        # Mock validate_* functions to isolate tests
        self.patcher1 = mock.patch('src.backend.apps.applications.validators.validate_application_editable', return_value=True)
        self.patcher2 = mock.patch('src.backend.apps.applications.validators.validate_borrower_info', return_value=True)
        self.patcher3 = mock.patch('src.backend.apps.applications.validators.validate_employment_info', return_value=True)
        self.patcher4 = mock.patch('src.backend.apps.applications.validators.validate_loan_details', return_value=True)
        self.patcher5 = mock.patch('src.backend.apps.applications.validators.validate_co_borrower_info', return_value=True)
        self.patcher6 = mock.patch('src.backend.apps.applications.validators.validate_required_documents', return_value=True)
        
        self.mock_editable = self.patcher1.start()
        self.mock_borrower = self.patcher2.start()
        self.mock_employment = self.patcher3.start()
        self.mock_loan = self.patcher4.start()
        self.mock_co_borrower = self.patcher5.start()
        self.mock_documents = self.patcher6.start()
    
    def tearDown(self):
        """Clean up patches"""
        self.patcher1.stop()
        self.patcher2.stop()
        self.patcher3.stop()
        self.patcher4.stop()
        self.patcher5.stop()
        self.patcher6.stop()
    
    def test_valid_application_submission(self):
        """Test that valid application submission passes validation"""
        self.assertTrue(validate_application_submission(self.application, self.borrower_profile, self.loan_details))
    
    def test_application_not_editable(self):
        """Test that non-editable application fails validation"""
        self.mock_editable.side_effect = ValidationError("Application not editable")
        
        with self.assertRaises(ValidationError):
            validate_application_submission(self.application, self.borrower_profile, self.loan_details)
    
    def test_invalid_borrower_info(self):
        """Test that invalid borrower info fails validation"""
        self.mock_borrower.side_effect = ValidationError("Invalid borrower info")
        
        with self.assertRaises(ValidationError):
            validate_application_submission(self.application, self.borrower_profile, self.loan_details)
    
    def test_invalid_employment_info(self):
        """Test that invalid employment info fails validation"""
        self.mock_employment.side_effect = ValidationError("Invalid employment info")
        
        with self.assertRaises(ValidationError):
            validate_application_submission(self.application, self.borrower_profile, self.loan_details)
    
    def test_invalid_loan_details(self):
        """Test that invalid loan details fails validation"""
        self.mock_loan.side_effect = ValidationError("Invalid loan details")
        
        with self.assertRaises(ValidationError):
            validate_application_submission(self.application, self.borrower_profile, self.loan_details)
    
    def test_invalid_co_borrower_info(self):
        """Test that invalid co-borrower info fails validation"""
        # Set application to have co-borrower
        self.application.co_borrower_profile = mock.Mock()
        self.mock_co_borrower.side_effect = ValidationError("Invalid co-borrower info")
        
        with self.assertRaises(ValidationError):
            validate_application_submission(self.application, self.borrower_profile, self.loan_details)
    
    def test_missing_required_documents(self):
        """Test that missing required documents fails validation"""
        self.mock_documents.side_effect = ValidationError("Missing required documents")
        
        with self.assertRaises(ValidationError):
            validate_application_submission(self.application, self.borrower_profile, self.loan_details)