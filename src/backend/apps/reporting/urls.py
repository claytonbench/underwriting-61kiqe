from django.urls import path  # Django 4.2+
from .views import (
    ReportConfigurationListView,
    ReportConfigurationDetailView,
    ReportGenerateView,
    SavedReportListView,
    SavedReportDetailView,
    ReportExportView,
    ReportScheduleListView,
    ReportScheduleDetailView,
    ReportScheduleExecuteView,
    ReportPermissionView,
)

app_name = "reporting"

urlpatterns = [
    # Report configuration endpoints
    path('configurations/', ReportConfigurationListView.as_view(), name='report-configuration-list'),
    path('configurations/<uuid:config_id>/', ReportConfigurationDetailView.as_view(), name='report-configuration-detail'),
    
    # Report generation endpoint
    path('generate/', ReportGenerateView.as_view(), name='report-generate'),
    
    # Saved report endpoints
    path('reports/', SavedReportListView.as_view(), name='saved-report-list'),
    path('reports/<uuid:report_id>/', SavedReportDetailView.as_view(), name='saved-report-detail'),
    path('reports/<uuid:report_id>/export/', ReportExportView.as_view(), name='report-export'),
    
    # Report schedule endpoints
    path('schedules/', ReportScheduleListView.as_view(), name='report-schedule-list'),
    path('schedules/<uuid:schedule_id>/', ReportScheduleDetailView.as_view(), name='report-schedule-detail'),
    path('schedules/<uuid:schedule_id>/execute/', ReportScheduleExecuteView.as_view(), name='report-schedule-execute'),
    
    # Report permission endpoint
    path('configurations/<uuid:config_id>/permissions/', ReportPermissionView.as_view(), name='report-permission'),
]