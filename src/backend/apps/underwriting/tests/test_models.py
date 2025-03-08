from django.test import TestCase
from unittest.mock import mock, patch
from django.utils import timezone
from decimal import Decimal

from apps.underwriting.models import (
    UnderwritingQueue, CreditInformation, UnderwritingDecision,
    DecisionReason, Stipulation, UnderwritingNote, UnderwritingQueueManager
)
from apps.applications.models import LoanApplication
from apps.underwriting.constants import (
    UNDERWRITING_QUEUE_PRIORITY, UNDERWRITING_QUEUE_STATUS,
    CREDIT_SCORE_TIERS, DECISION_REASON_CODES, UNDERWRITING_DECISION_TRANSITIONS
)
from utils.constants import (
    UNDERWRITING_DECISION, STIPULATION_TYPES, STIPULATION_STATUS, APPLICATION_STATUS
)


class TestUnderwritingQueueManager(TestCase):
    """Test case for the UnderwritingQueueManager class"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test users for borrowers and underwriters
        from apps.users.models import User
        self.borrower = User.objects.create(
            email="borrower@example.com",
            first_name="John",
            last_name="Borrower"
        )
        
        self.underwriter1 = User.objects.create(
            email="underwriter1@example.com",
            first_name="Alice",
            last_name="Underwriter"
        )
        
        self.underwriter2 = User.objects.create(
            email="underwriter2@example.com",
            first_name="Bob",
            last_name="Reviewer"
        )
        
        # Create test school and program
        from apps.schools.models import School, Program, ProgramVersion
        self.school = School.objects.create(
            name="Test School",
            legal_name="Test School Inc.",
            tax_id="12-3456789",
            address_line1="123 Education St",
            city="Testville",
            state="TX",
            zip_code="12345",
            phone="(555) 123-4567"
        )
        
        self.program = Program.objects.create(
            school=self.school,
            name="Test Program",
            description="A test program",
            duration_hours=500,
            duration_weeks=20
        )
        
        self.program_version = ProgramVersion.objects.create(
            program=self.program,
            version_number=1,
            effective_date=timezone.now().date(),
            tuition_amount=Decimal("10000.00"),
            is_current=True
        )
        
        # Create test loan applications
        self.application1 = LoanApplication.objects.create(
            borrower=self.borrower,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            status=APPLICATION_STATUS["SUBMITTED"]
        )
        
        self.application2 = LoanApplication.objects.create(
            borrower=self.borrower,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            status=APPLICATION_STATUS["SUBMITTED"]
        )
        
        # Create test underwriting queue items with different statuses and priorities
        self.queue_item1 = UnderwritingQueue.objects.create(
            application=self.application1,
            status=UNDERWRITING_QUEUE_STATUS["PENDING"],
            priority=UNDERWRITING_QUEUE_PRIORITY["HIGH"]
        )
        
        self.queue_item2 = UnderwritingQueue.objects.create(
            application=self.application2,
            status=UNDERWRITING_QUEUE_STATUS["ASSIGNED"],
            assigned_to=self.underwriter1,
            priority=UNDERWRITING_QUEUE_PRIORITY["MEDIUM"]
        )
        
        # Add more queue items with different statuses for testing the manager methods
        self.application3 = LoanApplication.objects.create(
            borrower=self.borrower,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            status=APPLICATION_STATUS["IN_REVIEW"]
        )
        
        self.queue_item3 = UnderwritingQueue.objects.create(
            application=self.application3,
            status=UNDERWRITING_QUEUE_STATUS["IN_PROGRESS"],
            assigned_to=self.underwriter1,
            priority=UNDERWRITING_QUEUE_PRIORITY["MEDIUM"]
        )
        
        # Add a queue item with different underwriter
        self.application4 = LoanApplication.objects.create(
            borrower=self.borrower,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            status=APPLICATION_STATUS["IN_REVIEW"]
        )
        
        self.queue_item4 = UnderwritingQueue.objects.create(
            application=self.application4,
            status=UNDERWRITING_QUEUE_STATUS["ASSIGNED"],
            assigned_to=self.underwriter2,
            priority=UNDERWRITING_QUEUE_PRIORITY["LOW"]
        )
        
        # Add a completed item
        self.application5 = LoanApplication.objects.create(
            borrower=self.borrower,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            status=APPLICATION_STATUS["APPROVED"]
        )
        
        self.queue_item5 = UnderwritingQueue.objects.create(
            application=self.application5,
            status=UNDERWRITING_QUEUE_STATUS["COMPLETED"],
            assigned_to=self.underwriter1,
            priority=UNDERWRITING_QUEUE_PRIORITY["HIGH"]
        )

    def test_get_by_status(self):
        """Test that get_by_status returns queue items with the specified status"""
        pending_items = UnderwritingQueue.objects.get_by_status(UNDERWRITING_QUEUE_STATUS["PENDING"])
        self.assertEqual(pending_items.count(), 1)
        self.assertEqual(pending_items.first(), self.queue_item1)
        
        assigned_items = UnderwritingQueue.objects.get_by_status(UNDERWRITING_QUEUE_STATUS["ASSIGNED"])
        self.assertEqual(assigned_items.count(), 2)
        self.assertIn(self.queue_item2, assigned_items)
        self.assertIn(self.queue_item4, assigned_items)

    def test_get_by_underwriter(self):
        """Test that get_by_underwriter returns queue items assigned to a specific underwriter"""
        underwriter1_items = UnderwritingQueue.objects.get_by_underwriter(self.underwriter1)
        self.assertEqual(underwriter1_items.count(), 3)  # queue_item2, queue_item3, queue_item5
        self.assertIn(self.queue_item2, underwriter1_items)
        self.assertIn(self.queue_item3, underwriter1_items)
        self.assertIn(self.queue_item5, underwriter1_items)
        
        underwriter2_items = UnderwritingQueue.objects.get_by_underwriter(self.underwriter2)
        self.assertEqual(underwriter2_items.count(), 1)
        self.assertEqual(underwriter2_items.first(), self.queue_item4)

    def test_get_pending(self):
        """Test that get_pending returns queue items with pending status"""
        pending_items = UnderwritingQueue.objects.get_pending()
        self.assertEqual(pending_items.count(), 1)
        self.assertEqual(pending_items.first(), self.queue_item1)

    def test_get_by_priority(self):
        """Test that get_by_priority returns queue items with the specified priority"""
        high_priority_items = UnderwritingQueue.objects.get_by_priority(UNDERWRITING_QUEUE_PRIORITY["HIGH"])
        self.assertEqual(high_priority_items.count(), 2)
        self.assertIn(self.queue_item1, high_priority_items)
        self.assertIn(self.queue_item5, high_priority_items)
        
        medium_priority_items = UnderwritingQueue.objects.get_by_priority(UNDERWRITING_QUEUE_PRIORITY["MEDIUM"])
        self.assertEqual(medium_priority_items.count(), 2)
        self.assertIn(self.queue_item2, medium_priority_items)
        self.assertIn(self.queue_item3, medium_priority_items)

    def test_get_overdue(self):
        """Test that get_overdue returns queue items that are past their due date"""
        # Create queue items with past due dates
        past_date = timezone.now() - timezone.timedelta(days=1)
        
        self.queue_item1.due_date = past_date
        self.queue_item1.save()
        
        self.queue_item2.due_date = past_date
        self.queue_item2.save()
        
        # Create queue items with future due dates
        future_date = timezone.now() + timezone.timedelta(days=1)
        
        self.queue_item3.due_date = future_date
        self.queue_item3.save()
        
        self.queue_item4.due_date = future_date
        self.queue_item4.save()
        
        # The completed item should not be returned even if it's past due
        self.queue_item5.due_date = past_date
        self.queue_item5.save()
        
        overdue_items = UnderwritingQueue.objects.get_overdue()
        self.assertEqual(overdue_items.count(), 2)
        self.assertIn(self.queue_item1, overdue_items)
        self.assertIn(self.queue_item2, overdue_items)
        self.assertNotIn(self.queue_item3, overdue_items)
        self.assertNotIn(self.queue_item4, overdue_items)
        self.assertNotIn(self.queue_item5, overdue_items)  # Should not be included as it's completed


class TestUnderwritingQueue(TestCase):
    """Test case for the UnderwritingQueue model"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test users for borrowers and underwriters
        from apps.users.models import User
        self.borrower = User.objects.create(
            email="borrower@example.com",
            first_name="John",
            last_name="Borrower"
        )
        
        self.underwriter = User.objects.create(
            email="underwriter@example.com",
            first_name="Alice",
            last_name="Underwriter"
        )
        
        # Create test school and program
        from apps.schools.models import School, Program, ProgramVersion
        self.school = School.objects.create(
            name="Test School",
            legal_name="Test School Inc.",
            tax_id="12-3456789",
            address_line1="123 Education St",
            city="Testville",
            state="TX",
            zip_code="12345",
            phone="(555) 123-4567"
        )
        
        self.program = Program.objects.create(
            school=self.school,
            name="Test Program",
            description="A test program",
            duration_hours=500,
            duration_weeks=20
        )
        
        self.program_version = ProgramVersion.objects.create(
            program=self.program,
            version_number=1,
            effective_date=timezone.now().date(),
            tuition_amount=Decimal("10000.00"),
            is_current=True
        )
        
        # Create test loan application
        self.application = LoanApplication.objects.create(
            borrower=self.borrower,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            status=APPLICATION_STATUS["SUBMITTED"]
        )
        
        # Create test underwriting queue item
        self.queue_item = UnderwritingQueue.objects.create(
            application=self.application,
            status=UNDERWRITING_QUEUE_STATUS["PENDING"],
            priority=UNDERWRITING_QUEUE_PRIORITY["MEDIUM"]
        )

    def test_save_new_queue_item(self):
        """Test that saving a new queue item sets default values correctly"""
        # Create a new queue item without setting status
        new_application = LoanApplication.objects.create(
            borrower=self.borrower,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            status=APPLICATION_STATUS["SUBMITTED"]
        )
        
        new_queue_item = UnderwritingQueue(application=new_application)
        new_queue_item.save()
        
        # Assert default values are set
        self.assertEqual(new_queue_item.status, UNDERWRITING_QUEUE_STATUS["PENDING"])
        self.assertIsNotNone(new_queue_item.due_date)
        
        # Create a new queue item with assigned_to but no assignment_date
        another_queue_item = UnderwritingQueue(
            application=new_application,
            assigned_to=self.underwriter
        )
        another_queue_item.save()
        
        # Assignment date should be set automatically
        self.assertIsNotNone(another_queue_item.assignment_date)
        
        # Create a new queue item with priority but no due_date
        priority_queue_item = UnderwritingQueue(
            application=new_application,
            priority=UNDERWRITING_QUEUE_PRIORITY["HIGH"]
        )
        priority_queue_item.save()
        
        # Due date should be calculated based on priority
        self.assertIsNotNone(priority_queue_item.due_date)
        # High priority should have shorter due date than medium priority
        self.assertLess(
            priority_queue_item.due_date,
            new_queue_item.due_date
        )

    def test_assign(self):
        """Test that assign method correctly assigns the queue item to an underwriter"""
        self.assertIsNone(self.queue_item.assigned_to)
        self.assertIsNone(self.queue_item.assignment_date)
        
        # Assign the queue item
        result = self.queue_item.assign(self.underwriter)
        
        # Reload from database to get updated values
        self.queue_item.refresh_from_db()
        
        # Assert changes were made
        self.assertTrue(result)
        self.assertEqual(self.queue_item.assigned_to, self.underwriter)
        self.assertIsNotNone(self.queue_item.assignment_date)
        self.assertEqual(self.queue_item.status, UNDERWRITING_QUEUE_STATUS["ASSIGNED"])
        
        # Test assigning an already assigned item (should fail)
        from apps.users.models import User
        another_underwriter = User.objects.create(
            email="another@example.com",
            first_name="Another",
            last_name="Underwriter"
        )
        
        result = self.queue_item.assign(another_underwriter)
        self.assertFalse(result)  # Should return False as it's already assigned

    def test_start_review(self):
        """Test that start_review method correctly updates the status"""
        # First assign the queue item
        self.queue_item.assign(self.underwriter)
        
        # Start the review
        result = self.queue_item.start_review()
        
        # Reload from database
        self.queue_item.refresh_from_db()
        
        # Assert status is updated
        self.assertTrue(result)
        self.assertEqual(self.queue_item.status, UNDERWRITING_QUEUE_STATUS["IN_PROGRESS"])
        
        # Test start_review on an unassigned item (should fail)
        unassigned_queue_item = UnderwritingQueue.objects.create(
            application=self.application,
            status=UNDERWRITING_QUEUE_STATUS["PENDING"]
        )
        
        result = unassigned_queue_item.start_review()
        self.assertFalse(result)  # Should return False as it's not assigned

    def test_complete(self):
        """Test that complete method correctly updates the status"""
        # First assign the queue item and start review
        self.queue_item.assign(self.underwriter)
        self.queue_item.start_review()
        
        # Complete the review
        result = self.queue_item.complete()
        
        # Reload from database
        self.queue_item.refresh_from_db()
        
        # Assert status is updated
        self.assertTrue(result)
        self.assertEqual(self.queue_item.status, UNDERWRITING_QUEUE_STATUS["COMPLETED"])
        
        # Test complete on an item not in progress (should fail)
        not_in_progress = UnderwritingQueue.objects.create(
            application=self.application,
            status=UNDERWRITING_QUEUE_STATUS["ASSIGNED"],
            assigned_to=self.underwriter
        )
        
        result = not_in_progress.complete()
        self.assertFalse(result)  # Should return False as it's not in progress

    def test_return_to_queue(self):
        """Test that return_to_queue method correctly resets the queue item"""
        # First assign the queue item
        self.queue_item.assign(self.underwriter)
        
        # Return to queue
        result = self.queue_item.return_to_queue()
        
        # Reload from database
        self.queue_item.refresh_from_db()
        
        # Assert the item is reset
        self.assertTrue(result)
        self.assertEqual(self.queue_item.status, UNDERWRITING_QUEUE_STATUS["RETURNED"])
        self.assertIsNone(self.queue_item.assigned_to)
        self.assertIsNone(self.queue_item.assignment_date)

    def test_is_overdue(self):
        """Test that is_overdue method correctly identifies overdue items"""
        # Create a queue item with a past due date and not COMPLETED status
        past_date = timezone.now() - timezone.timedelta(days=1)
        
        overdue_item = UnderwritingQueue.objects.create(
            application=self.application,
            due_date=past_date,
            status=UNDERWRITING_QUEUE_STATUS["PENDING"]
        )
        
        self.assertTrue(overdue_item.is_overdue())
        
        # Create a queue item with a future due date
        future_date = timezone.now() + timezone.timedelta(days=1)
        
        not_overdue_item = UnderwritingQueue.objects.create(
            application=self.application,
            due_date=future_date,
            status=UNDERWRITING_QUEUE_STATUS["PENDING"]
        )
        
        self.assertFalse(not_overdue_item.is_overdue())
        
        # Create a queue item with a past due date but COMPLETED status
        completed_item = UnderwritingQueue.objects.create(
            application=self.application,
            due_date=past_date,
            status=UNDERWRITING_QUEUE_STATUS["COMPLETED"]
        )
        
        self.assertFalse(completed_item.is_overdue())  # Should not be overdue as it's completed

    def test_str_method(self):
        """Test the string representation of UnderwritingQueue"""
        expected_str = f"Application {self.application.id} - {self.queue_item.status} (Priority: {self.queue_item.priority})"
        self.assertEqual(str(self.queue_item), expected_str)


class TestCreditInformation(TestCase):
    """Test case for the CreditInformation model"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test users for borrowers and staff
        from apps.users.models import User
        self.borrower = User.objects.create(
            email="borrower@example.com",
            first_name="John",
            last_name="Borrower"
        )
        
        self.staff = User.objects.create(
            email="staff@example.com",
            first_name="Staff",
            last_name="Member"
        )
        
        # Create test school and program
        from apps.schools.models import School, Program, ProgramVersion
        self.school = School.objects.create(
            name="Test School",
            legal_name="Test School Inc.",
            tax_id="12-3456789",
            address_line1="123 Education St",
            city="Testville",
            state="TX",
            zip_code="12345",
            phone="(555) 123-4567"
        )
        
        self.program = Program.objects.create(
            school=self.school,
            name="Test Program",
            description="A test program",
            duration_hours=500,
            duration_weeks=20
        )
        
        self.program_version = ProgramVersion.objects.create(
            program=self.program,
            version_number=1,
            effective_date=timezone.now().date(),
            tuition_amount=Decimal("10000.00"),
            is_current=True
        )
        
        # Create test loan application
        self.application = LoanApplication.objects.create(
            borrower=self.borrower,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            status=APPLICATION_STATUS["SUBMITTED"]
        )
        
        # Create test credit information
        self.credit_info = CreditInformation.objects.create(
            application=self.application,
            borrower=self.borrower,
            is_co_borrower=False,
            credit_score=720,
            report_reference="CR12345",
            file_path="credit_reports/CR12345.pdf",
            uploaded_by=self.staff,
            monthly_debt=Decimal("1000.00"),
            debt_to_income_ratio=Decimal("0.25")
        )

    def test_save_method(self):
        """Test that save method sets default values correctly"""
        # Create a new credit info record without uploaded_at and report_date
        new_credit_info = CreditInformation(
            application=self.application,
            borrower=self.borrower,
            is_co_borrower=False,
            credit_score=680,
            report_reference="CR67890",
            file_path="credit_reports/CR67890.pdf",
            monthly_debt=Decimal("1200.00"),
            debt_to_income_ratio=Decimal("0.30")
        )
        
        # Save should set uploaded_at and report_date
        new_credit_info.save()
        
        self.assertIsNotNone(new_credit_info.uploaded_at)
        self.assertIsNotNone(new_credit_info.report_date)

    def test_get_credit_tier(self):
        """Test that get_credit_tier returns the correct tier based on credit score"""
        # Create credit information records with different credit scores
        excellent_credit = CreditInformation.objects.create(
            application=self.application,
            borrower=self.borrower,
            is_co_borrower=False,
            credit_score=780,  # Excellent: >= 750
            report_reference="CR-EXC",
            file_path="credit_reports/excellent.pdf",
            monthly_debt=Decimal("800.00"),
            debt_to_income_ratio=Decimal("0.20")
        )
        
        good_credit = CreditInformation.objects.create(
            application=self.application,
            borrower=self.borrower,
            is_co_borrower=False,
            credit_score=720,  # Good: >= 700 and < 750
            report_reference="CR-GOOD",
            file_path="credit_reports/good.pdf",
            monthly_debt=Decimal("1000.00"),
            debt_to_income_ratio=Decimal("0.25")
        )
        
        fair_credit = CreditInformation.objects.create(
            application=self.application,
            borrower=self.borrower,
            is_co_borrower=False,
            credit_score=670,  # Fair: >= 650 and < 700
            report_reference="CR-FAIR",
            file_path="credit_reports/fair.pdf",
            monthly_debt=Decimal("1200.00"),
            debt_to_income_ratio=Decimal("0.30")
        )
        
        poor_credit = CreditInformation.objects.create(
            application=self.application,
            borrower=self.borrower,
            is_co_borrower=False,
            credit_score=620,  # Poor: >= 600 and < 650
            report_reference="CR-POOR",
            file_path="credit_reports/poor.pdf",
            monthly_debt=Decimal("1500.00"),
            debt_to_income_ratio=Decimal("0.38")
        )
        
        bad_credit = CreditInformation.objects.create(
            application=self.application,
            borrower=self.borrower,
            is_co_borrower=False,
            credit_score=580,  # Bad: < 600
            report_reference="CR-BAD",
            file_path="credit_reports/bad.pdf",
            monthly_debt=Decimal("1800.00"),
            debt_to_income_ratio=Decimal("0.45")
        )
        
        # Test credit tier classification
        self.assertEqual(excellent_credit.get_credit_tier(), "EXCELLENT")
        self.assertEqual(good_credit.get_credit_tier(), "GOOD")
        self.assertEqual(fair_credit.get_credit_tier(), "FAIR")
        self.assertEqual(poor_credit.get_credit_tier(), "POOR")
        self.assertEqual(bad_credit.get_credit_tier(), "BAD")

    def test_calculate_dti(self):
        """Test that calculate_dti correctly calculates debt-to-income ratio"""
        # Create a credit information record with monthly_debt = 1000
        credit_info = CreditInformation.objects.create(
            application=self.application,
            borrower=self.borrower,
            is_co_borrower=False,
            credit_score=700,
            report_reference="CR-DTI-TEST",
            file_path="credit_reports/dti_test.pdf",
            monthly_debt=Decimal("1000.00"),
            debt_to_income_ratio=Decimal("0.25")
        )
        
        # Calculate DTI with monthly_income = 4000
        self.assertEqual(credit_info.calculate_dti(Decimal("4000.00")), Decimal("0.25"))
        
        # Calculate DTI with monthly_income = 2000
        self.assertEqual(credit_info.calculate_dti(Decimal("2000.00")), Decimal("0.5"))

    @patch('utils.storage.get_presigned_url')
    def test_get_download_url(self, mock_get_presigned_url):
        """Test that get_download_url generates a presigned URL for the credit report"""
        # Setup mock
        mock_get_presigned_url.return_value = "https://example.com/presigned-url"
        
        # Call the method
        url = self.credit_info.get_download_url(expiry_seconds=3600)
        
        # Assert the mock was called correctly
        mock_get_presigned_url.assert_called_once_with(self.credit_info.file_path, 3600)
        
        # Assert the method returns the expected URL
        self.assertEqual(url, "https://example.com/presigned-url")

    def test_str_method(self):
        """Test the string representation of CreditInformation"""
        expected_str = f"Borrower {self.borrower.first_name} {self.borrower.last_name} - Score: {self.credit_info.credit_score}"
        self.assertEqual(str(self.credit_info), expected_str)
        
        # Test with co-borrower
        co_borrower_credit = CreditInformation.objects.create(
            application=self.application,
            borrower=self.borrower,
            is_co_borrower=True,
            credit_score=710,
            report_reference="CR-CO",
            file_path="credit_reports/co_borrower.pdf",
            monthly_debt=Decimal("900.00"),
            debt_to_income_ratio=Decimal("0.23")
        )
        
        expected_co_str = f"Co-borrower {self.borrower.first_name} {self.borrower.last_name} - Score: 710"
        self.assertEqual(str(co_borrower_credit), expected_co_str)


class TestUnderwritingDecision(TestCase):
    """Test case for the UnderwritingDecision model"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test users for borrowers and underwriters
        from apps.users.models import User
        self.borrower = User.objects.create(
            email="borrower@example.com",
            first_name="John",
            last_name="Borrower"
        )
        
        self.underwriter = User.objects.create(
            email="underwriter@example.com",
            first_name="Alice",
            last_name="Underwriter"
        )
        
        # Create test school and program
        from apps.schools.models import School, Program, ProgramVersion
        self.school = School.objects.create(
            name="Test School",
            legal_name="Test School Inc.",
            tax_id="12-3456789",
            address_line1="123 Education St",
            city="Testville",
            state="TX",
            zip_code="12345",
            phone="(555) 123-4567"
        )
        
        self.program = Program.objects.create(
            school=self.school,
            name="Test Program",
            description="A test program",
            duration_hours=500,
            duration_weeks=20
        )
        
        self.program_version = ProgramVersion.objects.create(
            program=self.program,
            version_number=1,
            effective_date=timezone.now().date(),
            tuition_amount=Decimal("10000.00"),
            is_current=True
        )
        
        # Create test loan application
        self.application = LoanApplication.objects.create(
            borrower=self.borrower,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            status=APPLICATION_STATUS["IN_REVIEW"]
        )
        
        # Create test underwriting decision
        self.decision = UnderwritingDecision.objects.create(
            application=self.application,
            decision=UNDERWRITING_DECISION["APPROVE"],
            underwriter=self.underwriter,
            approved_amount=Decimal("10000.00"),
            interest_rate=Decimal("5.25"),
            term_months=36,
            comments="Approved based on good credit history"
        )

    def test_save_method(self):
        """Test that save method sets default values and updates application status"""
        # Create a new decision without decision_date
        new_application = LoanApplication.objects.create(
            borrower=self.borrower,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            status=APPLICATION_STATUS["IN_REVIEW"]
        )
        
        # Mock the update_application_status method
        with patch.object(UnderwritingDecision, 'update_application_status') as mock_update:
            new_decision = UnderwritingDecision(
                application=new_application,
                decision=UNDERWRITING_DECISION["APPROVE"],
                underwriter=self.underwriter,
                approved_amount=Decimal("10000.00"),
                interest_rate=Decimal("5.25"),
                term_months=36
            )
            
            new_decision.save()
            
            # Assert decision_date is set automatically
            self.assertIsNotNone(new_decision.decision_date)
            
            # Assert update_application_status was called
            mock_update.assert_called_once()

    def test_update_application_status(self):
        """Test that update_application_status correctly updates the application status"""
        # Create applications and decisions with different decision types
        approve_app = LoanApplication.objects.create(
            borrower=self.borrower,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            status=APPLICATION_STATUS["IN_REVIEW"]
        )
        
        deny_app = LoanApplication.objects.create(
            borrower=self.borrower,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            status=APPLICATION_STATUS["IN_REVIEW"]
        )
        
        revise_app = LoanApplication.objects.create(
            borrower=self.borrower,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            status=APPLICATION_STATUS["IN_REVIEW"]
        )
        
        # Create decisions
        approve_decision = UnderwritingDecision.objects.create(
            application=approve_app,
            decision=UNDERWRITING_DECISION["APPROVE"],
            underwriter=self.underwriter
        )
        
        deny_decision = UnderwritingDecision.objects.create(
            application=deny_app,
            decision=UNDERWRITING_DECISION["DENY"],
            underwriter=self.underwriter
        )
        
        revise_decision = UnderwritingDecision.objects.create(
            application=revise_app,
            decision=UNDERWRITING_DECISION["REVISE"],
            underwriter=self.underwriter
        )
        
        # Call update_application_status for each decision
        approve_result = approve_decision.update_application_status()
        deny_result = deny_decision.update_application_status()
        revise_result = revise_decision.update_application_status()
        
        # Refresh applications
        approve_app.refresh_from_db()
        deny_app.refresh_from_db()
        revise_app.refresh_from_db()
        
        # Assert application statuses were updated according to UNDERWRITING_DECISION_TRANSITIONS
        self.assertEqual(approve_app.status, APPLICATION_STATUS["APPROVED"])
        self.assertEqual(deny_app.status, APPLICATION_STATUS["DENIED"])
        self.assertEqual(revise_app.status, APPLICATION_STATUS["REVISION_REQUESTED"])
        
        # Assert the method returns True for successful updates
        self.assertTrue(approve_result)
        self.assertTrue(deny_result)
        self.assertTrue(revise_result)

    def test_get_reasons(self):
        """Test that get_reasons returns the decision reasons associated with the decision"""
        # Create decision reasons
        reason1 = DecisionReason.objects.create(
            decision=self.decision,
            reason_code=DECISION_REASON_CODES["CREDIT_SCORE"],
            is_primary=True
        )
        
        reason2 = DecisionReason.objects.create(
            decision=self.decision,
            reason_code=DECISION_REASON_CODES["EMPLOYMENT_HISTORY"],
            is_primary=False
        )
        
        # Get reasons
        reasons = self.decision.get_reasons()
        
        # Assert all reasons are returned
        self.assertEqual(reasons.count(), 2)
        self.assertIn(reason1, reasons)
        self.assertIn(reason2, reasons)

    def test_get_stipulations(self):
        """Test that get_stipulations returns the stipulations associated with the application"""
        # Create stipulations
        stipulation1 = Stipulation.objects.create(
            application=self.application,
            stipulation_type=STIPULATION_TYPES["ENROLLMENT_AGREEMENT"],
            description="Enrollment agreement required",
            required_by_date=timezone.now().date() + timezone.timedelta(days=30),
            status=STIPULATION_STATUS["PENDING"],
            created_by=self.underwriter
        )
        
        stipulation2 = Stipulation.objects.create(
            application=self.application,
            stipulation_type=STIPULATION_TYPES["PROOF_OF_INCOME"],
            description="Recent pay stubs required",
            required_by_date=timezone.now().date() + timezone.timedelta(days=30),
            status=STIPULATION_STATUS["PENDING"],
            created_by=self.underwriter
        )
        
        # Get stipulations
        stipulations = self.decision.get_stipulations()
        
        # Assert all stipulations are returned
        self.assertEqual(stipulations.count(), 2)
        self.assertIn(stipulation1, stipulations)
        self.assertIn(stipulation2, stipulations)

    def test_is_approved(self):
        """Test that is_approved correctly identifies approved decisions"""
        # Create a decision with decision = APPROVE
        approve_decision = UnderwritingDecision.objects.create(
            application=self.application,
            decision=UNDERWRITING_DECISION["APPROVE"],
            underwriter=self.underwriter
        )
        self.assertTrue(approve_decision.is_approved())
        
        # Create a decision with decision = DENY
        deny_decision = UnderwritingDecision.objects.create(
            application=self.application,
            decision=UNDERWRITING_DECISION["DENY"],
            underwriter=self.underwriter
        )
        self.assertFalse(deny_decision.is_approved())
        
        # Create a decision with decision = REVISE
        revise_decision = UnderwritingDecision.objects.create(
            application=self.application,
            decision=UNDERWRITING_DECISION["REVISE"],
            underwriter=self.underwriter
        )
        self.assertFalse(revise_decision.is_approved())

    def test_is_denied(self):
        """Test that is_denied correctly identifies denied decisions"""
        # Create a decision with decision = DENY
        deny_decision = UnderwritingDecision.objects.create(
            application=self.application,
            decision=UNDERWRITING_DECISION["DENY"],
            underwriter=self.underwriter
        )
        self.assertTrue(deny_decision.is_denied())
        
        # Create a decision with decision = APPROVE
        approve_decision = UnderwritingDecision.objects.create(
            application=self.application,
            decision=UNDERWRITING_DECISION["APPROVE"],
            underwriter=self.underwriter
        )
        self.assertFalse(approve_decision.is_denied())
        
        # Create a decision with decision = REVISE
        revise_decision = UnderwritingDecision.objects.create(
            application=self.application,
            decision=UNDERWRITING_DECISION["REVISE"],
            underwriter=self.underwriter
        )
        self.assertFalse(revise_decision.is_denied())

    def test_is_revision_requested(self):
        """Test that is_revision_requested correctly identifies revision requests"""
        # Create a decision with decision = REVISE
        revise_decision = UnderwritingDecision.objects.create(
            application=self.application,
            decision=UNDERWRITING_DECISION["REVISE"],
            underwriter=self.underwriter
        )
        self.assertTrue(revise_decision.is_revision_requested())
        
        # Create a decision with decision = APPROVE
        approve_decision = UnderwritingDecision.objects.create(
            application=self.application,
            decision=UNDERWRITING_DECISION["APPROVE"],
            underwriter=self.underwriter
        )
        self.assertFalse(approve_decision.is_revision_requested())
        
        # Create a decision with decision = DENY
        deny_decision = UnderwritingDecision.objects.create(
            application=self.application,
            decision=UNDERWRITING_DECISION["DENY"],
            underwriter=self.underwriter
        )
        self.assertFalse(deny_decision.is_revision_requested())

    def test_str_method(self):
        """Test the string representation of UnderwritingDecision"""
        expected_str = f"Application {self.application.id} - {self.decision.get_decision_display()}"
        self.assertEqual(str(self.decision), expected_str)


class TestDecisionReason(TestCase):
    """Test case for the DecisionReason model"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test users for borrowers and underwriters
        from apps.users.models import User
        self.borrower = User.objects.create(
            email="borrower@example.com",
            first_name="John",
            last_name="Borrower"
        )
        
        self.underwriter = User.objects.create(
            email="underwriter@example.com",
            first_name="Alice",
            last_name="Underwriter"
        )
        
        # Create test school and program
        from apps.schools.models import School, Program, ProgramVersion
        self.school = School.objects.create(
            name="Test School",
            legal_name="Test School Inc.",
            tax_id="12-3456789",
            address_line1="123 Education St",
            city="Testville",
            state="TX",
            zip_code="12345",
            phone="(555) 123-4567"
        )
        
        self.program = Program.objects.create(
            school=self.school,
            name="Test Program",
            description="A test program",
            duration_hours=500,
            duration_weeks=20
        )
        
        self.program_version = ProgramVersion.objects.create(
            program=self.program,
            version_number=1,
            effective_date=timezone.now().date(),
            tuition_amount=Decimal("10000.00"),
            is_current=True
        )
        
        # Create test loan application
        self.application = LoanApplication.objects.create(
            borrower=self.borrower,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            status=APPLICATION_STATUS["IN_REVIEW"]
        )
        
        # Create test underwriting decision
        self.decision = UnderwritingDecision.objects.create(
            application=self.application,
            decision=UNDERWRITING_DECISION["DENY"],
            underwriter=self.underwriter
        )
        
        # Create test decision reason
        self.reason = DecisionReason.objects.create(
            decision=self.decision,
            reason_code=DECISION_REASON_CODES["CREDIT_SCORE"],
            description="Credit score below required threshold",
            is_primary=True
        )

    def test_save_method(self):
        """Test that save method sets description from reason code if not provided"""
        # Create a new reason with reason_code but no description
        new_reason = DecisionReason(
            decision=self.decision,
            reason_code=DECISION_REASON_CODES["DEBT_TO_INCOME"],
            is_primary=False
        )
        
        new_reason.save()
        
        # Description should be set from DECISION_REASON_DESCRIPTIONS based on reason_code
        from apps.underwriting.constants import DECISION_REASON_DESCRIPTIONS
        expected_description = DECISION_REASON_DESCRIPTIONS[DECISION_REASON_CODES["DEBT_TO_INCOME"]]
        self.assertEqual(new_reason.description, expected_description)

    def test_str_method(self):
        """Test the string representation of DecisionReason"""
        expected_str = f"{self.reason.get_reason_code_display()} (Primary) - {self.reason.description[:50]}"
        self.assertEqual(str(self.reason), expected_str)
        
        # Test with non-primary reason
        non_primary = DecisionReason.objects.create(
            decision=self.decision,
            reason_code=DECISION_REASON_CODES["EMPLOYMENT_HISTORY"],
            description="Insufficient employment history",
            is_primary=False
        )
        
        expected_non_primary_str = f"{non_primary.get_reason_code_display()} - {non_primary.description[:50]}"
        self.assertEqual(str(non_primary), expected_non_primary_str)


class TestStipulation(TestCase):
    """Test case for the Stipulation model"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test users for borrowers and staff
        from apps.users.models import User
        self.borrower = User.objects.create(
            email="borrower@example.com",
            first_name="John",
            last_name="Borrower"
        )
        
        self.staff = User.objects.create(
            email="staff@example.com",
            first_name="Staff",
            last_name="Member"
        )
        
        # Create test school and program
        from apps.schools.models import School, Program, ProgramVersion
        self.school = School.objects.create(
            name="Test School",
            legal_name="Test School Inc.",
            tax_id="12-3456789",
            address_line1="123 Education St",
            city="Testville",
            state="TX",
            zip_code="12345",
            phone="(555) 123-4567"
        )
        
        self.program = Program.objects.create(
            school=self.school,
            name="Test Program",
            description="A test program",
            duration_hours=500,
            duration_weeks=20
        )
        
        self.program_version = ProgramVersion.objects.create(
            program=self.program,
            version_number=1,
            effective_date=timezone.now().date(),
            tuition_amount=Decimal("10000.00"),
            is_current=True
        )
        
        # Create test loan application
        self.application = LoanApplication.objects.create(
            borrower=self.borrower,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            status=APPLICATION_STATUS["APPROVED"]
        )
        
        # Create test stipulation
        self.stipulation = Stipulation.objects.create(
            application=self.application,
            stipulation_type=STIPULATION_TYPES["ENROLLMENT_AGREEMENT"],
            description="Enrollment agreement required",
            required_by_date=timezone.now().date() + timezone.timedelta(days=30),
            status=STIPULATION_STATUS["PENDING"],
            created_by=self.staff
        )

    def test_save_method(self):
        """Test that save method sets created_at and status if not provided"""
        # Create a new stipulation without created_at and status
        future_date = timezone.now().date() + timezone.timedelta(days=30)
        
        new_stipulation = Stipulation(
            application=self.application,
            stipulation_type=STIPULATION_TYPES["PROOF_OF_INCOME"],
            description="Recent pay stubs required",
            required_by_date=future_date,
            created_by=self.staff
        )
        
        # Save the stipulation
        new_stipulation.save()
        
        # created_at should be set automatically
        self.assertIsNotNone(new_stipulation.created_at)
        
        # status should default to PENDING if not provided
        self.assertEqual(new_stipulation.status, STIPULATION_STATUS["PENDING"])

    def test_satisfy(self):
        """Test that satisfy method correctly marks a stipulation as satisfied"""
        # Create a stipulation with PENDING status
        self.assertEqual(self.stipulation.status, STIPULATION_STATUS["PENDING"])
        self.assertIsNone(self.stipulation.satisfied_at)
        self.assertIsNone(self.stipulation.satisfied_by)
        
        # Satisfy the stipulation with a user
        result = self.stipulation.satisfy(self.borrower)
        
        # Reload from database
        self.stipulation.refresh_from_db()
        
        # Assert status is changed to SATISFIED
        self.assertTrue(result)
        self.assertEqual(self.stipulation.status, STIPULATION_STATUS["SATISFIED"])
        self.assertIsNotNone(self.stipulation.satisfied_at)
        self.assertEqual(self.stipulation.satisfied_by, self.borrower)

    def test_is_satisfied(self):
        """Test that is_satisfied correctly identifies satisfied stipulations"""
        # Create a stipulation with status = SATISFIED
        satisfied = Stipulation.objects.create(
            application=self.application,
            stipulation_type=STIPULATION_TYPES["PROOF_OF_INCOME"],
            description="Recent pay stubs required",
            required_by_date=timezone.now().date() + timezone.timedelta(days=30),
            status=STIPULATION_STATUS["SATISFIED"],
            created_by=self.staff,
            satisfied_at=timezone.now(),
            satisfied_by=self.borrower
        )
        self.assertTrue(satisfied.is_satisfied())
        
        # Create a stipulation with status = PENDING
        pending = Stipulation.objects.create(
            application=self.application,
            stipulation_type=STIPULATION_TYPES["PROOF_OF_INCOME"],
            description="Recent pay stubs required",
            required_by_date=timezone.now().date() + timezone.timedelta(days=30),
            status=STIPULATION_STATUS["PENDING"],
            created_by=self.staff
        )
        self.assertFalse(pending.is_satisfied())
        
        # Create a stipulation with status = WAIVED
        waived = Stipulation.objects.create(
            application=self.application,
            stipulation_type=STIPULATION_TYPES["ADDITIONAL_DOCUMENTATION"],
            description="Some additional document",
            required_by_date=timezone.now().date() + timezone.timedelta(days=30),
            status=STIPULATION_STATUS["WAIVED"],
            created_by=self.staff
        )
        self.assertFalse(waived.is_satisfied())

    def test_is_pending(self):
        """Test that is_pending correctly identifies pending stipulations"""
        # Create a stipulation with status = PENDING
        pending = Stipulation.objects.create(
            application=self.application,
            stipulation_type=STIPULATION_TYPES["PROOF_OF_INCOME"],
            description="Recent pay stubs required",
            required_by_date=timezone.now().date() + timezone.timedelta(days=30),
            status=STIPULATION_STATUS["PENDING"],
            created_by=self.staff
        )
        self.assertTrue(pending.is_pending())
        
        # Create a stipulation with status = SATISFIED
        satisfied = Stipulation.objects.create(
            application=self.application,
            stipulation_type=STIPULATION_TYPES["PROOF_OF_INCOME"],
            description="Recent pay stubs required",
            required_by_date=timezone.now().date() + timezone.timedelta(days=30),
            status=STIPULATION_STATUS["SATISFIED"],
            created_by=self.staff,
            satisfied_at=timezone.now(),
            satisfied_by=self.borrower
        )
        self.assertFalse(satisfied.is_pending())
        
        # Create a stipulation with status = WAIVED
        waived = Stipulation.objects.create(
            application=self.application,
            stipulation_type=STIPULATION_TYPES["ADDITIONAL_DOCUMENTATION"],
            description="Some additional document",
            required_by_date=timezone.now().date() + timezone.timedelta(days=30),
            status=STIPULATION_STATUS["WAIVED"],
            created_by=self.staff
        )
        self.assertFalse(waived.is_pending())

    def test_is_waived(self):
        """Test that is_waived correctly identifies waived stipulations"""
        # Create a stipulation with status = WAIVED
        waived = Stipulation.objects.create(
            application=self.application,
            stipulation_type=STIPULATION_TYPES["ADDITIONAL_DOCUMENTATION"],
            description="Some additional document",
            required_by_date=timezone.now().date() + timezone.timedelta(days=30),
            status=STIPULATION_STATUS["WAIVED"],
            created_by=self.staff
        )
        self.assertTrue(waived.is_waived())
        
        # Create a stipulation with status = SATISFIED
        satisfied = Stipulation.objects.create(
            application=self.application,
            stipulation_type=STIPULATION_TYPES["PROOF_OF_INCOME"],
            description="Recent pay stubs required",
            required_by_date=timezone.now().date() + timezone.timedelta(days=30),
            status=STIPULATION_STATUS["SATISFIED"],
            created_by=self.staff,
            satisfied_at=timezone.now(),
            satisfied_by=self.borrower
        )
        self.assertFalse(satisfied.is_waived())
        
        # Create a stipulation with status = PENDING
        pending = Stipulation.objects.create(
            application=self.application,
            stipulation_type=STIPULATION_TYPES["PROOF_OF_INCOME"],
            description="Recent pay stubs required",
            required_by_date=timezone.now().date() + timezone.timedelta(days=30),
            status=STIPULATION_STATUS["PENDING"],
            created_by=self.staff
        )
        self.assertFalse(pending.is_waived())

    def test_is_overdue(self):
        """Test that is_overdue correctly identifies overdue stipulations"""
        # Create a stipulation with a past required_by_date and PENDING status
        past_date = timezone.now().date() - timezone.timedelta(days=1)
        
        overdue = Stipulation.objects.create(
            application=self.application,
            stipulation_type=STIPULATION_TYPES["PROOF_OF_INCOME"],
            description="Recent pay stubs required",
            required_by_date=past_date,
            status=STIPULATION_STATUS["PENDING"],
            created_by=self.staff
        )
        self.assertTrue(overdue.is_overdue())
        
        # Create a stipulation with a future required_by_date
        future_date = timezone.now().date() + timezone.timedelta(days=1)
        
        not_overdue = Stipulation.objects.create(
            application=self.application,
            stipulation_type=STIPULATION_TYPES["PROOF_OF_INCOME"],
            description="Recent pay stubs required",
            required_by_date=future_date,
            status=STIPULATION_STATUS["PENDING"],
            created_by=self.staff
        )
        self.assertFalse(not_overdue.is_overdue())
        
        # Create a stipulation with a past required_by_date but SATISFIED status
        satisfied = Stipulation.objects.create(
            application=self.application,
            stipulation_type=STIPULATION_TYPES["PROOF_OF_INCOME"],
            description="Recent pay stubs required",
            required_by_date=past_date,
            status=STIPULATION_STATUS["SATISFIED"],
            created_by=self.staff,
            satisfied_at=timezone.now(),
            satisfied_by=self.borrower
        )
        self.assertFalse(satisfied.is_overdue())  # Should not be overdue if satisfied
        
        # Create a stipulation with a past required_by_date but WAIVED status
        waived = Stipulation.objects.create(
            application=self.application,
            stipulation_type=STIPULATION_TYPES["ADDITIONAL_DOCUMENTATION"],
            description="Some additional document",
            required_by_date=past_date,
            status=STIPULATION_STATUS["WAIVED"],
            created_by=self.staff
        )
        self.assertFalse(waived.is_overdue())  # Should not be overdue if waived

    def test_str_method(self):
        """Test the string representation of Stipulation"""
        expected_str = f"{self.stipulation.get_stipulation_type_display()} - {self.stipulation.status}"
        self.assertEqual(str(self.stipulation), expected_str)


class TestUnderwritingNote(TestCase):
    """Test case for the UnderwritingNote model"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test users for borrowers and staff
        from apps.users.models import User
        self.borrower = User.objects.create(
            email="borrower@example.com",
            first_name="John",
            last_name="Borrower"
        )
        
        self.staff = User.objects.create(
            email="staff@example.com",
            first_name="Staff",
            last_name="Member"
        )
        
        # Create test school and program
        from apps.schools.models import School, Program, ProgramVersion
        self.school = School.objects.create(
            name="Test School",
            legal_name="Test School Inc.",
            tax_id="12-3456789",
            address_line1="123 Education St",
            city="Testville",
            state="TX",
            zip_code="12345",
            phone="(555) 123-4567"
        )
        
        self.program = Program.objects.create(
            school=self.school,
            name="Test Program",
            description="A test program",
            duration_hours=500,
            duration_weeks=20
        )
        
        self.program_version = ProgramVersion.objects.create(
            program=self.program,
            version_number=1,
            effective_date=timezone.now().date(),
            tuition_amount=Decimal("10000.00"),
            is_current=True
        )
        
        # Create test loan application
        self.application = LoanApplication.objects.create(
            borrower=self.borrower,
            school=self.school,
            program=self.program,
            program_version=self.program_version,
            status=APPLICATION_STATUS["IN_REVIEW"]
        )
        
        # Create test underwriting note
        self.note = UnderwritingNote.objects.create(
            application=self.application,
            note_text="This is a test note for underwriting",
            created_by=self.staff,
            is_internal=True
        )

    def test_save_method(self):
        """Test that save method sets created_at if not provided"""
        # Create a new note without created_at
        new_note = UnderwritingNote(
            application=self.application,
            note_text="Another test note",
            created_by=self.staff,
            is_internal=True
        )
        
        # Save the note
        new_note.save()
        
        # created_at should be set automatically
        self.assertIsNotNone(new_note.created_at)

    def test_str_method(self):
        """Test the string representation of UnderwritingNote"""
        expected_str = f"Application {self.application.id}: This is a test note for underwriting"
        self.assertEqual(str(self.note), expected_str)
        
        # Test with a longer note that should be truncated
        long_note = UnderwritingNote.objects.create(
            application=self.application,
            note_text="This is a very long note that should be truncated in the string representation because it exceeds the maximum length for the preview",
            created_by=self.staff,
            is_internal=True
        )
        
        expected_long_str = f"Application {self.application.id}: This is a very long note that should be truncated in..."
        self.assertEqual(str(long_note), expected_long_str)