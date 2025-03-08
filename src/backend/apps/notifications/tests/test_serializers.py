from unittest.mock import patch, mock  # standard library
from django.test import TestCase  # Django 3.2+
from rest_framework.exceptions import ValidationError  # rest_framework 3.14+
import uuid  # standard library

from ..serializers import (  # src/backend/apps/notifications/serializers.py
    NotificationTemplateSerializer,
    NotificationTemplateDetailSerializer,
    NotificationEventSerializer,
    NotificationEventMappingSerializer,
    NotificationSerializer,
    NotificationDetailSerializer,
    NotificationCreateSerializer,
    NotificationBulkCreateSerializer,
    NotificationStatusUpdateSerializer,
    TemplatePreviewSerializer
)
from ..models import NotificationTemplate, NotificationEvent, NotificationEventMapping, Notification  # src/backend/apps/notifications/models.py
from apps.users.models import User  # src/backend/apps/users/models.py
from apps.applications.models import LoanApplication  # src/backend/apps/applications/models.py
from ..constants import NOTIFICATION_TYPES, NOTIFICATION_STATUS, EVENT_TYPE, NOTIFICATION_PRIORITIES  # src/backend/apps/notifications/constants.py


class TestNotificationTemplateSerializer(TestCase):
    """Test case for the NotificationTemplateSerializer"""

    def setUp(self):
        """Set up test data before each test method runs"""
        self.template_data = {
            'name': 'Test Template',
            'description': 'A test template',
            'subject_template': 'Test Subject',
            'body_template': 'Test Body',
            'notification_type': NOTIFICATION_TYPES['APPLICATION_SUBMITTED'],
            'is_active': True
        }
        self.serializer = NotificationTemplateSerializer(data=self.template_data)

    def test_validate_valid_data(self):
        """Test that valid template data passes validation"""
        valid_data = {
            'name': 'Valid Template',
            'description': 'A valid template',
            'subject_template': 'Valid Subject',
            'body_template': 'Valid Body',
            'notification_type': NOTIFICATION_TYPES['APPLICATION_SUBMITTED'],
            'is_active': True
        }
        serializer = NotificationTemplateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

    def test_validate_invalid_notification_type(self):
        """Test that invalid notification_type fails validation"""
        invalid_data = {
            'name': 'Invalid Template',
            'description': 'An invalid template',
            'subject_template': 'Invalid Subject',
            'body_template': 'Invalid Body',
            'notification_type': 'invalid_type',
            'is_active': True
        }
        serializer = NotificationTemplateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('notification_type', serializer.errors)

    def test_validate_missing_templates(self):
        """Test that missing template content fails validation"""
        missing_data = {
            'name': 'Missing Template',
            'description': 'A template with missing content',
            'notification_type': NOTIFICATION_TYPES['APPLICATION_SUBMITTED'],
            'is_active': True
        }
        serializer = NotificationTemplateSerializer(data=missing_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_get_template_variables(self):
        """Test that template variables are correctly extracted"""
        template_data = {
            'name': 'Variable Template',
            'description': 'A template with variables',
            'subject_template': 'Subject with {{variable1}}',
            'body_template': 'Body with {{variable2}} and {{variable1}}',
            'notification_type': NOTIFICATION_TYPES['APPLICATION_SUBMITTED'],
            'is_active': True
        }
        template = NotificationTemplate(**template_data)
        serializer = NotificationTemplateDetailSerializer(template)
        variables = serializer.get_template_variables(template)
        self.assertEqual(variables, ["variable1", "variable2"])


class TestNotificationEventSerializer(TestCase):
    """Test case for the NotificationEventSerializer"""

    def setUp(self):
        """Set up test data before each test method runs"""
        self.event_data = {
            'event_type': EVENT_TYPE['APPLICATION_STATUS_CHANGE'],
            'entity_id': uuid.uuid4(),
            'entity_type': 'application',
            'triggered_by': None,
            'context_data': {}
        }
        self.serializer = NotificationEventSerializer(data=self.event_data)

    def test_validate_event_type_valid(self):
        """Test that valid event_type passes validation"""
        event_type = EVENT_TYPE['APPLICATION_STATUS_CHANGE']
        serializer = NotificationEventSerializer()
        validated_event_type = serializer.validate_event_type(event_type)
        self.assertEqual(validated_event_type, event_type)

    def test_validate_event_type_invalid(self):
        """Test that invalid event_type fails validation"""
        invalid_event_type = 'invalid_event'
        serializer = NotificationEventSerializer()
        with self.assertRaises(ValidationError):
            serializer.validate_event_type(invalid_event_type)


class TestNotificationEventMappingSerializer(TestCase):
    """Test case for the NotificationEventMappingSerializer"""

    def setUp(self):
        """Set up test data before each test method runs"""
        self.template = NotificationTemplate.objects.create(
            name='Test Template',
            description='A test template',
            subject_template='Test Subject',
            body_template='Test Body',
            notification_type=NOTIFICATION_TYPES['APPLICATION_SUBMITTED'],
            is_active=True
        )
        self.mapping_data = {
            'event_type': EVENT_TYPE['APPLICATION_STATUS_CHANGE'],
            'template': self.template.id,
            'recipient_type': 'borrower',
            'priority': NOTIFICATION_PRIORITIES['MEDIUM'],
            'is_active': True
        }
        self.serializer = NotificationEventMappingSerializer(data=self.mapping_data)

    def test_validate_valid_data(self):
        """Test that valid mapping data passes validation"""
        valid_data = {
            'event_type': EVENT_TYPE['APPLICATION_STATUS_CHANGE'],
            'template': self.template.id,
            'recipient_type': 'borrower',
            'priority': NOTIFICATION_PRIORITIES['MEDIUM'],
            'is_active': True
        }
        serializer = NotificationEventMappingSerializer(data=valid_data)
        with patch('apps.notifications.serializers.NotificationTemplate.objects.filter') as mock_filter:
            mock_filter.return_value.exists.return_value = True
            self.assertTrue(serializer.is_valid())

    def test_validate_invalid_event_type(self):
        """Test that invalid event_type fails validation"""
        invalid_data = {
            'event_type': 'invalid_event',
            'template': self.template.id,
            'recipient_type': 'borrower',
            'priority': NOTIFICATION_PRIORITIES['MEDIUM'],
            'is_active': True
        }
        serializer = NotificationEventMappingSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('event_type', serializer.errors)

    def test_validate_invalid_template(self):
        """Test that non-existent template fails validation"""
        invalid_data = {
            'event_type': EVENT_TYPE['APPLICATION_STATUS_CHANGE'],
            'template': uuid.uuid4(),
            'recipient_type': 'borrower',
            'priority': NOTIFICATION_PRIORITIES['MEDIUM'],
            'is_active': True
        }
        serializer = NotificationEventMappingSerializer(data=invalid_data)
        with patch('apps.notifications.serializers.NotificationTemplate.objects.filter') as mock_filter:
            mock_filter.return_value.exists.return_value = False
            self.assertFalse(serializer.is_valid())
            self.assertIn('template', serializer.errors)

    def test_validate_invalid_priority(self):
        """Test that invalid priority fails validation"""
        invalid_data = {
            'event_type': EVENT_TYPE['APPLICATION_STATUS_CHANGE'],
            'template': self.template.id,
            'recipient_type': 'borrower',
            'priority': 'invalid_priority',
            'is_active': True
        }
        serializer = NotificationEventMappingSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('priority', serializer.errors)


class TestNotificationSerializer(TestCase):
    """Test case for the NotificationSerializer"""

    def setUp(self):
        """Set up test data before each test method runs"""
        self.template = NotificationTemplate.objects.create(
            name='Test Template',
            description='A test template',
            subject_template='Test Subject',
            body_template='Test Body',
            notification_type=NOTIFICATION_TYPES['APPLICATION_SUBMITTED'],
            is_active=True
        )
        self.recipient = User.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='(123) 456-7890',
            user_type='borrower',
            auth0_user_id=uuid.uuid4()
        )
        self.notification = Notification.objects.create(
            template=self.template,
            recipient=self.recipient,
            recipient_email=self.recipient.email,
            subject='Test Subject',
            body='Test Body'
        )
        self.serializer = NotificationSerializer(instance=self.notification)

    def test_get_template_name(self):
        """Test that get_template_name returns the correct template name"""
        template_name = self.serializer.get_template_name(self.notification)
        self.assertEqual(template_name, self.template.name)

    def test_get_recipient_name(self):
        """Test that get_recipient_name returns the correct recipient name"""
        recipient_name = self.serializer.get_recipient_name(self.notification)
        self.assertEqual(recipient_name, 'John Doe')

    def test_get_recipient_name_none(self):
        """Test that get_recipient_name handles None recipient"""
        notification = Notification.objects.create(
            template=self.template,
            recipient=None,
            recipient_email='test@example.com',
            subject='Test Subject',
            body='Test Body'
        )
        serializer = NotificationSerializer(instance=notification)
        recipient_name = serializer.get_recipient_name(notification)
        self.assertIsNone(recipient_name)


class TestNotificationDetailSerializer(TestCase):
    """Test case for the NotificationDetailSerializer"""

    def setUp(self):
        """Set up test data before each test method runs"""
        self.template = NotificationTemplate.objects.create(
            name='Test Template',
            description='A test template',
            subject_template='Test Subject',
            body_template='Test Body',
            notification_type=NOTIFICATION_TYPES['APPLICATION_SUBMITTED'],
            is_active=True
        )
        self.recipient = User.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='(123) 456-7890',
            user_type='borrower',
            auth0_user_id=uuid.uuid4()
        )
        self.application = LoanApplication.objects.create(
            borrower=self.recipient,
            school_id=uuid.uuid4(),
            program_id=uuid.uuid4(),
            program_version_id=uuid.uuid4()
        )
        self.notification = Notification.objects.create(
            template=self.template,
            recipient=self.recipient,
            recipient_email=self.recipient.email,
            subject='Test Subject',
            body='Test Body',
            application=self.application
        )
        self.serializer = NotificationDetailSerializer(instance=self.notification)

    def test_get_application_details(self):
        """Test that get_application_details returns correct application info"""
        application_details = self.serializer.get_application_details(self.notification)
        self.assertEqual(application_details['id'], str(self.application.id))
        self.assertEqual(application_details['borrower_name'], 'John Doe')

    def test_get_application_details_none(self):
        """Test that get_application_details handles None application"""
        notification = Notification.objects.create(
            template=self.template,
            recipient=self.recipient,
            recipient_email=self.recipient.email,
            subject='Test Subject',
            body='Test Body',
            application=None
        )
        serializer = NotificationDetailSerializer(instance=notification)
        application_details = serializer.get_application_details(notification)
        self.assertIsNone(application_details)


class TestNotificationCreateSerializer(TestCase):
    """Test case for the NotificationCreateSerializer"""

    def setUp(self):
        """Set up test data before each test method runs"""
        self.template = NotificationTemplate.objects.create(
            name='Test Template',
            description='A test template',
            subject_template='Test Subject',
            body_template='Test Body',
            notification_type=NOTIFICATION_TYPES['APPLICATION_SUBMITTED'],
            is_active=True
        )
        self.recipient = User.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='(123) 456-7890',
            user_type='borrower',
            auth0_user_id=uuid.uuid4()
        )
        self.event = NotificationEvent.objects.create(
            event_type=EVENT_TYPE['APPLICATION_STATUS_CHANGE'],
            entity_id=uuid.uuid4(),
            entity_type='application'
        )
        self.application = LoanApplication.objects.create(
            borrower=self.recipient,
            school_id=uuid.uuid4(),
            program_id=uuid.uuid4(),
            program_version_id=uuid.uuid4()
        )
        self.valid_data = {
            'template_id': self.template.id,
            'recipient_id': self.recipient.id,
            'event_id': self.event.id,
            'application_id': self.application.id,
            'context': {'key': 'value'}
        }
        self.serializer = NotificationCreateSerializer(data=self.valid_data)

    def test_validate_valid_data(self):
        """Test that valid creation data passes validation"""
        with patch('apps.notifications.serializers.NotificationTemplate.objects.filter') as mock_template_filter, \
             patch('apps.notifications.serializers.User.objects.filter') as mock_user_filter:
            mock_template_filter.return_value.exists.return_value = True
            mock_user_filter.return_value.exists.return_value = True
            self.assertTrue(self.serializer.is_valid())

    def test_validate_invalid_template(self):
        """Test that non-existent template fails validation"""
        invalid_data = self.valid_data.copy()
        invalid_data['template_id'] = uuid.uuid4()
        serializer = NotificationCreateSerializer(data=invalid_data)
        with patch('apps.notifications.serializers.NotificationTemplate.objects.filter') as mock_filter:
            mock_filter.return_value.exists.return_value = False
            self.assertFalse(serializer.is_valid())
            self.assertIn('template_id', serializer.errors)

    def test_validate_invalid_recipient(self):
        """Test that non-existent recipient fails validation"""
        invalid_data = self.valid_data.copy()
        invalid_data['recipient_id'] = uuid.uuid4()
        serializer = NotificationCreateSerializer(data=invalid_data)
        with patch('apps.notifications.serializers.User.objects.filter') as mock_filter:
            mock_filter.return_value.exists.return_value = False
            self.assertFalse(serializer.is_valid())
            self.assertIn('recipient_id', serializer.errors)

    @patch('apps.notifications.serializers.notification_service.create_notification')
    def test_create(self, mock_create_notification):
        """Test that create method creates a notification correctly"""
        mock_create_notification.return_value = Notification(
            template=self.template,
            recipient=self.recipient,
            recipient_email=self.recipient.email,
            subject='Test Subject',
            body='Test Body'
        )
        self.serializer.is_valid()
        notification = self.serializer.create(self.serializer.validated_data)
        mock_create_notification.assert_called_with(
            template=self.template,
            recipient=self.recipient,
            context=self.valid_data['context'],
            application=self.application,
            event=self.event,
            delivery_method=self.valid_data.get('delivery_method'),
            priority=self.valid_data.get('priority'),
            category=self.valid_data.get('category')
        )
        self.assertEqual(notification.template, self.template)
        self.assertEqual(notification.recipient, self.recipient)


class TestNotificationBulkCreateSerializer(TestCase):
    """Test case for the NotificationBulkCreateSerializer"""

    def setUp(self):
        """Set up test data before each test method runs"""
        self.template = NotificationTemplate.objects.create(
            name='Test Template',
            description='A test template',
            subject_template='Test Subject',
            body_template='Test Body',
            notification_type=NOTIFICATION_TYPES['APPLICATION_SUBMITTED'],
            is_active=True
        )
        self.recipient = User.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='(123) 456-7890',
            user_type='borrower',
            auth0_user_id=uuid.uuid4()
        )
        self.event = NotificationEvent.objects.create(
            event_type=EVENT_TYPE['APPLICATION_STATUS_CHANGE'],
            entity_id=uuid.uuid4(),
            entity_type='application'
        )
        self.application = LoanApplication.objects.create(
            borrower=self.recipient,
            school_id=uuid.uuid4(),
            program_id=uuid.uuid4(),
            program_version_id=uuid.uuid4()
        )
        self.notification_data = [
            {
                'template_id': self.template.id,
                'recipient_id': self.recipient.id,
                'event_id': self.event.id,
                'application_id': self.application.id,
                'context': {'key': 'value1'}
            },
            {
                'template_id': self.template.id,
                'recipient_id': self.recipient.id,
                'event_id': self.event.id,
                'application_id': self.application.id,
                'context': {'key': 'value2'}
            }
        ]
        self.valid_data = {'notifications': self.notification_data}
        self.serializer = NotificationBulkCreateSerializer(data=self.valid_data)

    @patch('apps.notifications.serializers.NotificationCreateSerializer.create')
    def test_create(self, mock_create):
        """Test that create method creates multiple notifications correctly"""
        mock_create.return_value = Notification(
            template=self.template,
            recipient=self.recipient,
            recipient_email=self.recipient.email,
            subject='Test Subject',
            body='Test Body'
        )
        self.serializer.is_valid()
        notifications = self.serializer.create(self.serializer.validated_data)
        self.assertEqual(mock_create.call_count, len(self.notification_data))
        self.assertEqual(len(notifications), len(self.notification_data))


class TestNotificationStatusUpdateSerializer(TestCase):
    """Test case for the NotificationStatusUpdateSerializer"""

    def setUp(self):
        """Set up test data before each test method runs"""
        self.template = NotificationTemplate.objects.create(
            name='Test Template',
            description='A test template',
            subject_template='Test Subject',
            body_template='Test Body',
            notification_type=NOTIFICATION_TYPES['APPLICATION_SUBMITTED'],
            is_active=True
        )
        self.recipient = User.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='(123) 456-7890',
            user_type='borrower',
            auth0_user_id=uuid.uuid4()
        )
        self.notification = Notification.objects.create(
            template=self.template,
            recipient=self.recipient,
            recipient_email=self.recipient.email,
            subject='Test Subject',
            body='Test Body'
        )
        self.status_data = {'status': NOTIFICATION_STATUS['SENT']}
        self.serializer = NotificationStatusUpdateSerializer(data=self.status_data)

    def test_validate_status_valid(self):
        """Test that valid status passes validation"""
        status = NOTIFICATION_STATUS['SENT']
        serializer = NotificationStatusUpdateSerializer()
        validated_status = serializer.validate_status(status)
        self.assertEqual(validated_status, status)

    def test_validate_status_invalid(self):
        """Test that invalid status fails validation"""
        invalid_status = 'invalid_status'
        serializer = NotificationStatusUpdateSerializer()
        with self.assertRaises(ValidationError):
            serializer.validate_status(invalid_status)

    @patch('apps.notifications.models.Notification.mark_sent')
    def test_update_status_sent(self, mock_mark_sent):
        """Test that update_status sets status to sent correctly"""
        self.serializer.is_valid()
        updated_notification = self.serializer.update_status(self.notification, self.serializer.validated_data)
        mock_mark_sent.assert_called_once()
        self.assertEqual(updated_notification.status, NOTIFICATION_STATUS['SENT'])

    @patch('apps.notifications.models.Notification.mark_failed')
    def test_update_status_failed(self, mock_mark_failed):
        """Test that update_status sets status to failed correctly"""
        error_message = 'Test error message'
        status_data = {'status': NOTIFICATION_STATUS['FAILED'], 'error_message': error_message}
        serializer = NotificationStatusUpdateSerializer(data=status_data)
        serializer.is_valid()
        updated_notification = serializer.update_status(self.notification, serializer.validated_data)
        mock_mark_failed.assert_called_with(error_message)
        self.assertEqual(updated_notification.status, NOTIFICATION_STATUS['FAILED'])

    def test_update_status_other(self):
        """Test that update_status handles other status values correctly"""
        status_data = {'status': NOTIFICATION_STATUS['PENDING']}
        serializer = NotificationStatusUpdateSerializer(data=status_data)
        serializer.is_valid()
        updated_notification = serializer.update_status(self.notification, serializer.validated_data)
        self.assertEqual(updated_notification.status, NOTIFICATION_STATUS['PENDING'])
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.status, NOTIFICATION_STATUS['PENDING'])


class TestTemplatePreviewSerializer(TestCase):
    """Test case for the TemplatePreviewSerializer"""

    def setUp(self):
        """Set up test data before each test method runs"""
        self.template = NotificationTemplate.objects.create(
            name='Test Template',
            description='A test template',
            subject_template='Test Subject: {{key}}',
            body_template='Test Body: {{key}}',
            notification_type=NOTIFICATION_TYPES['APPLICATION_SUBMITTED'],
            is_active=True
        )
        self.preview_data = {'context': {'key': 'value'}}
        self.serializer = TemplatePreviewSerializer(data=self.preview_data)

    def test_validate_with_template_id(self):
        """Test validation with template_id"""
        data = {'template_id': self.template.id, 'context': {'key': 'value'}}
        serializer = TemplatePreviewSerializer(data=data)
        with patch('apps.notifications.serializers.NotificationTemplate.objects.filter') as mock_filter:
            mock_filter.return_value.exists.return_value = True
            self.assertTrue(serializer.is_valid())

    def test_validate_with_notification_type(self):
        """Test validation with notification_type"""
        data = {'notification_type': NOTIFICATION_TYPES['APPLICATION_SUBMITTED'], 'context': {'key': 'value'}}
        serializer = TemplatePreviewSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_with_templates(self):
        """Test validation with subject_template and body_template"""
        data = {'subject_template': 'Test Subject', 'body_template': 'Test Body', 'context': {'key': 'value'}}
        serializer = TemplatePreviewSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_missing_required_fields(self):
        """Test validation with missing required fields"""
        data = {'context': {'key': 'value'}}
        serializer = TemplatePreviewSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    @patch('apps.notifications.models.NotificationTemplate.render')
    def test_preview_with_template_id(self, mock_render):
        """Test preview generation with template_id"""
        mock_render.return_value = ('Rendered Subject', 'Rendered Body')
        data = {'template_id': self.template.id, 'context': {'key': 'value'}}
        serializer = TemplatePreviewSerializer(data=data)
        serializer.is_valid()
        preview = serializer.preview(serializer.validated_data)
        mock_render.assert_called_with({'key': 'value'})
        self.assertEqual(preview['subject'], 'Rendered Subject')
        self.assertEqual(preview['body'], 'Rendered Body')

    @patch('apps.notifications.models.NotificationTemplate.get_template_for_type')
    @patch('apps.notifications.models.NotificationTemplate.render')
    def test_preview_with_notification_type(self, mock_render, mock_get_template):
        """Test preview generation with notification_type"""
        mock_get_template.return_value = self.template
        mock_render.return_value = ('Rendered Subject', 'Rendered Body')
        data = {'notification_type': NOTIFICATION_TYPES['APPLICATION_SUBMITTED'], 'context': {'key': 'value'}}
        serializer = TemplatePreviewSerializer(data=data)
        serializer.is_valid()
        preview = serializer.preview(serializer.validated_data)
        mock_get_template.assert_called_with(NOTIFICATION_TYPES['APPLICATION_SUBMITTED'])
        mock_render.assert_called_with({'key': 'value'})
        self.assertEqual(preview['subject'], 'Rendered Subject')
        self.assertEqual(preview['body'], 'Rendered Body')

    def test_preview_with_templates(self):
        """Test preview generation with subject_template and body_template"""
        data = {
            'subject_template': 'Subject: {{key}}',
            'body_template': 'Body: {{key}}',
            'context': {'key': 'value'}
        }
        serializer = TemplatePreviewSerializer(data=data)
        serializer.is_valid()
        preview = serializer.preview(serializer.validated_data)
        self.assertEqual(preview['subject'], 'Subject: value')
        self.assertEqual(preview['body'], 'Body: value')