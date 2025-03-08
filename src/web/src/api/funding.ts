/**
 * API functions for interacting with the funding-related endpoints of the loan management system.
 * Handles API requests for funding requests, disbursements, enrollment verification,
 * stipulation verification, and funding notes.
 * 
 * @version 1.0.0
 */

import { apiClient, handleApiError } from '../config/api';
import { API_ENDPOINTS } from '../config/constants';
import { 
  ApiResponse, 
  PaginatedResponse,
  FundingRequest, 
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
} from '../types';

/**
 * Fetches a paginated list of funding requests with optional filtering and sorting
 * 
 * @param {Object} params - Parameters for the request
 * @param {number} params.page - Page number to fetch
 * @param {number} params.pageSize - Number of items per page
 * @param {FundingFilters} [params.filters] - Filter criteria for funding requests
 * @param {FundingSort} [params.sort] - Sorting criteria for funding requests
 * @returns {Promise<ApiResponse<PaginatedResponse<FundingRequestListItem>>>} Paginated funding request data
 */
export const getFundingRequests = async ({ 
  page, 
  pageSize,
  filters,
  sort 
}: { 
  page: number; 
  pageSize: number; 
  filters?: FundingFilters; 
  sort?: FundingSort 
}): Promise<ApiResponse<PaginatedResponse<FundingRequestListItem>>> => {
  try {
    // Construct query parameters
    const queryParams = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString()
    });

    // Add filter parameters if provided
    if (filters) {
      if (filters.status) queryParams.append('status', filters.status);
      if (filters.application_id) queryParams.append('application_id', filters.application_id);
      if (filters.borrower_name) queryParams.append('borrower_name', filters.borrower_name);
      if (filters.school_name) queryParams.append('school_name', filters.school_name);
      
      if (filters.date_range) {
        if (filters.date_range.start) queryParams.append('date_from', filters.date_range.start);
        if (filters.date_range.end) queryParams.append('date_to', filters.date_range.end);
      }
      
      if (filters.amount_range) {
        if (filters.amount_range.min !== null) queryParams.append('amount_min', filters.amount_range.min.toString());
        if (filters.amount_range.max !== null) queryParams.append('amount_max', filters.amount_range.max.toString());
      }
    }

    // Add sort parameters if provided
    if (sort) {
      queryParams.append('sort_by', sort.field);
      queryParams.append('sort_direction', sort.direction);
    }

    const response = await apiClient.get(`${API_ENDPOINTS.FUNDING.BASE}/requests`, { params: queryParams });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches a single funding request by ID with detailed information
 * 
 * @param {string} id - Funding request ID
 * @returns {Promise<ApiResponse<FundingRequestDetail>>} Detailed funding request data
 */
export const getFundingRequest = async (id: string): Promise<ApiResponse<FundingRequestDetail>> => {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.FUNDING.BASE}/requests/${id}`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches funding requests associated with a specific loan application
 * 
 * @param {string} applicationId - Loan application ID
 * @returns {Promise<ApiResponse<FundingRequest[]>>} Array of funding requests
 */
export const getFundingRequestsByApplication = async (applicationId: string): Promise<ApiResponse<FundingRequest[]>> => {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.FUNDING.BASE}/applications/${applicationId}/requests`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Approves a funding request with specified amount and optional comments
 * 
 * @param {FundingApprovalRequest} approvalData - Approval data with funding request ID, amount, and comments
 * @returns {Promise<ApiResponse<FundingRequest>>} Updated funding request data
 */
export const approveFundingRequest = async (approvalData: FundingApprovalRequest): Promise<ApiResponse<FundingRequest>> => {
  try {
    const response = await apiClient.post(`${API_ENDPOINTS.FUNDING.BASE}/requests/${approvalData.funding_request_id}/approve`, {
      approved_amount: approvalData.approved_amount,
      comments: approvalData.comments
    });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Rejects a funding request with required comments
 * 
 * @param {Object} params - Rejection parameters
 * @param {string} params.fundingRequestId - Funding request ID
 * @param {string} params.comments - Comments explaining the rejection reason
 * @returns {Promise<ApiResponse<FundingRequest>>} Updated funding request data
 */
export const rejectFundingRequest = async ({ 
  fundingRequestId, 
  comments 
}: { 
  fundingRequestId: string; 
  comments: string 
}): Promise<ApiResponse<FundingRequest>> => {
  try {
    const response = await apiClient.post(`${API_ENDPOINTS.FUNDING.BASE}/requests/${fundingRequestId}/reject`, { comments });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches a paginated list of disbursements with optional filtering and sorting
 * 
 * @param {Object} params - Parameters for the request
 * @param {number} params.page - Page number to fetch
 * @param {number} params.pageSize - Number of items per page
 * @param {DisbursementFilters} [params.filters] - Filter criteria for disbursements
 * @param {DisbursementSort} [params.sort] - Sorting criteria for disbursements
 * @returns {Promise<ApiResponse<PaginatedResponse<DisbursementListItem>>>} Paginated disbursement data
 */
export const getDisbursements = async ({ 
  page, 
  pageSize,
  filters,
  sort 
}: { 
  page: number; 
  pageSize: number; 
  filters?: DisbursementFilters; 
  sort?: DisbursementSort 
}): Promise<ApiResponse<PaginatedResponse<DisbursementListItem>>> => {
  try {
    // Construct query parameters
    const queryParams = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString()
    });

    // Add filter parameters if provided
    if (filters) {
      if (filters.status) queryParams.append('status', filters.status);
      if (filters.funding_request_id) queryParams.append('funding_request_id', filters.funding_request_id);
      if (filters.application_id) queryParams.append('application_id', filters.application_id);
      if (filters.borrower_name) queryParams.append('borrower_name', filters.borrower_name);
      if (filters.school_name) queryParams.append('school_name', filters.school_name);
      if (filters.disbursement_method) queryParams.append('disbursement_method', filters.disbursement_method);
      
      if (filters.date_range) {
        if (filters.date_range.start) queryParams.append('date_from', filters.date_range.start);
        if (filters.date_range.end) queryParams.append('date_to', filters.date_range.end);
      }
      
      if (filters.amount_range) {
        if (filters.amount_range.min !== null) queryParams.append('amount_min', filters.amount_range.min.toString());
        if (filters.amount_range.max !== null) queryParams.append('amount_max', filters.amount_range.max.toString());
      }
    }

    // Add sort parameters if provided
    if (sort) {
      queryParams.append('sort_by', sort.field);
      queryParams.append('sort_direction', sort.direction);
    }

    const response = await apiClient.get(`${API_ENDPOINTS.FUNDING.BASE}/disbursements`, { params: queryParams });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches a single disbursement by ID
 * 
 * @param {string} id - Disbursement ID
 * @returns {Promise<ApiResponse<Disbursement>>} Disbursement data
 */
export const getDisbursement = async (id: string): Promise<ApiResponse<Disbursement>> => {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.FUNDING.BASE}/disbursements/${id}`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches disbursements associated with a specific funding request
 * 
 * @param {string} fundingRequestId - Funding request ID
 * @returns {Promise<ApiResponse<Disbursement[]>>} Array of disbursements
 */
export const getDisbursementsByFundingRequest = async (fundingRequestId: string): Promise<ApiResponse<Disbursement[]>> => {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.FUNDING.BASE}/requests/${fundingRequestId}/disbursements`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Creates a new disbursement for a funding request
 * 
 * @param {DisbursementCreateRequest} disbursementData - Disbursement creation data
 * @returns {Promise<ApiResponse<Disbursement>>} Created disbursement data
 */
export const createDisbursement = async (disbursementData: DisbursementCreateRequest): Promise<ApiResponse<Disbursement>> => {
  try {
    const response = await apiClient.post(`${API_ENDPOINTS.FUNDING.BASE}/disbursements`, disbursementData);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Updates the status of a disbursement with optional reference number
 * 
 * @param {Object} params - Update parameters
 * @param {string} params.disbursementId - Disbursement ID
 * @param {string} params.status - New disbursement status
 * @param {string} [params.referenceNumber] - Optional reference number for completed disbursements
 * @returns {Promise<ApiResponse<Disbursement>>} Updated disbursement data
 */
export const updateDisbursementStatus = async ({ 
  disbursementId, 
  status, 
  referenceNumber 
}: { 
  disbursementId: string; 
  status: string; 
  referenceNumber?: string 
}): Promise<ApiResponse<Disbursement>> => {
  try {
    const data: { status: string; reference_number?: string } = { status };
    if (referenceNumber) {
      data.reference_number = referenceNumber;
    }
    
    const response = await apiClient.patch(`${API_ENDPOINTS.FUNDING.BASE}/disbursements/${disbursementId}/status`, data);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Submits enrollment verification for a funding request
 * 
 * @param {EnrollmentVerificationRequest} verificationData - Enrollment verification data
 * @returns {Promise<ApiResponse<EnrollmentVerification>>} Enrollment verification data
 */
export const verifyEnrollment = async (verificationData: EnrollmentVerificationRequest): Promise<ApiResponse<EnrollmentVerification>> => {
  try {
    const response = await apiClient.post(`${API_ENDPOINTS.FUNDING.BASE}/enrollment-verification`, verificationData);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches enrollment verification for a specific funding request
 * 
 * @param {string} fundingRequestId - Funding request ID
 * @returns {Promise<ApiResponse<EnrollmentVerification>>} Enrollment verification data
 */
export const getEnrollmentVerification = async (fundingRequestId: string): Promise<ApiResponse<EnrollmentVerification>> => {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.FUNDING.BASE}/requests/${fundingRequestId}/enrollment-verification`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Submits verification for a stipulation requirement
 * 
 * @param {StipulationVerificationRequest} verificationData - Stipulation verification data
 * @returns {Promise<ApiResponse<StipulationVerification>>} Stipulation verification data
 */
export const verifyStipulation = async (verificationData: StipulationVerificationRequest): Promise<ApiResponse<StipulationVerification>> => {
  try {
    const response = await apiClient.post(`${API_ENDPOINTS.FUNDING.BASE}/stipulations/verify`, verificationData);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches stipulation verifications for a specific funding request
 * 
 * @param {string} fundingRequestId - Funding request ID
 * @returns {Promise<ApiResponse<StipulationVerification[]>>} Array of stipulation verifications
 */
export const getStipulationVerifications = async (fundingRequestId: string): Promise<ApiResponse<StipulationVerification[]>> => {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.FUNDING.BASE}/requests/${fundingRequestId}/stipulations`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Adds a note to a funding request
 * 
 * @param {FundingNoteCreateRequest} noteData - Note creation data
 * @returns {Promise<ApiResponse<FundingNote>>} Created note data
 */
export const addFundingNote = async (noteData: FundingNoteCreateRequest): Promise<ApiResponse<FundingNote>> => {
  try {
    const response = await apiClient.post(`${API_ENDPOINTS.FUNDING.BASE}/notes`, noteData);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches notes for a specific funding request
 * 
 * @param {string} fundingRequestId - Funding request ID
 * @returns {Promise<ApiResponse<FundingNote[]>>} Array of funding notes
 */
export const getFundingNotes = async (fundingRequestId: string): Promise<ApiResponse<FundingNote[]>> => {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.FUNDING.BASE}/requests/${fundingRequestId}/notes`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches a summary of funding request statuses
 * 
 * @returns {Promise<ApiResponse<FundingStatusSummary>>} Funding status summary data
 */
export const getFundingStatusSummary = async (): Promise<ApiResponse<FundingStatusSummary>> => {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.FUNDING.BASE}/status-summary`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};