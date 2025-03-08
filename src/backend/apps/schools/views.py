# rest_framework version: 3.14+
from rest_framework import generics, status
# rest_framework version: 3.14+
from rest_framework.response import Response
# rest_framework version: 3.14+
from rest_framework import parsers
# rest_framework version: 3.14+
from rest_framework.parsers import MultiPartParser

from .models import (
    School, Program, ProgramVersion, SchoolContact, SchoolDocument
)
from .serializers import (
    SchoolSerializer, SchoolDetailSerializer, SchoolCreateSerializer, SchoolUpdateSerializer,
    ProgramSerializer, ProgramDetailSerializer, ProgramCreateSerializer, ProgramUpdateSerializer,
    ProgramVersionSerializer, ProgramVersionCreateSerializer,
    SchoolContactSerializer, SchoolDocumentSerializer
)
from .permissions import (
    CanManageSchools, CanViewSchools,
    CanManageSchoolPrograms, CanViewSchoolPrograms,
    CanManageProgramVersions, CanViewProgramVersions,
    CanManageSchoolContacts, CanViewSchoolContacts,
    CanManageSchoolDocuments, CanViewSchoolDocuments
)
from core.views import BaseGenericAPIView, TransactionMixin, AuditLogMixin, get_object_or_exception
from core.exceptions import ResourceNotFoundException, ValidationException


class SchoolListView(BaseGenericAPIView, generics.ListCreateAPIView):
    """
    API view for listing all schools and creating new schools
    """
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [CanViewSchools]

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the request method

        Returns:
            Serializer class to use
        """
        if self.request.method == 'POST':
            return SchoolCreateSerializer
        return self.serializer_class

    def get_permissions(self):
        """
        Returns the list of permission instances for the view

        Returns:
            list: List of permission instances
        """
        if self.request.method == 'POST':
            return [CanManageSchools()]
        return [permission() for permission in self.permission_classes]

    def list(self, request, *args, **kwargs):
        """
        List all schools with optional filtering

        parameters:
            request
            kwargs

        Returns:
            Response: Response containing serialized schools data
        """
        queryset = self.get_queryset()
        # Apply any filters from request query parameters
        # For example: queryset = queryset.filter(status=request.query_params.get('status'))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Create a new school

        parameters:
            request
            kwargs

        Returns:
            Response: Response containing the created school data
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class SchoolDetailView(BaseGenericAPIView, generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a specific school
    """
    queryset = School.objects.all()
    serializer_class = SchoolDetailSerializer
    permission_classes = [CanViewSchools]
    lookup_url_kwarg = 'school_id'

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the request method

        Returns:
            Serializer class to use
        """
        if self.request.method in ['PUT', 'PATCH']:
            return SchoolUpdateSerializer
        return self.serializer_class

    def get_permissions(self):
        """
        Returns the list of permission instances for the view

        Returns:
            list: List of permission instances
        """
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [CanManageSchools()]
        return [permission() for permission in self.permission_classes]

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific school

        parameters:
            request
            kwargs

        Returns:
            Response: Response containing serialized school data
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        Update a specific school

        parameters:
            request
            kwargs

        Returns:
            Response: Response containing the updated school data
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a specific school

        parameters:
            request
            kwargs

        Returns:
            Response: Response containing the updated school data
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a specific school

        parameters:
            request
            kwargs

        Returns:
            Response: Empty response with 204 status
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProgramListView(BaseGenericAPIView, generics.ListCreateAPIView):
    """
    API view for listing programs for a school and creating new programs
    """
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [CanViewSchoolPrograms]

    def get_queryset(self):
        """
        Returns the queryset filtered by the school_id from the URL

        Returns:
            QuerySet: Filtered queryset of programs
        """
        school_id = self.kwargs.get('school_id')
        school = get_object_or_exception(School.objects, {'id': school_id})
        # Check object permissions for the school
        for permission in self.get_permissions():
            has_object_permission_or_403(permission, self.request, self, school)
        return self.queryset.filter(school=school)

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the request method

        Returns:
            Serializer class to use
        """
        if self.request.method == 'POST':
            return ProgramCreateSerializer
        return self.serializer_class

    def get_permissions(self):
        """
        Returns the list of permission instances for the view

        Returns:
            list: List of permission instances
        """
        if self.request.method == 'POST':
            return [CanManageSchoolPrograms()]
        return [permission() for permission in self.permission_classes]

    def get_serializer_context(self):
        """
        Returns the serializer context with additional data

        Returns:
            dict: Serializer context dictionary
        """
        context = super().get_serializer_context()
        context['school_id'] = self.kwargs.get('school_id')
        return context

    def list(self, request, *args, **kwargs):
        """
        List programs for a school with optional filtering

        parameters:
            request
            kwargs

        Returns:
            Response: Response containing serialized programs data
        """
        queryset = self.get_queryset()
        # Apply any filters from request query parameters
        # For example: queryset = queryset.filter(status=request.query_params.get('status'))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Create a new program for a school

        parameters:
            request
            kwargs

        Returns:
            Response: Response containing the created program data
        """
        school_id = self.kwargs.get('school_id')
        school = get_object_or_exception(School.objects, {'id': school_id})
        # Check object permissions for the school
        for permission in self.get_permissions():
            has_object_permission_or_403(permission, self.request, self, school)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ProgramDetailView(BaseGenericAPIView, generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a specific program
    """
    queryset = Program.objects.all()
    serializer_class = ProgramDetailSerializer
    permission_classes = [CanViewSchoolPrograms]
    lookup_url_kwarg = 'program_id'

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the request method

        Returns:
            Serializer class to use
        """
        if self.request.method in ['PUT', 'PATCH']:
            return ProgramUpdateSerializer
        return self.serializer_class

    def get_permissions(self):
        """
        Returns the list of permission instances for the view

        Returns:
            list: List of permission instances
        """
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [CanManageSchoolPrograms()]
        return [permission() for permission in self.permission_classes]

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific program

        parameters:
            request
            kwargs

        Returns:
            Response: Response containing serialized program data
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        Update a specific program

        parameters:
            request
            kwargs

        Returns:
            Response: Response containing the updated program data
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a specific program

        parameters:
            request
            kwargs

        Returns:
            Response: Response containing the updated program data
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a specific program

        parameters:
            request
            kwargs

        Returns:
            Response: Empty response with 204 status
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProgramVersionListView(BaseGenericAPIView, generics.ListCreateAPIView):
    """
    API view for listing versions of a program and creating new versions
    """
    queryset = ProgramVersion.objects.all()
    serializer_class = ProgramVersionSerializer
    permission_classes = [CanViewProgramVersions]

    def get_queryset(self):
        """
        Returns the queryset filtered by the program_id from the URL

        Returns:
            QuerySet: Filtered queryset of program versions
        """
        program_id = self.kwargs.get('program_id')
        program = get_object_or_exception(Program.objects, {'id': program_id})
        # Check object permissions for the program
        for permission in self.get_permissions():
            has_object_permission_or_403(permission, self.request, self, program)
        return self.queryset.filter(program=program).order_by('version_number')

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the request method

        Returns:
            Serializer class to use
        """
        if self.request.method == 'POST':
            return ProgramVersionCreateSerializer
        return self.serializer_class

    def get_permissions(self):
        """
        Returns the list of permission instances for the view

        Returns:
            list: List of permission instances
        """
        if self.request.method == 'POST':
            return [CanManageProgramVersions()]
        return [permission() for permission in self.permission_classes]

    def get_serializer_context(self):
        """
        Returns the serializer context with additional data

        Returns:
            dict: Serializer context dictionary
        """
        context = super().get_serializer_context()
        context['program_id'] = self.kwargs.get('program_id')
        return context

    def list(self, request, *args, **kwargs):
        """
        List versions for a program

        parameters:
            request
            kwargs

        Returns:
            Response: Response containing serialized program versions data
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Create a new version for a program

        parameters:
            request
            kwargs

        Returns:
            Response: Response containing the created version data
        """
        program_id = self.kwargs.get('program_id')
        program = get_object_or_exception(Program.objects, {'id': program_id})
        # Check object permissions for the program
        for permission in self.get_permissions():
            has_object_permission_or_403(permission, self.request, self, program)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ProgramVersionDetailView(BaseGenericAPIView, generics.RetrieveAPIView):
    """
    API view for retrieving a specific program version
    """
    queryset = ProgramVersion.objects.all()
    serializer_class = ProgramVersionSerializer
    permission_classes = [CanViewProgramVersions]
    lookup_url_kwarg = 'version_id'

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific program version

        parameters:
            request
            kwargs

        Returns:
            Response: Response containing serialized program version data
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class SchoolContactListView(BaseGenericAPIView, generics.ListCreateAPIView):
    """
    API view for listing contacts for a school and creating new contacts
    """
    queryset = SchoolContact.objects.all()
    serializer_class = SchoolContactSerializer
    permission_classes = [CanViewSchoolContacts]

    def get_queryset(self):
        """
        Returns the queryset filtered by the school_id from the URL

        Returns:
            QuerySet: Filtered queryset of school contacts
        """
        school_id = self.kwargs.get('school_id')
        school = get_object_or_exception(School.objects, {'id': school_id})
        # Check object permissions for the school
        for permission in self.get_permissions():
            has_object_permission_or_403(permission, self.request, self, school)
        return self.queryset.filter(school=school)

    def get_permissions(self):
        """
        Returns the list of permission instances for the view

        Returns:
            list: List of permission instances
        """
        if self.request.method == 'POST':
            return [CanManageSchoolContacts()]
        return [permission() for permission in self.permission_classes]

    def get_serializer_context(self):
        """
        Returns the serializer context with additional data

        Returns:
            dict: Serializer context dictionary
        """
        context = super().get_serializer_context()
        context['school_id'] = self.kwargs.get('school_id')
        return context

    def list(self, request, *args, **kwargs):
        """
        List contacts for a school

        parameters:
            request
            kwargs

        Returns:
            Response: Response containing serialized school contacts data
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Create a new contact for a school

        parameters:
            request
            kwargs

        Returns:
            Response: Response containing the created contact data
        """
        school_id = self.kwargs.get('school_id')
        school = get_object_or_exception(School.objects, {'id': school_id})
        # Check object permissions for the school
        for permission in self.get_permissions():
            has_object_permission_or_403(permission, self.request, self, school)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class SchoolContactDetailView(BaseGenericAPIView, generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a specific school contact
    """
    queryset = SchoolContact.objects.all()
    serializer_class = SchoolContactSerializer
    permission_classes = [CanViewSchoolContacts]
    lookup_url_kwarg = 'contact_id'

    def get_permissions(self):
        """
        Returns the list of permission instances for the view

        Returns:
            list: List of permission instances
        """
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [CanManageSchoolContacts()]
        return [permission() for permission in self.permission_classes]

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific school contact

        parameters:
            request
            kwargs

        Returns:
            Response: Response containing serialized school contact data
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        Update a specific school contact

        parameters:
            request
            kwargs

        Returns:
            Response: Response containing the updated contact data
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a specific school contact

        parameters:
            request
            kwargs

        Returns:
            Response: Response containing the updated contact data
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a specific school contact

        parameters:
            request
            kwargs

        Returns:
            Response: Empty response with 204 status
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SchoolDocumentListView(BaseGenericAPIView, generics.ListCreateAPIView):
    """
    API view for listing documents for a school and uploading new documents
    """
    queryset = SchoolDocument.objects.all()
    serializer_class = SchoolDocumentSerializer
    permission_classes = [CanViewSchoolDocuments]
    parser_classes = [parsers.MultiPartParser]

    def get_queryset(self):
        """
        Returns the queryset filtered by the school_id from the URL

        Returns:
            QuerySet: Filtered queryset of school documents
        """
        school_id = self.kwargs.get('school_id')
        school = get_object_or_exception(School.objects, {'id': school_id})
        # Check object permissions for the school
        for permission in self.get_permissions():
            has_object_permission_or_403(permission, self.request, self, school)
        return self.queryset.filter(school=school)

    def get_permissions(self):
        """
        Returns the list of permission instances for the view

        Returns:
            list: List of permission instances
        """
        if self.request.method == 'POST':
            return [CanManageSchoolDocuments()]
        return [permission() for permission in self.permission_classes]

    def get_serializer_context(self):
        """
        Returns the serializer context with additional data

        Returns:
            dict: Serializer context dictionary
        """
        context = super().get_serializer_context()
        context['school_id'] = self.kwargs.get('school_id')
        context['request'] = self.request  # Pass the request object to the serializer
        return context

    def list(self, request, *args, **kwargs):
        """
        List documents for a school

        parameters:
            request
            kwargs

        Returns:
            Response: Response containing serialized school documents data
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Upload a new document for a school

        parameters:
            request
            kwargs

        Returns:
            Response: Response containing the uploaded document data
        """
        school_id = self.kwargs.get('school_id')
        school = get_object_or_exception(School.objects, {'id': school_id})
        # Check object permissions for the school
        for permission in self.get_permissions():
            has_object_permission_or_403(permission, self.request, self, school)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class SchoolDocumentDetailView(BaseGenericAPIView, generics.RetrieveDestroyAPIView):
    """
    API view for retrieving and deleting a specific school document
    """
    queryset = SchoolDocument.objects.all()
    serializer_class = SchoolDocumentSerializer
    permission_classes = [CanViewSchoolDocuments]
    lookup_url_kwarg = 'document_id'

    def get_permissions(self):
        """
        Returns the list of permission instances for the view

        Returns:
            list: List of permission instances
        """
        if self.request.method == 'DELETE':
            return [CanManageSchoolDocuments()]
        return [permission() for permission in self.permission_classes]

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific school document

        parameters:
            request
            kwargs

        Returns:
            Response: Response containing serialized school document data
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a specific school document

        parameters:
            request
            kwargs

        Returns:
            Response: Empty response with 204 status
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)