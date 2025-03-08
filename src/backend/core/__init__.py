"""
Core module for the loan management system.

This module serves as the central hub for core functionality and components used
throughout the loan management system. It provides base classes, utilities, and
constants that ensure consistency, maintainability, and code reuse across the
application.
"""

# Version identifier for the core module
__version__ = "1.0.0"

# Base model classes and managers
from .models import (
    BaseModel, 
    TimeStampedModel, 
    UUIDModel, 
    SoftDeleteModel, 
    AuditableModel,
    ActiveManager, 
    AllObjectsManager
)

# Exception classes and error handling utilities
from .exceptions import (
    BaseException,
    ValidationException,
    PermissionException,
    AuthenticationException,
    ResourceNotFoundException,
    BusinessRuleException,
    format_exception_response
)

# Permission classes and utilities
from .permissions import (
    USER_ROLES,
    has_object_permission_or_403,
    IsSystemAdmin,
    IsUnderwriter,
    IsQualityControl,
    IsSchoolAdmin,
    IsBorrower,
    IsCoBorrower
)

# Serializer classes and validation utilities
from .serializers import (
    BaseSerializer,
    BaseModelSerializer,
    ReadOnlyModelSerializer,
    validate_required_fields
)

# View classes and response formatting utilities
from .views import (
    BaseAPIView,
    BaseGenericAPIView,
    TransactionMixin,
    ReadOnlyViewMixin,
    format_success_response,
    format_error_response
)

# Signal definitions and utilities
from .signals import (
    model_change_signal,
    audit_log_signal,
    log_user_action
)

# Middleware components
from .middleware import (
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    ExceptionMiddleware,
    AuditMiddleware
)