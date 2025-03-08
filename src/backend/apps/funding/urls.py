# django.urls version: 4.2+
from django.urls import path

# Import Funding related views
from .views import (
    FundingRequestListView,
    FundingRequestDetailView,
    FundingRequestStatusUpdateView,
    FundingRequestApprovalView,
    EnrollmentVerificationListView,
    EnrollmentVerificationDetailView,
    VerifyEnrollmentView,
    StipulationVerificationListView,
    StipulationVerificationDetailView,
    VerifyStipulationView,
    RejectStipulationView,
    WaiveStipulationView,
    DisbursementListView,
    DisbursementDetailView,
    ProcessDisbursementView,
    CancelDisbursementView,
    FundingNoteListView,
    NextDisbursementDateView,
    FundingDashboardView
)

# Define the app name for URL namespacing
app_name = "funding"

# Define URL patterns for the funding app
urlpatterns = [
    # URL for listing and creating funding requests
    path('requests/', FundingRequestListView.as_view(), name='funding-request-list'),

    # URL for retrieving, updating, and deleting a specific funding request
    path('requests/<uuid:pk>/', FundingRequestDetailView.as_view(), name='funding-request-detail'),

    # URL for updating the status of a funding request
    path('requests/<uuid:pk>/status/', FundingRequestStatusUpdateView.as_view(), name='funding-request-status-update'),

    # URL for approving a funding request
    path('requests/<uuid:pk>/approve/', FundingRequestApprovalView.as_view(), name='funding-request-approve'),

    # URL for listing and creating enrollment verifications
    path('enrollment-verifications/', EnrollmentVerificationListView.as_view(), name='enrollment-verification-list'),

    # URL for retrieving a specific enrollment verification
    path('enrollment-verifications/<uuid:pk>/', EnrollmentVerificationDetailView.as_view(), name='enrollment-verification-detail'),

    # URL for verifying enrollment for a funding request
    path('requests/<uuid:pk>/verify-enrollment/', VerifyEnrollmentView.as_view(), name='verify-enrollment'),

    # URL for listing and creating stipulation verifications
    path('stipulation-verifications/', StipulationVerificationListView.as_view(), name='stipulation-verification-list'),

    # URL for retrieving a specific stipulation verification
    path('stipulation-verifications/<uuid:pk>/', StipulationVerificationDetailView.as_view(), name='stipulation-verification-detail'),

    # URL for verifying a stipulation
    path('stipulation-verifications/<uuid:pk>/verify/', VerifyStipulationView.as_view(), name='verify-stipulation'),

    # URL for rejecting a stipulation
    path('stipulation-verifications/<uuid:pk>/reject/', RejectStipulationView.as_view(), name='reject-stipulation'),

    # URL for waiving a stipulation
    path('stipulation-verifications/<uuid:pk>/waive/', WaiveStipulationView.as_view(), name='waive-stipulation'),

    # URL for listing and creating disbursements
    path('disbursements/', DisbursementListView.as_view(), name='disbursement-list'),

    # URL for retrieving, updating, and deleting a specific disbursement
    path('disbursements/<uuid:pk>/', DisbursementDetailView.as_view(), name='disbursement-detail'),

    # URL for processing a disbursement
    path('disbursements/<uuid:pk>/process/', ProcessDisbursementView.as_view(), name='process-disbursement'),

    # URL for cancelling a disbursement
    path('disbursements/<uuid:pk>/cancel/', CancelDisbursementView.as_view(), name='cancel-disbursement'),

    # URL for listing and creating funding notes
    path('notes/', FundingNoteListView.as_view(), name='funding-note-list'),

    # URL for getting the next available disbursement date
    path('next-disbursement-date/', NextDisbursementDateView.as_view(), name='next-disbursement-date'),

    # URL for the funding dashboard
    path('dashboard/', FundingDashboardView.as_view(), name='funding-dashboard'),
]