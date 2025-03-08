"""
Unit tests for core abstract model classes.

This module provides comprehensive tests for the core abstract model classes
that serve as the foundation for all database models in the loan management system,
including BaseModel, TimeStampedModel, UUIDModel, SoftDeleteModel, AuditableModel, and CoreModel.
"""

from django.test import TestCase
from unittest.mock import mock, patch
from django.utils import timezone
import uuid
from django.contrib.auth import get_user_model
from django.db import models

from ..models import (
    BaseModel,
    TimeStampedModel,
    UUIDModel,
    SoftDeleteModel,
    AuditableModel,
    CoreModel,
    ActiveManager,
    AllObjectsManager,
    model_change_signal,
    audit_log_signal,
)


class TestBaseModel(TestCase):
    """Test case for the BaseModel abstract class."""

    def setUp(self):
        """Set up test data before each test method runs."""
        # Create a concrete model class that inherits from BaseModel for testing
        class TestModel(BaseModel):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'core'

        self.TestModel = TestModel
        self.test_instance = TestModel(name="Test Instance")

    def test_save_method(self):
        """Test that the save method works correctly."""
        with patch.object(model_change_signal, 'send') as mock_signal:
            self.test_instance.save()
            mock_signal.assert_called_once_with(
                sender=self.TestModel,
                instance=self.test_instance,
                created=True
            )

    def test_delete_method(self):
        """Test that the delete method works correctly."""
        self.test_instance.save()
        with patch.object(audit_log_signal, 'send') as mock_signal:
            self.test_instance.delete()
            mock_signal.assert_called_once_with(
                sender=self.TestModel,
                instance=self.test_instance,
                action='delete',
                user=None
            )


class TestTimeStampedModel(TestCase):
    """Test case for the TimeStampedModel abstract class."""

    def setUp(self):
        """Set up test data before each test method runs."""
        # Create a concrete model class that inherits from TimeStampedModel for testing
        class TestModel(TimeStampedModel):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'core'

        self.TestModel = TestModel
        self.test_instance = TestModel(name="Test Instance")

    def test_timestamps_on_creation(self):
        """Test that created_at and updated_at are set on creation."""
        self.test_instance.save()
        self.assertIsNotNone(self.test_instance.created_at)
        self.assertIsNotNone(self.test_instance.updated_at)
        # On creation, created_at and updated_at should be very close
        self.assertAlmostEqual(
            self.test_instance.created_at,
            self.test_instance.updated_at,
            delta=timezone.timedelta(seconds=1)
        )

    def test_updated_at_on_save(self):
        """Test that updated_at is updated on save."""
        self.test_instance.save()
        initial_updated_at = self.test_instance.updated_at
        initial_created_at = self.test_instance.created_at
        
        # Wait a short time to ensure the timestamps will be different
        import time
        time.sleep(0.1)
        
        self.test_instance.name = "Updated Name"
        self.test_instance.save()
        
        # updated_at should change
        self.assertNotEqual(self.test_instance.updated_at, initial_updated_at)
        # created_at should not change
        self.assertEqual(self.test_instance.created_at, initial_created_at)


class TestUUIDModel(TestCase):
    """Test case for the UUIDModel abstract class."""

    def setUp(self):
        """Set up test data before each test method runs."""
        # Create a concrete model class that inherits from UUIDModel for testing
        class TestModel(UUIDModel):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'core'

        self.TestModel = TestModel
        self.test_instance = TestModel(name="Test Instance")

    def test_id_is_uuid(self):
        """Test that the id field is a UUID."""
        self.test_instance.save()
        self.assertIsNotNone(self.test_instance.id)
        self.assertIsInstance(self.test_instance.id, uuid.UUID)

    def test_id_generation_on_save(self):
        """Test that a UUID is generated on save if not provided."""
        # Create a new instance without setting id
        instance = self.TestModel(name="Another Test")
        instance.save()
        self.assertIsNotNone(instance.id)
        self.assertIsInstance(instance.id, uuid.UUID)

    def test_custom_id_preserved(self):
        """Test that a custom UUID is preserved on save."""
        custom_uuid = uuid.uuid4()
        instance = self.TestModel(id=custom_uuid, name="Custom ID Test")
        instance.save()
        self.assertEqual(instance.id, custom_uuid)


class TestSoftDeleteModel(TestCase):
    """Test case for the SoftDeleteModel abstract class."""

    def setUp(self):
        """Set up test data before each test method runs."""
        # Create a concrete model class that inherits from SoftDeleteModel for testing
        class TestModel(SoftDeleteModel):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'core'

        self.TestModel = TestModel
        
        # Create and save multiple instances
        self.instance1 = TestModel(name="Test 1")
        self.instance1.save()
        self.instance2 = TestModel(name="Test 2")
        self.instance2.save()
        self.instance3 = TestModel(name="Test 3")
        self.instance3.save()

    def test_soft_delete(self):
        """Test that soft delete sets is_deleted flag and deleted_at timestamp."""
        self.instance1.delete()
        
        # Retrieve the instance again from the database to verify changes
        refreshed_instance = self.TestModel.all_objects.get(pk=self.instance1.pk)
        
        self.assertTrue(refreshed_instance.is_deleted)
        self.assertIsNotNone(refreshed_instance.deleted_at)
        
        # Verify it still exists in the database
        self.assertEqual(self.TestModel.all_objects.filter(pk=self.instance1.pk).count(), 1)

    def test_hard_delete(self):
        """Test that hard delete actually removes the record."""
        instance_pk = self.instance2.pk
        self.instance2.delete(hard_delete=True)
        
        # Verify it no longer exists in the database
        self.assertEqual(self.TestModel.all_objects.filter(pk=instance_pk).count(), 0)

    def test_restore(self):
        """Test that restore method unsets is_deleted flag and deleted_at timestamp."""
        self.instance3.delete()
        
        # Verify it's deleted
        refreshed_instance = self.TestModel.all_objects.get(pk=self.instance3.pk)
        self.assertTrue(refreshed_instance.is_deleted)
        
        # Restore it
        refreshed_instance.restore()
        
        # Verify it's restored
        re_refreshed_instance = self.TestModel.all_objects.get(pk=self.instance3.pk)
        self.assertFalse(re_refreshed_instance.is_deleted)
        self.assertIsNone(re_refreshed_instance.deleted_at)

    def test_active_manager(self):
        """Test that the default manager filters out soft-deleted objects."""
        # Count before deletion
        count_before = self.TestModel.objects.count()
        
        # Soft delete one object
        self.instance1.delete()
        
        # Count after deletion
        count_after = self.TestModel.objects.count()
        
        # Verify count decreased by 1
        self.assertEqual(count_before - 1, count_after)
        
        # Verify deleted object is not in the queryset
        self.assertNotIn(self.instance1, self.TestModel.objects.all())

    def test_all_objects_manager(self):
        """Test that the all_objects manager includes soft-deleted objects."""
        # Count before deletion using all_objects
        count_before = self.TestModel.all_objects.count()
        
        # Soft delete one object
        self.instance1.delete()
        
        # Count after deletion using all_objects
        count_after = self.TestModel.all_objects.count()
        
        # Verify count remains the same
        self.assertEqual(count_before, count_after)
        
        # Verify deleted object is in the queryset
        self.assertIn(
            self.instance1.pk, 
            [obj.pk for obj in self.TestModel.all_objects.all()]
        )


class TestAuditableModel(TestCase):
    """Test case for the AuditableModel abstract class."""

    def setUp(self):
        """Set up test data before each test method runs."""
        # Create a concrete model class that inherits from AuditableModel for testing
        class TestModel(AuditableModel):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'core'

        self.TestModel = TestModel
        
        # Create a test user for auditing
        User = get_user_model()
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        self.test_instance = TestModel(name="Test Instance")

    def test_created_by_on_save(self):
        """Test that created_by is set on initial save."""
        self.test_instance.save(user=self.test_user)
        self.assertEqual(self.test_instance.created_by, self.test_user)

    def test_updated_by_on_save(self):
        """Test that updated_by is set on save."""
        self.test_instance.save(user=self.test_user)
        
        # Create a second user
        User = get_user_model()
        second_user = User.objects.create_user(
            username='seconduser',
            email='second@example.com',
            password='password123'
        )
        
        self.test_instance.name = "Updated Name"
        self.test_instance.save(user=second_user)
        
        # updated_by should be set to the second user
        self.assertEqual(self.test_instance.updated_by, second_user)
        # created_by should still be the first user
        self.assertEqual(self.test_instance.created_by, self.test_user)

    def test_save_without_user(self):
        """Test that save works without providing a user."""
        self.test_instance.save()  # No user parameter
        
        # Save should complete without errors
        self.assertIsNone(self.test_instance.created_by)
        self.assertIsNone(self.test_instance.updated_by)


class TestCoreModel(TestCase):
    """Test case for the CoreModel concrete class."""

    def setUp(self):
        """Set up test data before each test method runs."""
        # Create a test user for auditing
        User = get_user_model()
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a concrete model class that inherits from CoreModel for testing
        class TestModel(CoreModel):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'core'
        
        self.TestModel = TestModel
        self.test_instance = TestModel(name="Test Instance")

    def test_inheritance(self):
        """Test that CoreModel inherits from all the expected base classes."""
        self.assertTrue(issubclass(CoreModel, UUIDModel))
        self.assertTrue(issubclass(CoreModel, TimeStampedModel))
        self.assertTrue(issubclass(CoreModel, SoftDeleteModel))
        self.assertTrue(issubclass(CoreModel, AuditableModel))

    def test_core_model_functionality(self):
        """Test that CoreModel has all the expected functionality."""
        # Save with a user
        self.test_instance.save(user=self.test_user)
        
        # Test UUIDModel functionality
        self.assertIsInstance(self.test_instance.id, uuid.UUID)
        
        # Test TimeStampedModel functionality
        self.assertIsNotNone(self.test_instance.created_at)
        self.assertIsNotNone(self.test_instance.updated_at)
        
        # Test AuditableModel functionality
        self.assertEqual(self.test_instance.created_by, self.test_user)
        
        # Test SoftDeleteModel functionality
        self.assertFalse(self.test_instance.is_deleted)
        
        # Test soft delete
        self.test_instance.delete()
        
        # Refresh from database
        refreshed_instance = self.TestModel.all_objects.get(pk=self.test_instance.pk)
        
        self.assertTrue(refreshed_instance.is_deleted)
        self.assertIsNotNone(refreshed_instance.deleted_at)
        
        # Test restore
        refreshed_instance.restore()
        
        # Refresh from database again
        re_refreshed_instance = self.TestModel.all_objects.get(pk=self.test_instance.pk)
        
        self.assertFalse(re_refreshed_instance.is_deleted)
        self.assertIsNone(re_refreshed_instance.deleted_at)


class TestModelManagers(TestCase):
    """Test case for the ActiveManager and AllObjectsManager classes."""

    def setUp(self):
        """Set up test data before each test method runs."""
        # Create a concrete model class with both managers for testing
        class TestModel(SoftDeleteModel):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'core'

        self.TestModel = TestModel
        
        # Create and save multiple instances
        self.instance1 = TestModel(name="Test 1")
        self.instance1.save()
        self.instance2 = TestModel(name="Test 2")
        self.instance2.save()
        self.instance3 = TestModel(name="Test 3")
        self.instance3.save()
        
        # Soft delete some instances
        self.instance1.delete()  # Use the soft delete method

    def test_active_manager_get_queryset(self):
        """Test that ActiveManager.get_queryset filters out soft-deleted objects."""
        # Get queryset from the objects manager (ActiveManager)
        queryset = self.TestModel.objects.all()
        
        # Assert that the queryset only includes non-deleted objects
        self.assertEqual(queryset.count(), 2)
        
        # Assert that all objects in the queryset have is_deleted=False
        for obj in queryset:
            self.assertFalse(obj.is_deleted)

    def test_all_objects_manager_get_queryset(self):
        """Test that AllObjectsManager.get_queryset includes all objects."""
        # Get queryset from the all_objects manager (AllObjectsManager)
        queryset = self.TestModel.all_objects.all()
        
        # Assert that the queryset includes all objects
        self.assertEqual(queryset.count(), 3)
        
        # Assert that the queryset includes both deleted and non-deleted objects
        deleted_count = sum(1 for obj in queryset if obj.is_deleted)
        non_deleted_count = sum(1 for obj in queryset if not obj.is_deleted)
        
        self.assertEqual(deleted_count, 1)
        self.assertEqual(non_deleted_count, 2)


class TestModelSignals(TestCase):
    """Test case for the model signals defined in core models."""

    def setUp(self):
        """Set up test data before each test method runs."""
        # Create a concrete model class for testing
        class TestModel(BaseModel):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'core'

        self.TestModel = TestModel
        
        # Create signal receiver functions for testing
        self.model_change_called = False
        self.model_change_instance = None
        self.model_change_created = None
        
        self.audit_log_called = False
        self.audit_log_instance = None
        self.audit_log_action = None
        self.audit_log_user = None
        
        # Define receiver functions
        def model_change_receiver(sender, instance, created, **kwargs):
            self.model_change_called = True
            self.model_change_instance = instance
            self.model_change_created = created
        
        def audit_log_receiver(sender, instance, action, user, **kwargs):
            self.audit_log_called = True
            self.audit_log_instance = instance
            self.audit_log_action = action
            self.audit_log_user = user
        
        # Connect receivers to signals
        self.model_change_receiver = model_change_receiver
        self.audit_log_receiver = audit_log_receiver
        
        model_change_signal.connect(self.model_change_receiver)
        audit_log_signal.connect(self.audit_log_receiver)

    def tearDown(self):
        """Clean up after each test method runs."""
        # Disconnect signal receivers
        model_change_signal.disconnect(self.model_change_receiver)
        audit_log_signal.disconnect(self.audit_log_receiver)

    def test_model_change_signal(self):
        """Test that model_change_signal is emitted on save."""
        # Reset flags
        self.model_change_called = False
        
        # Create and save a new instance
        instance = self.TestModel(name="Test Signal")
        instance.save()
        
        # Assert that the signal was received
        self.assertTrue(self.model_change_called)
        self.assertEqual(self.model_change_instance, instance)
        self.assertTrue(self.model_change_created)
        
        # Reset flags
        self.model_change_called = False
        
        # Update and save the instance
        instance.name = "Updated Name"
        instance.save()
        
        # Assert that the signal was received for update
        self.assertTrue(self.model_change_called)
        self.assertEqual(self.model_change_instance, instance)
        self.assertFalse(self.model_change_created)

    def test_audit_log_signal(self):
        """Test that audit_log_signal is emitted on delete."""
        # Reset flags
        self.audit_log_called = False
        
        # Create and save a new instance
        instance = self.TestModel(name="Test Signal")
        instance.save()
        
        # Delete the instance
        instance.delete()
        
        # Assert that the signal was received
        self.assertTrue(self.audit_log_called)
        self.assertEqual(self.audit_log_instance, instance)
        self.assertEqual(self.audit_log_action, 'delete')
        self.assertIsNone(self.audit_log_user)