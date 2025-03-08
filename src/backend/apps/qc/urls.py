# django.urls version: 4.2+
from django.urls import path, include  # django.urls version: 4.2+

from .views import (  # Internal import
    QCReviewListView,
    QCReviewDetailView,
    QCReviewCreateView,
    QCReviewAssignView,
    QCReviewStatusUpdateView,
    QCReviewReopenView,
    QCReviewSummaryView,
    DocumentVerificationView,
    StipulationVerificationView,
    ChecklistItemView,
    QCReviewByApplicationView,
    QCReviewValidationView
)

app_name = "qc"

urlpatterns = [
    path('reviews/', QCReviewListView.as_view(), name='qc-review-list'),
    path('reviews/create/', QCReviewCreateView.as_view(), name='qc-review-create'),
    path('reviews/summary/', QCReviewSummaryView.as_view(), name='qc-review-summary'),
    path('reviews/<uuid:pk>/', QCReviewDetailView.as_view(), name='qc-review-detail'),
    path('reviews/<uuid:pk>/assign/', QCReviewAssignView.as_view(), name='qc-review-assign'),
    path('reviews/<uuid:pk>/status/', QCReviewStatusUpdateView.as_view(), name='qc-review-status-update'),
    path('reviews/<uuid:pk>/reopen/', QCReviewReopenView.as_view(), name='qc-review-reopen'),
    path('reviews/<uuid:pk>/validate/', QCReviewValidationView.as_view(), name='qc-review-validate'),
    path('application/<uuid:application_id>/review/', QCReviewByApplicationView.as_view(), name='qc-review-by-application'),
    path('documents/<uuid:pk>/', DocumentVerificationView.as_view(), name='document-verification'),
    path('stipulations/<uuid:pk>/', StipulationVerificationView.as_view(), name='stipulation-verification'),
    path('checklist/<uuid:pk>/', ChecklistItemView.as_view(), name='checklist-item'),
]