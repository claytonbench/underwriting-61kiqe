# django.urls - version 4.2+
from django.urls import path, include  # Import path and include for URL configuration
# rest_framework.routers - version 3.14+
from rest_framework.routers import DefaultRouter  # Import DefaultRouter for ViewSet URL generation

from .views import (  # src/backend/apps/workflow/views.py
    WorkflowTransitionHistoryViewSet,
    WorkflowTaskViewSet,
    AutomaticTransitionScheduleViewSet,
    WorkflowConfigurationViewSet,
    WorkflowStateView,
    WorkflowTransitionView,
    ApplicationTransitionView,
    DocumentTransitionView,
    FundingTransitionView,
    process_automatic_transitions_view,
    process_document_expiration_view,
    process_sla_monitoring_view,
)

# Define the app namespace for URL namespacing
app_name = "workflow"

# Create a DefaultRouter instance
router = DefaultRouter()

def register_routes():
    """
    Registers ViewSets with the DefaultRouter to generate URL patterns
    """
    # Register WorkflowTransitionHistoryViewSet with the router using 'workflow-history' as the base name
    router.register(r'workflow-history', WorkflowTransitionHistoryViewSet, basename='workflow-history')
    # Register WorkflowTaskViewSet with the router using 'workflow-tasks' as the base name
    router.register(r'workflow-tasks', WorkflowTaskViewSet, basename='workflow-tasks')
    # Register AutomaticTransitionScheduleViewSet with the router using 'automatic-transitions' as the base name
    router.register(r'automatic-transitions', AutomaticTransitionScheduleViewSet, basename='automatic-transitions')
    # Register WorkflowConfigurationViewSet with the router using 'workflow-configuration' as the base name
    router.register(r'workflow-configuration', WorkflowConfigurationViewSet, basename='workflow-configuration')

# Call the function to register the routes
register_routes()

# Define the URL patterns for the workflow app
urlpatterns = [
    # Include the router-generated URLs
    path('', include(router.urls)),
    # Define a URL pattern for retrieving workflow state information
    path('state/<str:content_type_id>/<str:object_id>/', WorkflowStateView.as_view(), name='workflow-state'),
    # Define a URL pattern for initiating a workflow transition
    path('transition/<str:content_type_id>/<str:object_id>/', WorkflowTransitionView.as_view(), name='workflow-transition'),
    # Define a URL pattern for application-specific transitions
    path('application/<str:content_type_id>/<str:object_id>/<str:transition_type>/', ApplicationTransitionView.as_view(), name='application-transition'),
    # Define a URL pattern for document-specific transitions
    path('document/<str:content_type_id>/<str:object_id>/<str:transition_type>/', DocumentTransitionView.as_view(), name='document-transition'),
    # Define a URL pattern for funding-specific transitions
    path('funding/<str:content_type_id>/<str:object_id>/<str:transition_type>/', FundingTransitionView.as_view(), name='funding-transition'),
    # Define a URL pattern for processing automatic transitions
    path('process-automatic-transitions/', process_automatic_transitions_view, name='process-automatic-transitions'),
    # Define a URL pattern for processing document expiration
    path('process-document-expiration/', process_document_expiration_view, name='process-document-expiration'),
    # Define a URL pattern for processing SLA monitoring
    path('process-sla-monitoring/', process_sla_monitoring_view, name='process-sla-monitoring'),
]