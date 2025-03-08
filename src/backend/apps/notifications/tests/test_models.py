"""
Unit tests for the notification models in the loan management system.

This module contains tests for the NotificationTemplate, NotificationEvent,
NotificationEventMapping, and Notification models, verifying their core
functionality for creating, managing, and rendering notifications.
"""

from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.utils import timezone
from django.template.loader import render_to_string
import json
import uuid

from ..models import (
    NotificationTemplate, NotificationEvent, 
    NotificationEventMapping, Notification
)
from ..constants import (
    NOTIFICATION_TYPES, NOTIFICATION_STATUS, 
    NOTIFICATION_DELIVERY_METHODS, NOTIFICATION_PRIORITIES,
    NOTIFICATION_CATEGORIES, EVENT_TYPE, MAX_RETRY_ATTEMPTS
)
from apps.users.models import User
from apps.applications.models import LoanApplication


class NotificationTemplateTestCase(TestCase):
    def setUp(self):
        """Set up test data for notification template tests."""
        self.template = NotificationTemplate.objects.create(
            name="Test Template",
            description="Test description",
            subject_template="Hello, {{name}}!",
            body_template="Dear {{name}},\n\nYour application {{application_id}} has been {{status}}.\n\nRegards,\nThe Team",
            notification_type=NOTIFICATION_TYPES['APPLICATION_APPROVED'],
            is_active=True
        )
    
    def test_template_creation(self):
        """Test creating a notification template."""
        template = NotificationTemplate.objects.create(
            name="Another Template",
            description="Another description",
            subject_template="Subject {{variable}}",
            body_template="Body {{variable}}",
            notification_type=NOTIFICATION_TYPES['APPLICATION_SUBMITTED']
        )
        
        self.assertEqual(template.name, "Another Template")
        self.assertEqual(template.description, "Another description")
        self.assertEqual(template.subject_template, "Subject {{variable}}")
        self.assertEqual(template.body_template, "Body {{variable}}")
        self.assertEqual(template.notification_type, NOTIFICATION_TYPES['APPLICATION_SUBMITTED'])
        self.assertTrue(template.is_active)  # Should be active by default
    
    def test_render_method(self):
        """Test rendering a template with context."""
        context = {
            "name": "John Doe",
            "application_id": "APP-12345",
            "status": "approved"
        }
        
        subject, body = self.template.render(context)
        
        self.assertEqual(subject, "Hello, John Doe!")
        self.assertIn("Dear John Doe,", body)
        self.assertIn("Your application APP-12345 has been approved.", body)
    
    @patch('django.template.loader.render_to_string')
    def test_render_with_template_path(self, mock_render_to_string):
        """Test rendering a template from a file path."""
        # Setup mock return
        mock_render_to_string.return_value = "Rendered content from file"
        
        # Update template to use a template path
        self.template.template_path = "notifications/email/test_template.html"
        self.template.save()
        
        context = {"name": "Jane Doe"}
        
        subject, body = self.template.render(context)
        
        # Verify render_to_string was called with correct args
        mock_render_to_string.assert_called_once_with(
            self.template.template_path, context
        )
        
        self.assertIn("Jane Doe", subject)  # Subject still uses template from model
        self.assertEqual(body, "Rendered content from file")
    
    def test_get_template_for_type(self):
        """Test getting an active template for a notification type."""
        # Create an inactive template with the same type
        inactive_template = NotificationTemplate.objects.create(
            name="Inactive Template",
            subject_template="Inactive subject",
            body_template="Inactive body",
            notification_type=NOTIFICATION_TYPES['APPLICATION_APPROVED'],
            is_active=False
        )
        
        # Get template for the type
        template = NotificationTemplate.get_template_for_type(
            NOTIFICATION_TYPES['APPLICATION_APPROVED']
        )
        
        # Should return the active one
        self.assertEqual(template.id, self.template.id)
        
        # Try with a type that doesn't exist
        template = NotificationTemplate.get_template_for_type("non_existent_type")
        self.assertIsNone(template)


class NotificationEventTestCase(TestCase):
    def setUp(self):
        """Set up test data for notification event tests."""
        # Create a user
        self.user = User.objects.create(
            email="testuser@example.com",
            first_name="Test",
            last_name="User"
        )
        
        # Create a test loan application
        self.application = LoanApplication.objects.create(
            borrower=self.user,
            status="draft"
        )
        
        # Create a test event
        self.event = NotificationEvent.objects.create(
            event_type=EVENT_TYPE['APPLICATION_STATUS_CHANGE'],
            entity_id=self.application.id,
            entity_type="application",
            triggered_by=self.user,
            context_data={
                "old_status": "draft",
                "new_status": "submitted",
                "application_id": str(self.application.id)
            },
            processed=False
        )
    
    def test_event_creation(self):
        """Test creating a notification event."""
        event = NotificationEvent.objects.create(
            event_type=EVENT_TYPE['DOCUMENT_STATUS_CHANGE'],
            entity_id=uuid.uuid4(),
            entity_type="document",
            triggered_by=self.user,
            processed=False
        )
        
        self.assertEqual(event.event_type, EVENT_TYPE['DOCUMENT_STATUS_CHANGE'])
        self.assertEqual(event.entity_type, "document")
        self.assertEqual(event.triggered_by, self.user)
        self.assertFalse(event.processed)
        self.assertIsNone(event.processed_at)
    
    def test_get_context(self):
        """Test getting context data from an event."""
        # Test with existing context data
        context = self.event.get_context()
        expected_context = {
            "old_status": "draft",
            "new_status": "submitted",
            "application_id": str(self.application.id)
        }
        
        self.assertEqual(context, expected_context)
        
        # Test with empty context data
        self.event.context_data = None
        self.event.save()
        
        context = self.event.get_context()
        self.assertEqual(context, {})
    
    def test_mark_processed(self):
        """Test marking an event as processed."""
        self.assertFalse(self.event.processed)
        self.assertIsNone(self.event.processed_at)
        
        self.event.mark_processed()
        
        # Refresh from DB
        self.event.refresh_from_db()
        
        self.assertTrue(self.event.processed)
        self.assertIsNotNone(self.event.processed_at)
    
    def test_get_entity(self):
        """Test getting the entity associated with an event."""
        # Test with valid entity
        entity = self.event.get_entity()
        self.assertEqual(entity, self.application)
        
        # Test with invalid entity type
        self.event.entity_type = "invalid_type"
        self.event.save()
        
        entity = self.event.get_entity()
        self.assertIsNone(entity)
        
        # Test with valid type but non-existent entity
        self.event.entity_type = "application"
        self.event.entity_id = uuid.uuid4()  # Random ID that doesn't exist
        self.event.save()
        
        entity = self.event.get_entity()
        self.assertIsNone(entity)


class NotificationEventMappingTestCase(TestCase):
    def setUp(self):
        """Set up test data for notification event mapping tests."""
        # Create a template
        self.template = NotificationTemplate.objects.create(
            name="Test Template",
            subject_template="Test Subject",
            body_template="Test Body",
            notification_type=NOTIFICATION_TYPES['APPLICATION_APPROVED']
        )
        
        # Create a mapping
        self.mapping = NotificationEventMapping.objects.create(
            event_type=EVENT_TYPE['APPLICATION_STATUS_CHANGE'],
            template=self.template,
            recipient_type="borrower",
            priority=NOTIFICATION_PRIORITIES['HIGH'],
            is_active=True
        )
    
    def test_mapping_creation(self):
        """Test creating a notification event mapping."""
        mapping = NotificationEventMapping.objects.create(
            event_type=EVENT_TYPE['DOCUMENT_STATUS_CHANGE'],
            template=self.template,
            recipient_type="school_admin",
            priority=NOTIFICATION_PRIORITIES['MEDIUM']
        )
        
        self.assertEqual(mapping.event_type, EVENT_TYPE['DOCUMENT_STATUS_CHANGE'])
        self.assertEqual(mapping.template, self.template)
        self.assertEqual(mapping.recipient_type, "school_admin")
        self.assertEqual(mapping.priority, NOTIFICATION_PRIORITIES['MEDIUM'])
        self.assertTrue(mapping.is_active)  # Should be active by default
    
    def test_get_mappings_for_event(self):
        """Test getting all active mappings for an event type."""
        # Create another mapping with same event type but inactive
        inactive_mapping = NotificationEventMapping.objects.create(
            event_type=EVENT_TYPE['APPLICATION_STATUS_CHANGE'],
            template=self.template,
            recipient_type="school_admin",
            is_active=False
        )
        
        # Create another active mapping with same event type
        another_mapping = NotificationEventMapping.objects.create(
            event_type=EVENT_TYPE['APPLICATION_STATUS_CHANGE'],
            template=self.template,
            recipient_type="underwriter",
            is_active=True
        )
        
        # Get mappings for the event type
        mappings = NotificationEventMapping.get_mappings_for_event(
            EVENT_TYPE['APPLICATION_STATUS_CHANGE']
        )
        
        # Should return two active mappings
        self.assertEqual(mappings.count(), 2)
        
        # Verify the returned mappings are the active ones
        mapping_ids = [m.id for m in mappings]
        self.assertIn(self.mapping.id, mapping_ids)
        self.assertIn(another_mapping.id, mapping_ids)
        self.assertNotIn(inactive_mapping.id, mapping_ids)
        
        # Test with non-existent event type
        mappings = NotificationEventMapping.get_mappings_for_event("non_existent_type")
        self.assertEqual(mappings.count(), 0)


class NotificationTestCase(TestCase):
    def setUp(self):
        """Set up test data for notification tests."""
        # Create a user
        self.user = User.objects.create(
            email="recipient@example.com",
            first_name="Test",
            last_name="Recipient"
        )
        
        # Create a template
        self.template = NotificationTemplate.objects.create(
            name="Test Template",
            subject_template="Test Subject",
            body_template="Test Body",
            notification_type=NOTIFICATION_TYPES['APPLICATION_APPROVED']
        )
        
        # Create an event
        self.application = LoanApplication.objects.create(
            borrower=self.user,
            status="approved"
        )
        
        self.event = NotificationEvent.objects.create(
            event_type=EVENT_TYPE['APPLICATION_STATUS_CHANGE'],
            entity_id=self.application.id,
            entity_type="application",
            triggered_by=self.user
        )
        
        # Create a notification
        self.notification = Notification.objects.create(
            template=self.template,
            recipient=self.user,
            recipient_email=self.user.email,
            subject="Your application has been approved",
            body="Congratulations! Your loan application has been approved.",
            event=self.event,
            application=self.application,
            status=NOTIFICATION_STATUS['PENDING'],
            delivery_method=NOTIFICATION_DELIVERY_METHODS['EMAIL'],
            priority=NOTIFICATION_PRIORITIES['HIGH'],
            category=NOTIFICATION_CATEGORIES['APPLICATION']
        )
    
    def test_notification_creation(self):
        """Test creating a notification."""
        notification = Notification.objects.create(
            template=self.template,
            recipient=self.user,
            recipient_email="another@example.com",
            subject="Test Subject",
            body="Test Body",
            event=self.event,
            status=NOTIFICATION_STATUS['PENDING']
        )
        
        self.assertEqual(notification.template, self.template)
        self.assertEqual(notification.recipient, self.user)
        self.assertEqual(notification.recipient_email, "another@example.com")
        self.assertEqual(notification.subject, "Test Subject")
        self.assertEqual(notification.body, "Test Body")
        self.assertEqual(notification.event, self.event)
        self.assertEqual(notification.status, NOTIFICATION_STATUS['PENDING'])
        self.assertIsNone(notification.sent_at)
        self.assertEqual(notification.error_message, None)
        self.assertEqual(notification.retry_count, 0)
    
    def test_mark_sent(self):
        """Test marking a notification as sent."""
        self.assertEqual(self.notification.status, NOTIFICATION_STATUS['PENDING'])
        self.assertIsNone(self.notification.sent_at)
        
        self.notification.mark_sent()
        
        # Refresh from DB
        self.notification.refresh_from_db()
        
        self.assertEqual(self.notification.status, NOTIFICATION_STATUS['SENT'])
        self.assertIsNotNone(self.notification.sent_at)
    
    def test_mark_failed(self):
        """Test marking a notification as failed."""
        error_message = "Failed to send email: SMTP error"
        
        self.notification.mark_failed(error_message)
        
        # Refresh from DB
        self.notification.refresh_from_db()
        
        self.assertEqual(self.notification.status, NOTIFICATION_STATUS['FAILED'])
        self.assertEqual(self.notification.error_message, error_message)
    
    def test_mark_retry(self):
        """Test marking a notification for retry."""
        initial_retry_count = self.notification.retry_count
        
        self.notification.mark_retry()
        
        # Refresh from DB
        self.notification.refresh_from_db()
        
        self.assertEqual(self.notification.status, NOTIFICATION_STATUS['PENDING'])
        self.assertEqual(self.notification.retry_count, initial_retry_count + 1)
        self.assertIsNotNone(self.notification.last_retry_at)
    
    def test_can_retry(self):
        """Test checking if a notification can be retried."""
        # Set retry count below max
        self.notification.retry_count = MAX_RETRY_ATTEMPTS - 1
        self.notification.save()
        
        self.assertTrue(self.notification.can_retry(MAX_RETRY_ATTEMPTS))
        
        # Set retry count to max
        self.notification.retry_count = MAX_RETRY_ATTEMPTS
        self.notification.save()
        
        self.assertFalse(self.notification.can_retry(MAX_RETRY_ATTEMPTS))
        
        # Set retry count above max
        self.notification.retry_count = MAX_RETRY_ATTEMPTS + 1
        self.notification.save()
        
        self.assertFalse(self.notification.can_retry(MAX_RETRY_ATTEMPTS))