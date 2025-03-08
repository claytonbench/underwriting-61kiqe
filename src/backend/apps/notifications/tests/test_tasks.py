import pytest  # pytest 7.0+
from unittest.mock import patch  # standard library
from datetime import datetime  # standard library
from django.utils import timezone  # Django 4.2+
import freezegun  # freezegun 1.2+

from ..tasks import (
    send_notification,
    process_notification_queue,
    retry_failed_notifications,
    process_notification_events,
    schedule_signature_reminders,
    cleanup_old_notifications
)
from ..models import Notification, NotificationEvent, NotificationTemplate
from ..email import send_notification_email, process_notification_batch
from ..services import process_pending_events
from ..constants import (
    NOTIFICATION_STATUS,
    NOTIFICATION_TYPES,
    EVENT_TYPE,
    BATCH_SIZE,
    MAX_RETRY_ATTEMPTS,
    NOTIFICATION_RETENTION_DAYS
)


@pytest.mark.notification
@pytest.mark.task
class TestNotificationTasks:
    """Test class for notification task functions"""

    def setUp(self):
        """Set up test data before each test method runs"""
        # Create test notification template
        self.template = NotificationTemplate.objects.create(
            name="Test Template",
            description="Test notification template",
            subject_template="Test Subject",
            body_template="Test Body",
            notification_type=NOTIFICATION_TYPES["APPLICATION_SUBMITTED"],
            is_active=True,
        )

        # Create test user for recipient
        self.user = Notification.objects.create(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            phone="555-555-5555",
            user_type="borrower",
            is_active=True,
        )

        # Create test notification objects with various statuses
        self.notification1 = Notification.objects.create(
            template=self.template,
            recipient=self.user,
            recipient_email="test1@example.com",
            subject="Test Notification 1",
            body="Test Notification Body 1",
            status=NOTIFICATION_STATUS["PENDING"],
        )
        self.notification2 = Notification.objects.create(
            template=self.template,
            recipient=self.user,
            recipient_email="test2@example.com",
            subject="Test Notification 2",
            body="Test Notification Body 2",
            status=NOTIFICATION_STATUS["FAILED"],
            retry_count=MAX_RETRY_ATTEMPTS - 1,
        )
        self.notification3 = Notification.objects.create(
            template=self.template,
            recipient=self.user,
            recipient_email="test3@example.com",
            subject="Test Notification 3",
            body="Test Notification Body 3",
            status=NOTIFICATION_STATUS["FAILED"],
            retry_count=MAX_RETRY_ATTEMPTS,
        )

        # Create test notification events
        self.event1 = NotificationEvent.objects.create(
            event_type=EVENT_TYPE["APPLICATION_STATUS_CHANGE"],
            entity_id=self.notification1.id,
            entity_type="notification",
        )
        self.event2 = NotificationEvent.objects.create(
            event_type=EVENT_TYPE["DOCUMENT_STATUS_CHANGE"],
            entity_id=self.notification2.id,
            entity_type="notification",
        )

    def tearDown(self):
        """Clean up after each test method runs"""
        # Delete test notification objects
        Notification.objects.all().delete()

        # Delete test notification events
        NotificationEvent.objects.all().delete()

        # Delete test notification template
        NotificationTemplate.objects.all().delete()

        # Delete test user
        Notification.objects.all().delete()

    @pytest.mark.notification
    @pytest.mark.task
    @patch('src.backend.apps.notifications.tasks.send_notification_email')
    def test_send_notification_success(self, mock_send_notification_email):
        """Test successful sending of a notification"""
        # Mock send_notification_email to return True
        mock_send_notification_email.return_value = True

        # Call send_notification with a valid notification ID
        result = send_notification(self.notification1.id)

        # Assert that send_notification_email was called with the correct notification
        mock_send_notification_email.assert_called_once_with(self.notification1)

        # Assert that the task returns True
        assert result is True

    @pytest.mark.notification
    @pytest.mark.task
    @patch('src.backend.apps.notifications.tasks.send_notification_email')
    def test_send_notification_not_found(self, mock_send_notification_email):
        """Test sending a notification that doesn't exist"""
        # Call send_notification with a non-existent notification ID
        result = send_notification("non_existent_id")

        # Assert that send_notification_email was not called
        mock_send_notification_email.assert_not_called()

        # Assert that the task returns False
        assert result is False

    @pytest.mark.notification
    @pytest.mark.task
    @patch('src.backend.apps.notifications.tasks.process_notification_batch')
    def test_process_notification_queue_with_pending(self, mock_process_notification_batch):
        """Test processing notification queue with pending notifications"""
        # Create multiple pending notifications
        pending_notifications = [
            Notification.objects.create(
                template=self.template,
                recipient=self.user,
                recipient_email=f"test{i}@example.com",
                subject=f"Test Notification {i}",
                body=f"Test Notification Body {i}",
                status=NOTIFICATION_STATUS["PENDING"],
            )
            for i in range(3)
        ]

        # Mock process_notification_batch to return success statistics
        mock_process_notification_batch.return_value = {"sent": 3, "failed": 0, "total": 3}

        # Call process_notification_queue
        result = process_notification_queue()

        # Assert that process_notification_batch was called with correct batches
        mock_process_notification_batch.assert_called_once()

        # Assert that the task returns correct aggregated statistics
        assert result == {"sent": 3, "failed": 0, "total": 3}

    @pytest.mark.notification
    @pytest.mark.task
    @patch('src.backend.apps.notifications.tasks.process_notification_batch')
    def test_process_notification_queue_empty(self, mock_process_notification_batch):
        """Test processing an empty notification queue"""
        # Ensure no pending notifications exist
        Notification.objects.filter(status=NOTIFICATION_STATUS["PENDING"]).delete()

        # Call process_notification_queue
        result = process_notification_queue()

        # Assert that process_notification_batch was not called
        mock_process_notification_batch.assert_not_called()

        # Assert that the task returns zero statistics
        assert result == {"sent": 0, "failed": 0, "total": 0}

    @pytest.mark.notification
    @pytest.mark.task
    @patch('src.backend.apps.notifications.models.Notification.can_retry')
    @patch('src.backend.apps.notifications.models.Notification.mark_retry')
    @patch('src.backend.apps.notifications.tasks.send_notification')
    def test_retry_failed_notifications_with_retryable(self, mock_send_notification, mock_mark_retry, mock_can_retry):
        """Test retrying failed notifications that are retryable"""
        # Create failed notifications with retry counts below MAX_RETRY_ATTEMPTS
        failed_notifications = [
            Notification.objects.create(
                template=self.template,
                recipient=self.user,
                recipient_email=f"test{i}@example.com",
                subject=f"Test Notification {i}",
                body=f"Test Notification Body {i}",
                status=NOTIFICATION_STATUS["FAILED"],
                retry_count=i,
            )
            for i in range(MAX_RETRY_ATTEMPTS)
        ]

        # Mock can_retry to return True
        mock_can_retry.return_value = True

        # Call retry_failed_notifications
        result = retry_failed_notifications()

        # Assert that mark_retry was called for each retryable notification
        assert mock_mark_retry.call_count == len(failed_notifications)

        # Assert that send_notification was called for each retryable notification
        assert mock_send_notification.call_count == len(failed_notifications)

        # Assert that the task returns correct retry statistics
        assert result == {"retried": len(failed_notifications), "total": len(failed_notifications)}

    @pytest.mark.notification
    @pytest.mark.task
    @patch('src.backend.apps.notifications.models.Notification.can_retry')
    @patch('src.backend.apps.notifications.models.Notification.mark_retry')
    @patch('src.backend.apps.notifications.tasks.send_notification')
    def test_retry_failed_notifications_non_retryable(self, mock_send_notification, mock_mark_retry, mock_can_retry):
        """Test retrying failed notifications that are not retryable"""
        # Create failed notifications with retry counts at MAX_RETRY_ATTEMPTS
        failed_notifications = [
            Notification.objects.create(
                template=self.template,
                recipient=self.user,
                recipient_email=f"test{i}@example.com",
                subject=f"Test Notification {i}",
                body=f"Test Notification Body {i}",
                status=NOTIFICATION_STATUS["FAILED"],
                retry_count=MAX_RETRY_ATTEMPTS,
            )
            for i in range(3)
        ]

        # Mock can_retry to return False
        mock_can_retry.return_value = False

        # Call retry_failed_notifications
        result = retry_failed_notifications()

        # Assert that mark_retry was not called
        mock_mark_retry.assert_not_called()

        # Assert that send_notification was not called
        mock_send_notification.assert_not_called()

        # Assert that the task returns zero retry statistics
        assert result == {"retried": 0, "total": len(failed_notifications)}

    @pytest.mark.notification
    @pytest.mark.task
    @patch('src.backend.apps.notifications.tasks.process_pending_events')
    def test_process_notification_events_success(self, mock_process_pending_events):
        """Test successful processing of notification events"""
        # Create unprocessed notification events
        events = [
            NotificationEvent.objects.create(
                event_type=EVENT_TYPE["APPLICATION_STATUS_CHANGE"],
                entity_id=self.notification1.id,
                entity_type="notification",
            )
            for i in range(3)
        ]

        # Mock process_pending_events to return success statistics
        mock_process_pending_events.return_value = {"events_processed": 3, "notifications_created": 3}

        # Call process_notification_events
        result = process_notification_events()

        # Assert that process_pending_events was called
        mock_process_pending_events.assert_called_once()

        # Assert that the task returns correct statistics
        assert result == {"events_processed": 3, "notifications_created": 3}

    @pytest.mark.notification
    @pytest.mark.task
    @patch('src.backend.apps.notifications.tasks.Document.objects.filter')
    @patch('src.backend.apps.notifications.tasks.schedule_reminder')
    def test_schedule_signature_reminders_with_pending(self, mock_schedule_reminder, mock_document_filter):
        """Test scheduling signature reminders for pending signatures"""
        # Mock Document.objects.filter to return test document packages
        mock_document_filter.return_value = [1, 2, 3]

        # Mock schedule_reminder to return test notifications
        mock_schedule_reminder.return_value = [1, 2, 3]

        # Call schedule_signature_reminders
        result = schedule_signature_reminders()

        # Assert that Document.objects.filter was called with correct filters
        mock_document_filter.assert_called()

        # Assert that schedule_reminder was called for each recipient
        mock_schedule_reminder.assert_called()

        # Assert that the task returns correct count of scheduled reminders
        assert result == 0

    @pytest.mark.notification
    @pytest.mark.task
    @freezegun.freeze_time('2023-01-15')
    def test_cleanup_old_notifications_with_old_records(self):
        """Test cleaning up old notification records"""
        # Create notifications with created_at dates older than NOTIFICATION_RETENTION_DAYS
        old_notification1 = Notification.objects.create(
            template=self.template,
            recipient=self.user,
            recipient_email="old1@example.com",
            subject="Old Notification 1",
            body="Old Notification Body 1",
            created_at=timezone.now() - timezone.timedelta(days=NOTIFICATION_RETENTION_DAYS + 1),
        )
        old_notification2 = Notification.objects.create(
            template=self.template,
            recipient=self.user,
            recipient_email="old2@example.com",
            subject="Old Notification 2",
            body="Old Notification Body 2",
            created_at=timezone.now() - timezone.timedelta(days=NOTIFICATION_RETENTION_DAYS + 2),
        )

        # Create notifications with recent created_at dates
        recent_notification1 = Notification.objects.create(
            template=self.template,
            recipient=self.user,
            recipient_email="recent1@example.com",
            subject="Recent Notification 1",
            body="Recent Notification Body 1",
            created_at=timezone.now() - timezone.timedelta(days=NOTIFICATION_RETENTION_DAYS - 1),
        )
        recent_notification2 = Notification.objects.create(
            template=self.template,
            recipient=self.user,
            recipient_email="recent2@example.com",
            subject="Recent Notification 2",
            body="Recent Notification Body 2",
            created_at=timezone.now(),
        )

        # Call cleanup_old_notifications
        result = cleanup_old_notifications()

        # Assert that old notifications are deleted
        assert not Notification.objects.filter(id__in=[old_notification1.id, old_notification2.id]).exists()

        # Assert that recent notifications are preserved
        assert Notification.objects.filter(id__in=[recent_notification1.id, recent_notification2.id]).exists()

        # Assert that the task returns correct count of deleted notifications
        assert result == 2