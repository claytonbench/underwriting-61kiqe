import { createAsyncThunk } from '@reduxjs/toolkit'; // ^1.9.5
import {
  QCReview,
  QCReviewListItem,
  QCReviewFilters,
  QCReviewSort,
  QCStatus,
  QCVerificationStatus,
  QCReturnReason,
  DocumentVerificationRequest,
  StipulationVerificationRequest,
  ChecklistItemVerificationRequest,
  QCReviewDecisionRequest,
  QCReviewAssignmentRequest,
  QCCountsByStatus
} from '../../types/qc.types';
import { UUID } from '../../types/common.types';
import {
  getQCReviews,
  getQCReview,
  getQCReviewByApplication,
  assignQCReview,
  startQCReview,
  submitQCDecision,
  updateDocumentVerification,
  updateStipulationVerification,
  updateChecklistItemVerification,
  getQCCountsByStatus,
  getMyAssignedQCReviews,
  addQCReviewNote
} from '../../api/qc';
import { handleApiError } from '../../config/api';

/**
 * Thunk to fetch a paginated list of QC reviews with optional filtering and sorting
 */
export const fetchQCReviewsThunk = createAsyncThunk(
  'qc/fetchQCReviews',
  async ({ page = 1, pageSize = 10, filters, sort }: {
    page?: number;
    pageSize?: number;
    filters?: QCReviewFilters;
    sort?: QCReviewSort;
  }) => {
    try {
      const response = await getQCReviews({
        page,
        page_size: pageSize,
        filters,
        sort
      });
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch QC reviews');
      }
      
      return {
        reviews: response.data?.results || [],
        total: response.data?.total || 0
      };
    } catch (error) {
      throw handleApiError(error);
    }
  }
);

/**
 * Thunk to fetch QC reviews assigned to the current user
 */
export const fetchMyAssignedQCReviewsThunk = createAsyncThunk(
  'qc/fetchMyAssignedQCReviews',
  async ({ page = 1, pageSize = 10, filters, sort }: {
    page?: number;
    pageSize?: number;
    filters?: QCReviewFilters;
    sort?: QCReviewSort;
  }) => {
    try {
      const response = await getMyAssignedQCReviews({
        page,
        page_size: pageSize,
        filters,
        sort
      });
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch assigned QC reviews');
      }
      
      return {
        reviews: response.data?.results || [],
        total: response.data?.total || 0
      };
    } catch (error) {
      throw handleApiError(error);
    }
  }
);

/**
 * Thunk to fetch a single QC review by ID with all related details
 */
export const fetchQCReviewDetailThunk = createAsyncThunk(
  'qc/fetchQCReviewDetail',
  async (id: UUID) => {
    try {
      const response = await getQCReview(id);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch QC review details');
      }
      
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }
);

/**
 * Thunk to fetch a QC review for a specific application
 */
export const fetchQCReviewByApplicationThunk = createAsyncThunk(
  'qc/fetchQCReviewByApplication',
  async (applicationId: UUID) => {
    try {
      const response = await getQCReviewByApplication(applicationId);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch QC review for application');
      }
      
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }
);

/**
 * Thunk to assign a QC review to a specific reviewer
 */
export const assignQCReviewThunk = createAsyncThunk(
  'qc/assignQCReview',
  async (data: QCReviewAssignmentRequest) => {
    try {
      const response = await assignQCReview(data);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to assign QC review');
      }
      
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }
);

/**
 * Thunk to start the QC review process, changing its status from pending to in_review
 */
export const startQCReviewThunk = createAsyncThunk(
  'qc/startQCReview',
  async (id: UUID) => {
    try {
      const response = await startQCReview(id);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to start QC review');
      }
      
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }
);

/**
 * Thunk to submit a decision for a QC review (approve or return)
 */
export const submitQCDecisionThunk = createAsyncThunk(
  'qc/submitQCDecision',
  async (data: QCReviewDecisionRequest) => {
    try {
      const response = await submitQCDecision(data);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to submit QC decision');
      }
      
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }
);

/**
 * Thunk to verify a document in a QC review
 */
export const verifyDocumentThunk = createAsyncThunk(
  'qc/verifyDocument',
  async (data: DocumentVerificationRequest) => {
    try {
      const request: DocumentVerificationRequest = {
        ...data,
        status: QCVerificationStatus.VERIFIED
      };
      
      const response = await updateDocumentVerification(request);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to verify document');
      }
      
      return {
        id: data.document_verification_id,
        status: QCVerificationStatus.VERIFIED,
        comments: data.comments
      };
    } catch (error) {
      throw handleApiError(error);
    }
  }
);

/**
 * Thunk to reject a document in a QC review
 */
export const rejectDocumentThunk = createAsyncThunk(
  'qc/rejectDocument',
  async ({ document_verification_id, comments }: { document_verification_id: UUID; comments?: string }) => {
    try {
      const request: DocumentVerificationRequest = {
        document_verification_id,
        status: QCVerificationStatus.REJECTED,
        comments: comments || null
      };
      
      const response = await updateDocumentVerification(request);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to reject document');
      }
      
      return {
        id: document_verification_id,
        status: QCVerificationStatus.REJECTED,
        comments
      };
    } catch (error) {
      throw handleApiError(error);
    }
  }
);

/**
 * Thunk to verify a stipulation in a QC review
 */
export const verifyStipulationThunk = createAsyncThunk(
  'qc/verifyStipulation',
  async (data: StipulationVerificationRequest) => {
    try {
      const request: StipulationVerificationRequest = {
        ...data,
        status: QCVerificationStatus.VERIFIED
      };
      
      const response = await updateStipulationVerification(request);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to verify stipulation');
      }
      
      return {
        id: data.stipulation_verification_id,
        status: QCVerificationStatus.VERIFIED,
        comments: data.comments
      };
    } catch (error) {
      throw handleApiError(error);
    }
  }
);

/**
 * Thunk to reject a stipulation in a QC review
 */
export const rejectStipulationThunk = createAsyncThunk(
  'qc/rejectStipulation',
  async ({ stipulation_verification_id, comments }: { stipulation_verification_id: UUID; comments?: string }) => {
    try {
      const request: StipulationVerificationRequest = {
        stipulation_verification_id,
        status: QCVerificationStatus.REJECTED,
        comments: comments || null
      };
      
      const response = await updateStipulationVerification(request);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to reject stipulation');
      }
      
      return {
        id: stipulation_verification_id,
        status: QCVerificationStatus.REJECTED,
        comments
      };
    } catch (error) {
      throw handleApiError(error);
    }
  }
);

/**
 * Thunk to waive a stipulation in a QC review
 */
export const waiveStipulationThunk = createAsyncThunk(
  'qc/waiveStipulation',
  async ({ stipulation_verification_id, comments }: { stipulation_verification_id: UUID; comments?: string }) => {
    try {
      const request: StipulationVerificationRequest = {
        stipulation_verification_id,
        status: QCVerificationStatus.WAIVED,
        comments: comments || null
      };
      
      const response = await updateStipulationVerification(request);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to waive stipulation');
      }
      
      return {
        id: stipulation_verification_id,
        status: QCVerificationStatus.WAIVED,
        comments
      };
    } catch (error) {
      throw handleApiError(error);
    }
  }
);

/**
 * Thunk to verify a checklist item in a QC review
 */
export const verifyChecklistItemThunk = createAsyncThunk(
  'qc/verifyChecklistItem',
  async (data: ChecklistItemVerificationRequest) => {
    try {
      const request: ChecklistItemVerificationRequest = {
        ...data,
        status: QCVerificationStatus.VERIFIED
      };
      
      const response = await updateChecklistItemVerification(request);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to verify checklist item');
      }
      
      return {
        id: data.checklist_item_id,
        status: QCVerificationStatus.VERIFIED,
        comments: data.comments
      };
    } catch (error) {
      throw handleApiError(error);
    }
  }
);

/**
 * Thunk to reject a checklist item in a QC review
 */
export const rejectChecklistItemThunk = createAsyncThunk(
  'qc/rejectChecklistItem',
  async ({ checklist_item_id, comments }: { checklist_item_id: UUID; comments?: string }) => {
    try {
      const request: ChecklistItemVerificationRequest = {
        checklist_item_id,
        status: QCVerificationStatus.REJECTED,
        comments: comments || null
      };
      
      const response = await updateChecklistItemVerification(request);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to reject checklist item');
      }
      
      return {
        id: checklist_item_id,
        status: QCVerificationStatus.REJECTED,
        comments
      };
    } catch (error) {
      throw handleApiError(error);
    }
  }
);

/**
 * Thunk to waive a checklist item in a QC review
 */
export const waiveChecklistItemThunk = createAsyncThunk(
  'qc/waiveChecklistItem',
  async ({ checklist_item_id, comments }: { checklist_item_id: UUID; comments?: string }) => {
    try {
      const request: ChecklistItemVerificationRequest = {
        checklist_item_id,
        status: QCVerificationStatus.WAIVED,
        comments: comments || null
      };
      
      const response = await updateChecklistItemVerification(request);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to waive checklist item');
      }
      
      return {
        id: checklist_item_id,
        status: QCVerificationStatus.WAIVED,
        comments
      };
    } catch (error) {
      throw handleApiError(error);
    }
  }
);

/**
 * Thunk to add a note to a QC review
 */
export const addQCReviewNoteThunk = createAsyncThunk(
  'qc/addQCReviewNote',
  async ({ id, note }: { id: UUID; note: string }) => {
    try {
      const response = await addQCReviewNote(id, note);
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to add QC review note');
      }
      
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }
);

/**
 * Thunk to fetch counts of QC reviews grouped by status
 */
export const fetchQCCountsByStatusThunk = createAsyncThunk(
  'qc/fetchQCCountsByStatus',
  async () => {
    try {
      const response = await getQCCountsByStatus();
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch QC counts by status');
      }
      
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }
);