# django version: 4.2+
from django.urls import path

from .views import (
    SchoolListView,
    SchoolDetailView,
    ProgramListView,
    ProgramDetailView,
    ProgramVersionListView,
    ProgramVersionDetailView,
    SchoolContactListView,
    SchoolContactDetailView,
    SchoolDocumentListView,
    SchoolDocumentDetailView
)

app_name = "schools"

urlpatterns = [
    path('', SchoolListView.as_view(), name='school-list-create'),
    path('<uuid:school_id>/', SchoolDetailView.as_view(), name='school-detail'),
    path('<uuid:school_id>/programs/', ProgramListView.as_view(), name='program-list-create'),
    path('<uuid:school_id>/programs/<uuid:program_id>/', ProgramDetailView.as_view(), name='program-detail'),
    path('<uuid:school_id>/programs/<uuid:program_id>/versions/', ProgramVersionListView.as_view(), name='program-version-list-create'),
    path('<uuid:school_id>/programs/<uuid:program_id>/versions/<uuid:version_id>/', ProgramVersionDetailView.as_view(), name='program-version-detail'),
    path('<uuid:school_id>/contacts/', SchoolContactListView.as_view(), name='school-contact-list-create'),
    path('<uuid:school_id>/contacts/<uuid:contact_id>/', SchoolContactDetailView.as_view(), name='school-contact-detail'),
    path('<uuid:school_id>/documents/', SchoolDocumentListView.as_view(), name='school-document-list-create'),
    path('<uuid:school_id>/documents/<uuid:document_id>/', SchoolDocumentDetailView.as_view(), name='school-document-detail')
]