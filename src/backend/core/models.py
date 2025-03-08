"""
Core abstract model classes for the loan management system.

This module defines abstract base model classes that provide common functionality
such as UUID primary keys, timestamps, soft deletion, and audit logging to ensure
consistency across the application's data layer.
"""

from django.db import models  # Django 4.2+
from django.utils import timezone  # Django 4.2+
import uuid  # standard library
from django.contrib.auth import get_user_model  # Django 4.2+
from django.dispatch import Signal  # Django 4.2+

# Signals for model changes and audit logging
# Note: providing_args is deprecated in Django 3.1+ but kept for compatibility
model_change_signal = Signal(providing_args=['instance', 'created'])
audit_log_signal = Signal(providing_args=['instance', 'action', 'user'])


class BaseModel(models.Model):
    """
    Abstract base model that all other models should inherit from.
    Provides basic functionality for all models.
    """
    class Meta:
        abstract = True

    def save(self, **kwargs):
        """
        Override of the save method to handle custom save logic.
        Emits model_change_signal if configured.
        
        Args:
            **kwargs: Additional keyword arguments to pass to the parent save method.
        """
        created = not self.pk  # Check if this is a new instance
        super().save(**kwargs)
        model_change_signal.send(sender=self.__class__, instance=self, created=created)

    def delete(self, **kwargs):
        """
        Override of the delete method to handle custom delete logic.
        Emits audit_log_signal for deletion if configured.
        
        Args:
            **kwargs: Additional keyword arguments to pass to the parent delete method.
            
        Returns:
            tuple: Tuple containing the number of deleted objects and a dictionary
                  of deleted objects by type.
        """
        result = super().delete(**kwargs)
        audit_log_signal.send(
            sender=self.__class__, 
            instance=self, 
            action='delete',
            user=kwargs.get('user')
        )
        return result


class TimeStampedModel(BaseModel):
    """
    Abstract model that adds created_at and updated_at timestamp fields.
    Automatically sets these fields when an object is created or updated.
    """
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class UUIDModel(BaseModel):
    """
    Abstract model that uses UUID as primary key instead of auto-incrementing ID.
    Automatically generates a UUID for new instances if not provided.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

    def save(self, **kwargs):
        """
        Override of the save method to generate UUID if not provided.
        Ensures all objects have a valid UUID as their primary key.
        
        Args:
            **kwargs: Additional keyword arguments to pass to the parent save method.
        """
        if not self.pk:  # New instance
            self.id = uuid.uuid4()
        super().save(**kwargs)


class ActiveManager(models.Manager):
    """
    Model manager that filters out soft-deleted objects.
    When using this manager, only non-deleted objects will be returned.
    """
    def get_queryset(self):
        """
        Override to filter out soft-deleted objects.
        
        Returns:
            QuerySet: QuerySet filtered to exclude soft-deleted objects.
        """
        return super().get_queryset().filter(is_deleted=False)


class AllObjectsManager(models.Manager):
    """
    Model manager that includes all objects, including soft-deleted ones.
    When using this manager, all objects will be returned regardless of deletion status.
    """
    def get_queryset(self):
        """
        Returns all objects without filtering.
        
        Returns:
            QuerySet: QuerySet including all objects.
        """
        return super().get_queryset()


class SoftDeleteModel(BaseModel):
    """
    Abstract model that implements soft deletion instead of actually removing records.
    Objects are marked as deleted but remain in the database for audit and recovery.
    """
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Use custom managers
    objects = ActiveManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def delete(self, hard_delete=False, **kwargs):
        """
        Override of delete method to perform soft deletion.
        Sets is_deleted to True and deleted_at to current time unless hard_delete is True.
        
        Args:
            hard_delete (bool): If True, performs an actual deletion instead of soft delete.
            **kwargs: Additional keyword arguments to pass to the parent delete method.
            
        Returns:
            tuple: Tuple containing the number of deleted objects and a dictionary
                  of deleted objects by type.
        """
        if hard_delete:
            return super().delete(**kwargs)
        
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
        
        audit_log_signal.send(
            sender=self.__class__, 
            instance=self, 
            action='soft_delete',
            user=kwargs.get('user')
        )
        
        # Simulate the response format of the delete method
        return (1, {f"{self._meta.label}": 1})

    def restore(self):
        """
        Method to restore a soft-deleted object.
        Sets is_deleted to False and deleted_at to None.
        """
        self.is_deleted = False
        self.deleted_at = None
        self.save()
        
        audit_log_signal.send(
            sender=self.__class__, 
            instance=self, 
            action='restore',
            user=None
        )


class AuditableModel(BaseModel):
    """
    Abstract model that tracks who created and updated records.
    Maintains references to the users who performed these actions.
    """
    created_by = models.ForeignKey(
        get_user_model(), 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
    )
    updated_by = models.ForeignKey(
        get_user_model(), 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated",
    )

    class Meta:
        abstract = True

    def save(self, user=None, **kwargs):
        """
        Override of save method to track user who created/updated the record.
        Sets created_by to user for new objects and updated_by for all saves if user is provided.
        
        Args:
            user (User): The user performing the save action.
            **kwargs: Additional keyword arguments to pass to the parent save method.
        """
        if not self.pk and user:  # New instance with user provided
            self.created_by = user
        if user:
            self.updated_by = user
        super().save(**kwargs)


class CoreModel(UUIDModel, TimeStampedModel, SoftDeleteModel, AuditableModel):
    """
    Concrete model class that combines UUIDModel, TimeStampedModel, SoftDeleteModel, and AuditableModel.
    Provides a complete set of core functionality for standard models in the system.
    """
    class Meta:
        abstract = True