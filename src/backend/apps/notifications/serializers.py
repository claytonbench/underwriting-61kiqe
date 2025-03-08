"""
Implements serializers for the notification system in the loan management application. These serializers handle the conversion of notification models to JSON for API responses and validate incoming data for API requests. The serializers support operations for notification templates, notification events, notification records, and template previews.
"""

from rest_framework import serializers  # rest_framework 3.14+
from rest_framework.exceptions import ValidationError  # rest_framework 3.14+

from core.serializers import BaseModelSerializer, AuditFieldsMixin, ValidationException  # src/backend/core/serializers.py
from .models import NotificationTemplate, NotificationEvent, NotificationEventMapping, Notification  # src/backend/apps/notifications/models.py
from apps.users.models import User  # src/backend/apps/users/models.py
from apps.applications.models import LoanApplication  # src/backend/apps/applications/models.py
from .constants import NOTIFICATION_TYPES, NOTIFICATION_STATUS, NOTIFICATION_DELIVERY_METHODS, NOTIFICATION_PRIORITIES, NOTIFICATION_CATEGORIES, EMAIL_TEMPLATES, EVENT_TYPE  # src/backend/apps/notifications/constants.py
from .services import NotificationService  # src/backend/apps/notifications/services.py

notification_service = NotificationService()


class NotificationTemplateSerializer(BaseModelSerializer):
    """
    Serializer for notification templates
    """
    class Meta:
        model = NotificationTemplate
        fields = ['id', 'name', 'description', 'subject_template', 'body_template', 'notification_type', 'is_active', 'template_path', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from BaseModelSerializer"""
        super().__init__(*args, **kwargs)

    def validate(self, data: dict) -> dict:
        """Validates the template data"""
        if 'notification_type' in data and data['notification_type'] not in NOTIFICATION_TYPES:
            raise ValidationError("Invalid notification type")

        if 'template_path' in data and data['template_path']:
            # Add validation logic for template_path if needed
            pass  # Placeholder for template path validation

        if 'template_path' not in data or not data.get('template_path'):
            if 'subject_template' not in data or 'body_template' not in data:
                raise ValidationError("Both subject_template and body_template are required when template_path is not provided")

        return data

    def get_template_variables(self, obj: NotificationTemplate) -> list:
        """Gets the available template variables"""
        # Add logic to extract variable names from the template
        # This is a placeholder and should be implemented based on your template engine
        return ["variable1", "variable2"]


class NotificationTemplateDetailSerializer(NotificationTemplateSerializer):
    """
    Detailed serializer for notification templates
    """
    template_variables = serializers.SerializerMethodField()

    class Meta:
        model = NotificationTemplate
        fields = ['id', 'name', 'description', 'subject_template', 'body_template', 'notification_type', 'is_active', 'template_path', 'created_at', 'updated_at', 'created_by', 'updated_by']

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from NotificationTemplateSerializer"""
        super().__init__(*args, **kwargs)

    def get_template_variables(self, obj: NotificationTemplate) -> list:
        """Gets the available template variables"""
        # Add logic to extract variable names from the template
        # This is a placeholder and should be implemented based on your template engine
        return ["variable1", "variable2"]


class NotificationEventSerializer(BaseModelSerializer):
    """
    Serializer for notification events
    """
    class Meta:
        model = NotificationEvent
        fields = ['id', 'event_type', 'entity_id', 'entity_type', 'triggered_by', 'context_data', 'processed', 'processed_at', 'created_at']

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from BaseModelSerializer"""
        super().__init__(*args, **kwargs)

    def validate_event_type(self, event_type: str) -> str:
        """Validates the event type"""
        if event_type not in EVENT_TYPE:
            raise ValidationError("Invalid event type")
        return event_type


class NotificationEventMappingSerializer(BaseModelSerializer):
    """
    Serializer for notification event mappings
    """
    class Meta:
        model = NotificationEventMapping
        fields = ['id', 'event_type', 'template', 'recipient_type', 'priority', 'is_active', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from BaseModelSerializer"""
        super().__init__(*args, **kwargs)

    def validate(self, data: dict) -> dict:
        """Validates the event mapping data"""
        if 'event_type' in data and data['event_type'] not in EVENT_TYPE:
            raise ValidationError("Invalid event type")
        if 'template' in data and not NotificationTemplate.objects.filter(id=data['template'].id).exists():
            raise ValidationError("Invalid template")
        if 'priority' in data and data['priority'] not in NOTIFICATION_PRIORITIES:
            raise ValidationError("Invalid priority")
        return data


class NotificationSerializer(BaseModelSerializer):
    """
    Serializer for notifications
    """
    template_name = serializers.SerializerMethodField()
    recipient_name = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'template', 'recipient', 'recipient_email', 'subject', 'status', 'delivery_method', 'priority', 'category', 'event', 'application', 'created_at', 'sent_at']

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from BaseModelSerializer"""
        super().__init__(*args, **kwargs)

    def get_template_name(self, obj: Notification) -> str:
        """Gets the template name"""
        return obj.template.name if obj.template else None

    def get_recipient_name(self, obj: Notification) -> str:
        """Gets the recipient name"""
        return f"{obj.recipient.first_name} {obj.recipient.last_name}" if obj.recipient else None


class NotificationDetailSerializer(NotificationSerializer):
    """
    Detailed serializer for notifications
    """
    template_name = serializers.SerializerMethodField()
    recipient_name = serializers.SerializerMethodField()
    application_details = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'template', 'recipient', 'recipient_email', 'subject', 'body', 'status', 'delivery_method', 'priority', 'category', 'event', 'application', 'created_at', 'sent_at', 'error_message', 'retry_count', 'last_retry_at']

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from NotificationSerializer"""
        super().__init__(*args, **kwargs)

    def get_application_details(self, obj: Notification) -> dict:
        """Gets the application details"""
        if not obj.application:
            return None

        return {
            'id': str(obj.application.id),
            'borrower_name': f"{obj.application.borrower.first_name} {obj.application.borrower.last_name}",
            'school': obj.application.school.name if obj.application.school else None,
            'program': obj.application.program.name if obj.application.program else None,
        }


class NotificationCreateSerializer(serializers.Serializer):
    """
    Serializer for creating notifications
    """
    template_id = serializers.UUIDField()
    recipient_id = serializers.UUIDField()
    context = serializers.DictField(required=False)
    event_id = serializers.UUIDField(required=False)
    application_id = serializers.UUIDField(required=False)
    delivery_method = serializers.ChoiceField(choices=NOTIFICATION_DELIVERY_METHODS.items(), default='email')
    priority = serializers.ChoiceField(choices=NOTIFICATION_PRIORITIES.items(), default='medium')
    category = serializers.ChoiceField(choices=NOTIFICATION_CATEGORIES.items(), default='system')

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from serializers.Serializer"""
        super().__init__(*args, **kwargs)

    def validate(self, data: dict) -> dict:
        """Validates the notification creation data"""
        if not NotificationTemplate.objects.filter(id=data['template_id']).exists():
            raise ValidationError("Invalid template_id")
        if not User.objects.filter(id=data['recipient_id']).exists():
            raise ValidationError("Invalid recipient_id")
        if 'event_id' in data and data['event_id'] and not NotificationEvent.objects.filter(id=data['event_id']).exists():
            raise ValidationError("Invalid event_id")
        if 'application_id' in data and data['application_id'] and not LoanApplication.objects.filter(id=data['application_id']).exists():
            raise ValidationError("Invalid application_id")
        return data

    def create(self, validated_data: dict) -> Notification:
        """Creates a notification"""
        template = NotificationTemplate.objects.get(id=validated_data['template_id'])
        recipient = User.objects.get(id=validated_data['recipient_id'])
        event = NotificationEvent.objects.get(id=validated_data.get('event_id')) if validated_data.get('event_id') else None
        application = LoanApplication.objects.get(id=validated_data.get('application_id')) if validated_data.get('application_id') else None
        context = validated_data.get('context', {})
        delivery_method = validated_data.get('delivery_method')
        priority = validated_data.get('priority')
        category = validated_data.get('category')

        notification = notification_service.create_notification(
            template=template,
            recipient=recipient,
            context=context,
            application=application,
            event=event,
            delivery_method=delivery_method,
            priority=priority,
            category=category
        )
        return notification


class NotificationBulkCreateSerializer(serializers.Serializer):
    """
    Serializer for bulk creating notifications
    """
    notifications = serializers.ListField(child=NotificationCreateSerializer())

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from serializers.Serializer"""
        super().__init__(*args, **kwargs)

    def create(self, validated_data: dict) -> list:
        """Creates multiple notifications"""
        notifications_data = validated_data.get('notifications')
        created_notifications = []
        for notification_data in notifications_data:
            serializer = NotificationCreateSerializer(data=notification_data)
            if serializer.is_valid(raise_exception=True):
                notification = serializer.create(serializer.validated_data)
                created_notifications.append(notification)
        return created_notifications


class NotificationStatusUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating notification status
    """
    status = serializers.ChoiceField(choices=NOTIFICATION_STATUS.items())
    error_message = serializers.CharField(required=False, allow_blank=True)

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from serializers.Serializer"""
        super().__init__(*args, **kwargs)

    def validate_status(self, status: str) -> str:
        """Validates the status value"""
        if status not in NOTIFICATION_STATUS:
            raise ValidationError("Invalid status")
        return status

    def update_status(self, notification: Notification, validated_data: dict) -> Notification:
        """Updates the notification status"""
        status = validated_data.get('status')
        if status == 'sent':
            notification.mark_sent()
        elif status == 'failed':
            error_message = validated_data.get('error_message', '')
            notification.mark_failed(error_message)
        else:
            notification.status = status
            notification.save()
        return notification


class TemplatePreviewSerializer(serializers.Serializer):
    """
    Serializer for previewing notification templates
    """
    template_id = serializers.UUIDField(required=False)
    notification_type = serializers.ChoiceField(choices=NOTIFICATION_TYPES.items(), required=False)
    subject_template = serializers.CharField(required=False)
    body_template = serializers.CharField(required=False)
    context = serializers.DictField(required=True)

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from serializers.Serializer"""
        super().__init__(*args, **kwargs)

    def validate(self, data: dict) -> dict:
        """Validates the template preview data"""
        if 'template_id' not in data and ('subject_template' not in data or 'body_template' not in data) and 'notification_type' not in data:
            raise ValidationError("Either template_id, notification_type, or both subject_template and body_template must be provided")

        if 'template_id' in data and not NotificationTemplate.objects.filter(id=data['template_id']).exists():
            raise ValidationError("Invalid template_id")

        if 'notification_type' in data and data['notification_type'] not in NOTIFICATION_TYPES:
            raise ValidationError("Invalid notification_type")

        return data

    def preview(self, validated_data: dict) -> dict:
        """Generates a preview of the rendered template"""
        context = validated_data.get('context', {})
        template = None

        if 'template_id' in validated_data:
            template = NotificationTemplate.objects.get(id=validated_data['template_id'])
        elif 'notification_type' in validated_data:
            template = NotificationTemplate.objects.get(notification_type=validated_data['notification_type'])
        else:
            # Create a temporary template
            template = NotificationTemplate(
                subject_template=validated_data['subject_template'],
                body_template=validated_data['body_template'],
                notification_type='preview_template',
                name='Preview Template'
            )

        subject, body = template.render(context)
        return {'subject': subject, 'body': body}