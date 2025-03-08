import { createAsyncThunk } from '@reduxjs/toolkit'; // ^1.9.5

import {
  QCReview, 
  QCReviewListItem, 
  QCReviewFilters, 
  QCReviewSort, 
  DocumentVerification, 
  QCStipulationVerification, 
  QCChecklistItem, 
  QCReviewDecisionRequest, 
  QCReviewAssignmentRequest, 
  DocumentVerificationRequest, 
  StipulationVerificationRequest, 
  ChecklistItemVerificationRequest, 
  QCVerificationStatus, 
  QCStatus, 
  QCCountsByStatus
} from '../../types/qc.types';

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

import { UUID } from '../../types/common.types';

/**
 * Async thunk to fetch a paginated list of QC reviews
 */
export const fetchQCReviews = createAsyncThunk(
  'qc/fetchQCReviews',
  async ({
    page,
    pageSize,
    filters,
    sort
  }: {
    page: number;
    pageSize: number;
    filters?: QCReviewFilters;
    sort?: QCReviewSort;
  }) => {
    const response = await getQCReviews({
      page,
      page_size: pageSize,
      filters,
      sort
    });
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch QC reviews');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to fetch a single QC review by ID with all related details
 */
export const fetchQCReviewDetail = createAsyncThunk(
  'qc/fetchQCReviewDetail',
  async (id: UUID) => {
    const response = await getQCReview(id);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch QC review details');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to fetch a QC review for a specific application
 */
export const fetchQCReviewByApplication = createAsyncThunk(
  'qc/fetchQCReviewByApplication',
  async (applicationId: UUID) => {
    const response = await getQCReviewByApplication(applicationId);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch QC review for application');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to create a new QC review for an application
 */
export const createNewQCReview = createAsyncThunk(
  'qc/createNewQCReview',
  async (applicationId: UUID) => {
    const response = await getQCReviewByApplication(applicationId);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to create new QC review');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to assign a QC review to a specific reviewer
 */
export const assignQCReviewToReviewer = createAsyncThunk(
  'qc/assignQCReviewToReviewer',
  async (assignmentData: QCReviewAssignmentRequest) => {
    const response = await assignQCReview(assignmentData);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to assign QC review');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to start the QC review process, changing its status from pending to in_review
 */
export const startQCReviewProcess = createAsyncThunk(
  'qc/startQCReviewProcess',
  async (id: UUID) => {
    const response = await startQCReview(id);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to start QC review process');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to submit a decision for a QC review (approve or return)
 */
export const updateQCReviewStatusAction = createAsyncThunk(
  'qc/updateQCReviewStatusAction',
  async (decisionData: QCReviewDecisionRequest) => {
    const response = await submitQCDecision(decisionData);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to submit QC decision');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to fetch document verifications for a QC review
 */
export const fetchDocumentVerifications = createAsyncThunk(
  'qc/fetchDocumentVerifications',
  async (qcReviewId: UUID) => {
    const response = await getQCReview(qcReviewId);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch document verifications');
    }
    
    return response.data.document_verifications;
  }
);

/**
 * Async thunk to mark a document as verified in a QC review
 */
export const verifyDocumentAction = createAsyncThunk(
  'qc/verifyDocumentAction',
  async (verificationData: DocumentVerificationRequest) => {
    // Set status to VERIFIED in the verification data
    const dataWithStatus = {
      ...verificationData,
      status: QCVerificationStatus.VERIFIED
    };
    
    const response = await updateDocumentVerification(dataWithStatus);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to verify document');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to mark a document as rejected in a QC review
 */
export const rejectDocumentAction = createAsyncThunk(
  'qc/rejectDocumentAction',
  async (verificationData: DocumentVerificationRequest) => {
    // Set status to REJECTED in the verification data
    const dataWithStatus = {
      ...verificationData,
      status: QCVerificationStatus.REJECTED
    };
    
    const response = await updateDocumentVerification(dataWithStatus);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to reject document');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to fetch stipulation verifications for a QC review
 */
export const fetchStipulationVerifications = createAsyncThunk(
  'qc/fetchStipulationVerifications',
  async (qcReviewId: UUID) => {
    const response = await getQCReview(qcReviewId);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch stipulation verifications');
    }
    
    return response.data.stipulation_verifications;
  }
);

/**
 * Async thunk to mark a stipulation as verified in a QC review
 */
export const verifyStipulationAction = createAsyncThunk(
  'qc/verifyStipulationAction',
  async (verificationData: StipulationVerificationRequest) => {
    // Set status to VERIFIED in the verification data
    const dataWithStatus = {
      ...verificationData,
      status: QCVerificationStatus.VERIFIED
    };
    
    const response = await updateStipulationVerification(dataWithStatus);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to verify stipulation');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to mark a stipulation as rejected in a QC review
 */
export const rejectStipulationAction = createAsyncThunk(
  'qc/rejectStipulationAction',
  async (verificationData: StipulationVerificationRequest) => {
    // Set status to REJECTED in the verification data
    const dataWithStatus = {
      ...verificationData,
      status: QCVerificationStatus.REJECTED
    };
    
    const response = await updateStipulationVerification(dataWithStatus);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to reject stipulation');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to mark a stipulation as waived in a QC review
 */
export const waiveStipulationAction = createAsyncThunk(
  'qc/waiveStipulationAction',
  async (verificationData: StipulationVerificationRequest) => {
    // Set status to WAIVED in the verification data
    const dataWithStatus = {
      ...verificationData,
      status: QCVerificationStatus.WAIVED
    };
    
    const response = await updateStipulationVerification(dataWithStatus);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to waive stipulation');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to fetch checklist items for a QC review
 */
export const fetchChecklistItems = createAsyncThunk(
  'qc/fetchChecklistItems',
  async (qcReviewId: UUID) => {
    const response = await getQCReview(qcReviewId);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch checklist items');
    }
    
    return response.data.checklist_items;
  }
);

/**
 * Async thunk to mark a checklist item as verified in a QC review
 */
export const verifyChecklistItemAction = createAsyncThunk(
  'qc/verifyChecklistItemAction',
  async (verificationData: ChecklistItemVerificationRequest) => {
    // Set status to VERIFIED in the verification data
    const dataWithStatus = {
      ...verificationData,
      status: QCVerificationStatus.VERIFIED
    };
    
    const response = await updateChecklistItemVerification(dataWithStatus);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to verify checklist item');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to mark a checklist item as rejected in a QC review
 */
export const rejectChecklistItemAction = createAsyncThunk(
  'qc/rejectChecklistItemAction',
  async (verificationData: ChecklistItemVerificationRequest) => {
    // Set status to REJECTED in the verification data
    const dataWithStatus = {
      ...verificationData,
      status: QCVerificationStatus.REJECTED
    };
    
    const response = await updateChecklistItemVerification(dataWithStatus);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to reject checklist item');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to mark a checklist item as waived in a QC review
 */
export const waiveChecklistItemAction = createAsyncThunk(
  'qc/waiveChecklistItemAction',
  async (verificationData: ChecklistItemVerificationRequest) => {
    // Set status to WAIVED in the verification data
    const dataWithStatus = {
      ...verificationData,
      status: QCVerificationStatus.WAIVED
    };
    
    const response = await updateChecklistItemVerification(dataWithStatus);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to waive checklist item');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to fetch notes for a QC review
 */
export const fetchQCNotes = createAsyncThunk(
  'qc/fetchQCNotes',
  async (qcReviewId: UUID) => {
    const response = await getQCReview(qcReviewId);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch QC notes');
    }
    
    return response.data.notes;
  }
);

/**
 * Async thunk to add a note to a QC review
 */
export const createQCNoteAction = createAsyncThunk(
  'qc/createQCNoteAction',
  async ({ qcReviewId, note }: { qcReviewId: UUID; note: string }) => {
    const response = await addQCReviewNote(qcReviewId, note);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to create QC note');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to fetch summary statistics for QC reviews
 */
export const fetchQCReviewSummaryAction = createAsyncThunk(
  'qc/fetchQCReviewSummaryAction',
  async () => {
    const response = await getQCCountsByStatus();
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch QC review summary');
    }
    
    return response.data;
  }
);

/**
 * Async thunk to fetch QC reviews assigned to the current user
 */
export const fetchMyAssignedQCReviews = createAsyncThunk(
  'qc/fetchMyAssignedQCReviews',
  async ({
    page,
    pageSize,
    filters,
    sort
  }: {
    page: number;
    pageSize: number;
    filters?: QCReviewFilters;
    sort?: QCReviewSort;
  }) => {
    const response = await getMyAssignedQCReviews({
      page,
      page_size: pageSize,
      filters,
      sort
    });
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch assigned QC reviews');
    }
    
    return response.data;
  }
);