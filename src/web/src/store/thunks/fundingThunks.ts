import { createAsyncThunk } from '@reduxjs/toolkit';
import {
  FundingRequestDetail,
  FundingRequestListItem,
  Disbursement,
  DisbursementListItem,
  EnrollmentVerification,
  StipulationVerification,
  FundingNote,
  FundingStatusSummary,
  FundingFilters,
  DisbursementFilters,
  FundingSort,
  DisbursementSort,
  FundingApprovalRequest,
  EnrollmentVerificationRequest,
  StipulationVerificationRequest,
  DisbursementCreateRequest,
  FundingNoteCreateRequest
} from '../../types/funding.types';
import { UUID } from '../../types/common.types';
import {
  getFundingRequests as apiGetFundingRequests,
  getFundingRequest as apiGetFundingRequest,
  getFundingRequestsByApplication as apiGetFundingRequestsByApplication,
  approveFundingRequest as apiApproveFundingRequest,
  rejectFundingRequest as apiRejectFundingRequest,
  getDisbursements as apiGetDisbursements,
  getDisbursement as apiGetDisbursement,
  getDisbursementsByFundingRequest as apiGetDisbursementsByFundingRequest,
  createDisbursement as apiCreateDisbursement,
  updateDisbursementStatus as apiUpdateDisbursementStatus,
  verifyEnrollment as apiVerifyEnrollment,
  getEnrollmentVerification as apiGetEnrollmentVerification,
  verifyStipulation as apiVerifyStipulation,
  getStipulationVerifications as apiGetStipulationVerifications,
  addFundingNote as apiAddFundingNote,
  getFundingNotes as apiGetFundingNotes,
  getFundingStatusSummary as apiGetFundingStatusSummary
} from '../../api/funding';

/**
 * Thunk to fetch a paginated list of funding requests with optional filtering and sorting
 */
export const fetchFundingRequests = createAsyncThunk(
  'funding/fetchFundingRequests',
  async ({ 
    page = 1, 
    pageSize = 10, 
    filters, 
    sort 
  }: { 
    page?: number; 
    pageSize?: number; 
    filters?: FundingFilters; 
    sort?: FundingSort 
  }) => {
    const response = await apiGetFundingRequests({ page, pageSize, filters, sort });
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch funding requests');
    }
    return response.data;
  }
);

/**
 * Thunk to fetch a single funding request by ID with detailed information
 */
export const fetchFundingRequestById = createAsyncThunk(
  'funding/fetchFundingRequestById',
  async (id: UUID) => {
    const response = await apiGetFundingRequest(id);
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch funding request details');
    }
    return response.data;
  }
);

/**
 * Thunk to fetch funding requests associated with a specific loan application
 */
export const fetchFundingRequestsByApplication = createAsyncThunk(
  'funding/fetchFundingRequestsByApplication',
  async (applicationId: UUID) => {
    const response = await apiGetFundingRequestsByApplication(applicationId);
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch funding requests by application');
    }
    return response.data;
  }
);

/**
 * Thunk to approve a funding request with specified amount and optional comments
 */
export const approveFundingRequest = createAsyncThunk(
  'funding/approveFundingRequest',
  async (approvalData: FundingApprovalRequest) => {
    const approvalResponse = await apiApproveFundingRequest(approvalData);
    if (!approvalResponse.success) {
      throw new Error(approvalResponse.message || 'Failed to approve funding request');
    }
    
    // Fetch the updated funding request details
    const detailResponse = await apiGetFundingRequest(approvalData.funding_request_id);
    if (!detailResponse.success) {
      throw new Error(detailResponse.message || 'Failed to fetch updated funding request details');
    }
    
    return detailResponse.data;
  }
);

/**
 * Thunk to reject a funding request with required comments
 */
export const rejectFundingRequest = createAsyncThunk(
  'funding/rejectFundingRequest',
  async ({ fundingRequestId, comments }: { fundingRequestId: UUID; comments: string }) => {
    const rejectionResponse = await apiRejectFundingRequest({ fundingRequestId, comments });
    if (!rejectionResponse.success) {
      throw new Error(rejectionResponse.message || 'Failed to reject funding request');
    }
    
    // Fetch the updated funding request details
    const detailResponse = await apiGetFundingRequest(fundingRequestId);
    if (!detailResponse.success) {
      throw new Error(detailResponse.message || 'Failed to fetch updated funding request details');
    }
    
    return detailResponse.data;
  }
);

/**
 * Thunk to fetch a paginated list of disbursements with optional filtering and sorting
 */
export const fetchDisbursements = createAsyncThunk(
  'funding/fetchDisbursements',
  async ({ 
    page = 1, 
    pageSize = 10, 
    filters, 
    sort 
  }: { 
    page?: number; 
    pageSize?: number; 
    filters?: DisbursementFilters; 
    sort?: DisbursementSort 
  }) => {
    const response = await apiGetDisbursements({ page, pageSize, filters, sort });
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch disbursements');
    }
    return response.data;
  }
);

/**
 * Thunk to fetch a single disbursement by ID
 */
export const fetchDisbursementById = createAsyncThunk(
  'funding/fetchDisbursementById',
  async (id: UUID) => {
    const response = await apiGetDisbursement(id);
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch disbursement details');
    }
    return response.data;
  }
);

/**
 * Thunk to fetch disbursements associated with a specific funding request
 */
export const fetchDisbursementsByFundingRequest = createAsyncThunk(
  'funding/fetchDisbursementsByFundingRequest',
  async (fundingRequestId: UUID) => {
    const response = await apiGetDisbursementsByFundingRequest(fundingRequestId);
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch disbursements by funding request');
    }
    return response.data;
  }
);

/**
 * Thunk to create a new disbursement for a funding request
 */
export const createDisbursement = createAsyncThunk(
  'funding/createDisbursement',
  async (disbursementData: DisbursementCreateRequest) => {
    const response = await apiCreateDisbursement(disbursementData);
    if (!response.success) {
      throw new Error(response.message || 'Failed to create disbursement');
    }
    return response.data;
  }
);

/**
 * Thunk to update the status of a disbursement with optional reference number
 */
export const updateDisbursementStatus = createAsyncThunk(
  'funding/updateDisbursementStatus',
  async ({ 
    disbursementId, 
    status, 
    referenceNumber 
  }: { 
    disbursementId: UUID; 
    status: string; 
    referenceNumber?: string 
  }) => {
    const response = await apiUpdateDisbursementStatus({ disbursementId, status, referenceNumber });
    if (!response.success) {
      throw new Error(response.message || 'Failed to update disbursement status');
    }
    return response.data;
  }
);

/**
 * Thunk to submit enrollment verification for a funding request
 */
export const verifyEnrollment = createAsyncThunk(
  'funding/verifyEnrollment',
  async (verificationData: EnrollmentVerificationRequest) => {
    const response = await apiVerifyEnrollment(verificationData);
    if (!response.success) {
      throw new Error(response.message || 'Failed to verify enrollment');
    }
    return response.data;
  }
);

/**
 * Thunk to fetch enrollment verification for a specific funding request
 */
export const fetchEnrollmentVerification = createAsyncThunk(
  'funding/fetchEnrollmentVerification',
  async (fundingRequestId: UUID) => {
    const response = await apiGetEnrollmentVerification(fundingRequestId);
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch enrollment verification');
    }
    return response.data;
  }
);

/**
 * Thunk to submit verification for a stipulation requirement
 */
export const verifyStipulation = createAsyncThunk(
  'funding/verifyStipulation',
  async (verificationData: StipulationVerificationRequest) => {
    const response = await apiVerifyStipulation(verificationData);
    if (!response.success) {
      throw new Error(response.message || 'Failed to verify stipulation');
    }
    return response.data;
  }
);

/**
 * Thunk to fetch stipulation verifications for a specific funding request
 */
export const fetchStipulationVerifications = createAsyncThunk(
  'funding/fetchStipulationVerifications',
  async (fundingRequestId: UUID) => {
    const response = await apiGetStipulationVerifications(fundingRequestId);
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch stipulation verifications');
    }
    return response.data;
  }
);

/**
 * Thunk to add a note to a funding request
 */
export const addFundingNote = createAsyncThunk(
  'funding/addFundingNote',
  async (noteData: FundingNoteCreateRequest) => {
    const response = await apiAddFundingNote(noteData);
    if (!response.success) {
      throw new Error(response.message || 'Failed to add funding note');
    }
    return response.data;
  }
);

/**
 * Thunk to fetch notes for a specific funding request
 */
export const fetchFundingNotes = createAsyncThunk(
  'funding/fetchFundingNotes',
  async (fundingRequestId: UUID) => {
    const response = await apiGetFundingNotes(fundingRequestId);
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch funding notes');
    }
    return response.data;
  }
);

/**
 * Thunk to fetch a summary of funding request statuses
 */
export const fetchFundingStatusSummary = createAsyncThunk(
  'funding/fetchFundingStatusSummary',
  async () => {
    const response = await apiGetFundingStatusSummary();
    if (!response.success) {
      throw new Error(response.message || 'Failed to fetch funding status summary');
    }
    return response.data;
  }
);