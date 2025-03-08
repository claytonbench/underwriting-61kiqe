import unittest
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import patch

from ../../utils.validators import (
    ValidationError, validate_email, validate_phone, validate_ssn, 
    validate_zip_code, validate_state_code, validate_date, 
    validate_future_date, validate_positive_number, validate_non_negative_number,
    validate_loan_amount, validate_password, validate_boolean, 
    validate_in_choices, validate_file_extension, validate_file_size
)
from ../../utils.constants import (
    EMAIL_REGEX, PHONE_REGEX, ZIP_CODE_REGEX, SSN_REGEX, US_STATES,
    MINIMUM_LOAN_AMOUNT, MAXIMUM_LOAN_AMOUNT, PASSWORD_COMPLEXITY_REGEX,
    PASSWORD_MIN_LENGTH, ALLOWED_DOCUMENT_EXTENSIONS, MAX_UPLOAD_SIZE_MB, DATE_FORMAT
)


class TestValidationError(unittest.TestCase):
    """Test case class for testing the ValidationError exception."""
    
    def test_validation_error_creation(self):
        """Test that ValidationError can be created with a message."""
        error_message = "Test validation error"
        error = ValidationError(error_message)
        self.assertEqual(str(error), error_message)
        self.assertTrue(issubclass(ValidationError, Exception))


class TestEmailValidation(unittest.TestCase):
    """Test case class for testing the email validation function."""
    
    def test_valid_email(self):
        """Test that valid email addresses pass validation."""
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.com",
            "user123@example.co.uk",
            "user-name@example.org"
        ]
        for email in valid_emails:
            self.assertTrue(validate_email(email))
    
    def test_invalid_email(self):
        """Test that invalid email addresses fail validation."""
        invalid_emails = [
            "user@",
            "user@.com",
            "@example.com",
            "user@example.",
            "user@ex ample.com",
            "user name@example.com",
            "user@exa mple.com",
            "useñ@example.com"  # Non-ASCII character
        ]
        for email in invalid_emails:
            with self.assertRaises(ValidationError):
                validate_email(email)
    
    def test_none_email(self):
        """Test that None value fails validation."""
        with self.assertRaises(ValidationError):
            validate_email(None)
    
    def test_empty_email(self):
        """Test that empty string fails validation."""
        with self.assertRaises(ValidationError):
            validate_email("")


class TestPhoneValidation(unittest.TestCase):
    """Test case class for testing the phone validation function."""
    
    def test_valid_phone(self):
        """Test that valid phone numbers pass validation."""
        valid_phones = [
            "(123) 456-7890",
            "(555) 123-4567",
            "(800) 555-0100"
        ]
        for phone in valid_phones:
            self.assertTrue(validate_phone(phone))
    
    def test_invalid_phone(self):
        """Test that invalid phone numbers fail validation."""
        invalid_phones = [
            "123-456-7890",  # Missing parentheses
            "(123)456-7890",  # Missing space
            "(123) 4567890",  # Missing hyphen
            "(123) 456-789",  # Too short
            "(123) 456-78901",  # Too long
            "123) 456-7890",  # Missing opening parenthesis
            "(123 456-7890",  # Missing closing parenthesis
            "(abc) def-ghij"  # Non-numeric
        ]
        for phone in invalid_phones:
            with self.assertRaises(ValidationError):
                validate_phone(phone)
    
    def test_none_phone(self):
        """Test that None value fails validation."""
        with self.assertRaises(ValidationError):
            validate_phone(None)
    
    def test_empty_phone(self):
        """Test that empty string fails validation."""
        with self.assertRaises(ValidationError):
            validate_phone("")


class TestSSNValidation(unittest.TestCase):
    """Test case class for testing the SSN validation function."""
    
    def test_valid_ssn(self):
        """Test that valid SSNs pass validation."""
        valid_ssns = [
            "123-45-6789",
            "000-00-0000",
            "999-99-9999"
        ]
        for ssn in valid_ssns:
            self.assertTrue(validate_ssn(ssn))
    
    def test_invalid_ssn(self):
        """Test that invalid SSNs fail validation."""
        invalid_ssns = [
            "123456789",  # Missing hyphens
            "123-456-789",  # Wrong format
            "12-345-6789",  # Wrong format
            "123-45-678",  # Too short
            "123-45-67890",  # Too long
            "12A-45-6789",  # Non-numeric
            "123-4B-6789",  # Non-numeric
            "123-45-678C"  # Non-numeric
        ]
        for ssn in invalid_ssns:
            with self.assertRaises(ValidationError):
                validate_ssn(ssn)
    
    def test_none_ssn(self):
        """Test that None value fails validation."""
        with self.assertRaises(ValidationError):
            validate_ssn(None)
    
    def test_empty_ssn(self):
        """Test that empty string fails validation."""
        with self.assertRaises(ValidationError):
            validate_ssn("")


class TestZipCodeValidation(unittest.TestCase):
    """Test case class for testing the ZIP code validation function."""
    
    def test_valid_zip_code(self):
        """Test that valid ZIP codes pass validation."""
        valid_zip_codes = [
            "12345",  # 5-digit format
            "12345-6789"  # 9-digit format
        ]
        for zip_code in valid_zip_codes:
            self.assertTrue(validate_zip_code(zip_code))
    
    def test_invalid_zip_code(self):
        """Test that invalid ZIP codes fail validation."""
        invalid_zip_codes = [
            "1234",  # Too short
            "123456",  # Too long
            "12345-",  # Incomplete 9-digit format
            "-12345",  # Incorrect format
            "12345-67",  # Incomplete 9-digit format
            "12345-678901",  # Too long
            "abcde",  # Non-numeric
            "123-45",  # Incorrect format
            "12345-abcd"  # Non-numeric extension
        ]
        for zip_code in invalid_zip_codes:
            with self.assertRaises(ValidationError):
                validate_zip_code(zip_code)
    
    def test_none_zip_code(self):
        """Test that None value fails validation."""
        with self.assertRaises(ValidationError):
            validate_zip_code(None)
    
    def test_empty_zip_code(self):
        """Test that empty string fails validation."""
        with self.assertRaises(ValidationError):
            validate_zip_code("")


class TestStateCodeValidation(unittest.TestCase):
    """Test case class for testing the state code validation function."""
    
    def test_valid_state_code(self):
        """Test that valid state codes pass validation."""
        valid_state_codes = list(US_STATES.keys())[:5]  # Test a subset of state codes
        for state_code in valid_state_codes:
            self.assertTrue(validate_state_code(state_code))
    
    def test_case_insensitive(self):
        """Test that state code validation is case-insensitive."""
        lowercase_state_codes = [code.lower() for code in list(US_STATES.keys())[:5]]
        for state_code in lowercase_state_codes:
            self.assertTrue(validate_state_code(state_code))
    
    def test_invalid_state_code(self):
        """Test that invalid state codes fail validation."""
        invalid_state_codes = [
            "XX",  # Not a valid state code
            "ZZ",  # Not a valid state code
            "ABC",  # Too long
            "A",  # Too short
            "123"  # Numeric
        ]
        for state_code in invalid_state_codes:
            with self.assertRaises(ValidationError):
                validate_state_code(state_code)
    
    def test_none_state_code(self):
        """Test that None value fails validation."""
        with self.assertRaises(ValidationError):
            validate_state_code(None)
    
    def test_empty_state_code(self):
        """Test that empty string fails validation."""
        with self.assertRaises(ValidationError):
            validate_state_code("")


class TestDateValidation(unittest.TestCase):
    """Test case class for testing the date validation function."""
    
    def test_valid_date(self):
        """Test that valid date strings pass validation."""
        valid_dates = [
            ("2023-01-01", "%Y-%m-%d", 2023, 1, 1),
            ("01/15/2023", "%m/%d/%Y", 2023, 1, 15),
            ("15-Mar-2023", "%d-%b-%Y", 2023, 3, 15)
        ]
        for date_str, format_str, year, month, day in valid_dates:
            result = validate_date(date_str, format_str)
            self.assertEqual(result.year, year)
            self.assertEqual(result.month, month)
            self.assertEqual(result.day, day)
    
    def test_invalid_date(self):
        """Test that invalid date strings fail validation."""
        invalid_dates = [
            "2023-02-30",  # Invalid day
            "2023-13-01",  # Invalid month
            "2023/01/01",  # Wrong separator for default format
            "01-01-2023",  # Wrong format for default format
            "abc"  # Not a date
        ]
        for date_str in invalid_dates:
            with self.assertRaises(ValidationError):
                validate_date(date_str)
    
    def test_invalid_format(self):
        """Test that date strings with invalid format fail validation."""
        date_str = "01/15/2023"
        wrong_format = "%Y-%m-%d"  # Doesn't match the date string
        with self.assertRaises(ValidationError):
            validate_date(date_str, wrong_format)
    
    def test_none_date(self):
        """Test that None value fails validation."""
        with self.assertRaises(ValidationError):
            validate_date(None)
    
    def test_empty_date(self):
        """Test that empty string fails validation."""
        with self.assertRaises(ValidationError):
            validate_date("")


class TestFutureDateValidation(unittest.TestCase):
    """Test case class for testing the future date validation function."""
    
    def test_future_date(self):
        """Test that future dates pass validation."""
        from datetime import timedelta
        future_date = date.today() + timedelta(days=1)
        self.assertTrue(validate_future_date(future_date))
    
    def test_today_date(self):
        """Test that today's date fails validation."""
        today = date.today()
        with self.assertRaises(ValidationError):
            validate_future_date(today)
    
    def test_past_date(self):
        """Test that past dates fail validation."""
        from datetime import timedelta
        past_date = date.today() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            validate_future_date(past_date)
    
    def test_none_date(self):
        """Test that None value fails validation."""
        with self.assertRaises(ValidationError):
            validate_future_date(None)
    
    @patch('datetime.date')
    def test_with_mocked_today(self, mock_date):
        """Test with a mocked today's date to ensure consistent testing."""
        mock_today = date(2023, 1, 15)
        mock_date.today.return_value = mock_today
        
        # Date before the mocked today should fail
        past_date = date(2023, 1, 14)
        with self.assertRaises(ValidationError):
            validate_future_date(past_date)
        
        # Date after the mocked today should pass
        future_date = date(2023, 1, 16)
        self.assertTrue(validate_future_date(future_date))
        
        # The mocked today date should fail
        with self.assertRaises(ValidationError):
            validate_future_date(mock_today)


class TestPositiveNumberValidation(unittest.TestCase):
    """Test case class for testing the positive number validation function."""
    
    def test_positive_integer(self):
        """Test that positive integers pass validation."""
        positive_integers = [1, 5, 10, 100, 1000]
        for num in positive_integers:
            self.assertTrue(validate_positive_number(num))
    
    def test_positive_float(self):
        """Test that positive floats pass validation."""
        positive_floats = [0.1, 1.5, 10.99, 100.001]
        for num in positive_floats:
            self.assertTrue(validate_positive_number(num))
    
    def test_positive_decimal(self):
        """Test that positive Decimal values pass validation."""
        positive_decimals = [Decimal('0.1'), Decimal('1.5'), Decimal('10.99')]
        for num in positive_decimals:
            self.assertTrue(validate_positive_number(num))
    
    def test_zero(self):
        """Test that zero fails validation."""
        with self.assertRaises(ValidationError):
            validate_positive_number(0)
    
    def test_negative_number(self):
        """Test that negative numbers fail validation."""
        negative_numbers = [-1, -5, -10.5, Decimal('-1.5')]
        for num in negative_numbers:
            with self.assertRaises(ValidationError):
                validate_positive_number(num)
    
    def test_none_value(self):
        """Test that None value fails validation."""
        with self.assertRaises(ValidationError):
            validate_positive_number(None)
    
    def test_non_numeric_value(self):
        """Test that non-numeric values fail validation."""
        non_numeric_values = ["abc", "", "10a", [1, 2, 3], {"key": "value"}]
        for value in non_numeric_values:
            with self.assertRaises(ValidationError):
                validate_positive_number(value)


class TestNonNegativeNumberValidation(unittest.TestCase):
    """Test case class for testing the non-negative number validation function."""
    
    def test_positive_number(self):
        """Test that positive numbers pass validation."""
        positive_numbers = [1, 5, 10.5, Decimal('15.99')]
        for num in positive_numbers:
            self.assertTrue(validate_non_negative_number(num))
    
    def test_zero(self):
        """Test that zero passes validation."""
        self.assertTrue(validate_non_negative_number(0))
    
    def test_negative_number(self):
        """Test that negative numbers fail validation."""
        negative_numbers = [-1, -5, -10.5, Decimal('-1.5')]
        for num in negative_numbers:
            with self.assertRaises(ValidationError):
                validate_non_negative_number(num)
    
    def test_none_value(self):
        """Test that None value fails validation."""
        with self.assertRaises(ValidationError):
            validate_non_negative_number(None)
    
    def test_non_numeric_value(self):
        """Test that non-numeric values fail validation."""
        non_numeric_values = ["abc", "", "10a", [1, 2, 3], {"key": "value"}]
        for value in non_numeric_values:
            with self.assertRaises(ValidationError):
                validate_non_negative_number(value)


class TestLoanAmountValidation(unittest.TestCase):
    """Test case class for testing the loan amount validation function."""
    
    def test_valid_loan_amount(self):
        """Test that valid loan amounts pass validation."""
        valid_amounts = [
            MINIMUM_LOAN_AMOUNT + Decimal('1000'),
            MAXIMUM_LOAN_AMOUNT - Decimal('1000'),
            Decimal('10000'),
            Decimal('25000')
        ]
        for amount in valid_amounts:
            self.assertTrue(validate_loan_amount(amount))
    
    def test_minimum_loan_amount(self):
        """Test that the minimum loan amount passes validation."""
        self.assertTrue(validate_loan_amount(MINIMUM_LOAN_AMOUNT))
    
    def test_maximum_loan_amount(self):
        """Test that the maximum loan amount passes validation."""
        self.assertTrue(validate_loan_amount(MAXIMUM_LOAN_AMOUNT))
    
    def test_below_minimum_loan_amount(self):
        """Test that loan amounts below the minimum fail validation."""
        below_min = MINIMUM_LOAN_AMOUNT - Decimal('0.01')
        with self.assertRaises(ValidationError):
            validate_loan_amount(below_min)
    
    def test_above_maximum_loan_amount(self):
        """Test that loan amounts above the maximum fail validation."""
        above_max = MAXIMUM_LOAN_AMOUNT + Decimal('0.01')
        with self.assertRaises(ValidationError):
            validate_loan_amount(above_max)
    
    def test_none_loan_amount(self):
        """Test that None value fails validation."""
        with self.assertRaises(ValidationError):
            validate_loan_amount(None)
    
    def test_non_numeric_loan_amount(self):
        """Test that non-numeric loan amounts fail validation."""
        non_numeric_values = ["abc", "", "10a", [1, 2, 3], {"key": "value"}]
        for value in non_numeric_values:
            with self.assertRaises(ValidationError):
                validate_loan_amount(value)


class TestPasswordValidation(unittest.TestCase):
    """Test case class for testing the password validation function."""
    
    def test_valid_password(self):
        """Test that valid passwords pass validation."""
        valid_passwords = [
            "Password123!",
            "Secure_Password1",
            "Super$ecureP4ss",
            "ComplexP@ssw0rd",
            "P@ssw0rd_123456"
        ]
        for password in valid_passwords:
            self.assertTrue(validate_password(password))
    
    def test_short_password(self):
        """Test that passwords shorter than minimum length fail validation."""
        short_password = "P@ss1"  # Too short
        with self.assertRaises(ValidationError):
            validate_password(short_password)
    
    def test_password_without_uppercase(self):
        """Test that passwords without uppercase letters fail validation."""
        password = "password123!"  # No uppercase
        with self.assertRaises(ValidationError):
            validate_password(password)
    
    def test_password_without_lowercase(self):
        """Test that passwords without lowercase letters fail validation."""
        password = "PASSWORD123!"  # No lowercase
        with self.assertRaises(ValidationError):
            validate_password(password)
    
    def test_password_without_digit(self):
        """Test that passwords without digits fail validation."""
        password = "PasswordAbc!"  # No digit
        with self.assertRaises(ValidationError):
            validate_password(password)
    
    def test_password_without_special_char(self):
        """Test that passwords without special characters fail validation."""
        password = "Password123"  # No special character
        with self.assertRaises(ValidationError):
            validate_password(password)
    
    def test_none_password(self):
        """Test that None value fails validation."""
        with self.assertRaises(ValidationError):
            validate_password(None)
    
    def test_empty_password(self):
        """Test that empty string fails validation."""
        with self.assertRaises(ValidationError):
            validate_password("")


class TestBooleanValidation(unittest.TestCase):
    """Test case class for testing the boolean validation function."""
    
    def test_boolean_values(self):
        """Test that boolean values pass validation."""
        self.assertTrue(validate_boolean(True))
        self.assertFalse(validate_boolean(False))
    
    def test_string_values(self):
        """Test that string representations of booleans pass validation."""
        true_strings = ["true", "True", "TRUE", "t", "T", "yes", "Yes", "YES", "y", "Y", "1"]
        false_strings = ["false", "False", "FALSE", "f", "F", "no", "No", "NO", "n", "N", "0"]
        
        for value in true_strings:
            self.assertTrue(validate_boolean(value))
        
        for value in false_strings:
            self.assertFalse(validate_boolean(value))
    
    def test_numeric_values(self):
        """Test that numeric values pass validation."""
        self.assertTrue(validate_boolean(1))
        self.assertTrue(validate_boolean(100))
        self.assertFalse(validate_boolean(0))
    
    def test_invalid_values(self):
        """Test that invalid boolean values fail validation."""
        invalid_values = [None, "maybe", "2", [True], {"key": True}]
        for value in invalid_values:
            with self.assertRaises(ValidationError):
                validate_boolean(value)


class TestInChoicesValidation(unittest.TestCase):
    """Test case class for testing the choices validation function."""
    
    def test_value_in_choices(self):
        """Test that values in the choices list pass validation."""
        choices = ["A", "B", "C", 1, 2, 3]
        for value in choices:
            self.assertTrue(validate_in_choices(value, choices))
    
    def test_value_not_in_choices(self):
        """Test that values not in the choices list fail validation."""
        choices = ["A", "B", "C", 1, 2, 3]
        not_in_choices = "D"
        with self.assertRaises(ValidationError):
            validate_in_choices(not_in_choices, choices)
    
    def test_none_value(self):
        """Test that None value fails validation."""
        choices = ["A", "B", "C"]
        with self.assertRaises(ValidationError):
            validate_in_choices(None, choices)
    
    def test_empty_choices(self):
        """Test validation with an empty choices list."""
        choices = []
        value = "A"
        with self.assertRaises(ValidationError):
            validate_in_choices(value, choices)


class TestFileExtensionValidation(unittest.TestCase):
    """Test case class for testing the file extension validation function."""
    
    def test_valid_extensions(self):
        """Test that files with allowed extensions pass validation."""
        valid_filenames = [
            "document.pdf",
            "image.jpg",
            "picture.jpeg",
            "graphic.png"
        ]
        for filename in valid_filenames:
            self.assertTrue(validate_file_extension(filename, ALLOWED_DOCUMENT_EXTENSIONS))
    
    def test_case_insensitive(self):
        """Test that extension validation is case-insensitive."""
        uppercase_filenames = [
            "document.PDF",
            "image.JPG",
            "picture.JPEG",
            "graphic.PNG"
        ]
        for filename in uppercase_filenames:
            self.assertTrue(validate_file_extension(filename, ALLOWED_DOCUMENT_EXTENSIONS))
    
    def test_invalid_extensions(self):
        """Test that files with disallowed extensions fail validation."""
        invalid_filenames = [
            "script.js",
            "data.csv",
            "archive.zip",
            "executable.exe"
        ]
        for filename in invalid_filenames:
            with self.assertRaises(ValidationError):
                validate_file_extension(filename, ALLOWED_DOCUMENT_EXTENSIONS)
    
    def test_no_extension(self):
        """Test that files without extensions fail validation."""
        filename = "noextension"
        with self.assertRaises(ValidationError):
            validate_file_extension(filename, ALLOWED_DOCUMENT_EXTENSIONS)
    
    def test_none_filename(self):
        """Test that None value fails validation."""
        with self.assertRaises(ValidationError):
            validate_file_extension(None, ALLOWED_DOCUMENT_EXTENSIONS)
    
    def test_empty_filename(self):
        """Test that empty string fails validation."""
        with self.assertRaises(ValidationError):
            validate_file_extension("", ALLOWED_DOCUMENT_EXTENSIONS)


class TestFileSizeValidation(unittest.TestCase):
    """Test case class for testing the file size validation function."""
    
    def test_valid_file_size(self):
        """Test that file sizes within the limit pass validation."""
        valid_sizes = [
            1 * 1024 * 1024,  # 1 MB
            5 * 1024 * 1024,  # 5 MB
            MAX_UPLOAD_SIZE_MB * 1024 * 1024 - 1  # Just under the limit
        ]
        for size in valid_sizes:
            self.assertTrue(validate_file_size(size, MAX_UPLOAD_SIZE_MB))
    
    def test_maximum_file_size(self):
        """Test that the maximum file size passes validation."""
        max_size_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024
        self.assertTrue(validate_file_size(max_size_bytes, MAX_UPLOAD_SIZE_MB))
    
    def test_exceeding_file_size(self):
        """Test that file sizes exceeding the limit fail validation."""
        exceeding_size = MAX_UPLOAD_SIZE_MB * 1024 * 1024 + 1  # Just over the limit
        with self.assertRaises(ValidationError):
            validate_file_size(exceeding_size, MAX_UPLOAD_SIZE_MB)
    
    def test_none_file_size(self):
        """Test that None value fails validation."""
        with self.assertRaises(ValidationError):
            validate_file_size(None, MAX_UPLOAD_SIZE_MB)
    
    def test_negative_file_size(self):
        """Test that negative file sizes fail validation."""
        negative_size = -1
        with self.assertRaises(ValidationError):
            validate_file_size(negative_size, MAX_UPLOAD_SIZE_MB)


if __name__ == '__main__':
    unittest.main()