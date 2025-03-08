from django.contrib import admin  # Django admin v4.2+
from django.urls import path, include, re_path  # Django URL routing v4.2+
from django.conf.urls.static import static  # Django static file serving v4.2+
from drf_yasg.views import get_schema_view  # DRF YASG v1.20+
from drf_yasg import openapi  # DRF YASG v1.20+
from rest_framework import permissions  # DRF v3.14+
from django.conf import settings  # Django settings v4.2+

# Schema view for API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Loan Management System API",
        default_version='v1',
        description="API for educational loan management system",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=[permissions.IsAuthenticated],
)

# Main URL patterns
urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('api/v1/auth/', include('apps.authentication.urls')),
    
    # App-specific URLs
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/schools/', include('apps.schools.urls')),
    path('api/v1/applications/', include('apps.applications.urls')),
    path('api/v1/underwriting/', include('apps.underwriting.urls')),
    path('api/v1/documents/', include('apps.documents.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/funding/', include('apps.funding.urls')),
    path('api/v1/qc/', include('apps.qc.urls')),
    path('api/v1/reporting/', include('apps.reporting.urls')),
    path('api/v1/workflow/', include('apps.workflow.urls')),
    
    # API documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Health check
    path('health/', include('health_check.urls')),
]

def serve_static_files():
    """
    Conditionally adds static/media file serving URLs in development mode
    
    Returns:
        list: Additional URL patterns for static/media files if in DEBUG mode
    """
    if settings.DEBUG:
        return static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
               static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    return []

# Add static/media file serving patterns in development
urlpatterns += serve_static_files()