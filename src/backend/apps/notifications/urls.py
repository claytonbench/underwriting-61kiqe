from django.urls import path  # django.urls 4.2+
from .views import (  # src/backend/apps/notifications/views.py
    NotificationTemplateListCreateView,
    NotificationTemplateDetailView,
    NotificationEventMappingListCreateView,
    NotificationEventMappingDetailView,
    NotificationListView,
    NotificationDetailView,
    NotificationCreateView,
    NotificationBulkCreateView,
    NotificationStatusUpdateView,
    TemplatePreviewView,
    ProcessPendingEventsView,
    SendPendingNotificationsView,
    UserNotificationsView,
    MarkNotificationReadView
)

# Define the app namespace
app_name = "notifications"

# Define URL patterns for the notifications app
urlpatterns = [
    # URL for listing and creating notification templates
    path('templates/', NotificationTemplateListCreateView.as_view(), name='notification-template-list-create'),

    # URL for retrieving, updating, and deleting a specific notification template
    path('templates/<uuid:pk>/', NotificationTemplateDetailView.as_view(), name='notification-template-detail'),

    # URL for previewing a rendered notification template
    path('templates/preview/', TemplatePreviewView.as_view(), name='template-preview'),

    # URL for listing and creating notification event mappings
    path('event-mappings/', NotificationEventMappingListCreateView.as_view(), name='notification-event-mapping-list-create'),

    # URL for retrieving, updating, and deleting a specific notification event mapping
    path('event-mappings/<uuid:pk>/', NotificationEventMappingDetailView.as_view(), name='notification-event-mapping-detail'),

    # URL for listing notifications
    path('', NotificationListView.as_view(), name='notification-list'),

    # URL for retrieving a specific notification
    path('<uuid:pk>/', NotificationDetailView.as_view(), name='notification-detail'),

    # URL for creating a new notification
    path('create/', NotificationCreateView.as_view(), name='notification-create'),

    # URL for bulk creating notifications
    path('bulk-create/', NotificationBulkCreateView.as_view(), name='notification-bulk-create'),

    # URL for updating the status of a notification
    path('<uuid:pk>/status/', NotificationStatusUpdateView.as_view(), name='notification-status-update'),

    # URL for processing pending notification events
    path('process-events/', ProcessPendingEventsView.as_view(), name='process-pending-events'),

    # URL for sending pending notifications
    path('send-pending/', SendPendingNotificationsView.as_view(), name='send-pending-notifications'),

    # URL for retrieving notifications for the current user
    path('user/', UserNotificationsView.as_view(), name='user-notifications'),

    # URL for marking a notification as read for the current user
    path('user/<uuid:pk>/mark-read/', MarkNotificationReadView.as_view(), name='mark-notification-read'),
]