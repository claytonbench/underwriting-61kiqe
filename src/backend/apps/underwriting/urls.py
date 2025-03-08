# django version: 4.2+
from django.urls import path, include
# rest_framework version: 3.14+
from rest_framework.routers import DefaultRouter

from .views import (
    UnderwritingQueueViewSet,
    ApplicationReviewView,
    ApplicationEvaluationView,
    UnderwritingDecisionView,
    StipulationViewSet,
    UnderwritingNoteViewSet,
    CreditInformationView,
    UnderwritingStatisticsView,
    UnderwriterWorkloadView
)

# Define the app namespace
app_name = "underwriting"

# Create a router for the ViewSet
router = DefaultRouter()


def register_routes():
    """Registers ViewSets with the DefaultRouter to generate URL patterns"""
    # Register UnderwritingQueueViewSet with the router using 'queue' as the base name
    router.register(r'queue', UnderwritingQueueViewSet, basename='queue')
    # Register StipulationViewSet with the router using 'stipulations' as the base name
    router.register(r'stipulations', StipulationViewSet, basename='stipulations')
    # Register UnderwritingNoteViewSet with the router using 'notes' as the base name
    router.register(r'notes', UnderwritingNoteViewSet, basename='notes')


# Call the function to register the routes
register_routes()

# Define the URL patterns for the underwriting app
urlpatterns = [
    # Include the router-generated URLs
    path('', include(router.urls)),
    # Define a path for retrieving comprehensive application data for underwriting review
    path('applications/<int:application_id>/review/', ApplicationReviewView.as_view(), name='application-review'),
    # Define a path for evaluating an application against underwriting criteria
    path('applications/<int:application_id>/evaluate/', ApplicationEvaluationView.as_view(), name='application-evaluation'),
    # Define a path for creating and retrieving underwriting decisions
    path('applications/<int:application_id>/decision/', UnderwritingDecisionView.as_view(), name='underwriting-decision'),
    # Define a path for managing credit information
    path('applications/<int:application_id>/credit/', CreditInformationView.as_view(), name='credit-information'),
    # Define a path for retrieving underwriting statistics
    path('statistics/', UnderwritingStatisticsView.as_view(), name='underwriting-statistics'),
    # Define a path for retrieving underwriter workload statistics
    path('workload/', UnderwriterWorkloadView.as_view(), name='underwriter-workload'),
    # Define a path for retrieving underwriter workload statistics for a specific underwriter
    path('workload/<int:underwriter_id>/', UnderwriterWorkloadView.as_view(), name='underwriter-workload-detail'),
]