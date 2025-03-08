import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal
from uuid import uuid4

from ..services import (
    create_funding_request,
    verify_enrollment,
    check_stipulations,
    verify_stipulation,
    reject_stipulation,
    waive_stipulation,
    approve_funding,
    schedule_disbursement,
    process_disbursement,
    cancel_funding_request,
    add_funding_note,
    get_pending_enrollment_verifications,
    get_pending_stipulations,
    get_ready_for_approval,
    get_approved_requests,
    get_scheduled_disbursements,
    get_disbursed_requests,
    get_disbursements_by_date_range,
    get_next_disbursement_date,
    is_eligible_for_funding,
    FundingService,
    DisbursementService
)
from ..models import FundingRequest, Disbursement, EnrollmentVerification, StipulationVerification, FundingNote
from ..constants import (
    FUNDING_REQUEST_STATUS,
    DISBURSEMENT_METHOD,
    DISBURSEMENT_STATUS,
    ENROLLMENT_VERIFICATION_TYPE,
    FUNDING_NOTE_TYPE,
    MINIMUM_DAYS_BEFORE_DISBURSEMENT,
    DISBURSEMENT_SCHEDULE_DAYS
)
from ...applications.models import LoanApplication
from ...qc.models import QCReview
from ...underwriting.models import Stipulation
from ...documents.models import DocumentPackage
from ...notifications.services import NotificationService
from ...notifications.constants import EVENT_TYPE


@pytest.mark.django_db
def test_create_funding_request(mock_application, mock_user, mock_qc_review):
    """Tests the creation of a funding request for an application that has passed QC review"""
    # Arrange
    mock_qc_review.is_complete.return_value = True
    mock_application.qc_review = mock_qc_review
    mock_application.get_loan_details.return_value.requested_amount = Decimal('10000.00')
    mock_funding_request = MagicMock()
    FundingRequest.objects.create = MagicMock(return_value=mock_funding_request)

    # Act
    funding_request = create_funding_request(mock_application, mock_user)

    # Assert
    FundingRequest.objects.create.assert_called_once_with(
        application=mock_application,
        requested_amount=Decimal('10000.00'),
        requested_by=mock_user
    )
    assert funding_request == mock_funding_request


@pytest.mark.django_db
def test_create_funding_request_no_qc_review(mock_application, mock_user):
    """Tests that funding request creation fails when QC review is not complete"""
    # Arrange
    mock_application.qc_review = None
    FundingRequest.objects.create = MagicMock()

    # Act
    funding_request = create_funding_request(mock_application, mock_user)

    # Assert
    assert funding_request is None
    FundingRequest.objects.create.assert_not_called()


@pytest.mark.django_db
def test_create_funding_request_incomplete_qc(mock_application, mock_user, mock_qc_review):
    """Tests that funding request creation fails when QC review is not complete"""
    # Arrange
    mock_qc_review.is_complete.return_value = False
    mock_application.qc_review = mock_qc_review
    FundingRequest.objects.create = MagicMock()

    # Act
    funding_request = create_funding_request(mock_application, mock_user)

    # Assert
    assert funding_request is None
    FundingRequest.objects.create.assert_not_called()


@pytest.mark.django_db
def test_verify_enrollment(mock_funding_request, mock_user):
    """Tests the enrollment verification process for a funding request"""
    # Arrange
    mock_funding_request.verify_enrollment = MagicMock(return_value=True)
    verification_type = ENROLLMENT_VERIFICATION_TYPE['ENROLLMENT_AGREEMENT']
    start_date = timezone.now().date()
    comments = "Enrollment verified"
    document_id = uuid4()

    # Act
    result = verify_enrollment(mock_funding_request, mock_user, verification_type, start_date, comments, document_id)

    # Assert
    mock_funding_request.verify_enrollment.assert_called_once_with(
        verification_type=verification_type,
        verified_by=mock_user,
        start_date=start_date,
        comments=comments,
        document_id=document_id
    )
    assert result is True


@pytest.mark.django_db
def test_verify_enrollment_invalid_type(mock_funding_request, mock_user):
    """Tests that enrollment verification fails with an invalid verification type"""
    # Arrange
    invalid_verification_type = "invalid_type"
    start_date = timezone.now().date()
    comments = "Enrollment verified"
    document_id = uuid4()

    # Act
    result = verify_enrollment(mock_funding_request, mock_user, invalid_verification_type, start_date, comments, document_id)

    # Assert
    assert result is False


@pytest.mark.django_db
def test_check_stipulations(mock_funding_request, mock_user):
    """Tests checking if all stipulations for a funding request are satisfied"""
    # Arrange
    mock_funding_request.check_stipulations = MagicMock(return_value=True)

    # Act
    result = check_stipulations(mock_funding_request, mock_user)

    # Assert
    mock_funding_request.check_stipulations.assert_called_once_with(verified_by=mock_user)
    assert result is True


@pytest.mark.django_db
def test_verify_stipulation(mock_funding_request, mock_stipulation, mock_user):
    """Tests verifying a specific stipulation for a funding request"""
    # Arrange
    mock_stipulation_verification = MagicMock()
    StipulationVerification.objects.get = MagicMock(side_effect=StipulationVerification.DoesNotExist)
    StipulationVerification.objects.create = MagicMock(return_value=mock_stipulation_verification)
    mock_stipulation_verification.verify = MagicMock(return_value=True)
    comments = "Stipulation verified"

    # Act
    result = verify_stipulation(mock_funding_request, mock_stipulation, mock_user, comments)

    # Assert
    StipulationVerification.objects.create.assert_called_once_with(
        qc_review=mock_funding_request,
        stipulation=mock_stipulation,
        verified_by=mock_user,
        comments=comments
    )
    mock_stipulation_verification.verify.assert_called_once_with(user=mock_user)
    assert result == mock_stipulation_verification


@pytest.mark.django_db
def test_verify_stipulation_existing(mock_funding_request, mock_stipulation, mock_user, mock_stipulation_verification):
    """Tests verifying a stipulation that already has a verification record"""
    # Arrange
    StipulationVerification.objects.get = MagicMock(return_value=mock_stipulation_verification)
    mock_stipulation_verification.verify = MagicMock(return_value=True)
    comments = "Stipulation verified"

    # Act
    result = verify_stipulation(mock_funding_request, mock_stipulation, mock_user, comments)

    # Assert
    StipulationVerification.objects.create.assert_not_called()
    mock_stipulation_verification.verify.assert_called_once_with(user=mock_user)
    assert result == mock_stipulation_verification


@pytest.mark.django_db
def test_reject_stipulation(mock_funding_request, mock_stipulation, mock_user):
    """Tests rejecting a specific stipulation verification for a funding request"""
    # Arrange
    mock_stipulation_verification = MagicMock()
    StipulationVerification.objects.get = MagicMock(side_effect=StipulationVerification.DoesNotExist)
    StipulationVerification.objects.create = MagicMock(return_value=mock_stipulation_verification)
    mock_stipulation_verification.reject = MagicMock(return_value=True)
    mock_funding_request.update_status = MagicMock()
    comments = "Stipulation rejected"

    # Act
    result = reject_stipulation(mock_funding_request, mock_stipulation, mock_user, comments)

    # Assert
    StipulationVerification.objects.create.assert_called_once_with(
        qc_review=mock_funding_request,
        stipulation=mock_stipulation,
        verified_by=mock_user,
        comments=comments
    )
    mock_stipulation_verification.reject.assert_called_once_with(user=mock_user)
    mock_funding_request.update_status.assert_called_once_with(FUNDING_REQUEST_STATUS['PENDING_STIPULATIONS'])
    assert result == mock_stipulation_verification


@pytest.mark.django_db
def test_waive_stipulation(mock_funding_request, mock_stipulation, mock_user):
    """Tests waiving a specific stipulation for a funding request"""
    # Arrange
    mock_stipulation_verification = MagicMock()
    StipulationVerification.objects.get = MagicMock(side_effect=StipulationVerification.DoesNotExist)
    StipulationVerification.objects.create = MagicMock(return_value=mock_stipulation_verification)
    mock_stipulation_verification.waive = MagicMock(return_value=True)
    mock_funding_request.check_stipulations = MagicMock(return_value=True)
    comments = "Stipulation waived"

    # Act
    result = waive_stipulation(mock_funding_request, mock_stipulation, mock_user, comments)

    # Assert
    StipulationVerification.objects.create.assert_called_once_with(
        qc_review=mock_funding_request,
        stipulation=mock_stipulation,
        verified_by=mock_user,
        comments=comments
    )
    mock_stipulation_verification.waive.assert_called_once_with(user=mock_user)
    mock_funding_request.check_stipulations.assert_called_once()
    assert result == mock_stipulation_verification


@pytest.mark.django_db
def test_approve_funding(mock_funding_request, mock_user):
    """Tests approving a funding request for disbursement"""
    # Arrange
    mock_funding_request.status = FUNDING_REQUEST_STATUS['STIPULATIONS_COMPLETE']
    approved_amount = Decimal('10000.00')
    comments = "Funding approved"
    mock_funding_request.approve = MagicMock(return_value=True)

    # Act
    result = approve_funding(mock_funding_request, mock_user, approved_amount, comments)

    # Assert
    mock_funding_request.approve.assert_called_once_with(approved_by=mock_user, approved_amount=approved_amount, comments=comments)
    assert result is True


@pytest.mark.django_db
def test_approve_funding_invalid_status(mock_funding_request, mock_user):
    """Tests that funding approval fails when the funding request is not in STIPULATIONS_COMPLETE status"""
    # Arrange
    mock_funding_request.status = FUNDING_REQUEST_STATUS['PENDING']
    approved_amount = Decimal('10000.00')
    comments = "Funding approved"
    mock_funding_request.approve = MagicMock()

    # Act
    result = approve_funding(mock_funding_request, mock_user, approved_amount, comments)

    # Assert
    mock_funding_request.approve.assert_not_called()
    assert result is False


@pytest.mark.django_db
def test_schedule_disbursement(mock_funding_request, mock_user):
    """Tests scheduling a disbursement for an approved funding request"""
    # Arrange
    mock_funding_request.status = FUNDING_REQUEST_STATUS['APPROVED']
    disbursement_date = timezone.now().date() + timedelta(days=MINIMUM_DAYS_BEFORE_DISBURSEMENT + 7)
    while disbursement_date.weekday() not in DISBURSEMENT_SCHEDULE_DAYS:
        disbursement_date += timedelta(days=1)
    method = DISBURSEMENT_METHOD['ACH']
    comments = "Disbursement scheduled"
    mock_disbursement = MagicMock()
    mock_funding_request.schedule_disbursement = MagicMock(return_value=mock_disbursement)

    # Act
    result = schedule_disbursement(mock_funding_request, mock_user, disbursement_date, method, comments)

    # Assert
    mock_funding_request.schedule_disbursement.assert_called_once_with(
        scheduled_by=mock_user,
        disbursement_date=disbursement_date,
        method=method,
        comments=comments
    )
    assert result == mock_disbursement


@pytest.mark.django_db
def test_schedule_disbursement_invalid_status(mock_funding_request, mock_user):
    """Tests that disbursement scheduling fails when the funding request is not in APPROVED status"""
    # Arrange
    mock_funding_request.status = FUNDING_REQUEST_STATUS['PENDING']
    disbursement_date = timezone.now().date() + timedelta(days=MINIMUM_DAYS_BEFORE_DISBURSEMENT + 7)
    method = DISBURSEMENT_METHOD['ACH']
    comments = "Disbursement scheduled"
    mock_funding_request.schedule_disbursement = MagicMock()

    # Act
    result = schedule_disbursement(mock_funding_request, mock_user, disbursement_date, method, comments)

    # Assert
    mock_funding_request.schedule_disbursement.assert_not_called()
    assert result is None


@pytest.mark.django_db
def test_schedule_disbursement_invalid_date(mock_funding_request, mock_user):
    """Tests that disbursement scheduling fails when the disbursement date is too soon"""
    # Arrange
    mock_funding_request.status = FUNDING_REQUEST_STATUS['APPROVED']
    disbursement_date = timezone.now().date() + timedelta(days=MINIMUM_DAYS_BEFORE_DISBURSEMENT - 1)
    method = DISBURSEMENT_METHOD['ACH']
    comments = "Disbursement scheduled"
    mock_funding_request.schedule_disbursement = MagicMock()

    # Act
    result = schedule_disbursement(mock_funding_request, mock_user, disbursement_date, method, comments)

    # Assert
    mock_funding_request.schedule_disbursement.assert_not_called()
    assert result is None


@pytest.mark.django_db
def test_schedule_disbursement_invalid_day(mock_funding_request, mock_user):
    """Tests that disbursement scheduling fails when the disbursement date is not on a valid day"""
    # Arrange
    mock_funding_request.status = FUNDING_REQUEST_STATUS['APPROVED']
    disbursement_date = timezone.now().date() + timedelta(days=MINIMUM_DAYS_BEFORE_DISBURSEMENT + 7)
    while disbursement_date.weekday() in DISBURSEMENT_SCHEDULE_DAYS:
        disbursement_date += timedelta(days=1)
    method = DISBURSEMENT_METHOD['ACH']
    comments = "Disbursement scheduled"
    mock_funding_request.schedule_disbursement = MagicMock()

    # Act
    result = schedule_disbursement(mock_funding_request, mock_user, disbursement_date, method, comments)

    # Assert
    mock_funding_request.schedule_disbursement.assert_not_called()
    assert result is None


@pytest.mark.django_db
def test_process_disbursement(mock_funding_request, mock_user):
    """Tests processing a scheduled disbursement"""
    # Arrange
    mock_funding_request.status = FUNDING_REQUEST_STATUS['SCHEDULED_FOR_DISBURSEMENT']
    reference_number = "REF123"
    comments = "Disbursement processed"
    mock_funding_request.process_disbursement = MagicMock(return_value=True)

    # Act
    result = process_disbursement(mock_funding_request, mock_user, reference_number, comments)

    # Assert
    mock_funding_request.process_disbursement.assert_called_once_with(
        processed_by=mock_user,
        reference_number=reference_number,
        comments=comments
    )
    assert result is True


@pytest.mark.django_db
def test_process_disbursement_invalid_status(mock_funding_request, mock_user):
    """Tests that disbursement processing fails when the funding request is not in SCHEDULED_FOR_DISBURSEMENT status"""
    # Arrange
    mock_funding_request.status = FUNDING_REQUEST_STATUS['APPROVED']
    reference_number = "REF123"
    comments = "Disbursement processed"
    mock_funding_request.process_disbursement = MagicMock()

    # Act
    result = process_disbursement(mock_funding_request, mock_user, reference_number, comments)

    # Assert
    mock_funding_request.process_disbursement.assert_not_called()
    assert result is False


@pytest.mark.django_db
def test_cancel_funding_request(mock_funding_request, mock_user):
    """Tests canceling a funding request"""
    # Arrange
    comments = "Funding request cancelled"
    mock_funding_request.cancel = MagicMock(return_value=True)

    # Act
    result = cancel_funding_request(mock_funding_request, mock_user, comments)

    # Assert
    mock_funding_request.cancel.assert_called_once_with(cancelled_by=mock_user, comments=comments)
    assert result is True


@pytest.mark.django_db
def test_add_funding_note(mock_funding_request, mock_user):
    """Tests adding a note to a funding request"""
    # Arrange
    note_text = "Additional information"
    note_type = FUNDING_NOTE_TYPE['GENERAL']
    mock_funding_note = MagicMock()
    FundingNote.objects.create = MagicMock(return_value=mock_funding_note)

    # Act
    result = add_funding_note(mock_funding_request, mock_user, note_text, note_type)

    # Assert
    FundingNote.objects.create.assert_called_once_with(
        funding_request=mock_funding_request,
        note_text=note_text,
        note_type=note_type,
        created_by=mock_user
    )
    assert result == mock_funding_note


@pytest.mark.django_db
def test_add_funding_note_invalid_type(mock_funding_request, mock_user):
    """Tests that adding a funding note fails with an invalid note type"""
    # Arrange
    note_text = "Additional information"
    invalid_note_type = "invalid_type"
    FundingNote.objects.create = MagicMock()

    # Act
    result = add_funding_note(mock_funding_request, mock_user, note_text, invalid_note_type)

    # Assert
    FundingNote.objects.create.assert_not_called()
    assert result is None


@pytest.mark.django_db
def test_get_pending_enrollment_verifications():
    """Tests getting all funding requests pending enrollment verification"""
    # Arrange
    mock_queryset = MagicMock()
    FundingRequest.objects.get_pending_enrollment = MagicMock(return_value=mock_queryset)

    # Act
    result = get_pending_enrollment_verifications()

    # Assert
    FundingRequest.objects.get_pending_enrollment.assert_called_once()
    assert result == mock_queryset


@pytest.mark.django_db
def test_get_pending_stipulations():
    """Tests getting all funding requests pending stipulation completion"""
    # Arrange
    mock_queryset = MagicMock()
    FundingRequest.objects.get_pending_stipulations = MagicMock(return_value=mock_queryset)

    # Act
    result = get_pending_stipulations()

    # Assert
    FundingRequest.objects.get_pending_stipulations.assert_called_once()
    assert result == mock_queryset


@pytest.mark.django_db
def test_get_ready_for_approval():
    """Tests getting all funding requests ready for approval"""
    # Arrange
    mock_queryset = MagicMock()
    FundingRequest.objects.get_ready_for_approval = MagicMock(return_value=mock_queryset)

    # Act
    result = get_ready_for_approval()

    # Assert
    FundingRequest.objects.get_ready_for_approval.assert_called_once()
    assert result == mock_queryset


@pytest.mark.django_db
def test_get_approved_requests():
    """Tests getting all approved funding requests"""
    # Arrange
    mock_queryset = MagicMock()
    FundingRequest.objects.get_approved = MagicMock(return_value=mock_queryset)

    # Act
    result = get_approved_requests()

    # Assert
    FundingRequest.objects.get_approved.assert_called_once()
    assert result == mock_queryset


@pytest.mark.django_db
def test_get_scheduled_disbursements():
    """Tests getting all funding requests with scheduled disbursements"""
    # Arrange
    mock_queryset = MagicMock()
    FundingRequest.objects.get_scheduled_for_disbursement = MagicMock(return_value=mock_queryset)

    # Act
    result = get_scheduled_disbursements()

    # Assert
    FundingRequest.objects.get_scheduled_for_disbursement.assert_called_once()
    assert result == mock_queryset


@pytest.mark.django_db
def test_get_disbursed_requests():
    """Tests getting all funding requests that have been disbursed"""
    # Arrange
    mock_queryset = MagicMock()
    FundingRequest.objects.get_disbursed = MagicMock(return_value=mock_queryset)

    # Act
    result = get_disbursed_requests()

    # Assert
    FundingRequest.objects.get_disbursed.assert_called_once()
    assert result == mock_queryset


@pytest.mark.django_db
def test_get_disbursements_by_date_range():
    """Tests getting disbursements within a specified date range"""
    # Arrange
    start_date = timezone.now().date() - timedelta(days=30)
    end_date = timezone.now().date()
    mock_queryset = MagicMock()
    Disbursement.objects.filter = MagicMock(return_value=mock_queryset)

    # Act
    result = get_disbursements_by_date_range(start_date, end_date)

    # Assert
    Disbursement.objects.filter.assert_called_once_with(
        disbursement_date__gte=start_date,
        disbursement_date__lte=end_date
    )
    assert result == mock_queryset


def test_get_next_disbursement_date():
    """Tests calculating the next valid disbursement date from a given date"""
    # Arrange
    from_date = timezone.now().date()
    expected_date = from_date + timedelta(days=MINIMUM_DAYS_BEFORE_DISBURSEMENT)
    while expected_date.weekday() not in DISBURSEMENT_SCHEDULE_DAYS:
        expected_date += timedelta(days=1)

    # Act
    next_date = get_next_disbursement_date(from_date)

    # Assert
    assert next_date >= from_date + timedelta(days=MINIMUM_DAYS_BEFORE_DISBURSEMENT)
    assert next_date.weekday() in DISBURSEMENT_SCHEDULE_DAYS


@pytest.mark.django_db
def test_is_eligible_for_funding(mock_application, mock_qc_review, mock_document_package):
    """Tests checking if an application is eligible for funding"""
    # Arrange
    mock_qc_review.is_complete.return_value = True
    mock_document_package.is_complete.return_value = True
    QCReview.objects.get = MagicMock(return_value=mock_qc_review)
    DocumentPackage.objects.filter = MagicMock(return_value=[mock_document_package])

    # Act
    result = is_eligible_for_funding(mock_application)

    # Assert
    QCReview.objects.get.assert_called_once_with(application=mock_application)
    DocumentPackage.objects.filter.assert_called_once_with(application=mock_application)
    assert result is True


@pytest.mark.django_db
def test_is_eligible_for_funding_no_qc_review(mock_application):
    """Tests that an application is not eligible for funding without a QC review"""
    # Arrange
    QCReview.objects.get = MagicMock(side_effect=QCReview.DoesNotExist)

    # Act
    result = is_eligible_for_funding(mock_application)

    # Assert
    assert result is False


@pytest.mark.django_db
def test_is_eligible_for_funding_incomplete_qc(mock_application, mock_qc_review):
    """Tests that an application is not eligible for funding with an incomplete QC review"""
    # Arrange
    mock_qc_review.is_complete.return_value = False
    QCReview.objects.get = MagicMock(return_value=mock_qc_review)

    # Act
    result = is_eligible_for_funding(mock_application)

    # Assert
    assert result is False


@pytest.mark.django_db
def test_is_eligible_for_funding_incomplete_documents(mock_application, mock_qc_review, mock_document_package):
    """Tests that an application is not eligible for funding with incomplete document packages"""
    # Arrange
    mock_qc_review.is_complete.return_value = True
    mock_document_package.is_complete.return_value = False
    QCReview.objects.get = MagicMock(return_value=mock_qc_review)
    DocumentPackage.objects.filter = MagicMock(return_value=[mock_document_package])

    # Act
    result = is_eligible_for_funding(mock_application)

    # Assert
    assert result is False


@pytest.mark.django_db
def test_funding_service_create_funding_request(mock_application, mock_user):
    """Tests the FundingService class create_funding_request method"""
    # Arrange
    mock_funding_request = MagicMock()
    create_funding_request = MagicMock(return_value=mock_funding_request)

    # Act
    funding_service = FundingService()
    funding_service.create_funding_request = create_funding_request
    result = funding_service.create_funding_request(mock_application, mock_user)

    # Assert
    create_funding_request.assert_called_once_with(mock_application, mock_user)
    assert result == mock_funding_request


@pytest.mark.django_db
def test_disbursement_service_schedule_disbursement(mock_funding_request, mock_user):
    """Tests the DisbursementService class schedule_disbursement method"""
    # Arrange
    disbursement_date = timezone.now().date() + timedelta(days=MINIMUM_DAYS_BEFORE_DISBURSEMENT + 7)
    method = DISBURSEMENT_METHOD['ACH']
    comments = "Disbursement scheduled"
    mock_disbursement = MagicMock()
    schedule_disbursement = MagicMock(return_value=mock_disbursement)

    # Act
    disbursement_service = DisbursementService()
    disbursement_service.schedule_disbursement = schedule_disbursement
    result = disbursement_service.schedule_disbursement(mock_funding_request, mock_user, disbursement_date, method, comments)

    # Assert
    schedule_disbursement.assert_called_once_with(mock_funding_request, mock_user, disbursement_date, method, comments)
    assert result == mock_disbursement


@pytest.mark.django_db
def test_disbursement_service_get_disbursement_schedule():
    """Tests the DisbursementService class get_disbursement_schedule method"""
    # Arrange
    start_date = timezone.now().date() - timedelta(days=30)
    end_date = timezone.now().date()
    mock_disbursement1 = MagicMock(disbursement_date=start_date)
    mock_disbursement2 = MagicMock(disbursement_date=end_date)
    mock_disbursements = [mock_disbursement1, mock_disbursement2]
    get_disbursements_by_date_range = MagicMock(return_value=mock_disbursements)

    # Act
    disbursement_service = DisbursementService()
    disbursement_service.get_disbursements_by_date_range = get_disbursements_by_date_range
    result = disbursement_service.get_disbursement_schedule(start_date, end_date)

    # Assert
    get_disbursements_by_date_range.assert_called_once_with(start_date, end_date)
    assert isinstance(result, dict)
    assert start_date in result
    assert end_date in result
    assert len(result[start_date]) == 1
    assert len(result[end_date]) == 1
    assert result[start_date][0] == mock_disbursement1
    assert result[end_date][0] == mock_disbursement2


@pytest.mark.django_db
def test_disbursement_service_cancel_disbursement(mock_disbursement, mock_user):
    """Tests the DisbursementService class cancel_disbursement method"""
    # Arrange
    mock_disbursement.cancel = MagicMock(return_value=True)

    # Act
    disbursement_service = DisbursementService()
    result = disbursement_service.cancel_disbursement(mock_disbursement, mock_user)

    # Assert
    mock_disbursement.cancel.assert_called_once_with(cancelled_by=mock_user)
    assert result is True