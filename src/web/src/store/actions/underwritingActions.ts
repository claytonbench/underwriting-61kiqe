import { createAction, createAsyncThunk } from '@reduxjs/toolkit'; // ^1.9.5

import {
  UnderwritingQueueItem,
  UnderwritingQueueFilters,
  UnderwritingQueueSort,
  UnderwritingApplicationDetail,
  UnderwritingDecisionRequest,
  UnderwritingNoteCreateRequest,
  StipulationUpdateRequest
} from '../../types/underwriting.types';

import {
  getUnderwritingQueue,
  getApplicationForUnderwriting,
  assignApplication,
  startApplicationReview,
  getCreditInformation,
  uploadCreditInformation,
  createUnderwritingDecision,
  getUnderwritingDecision,
  getStipulations,
  updateStipulation,
  createUnderwritingNote,
  getUnderwritingNotes,
  getUnderwritingMetrics,
  updateQueuePriority,
  returnApplicationForRevision
} from '../../api/underwriting';

// Simple action creators
export const setUnderwritingFilters = createAction<UnderwritingQueueFilters>(
  'underwriting/setFilters'
);

export const setUnderwritingSort = createAction<UnderwritingQueueSort>(
  'underwriting/setSort'
);

export const selectApplication = createAction<string>(
  'underwriting/selectApplication'
);

export const clearSelectedApplication = createAction(
  'underwriting/clearSelectedApplication'
);

export const resetUnderwritingState = createAction(
  'underwriting/resetState'
);

export const clearUnderwritingError = createAction(
  'underwriting/clearError'
);

export const updateDecisionDraft = createAction<Partial<UnderwritingDecisionRequest>>(
  'underwriting/updateDecisionDraft'
);

// Async thunk action creators
export const fetchUnderwritingQueue = createAsyncThunk(
  'underwriting/fetchQueue',
  async ({ 
    page = 1, 
    pageSize = 10, 
    filters = {}, 
    sort = {} 
  }: { 
    page?: number; 
    pageSize?: number; 
    filters?: UnderwritingQueueFilters; 
    sort?: UnderwritingQueueSort 
  }) => {
    const response = await getUnderwritingQueue({
      page,
      page_size: pageSize,
      filters,
      sort
    });
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch underwriting queue');
    }
    
    return response.data;
  }
);

export const fetchAssignedApplications = createAsyncThunk(
  'underwriting/fetchAssigned',
  async ({ 
    page = 1, 
    pageSize = 10, 
    filters = {}, 
    sort = {} 
  }: { 
    page?: number; 
    pageSize?: number; 
    filters?: UnderwritingQueueFilters; 
    sort?: UnderwritingQueueSort 
  }) => {
    const response = await getUnderwritingQueue({
      page,
      page_size: pageSize,
      filters: { ...filters, assigned_to: 'current_user' },
      sort
    });
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch assigned applications');
    }
    
    return response.data;
  }
);

export const fetchApplicationDetail = createAsyncThunk(
  'underwriting/fetchApplicationDetail',
  async (applicationId: string) => {
    const response = await getApplicationForUnderwriting(applicationId);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch application details');
    }
    
    return response.data;
  }
);

export const assignApplicationToUnderwriter = createAsyncThunk(
  'underwriting/assignApplication',
  async ({ queueId, underwriterId }: { queueId: string; underwriterId: string }) => {
    const response = await assignApplication({
      queue_id: queueId,
      underwriter_id: underwriterId
    });
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to assign application');
    }
    
    return response.data;
  }
);

export const unassignApplicationFromUnderwriter = createAsyncThunk(
  'underwriting/unassignApplication',
  async (queueId: string) => {
    const response = await assignApplication({
      queue_id: queueId,
      underwriter_id: null
    });
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to unassign application');
    }
    
    return response.data;
  }
);

export const startReviewingApplication = createAsyncThunk(
  'underwriting/startReviewing',
  async (queueId: string) => {
    const response = await startApplicationReview(queueId);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to start application review');
    }
    
    return response.data;
  }
);

export const fetchCreditInformation = createAsyncThunk(
  'underwriting/fetchCreditInfo',
  async ({ applicationId, isCoApplicant }: { applicationId: string; isCoApplicant: boolean }) => {
    const response = await getCreditInformation(applicationId, isCoApplicant);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch credit information');
    }
    
    return response.data;
  }
);

export const uploadCreditReportFile = createAsyncThunk(
  'underwriting/uploadCreditReport',
  async ({ 
    applicationId, 
    isCoApplicant, 
    creditScore, 
    monthlyDebt, 
    file 
  }: { 
    applicationId: string; 
    isCoApplicant: boolean; 
    creditScore: number; 
    monthlyDebt: number; 
    file: File 
  }) => {
    const response = await uploadCreditInformation(applicationId, {
      credit_score: creditScore,
      monthly_debt: monthlyDebt,
      report_file: file,
      is_co_borrower: isCoApplicant
    });
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to upload credit report');
    }
    
    return response.data;
  }
);

export const submitDecision = createAsyncThunk(
  'underwriting/submitDecision',
  async (decisionData: UnderwritingDecisionRequest) => {
    const response = await createUnderwritingDecision(decisionData);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to submit decision');
    }
    
    return response.data;
  }
);

export const fetchDecision = createAsyncThunk(
  'underwriting/fetchDecision',
  async (applicationId: string) => {
    const response = await getUnderwritingDecision(applicationId);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch decision');
    }
    
    return response.data;
  }
);

export const saveDraftDecision = createAsyncThunk(
  'underwriting/saveDraftDecision',
  async (decisionData: UnderwritingDecisionRequest) => {
    // This is a placeholder - in a real implementation, there would be an API function
    // to save a draft decision. For now, we'll just return the decision data
    return decisionData;
  }
);

export const fetchStipulations = createAsyncThunk(
  'underwriting/fetchStipulations',
  async (applicationId: string) => {
    const response = await getStipulations(applicationId);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch stipulations');
    }
    
    return response.data;
  }
);

export const updateStipulationStatus = createAsyncThunk(
  'underwriting/updateStipulation',
  async (updateData: StipulationUpdateRequest) => {
    const response = await updateStipulation(updateData);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to update stipulation');
    }
    
    return response.data;
  }
);

export const addNote = createAsyncThunk(
  'underwriting/addNote',
  async (noteData: UnderwritingNoteCreateRequest) => {
    const response = await createUnderwritingNote(noteData);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to add note');
    }
    
    return response.data;
  }
);

export const fetchNotes = createAsyncThunk(
  'underwriting/fetchNotes',
  async (applicationId: string) => {
    const response = await getUnderwritingNotes(applicationId);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch notes');
    }
    
    return response.data;
  }
);

export const fetchMetrics = createAsyncThunk(
  'underwriting/fetchMetrics',
  async ({ startDate, endDate }: { startDate?: string; endDate?: string } = {}) => {
    const response = await getUnderwritingMetrics({
      start_date: startDate,
      end_date: endDate
    });
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch metrics');
    }
    
    return response.data;
  }
);

export const updateApplicationPriority = createAsyncThunk(
  'underwriting/updatePriority',
  async ({ queueId, priority }: { queueId: string; priority: string }) => {
    const response = await updateQueuePriority(queueId, priority);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to update priority');
    }
    
    return response.data;
  }
);

export const requestApplicationRevision = createAsyncThunk(
  'underwriting/requestRevision',
  async ({ 
    applicationId, 
    comments, 
    requiredChanges 
  }: { 
    applicationId: string; 
    comments: string; 
    requiredChanges: string[] 
  }) => {
    const response = await returnApplicationForRevision(applicationId, {
      comments,
      required_changes: requiredChanges
    });
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to request revision');
    }
    
    return response.data;
  }
);