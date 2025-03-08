from django.urls import path  # django.urls 4.2+

from .views import (  # Internal import
    DocumentTemplateListView,
    DocumentTemplateDetailView,
    DocumentPackageListView,
    DocumentPackageDetailView,
    DocumentPackageCreateView,
    DocumentListView,
    DocumentDetailView,
    DocumentDownloadView,
    DocumentUploadView,
    SignatureRequestListView,
    SignatureRequestDetailView,
    CreateSignatureRequestView,
    CreatePackageSignatureRequestView,
    SignatureStatusView,
    PackageSignatureStatusView,
    SignatureReminderView,
    ProcessSignedDocumentView,
    ProcessPackageSignedDocumentsView,
    VoidSignatureRequestView,
    DocuSignWebhookView,
    ApplicationDocumentsView,
    ApplicationDocumentPackagesView,
    SigningUrlView
)

app_name = "documents"  # Django namespace for the documents app URLs

urlpatterns = [
    # URL patterns for document templates
    path('templates/', DocumentTemplateListView.as_view(), name='document-template-list'),  # List and create document templates
    path('templates/<uuid:pk>/', DocumentTemplateDetailView.as_view(), name='document-template-detail'),  # Retrieve, update, and delete document templates

    # URL patterns for document packages
    path('packages/', DocumentPackageListView.as_view(), name='document-package-list'),  # List document packages
    path('packages/<uuid:pk>/', DocumentPackageDetailView.as_view(), name='document-package-detail'),  # Retrieve document packages
    path('packages/create/', DocumentPackageCreateView.as_view(), name='document-package-create'),  # Create document packages

    # URL patterns for individual documents
    path('', DocumentListView.as_view(), name='document-list'),  # List documents
    path('<uuid:pk>/', DocumentDetailView.as_view(), name='document-detail'),  # Retrieve documents
    path('<uuid:pk>/download/', DocumentDownloadView.as_view(), name='document-download'),  # Download documents
    path('upload/', DocumentUploadView.as_view(), name='document-upload'),  # Upload documents

    # URL patterns for signature requests
    path('signature-requests/', SignatureRequestListView.as_view(), name='signature-request-list'),  # List signature requests
    path('signature-requests/<uuid:pk>/', SignatureRequestDetailView.as_view(), name='signature-request-detail'),  # Retrieve signature requests
    path('<uuid:document_id>/request-signature/', CreateSignatureRequestView.as_view(), name='create-signature-request'),  # Create signature requests for documents
    path('packages/<uuid:package_id>/request-signature/', CreatePackageSignatureRequestView.as_view(), name='create-package-signature-request'),  # Create signature requests for document packages

    # URL patterns for signature status
    path('<uuid:document_id>/signature-status/', SignatureStatusView.as_view(), name='signature-status'),  # Get and update signature status
    path('packages/<uuid:package_id>/signature-status/', PackageSignatureStatusView.as_view(), name='package-signature-status'),  # Get and update package signature status

    # URL patterns for signature reminders
    path('signature-requests/<uuid:signature_request_id>/remind/', SignatureReminderView.as_view(), name='signature-reminder'),  # Send signature reminders

    # URL patterns for processing signed documents
    path('<uuid:document_id>/process-signed/', ProcessSignedDocumentView.as_view(), name='process-signed-document'),  # Process signed documents
    path('packages/<uuid:package_id>/process-signed/', ProcessPackageSignedDocumentsView.as_view(), name='process-package-signed-documents'),  # Process signed documents in a package

    # URL patterns for voiding signature requests
    path('<uuid:document_id>/void-signature/', VoidSignatureRequestView.as_view(), name='void-signature-request'),  # Void signature requests

    # URL patterns for DocuSign webhooks
    path('webhook/docusign/', DocuSignWebhookView.as_view(), name='docusign-webhook'),  # Handle DocuSign webhooks

    # URL patterns for application documents
    path('application/<uuid:application_id>/', ApplicationDocumentsView.as_view(), name='application-documents'),  # Get all documents for an application
    path('application/<uuid:application_id>/packages/', ApplicationDocumentPackagesView.as_view(), name='application-document-packages'),  # Get all document packages for an application

    # URL pattern for signing URL
    path('signature-requests/<uuid:signature_request_id>/signing-url/', SigningUrlView.as_view(), name='signing-url') # Get signing URL
]