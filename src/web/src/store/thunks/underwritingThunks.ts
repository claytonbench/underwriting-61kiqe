import { createAsyncThunk } from '@reduxjs/toolkit'; // @reduxjs/toolkit ^1.9.5
import { RootState } from '../index';
import {
  UnderwritingQueueFilters,
  UnderwritingQueueSort,
  UnderwritingApplicationDetail,
  UnderwritingDecisionRequest,
  UnderwritingQueue,
  CreditInformation,
  Stipulation,
  UnderwritingNote,
  UnderwritingMetrics,
  UnderwritingQueueResponse,
  UnderwritingDecisionData,
  UnderwritingQueueAssignRequest,
  UnderwritingNoteCreateRequest,
  StipulationUpdateRequest,
  UUID
} from '../../types/underwriting.types';
import {
  getUnderwritingQueue,
  getApplicationForUnderwriting,
  assignApplication,
  startApplicationReview,
  getCreditInformation,
  uploadCreditInformation,
  getUnderwritingDecision,
  createUnderwritingDecision,
  getStipulations,
  updateStipulation,
  getUnderwritingNotes,
  createUnderwritingNote,
  getUnderwritingMetrics,
  updateQueuePriority,
  returnApplicationForRevision
} from '../../api/underwriting';

/**
 * Async thunk to fetch a paginated list of applications in the underwriting queue
 */
export const fetchUnderwritingQueue = createAsyncThunk<
  UnderwritingQueueResponse,
  {
    page?: number;
    page_size?: number;
    filters?: UnderwritingQueueFilters;
    sort?: UnderwritingQueueSort;
  },
  { state: RootState }
>(
  'underwriting/fetchQueue',
  async ({ page, page_size, filters, sort }, { getState }) => {
    // LD1: Extract state.underwriting.filters, state.underwriting.sort, state.underwriting.page, and state.underwriting.pageSize from getState()
    const { underwriting } = getState();
    const { filters: stateFilters, sort: stateSort } = underwriting;

    // LD1: Merge provided parameters with state values, with provided values taking precedence
    const mergedParams = {
      page: page !== undefined ? page : underwriting.page,
      page_size: page_size !== undefined ? page_size : underwriting.pageSize,
      filters: { ...stateFilters, ...filters },
      sort: sort !== undefined ? sort : stateSort,
    };

    // LD1: Call getUnderwritingQueue API function with merged parameters
    const response = await getUnderwritingQueue(mergedParams);

    // LD1: Return the response data or throw error for rejection
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch underwriting queue');
    }

    return response.data;
  }
);

/**
 * Async thunk to fetch applications assigned to the current underwriter
 */
export const fetchAssignedApplications = createAsyncThunk<
  UnderwritingQueueResponse,
  { page?: number; page_size?: number },
  { state: RootState }
>(
  'underwriting/fetchAssigned',
  async ({ page, page_size }, { getState }) => {
    // LD1: Extract state.auth.user.id to get current user ID
    const userId = getState().auth.user?.id;

    // LD1: Extract state.underwriting.page and state.underwriting.pageSize from getState()
    const { underwriting } = getState();

    // LD1: Merge provided parameters with state values, with provided values taking precedence
    const mergedParams = {
      page: page !== undefined ? page : underwriting.page,
      page_size: page_size !== undefined ? page_size : underwriting.pageSize,
    };

    // LD1: Create filters object with assigned_to set to current user ID
    const filters: UnderwritingQueueFilters = {
      assigned_to: userId || null,
    };

    // LD1: Call getUnderwritingQueue API function with merged parameters and filters
    const response = await getUnderwritingQueue({
      page: mergedParams.page,
      page_size: mergedParams.page_size,
      filters,
    });

    // LD1: Return the response data or throw error for rejection
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch assigned applications');
    }

    return response.data;
  }
);

/**
 * Async thunk to assign an application to an underwriter
 */
export const assignApplicationToUnderwriter = createAsyncThunk<
  UnderwritingQueue,
  UnderwritingQueueAssignRequest
>(
  'underwriting/assignApplication',
  async (assignRequest: UnderwritingQueueAssignRequest) => {
    // LD1: Call assignApplication API function with the provided assignment request
    const response = await assignApplication(assignRequest);

    // LD1: Return the response data or throw error for rejection
    if (!response.success) {
      throw new Error(response.message || 'Failed to assign application');
    }

    return response.data;
  }
);

/**
 * Async thunk to unassign an application from an underwriter
 */
export const unassignApplicationFromUnderwriter = createAsyncThunk<
  UnderwritingQueue,
  UUID
>(
  'underwriting/unassignApplication',
  async (queueId: UUID) => {
    // LD1: Create an assignment request with queue_id set to provided queueId and underwriter_id set to null
    const assignRequest: UnderwritingQueueAssignRequest = {
      queue_id: queueId,
      underwriter_id: null,
    };

    // LD1: Call assignApplication API function with the created assignment request
    const response = await assignApplication(assignRequest);

    // LD1: Return the response data or throw error for rejection
    if (!response.success) {
      throw new Error(response.message || 'Failed to unassign application');
    }

    return response.data;
  }
);

/**
 * Async thunk to mark an application as in review by the underwriter
 */
export const startReviewingApplication = createAsyncThunk<
  UnderwritingQueue,
  UUID
>(
  'underwriting/startReviewing',
  async (queueId: UUID) => {
    // LD1: Call startApplicationReview API function with the provided queueId
    const response = await startApplicationReview(queueId);

    // LD1: Return the response data or throw error for rejection
    if (!response.success) {
      throw new Error(response.message || 'Failed to start application review');
    }

    return response.data;
  }
);

/**
 * Async thunk to fetch comprehensive application data for underwriting review
 */
export const fetchApplicationDetail = createAsyncThunk<
  UnderwritingApplicationDetail,
  UUID
>(
  'underwriting/fetchApplicationDetail',
  async (applicationId: UUID) => {
    // LD1: Call getApplicationForUnderwriting API function with the provided applicationId
    const response = await getApplicationForUnderwriting(applicationId);

    // LD1: Return the response data or throw error for rejection
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch application details');
    }

    return response.data;
  }
);

/**
 * Async thunk to fetch credit information for a borrower or co-borrower
 */
export const fetchCreditInformation = createAsyncThunk<
  CreditInformation,
  { applicationId: UUID; isCoApplicant: boolean }
>(
  'underwriting/fetchCreditInfo',
  async ({ applicationId, isCoApplicant }) => {
    // LD1: Destructure applicationId and isCoApplicant from the provided parameters

    // LD1: Call getCreditInformation API function with applicationId and isCoApplicant
    const response = await getCreditInformation(applicationId, isCoApplicant);

    // LD1: Return the response data or throw error for rejection
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch credit information');
    }

    return response.data;
  }
);

/**
 * Async thunk to upload credit report information for a borrower or co-borrower
 */
export const uploadCreditReportFile = createAsyncThunk<
  CreditInformation,
  {
    applicationId: UUID;
    creditScore: number;
    monthlyDebt: number;
    reportFile: File;
    isCoApplicant: boolean;
  }
>(
  'underwriting/uploadCreditReport',
  async ({ applicationId, creditScore, monthlyDebt, reportFile, isCoApplicant }) => {
    // LD1: Destructure applicationId, creditScore, monthlyDebt, reportFile, and isCoApplicant from the provided parameters

    // LD1: Call uploadCreditInformation API function with applicationId and formatted credit data
    const response = await uploadCreditInformation(applicationId, {
      credit_score: creditScore,
      monthly_debt: monthlyDebt,
      report_file: reportFile,
      is_co_borrower: isCoApplicant,
    });

    // LD1: Return the response data or throw error for rejection
    if (!response.success) {
      throw new Error(response.message || 'Failed to upload credit report');
    }

    return response.data;
  }
);

/**
 * Async thunk to fetch the underwriting decision for an application
 */
export const fetchDecision = createAsyncThunk<
  UnderwritingDecisionData,
  UUID
>(
  'underwriting/fetchDecision',
  async (applicationId: UUID) => {
    // LD1: Call getUnderwritingDecision API function with the provided applicationId
    const response = await getUnderwritingDecision(applicationId);

    // LD1: Return the response data or throw error for rejection
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch decision');
    }

    return response.data;
  }
);

/**
 * Async thunk to submit an underwriting decision for an application
 */
export const submitDecision = createAsyncThunk<
  UnderwritingDecisionData,
  UnderwritingDecisionRequest
>(
  'underwriting/submitDecision',
  async (decisionRequest: UnderwritingDecisionRequest) => {
    // LD1: Call createUnderwritingDecision API function with the provided decisionRequest
    const response = await createUnderwritingDecision(decisionRequest);

    // LD1: Return the response data or throw error for rejection
    if (!response.success) {
      throw new Error(response.message || 'Failed to submit decision');
    }

    return response.data;
  }
);

/**
 * Async thunk to save a draft of an underwriting decision
 */
export const saveDraftDecision = createAsyncThunk<
  Partial<UnderwritingDecisionRequest>,
  Partial<UnderwritingDecisionRequest>
>(
  'underwriting/saveDraftDecision',
  async (decisionDraft: Partial<UnderwritingDecisionRequest>) => {
    // LD1: Return the provided draft data directly (no API call, just updates Redux state)
    // LD1: This thunk doesn't persist the draft to the backend, only to Redux state
    return decisionDraft;
  }
);

/**
 * Async thunk to fetch stipulations for an application
 */
export const fetchStipulations = createAsyncThunk<
  Stipulation[],
  { applicationId: UUID; status?: string }
>(
  'underwriting/fetchStipulations',
  async ({ applicationId, status }) => {
    // LD1: Destructure applicationId and status from the provided parameters

    // LD1: Call getStipulations API function with applicationId and optional status filter
    const response = await getStipulations(applicationId, { status });

    // LD1: Return the response data or throw error for rejection
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch stipulations');
    }

    return response.data;
  }
);

/**
 * Async thunk to update a stipulation's status
 */
export const updateStipulationStatus = createAsyncThunk<
  Stipulation,
  StipulationUpdateRequest
>(
  'underwriting/updateStipulation',
  async (updateRequest: StipulationUpdateRequest) => {
    // LD1: Call updateStipulation API function with the provided updateRequest
    const response = await updateStipulation(updateRequest);

    // LD1: Return the response data or throw error for rejection
    if (!response.success) {
      throw new Error(response.message || 'Failed to update stipulation');
    }

    return response.data;
  }
);

/**
 * Async thunk to add a note to an application in the underwriting process
 */
export const addNote = createAsyncThunk<
  UnderwritingNote,
  UnderwritingNoteCreateRequest
>(
  'underwriting/addNote',
  async (noteRequest: UnderwritingNoteCreateRequest) => {
    // LD1: Call createUnderwritingNote API function with the provided noteRequest
    const response = await createUnderwritingNote(noteRequest);

    // LD1: Return the response data or throw error for rejection
    if (!response.success) {
      throw new Error(response.message || 'Failed to add note');
    }

    return response.data;
  }
);

/**
 * Async thunk to fetch notes for an application in the underwriting process
 */
export const fetchNotes = createAsyncThunk<
  UnderwritingNote[],
  UUID
>(
  'underwriting/fetchNotes',
  async (applicationId: UUID) => {
    // LD1: Call getUnderwritingNotes API function with the provided applicationId
    const response = await getUnderwritingNotes(applicationId);

    // LD1: Return the response data or throw error for rejection
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch notes');
    }

    return response.data;
  }
);

/**
 * Async thunk to fetch metrics and statistics about the underwriting process
 */
export const fetchMetrics = createAsyncThunk<
  UnderwritingMetrics,
  { startDate?: string; endDate?: string }
>(
  'underwriting/fetchMetrics',
  async ({ startDate, endDate }: { startDate?: string; endDate?: string } = {}) => {
    // LD1: Destructure startDate and endDate from the provided parameters

    // LD1: Format parameters to match API expectations (start_date, end_date)
    const formattedParams = {
      start_date: startDate,
      end_date: endDate,
    };

    // LD1: Call getUnderwritingMetrics API function with formatted parameters
    const response = await getUnderwritingMetrics(formattedParams);

    // LD1: Return the response data or throw error for rejection
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch metrics');
    }

    return response.data;
  }
);

/**
 * Async thunk to update the priority of an application in the underwriting queue
 */
export const updateApplicationPriority = createAsyncThunk<
  UnderwritingQueue,
  { queueId: UUID; priority: string }
>(
  'underwriting/updatePriority',
  async ({ queueId, priority }: { queueId: UUID; priority: string }) => {
    // LD1: Destructure queueId and priority from the provided parameters

    // LD1: Make PUT request to underwriting/queue/:queueId/priority endpoint with priority data
    const response = await updateQueuePriority(queueId, priority);

    // LD1: Return the response data or throw error for rejection
    if (!response.success) {
      throw new Error(response.message || 'Failed to update priority');
    }

    return response.data;
  }
);

/**
 * Async thunk to request revisions for an application
 */
export const requestApplicationRevision = createAsyncThunk<
  UnderwritingQueue,
  {
    applicationId: UUID;
    comments: string;
    items: Array<{ field: string; reason: string }>;
  }
>(
  'underwriting/requestRevision',
  async ({ applicationId, comments, items }) => {
    // LD1: Destructure applicationId, comments, and items from the provided parameters

    // LD1: Make POST request to underwriting/applications/:applicationId/request-revision endpoint with revision data
    const response = await returnApplicationForRevision(applicationId, {
      comments,
      required_changes: items,
    });

    // LD1: Return the response data or throw error for rejection
    if (!response.success) {
      throw new Error(response.message || 'Failed to request revision');
    }

    return response.data;
  }
);