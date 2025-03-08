"""
Defines serializers for the school and program management components of the loan management system.

These serializers handle the conversion of school, program, program version, school contact, 
and school document models to and from JSON representations for API interactions.
"""

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model

from core.serializers import (
    BaseModelSerializer, ReadOnlyModelSerializer, AuditFieldsMixin, SensitiveDataMixin
)
from .models import (
    School, Program, ProgramVersion, SchoolContact, SchoolDocument,
    SCHOOL_STATUS_CHOICES, PROGRAM_STATUS_CHOICES, DOCUMENT_TYPE_CHOICES
)
from apps.users.models import SchoolAdminProfile, User
from utils.validators import (
    validate_state_code, validate_zip_code, validate_phone, validate_positive_number
)


class SchoolSerializer(BaseModelSerializer):
    """
    Basic serializer for School model with minimal fields.
    """
    status = serializers.ChoiceField(choices=SCHOOL_STATUS_CHOICES)
    active_programs_count = serializers.SerializerMethodField()
    
    class Meta:
        model = School
        fields = [
            'id', 'name', 'legal_name', 'address_line1', 'address_line2', 'city', 
            'state', 'zip_code', 'phone', 'website', 'status', 'created_at', 'updated_at',
            'active_programs_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_active_programs_count(self):
        """
        Returns the count of active programs for the school.
        
        Returns:
            int: Count of active programs
        """
        return self.instance.get_active_programs().count()


class SchoolDetailSerializer(SchoolSerializer):
    """
    Detailed serializer for School model with related information.
    """
    administrators = serializers.SerializerMethodField()
    active_programs = serializers.SerializerMethodField()
    
    class Meta(SchoolSerializer.Meta):
        fields = SchoolSerializer.Meta.fields + ['administrators', 'active_programs']
    
    def get_administrators(self, obj):
        """
        Returns serialized data for school administrators.
        
        Args:
            obj: School instance
            
        Returns:
            list: List of serialized administrator data
        """
        admin_profiles = SchoolAdminProfile.objects.filter(school=obj)
        admin_data = []
        
        for profile in admin_profiles:
            admin_data.append({
                'id': profile.user.id,
                'name': profile.user.get_full_name(),
                'email': profile.user.email,
                'title': profile.title,
                'department': profile.department,
                'is_primary_contact': profile.is_primary_contact,
                'can_sign_documents': profile.can_sign_documents
            })
        
        return admin_data
    
    def get_active_programs(self, obj):
        """
        Returns serialized data for active programs.
        
        Args:
            obj: School instance
            
        Returns:
            list: List of serialized program data
        """
        programs = obj.get_active_programs()
        return ProgramSerializer(programs, many=True).data


class SchoolCreateSerializer(SchoolSerializer):
    """
    Serializer for creating new schools with initial administrators.
    """
    administrators = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all()),
        required=True,
        write_only=True
    )
    
    class Meta(SchoolSerializer.Meta):
        fields = SchoolSerializer.Meta.fields + ['tax_id', 'administrators']
    
    def validate(self, data):
        """
        Validates the school creation data.
        
        Args:
            data: Data to validate
            
        Returns:
            dict: Validated data
        
        Raises:
            ValidationError: If validation fails
        """
        # Validate state code
        try:
            if 'state' in data:
                validate_state_code(data['state'])
        except Exception as e:
            raise ValidationError({'state': str(e)})
        
        # Validate zip code
        try:
            if 'zip_code' in data:
                validate_zip_code(data['zip_code'])
        except Exception as e:
            raise ValidationError({'zip_code': str(e)})
        
        # Validate phone
        try:
            if 'phone' in data:
                validate_phone(data['phone'])
        except Exception as e:
            raise ValidationError({'phone': str(e)})
        
        # Ensure at least one administrator is provided
        if 'administrators' not in data or not data['administrators']:
            raise ValidationError({'administrators': 'At least one administrator is required'})
        
        return data
    
    def create(self, validated_data):
        """
        Creates a new school with administrators.
        
        Args:
            validated_data: Validated data from request
            
        Returns:
            School: Created school instance
        """
        # Extract administrators from validated data
        administrators = validated_data.pop('administrators')
        
        # Create school in a transaction to ensure atomicity
        with transaction.atomic():
            school = School.objects.create(**validated_data)
            
            # Create school admin profiles for each administrator
            for user in administrators:
                SchoolAdminProfile.objects.create(
                    user=user,
                    school=school,
                    title='Administrator',  # Default title
                    department='Administration',  # Default department
                    is_primary_contact=False,  # Only first user as primary by default
                    can_sign_documents=True  # All administrators can sign by default
                )
            
            # Make the first administrator the primary contact
            if administrators:
                primary_admin = SchoolAdminProfile.objects.get(user=administrators[0], school=school)
                primary_admin.is_primary_contact = True
                primary_admin.save()
                
        return school


class SchoolUpdateSerializer(SchoolSerializer):
    """
    Serializer for updating existing schools.
    """
    class Meta(SchoolSerializer.Meta):
        fields = SchoolSerializer.Meta.fields + ['tax_id']
    
    def validate(self, data):
        """
        Validates the school update data.
        
        Args:
            data: Data to validate
            
        Returns:
            dict: Validated data
        
        Raises:
            ValidationError: If validation fails
        """
        # Validate state code if provided
        try:
            if 'state' in data:
                validate_state_code(data['state'])
        except Exception as e:
            raise ValidationError({'state': str(e)})
        
        # Validate zip code if provided
        try:
            if 'zip_code' in data:
                validate_zip_code(data['zip_code'])
        except Exception as e:
            raise ValidationError({'zip_code': str(e)})
        
        # Validate phone if provided
        try:
            if 'phone' in data:
                validate_phone(data['phone'])
        except Exception as e:
            raise ValidationError({'phone': str(e)})
        
        return data
    
    def update(self, instance, validated_data):
        """
        Updates an existing school.
        
        Args:
            instance: School instance to update
            validated_data: Validated data from request
            
        Returns:
            School: Updated school instance
        """
        # Update school instance with validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class ProgramSerializer(BaseModelSerializer):
    """
    Basic serializer for Program model with minimal fields.
    """
    status = serializers.ChoiceField(choices=PROGRAM_STATUS_CHOICES)
    current_tuition = serializers.SerializerMethodField()
    
    class Meta:
        model = Program
        fields = [
            'id', 'school', 'name', 'description', 'duration_hours', 
            'duration_weeks', 'status', 'created_at', 'updated_at', 'current_tuition'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'current_tuition']
    
    def get_current_tuition(self, obj):
        """
        Returns the current tuition amount for the program.
        
        Args:
            obj: Program instance
            
        Returns:
            Decimal: Current tuition amount
        """
        current_version = obj.get_current_version()
        return current_version.tuition_amount if current_version else None


class ProgramDetailSerializer(ProgramSerializer):
    """
    Detailed serializer for Program model with version history.
    """
    versions = serializers.SerializerMethodField()
    current_version = serializers.SerializerMethodField()
    
    class Meta(ProgramSerializer.Meta):
        fields = ProgramSerializer.Meta.fields + ['versions', 'current_version']
    
    def get_versions(self, obj):
        """
        Returns serialized data for program versions.
        
        Args:
            obj: Program instance
            
        Returns:
            list: List of serialized program version data
        """
        versions = obj.get_all_versions()
        return ProgramVersionSerializer(versions, many=True).data
    
    def get_current_version(self, obj):
        """
        Returns serialized data for the current program version.
        
        Args:
            obj: Program instance
            
        Returns:
            dict: Serialized current version data
        """
        current_version = obj.get_current_version()
        if current_version:
            return ProgramVersionSerializer(current_version).data
        return None


class ProgramCreateSerializer(ProgramSerializer):
    """
    Serializer for creating new programs with initial version.
    """
    tuition_amount = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=True, 
        write_only=True
    )
    effective_date = serializers.DateField(required=True, write_only=True)
    
    class Meta(ProgramSerializer.Meta):
        fields = ProgramSerializer.Meta.fields + ['tuition_amount', 'effective_date']
    
    def validate(self, data):
        """
        Validates the program creation data.
        
        Args:
            data: Data to validate
            
        Returns:
            dict: Validated data
        
        Raises:
            ValidationError: If validation fails
        """
        # Validate duration_hours is positive
        try:
            if 'duration_hours' in data:
                validate_positive_number(data['duration_hours'])
        except Exception as e:
            raise ValidationError({'duration_hours': str(e)})
        
        # Validate duration_weeks is positive
        try:
            if 'duration_weeks' in data:
                validate_positive_number(data['duration_weeks'])
        except Exception as e:
            raise ValidationError({'duration_weeks': str(e)})
        
        # Validate tuition_amount is positive
        try:
            if 'tuition_amount' in data:
                validate_positive_number(data['tuition_amount'])
        except Exception as e:
            raise ValidationError({'tuition_amount': str(e)})
        
        # Ensure effective_date is provided
        if 'effective_date' not in data:
            raise ValidationError({'effective_date': 'Effective date is required for the initial version'})
        
        # Ensure effective date is not in the past
        if data['effective_date'] < timezone.now().date():
            raise ValidationError({'effective_date': 'Effective date cannot be in the past'})
        
        return data
    
    def create(self, validated_data):
        """
        Creates a new program with initial version.
        
        Args:
            validated_data: Validated data from request
            
        Returns:
            Program: Created program instance
        """
        # Extract version-specific fields
        tuition_amount = validated_data.pop('tuition_amount')
        effective_date = validated_data.pop('effective_date')
        
        # Create program and initial version in a transaction
        with transaction.atomic():
            program = Program.objects.create(**validated_data)
            
            # Create initial program version
            ProgramVersion.objects.create(
                program=program,
                version_number=1,
                effective_date=effective_date,
                tuition_amount=tuition_amount,
                is_current=True
            )
            
        return program


class ProgramUpdateSerializer(ProgramSerializer):
    """
    Serializer for updating existing programs.
    """
    tuition_amount = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False, 
        write_only=True
    )
    effective_date = serializers.DateField(required=False, write_only=True)
    
    class Meta(ProgramSerializer.Meta):
        fields = ProgramSerializer.Meta.fields + ['tuition_amount', 'effective_date']
    
    def validate(self, data):
        """
        Validates the program update data.
        
        Args:
            data: Data to validate
            
        Returns:
            dict: Validated data
        
        Raises:
            ValidationError: If validation fails
        """
        # Validate duration_hours is positive if provided
        try:
            if 'duration_hours' in data:
                validate_positive_number(data['duration_hours'])
        except Exception as e:
            raise ValidationError({'duration_hours': str(e)})
        
        # Validate duration_weeks is positive if provided
        try:
            if 'duration_weeks' in data:
                validate_positive_number(data['duration_weeks'])
        except Exception as e:
            raise ValidationError({'duration_weeks': str(e)})
        
        # Validate tuition_amount is positive if provided
        try:
            if 'tuition_amount' in data:
                validate_positive_number(data['tuition_amount'])
        except Exception as e:
            raise ValidationError({'tuition_amount': str(e)})
        
        # If tuition_amount is provided, effective_date must also be provided
        if 'tuition_amount' in data and 'effective_date' not in data:
            raise ValidationError({
                'effective_date': 'Effective date is required when updating tuition amount'
            })
        
        # Validate effective_date is not in the past if provided
        if 'effective_date' in data and data['effective_date'] < timezone.now().date():
            raise ValidationError({'effective_date': 'Effective date cannot be in the past'})
        
        return data
    
    def update(self, instance, validated_data):
        """
        Updates an existing program and creates a new version if tuition changes.
        
        Args:
            instance: Program instance to update
            validated_data: Validated data from request
            
        Returns:
            Program: Updated program instance
        """
        # Extract version-specific fields if present
        tuition_amount = validated_data.pop('tuition_amount', None)
        effective_date = validated_data.pop('effective_date', None)
        
        # Update program in a transaction
        with transaction.atomic():
            # Update program instance attributes
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            
            instance.save()
            
            # Create a new program version if tuition amount is provided
            if tuition_amount is not None and effective_date is not None:
                instance.create_new_version(tuition_amount, effective_date)
            
        return instance


class ProgramVersionSerializer(BaseModelSerializer):
    """
    Serializer for ProgramVersion model.
    """
    class Meta:
        model = ProgramVersion
        fields = [
            'id', 'program', 'version_number', 'effective_date', 
            'tuition_amount', 'is_current', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProgramVersionCreateSerializer(ProgramVersionSerializer):
    """
    Serializer for creating new program versions.
    """
    class Meta(ProgramVersionSerializer.Meta):
        fields = ['program', 'tuition_amount', 'effective_date']
    
    def validate(self, data):
        """
        Validates the program version creation data.
        
        Args:
            data: Data to validate
            
        Returns:
            dict: Validated data
        
        Raises:
            ValidationError: If validation fails
        """
        # Validate tuition_amount is positive
        try:
            if 'tuition_amount' in data:
                validate_positive_number(data['tuition_amount'])
        except Exception as e:
            raise ValidationError({'tuition_amount': str(e)})
        
        # Ensure effective_date is provided
        if 'effective_date' not in data:
            raise ValidationError({'effective_date': 'Effective date is required'})
        
        # Ensure effective date is not in the past
        if data['effective_date'] < timezone.now().date():
            raise ValidationError({'effective_date': 'Effective date cannot be in the past'})
        
        return data
    
    def create(self, validated_data):
        """
        Creates a new program version.
        
        Args:
            validated_data: Validated data from request
            
        Returns:
            ProgramVersion: Created program version instance
        """
        program = validated_data.pop('program')
        tuition_amount = validated_data.pop('tuition_amount')
        effective_date = validated_data.pop('effective_date')
        
        # Use the program's create_new_version method to handle version management logic
        return program.create_new_version(tuition_amount, effective_date)


class SchoolContactSerializer(BaseModelSerializer):
    """
    Serializer for SchoolContact model.
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = SchoolContact
        fields = [
            'id', 'school', 'first_name', 'last_name', 'full_name', 'title', 
            'email', 'phone', 'is_primary', 'can_sign_documents', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'full_name', 'created_at', 'updated_at']
    
    def validate(self, data):
        """
        Validates the school contact data.
        
        Args:
            data: Data to validate
            
        Returns:
            dict: Validated data
        
        Raises:
            ValidationError: If validation fails
        """
        # Validate phone
        try:
            if 'phone' in data:
                validate_phone(data['phone'])
        except Exception as e:
            raise ValidationError({'phone': str(e)})
        
        return data
    
    def to_representation(self, instance):
        """
        Customizes the serialized representation of the contact.
        
        Args:
            instance: SchoolContact instance
            
        Returns:
            dict: Serialized representation
        """
        representation = super().to_representation(instance)
        representation['full_name'] = instance.get_full_name()
        return representation


class SchoolDocumentSerializer(BaseModelSerializer):
    """
    Serializer for SchoolDocument model.
    """
    document_type = serializers.ChoiceField(choices=DOCUMENT_TYPE_CHOICES)
    download_url = serializers.SerializerMethodField()
    uploaded_by = serializers.SerializerMethodField()
    
    class Meta:
        model = SchoolDocument
        fields = [
            'id', 'school', 'document_type', 'file_name', 'file_path',
            'uploaded_at', 'uploaded_by', 'status', 'download_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'uploaded_at', 'uploaded_by', 'download_url',
            'created_at', 'updated_at'
        ]
    
    def get_download_url(self, obj):
        """
        Generates a download URL for the document.
        
        Args:
            obj: SchoolDocument instance
            
        Returns:
            str: Presigned download URL
        """
        return obj.get_download_url()
    
    def get_uploaded_by(self, obj):
        """
        Returns information about the user who uploaded the document.
        
        Args:
            obj: SchoolDocument instance
            
        Returns:
            dict: User information
        """
        if obj.uploaded_by:
            return {
                'id': obj.uploaded_by.id,
                'name': obj.uploaded_by.get_full_name(),
                'email': obj.uploaded_by.email
            }
        return None


class UserSerializer(BaseModelSerializer):
    """
    Minimal serializer for User model used in school-related contexts.
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'phone', 'user_type']
        read_only_fields = ['id', 'email', 'full_name', 'user_type']
    
    def get_full_name(self, obj):
        """
        Returns the user's full name.
        
        Args:
            obj: User instance
            
        Returns:
            str: User's full name
        """
        return obj.get_full_name()


class SchoolAdminSerializer(BaseModelSerializer):
    """
    Serializer for SchoolAdminProfile model.
    """
    user_details = serializers.SerializerMethodField()
    
    class Meta:
        model = SchoolAdminProfile
        fields = [
            'id', 'user', 'school', 'title', 'department', 
            'is_primary_contact', 'can_sign_documents',
            'user_details', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_details']
    
    def get_user_details(self, obj):
        """
        Returns detailed information about the administrator user.
        
        Args:
            obj: SchoolAdminProfile instance
            
        Returns:
            dict: User details
        """
        return UserSerializer(obj.user).data