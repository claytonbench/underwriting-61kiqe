"""
Tests for the funding API views.

This module contains test cases for all the API views in the funding module,
covering funding requests, enrollment verification, stipulation verification,
disbursements, and funding notes throughout the loan funding process.
"""

from rest_framework.test import APITestCase  # version 3.14+
from rest_framework import status  # version 3.14+
from django.urls import reverse  # version 4.2+
from django.utils import timezone  # version 4.2+
from unittest.mock import patch, mock  # standard library
from decimal import Decimal  # standard library
import datetime  # standard library
import uuid  # standard library

from ..models import (
    FundingRequest, 
    EnrollmentVerification, 
    StipulationVerification, 
    Disbursement, 
    FundingNote
)
from ..constants import (
    FUNDING_REQUEST_STATUS, 
    DISBURSEMENT_METHOD, 
    ENROLLMENT_VERIFICATION_TYPE,
    VERIFICATION_STATUS,
    FUNDING_NOTE_TYPE
)
from ..services import FundingService, DisbursementService
from apps.applications.models import LoanApplication
from apps.underwriting.models import Stipulation

# Mocked service instances for testing
funding_service_mock = mock.Mock(spec=FundingService)
disbursement_service_mock = mock.Mock(spec=DisbursementService)


class FundingRequestListViewTest(APITestCase):
    """Test case for the FundingRequestListView API view"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test users
        self.borrower_user = User.objects.create(email="borrower@example.com", first_name="Borrower", last_name="User", user_type="borrower")
        self.co_borrower_user = User.objects.create(email="co_borrower@example.com", first_name="Co", last_name="Borrower", user_type="co_borrower")
        self.staff_user = User.objects.create(email="staff@example.com", first_name="Staff", last_name="User", user_type="underwriter")
        
        # Create borrower profiles
        self.borrower_profile = BorrowerProfile.objects.create(
            user=self.borrower_user,
            ssn="123-45-6789",
            dob=timezone.now().date() - datetime.timedelta(days=365*25),
            citizenship_status="us_citizen",
            address_line1="123 Main St",
            city="Anytown",
            state="CA",
            zip_code="12345",
            housing_status="rent",
            housing_payment=Decimal("1000.00")
        )
        
        self.co_borrower_profile = BorrowerProfile.objects.create(
            user=self.co_borrower_user,
            ssn="987-65-4321",
            dob=timezone.now().date() - datetime.timedelta(days=365*30),
            citizenship_status="us_citizen",
            address_line1="456 Oak St",
            city="Othertown",
            state="NY",
            zip_code="54321",
            housing_status="own",
            housing_payment=Decimal("1500.00")
        )
        
        # Create school, program, program version
        self.school = School.objects.create(
            name="Test School",
            legal_name="Test School Inc.",
            tax_id="12-3456789",
            address_line1="789 School St",
            city="Education City",
            state="CA",
            zip_code="12345",
            phone="(555) 123-4567",
            status="active"
        )
        
        self.program = Program.objects.create(
            school=self.school,
            name="Test Program",
            description="A test program",
            duration_hours=120,
            duration_weeks=12,
            status="active"
        )
        
        self.program_version = ProgramVersion.objects.create(
            program=self.program,
            version_number=1,
            effective_date=timezone.now().date(),
            tuition_amount=Decimal("10000.00"),
            is_current=True
        )
        
        # Create loan applications
        self.loan_application1 = LoanApplication.objects.create(
            borrower=self.borrower_user,
            co_borrower=self.co_borrower_user,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            application_type="standard",
            status="qc_approved",
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        self.loan_application2 = LoanApplication.objects.create(
            borrower=self.borrower_user,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            application_type="standard",
            status="qc_approved",
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create funding requests
        self.funding_request1 = FundingRequest.objects.create(
            application=self.loan_application1,
            status=FUNDING_REQUEST_STATUS["PENDING"],
            requested_amount=Decimal("9000.00"),
            requested_by=self.staff_user,
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        self.funding_request2 = FundingRequest.objects.create(
            application=self.loan_application2,
            status=FUNDING_REQUEST_STATUS["ENROLLMENT_VERIFIED"],
            requested_amount=Decimal("8000.00"),
            requested_by=self.staff_user,
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Set up URL
        self.url = reverse('funding-requests-list')
    
    def test_list_funding_requests(self):
        """Test listing funding requests"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Make GET request
        response = self.client.get(self.url)
        
        # Assert response status code and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['application'], str(self.loan_application1.id))
        self.assertEqual(response.data['results'][0]['status'], FUNDING_REQUEST_STATUS["PENDING"])
        self.assertEqual(response.data['results'][0]['requested_amount'], '9000.00')
    
    def test_list_funding_requests_with_status_filter(self):
        """Test listing funding requests filtered by status"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Make GET request with status filter
        response = self.client.get(f"{self.url}?status={FUNDING_REQUEST_STATUS['ENROLLMENT_VERIFIED']}")
        
        # Assert response status code and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['application'], str(self.loan_application2.id))
        self.assertEqual(response.data['results'][0]['status'], FUNDING_REQUEST_STATUS["ENROLLMENT_VERIFIED"])
    
    @patch('apps.funding.services.FundingService.create_funding_request')
    def test_create_funding_request(self, mock_create_funding_request):
        """Test creating a new funding request"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Prepare data
        data = {
            'application_id': str(self.loan_application1.id),
            'requested_amount': '9500.00'
        }
        
        # Setup mock return value
        mock_funding_request = mock.MagicMock()
        mock_funding_request.id = uuid.uuid4()
        mock_funding_request.application = self.loan_application1
        mock_funding_request.status = FUNDING_REQUEST_STATUS["PENDING"]
        mock_funding_request.requested_amount = Decimal('9500.00')
        mock_create_funding_request.return_value = mock_funding_request
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_create_funding_request.assert_called_once_with(
            application_id=str(self.loan_application1.id),
            requested_amount=Decimal('9500.00'),
            user=self.staff_user
        )
    
    def test_create_funding_request_invalid_data(self):
        """Test creating a funding request with invalid data"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Prepare data with missing required fields
        data = {
            'requested_amount': '9500.00'
            # Missing application_id
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('application_id', response.data)
    
    def test_create_funding_request_unauthorized(self):
        """Test that non-staff users cannot create funding requests"""
        # Authenticate as borrower
        self.client.force_authenticate(user=self.borrower_user)
        
        # Prepare data
        data = {
            'application_id': str(self.loan_application1.id),
            'requested_amount': '9500.00'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class FundingRequestDetailViewTest(APITestCase):
    """Test case for the FundingRequestDetailView API view"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test users
        self.borrower_user = User.objects.create(email="borrower@example.com", first_name="Borrower", last_name="User", user_type="borrower")
        self.co_borrower_user = User.objects.create(email="co_borrower@example.com", first_name="Co", last_name="Borrower", user_type="co_borrower")
        self.staff_user = User.objects.create(email="staff@example.com", first_name="Staff", last_name="User", user_type="underwriter")
        
        # Create borrower profiles
        self.borrower_profile = BorrowerProfile.objects.create(
            user=self.borrower_user,
            ssn="123-45-6789",
            dob=timezone.now().date() - datetime.timedelta(days=365*25),
            citizenship_status="us_citizen",
            address_line1="123 Main St",
            city="Anytown",
            state="CA",
            zip_code="12345",
            housing_status="rent",
            housing_payment=Decimal("1000.00")
        )
        
        # Create school, program, program version
        self.school = School.objects.create(
            name="Test School",
            legal_name="Test School Inc.",
            tax_id="12-3456789",
            address_line1="789 School St",
            city="Education City",
            state="CA",
            zip_code="12345",
            phone="(555) 123-4567",
            status="active"
        )
        
        self.program = Program.objects.create(
            school=self.school,
            name="Test Program",
            description="A test program",
            duration_hours=120,
            duration_weeks=12,
            status="active"
        )
        
        self.program_version = ProgramVersion.objects.create(
            program=self.program,
            version_number=1,
            effective_date=timezone.now().date(),
            tuition_amount=Decimal("10000.00"),
            is_current=True
        )
        
        # Create loan application
        self.loan_application = LoanApplication.objects.create(
            borrower=self.borrower_user,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            application_type="standard",
            status="qc_approved",
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create funding request
        self.funding_request = FundingRequest.objects.create(
            application=self.loan_application,
            status=FUNDING_REQUEST_STATUS["PENDING"],
            requested_amount=Decimal("9000.00"),
            requested_by=self.staff_user,
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Set up URL
        self.url = reverse('funding-request-detail', kwargs={'pk': self.funding_request.id})
    
    def test_get_funding_request(self):
        """Test retrieving a specific funding request"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Make GET request
        response = self.client.get(self.url)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.funding_request.id))
        self.assertEqual(response.data['application'], str(self.loan_application.id))
        self.assertEqual(response.data['status'], FUNDING_REQUEST_STATUS["PENDING"])
        self.assertEqual(response.data['requested_amount'], '9000.00')
    
    def test_get_funding_request_not_found(self):
        """Test retrieving a non-existent funding request"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Make GET request with invalid ID
        url = reverse('funding-request-detail', kwargs={'pk': uuid.uuid4()})
        response = self.client.get(url)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_funding_request_unauthorized(self):
        """Test that non-staff users cannot retrieve funding requests"""
        # Authenticate as borrower
        self.client.force_authenticate(user=self.borrower_user)
        
        # Make GET request
        response = self.client.get(self.url)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class FundingRequestStatusUpdateViewTest(APITestCase):
    """Test case for the FundingRequestStatusUpdateView API view"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test users
        self.borrower_user = User.objects.create(email="borrower@example.com", first_name="Borrower", last_name="User", user_type="borrower")
        self.staff_user = User.objects.create(email="staff@example.com", first_name="Staff", last_name="User", user_type="underwriter")
        
        # Create borrower profile
        self.borrower_profile = BorrowerProfile.objects.create(
            user=self.borrower_user,
            ssn="123-45-6789",
            dob=timezone.now().date() - datetime.timedelta(days=365*25),
            citizenship_status="us_citizen",
            address_line1="123 Main St",
            city="Anytown",
            state="CA",
            zip_code="12345",
            housing_status="rent",
            housing_payment=Decimal("1000.00")
        )
        
        # Create school, program, program version
        self.school = School.objects.create(
            name="Test School",
            legal_name="Test School Inc.",
            tax_id="12-3456789",
            address_line1="789 School St",
            city="Education City",
            state="CA",
            zip_code="12345",
            phone="(555) 123-4567",
            status="active"
        )
        
        self.program = Program.objects.create(
            school=self.school,
            name="Test Program",
            description="A test program",
            duration_hours=120,
            duration_weeks=12,
            status="active"
        )
        
        self.program_version = ProgramVersion.objects.create(
            program=self.program,
            version_number=1,
            effective_date=timezone.now().date(),
            tuition_amount=Decimal("10000.00"),
            is_current=True
        )
        
        # Create loan application
        self.loan_application = LoanApplication.objects.create(
            borrower=self.borrower_user,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            application_type="standard",
            status="qc_approved",
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create funding request
        self.funding_request = FundingRequest.objects.create(
            application=self.loan_application,
            status=FUNDING_REQUEST_STATUS["PENDING"],
            requested_amount=Decimal("9000.00"),
            requested_by=self.staff_user,
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Set up URL
        self.url = reverse('funding-request-status-update', kwargs={'pk': self.funding_request.id})
    
    @patch('apps.funding.models.FundingRequest.update_status')
    def test_update_funding_request_status(self, mock_update_status):
        """Test updating the status of a funding request"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Set up mock return value
        mock_update_status.return_value = True
        
        # Prepare data
        data = {
            'status': FUNDING_REQUEST_STATUS["ENROLLMENT_VERIFIED"],
            'comments': 'Status updated for testing'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_update_status.assert_called_once_with(
            FUNDING_REQUEST_STATUS["ENROLLMENT_VERIFIED"], 
            self.staff_user, 
            'Status updated for testing'
        )
        self.assertIn('message', response.data)
    
    @patch('apps.funding.models.FundingRequest.update_status')
    def test_update_funding_request_status_invalid_transition(self, mock_update_status):
        """Test updating the status with an invalid transition"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Set up mock return value
        mock_update_status.return_value = False
        
        # Prepare data
        data = {
            'status': FUNDING_REQUEST_STATUS["DISBURSED"],  # Invalid immediate transition from PENDING
            'comments': 'Invalid status update'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_update_status.assert_called_once_with(
            FUNDING_REQUEST_STATUS["DISBURSED"], 
            self.staff_user, 
            'Invalid status update'
        )
        self.assertIn('error', response.data)
    
    def test_update_funding_request_status_invalid_data(self):
        """Test updating the status with invalid data"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Prepare data with missing required fields
        data = {
            # Missing status field
            'comments': 'Invalid status update'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)
    
    def test_update_funding_request_status_unauthorized(self):
        """Test that non-staff users cannot update funding request status"""
        # Authenticate as borrower
        self.client.force_authenticate(user=self.borrower_user)
        
        # Prepare data
        data = {
            'status': FUNDING_REQUEST_STATUS["ENROLLMENT_VERIFIED"],
            'comments': 'Status updated for testing'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class FundingRequestApprovalViewTest(APITestCase):
    """Test case for the FundingRequestApprovalView API view"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test users
        self.borrower_user = User.objects.create(email="borrower@example.com", first_name="Borrower", last_name="User", user_type="borrower")
        self.staff_user = User.objects.create(email="staff@example.com", first_name="Staff", last_name="User", user_type="underwriter")
        
        # Create borrower profile
        self.borrower_profile = BorrowerProfile.objects.create(
            user=self.borrower_user,
            ssn="123-45-6789",
            dob=timezone.now().date() - datetime.timedelta(days=365*25),
            citizenship_status="us_citizen",
            address_line1="123 Main St",
            city="Anytown",
            state="CA",
            zip_code="12345",
            housing_status="rent",
            housing_payment=Decimal("1000.00")
        )
        
        # Create school, program, program version
        self.school = School.objects.create(
            name="Test School",
            legal_name="Test School Inc.",
            tax_id="12-3456789",
            address_line1="789 School St",
            city="Education City",
            state="CA",
            zip_code="12345",
            phone="(555) 123-4567",
            status="active"
        )
        
        self.program = Program.objects.create(
            school=self.school,
            name="Test Program",
            description="A test program",
            duration_hours=120,
            duration_weeks=12,
            status="active"
        )
        
        self.program_version = ProgramVersion.objects.create(
            program=self.program,
            version_number=1,
            effective_date=timezone.now().date(),
            tuition_amount=Decimal("10000.00"),
            is_current=True
        )
        
        # Create loan application
        self.loan_application = LoanApplication.objects.create(
            borrower=self.borrower_user,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            application_type="standard",
            status="qc_approved",
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create funding request with STIPULATIONS_COMPLETE status (ready for approval)
        self.funding_request = FundingRequest.objects.create(
            application=self.loan_application,
            status=FUNDING_REQUEST_STATUS["STIPULATIONS_COMPLETE"],
            requested_amount=Decimal("9000.00"),
            requested_by=self.staff_user,
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Set up URL
        self.url = reverse('funding-request-approve', kwargs={'pk': self.funding_request.id})
    
    @patch('apps.funding.services.FundingService.approve_funding')
    def test_approve_funding_request(self, mock_approve_funding):
        """Test approving a funding request"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Set up mock return value
        mock_approve_funding.return_value = True
        
        # Prepare data
        data = {
            'approved_amount': '9000.00',
            'comments': 'Funding approved'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_approve_funding.assert_called_once_with(
            funding_request_id=str(self.funding_request.id),
            approved_amount=Decimal('9000.00'),
            user=self.staff_user,
            comments='Funding approved'
        )
        self.assertIn('message', response.data)
    
    @patch('apps.funding.services.FundingService.approve_funding')
    def test_approve_funding_request_invalid_status(self, mock_approve_funding):
        """Test approving a funding request with invalid status"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Set up mock return value
        mock_approve_funding.return_value = False
        
        # Prepare data
        data = {
            'approved_amount': '9000.00',
            'comments': 'Funding approved'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_approve_funding.assert_called_once_with(
            funding_request_id=str(self.funding_request.id),
            approved_amount=Decimal('9000.00'),
            user=self.staff_user,
            comments='Funding approved'
        )
        self.assertIn('error', response.data)
    
    def test_approve_funding_request_invalid_data(self):
        """Test approving a funding request with invalid data"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Prepare data with missing required fields
        data = {
            # Missing approved_amount
            'comments': 'Funding approved'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('approved_amount', response.data)
    
    def test_approve_funding_request_unauthorized(self):
        """Test that non-staff users cannot approve funding requests"""
        # Authenticate as borrower
        self.client.force_authenticate(user=self.borrower_user)
        
        # Prepare data
        data = {
            'approved_amount': '9000.00',
            'comments': 'Funding approved'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class EnrollmentVerificationListViewTest(APITestCase):
    """Test case for the EnrollmentVerificationListView API view"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test users
        self.borrower_user = User.objects.create(email="borrower@example.com", first_name="Borrower", last_name="User", user_type="borrower")
        self.school_admin_user = User.objects.create(email="school@example.com", first_name="School", last_name="Admin", user_type="school_admin")
        self.staff_user = User.objects.create(email="staff@example.com", first_name="Staff", last_name="User", user_type="underwriter")
        
        # Create borrower profile
        self.borrower_profile = BorrowerProfile.objects.create(
            user=self.borrower_user,
            ssn="123-45-6789",
            dob=timezone.now().date() - datetime.timedelta(days=365*25),
            citizenship_status="us_citizen",
            address_line1="123 Main St",
            city="Anytown",
            state="CA",
            zip_code="12345",
            housing_status="rent",
            housing_payment=Decimal("1000.00")
        )
        
        # Create school, program, program version
        self.school = School.objects.create(
            name="Test School",
            legal_name="Test School Inc.",
            tax_id="12-3456789",
            address_line1="789 School St",
            city="Education City",
            state="CA",
            zip_code="12345",
            phone="(555) 123-4567",
            status="active"
        )
        
        # Create school admin profile
        self.school_admin_profile = SchoolAdminProfile.objects.create(
            user=self.school_admin_user,
            school=self.school,
            title="Admissions Director",
            department="Admissions",
            is_primary_contact=True,
            can_sign_documents=True
        )
        
        self.program = Program.objects.create(
            school=self.school,
            name="Test Program",
            description="A test program",
            duration_hours=120,
            duration_weeks=12,
            status="active"
        )
        
        self.program_version = ProgramVersion.objects.create(
            program=self.program,
            version_number=1,
            effective_date=timezone.now().date(),
            tuition_amount=Decimal("10000.00"),
            is_current=True
        )
        
        # Create loan application
        self.loan_application = LoanApplication.objects.create(
            borrower=self.borrower_user,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            application_type="standard",
            status="qc_approved",
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create funding request
        self.funding_request = FundingRequest.objects.create(
            application=self.loan_application,
            status=FUNDING_REQUEST_STATUS["PENDING"],
            requested_amount=Decimal("9000.00"),
            requested_by=self.staff_user,
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create enrollment verification
        self.enrollment_verification = EnrollmentVerification.objects.create(
            application=self.loan_application,
            verification_type=ENROLLMENT_VERIFICATION_TYPE["ENROLLMENT_AGREEMENT"],
            verified_by=self.school_admin_user,
            start_date=timezone.now().date() + datetime.timedelta(days=30),
            document_id=uuid.uuid4(),
            created_by=self.school_admin_user,
            updated_by=self.school_admin_user
        )
        
        # Set up URL
        self.url = reverse('enrollment-verifications-list')
    
    def test_list_enrollment_verifications(self):
        """Test listing enrollment verifications"""
        # Authenticate as school admin user
        self.client.force_authenticate(user=self.school_admin_user)
        
        # Make GET request
        response = self.client.get(self.url)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['application'], str(self.loan_application.id))
        self.assertEqual(response.data['results'][0]['verification_type'], ENROLLMENT_VERIFICATION_TYPE["ENROLLMENT_AGREEMENT"])
    
    def test_create_enrollment_verification(self):
        """Test creating a new enrollment verification"""
        # Authenticate as school admin user
        self.client.force_authenticate(user=self.school_admin_user)
        
        # Prepare data
        data = {
            'funding_request_id': str(self.funding_request.id),
            'verification_type': ENROLLMENT_VERIFICATION_TYPE["SCHOOL_CONFIRMATION"],
            'start_date': (timezone.now().date() + datetime.timedelta(days=45)).isoformat(),
            'document_id': str(uuid.uuid4())
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['verification_type'], ENROLLMENT_VERIFICATION_TYPE["SCHOOL_CONFIRMATION"])
        self.assertEqual(response.data['verified_by'], str(self.school_admin_user.id))
        
        # Verify database record was created
        self.assertTrue(EnrollmentVerification.objects.filter(
            application=self.loan_application,
            verification_type=ENROLLMENT_VERIFICATION_TYPE["SCHOOL_CONFIRMATION"]
        ).exists())
    
    def test_create_enrollment_verification_invalid_data(self):
        """Test creating an enrollment verification with invalid data"""
        # Authenticate as school admin user
        self.client.force_authenticate(user=self.school_admin_user)
        
        # Prepare data with missing required fields
        data = {
            'funding_request_id': str(self.funding_request.id),
            # Missing verification_type
            'start_date': (timezone.now().date() + datetime.timedelta(days=45)).isoformat()
            # Missing document_id
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('verification_type', response.data)
        self.assertIn('document_id', response.data)
    
    def test_create_enrollment_verification_unauthorized(self):
        """Test that non-school admin users cannot create enrollment verifications"""
        # Authenticate as borrower
        self.client.force_authenticate(user=self.borrower_user)
        
        # Prepare data
        data = {
            'funding_request_id': str(self.funding_request.id),
            'verification_type': ENROLLMENT_VERIFICATION_TYPE["SCHOOL_CONFIRMATION"],
            'start_date': (timezone.now().date() + datetime.timedelta(days=45)).isoformat(),
            'document_id': str(uuid.uuid4())
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class VerifyEnrollmentViewTest(APITestCase):
    """Test case for the VerifyEnrollmentView API view"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test users
        self.borrower_user = User.objects.create(email="borrower@example.com", first_name="Borrower", last_name="User", user_type="borrower")
        self.school_admin_user = User.objects.create(email="school@example.com", first_name="School", last_name="Admin", user_type="school_admin")
        self.staff_user = User.objects.create(email="staff@example.com", first_name="Staff", last_name="User", user_type="underwriter")
        
        # Create borrower profile
        self.borrower_profile = BorrowerProfile.objects.create(
            user=self.borrower_user,
            ssn="123-45-6789",
            dob=timezone.now().date() - datetime.timedelta(days=365*25),
            citizenship_status="us_citizen",
            address_line1="123 Main St",
            city="Anytown",
            state="CA",
            zip_code="12345",
            housing_status="rent",
            housing_payment=Decimal("1000.00")
        )
        
        # Create school, program, program version
        self.school = School.objects.create(
            name="Test School",
            legal_name="Test School Inc.",
            tax_id="12-3456789",
            address_line1="789 School St",
            city="Education City",
            state="CA",
            zip_code="12345",
            phone="(555) 123-4567",
            status="active"
        )
        
        # Create school admin profile
        self.school_admin_profile = SchoolAdminProfile.objects.create(
            user=self.school_admin_user,
            school=self.school,
            title="Admissions Director",
            department="Admissions",
            is_primary_contact=True,
            can_sign_documents=True
        )
        
        self.program = Program.objects.create(
            school=self.school,
            name="Test Program",
            description="A test program",
            duration_hours=120,
            duration_weeks=12,
            status="active"
        )
        
        self.program_version = ProgramVersion.objects.create(
            program=self.program,
            version_number=1,
            effective_date=timezone.now().date(),
            tuition_amount=Decimal("10000.00"),
            is_current=True
        )
        
        # Create loan application
        self.loan_application = LoanApplication.objects.create(
            borrower=self.borrower_user,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            application_type="standard",
            status="qc_approved",
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create funding request
        self.funding_request = FundingRequest.objects.create(
            application=self.loan_application,
            status=FUNDING_REQUEST_STATUS["PENDING"],
            requested_amount=Decimal("9000.00"),
            requested_by=self.staff_user,
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Set up URL
        self.url = reverse('verify-enrollment', kwargs={'pk': self.funding_request.id})
    
    @patch('apps.funding.services.FundingService.verify_enrollment')
    def test_verify_enrollment(self, mock_verify_enrollment):
        """Test verifying enrollment for a funding request"""
        # Authenticate as school admin user
        self.client.force_authenticate(user=self.school_admin_user)
        
        # Set up mock return value
        mock_verify_enrollment.return_value = True
        
        # Prepare data
        data = {
            'verification_type': ENROLLMENT_VERIFICATION_TYPE["ENROLLMENT_AGREEMENT"],
            'start_date': (timezone.now().date() + datetime.timedelta(days=30)).isoformat(),
            'comments': 'Enrollment verified for testing',
            'document_id': str(uuid.uuid4())
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_verify_enrollment.assert_called_once_with(
            funding_request_id=str(self.funding_request.id),
            verification_type=ENROLLMENT_VERIFICATION_TYPE["ENROLLMENT_AGREEMENT"],
            start_date=datetime.datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            user=self.school_admin_user,
            comments='Enrollment verified for testing',
            document_id=data['document_id']
        )
        self.assertIn('message', response.data)
    
    def test_verify_enrollment_invalid_data(self):
        """Test verifying enrollment with invalid data"""
        # Authenticate as school admin user
        self.client.force_authenticate(user=self.school_admin_user)
        
        # Prepare data with missing required fields
        data = {
            # Missing verification_type
            'start_date': (timezone.now().date() + datetime.timedelta(days=30)).isoformat(),
            'comments': 'Enrollment verified for testing'
            # Missing document_id
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('verification_type', response.data)
        self.assertIn('document_id', response.data)
    
    @patch('apps.funding.services.FundingService.verify_enrollment')
    def test_verify_enrollment_verification_failed(self, mock_verify_enrollment):
        """Test verifying enrollment when verification fails"""
        # Authenticate as school admin user
        self.client.force_authenticate(user=self.school_admin_user)
        
        # Set up mock return value
        mock_verify_enrollment.return_value = False
        
        # Prepare data
        data = {
            'verification_type': ENROLLMENT_VERIFICATION_TYPE["ENROLLMENT_AGREEMENT"],
            'start_date': (timezone.now().date() + datetime.timedelta(days=30)).isoformat(),
            'comments': 'Enrollment verified for testing',
            'document_id': str(uuid.uuid4())
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_verify_enrollment.assert_called_once()
        self.assertIn('error', response.data)
    
    def test_verify_enrollment_unauthorized(self):
        """Test that non-school admin users cannot verify enrollment"""
        # Authenticate as borrower
        self.client.force_authenticate(user=self.borrower_user)
        
        # Prepare data
        data = {
            'verification_type': ENROLLMENT_VERIFICATION_TYPE["ENROLLMENT_AGREEMENT"],
            'start_date': (timezone.now().date() + datetime.timedelta(days=30)).isoformat(),
            'comments': 'Enrollment verified for testing',
            'document_id': str(uuid.uuid4())
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class StipulationVerificationListViewTest(APITestCase):
    """Test case for the StipulationVerificationListView API view"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test users
        self.borrower_user = User.objects.create(email="borrower@example.com", first_name="Borrower", last_name="User", user_type="borrower")
        self.staff_user = User.objects.create(email="staff@example.com", first_name="Staff", last_name="User", user_type="underwriter")
        
        # Create borrower profile
        self.borrower_profile = BorrowerProfile.objects.create(
            user=self.borrower_user,
            ssn="123-45-6789",
            dob=timezone.now().date() - datetime.timedelta(days=365*25),
            citizenship_status="us_citizen",
            address_line1="123 Main St",
            city="Anytown",
            state="CA",
            zip_code="12345",
            housing_status="rent",
            housing_payment=Decimal("1000.00")
        )
        
        # Create school, program, program version
        self.school = School.objects.create(
            name="Test School",
            legal_name="Test School Inc.",
            tax_id="12-3456789",
            address_line1="789 School St",
            city="Education City",
            state="CA",
            zip_code="12345",
            phone="(555) 123-4567",
            status="active"
        )
        
        self.program = Program.objects.create(
            school=self.school,
            name="Test Program",
            description="A test program",
            duration_hours=120,
            duration_weeks=12,
            status="active"
        )
        
        self.program_version = ProgramVersion.objects.create(
            program=self.program,
            version_number=1,
            effective_date=timezone.now().date(),
            tuition_amount=Decimal("10000.00"),
            is_current=True
        )
        
        # Create loan application
        self.loan_application = LoanApplication.objects.create(
            borrower=self.borrower_user,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            application_type="standard",
            status="qc_approved",
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create funding request
        self.funding_request = FundingRequest.objects.create(
            application=self.loan_application,
            status=FUNDING_REQUEST_STATUS["PENDING_STIPULATIONS"],
            requested_amount=Decimal("9000.00"),
            requested_by=self.staff_user,
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create stipulation
        self.stipulation = Stipulation.objects.create(
            application=self.loan_application,
            stipulation_type="proof_of_income",
            description="Please provide recent pay stubs as proof of income",
            required_by_date=timezone.now().date() + datetime.timedelta(days=14),
            created_by=self.staff_user
        )
        
        # Create stipulation verification
        self.stipulation_verification = StipulationVerification.objects.create(
            funding_request=self.funding_request,
            stipulation=self.stipulation,
            status=VERIFICATION_STATUS["PENDING"],
            verified_by=self.staff_user,
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Set up URL
        self.url = reverse('stipulation-verifications-list')
    
    def test_list_stipulation_verifications(self):
        """Test listing stipulation verifications"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Make GET request
        response = self.client.get(self.url)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['funding_request'], str(self.funding_request.id))
        self.assertEqual(response.data['results'][0]['stipulation'], str(self.stipulation.id))
        self.assertEqual(response.data['results'][0]['status'], VERIFICATION_STATUS["PENDING"])
    
    def test_create_stipulation_verification(self):
        """Test creating a new stipulation verification"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Create a new stipulation for testing
        new_stipulation = Stipulation.objects.create(
            application=self.loan_application,
            stipulation_type="proof_of_identity",
            description="Please provide a valid ID",
            required_by_date=timezone.now().date() + datetime.timedelta(days=14),
            created_by=self.staff_user
        )
        
        # Prepare data
        data = {
            'funding_request_id': str(self.funding_request.id),
            'stipulation_id': str(new_stipulation.id),
            'status': VERIFICATION_STATUS["VERIFIED"],
            'comments': 'Verified ID provided'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['funding_request'], str(self.funding_request.id))
        self.assertEqual(response.data['stipulation'], str(new_stipulation.id))
        self.assertEqual(response.data['status'], VERIFICATION_STATUS["VERIFIED"])
        
        # Verify database record was created
        self.assertTrue(StipulationVerification.objects.filter(
            funding_request=self.funding_request,
            stipulation=new_stipulation,
            status=VERIFICATION_STATUS["VERIFIED"]
        ).exists())
    
    def test_create_stipulation_verification_invalid_data(self):
        """Test creating a stipulation verification with invalid data"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Prepare data with missing required fields
        data = {
            'funding_request_id': str(self.funding_request.id),
            # Missing stipulation_id
            'status': VERIFICATION_STATUS["VERIFIED"],
            'comments': 'Verified ID provided'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stipulation_id', response.data)
    
    def test_create_stipulation_verification_unauthorized(self):
        """Test that non-staff users cannot create stipulation verifications"""
        # Authenticate as borrower
        self.client.force_authenticate(user=self.borrower_user)
        
        # Create a new stipulation for testing
        new_stipulation = Stipulation.objects.create(
            application=self.loan_application,
            stipulation_type="proof_of_identity",
            description="Please provide a valid ID",
            required_by_date=timezone.now().date() + datetime.timedelta(days=14),
            created_by=self.staff_user
        )
        
        # Prepare data
        data = {
            'funding_request_id': str(self.funding_request.id),
            'stipulation_id': str(new_stipulation.id),
            'status': VERIFICATION_STATUS["VERIFIED"],
            'comments': 'Verified ID provided'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class VerifyStipulationViewTest(APITestCase):
    """Test case for the VerifyStipulationView API view"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test users
        self.borrower_user = User.objects.create(email="borrower@example.com", first_name="Borrower", last_name="User", user_type="borrower")
        self.staff_user = User.objects.create(email="staff@example.com", first_name="Staff", last_name="User", user_type="underwriter")
        
        # Create borrower profile
        self.borrower_profile = BorrowerProfile.objects.create(
            user=self.borrower_user,
            ssn="123-45-6789",
            dob=timezone.now().date() - datetime.timedelta(days=365*25),
            citizenship_status="us_citizen",
            address_line1="123 Main St",
            city="Anytown",
            state="CA",
            zip_code="12345",
            housing_status="rent",
            housing_payment=Decimal("1000.00")
        )
        
        # Create school, program, program version
        self.school = School.objects.create(
            name="Test School",
            legal_name="Test School Inc.",
            tax_id="12-3456789",
            address_line1="789 School St",
            city="Education City",
            state="CA",
            zip_code="12345",
            phone="(555) 123-4567",
            status="active"
        )
        
        self.program = Program.objects.create(
            school=self.school,
            name="Test Program",
            description="A test program",
            duration_hours=120,
            duration_weeks=12,
            status="active"
        )
        
        self.program_version = ProgramVersion.objects.create(
            program=self.program,
            version_number=1,
            effective_date=timezone.now().date(),
            tuition_amount=Decimal("10000.00"),
            is_current=True
        )
        
        # Create loan application
        self.loan_application = LoanApplication.objects.create(
            borrower=self.borrower_user,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            application_type="standard",
            status="qc_approved",
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create funding request
        self.funding_request = FundingRequest.objects.create(
            application=self.loan_application,
            status=FUNDING_REQUEST_STATUS["PENDING_STIPULATIONS"],
            requested_amount=Decimal("9000.00"),
            requested_by=self.staff_user,
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create stipulation
        self.stipulation = Stipulation.objects.create(
            application=self.loan_application,
            stipulation_type="proof_of_income",
            description="Please provide recent pay stubs as proof of income",
            required_by_date=timezone.now().date() + datetime.timedelta(days=14),
            created_by=self.staff_user
        )
        
        # Create stipulation verification
        self.stipulation_verification = StipulationVerification.objects.create(
            funding_request=self.funding_request,
            stipulation=self.stipulation,
            status=VERIFICATION_STATUS["PENDING"],
            verified_by=self.staff_user,
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Set up URL
        self.url = reverse('verify-stipulation', kwargs={'pk': self.stipulation_verification.id})
    
    @patch('apps.funding.services.FundingService.verify_stipulation')
    def test_verify_stipulation(self, mock_verify_stipulation):
        """Test verifying a stipulation"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Set up mock return value
        mock_stipulation_verification = mock.MagicMock()
        mock_stipulation_verification.id = self.stipulation_verification.id
        mock_stipulation_verification.status = VERIFICATION_STATUS["VERIFIED"]
        mock_verify_stipulation.return_value = mock_stipulation_verification
        
        # Prepare data
        data = {
            'comments': 'Stipulation verified'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_verify_stipulation.assert_called_once_with(
            verification_id=str(self.stipulation_verification.id),
            user=self.staff_user,
            comments='Stipulation verified'
        )
        self.assertIn('message', response.data)
    
    def test_verify_stipulation_not_found(self):
        """Test verifying a non-existent stipulation verification"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Set up URL with invalid ID
        url = reverse('verify-stipulation', kwargs={'pk': uuid.uuid4()})
        
        # Prepare data
        data = {
            'comments': 'Stipulation verified'
        }
        
        # Make POST request
        response = self.client.post(url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_verify_stipulation_unauthorized(self):
        """Test that non-staff users cannot verify stipulations"""
        # Authenticate as borrower
        self.client.force_authenticate(user=self.borrower_user)
        
        # Prepare data
        data = {
            'comments': 'Stipulation verified'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RejectStipulationViewTest(APITestCase):
    """Test case for the RejectStipulationView API view"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test users
        self.borrower_user = User.objects.create(email="borrower@example.com", first_name="Borrower", last_name="User", user_type="borrower")
        self.staff_user = User.objects.create(email="staff@example.com", first_name="Staff", last_name="User", user_type="underwriter")
        
        # Create borrower profile
        self.borrower_profile = BorrowerProfile.objects.create(
            user=self.borrower_user,
            ssn="123-45-6789",
            dob=timezone.now().date() - datetime.timedelta(days=365*25),
            citizenship_status="us_citizen",
            address_line1="123 Main St",
            city="Anytown",
            state="CA",
            zip_code="12345",
            housing_status="rent",
            housing_payment=Decimal("1000.00")
        )
        
        # Create school, program, program version
        self.school = School.objects.create(
            name="Test School",
            legal_name="Test School Inc.",
            tax_id="12-3456789",
            address_line1="789 School St",
            city="Education City",
            state="CA",
            zip_code="12345",
            phone="(555) 123-4567",
            status="active"
        )
        
        self.program = Program.objects.create(
            school=self.school,
            name="Test Program",
            description="A test program",
            duration_hours=120,
            duration_weeks=12,
            status="active"
        )
        
        self.program_version = ProgramVersion.objects.create(
            program=self.program,
            version_number=1,
            effective_date=timezone.now().date(),
            tuition_amount=Decimal("10000.00"),
            is_current=True
        )
        
        # Create loan application
        self.loan_application = LoanApplication.objects.create(
            borrower=self.borrower_user,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            application_type="standard",
            status="qc_approved",
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create funding request
        self.funding_request = FundingRequest.objects.create(
            application=self.loan_application,
            status=FUNDING_REQUEST_STATUS["PENDING_STIPULATIONS"],
            requested_amount=Decimal("9000.00"),
            requested_by=self.staff_user,
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create stipulation
        self.stipulation = Stipulation.objects.create(
            application=self.loan_application,
            stipulation_type="proof_of_income",
            description="Please provide recent pay stubs as proof of income",
            required_by_date=timezone.now().date() + datetime.timedelta(days=14),
            created_by=self.staff_user
        )
        
        # Create stipulation verification
        self.stipulation_verification = StipulationVerification.objects.create(
            funding_request=self.funding_request,
            stipulation=self.stipulation,
            status=VERIFICATION_STATUS["PENDING"],
            verified_by=self.staff_user,
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Set up URL
        self.url = reverse('reject-stipulation', kwargs={'pk': self.stipulation_verification.id})
    
    @patch('apps.funding.services.FundingService.reject_stipulation')
    def test_reject_stipulation(self, mock_reject_stipulation):
        """Test rejecting a stipulation"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Set up mock return value
        mock_stipulation_verification = mock.MagicMock()
        mock_stipulation_verification.id = self.stipulation_verification.id
        mock_stipulation_verification.status = VERIFICATION_STATUS["REJECTED"]
        mock_reject_stipulation.return_value = mock_stipulation_verification
        
        # Prepare data
        data = {
            'comments': 'Stipulation rejected - document not legible'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_reject_stipulation.assert_called_once_with(
            verification_id=str(self.stipulation_verification.id),
            user=self.staff_user,
            comments='Stipulation rejected - document not legible'
        )
        self.assertIn('message', response.data)
    
    def test_reject_stipulation_not_found(self):
        """Test rejecting a non-existent stipulation verification"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Set up URL with invalid ID
        url = reverse('reject-stipulation', kwargs={'pk': uuid.uuid4()})
        
        # Prepare data
        data = {
            'comments': 'Stipulation rejected'
        }
        
        # Make POST request
        response = self.client.post(url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_reject_stipulation_unauthorized(self):
        """Test that non-staff users cannot reject stipulations"""
        # Authenticate as borrower
        self.client.force_authenticate(user=self.borrower_user)
        
        # Prepare data
        data = {
            'comments': 'Stipulation rejected'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class WaiveStipulationViewTest(APITestCase):
    """Test case for the WaiveStipulationView API view"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test users
        self.borrower_user = User.objects.create(email="borrower@example.com", first_name="Borrower", last_name="User", user_type="borrower")
        self.staff_user = User.objects.create(email="staff@example.com", first_name="Staff", last_name="User", user_type="underwriter")
        
        # Create borrower profile
        self.borrower_profile = BorrowerProfile.objects.create(
            user=self.borrower_user,
            ssn="123-45-6789",
            dob=timezone.now().date() - datetime.timedelta(days=365*25),
            citizenship_status="us_citizen",
            address_line1="123 Main St",
            city="Anytown",
            state="CA",
            zip_code="12345",
            housing_status="rent",
            housing_payment=Decimal("1000.00")
        )
        
        # Create school, program, program version
        self.school = School.objects.create(
            name="Test School",
            legal_name="Test School Inc.",
            tax_id="12-3456789",
            address_line1="789 School St",
            city="Education City",
            state="CA",
            zip_code="12345",
            phone="(555) 123-4567",
            status="active"
        )
        
        self.program = Program.objects.create(
            school=self.school,
            name="Test Program",
            description="A test program",
            duration_hours=120,
            duration_weeks=12,
            status="active"
        )
        
        self.program_version = ProgramVersion.objects.create(
            program=self.program,
            version_number=1,
            effective_date=timezone.now().date(),
            tuition_amount=Decimal("10000.00"),
            is_current=True
        )
        
        # Create loan application
        self.loan_application = LoanApplication.objects.create(
            borrower=self.borrower_user,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            application_type="standard",
            status="qc_approved",
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create funding request
        self.funding_request = FundingRequest.objects.create(
            application=self.loan_application,
            status=FUNDING_REQUEST_STATUS["PENDING_STIPULATIONS"],
            requested_amount=Decimal("9000.00"),
            requested_by=self.staff_user,
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create stipulation
        self.stipulation = Stipulation.objects.create(
            application=self.loan_application,
            stipulation_type="proof_of_income",
            description="Please provide recent pay stubs as proof of income",
            required_by_date=timezone.now().date() + datetime.timedelta(days=14),
            created_by=self.staff_user
        )
        
        # Create stipulation verification
        self.stipulation_verification = StipulationVerification.objects.create(
            funding_request=self.funding_request,
            stipulation=self.stipulation,
            status=VERIFICATION_STATUS["PENDING"],
            verified_by=self.staff_user,
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Set up URL
        self.url = reverse('waive-stipulation', kwargs={'pk': self.stipulation_verification.id})
    
    @patch('apps.funding.services.FundingService.waive_stipulation')
    def test_waive_stipulation(self, mock_waive_stipulation):
        """Test waiving a stipulation"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Set up mock return value
        mock_stipulation_verification = mock.MagicMock()
        mock_stipulation_verification.id = self.stipulation_verification.id
        mock_stipulation_verification.status = VERIFICATION_STATUS["WAIVED"]
        mock_waive_stipulation.return_value = mock_stipulation_verification
        
        # Prepare data
        data = {
            'comments': 'Stipulation waived - verified through alternative means'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_waive_stipulation.assert_called_once_with(
            verification_id=str(self.stipulation_verification.id),
            user=self.staff_user,
            comments='Stipulation waived - verified through alternative means'
        )
        self.assertIn('message', response.data)
    
    def test_waive_stipulation_not_found(self):
        """Test waiving a non-existent stipulation verification"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Set up URL with invalid ID
        url = reverse('waive-stipulation', kwargs={'pk': uuid.uuid4()})
        
        # Prepare data
        data = {
            'comments': 'Stipulation waived'
        }
        
        # Make POST request
        response = self.client.post(url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_waive_stipulation_unauthorized(self):
        """Test that non-staff users cannot waive stipulations"""
        # Authenticate as borrower
        self.client.force_authenticate(user=self.borrower_user)
        
        # Prepare data
        data = {
            'comments': 'Stipulation waived'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DisbursementListViewTest(APITestCase):
    """Test case for the DisbursementListView API view"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test users
        self.borrower_user = User.objects.create(email="borrower@example.com", first_name="Borrower", last_name="User", user_type="borrower")
        self.staff_user = User.objects.create(email="staff@example.com", first_name="Staff", last_name="User", user_type="underwriter")
        
        # Create borrower profile
        self.borrower_profile = BorrowerProfile.objects.create(
            user=self.borrower_user,
            ssn="123-45-6789",
            dob=timezone.now().date() - datetime.timedelta(days=365*25),
            citizenship_status="us_citizen",
            address_line1="123 Main St",
            city="Anytown",
            state="CA",
            zip_code="12345",
            housing_status="rent",
            housing_payment=Decimal("1000.00")
        )
        
        # Create school, program, program version
        self.school = School.objects.create(
            name="Test School",
            legal_name="Test School Inc.",
            tax_id="12-3456789",
            address_line1="789 School St",
            city="Education City",
            state="CA",
            zip_code="12345",
            phone="(555) 123-4567",
            status="active"
        )
        
        self.program = Program.objects.create(
            school=self.school,
            name="Test Program",
            description="A test program",
            duration_hours=120,
            duration_weeks=12,
            status="active"
        )
        
        self.program_version = ProgramVersion.objects.create(
            program=self.program,
            version_number=1,
            effective_date=timezone.now().date(),
            tuition_amount=Decimal("10000.00"),
            is_current=True
        )
        
        # Create loan application
        self.loan_application = LoanApplication.objects.create(
            borrower=self.borrower_user,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            application_type="standard",
            status="qc_approved",
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create funding request with APPROVED status
        self.funding_request = FundingRequest.objects.create(
            application=self.loan_application,
            status=FUNDING_REQUEST_STATUS["APPROVED"],
            requested_amount=Decimal("9000.00"),
            approved_amount=Decimal("9000.00"),
            requested_by=self.staff_user,
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create disbursements
        self.disbursement1 = Disbursement.objects.create(
            funding_request=self.funding_request,
            amount=Decimal("4500.00"),
            disbursement_date=timezone.now().date() + datetime.timedelta(days=7),
            disbursement_method=DISBURSEMENT_METHOD["ACH"],
            status="scheduled",
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        self.disbursement2 = Disbursement.objects.create(
            funding_request=self.funding_request,
            amount=Decimal("4500.00"),
            disbursement_date=timezone.now().date() + datetime.timedelta(days=90),
            disbursement_method=DISBURSEMENT_METHOD["ACH"],
            status="scheduled",
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Set up URL
        self.url = reverse('disbursements-list')
    
    def test_list_disbursements(self):
        """Test listing disbursements"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Make GET request
        response = self.client.get(self.url)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['funding_request'], str(self.funding_request.id))
        self.assertEqual(response.data['results'][0]['amount'], '4500.00')
        self.assertEqual(response.data['results'][0]['disbursement_method'], DISBURSEMENT_METHOD["ACH"])
    
    @patch('apps.funding.services.DisbursementService.schedule_disbursement')
    def test_create_disbursement(self, mock_schedule_disbursement):
        """Test creating a new disbursement"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Set up mock return value
        mock_disbursement = mock.MagicMock()
        mock_disbursement.id = uuid.uuid4()
        mock_disbursement.funding_request = self.funding_request
        mock_disbursement.amount = Decimal("9000.00")
        mock_disbursement.disbursement_date = timezone.now().date() + datetime.timedelta(days=14)
        mock_disbursement.disbursement_method = DISBURSEMENT_METHOD["WIRE"]
        mock_disbursement.status = "scheduled"
        mock_schedule_disbursement.return_value = mock_disbursement
        
        # Prepare data
        data = {
            'funding_request_id': str(self.funding_request.id),
            'amount': '9000.00',
            'disbursement_date': (timezone.now().date() + datetime.timedelta(days=14)).isoformat(),
            'disbursement_method': DISBURSEMENT_METHOD["WIRE"],
            'comments': 'Scheduled for disbursement'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_schedule_disbursement.assert_called_once_with(
            funding_request_id=str(self.funding_request.id),
            amount=Decimal('9000.00'),
            disbursement_date=datetime.datetime.strptime(data['disbursement_date'], '%Y-%m-%d').date(),
            disbursement_method=DISBURSEMENT_METHOD["WIRE"],
            user=self.staff_user,
            comments='Scheduled for disbursement'
        )
        self.assertIn('id', response.data)
    
    def test_create_disbursement_invalid_data(self):
        """Test creating a disbursement with invalid data"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Prepare data with missing required fields
        data = {
            'funding_request_id': str(self.funding_request.id),
            # Missing amount
            'disbursement_date': (timezone.now().date() + datetime.timedelta(days=14)).isoformat(),
            # Missing disbursement_method
            'comments': 'Scheduled for disbursement'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', response.data)
        self.assertIn('disbursement_method', response.data)
    
    @patch('apps.funding.services.DisbursementService.schedule_disbursement')
    def test_create_disbursement_scheduling_failed(self, mock_schedule_disbursement):
        """Test creating a disbursement when scheduling fails"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Set up mock return value
        mock_schedule_disbursement.return_value = None
        
        # Prepare data
        data = {
            'funding_request_id': str(self.funding_request.id),
            'amount': '9000.00',
            'disbursement_date': (timezone.now().date() + datetime.timedelta(days=14)).isoformat(),
            'disbursement_method': DISBURSEMENT_METHOD["WIRE"],
            'comments': 'Scheduled for disbursement'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_schedule_disbursement.assert_called_once()
        self.assertIn('error', response.data)
    
    def test_create_disbursement_unauthorized(self):
        """Test that non-staff users cannot create disbursements"""
        # Authenticate as borrower
        self.client.force_authenticate(user=self.borrower_user)
        
        # Prepare data
        data = {
            'funding_request_id': str(self.funding_request.id),
            'amount': '9000.00',
            'disbursement_date': (timezone.now().date() + datetime.timedelta(days=14)).isoformat(),
            'disbursement_method': DISBURSEMENT_METHOD["WIRE"],
            'comments': 'Scheduled for disbursement'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ProcessDisbursementViewTest(APITestCase):
    """Test case for the ProcessDisbursementView API view"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test users
        self.borrower_user = User.objects.create(email="borrower@example.com", first_name="Borrower", last_name="User", user_type="borrower")
        self.staff_user = User.objects.create(email="staff@example.com", first_name="Staff", last_name="User", user_type="underwriter")
        
        # Create borrower profile
        self.borrower_profile = BorrowerProfile.objects.create(
            user=self.borrower_user,
            ssn="123-45-6789",
            dob=timezone.now().date() - datetime.timedelta(days=365*25),
            citizenship_status="us_citizen",
            address_line1="123 Main St",
            city="Anytown",
            state="CA",
            zip_code="12345",
            housing_status="rent",
            housing_payment=Decimal("1000.00")
        )
        
        # Create school, program, program version
        self.school = School.objects.create(
            name="Test School",
            legal_name="Test School Inc.",
            tax_id="12-3456789",
            address_line1="789 School St",
            city="Education City",
            state="CA",
            zip_code="12345",
            phone="(555) 123-4567",
            status="active"
        )
        
        self.program = Program.objects.create(
            school=self.school,
            name="Test Program",
            description="A test program",
            duration_hours=120,
            duration_weeks=12,
            status="active"
        )
        
        self.program_version = ProgramVersion.objects.create(
            program=self.program,
            version_number=1,
            effective_date=timezone.now().date(),
            tuition_amount=Decimal("10000.00"),
            is_current=True
        )
        
        # Create loan application
        self.loan_application = LoanApplication.objects.create(
            borrower=self.borrower_user,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            application_type="standard",
            status="qc_approved",
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create funding request with SCHEDULED_FOR_DISBURSEMENT status
        self.funding_request = FundingRequest.objects.create(
            application=self.loan_application,
            status=FUNDING_REQUEST_STATUS["SCHEDULED_FOR_DISBURSEMENT"],
            requested_amount=Decimal("9000.00"),
            approved_amount=Decimal("9000.00"),
            requested_by=self.staff_user,
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create disbursement with "scheduled" status
        self.disbursement = Disbursement.objects.create(
            funding_request=self.funding_request,
            amount=Decimal("9000.00"),
            disbursement_date=timezone.now().date(),
            disbursement_method=DISBURSEMENT_METHOD["ACH"],
            status="scheduled",
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Set up URL
        self.url = reverse('process-disbursement', kwargs={'pk': self.disbursement.id})
    
    @patch('apps.funding.services.DisbursementService.process_disbursement')
    def test_process_disbursement(self, mock_process_disbursement):
        """Test processing a disbursement"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Set up mock return value
        mock_process_disbursement.return_value = True
        
        # Prepare data
        data = {
            'reference_number': 'ACH12345678',
            'comments': 'Disbursement processed'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_process_disbursement.assert_called_once_with(
            disbursement_id=str(self.disbursement.id),
            reference_number='ACH12345678',
            user=self.staff_user,
            comments='Disbursement processed'
        )
        self.assertIn('message', response.data)
    
    def test_process_disbursement_invalid_data(self):
        """Test processing a disbursement with invalid data"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Prepare data with missing required fields
        data = {
            # Missing reference_number
            'comments': 'Disbursement processed'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('reference_number', response.data)
    
    @patch('apps.funding.services.DisbursementService.process_disbursement')
    def test_process_disbursement_processing_failed(self, mock_process_disbursement):
        """Test processing a disbursement when processing fails"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Set up mock return value
        mock_process_disbursement.return_value = False
        
        # Prepare data
        data = {
            'reference_number': 'ACH12345678',
            'comments': 'Disbursement processed'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_process_disbursement.assert_called_once()
        self.assertIn('error', response.data)
    
    def test_process_disbursement_not_found(self):
        """Test processing a non-existent disbursement"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Set up URL with invalid ID
        url = reverse('process-disbursement', kwargs={'pk': uuid.uuid4()})
        
        # Prepare data
        data = {
            'reference_number': 'ACH12345678',
            'comments': 'Disbursement processed'
        }
        
        # Make POST request
        response = self.client.post(url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_process_disbursement_unauthorized(self):
        """Test that non-staff users cannot process disbursements"""
        # Authenticate as borrower
        self.client.force_authenticate(user=self.borrower_user)
        
        # Prepare data
        data = {
            'reference_number': 'ACH12345678',
            'comments': 'Disbursement processed'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CancelDisbursementViewTest(APITestCase):
    """Test case for the CancelDisbursementView API view"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test users
        self.borrower_user = User.objects.create(email="borrower@example.com", first_name="Borrower", last_name="User", user_type="borrower")
        self.staff_user = User.objects.create(email="staff@example.com", first_name="Staff", last_name="User", user_type="underwriter")
        
        # Create borrower profile
        self.borrower_profile = BorrowerProfile.objects.create(
            user=self.borrower_user,
            ssn="123-45-6789",
            dob=timezone.now().date() - datetime.timedelta(days=365*25),
            citizenship_status="us_citizen",
            address_line1="123 Main St",
            city="Anytown",
            state="CA",
            zip_code="12345",
            housing_status="rent",
            housing_payment=Decimal("1000.00")
        )
        
        # Create school, program, program version
        self.school = School.objects.create(
            name="Test School",
            legal_name="Test School Inc.",
            tax_id="12-3456789",
            address_line1="789 School St",
            city="Education City",
            state="CA",
            zip_code="12345",
            phone="(555) 123-4567",
            status="active"
        )
        
        self.program = Program.objects.create(
            school=self.school,
            name="Test Program",
            description="A test program",
            duration_hours=120,
            duration_weeks=12,
            status="active"
        )
        
        self.program_version = ProgramVersion.objects.create(
            program=self.program,
            version_number=1,
            effective_date=timezone.now().date(),
            tuition_amount=Decimal("10000.00"),
            is_current=True
        )
        
        # Create loan application
        self.loan_application = LoanApplication.objects.create(
            borrower=self.borrower_user,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            application_type="standard",
            status="qc_approved",
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create funding request with SCHEDULED_FOR_DISBURSEMENT status
        self.funding_request = FundingRequest.objects.create(
            application=self.loan_application,
            status=FUNDING_REQUEST_STATUS["SCHEDULED_FOR_DISBURSEMENT"],
            requested_amount=Decimal("9000.00"),
            approved_amount=Decimal("9000.00"),
            requested_by=self.staff_user,
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create disbursement with "scheduled" status
        self.disbursement = Disbursement.objects.create(
            funding_request=self.funding_request,
            amount=Decimal("9000.00"),
            disbursement_date=timezone.now().date() + datetime.timedelta(days=7),
            disbursement_method=DISBURSEMENT_METHOD["ACH"],
            status="scheduled",
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Set up URL
        self.url = reverse('cancel-disbursement', kwargs={'pk': self.disbursement.id})
    
    @patch('apps.funding.services.DisbursementService.cancel_disbursement')
    def test_cancel_disbursement(self, mock_cancel_disbursement):
        """Test cancelling a disbursement"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Set up mock return value
        mock_cancel_disbursement.return_value = True
        
        # Prepare data
        data = {
            'reason': 'Student withdrew from program'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_cancel_disbursement.assert_called_once_with(
            disbursement_id=str(self.disbursement.id),
            user=self.staff_user,
            reason='Student withdrew from program'
        )
        self.assertIn('message', response.data)
    
    @patch('apps.funding.services.DisbursementService.cancel_disbursement')
    def test_cancel_disbursement_cancellation_failed(self, mock_cancel_disbursement):
        """Test cancelling a disbursement when cancellation fails"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Set up mock return value
        mock_cancel_disbursement.return_value = False
        
        # Prepare data
        data = {
            'reason': 'Student withdrew from program'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_cancel_disbursement.assert_called_once()
        self.assertIn('error', response.data)
    
    def test_cancel_disbursement_not_found(self):
        """Test cancelling a non-existent disbursement"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Set up URL with invalid ID
        url = reverse('cancel-disbursement', kwargs={'pk': uuid.uuid4()})
        
        # Prepare data
        data = {
            'reason': 'Student withdrew from program'
        }
        
        # Make POST request
        response = self.client.post(url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_cancel_disbursement_unauthorized(self):
        """Test that non-staff users cannot cancel disbursements"""
        # Authenticate as borrower
        self.client.force_authenticate(user=self.borrower_user)
        
        # Prepare data
        data = {
            'reason': 'Student withdrew from program'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class FundingNoteListViewTest(APITestCase):
    """Test case for the FundingNoteListView API view"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test users
        self.borrower_user = User.objects.create(email="borrower@example.com", first_name="Borrower", last_name="User", user_type="borrower")
        self.staff_user = User.objects.create(email="staff@example.com", first_name="Staff", last_name="User", user_type="underwriter")
        
        # Create borrower profile
        self.borrower_profile = BorrowerProfile.objects.create(
            user=self.borrower_user,
            ssn="123-45-6789",
            dob=timezone.now().date() - datetime.timedelta(days=365*25),
            citizenship_status="us_citizen",
            address_line1="123 Main St",
            city="Anytown",
            state="CA",
            zip_code="12345",
            housing_status="rent",
            housing_payment=Decimal("1000.00")
        )
        
        # Create school, program, program version
        self.school = School.objects.create(
            name="Test School",
            legal_name="Test School Inc.",
            tax_id="12-3456789",
            address_line1="789 School St",
            city="Education City",
            state="CA",
            zip_code="12345",
            phone="(555) 123-4567",
            status="active"
        )
        
        self.program = Program.objects.create(
            school=self.school,
            name="Test Program",
            description="A test program",
            duration_hours=120,
            duration_weeks=12,
            status="active"
        )
        
        self.program_version = ProgramVersion.objects.create(
            program=self.program,
            version_number=1,
            effective_date=timezone.now().date(),
            tuition_amount=Decimal("10000.00"),
            is_current=True
        )
        
        # Create loan application
        self.loan_application = LoanApplication.objects.create(
            borrower=self.borrower_user,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            application_type="standard",
            status="qc_approved",
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create funding request
        self.funding_request = FundingRequest.objects.create(
            application=self.loan_application,
            status=FUNDING_REQUEST_STATUS["PENDING"],
            requested_amount=Decimal("9000.00"),
            requested_by=self.staff_user,
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Create funding notes
        self.funding_note1 = FundingNote.objects.create(
            funding_request=self.funding_request,
            note_type=FUNDING_NOTE_TYPE["GENERAL"],
            note_text="Initial funding request note",
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        self.funding_note2 = FundingNote.objects.create(
            funding_request=self.funding_request,
            note_type=FUNDING_NOTE_TYPE["STIPULATION"],
            note_text="Additional documentation may be required",
            created_by=self.staff_user,
            updated_by=self.staff_user
        )
        
        # Set up URL
        self.url = reverse('funding-notes-list')
    
    def test_list_funding_notes(self):
        """Test listing funding notes"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Make GET request
        response = self.client.get(self.url)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['funding_request'], str(self.funding_request.id))
        self.assertIn(response.data['results'][0]['note_type'], [FUNDING_NOTE_TYPE["GENERAL"], FUNDING_NOTE_TYPE["STIPULATION"]])
    
    @patch('apps.funding.services.FundingService.add_funding_note')
    def test_create_funding_note(self, mock_add_funding_note):
        """Test creating a new funding note"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Set up mock return value
        mock_note = mock.MagicMock()
        mock_note.id = uuid.uuid4()
        mock_note.funding_request = self.funding_request
        mock_note.note_type = FUNDING_NOTE_TYPE["APPROVAL"]
        mock_note.note_text = "Approved funding request"
        mock_note.created_by = self.staff_user
        mock_add_funding_note.return_value = mock_note
        
        # Prepare data
        data = {
            'funding_request_id': str(self.funding_request.id),
            'note_type': FUNDING_NOTE_TYPE["APPROVAL"],
            'note_text': 'Approved funding request'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_add_funding_note.assert_called_once_with(
            funding_request_id=str(self.funding_request.id),
            note_type=FUNDING_NOTE_TYPE["APPROVAL"],
            note_text='Approved funding request',
            user=self.staff_user
        )
        self.assertIn('id', response.data)
    
    def test_create_funding_note_invalid_data(self):
        """Test creating a funding note with invalid data"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Prepare data with missing required fields
        data = {
            'funding_request_id': str(self.funding_request.id),
            # Missing note_type
            'note_text': 'Approved funding request'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('note_type', response.data)
    
    def test_create_funding_note_unauthorized(self):
        """Test that non-staff users cannot create funding notes"""
        # Authenticate as borrower
        self.client.force_authenticate(user=self.borrower_user)
        
        # Prepare data
        data = {
            'funding_request_id': str(self.funding_request.id),
            'note_type': FUNDING_NOTE_TYPE["APPROVAL"],
            'note_text': 'Approved funding request'
        }
        
        # Make POST request
        response = self.client.post(self.url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class NextDisbursementDateViewTest(APITestCase):
    """Test case for the NextDisbursementDateView API view"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test staff user
        self.borrower_user = User.objects.create(email="borrower@example.com", first_name="Borrower", last_name="User", user_type="borrower")
        self.staff_user = User.objects.create(email="staff@example.com", first_name="Staff", last_name="User", user_type="underwriter")
        
        # Set up URL
        self.url = reverse('next-disbursement-date')
    
    @patch('apps.funding.services.DisbursementService.get_next_disbursement_date')
    def test_get_next_disbursement_date(self, mock_get_next_disbursement_date):
        """Test getting the next available disbursement date"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Set up mock return value
        next_date = timezone.now().date() + datetime.timedelta(days=5)
        mock_get_next_disbursement_date.return_value = next_date
        
        # Make GET request
        response = self.client.get(self.url)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_next_disbursement_date.assert_called_once_with(None)
        self.assertEqual(response.data['next_disbursement_date'], next_date.isoformat())
    
    @patch('apps.funding.services.DisbursementService.get_next_disbursement_date')
    def test_get_next_disbursement_date_with_from_date(self, mock_get_next_disbursement_date):
        """Test getting the next available disbursement date with a from_date parameter"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Set up mock return value
        from_date_str = (timezone.now().date() + datetime.timedelta(days=10)).isoformat()
        from_date = datetime.datetime.strptime(from_date_str, '%Y-%m-%d').date()
        next_date = from_date + datetime.timedelta(days=2)
        mock_get_next_disbursement_date.return_value = next_date
        
        # Make GET request with from_date parameter
        response = self.client.get(f"{self.url}?from_date={from_date_str}")
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_next_disbursement_date.assert_called_once_with(from_date)
        self.assertEqual(response.data['next_disbursement_date'], next_date.isoformat())
    
    def test_get_next_disbursement_date_unauthorized(self):
        """Test that non-staff users cannot get the next disbursement date"""
        # Authenticate as borrower
        self.client.force_authenticate(user=self.borrower_user)
        
        # Make GET request
        response = self.client.get(self.url)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class FundingDashboardViewTest(APITestCase):
    """Test case for the FundingDashboardView API view"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test staff user
        self.borrower_user = User.objects.create(email="borrower@example.com", first_name="Borrower", last_name="User", user_type="borrower")
        self.staff_user = User.objects.create(email="staff@example.com", first_name="Staff", last_name="User", user_type="underwriter")
        
        # Set up URL
        self.url = reverse('funding-dashboard')
    
    @patch('apps.funding.services.FundingService.get_pending_requests_count')
    @patch('apps.funding.services.FundingService.get_approved_requests_count')
    @patch('apps.funding.services.FundingService.get_disbursed_requests_count')
    @patch('apps.funding.services.FundingService.get_cancelled_requests_count')
    @patch('apps.funding.services.FundingService.get_pending_stipulations_count')
    def test_get_funding_dashboard(self, mock_pending_stipulations, mock_cancelled, 
                                  mock_disbursed, mock_approved, mock_pending):
        """Test getting the funding dashboard data"""
        # Authenticate as staff user
        self.client.force_authenticate(user=self.staff_user)
        
        # Set up mock return values
        mock_pending.return_value = 10
        mock_approved.return_value = 25
        mock_disbursed.return_value = 50
        mock_cancelled.return_value = 5
        mock_pending_stipulations.return_value = 15
        
        # Make GET request
        response = self.client.get(self.url)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pending_requests'], 10)
        self.assertEqual(response.data['approved_requests'], 25)
        self.assertEqual(response.data['disbursed_requests'], 50)
        self.assertEqual(response.data['cancelled_requests'], 5)
        self.assertEqual(response.data['pending_stipulations'], 15)
        
        # Verify all mocks were called
        mock_pending.assert_called_once()
        mock_approved.assert_called_once()
        mock_disbursed.assert_called_once()
        mock_cancelled.assert_called_once()
        mock_pending_stipulations.assert_called_once()
    
    def test_get_funding_dashboard_unauthorized(self):
        """Test that non-staff users cannot get the funding dashboard data"""
        # Authenticate as borrower
        self.client.force_authenticate(user=self.borrower_user)
        
        # Make GET request
        response = self.client.get(self.url)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)