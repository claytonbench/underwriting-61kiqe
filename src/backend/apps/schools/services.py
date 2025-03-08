"""
Provides service functions for managing schools, programs, program versions, school contacts, and school documents in the loan management system. This module implements the business logic layer between the API views and the database models, handling data validation, permission checks, and complex operations.
"""

import os
import uuid
import datetime
from django.db import transaction
from django.core.exceptions import ValidationError, ObjectDoesNotExist, PermissionDenied
from django.utils import timezone

from .models import (
    School, Program, ProgramVersion, SchoolContact, SchoolDocument,
    SCHOOL_STATUS_CHOICES, PROGRAM_STATUS_CHOICES, DOCUMENT_TYPE_CHOICES
)
from ..users.models import SchoolAdminProfile, User, USER_TYPES
from ...utils.storage import S3Storage, StorageError
from ...utils.validators import (
    validate_state_code, validate_zip_code, validate_phone, validate_positive_number
)
from ...utils.logging import getLogger

# Configure logger
logger = getLogger('schools.services')

# Storage configuration
DOCUMENT_BUCKET_NAME = os.environ.get('DOCUMENT_BUCKET_NAME', 'loan-management-documents')
S3_REGION_NAME = os.environ.get('S3_REGION_NAME', 'us-east-1')


def create_school(school_data, administrators=None, created_by=None):
    """
    Creates a new school with optional initial administrators.
    
    Args:
        school_data (dict): Dictionary containing school information
        administrators (list): List of user IDs to be added as administrators
        created_by (User): User creating the school
        
    Returns:
        School: The newly created school instance
        
    Raises:
        ValidationError: If the provided data is invalid
        Exception: If the creation process fails
    """
    # Validate school data
    if 'state' in school_data:
        validate_state_code(school_data['state'])
    if 'zip_code' in school_data:
        validate_zip_code(school_data['zip_code'])
    if 'phone' in school_data:
        validate_phone(school_data['phone'])
    
    # Begin transaction
    with transaction.atomic():
        # Create the school instance
        school = School(**school_data)
        
        # Set audit fields
        if created_by:
            school.created_by = created_by
            school.updated_by = created_by
        
        # Save the school
        school.save()
        
        # Add administrators if provided
        if administrators and isinstance(administrators, list):
            for admin_id in administrators:
                try:
                    user = User.objects.get(id=admin_id)
                    # Ensure the user has the school_admin role
                    if not user.user_type == USER_TYPES['SCHOOL_ADMIN']:
                        user.user_type = USER_TYPES['SCHOOL_ADMIN']
                        user.save()
                    
                    # Create school admin profile
                    SchoolAdminProfile.objects.create(
                        user=user,
                        school=school,
                        title="Administrator",
                        department="Administration",
                        created_by=created_by,
                        updated_by=created_by
                    )
                except User.DoesNotExist:
                    logger.warning(f"User {admin_id} not found when adding as school administrator")
        
        logger.info(f"School created: {school.name} (ID: {school.id})", extra={
            'school_id': str(school.id),
            'created_by': str(created_by.id) if created_by else None
        })
        
        return school


def update_school(school_id, school_data, updated_by=None):
    """
    Updates an existing school with the provided data.
    
    Args:
        school_id (UUID): ID of the school to update
        school_data (dict): Dictionary containing updated school information
        updated_by (User): User updating the school
        
    Returns:
        School: The updated school instance
        
    Raises:
        ObjectDoesNotExist: If the school is not found
        ValidationError: If the provided data is invalid
        Exception: If the update process fails
    """
    # Get the school
    school = School.objects.get(id=school_id)
    
    # Validate updated data
    if 'state' in school_data:
        validate_state_code(school_data['state'])
    if 'zip_code' in school_data:
        validate_zip_code(school_data['zip_code'])
    if 'phone' in school_data:
        validate_phone(school_data['phone'])
    
    # Begin transaction
    with transaction.atomic():
        # Update school fields
        for key, value in school_data.items():
            if hasattr(school, key):
                setattr(school, key, value)
        
        # Set audit fields
        if updated_by:
            school.updated_by = updated_by
        
        # Save the school
        school.save()
        
        logger.info(f"School updated: {school.name} (ID: {school.id})", extra={
            'school_id': str(school.id),
            'updated_by': str(updated_by.id) if updated_by else None
        })
        
        return school


def delete_school(school_id, deleted_by=None):
    """
    Deletes (soft-deletes) a school by ID.
    
    Args:
        school_id (UUID): ID of the school to delete
        deleted_by (User): User performing the deletion
        
    Returns:
        bool: True if deletion was successful
        
    Raises:
        ObjectDoesNotExist: If the school is not found
        Exception: If the deletion process fails
    """
    # Get the school
    school = School.objects.get(id=school_id)
    
    # Begin transaction
    with transaction.atomic():
        # Soft-delete the school
        school.delete(hard_delete=False)
        
        # Set deleted_by in audit trail
        if deleted_by:
            # In a soft-delete, we can still update the record
            school.updated_by = deleted_by
            school.save()
        
        logger.info(f"School deleted: {school.name} (ID: {school.id})", extra={
            'school_id': str(school.id),
            'deleted_by': str(deleted_by.id) if deleted_by else None
        })
        
        return True


def get_school_by_id(school_id):
    """
    Retrieves a school by its ID.
    
    Args:
        school_id (UUID): ID of the school to retrieve
        
    Returns:
        School: The school instance if found
        
    Raises:
        ObjectDoesNotExist: If the school is not found
    """
    return School.objects.get(id=school_id)


def get_schools_for_user(user):
    """
    Retrieves schools that a user has access to based on their role.
    
    Args:
        user (User): The user to get schools for
        
    Returns:
        QuerySet: QuerySet of School objects
        
    Notes:
        - System admins and internal users can see all schools
        - School admins can only see their associated school
        - Other users have no access to schools
    """
    # Check if user is a system admin or internal user
    if user.user_type in [USER_TYPES['SYSTEM_ADMIN'], USER_TYPES['UNDERWRITER'], USER_TYPES['QC']]:
        return School.objects.all()
    
    # Check if user is a school administrator
    elif user.user_type == USER_TYPES['SCHOOL_ADMIN']:
        try:
            admin_profile = SchoolAdminProfile.objects.get(user=user)
            return School.objects.filter(id=admin_profile.school.id)
        except SchoolAdminProfile.DoesNotExist:
            return School.objects.none()
    
    # Other users have no access to schools
    return School.objects.none()


def create_program(school_id, program_data, created_by=None):
    """
    Creates a new program for a school with initial version.
    
    Args:
        school_id (UUID): ID of the school to create the program for
        program_data (dict): Dictionary containing program information
        created_by (User): User creating the program
        
    Returns:
        Program: The newly created program instance
        
    Raises:
        ObjectDoesNotExist: If the school is not found
        ValidationError: If the provided data is invalid
        Exception: If the creation process fails
    """
    # Get the school
    school = School.objects.get(id=school_id)
    
    # Validate program data
    if 'duration_hours' in program_data:
        validate_positive_number(program_data['duration_hours'])
    if 'duration_weeks' in program_data:
        validate_positive_number(program_data['duration_weeks'])
    
    # Extract tuition amount and effective date for program version
    tuition_amount = program_data.pop('tuition_amount', None)
    effective_date = program_data.pop('effective_date', None)
    
    if not tuition_amount:
        raise ValidationError("Tuition amount is required for program creation")
    
    if not effective_date:
        effective_date = timezone.now().date()
    elif isinstance(effective_date, str):
        effective_date = datetime.datetime.strptime(effective_date, '%Y-%m-%d').date()
    
    # Begin transaction
    with transaction.atomic():
        # Create program
        program = Program(school=school, **program_data)
        
        # Set audit fields
        if created_by:
            program.created_by = created_by
            program.updated_by = created_by
        
        # Save program
        program.save()
        
        # Create initial program version
        program.create_new_version(tuition_amount=tuition_amount, effective_date=effective_date)
        
        logger.info(f"Program created: {program.name} for school {school.name}", extra={
            'program_id': str(program.id),
            'school_id': str(school.id),
            'created_by': str(created_by.id) if created_by else None
        })
        
        return program


def update_program(program_id, program_data, updated_by=None):
    """
    Updates an existing program and optionally creates a new version.
    
    Args:
        program_id (UUID): ID of the program to update
        program_data (dict): Dictionary containing updated program information
        updated_by (User): User updating the program
        
    Returns:
        Program: The updated program instance
        
    Raises:
        ObjectDoesNotExist: If the program is not found
        ValidationError: If the provided data is invalid
        Exception: If the update process fails
    """
    # Get the program
    program = Program.objects.get(id=program_id)
    
    # Validate program data
    if 'duration_hours' in program_data:
        validate_positive_number(program_data['duration_hours'])
    if 'duration_weeks' in program_data:
        validate_positive_number(program_data['duration_weeks'])
    
    # Extract tuition amount and effective date for program version
    tuition_amount = program_data.pop('tuition_amount', None)
    effective_date = program_data.pop('effective_date', None)
    
    # Begin transaction
    with transaction.atomic():
        # Update program fields
        for key, value in program_data.items():
            if hasattr(program, key):
                setattr(program, key, value)
        
        # Set audit fields
        if updated_by:
            program.updated_by = updated_by
        
        # Save program
        program.save()
        
        # Create new program version if tuition amount provided
        if tuition_amount and effective_date:
            if isinstance(effective_date, str):
                effective_date = datetime.datetime.strptime(effective_date, '%Y-%m-%d').date()
                
            program.create_new_version(tuition_amount=tuition_amount, effective_date=effective_date)
            logger.info(f"New program version created for {program.name} with tuition {tuition_amount}", extra={
                'program_id': str(program.id),
                'updated_by': str(updated_by.id) if updated_by else None
            })
        
        logger.info(f"Program updated: {program.name}", extra={
            'program_id': str(program.id),
            'updated_by': str(updated_by.id) if updated_by else None
        })
        
        return program


def delete_program(program_id, deleted_by=None):
    """
    Deletes (soft-deletes) a program by ID.
    
    Args:
        program_id (UUID): ID of the program to delete
        deleted_by (User): User performing the deletion
        
    Returns:
        bool: True if deletion was successful
        
    Raises:
        ObjectDoesNotExist: If the program is not found
        Exception: If the deletion process fails
    """
    # Get the program
    program = Program.objects.get(id=program_id)
    
    # Begin transaction
    with transaction.atomic():
        # Soft-delete the program
        program.delete(hard_delete=False)
        
        # Set deleted_by in audit trail
        if deleted_by:
            # In a soft-delete, we can still update the record
            program.updated_by = deleted_by
            program.save()
        
        logger.info(f"Program deleted: {program.name} (ID: {program.id})", extra={
            'program_id': str(program.id),
            'school_id': str(program.school.id),
            'deleted_by': str(deleted_by.id) if deleted_by else None
        })
        
        return True


def get_program_by_id(program_id):
    """
    Retrieves a program by its ID.
    
    Args:
        program_id (UUID): ID of the program to retrieve
        
    Returns:
        Program: The program instance if found
        
    Raises:
        ObjectDoesNotExist: If the program is not found
    """
    return Program.objects.get(id=program_id)


def get_programs_for_school(school_id, active_only=True):
    """
    Retrieves programs for a specific school.
    
    Args:
        school_id (UUID): ID of the school to get programs for
        active_only (bool): If True, return only active programs
        
    Returns:
        QuerySet: QuerySet of Program objects
        
    Raises:
        ObjectDoesNotExist: If the school is not found
    """
    # Get the school
    school = School.objects.get(id=school_id)
    
    # Return programs based on active_only flag
    if active_only:
        return school.get_active_programs()
    else:
        return Program.objects.filter(school=school)


def create_program_version(program_id, version_data, created_by=None):
    """
    Creates a new version of a program with updated tuition.
    
    Args:
        program_id (UUID): ID of the program to create a version for
        version_data (dict): Dictionary containing version information (tuition_amount, effective_date)
        created_by (User): User creating the version
        
    Returns:
        ProgramVersion: The newly created program version instance
        
    Raises:
        ObjectDoesNotExist: If the program is not found
        ValidationError: If the provided data is invalid
        Exception: If the creation process fails
    """
    # Get the program
    program = Program.objects.get(id=program_id)
    
    # Extract required fields
    tuition_amount = version_data.get('tuition_amount')
    effective_date = version_data.get('effective_date')
    
    if not tuition_amount:
        raise ValidationError("Tuition amount is required for program version creation")
    
    # Validate tuition amount
    validate_positive_number(tuition_amount)
    
    # Validate effective date
    if not effective_date:
        effective_date = timezone.now().date()
    elif isinstance(effective_date, str):
        effective_date = datetime.datetime.strptime(effective_date, '%Y-%m-%d').date()
    
    # Check that effective date is not in the past
    if effective_date < timezone.now().date():
        raise ValidationError("Effective date cannot be in the past")
    
    # Begin transaction
    with transaction.atomic():
        # Create new program version
        version = program.create_new_version(tuition_amount=tuition_amount, effective_date=effective_date)
        
        # Set audit fields if possible
        if hasattr(version, 'created_by') and created_by:
            version.created_by = created_by
            version.updated_by = created_by
            version.save()
        
        logger.info(f"Program version created: {program.name} v{version.version_number} with tuition {tuition_amount}", extra={
            'program_id': str(program.id),
            'version_id': str(version.id),
            'created_by': str(created_by.id) if created_by else None
        })
        
        return version


def get_program_version_by_id(version_id):
    """
    Retrieves a program version by its ID.
    
    Args:
        version_id (UUID): ID of the program version to retrieve
        
    Returns:
        ProgramVersion: The program version instance if found
        
    Raises:
        ObjectDoesNotExist: If the program version is not found
    """
    return ProgramVersion.objects.get(id=version_id)


def get_program_versions(program_id):
    """
    Retrieves all versions for a specific program.
    
    Args:
        program_id (UUID): ID of the program to get versions for
        
    Returns:
        QuerySet: QuerySet of ProgramVersion objects
        
    Raises:
        ObjectDoesNotExist: If the program is not found
    """
    # Get the program
    program = Program.objects.get(id=program_id)
    
    # Return all versions
    return program.get_all_versions()


def add_school_contact(school_id, contact_data, created_by=None):
    """
    Adds a contact to a school.
    
    Args:
        school_id (UUID): ID of the school to add the contact to
        contact_data (dict): Dictionary containing contact information
        created_by (User): User creating the contact
        
    Returns:
        SchoolContact: The newly created school contact instance
        
    Raises:
        ObjectDoesNotExist: If the school is not found
        ValidationError: If the provided data is invalid
        Exception: If the creation process fails
    """
    # Get the school
    school = School.objects.get(id=school_id)
    
    # Validate contact data
    if 'phone' in contact_data:
        validate_phone(contact_data['phone'])
    
    # Begin transaction
    with transaction.atomic():
        # Create contact
        is_primary = contact_data.get('is_primary', False)
        
        # If this contact is being set as primary, update other contacts first
        if is_primary:
            SchoolContact.objects.filter(school=school, is_primary=True).update(is_primary=False)
        
        contact = SchoolContact(school=school, **contact_data)
        
        # Set audit fields
        if created_by:
            contact.created_by = created_by
            contact.updated_by = created_by
        
        # Save contact
        contact.save()
        
        logger.info(f"School contact added: {contact.get_full_name()} for {school.name}", extra={
            'contact_id': str(contact.id),
            'school_id': str(school.id),
            'created_by': str(created_by.id) if created_by else None
        })
        
        return contact


def update_school_contact(contact_id, contact_data, updated_by=None):
    """
    Updates an existing school contact.
    
    Args:
        contact_id (UUID): ID of the contact to update
        contact_data (dict): Dictionary containing updated contact information
        updated_by (User): User updating the contact
        
    Returns:
        SchoolContact: The updated school contact instance
        
    Raises:
        ObjectDoesNotExist: If the contact is not found
        ValidationError: If the provided data is invalid
        Exception: If the update process fails
    """
    # Get the contact
    contact = SchoolContact.objects.get(id=contact_id)
    
    # Validate contact data
    if 'phone' in contact_data:
        validate_phone(contact_data['phone'])
    
    # Begin transaction
    with transaction.atomic():
        # Check if primary status is changing
        is_primary = contact_data.get('is_primary')
        
        if is_primary and not contact.is_primary:
            # Update other contacts for this school
            SchoolContact.objects.filter(school=contact.school, is_primary=True).update(is_primary=False)
        
        # Update contact fields
        for key, value in contact_data.items():
            if hasattr(contact, key):
                setattr(contact, key, value)
        
        # Set audit fields
        if updated_by:
            contact.updated_by = updated_by
        
        # Save contact
        contact.save()
        
        logger.info(f"School contact updated: {contact.get_full_name()}", extra={
            'contact_id': str(contact.id),
            'school_id': str(contact.school.id),
            'updated_by': str(updated_by.id) if updated_by else None
        })
        
        return contact


def remove_school_contact(contact_id, deleted_by=None):
    """
    Removes (soft-deletes) a contact from a school.
    
    Args:
        contact_id (UUID): ID of the contact to remove
        deleted_by (User): User performing the removal
        
    Returns:
        bool: True if removal was successful
        
    Raises:
        ObjectDoesNotExist: If the contact is not found
        Exception: If the removal process fails
    """
    # Get the contact
    contact = SchoolContact.objects.get(id=contact_id)
    
    # Begin transaction
    with transaction.atomic():
        # Soft-delete the contact
        contact.delete(hard_delete=False)
        
        # Set deleted_by in audit trail
        if deleted_by:
            # In a soft-delete, we can still update the record
            contact.updated_by = deleted_by
            contact.save()
        
        logger.info(f"School contact removed: {contact.get_full_name()} from {contact.school.name}", extra={
            'contact_id': str(contact.id),
            'school_id': str(contact.school.id),
            'deleted_by': str(deleted_by.id) if deleted_by else None
        })
        
        return True


def get_school_contact_by_id(contact_id):
    """
    Retrieves a school contact by its ID.
    
    Args:
        contact_id (UUID): ID of the contact to retrieve
        
    Returns:
        SchoolContact: The school contact instance if found
        
    Raises:
        ObjectDoesNotExist: If the contact is not found
    """
    return SchoolContact.objects.get(id=contact_id)


def get_school_contacts(school_id):
    """
    Retrieves contacts for a specific school.
    
    Args:
        school_id (UUID): ID of the school to get contacts for
        
    Returns:
        QuerySet: QuerySet of SchoolContact objects
        
    Raises:
        ObjectDoesNotExist: If the school is not found
    """
    # Get the school
    school = School.objects.get(id=school_id)
    
    # Return contacts
    return SchoolContact.objects.filter(school=school)


def upload_school_document(school_id, document_data, document_file, uploaded_by=None):
    """
    Uploads a document for a school.
    
    Args:
        school_id (UUID): ID of the school to upload the document for
        document_data (dict): Dictionary containing document information
        document_file (file): The document file to upload
        uploaded_by (User): User uploading the document
        
    Returns:
        SchoolDocument: The newly created school document instance
        
    Raises:
        ObjectDoesNotExist: If the school is not found
        ValidationError: If the provided data is invalid
        StorageError: If the document upload fails
        Exception: If the process fails
    """
    # Get the school
    school = School.objects.get(id=school_id)
    
    # Validate document type
    document_type = document_data.get('document_type')
    if not document_type or document_type not in dict(DOCUMENT_TYPE_CHOICES):
        raise ValidationError(f"Invalid document type: {document_type}")
    
    # Generate file path
    file_name = document_file.name
    file_extension = os.path.splitext(file_name)[1].lower()
    unique_id = uuid.uuid4()
    file_path = f"schools/{school.id}/documents/{document_type}/{unique_id}{file_extension}"
    
    # Initialize storage
    storage = S3Storage(bucket_name=DOCUMENT_BUCKET_NAME, region_name=S3_REGION_NAME)
    
    # Upload file to S3
    try:
        storage.store(
            file_obj=document_file,
            key=file_path,
            content_type=document_file.content_type if hasattr(document_file, 'content_type') else None,
            metadata={
                'school_id': str(school.id),
                'document_type': document_type,
                'uploaded_by': str(uploaded_by.id) if uploaded_by else 'system'
            }
        )
    except StorageError as e:
        logger.error(f"Document upload failed: {str(e)}", extra={
            'school_id': str(school.id),
            'document_type': document_type,
            'file_name': file_name
        })
        raise
    
    # Begin transaction
    with transaction.atomic():
        # Create document record
        document = SchoolDocument(
            school=school,
            document_type=document_type,
            file_name=file_name,
            file_path=file_path,
            uploaded_by=uploaded_by
        )
        
        # Save document
        document.save()
        
        logger.info(f"School document uploaded: {file_name} for {school.name}", extra={
            'document_id': str(document.id),
            'school_id': str(school.id),
            'document_type': document_type,
            'uploaded_by': str(uploaded_by.id) if uploaded_by else None
        })
        
        return document


def get_school_document_by_id(document_id):
    """
    Retrieves a school document by its ID.
    
    Args:
        document_id (UUID): ID of the document to retrieve
        
    Returns:
        SchoolDocument: The school document instance if found
        
    Raises:
        ObjectDoesNotExist: If the document is not found
    """
    return SchoolDocument.objects.get(id=document_id)


def get_school_documents(school_id, document_type=None):
    """
    Retrieves documents for a specific school.
    
    Args:
        school_id (UUID): ID of the school to get documents for
        document_type (str): Optional document type to filter by
        
    Returns:
        QuerySet: QuerySet of SchoolDocument objects
        
    Raises:
        ObjectDoesNotExist: If the school is not found
    """
    # Get the school
    school = School.objects.get(id=school_id)
    
    # Get documents, filtered by type if provided
    documents = SchoolDocument.objects.filter(school=school)
    if document_type:
        documents = documents.filter(document_type=document_type)
    
    return documents


def delete_school_document(document_id, deleted_by=None):
    """
    Deletes a school document by ID.
    
    Args:
        document_id (UUID): ID of the document to delete
        deleted_by (User): User performing the deletion
        
    Returns:
        bool: True if deletion was successful
        
    Raises:
        ObjectDoesNotExist: If the document is not found
        StorageError: If the document deletion from storage fails
        Exception: If the deletion process fails
    """
    # Get the document
    document = SchoolDocument.objects.get(id=document_id)
    
    # Initialize storage
    storage = S3Storage(bucket_name=DOCUMENT_BUCKET_NAME, region_name=S3_REGION_NAME)
    
    # Delete file from S3
    try:
        storage.delete(document.file_path)
    except StorageError as e:
        logger.warning(f"Error deleting document file from storage: {str(e)}", extra={
            'document_id': str(document.id),
            'file_path': document.file_path
        })
        # Continue with database deletion even if storage deletion fails
    
    # Begin transaction
    with transaction.atomic():
        # Soft-delete the document record
        document.delete(hard_delete=False)
        
        # Set deleted_by in audit trail
        if deleted_by:
            # In a soft-delete, we can still update the record
            document.updated_by = deleted_by
            document.save()
        
        logger.info(f"School document deleted: {document.file_name} from {document.school.name}", extra={
            'document_id': str(document.id),
            'school_id': str(document.school.id),
            'deleted_by': str(deleted_by.id) if deleted_by else None
        })
        
        return True