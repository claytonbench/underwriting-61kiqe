import { Dispatch } from 'redux';
import { ThunkDispatch } from 'redux-thunk';

import {
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

import {
  setFundingFilters,
  setFundingSort,
  setDisbursementFilters,
  setDisbursementSort,
  resetFundingState,
  clearFundingError
} from '../slices/fundingSlice';

import {
  fetchFundingRequests,
  fetchFundingRequestById,
  fetchFundingRequestsByApplication,
  approveFundingRequest,
  rejectFundingRequest,
  fetchDisbursements,
  fetchDisbursementById,
  fetchDisbursementsByFundingRequest,
  createDisbursement,
  updateDisbursementStatus,
  verifyEnrollment,
  fetchEnrollmentVerification,
  verifyStipulation,
  fetchStipulationVerifications,
  addFundingNote,
  fetchFundingNotes,
  fetchFundingStatusSummary
} from '../thunks/fundingThunks';

/**
 * Action creator that updates funding request filters and fetches filtered results
 * 
 * @param filters - Filter criteria for funding requests
 * @returns Thunk action function that dispatches filter update and fetches results
 */
export const updateFundingFilters = (filters: FundingFilters) => {
  return (dispatch: ThunkDispatch<any, any, any>, getState: () => any) => {
    // Update filters in the state
    dispatch(setFundingFilters(filters));
    
    // Get current page size
    const { pageSize } = getState().funding;
    
    // Fetch funding requests with updated filters
    // Reset to page 1 when filters change, maintain current pageSize
    dispatch(fetchFundingRequests({ page: 1, pageSize, filters }));
  };
};

/**
 * Action creator that updates funding request sort options and fetches sorted results
 * 
 * @param sort - Sort options for funding requests
 * @returns Thunk action function that dispatches sort update and fetches results
 */
export const updateFundingSort = (sort: FundingSort | null) => {
  return (dispatch: ThunkDispatch<any, any, any>, getState: () => any) => {
    // Update sort in the state
    dispatch(setFundingSort(sort));
    
    // Get current state values
    const state = getState();
    const { fundingPage: page, pageSize, fundingFilters: filters } = state.funding;
    
    // Fetch funding requests with current page, pageSize, filters, and updated sort
    dispatch(fetchFundingRequests({ 
      page, 
      pageSize, 
      filters, 
      sort 
    }));
  };
};

/**
 * Action creator that updates disbursement filters and fetches filtered results
 * 
 * @param filters - Filter criteria for disbursements
 * @returns Thunk action function that dispatches filter update and fetches results
 */
export const updateDisbursementFilters = (filters: DisbursementFilters) => {
  return (dispatch: ThunkDispatch<any, any, any>, getState: () => any) => {
    // Update filters in the state
    dispatch(setDisbursementFilters(filters));
    
    // Get current page size
    const { pageSize } = getState().funding;
    
    // Fetch disbursements with updated filters
    // Reset to page 1 when filters change, maintain current pageSize
    dispatch(fetchDisbursements({ page: 1, pageSize, filters }));
  };
};

/**
 * Action creator that updates disbursement sort options and fetches sorted results
 * 
 * @param sort - Sort options for disbursements
 * @returns Thunk action function that dispatches sort update and fetches results
 */
export const updateDisbursementSort = (sort: DisbursementSort | null) => {
  return (dispatch: ThunkDispatch<any, any, any>, getState: () => any) => {
    // Update sort in the state
    dispatch(setDisbursementSort(sort));
    
    // Get current state values
    const state = getState();
    const { disbursementPage: page, pageSize, disbursementFilters: filters } = state.funding;
    
    // Fetch disbursements with current page, pageSize, filters, and updated sort
    dispatch(fetchDisbursements({ 
      page, 
      pageSize, 
      filters, 
      sort 
    }));
  };
};

/**
 * Action creator that loads a funding request and its related data
 * 
 * @param fundingRequestId - ID of the funding request to load
 * @returns Thunk action function that dispatches multiple data fetching actions
 */
export const loadFundingRequestDetails = (fundingRequestId: string) => {
  return (dispatch: ThunkDispatch<any, any, any>) => {
    // Fetch the funding request details
    dispatch(fetchFundingRequestById(fundingRequestId));
    
    // Fetch related data
    dispatch(fetchDisbursementsByFundingRequest(fundingRequestId));
    dispatch(fetchStipulationVerifications(fundingRequestId));
    dispatch(fetchFundingNotes(fundingRequestId));
  };
};

/**
 * Action creator that approves a funding request and reloads related data
 * 
 * @param approvalData - Funding approval data
 * @returns Thunk action function that dispatches approval and reloads data
 */
export const approveFundingRequestAction = (approvalData: FundingApprovalRequest) => {
  return async (dispatch: ThunkDispatch<any, any, any>) => {
    // Approve the funding request
    await dispatch(approveFundingRequest(approvalData));
    
    // Reload funding request details
    dispatch(loadFundingRequestDetails(approvalData.funding_request_id));
    
    // Update status summary counts
    dispatch(fetchFundingStatusSummary());
  };
};

/**
 * Action creator that rejects a funding request and reloads related data
 * 
 * @param fundingRequestId - ID of the funding request to reject
 * @param comments - Comments explaining the rejection reason
 * @returns Thunk action function that dispatches rejection and reloads data
 */
export const rejectFundingRequestAction = ({ 
  fundingRequestId, 
  comments 
}: { 
  fundingRequestId: string; 
  comments: string 
}) => {
  return async (dispatch: ThunkDispatch<any, any, any>) => {
    // Reject the funding request
    await dispatch(rejectFundingRequest({ fundingRequestId, comments }));
    
    // Reload funding request details
    dispatch(loadFundingRequestDetails(fundingRequestId));
    
    // Update status summary counts
    dispatch(fetchFundingStatusSummary());
  };
};

/**
 * Action creator that creates a disbursement and reloads related data
 * 
 * @param disbursementData - Disbursement creation data
 * @returns Thunk action function that dispatches disbursement creation and reloads data
 */
export const createDisbursementAction = (disbursementData: DisbursementCreateRequest) => {
  return async (dispatch: ThunkDispatch<any, any, any>) => {
    // Create the disbursement
    await dispatch(createDisbursement(disbursementData));
    
    // Reload disbursements for the funding request
    dispatch(fetchDisbursementsByFundingRequest(disbursementData.funding_request_id));
    
    // Reload funding request details
    dispatch(loadFundingRequestDetails(disbursementData.funding_request_id));
  };
};

/**
 * Action creator that updates a disbursement status and reloads related data
 * 
 * @param disbursementId - ID of the disbursement to update
 * @param status - New status for the disbursement
 * @param referenceNumber - Optional reference number for completed disbursements
 * @returns Thunk action function that dispatches status update and reloads data
 */
export const updateDisbursementStatusAction = ({ 
  disbursementId, 
  status, 
  referenceNumber 
}: { 
  disbursementId: string; 
  status: string; 
  referenceNumber?: string 
}) => {
  return async (dispatch: ThunkDispatch<any, any, any>) => {
    // Update the disbursement status
    const response = await dispatch(updateDisbursementStatus({ 
      disbursementId, 
      status, 
      referenceNumber 
    }));
    
    // Extract funding request ID from the response
    const fundingRequestId = response.funding_request_id;
    
    // Reload disbursements for the funding request
    dispatch(fetchDisbursementsByFundingRequest(fundingRequestId));
    
    // Reload funding request details
    dispatch(loadFundingRequestDetails(fundingRequestId));
  };
};

/**
 * Action creator that submits enrollment verification and reloads related data
 * 
 * @param verificationData - Enrollment verification data
 * @returns Thunk action function that dispatches verification and reloads data
 */
export const verifyEnrollmentAction = (verificationData: EnrollmentVerificationRequest) => {
  return async (dispatch: ThunkDispatch<any, any, any>) => {
    // Submit enrollment verification
    await dispatch(verifyEnrollment(verificationData));
    
    // Reload funding request details
    dispatch(loadFundingRequestDetails(verificationData.funding_request_id));
    
    // Update status summary counts
    dispatch(fetchFundingStatusSummary());
  };
};

/**
 * Action creator that submits stipulation verification and reloads related data
 * 
 * @param verificationData - Stipulation verification data
 * @returns Thunk action function that dispatches verification and reloads data
 */
export const verifyStipulationAction = (verificationData: StipulationVerificationRequest) => {
  return async (dispatch: ThunkDispatch<any, any, any>) => {
    // Submit stipulation verification
    await dispatch(verifyStipulation(verificationData));
    
    // Reload stipulation verifications
    dispatch(fetchStipulationVerifications(verificationData.funding_request_id));
    
    // Reload funding request details
    dispatch(loadFundingRequestDetails(verificationData.funding_request_id));
  };
};

/**
 * Action creator that adds a note to a funding request and reloads notes
 * 
 * @param noteData - Note creation data
 * @returns Thunk action function that dispatches note creation and reloads notes
 */
export const addFundingNoteAction = (noteData: FundingNoteCreateRequest) => {
  return async (dispatch: ThunkDispatch<any, any, any>) => {
    // Add the funding note
    await dispatch(addFundingNote(noteData));
    
    // Reload funding notes
    dispatch(fetchFundingNotes(noteData.funding_request_id));
  };
};

/**
 * Action creator that loads all data needed for the funding dashboard
 * 
 * @param page - Page number to load
 * @param pageSize - Number of items per page
 * @returns Thunk action function that dispatches multiple data fetching actions
 */
export const loadFundingDashboard = ({ 
  page, 
  pageSize 
}: { 
  page: number; 
  pageSize: number 
}) => {
  return (dispatch: ThunkDispatch<any, any, any>, getState: () => any) => {
    // Get current state values
    const state = getState();
    const { fundingFilters: filters, fundingSort: sort } = state.funding;
    
    // Fetch funding requests
    dispatch(fetchFundingRequests({ page, pageSize, filters, sort }));
    
    // Fetch status summary
    dispatch(fetchFundingStatusSummary());
  };
};

/**
 * Action creator that loads all data needed for the disbursement dashboard
 * 
 * @param page - Page number to load
 * @param pageSize - Number of items per page
 * @returns Thunk action function that dispatches multiple data fetching actions
 */
export const loadDisbursementDashboard = ({ 
  page, 
  pageSize 
}: { 
  page: number; 
  pageSize: number 
}) => {
  return (dispatch: ThunkDispatch<any, any, any>, getState: () => any) => {
    // Get current state values
    const state = getState();
    const { disbursementFilters: filters, disbursementSort: sort } = state.funding;
    
    // Fetch disbursements
    dispatch(fetchDisbursements({ page, pageSize, filters, sort }));
  };
};

/**
 * Action creator that resets the funding state to its initial values
 * 
 * @returns Thunk action function that dispatches the reset action
 */
export const clearFundingStateAction = () => {
  return (dispatch: Dispatch) => {
    dispatch(resetFundingState());
  };
};

/**
 * Action creator that clears any funding-related error messages
 * 
 * @returns Thunk action function that dispatches the clear error action
 */
export const clearFundingErrorAction = () => {
  return (dispatch: Dispatch) => {
    dispatch(clearFundingError());
  };
};