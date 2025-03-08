# django.urls 4.2+
from django.urls import path, include  # Define URL patterns
# rest_framework 3.14+
from rest_framework.routers import DefaultRouter  # Router for automatically generating URL patterns for ViewSets

from .views import ApplicationViewSet, ApplicationDocumentViewSet, ApplicationCalculatorView  # src/backend/apps/applications/views.py


app_name = "applications"  # Django namespace for the applications app URLs

router = DefaultRouter()  # Create a DefaultRouter instance

def register_routes():
    """Registers ViewSets with the DefaultRouter to generate URL patterns"""
    router.register(r'applications', ApplicationViewSet, basename='applications')  # Register ApplicationViewSet with the router using 'applications' as the base name
    router.register(r'application-documents', ApplicationDocumentViewSet, basename='application-documents')  # Register ApplicationDocumentViewSet with the router using 'application-documents' as the base name

register_routes()

urlpatterns = [
    path('calculator/', ApplicationCalculatorView.as_view(), name='application-calculator'),  # Custom path for the ApplicationCalculatorView
    path('', include(router.urls)),  # Include the router-generated URL patterns
]