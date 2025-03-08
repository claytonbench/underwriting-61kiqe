"""
Provides validation functions specific to loan applications, ensuring data integrity
and compliance with business rules throughout the application lifecycle.

This module includes validations for application state transitions, required fields,
financial data, and document requirements.
"""

from datetime import datetime, date
from decimal import Decimal

from ...utils.validators import (
    ValidationError, validate_email, validate_phone, validate_ssn,
    validate_zip_code, validate_state_code, validate_date, validate_future_date,
    validate_positive_number, validate_non_negative_number, validate_loan_amount,
    validate_in_choices
)

from .constants import (
    APPLICATION_EDITABLE_STATUSES, APPLICATION_SUBMISSION_FIELDS_VALIDATION,
    REQUIRED_BORROWER_FIELDS, REQUIRED_EMPLOYMENT_FIELDS, REQUIRED_LOAN_FIELDS,
    DOCUMENT_REQUIREMENTS, MINIMUM_EMPLOYMENT_MONTHS, ERROR_MESSAGES
)

from ...utils.constants import (
    CITIZENSHIP_STATUS, MINIMUM_AGE, MINIMUM_INCOME, DATE_FORMAT
)


def validate_application_editable(application):
    """
    Validates that an application is in an editable state.
    
    Args:
        application: The application object to validate.
        
    Returns:
        True if application is editable, raises ValidationError otherwise.
    """
    if application.status not in APPLICATION_EDITABLE_STATUSES:
        raise ValidationError(ERROR_MESSAGES["APPLICATION_NOT_EDITABLE"])
    return True


def validate_application_submission(application, borrower_profile, loan_details):
    """
    Validates that an application has all required fields for submission.
    
    Args:
        application: The application object to validate.
        borrower_profile: The borrower profile object to validate.
        loan_details: The loan details object to validate.
        
    Returns:
        True if application is valid for submission, raises ValidationError otherwise.
    """
    # Validate application is in an editable state
    validate_application_editable(application)
    
    # Validate borrower information
    validate_borrower_info(borrower_profile)
    
    # Validate employment information if available
    if hasattr(borrower_profile, 'employment_info'):
        validate_employment_info(borrower_profile.employment_info)
    
    # Validate loan details
    validate_loan_details(loan_details)
    
    # Validate co-borrower information if present
    if hasattr(application, 'co_borrower_profile') and application.co_borrower_profile:
        validate_co_borrower_info(application.co_borrower_profile)
    
    # Validate required documents
    validate_required_documents(application)
    
    return True


def validate_borrower_info(borrower_profile):
    """
    Validates borrower personal information.
    
    Args:
        borrower_profile: The borrower profile object to validate.
        
    Returns:
        True if borrower information is valid, raises ValidationError otherwise.
    """
    # Check for missing required fields
    missing_fields = validate_missing_fields(borrower_profile.__dict__, REQUIRED_BORROWER_FIELDS)
    if missing_fields:
        raise ValidationError(ERROR_MESSAGES["MISSING_REQUIRED_FIELDS"].format(
            fields=", ".join(missing_fields)
        ))
    
    # Validate email format
    validate_email(borrower_profile.email)
    
    # Validate phone format
    validate_phone(borrower_profile.phone)
    
    # Validate SSN format
    validate_ssn(borrower_profile.ssn)
    
    # Validate address fields
    validate_zip_code(borrower_profile.zip_code)
    validate_state_code(borrower_profile.state)
    
    # Validate citizenship eligibility
    validate_citizenship_eligibility(borrower_profile.citizenship_status)
    
    # Validate borrower age
    if isinstance(borrower_profile.dob, str):
        dob = datetime.strptime(borrower_profile.dob, DATE_FORMAT).date()
    else:
        dob = borrower_profile.dob
    validate_borrower_age(dob)
    
    # Validate housing payment is a non-negative number
    validate_non_negative_number(borrower_profile.housing_payment)
    
    return True


def validate_co_borrower_info(co_borrower_profile):
    """
    Validates co-borrower personal information if present.
    
    Args:
        co_borrower_profile: The co-borrower profile object to validate.
        
    Returns:
        True if co-borrower information is valid or None, raises ValidationError otherwise.
    """
    if co_borrower_profile is None:
        return True
    
    # Check for missing required fields
    missing_fields = validate_missing_fields(co_borrower_profile.__dict__, REQUIRED_BORROWER_FIELDS)
    if missing_fields:
        raise ValidationError(ERROR_MESSAGES["MISSING_REQUIRED_FIELDS"].format(
            fields=", ".join(missing_fields)
        ))
    
    # Validate email format
    validate_email(co_borrower_profile.email)
    
    # Validate phone format
    validate_phone(co_borrower_profile.phone)
    
    # Validate SSN format
    validate_ssn(co_borrower_profile.ssn)
    
    # Validate address fields
    validate_zip_code(co_borrower_profile.zip_code)
    validate_state_code(co_borrower_profile.state)
    
    # Validate citizenship eligibility
    validate_citizenship_eligibility(co_borrower_profile.citizenship_status)
    
    # Validate co-borrower age
    if isinstance(co_borrower_profile.dob, str):
        dob = datetime.strptime(co_borrower_profile.dob, DATE_FORMAT).date()
    else:
        dob = co_borrower_profile.dob
    validate_borrower_age(dob)
    
    # Validate housing payment is a non-negative number
    validate_non_negative_number(co_borrower_profile.housing_payment)
    
    return True


def validate_employment_info(employment_info):
    """
    Validates borrower employment information.
    
    Args:
        employment_info: The employment information object to validate.
        
    Returns:
        True if employment information is valid, raises ValidationError otherwise.
    """
    # Check for missing required fields
    missing_fields = validate_missing_fields(employment_info.__dict__, REQUIRED_EMPLOYMENT_FIELDS)
    if missing_fields:
        raise ValidationError(ERROR_MESSAGES["MISSING_REQUIRED_FIELDS"].format(
            fields=", ".join(missing_fields)
        ))
    
    # Validate employment duration meets minimum requirement
    total_employment_months = (employment_info.years_employed * 12) + employment_info.months_employed
    if total_employment_months < MINIMUM_EMPLOYMENT_MONTHS:
        raise ValidationError(ERROR_MESSAGES["MINIMUM_EMPLOYMENT_REQUIREMENT"].format(
            min_months=MINIMUM_EMPLOYMENT_MONTHS
        ))
    
    # Validate annual income meets minimum requirement
    annual_income = Decimal(str(employment_info.annual_income))
    if annual_income < MINIMUM_INCOME:
        raise ValidationError(ERROR_MESSAGES["MINIMUM_INCOME_REQUIREMENT"].format(
            min_income=MINIMUM_INCOME
        ))
    
    # Validate annual income is a positive number
    validate_positive_number(employment_info.annual_income)
    
    return True


def validate_loan_details(loan_details):
    """
    Validates loan financial details.
    
    Args:
        loan_details: The loan details object to validate.
        
    Returns:
        True if loan details are valid, raises ValidationError otherwise.
    """
    # Check for missing required fields
    missing_fields = validate_missing_fields(loan_details.__dict__, REQUIRED_LOAN_FIELDS)
    if missing_fields:
        raise ValidationError(ERROR_MESSAGES["MISSING_REQUIRED_FIELDS"].format(
            fields=", ".join(missing_fields)
        ))
    
    # Validate tuition amount is a positive number
    validate_positive_number(loan_details.tuition_amount)
    
    # Validate deposit amount is a non-negative number (if present)
    if hasattr(loan_details, 'deposit_amount') and loan_details.deposit_amount is not None:
        validate_non_negative_number(loan_details.deposit_amount)
    else:
        loan_details.deposit_amount = Decimal('0.00')
    
    # Validate other funding is a non-negative number (if present)
    if hasattr(loan_details, 'other_funding') and loan_details.other_funding is not None:
        validate_non_negative_number(loan_details.other_funding)
    else:
        loan_details.other_funding = Decimal('0.00')
    
    # Validate requested loan amount is within allowed range
    validate_loan_amount(loan_details.requested_amount)
    
    # Validate requested amount does not exceed tuition minus deposit and other funding
    available_amount = loan_details.tuition_amount - loan_details.deposit_amount - loan_details.other_funding
    if loan_details.requested_amount > available_amount:
        raise ValidationError(ERROR_MESSAGES["LOAN_EXCEEDS_TUITION"])
    
    # Validate start date is in the future
    if isinstance(loan_details.start_date, str):
        start_date = datetime.strptime(loan_details.start_date, DATE_FORMAT).date()
    else:
        start_date = loan_details.start_date
    validate_future_date(start_date)
    
    # Validate completion date is after start date (if provided)
    if hasattr(loan_details, 'completion_date') and loan_details.completion_date:
        if isinstance(loan_details.completion_date, str):
            completion_date = datetime.strptime(loan_details.completion_date, DATE_FORMAT).date()
        else:
            completion_date = loan_details.completion_date
        
        if completion_date <= start_date:
            raise ValidationError(ERROR_MESSAGES["INVALID_COMPLETION_DATE"])
    
    return True


def validate_required_documents(application):
    """
    Validates that all required documents are uploaded.
    
    Args:
        application: The application object to validate.
        
    Returns:
        True if all required documents are present, raises ValidationError otherwise.
    """
    # Get all documents associated with the application
    documents = getattr(application, 'documents', [])
    document_types = [doc.document_type for doc in documents]
    
    # Check for missing required documents
    missing_documents = []
    for doc_type, config in DOCUMENT_REQUIREMENTS.items():
        if config['required'] and doc_type not in document_types:
            missing_documents.append(config['description'])
    
    if missing_documents:
        raise ValidationError(f"The following required documents are missing: {', '.join(missing_documents)}")
    
    return True


def validate_citizenship_eligibility(citizenship_status):
    """
    Validates that the citizenship status is eligible for a loan.
    
    Args:
        citizenship_status: The citizenship status to validate.
        
    Returns:
        True if citizenship status is eligible, raises ValidationError otherwise.
    """
    eligible_statuses = [
        CITIZENSHIP_STATUS["US_CITIZEN"],
        CITIZENSHIP_STATUS["PERMANENT_RESIDENT"],
        CITIZENSHIP_STATUS["ELIGIBLE_NON_CITIZEN"]
    ]
    
    if citizenship_status not in eligible_statuses:
        raise ValidationError(ERROR_MESSAGES["INVALID_CITIZENSHIP"])
    
    return True


def validate_borrower_age(dob):
    """
    Validates that the borrower meets the minimum age requirement.
    
    Args:
        dob: The date of birth to validate.
        
    Returns:
        True if borrower meets minimum age requirement, raises ValidationError otherwise.
    """
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    
    if age < MINIMUM_AGE:
        raise ValidationError(ERROR_MESSAGES["MINIMUM_AGE_REQUIREMENT"].format(
            min_age=MINIMUM_AGE
        ))
    
    return True


def validate_missing_fields(data, required_fields):
    """
    Validates that all required fields are present in the data.
    
    Args:
        data: The data dictionary to validate.
        required_fields: List of required field names.
        
    Returns:
        List of missing field names, empty list if all fields are present.
    """
    missing_fields = []
    for field in required_fields:
        # Check if field is missing or empty
        if field not in data or data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            missing_fields.append(field)
    
    return missing_fields