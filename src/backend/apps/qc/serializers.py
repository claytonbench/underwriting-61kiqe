"""
Defines serializers for the Quality Control (QC) module of the loan management system. These serializers handle the transformation of QC-related models to and from JSON for API operations, including QC reviews, document verification, stipulation verification, and checklist items. The serializers support the QC review process that occurs after document completion and before funding approval.
"""
from rest_framework import serializers  # rest_framework version: 3.14+
from rest_framework.exceptions import ValidationError  # rest_framework version: 3.14+
from django.contrib.auth import get_user_model  # django version: 4.2+

from core.serializers import BaseModelSerializer, ReadOnlyModelSerializer  # Internal import
from .models import (  # Internal import
    QCReview, DocumentVerification, QCStipulationVerification, QCChecklistItem, QCNote
)
from apps.applications.models import LoanApplication  # Internal import
from apps.documents.models import Document  # Internal import
from apps.underwriting.models import Stipulation  # Internal import
from apps.users.models import User  # Internal import
from apps.users.serializers import UserSerializer  # Internal import
from apps.applications.serializers import LoanApplicationSerializer  # Internal import
from apps.documents.serializers import DocumentSerializer  # Internal import
from apps.underwriting.serializers import StipulationSerializer  # Internal import
from .constants import (  # Internal import
    QC_STATUS, QC_VERIFICATION_STATUS, QC_RETURN_REASON,
    QC_CHECKLIST_CATEGORY, QC_PRIORITY, QC_ASSIGNMENT_TYPE
)


class QCReviewSerializer(BaseModelSerializer):
    """
    Serializer for QCReview model with basic fields
    """
    class Meta:
        model = QCReview
        fields = ['id', 'application', 'status', 'priority', 'assigned_to', 'assignment_type', 'assigned_at', 'completed_at', 'return_reason', 'notes']

    def validate(self, data: dict) -> dict:
        """
        Validates the QCReview data

        Args:
            data (dict): data

        Returns:
            dict: Validated data
        """
        if data.get('status') == QC_STATUS['RETURNED'] and not data.get('return_reason'):
            raise ValidationError("Return reason is required when status is returned")
        # if data.get('status') == QC_STATUS['APPROVED'] and not self.instance.is_complete():
        #     raise ValidationError("All verifications must be complete before approving")
        return data

    def to_representation(self, instance: QCReview) -> dict:
        """
        Customizes the representation of QCReview instances

        Args:
            instance (QCReview): instance

        Returns:
            dict: Serialized representation
        """
        representation = super().to_representation(instance)
        representation['completion_percentage'] = instance.get_completion_percentage()
        return representation


class QCReviewDetailSerializer(BaseModelSerializer):
    """
    Detailed serializer for QCReview model with nested related objects
    """
    application = LoanApplicationSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    document_verifications = serializers.SerializerMethodField()
    stipulation_verifications = serializers.SerializerMethodField()
    checklist_items = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()

    class Meta:
        model = QCReview
        fields = ['id', 'application', 'status', 'priority', 'assigned_to', 'assignment_type', 'assigned_at', 'completed_at', 'return_reason', 'notes', 'document_verifications', 'stipulation_verifications', 'checklist_items', 'completion_percentage']

    def get_document_verifications(self, instance: QCReview) -> list:
        """
        Gets document verifications for the QC review

        Args:
            instance (QCReview): instance

        Returns:
            list: Serialized document verifications
        """
        document_verifications = instance.get_document_verifications()
        serializer = DocumentVerificationSerializer(document_verifications, many=True, read_only=True)
        return serializer.data

    def get_stipulation_verifications(self, instance: QCReview) -> list:
        """
        Gets stipulation verifications for the QC review

        Args:
            instance (QCReview): instance

        Returns:
            list: Serialized stipulation verifications
        """
        stipulation_verifications = instance.get_stipulation_verifications()
        serializer = QCStipulationVerificationSerializer(stipulation_verifications, many=True, read_only=True)
        return serializer.data

    def get_checklist_items(self, instance: QCReview) -> list:
        """
        Gets checklist items for the QC review

        Args:
            instance (QCReview): instance

        Returns:
            list: Serialized checklist items
        """
        checklist_items = instance.get_checklist_items()
        serializer = QCChecklistItemSerializer(checklist_items, many=True, read_only=True)
        return serializer.data

    def get_completion_percentage(self, instance: QCReview) -> float:
        """
        Gets the completion percentage for the QC review

        Args:
            instance (QCReview): instance

        Returns:
            float: Completion percentage
        """
        return instance.get_completion_percentage()


class QCReviewListSerializer(BaseModelSerializer):
    """
    Serializer for QCReview model optimized for list views
    """
    application_id = serializers.CharField(source='application.id', read_only=True)
    borrower_name = serializers.CharField(source='application.borrower.get_full_name', read_only=True)
    school_name = serializers.CharField(source='application.school.name', read_only=True)
    program_name = serializers.CharField(source='application.program.name', read_only=True)
    loan_amount = serializers.DecimalField(source='application.loan_details.approved_amount', max_digits=10, decimal_places=2, read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    completion_percentage = serializers.SerializerMethodField()

    class Meta:
        model = QCReview
        fields = ['id', 'application_id', 'borrower_name', 'school_name', 'program_name', 'loan_amount', 'status', 'priority', 'assigned_to', 'assigned_to_name', 'assigned_at', 'completed_at', 'completion_percentage']

    def get_completion_percentage(self, instance: QCReview) -> float:
        """
        Gets the completion percentage for the QC review

        Args:
            instance (QCReview): instance

        Returns:
            float: Completion percentage
        """
        return instance.get_completion_percentage()


class DocumentVerificationSerializer(BaseModelSerializer):
    """
    Serializer for DocumentVerification model
    """
    document_details = DocumentSerializer(source='document', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.get_full_name', read_only=True)

    class Meta:
        model = DocumentVerification
        fields = ['id', 'qc_review', 'document', 'document_details', 'status', 'verified_by', 'verified_by_name', 'verified_at', 'comments']

    def validate(self, data: dict) -> dict:
        """
        Validates the DocumentVerification data

        Args:
            data (dict): data

        Returns:
            dict: Validated data
        """
        if data.get('status') in (QC_VERIFICATION_STATUS['VERIFIED'], QC_VERIFICATION_STATUS['REJECTED'], QC_VERIFICATION_STATUS['WAIVED']) and not data.get('comments'):
            raise ValidationError("Comments are required when status is verified, rejected, or waived")
        return data

    def update(self, instance: DocumentVerification, validated_data: dict) -> DocumentVerification:
        """
        Updates a DocumentVerification instance

        Args:
            instance (DocumentVerification): instance
            validated_data (dict): validated_data

        Returns:
            DocumentVerification: Updated instance
        """
        user = self.context['request'].user
        status = validated_data.get('status')
        comments = validated_data.get('comments')

        if status == QC_VERIFICATION_STATUS['VERIFIED']:
            instance.verify(user, comments)
        elif status == QC_VERIFICATION_STATUS['REJECTED']:
            instance.reject(user, comments)
        elif status == QC_VERIFICATION_STATUS['WAIVED']:
            instance.waive(user, comments)
        else:
            return super().update(instance, validated_data)

        return instance


class QCStipulationVerificationSerializer(BaseModelSerializer):
    """
    Serializer for QCStipulationVerification model
    """
    stipulation_details = StipulationSerializer(source='stipulation', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.get_full_name', read_only=True)

    class Meta:
        model = QCStipulationVerification
        fields = ['id', 'qc_review', 'stipulation', 'stipulation_details', 'status', 'verified_by', 'verified_by_name', 'verified_at', 'comments']

    def validate(self, data: dict) -> dict:
        """
        Validates the QCStipulationVerification data

        Args:
            data (dict): data

        Returns:
            dict: Validated data
        """
        if data.get('status') in (QC_VERIFICATION_STATUS['VERIFIED'], QC_VERIFICATION_STATUS['REJECTED'], QC_VERIFICATION_STATUS['WAIVED']) and not data.get('comments'):
            raise ValidationError("Comments are required when status is verified, rejected, or waived")
        return data

    def update(self, instance: QCStipulationVerification, validated_data: dict) -> QCStipulationVerification:
        """
        Updates a QCStipulationVerification instance

        Args:
            instance (QCStipulationVerification): instance
            validated_data (dict): validated_data

        Returns:
            QCStipulationVerification: Updated instance
        """
        user = self.context['request'].user
        status = validated_data.get('status')
        comments = validated_data.get('comments')

        if status == QC_VERIFICATION_STATUS['VERIFIED']:
            instance.verify(user, comments)
        elif status == QC_VERIFICATION_STATUS['REJECTED']:
            instance.reject(user, comments)
        elif status == QC_VERIFICATION_STATUS['WAIVED']:
            instance.waive(user, comments)
        else:
            return super().update(instance, validated_data)

        return instance


class QCChecklistItemSerializer(BaseModelSerializer):
    """
    Serializer for QCChecklistItem model
    """
    verified_by_name = serializers.CharField(source='verified_by.get_full_name', read_only=True)

    class Meta:
        model = QCChecklistItem
        fields = ['id', 'qc_review', 'category', 'item_text', 'status', 'verified_by', 'verified_by_name', 'verified_at', 'comments']

    def validate(self, data: dict) -> dict:
        """
        Validates the QCChecklistItem data

        Args:
            data (dict): data

        Returns:
            dict: Validated data
        """
        if data.get('status') in (QC_VERIFICATION_STATUS['VERIFIED'], QC_VERIFICATION_STATUS['REJECTED'], QC_VERIFICATION_STATUS['WAIVED']) and not data.get('comments'):
            raise ValidationError("Comments are required when status is verified, rejected, or waived")
        return data

    def update(self, instance: QCChecklistItem, validated_data: dict) -> QCChecklistItem:
        """
        Updates a QCChecklistItem instance

        Args:
            instance (QCChecklistItem): instance
            validated_data (dict): validated_data

        Returns:
            QCChecklistItem: Updated instance
        """
        user = self.context['request'].user
        status = validated_data.get('status')
        comments = validated_data.get('comments')

        if status == QC_VERIFICATION_STATUS['VERIFIED']:
            instance.verify(user, comments)
        elif status == QC_VERIFICATION_STATUS['REJECTED']:
            instance.reject(user, comments)
        elif status == QC_VERIFICATION_STATUS['WAIVED']:
            instance.waive(user, comments)
        else:
            return super().update(instance, validated_data)

        return instance


class QCNoteSerializer(BaseModelSerializer):
    """
    Serializer for QCNote model
    """
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = QCNote
        fields = ['id', 'qc_review', 'note_text', 'created_at', 'created_by', 'created_by_name', 'is_internal']

    def create(self, validated_data: dict) -> QCNote:
        """
        Creates a new QCNote instance

        Args:
            validated_data (dict): validated_data

        Returns:
            QCNote: Created instance
        """
        user = self.context['request'].user
        validated_data['created_by'] = user
        return super().create(validated_data)


class QCReviewAssignmentSerializer(serializers.Serializer):
    """
    Serializer for assigning QC reviews to reviewers
    """
    reviewer_id = serializers.UUIDField()
    assignment_type = serializers.ChoiceField(choices=[(k, v) for k, v in QC_ASSIGNMENT_TYPE.items()], default=QC_ASSIGNMENT_TYPE['MANUAL'])

    def validate(self, data: dict) -> dict:
        """
        Validates the assignment data

        Args:
            data (dict): data

        Returns:
            dict: Validated data
        """
        reviewer_id = data.get('reviewer_id')
        try:
            user = get_user_model().objects.get(pk=reviewer_id)
        except get_user_model().DoesNotExist:
            raise ValidationError("Invalid reviewer ID")

        # Check if the user has permission to be a QC reviewer
        if user.user_type not in ['qc', 'system_admin']:
            raise ValidationError("User does not have permission to be a QC reviewer")

        return data

    def save(self, **kwargs) -> QCReview:
        """
        Saves the assignment

        Args:
            kwargs (dict): kwargs

        Returns:
            QCReview: Updated QC review
        """
        qc_review = self.context.get('qc_review')
        reviewer_id = self.validated_data.get('reviewer_id')
        assignment_type = self.validated_data.get('assignment_type')

        reviewer = get_user_model().objects.get(pk=reviewer_id)
        qc_review.assign_to(reviewer, assignment_type)
        return qc_review


class QCReviewStatusUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating QC review status
    """
    status = serializers.ChoiceField(choices=[(k, v) for k, v in QC_STATUS.items()])
    return_reason = serializers.ChoiceField(choices=[(k, v) for k, v in QC_RETURN_REASON.items()], required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_null=True)

    def validate(self, data: dict) -> dict:
        """
        Validates the status update data

        Args:
            data (dict): data

        Returns:
            dict: Validated data
        """
        status = data.get('status')
        if status == QC_STATUS['APPROVED']:
            qc_review = self.context.get('qc_review')
            if not qc_review.is_complete():
                raise ValidationError("All verifications must be complete before approving")
        if status == QC_STATUS['RETURNED'] and not data.get('return_reason'):
            raise ValidationError("Return reason is required when status is returned")
        return data

    def save(self, **kwargs) -> QCReview:
        """
        Saves the status update

        Args:
            kwargs (dict): kwargs

        Returns:
            QCReview: Updated QC review
        """
        qc_review = self.context.get('qc_review')
        user = self.context['request'].user
        status = self.validated_data.get('status')
        return_reason = self.validated_data.get('return_reason')
        notes = self.validated_data.get('notes')

        if status == QC_STATUS['APPROVED']:
            qc_review.approve(user, notes)
        elif status == QC_STATUS['RETURNED']:
            qc_review.return_for_correction(user, return_reason, notes)
        return qc_review


class QCReviewSummarySerializer(serializers.Serializer):
    """
    Serializer for QC review summary statistics
    """
    pending_count = serializers.IntegerField()
    in_review_count = serializers.IntegerField()
    approved_count = serializers.IntegerField()
    returned_count = serializers.IntegerField()
    overdue_count = serializers.IntegerField()
    assigned_to_me_count = serializers.IntegerField()
    completed_today_count = serializers.IntegerField()
    average_completion_time = serializers.FloatField()