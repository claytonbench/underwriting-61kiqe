"""
Implements API views for the notification system in the loan management application. These views handle notification template management, notification creation, status updates, event processing, and user notification retrieval. The views enforce appropriate permissions and provide endpoints for both system-level notification management and user-facing notification functionality.
"""

import logging  # standard library
from rest_framework import generics  # rest_framework 3.14+
from rest_framework.response import Response  # rest_framework 3.14+
from rest_framework import status  # rest_framework 3.14+
from rest_framework.generics import ListCreateAPIView  # rest_framework 3.14+
from rest_framework.generics import RetrieveUpdateDestroyAPIView  # rest_framework 3.14+
from rest_framework.generics import ListAPIView  # rest_framework 3.14+
from rest_framework.generics import RetrieveAPIView  # rest_framework 3.14+
from rest_framework.generics import CreateAPIView  # rest_framework 3.14+
from rest_framework.generics import UpdateAPIView  # rest_framework 3.14+
from django.db.models import Q  # Django 4.2+

from core.views import BaseGenericAPIView, BaseAPIView, TransactionMixin, AuditLogMixin  # src/backend/core/views.py
from .models import NotificationTemplate, NotificationEvent, NotificationEventMapping, Notification  # src/backend/apps/notifications/models.py
from .serializers import NotificationTemplateSerializer, NotificationTemplateDetailSerializer, NotificationEventSerializer, NotificationEventMappingSerializer, NotificationSerializer, NotificationDetailSerializer, NotificationCreateSerializer, NotificationBulkCreateSerializer, NotificationStatusUpdateSerializer, TemplatePreviewSerializer  # src/backend/apps/notifications/serializers.py
from .services import NotificationService  # src/backend/apps/notifications/services.py
from core.permissions import IsSystemAdmin, IsAuthenticated, IsInternalUser, IsOwner  # src/backend/core/permissions.py

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize notification service
notification_service = NotificationService()


class NotificationTemplateListCreateView(BaseGenericAPIView, ListCreateAPIView):
    """
    View for listing and creating notification templates
    """
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsSystemAdmin]

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from ListCreateAPIView"""
        super().__init__(*args, **kwargs)

    def perform_create(self, serializer):
        """
        Override perform_create to add the current user as created_by

        Args:
            serializer (NotificationTemplateSerializer): NotificationTemplateSerializer

        Returns:
            NotificationTemplate: Created notification template
        """
        serializer.save(created_by=self.request.user)
        return serializer.instance


class NotificationTemplateDetailView(BaseGenericAPIView, RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, and deleting notification templates
    """
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateDetailSerializer
    permission_classes = [IsSystemAdmin]

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from RetrieveUpdateDestroyAPIView"""
        super().__init__(*args, **kwargs)

    def perform_update(self, serializer):
        """
        Override perform_update to add the current user as updated_by

        Args:
            serializer (NotificationTemplateDetailSerializer): NotificationTemplateDetailSerializer

        Returns:
            NotificationTemplate: Updated notification template
        """
        serializer.save(updated_by=self.request.user)
        return serializer.instance


class NotificationEventMappingListCreateView(BaseGenericAPIView, ListCreateAPIView):
    """
    View for listing and creating notification event mappings
    """
    queryset = NotificationEventMapping.objects.all()
    serializer_class = NotificationEventMappingSerializer
    permission_classes = [IsSystemAdmin]

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from ListCreateAPIView"""
        super().__init__(*args, **kwargs)

    def perform_create(self, serializer):
        """
        Override perform_create to add the current user as created_by

        Args:
            serializer (NotificationEventMappingSerializer): NotificationEventMappingSerializer

        Returns:
            NotificationEventMapping: Created notification event mapping
        """
        serializer.save(created_by=self.request.user)
        return serializer.instance


class NotificationEventMappingDetailView(BaseGenericAPIView, RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, and deleting notification event mappings
    """
    queryset = NotificationEventMapping.objects.all()
    serializer_class = NotificationEventMappingSerializer
    permission_classes = [IsSystemAdmin]

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from RetrieveUpdateDestroyAPIView"""
        super().__init__(*args, **kwargs)

    def perform_update(self, serializer):
        """
        Override perform_update to add the current user as updated_by

        Args:
            serializer (NotificationEventMappingSerializer): NotificationEventMappingSerializer

        Returns:
            NotificationEventMapping: Updated notification event mapping
        """
        serializer.save(updated_by=self.request.user)
        return serializer.instance


class NotificationListView(BaseGenericAPIView, ListAPIView):
    """
    View for listing notifications with filtering
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsInternalUser]

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from ListAPIView"""
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        """
        Override get_queryset to apply filters

        Returns:
            QuerySet: Filtered notification queryset
        """
        queryset = super().get_queryset()

        # Apply filters from query parameters
        status_filter = self.request.query_params.get('status')
        recipient_filter = self.request.query_params.get('recipient')
        template_filter = self.request.query_params.get('template')
        event_filter = self.request.query_params.get('event')
        application_filter = self.request.query_params.get('application')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if recipient_filter:
            queryset = queryset.filter(recipient=recipient_filter)
        if template_filter:
            queryset = queryset.filter(template=template_filter)
        if event_filter:
            queryset = queryset.filter(event=event_filter)
        if application_filter:
            queryset = queryset.filter(application=application_filter)

        return queryset


class NotificationDetailView(BaseGenericAPIView, RetrieveAPIView):
    """
    View for retrieving notification details
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationDetailSerializer
    permission_classes = [IsInternalUser | IsOwner]

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from RetrieveAPIView"""
        super().__init__(*args, **kwargs)


class NotificationCreateView(BaseGenericAPIView, CreateAPIView):
    """
    View for creating notifications
    """
    serializer_class = NotificationCreateSerializer
    permission_classes = [IsInternalUser]

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from CreateAPIView"""
        super().__init__(*args, **kwargs)

    def perform_create(self, serializer):
        """
        Override perform_create to use the notification service

        Args:
            serializer (NotificationCreateSerializer): NotificationCreateSerializer

        Returns:
            Notification: Created notification
        """
        serializer.save()
        return serializer.instance


class NotificationBulkCreateView(BaseAPIView):
    """
    View for creating multiple notifications at once
    """
    serializer_class = NotificationBulkCreateSerializer
    permission_classes = [IsInternalUser]

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from BaseAPIView"""
        super().__init__(*args, **kwargs)

    def post(self, request):
        """
        Handle POST requests for bulk notification creation

        Args:
            request (Request): Request

        Returns:
            Response: Response with created notifications
        """
        serializer = NotificationBulkCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            notifications = serializer.save()
            return Response(NotificationSerializer(notifications, many=True).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationStatusUpdateView(BaseGenericAPIView, UpdateAPIView):
    """
    View for updating notification status
    """
    serializer_class = NotificationStatusUpdateSerializer
    permission_classes = [IsInternalUser]
    queryset = Notification.objects.all()

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from UpdateAPIView"""
        super().__init__(*args, **kwargs)

    def perform_update(self, serializer):
        """
        Override perform_update to use the status update serializer

        Args:
            serializer (NotificationStatusUpdateSerializer): NotificationStatusUpdateSerializer

        Returns:
            Notification: Updated notification
        """
        notification = self.get_object()
        serializer.update_status(notification, serializer.validated_data)
        return notification


class TemplatePreviewView(BaseAPIView):
    """
    View for previewing rendered notification templates
    """
    serializer_class = TemplatePreviewSerializer
    permission_classes = [IsInternalUser]

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from BaseAPIView"""
        super().__init__(*args, **kwargs)

    def post(self, request):
        """
        Handle POST requests for template previews

        Args:
            request (Request): Request

        Returns:
            Response: Response with rendered template preview
        """
        serializer = TemplatePreviewSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            preview = serializer.preview(serializer.validated_data)
            return Response(preview, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProcessPendingEventsView(BaseAPIView):
    """
    View for processing pending notification events
    """
    permission_classes = [IsSystemAdmin]

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from BaseAPIView"""
        super().__init__(*args, **kwargs)

    def post(self, request):
        """
        Handle POST requests to process pending events

        Args:
            request (Request): Request

        Returns:
            Response: Response with processing results
        """
        result = notification_service.process_pending_events()
        return Response(result, status=status.HTTP_200_OK)


class SendPendingNotificationsView(BaseAPIView):
    """
    View for sending pending notifications
    """
    permission_classes = [IsSystemAdmin]

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from BaseAPIView"""
        super().__init__(*args, **kwargs)

    def post(self, request):
        """
        Handle POST requests to send pending notifications

        Args:
            request (Request): Request

        Returns:
            Response: Response with sending results
        """
        # Query for pending notifications
        pending_notifications = Notification.objects.filter(status='pending')
        
        # Process each notification
        success_count = 0
        failure_count = 0
        for notification in pending_notifications:
            if notification_service.send_notification(notification):
                success_count += 1
            else:
                failure_count += 1
        
        # Return response with sending statistics
        result = {
            'success_count': success_count,
            'failure_count': failure_count,
            'total_count': pending_notifications.count()
        }
        return Response(result, status=status.HTTP_200_OK)


class UserNotificationsView(BaseGenericAPIView, ListAPIView):
    """
    View for retrieving notifications for the current user
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from ListAPIView"""
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        """
        Override get_queryset to filter by current user

        Returns:
            QuerySet: User's notification queryset
        """
        user = self.request.user
        queryset = Notification.objects.filter(recipient=user)

        # Apply additional filters (read status, date range, etc.)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset


class MarkNotificationReadView(BaseAPIView):
    """
    View for marking a notification as read
    """
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()

    def __init__(self, *args, **kwargs):
        """Default constructor inherited from BaseAPIView"""
        super().__init__(*args, **kwargs)

    def post(self, request, pk):
        """
        Handle POST requests to mark notification as read

        Args:
            request (Request): Request
            pk (UUID): UUID

        Returns:
            Response: Response with success status
        """
        try:
            # Get notification by pk
            notification = self.queryset.get(pk=pk)

            # Verify the notification belongs to the current user
            if notification.recipient != request.user:
                return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

            # Update notification read status
            notification.status = 'read'  # Assuming you have a 'read' status
            notification.save()

            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({'detail': 'Notification not found.'}, status=status.HTTP_404_NOT_FOUND)