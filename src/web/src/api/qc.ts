import { AxiosRequestConfig } from 'axios'; // ^1.4.0
import { apiClient, handleApiError } from '../config/api';
import { API_ENDPOINTS } from '../config/constants';
import {
  QCReview,
  QCReviewListItem,
  QCReviewFilters,
  QCReviewSort,
  QCReviewListResponse,
  DocumentVerificationRequest,
  StipulationVerificationRequest,
  ChecklistItemVerificationRequest,
  QCReviewDecisionRequest,
  QCReviewAssignmentRequest,
  QCCountsByStatus
} from '../types/qc.types';
import { ApiResponse, UUID } from '../types/common.types';

/**
 * Fetches a paginated list of QC reviews with optional filtering and sorting
 * 
 * @param options - Pagination, filtering, and sorting options
 * @returns Promise resolving to paginated QC review list response
 */
export async function getQCReviews({
  page = 1,
  page_size = 10,
  filters,
  sort
}: {
  page?: number;
  page_size?: number;
  filters?: QCReviewFilters;
  sort?: QCReviewSort;
} = {}): Promise<ApiResponse<QCReviewListResponse>> {
  try {
    // Construct query parameters
    const params: Record<string, any> = { page, page_size };
    
    // Add filters if provided
    if (filters) {
      if (filters.status) params.status = filters.status;
      if (filters.priority) params.priority = filters.priority;
      if (filters.assigned_to) params.assigned_to = filters.assigned_to;
      if (filters.application_id) params.application_id = filters.application_id;
      if (filters.borrower_name) params.borrower_name = filters.borrower_name;
      if (filters.school_id) params.school_id = filters.school_id;
      if (filters.date_range) {
        if (filters.date_range.start) params.date_start = filters.date_range.start;
        if (filters.date_range.end) params.date_end = filters.date_range.end;
      }
    }
    
    // Add sort if provided
    if (sort) {
      params.sort_by = sort.field;
      params.sort_direction = sort.direction;
    }
    
    const config: AxiosRequestConfig = { params };
    const response = await apiClient.get(`${API_ENDPOINTS.QC.BASE}`, config);
    
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Fetches a single QC review by ID with all related details
 * 
 * @param id - QC review ID
 * @returns Promise resolving to QC review detail response
 */
export async function getQCReview(id: UUID): Promise<ApiResponse<QCReview>> {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.QC.BASE}/${id}`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Fetches a QC review for a specific application
 * 
 * @param applicationId - Application ID
 * @returns Promise resolving to QC review detail response
 */
export async function getQCReviewByApplication(applicationId: UUID): Promise<ApiResponse<QCReview>> {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.QC.REVIEW(applicationId)}`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Assigns a QC review to a specific reviewer
 * 
 * @param data - Assignment request data
 * @returns Promise resolving to updated QC review data
 */
export async function assignQCReview(data: QCReviewAssignmentRequest): Promise<ApiResponse<QCReview>> {
  try {
    const response = await apiClient.post(`${API_ENDPOINTS.QC.BASE}/assign`, data);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Starts the QC review process, changing its status from pending to in_review
 * 
 * @param id - QC review ID
 * @returns Promise resolving to updated QC review data
 */
export async function startQCReview(id: UUID): Promise<ApiResponse<QCReview>> {
  try {
    const response = await apiClient.post(`${API_ENDPOINTS.QC.BASE}/${id}/start`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Submits a decision for a QC review (approve or return)
 * 
 * @param data - QC review decision data
 * @returns Promise resolving to updated QC review data
 */
export async function submitQCDecision(data: QCReviewDecisionRequest): Promise<ApiResponse<QCReview>> {
  try {
    // Use the appropriate endpoint based on the decision
    const endpoint = data.status === 'approved' 
      ? API_ENDPOINTS.QC.APPROVE(data.qc_review_id)
      : API_ENDPOINTS.QC.REJECT(data.qc_review_id);
    
    const response = await apiClient.post(endpoint, data);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Updates the verification status of a document in a QC review
 * 
 * @param data - Document verification request data
 * @returns Promise resolving to updated QC review data
 */
export async function updateDocumentVerification(data: DocumentVerificationRequest): Promise<ApiResponse<QCReview>> {
  try {
    const response = await apiClient.put(`${API_ENDPOINTS.QC.VERIFICATIONS}/document`, data);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Updates the verification status of a stipulation in a QC review
 * 
 * @param data - Stipulation verification request data
 * @returns Promise resolving to updated QC review data
 */
export async function updateStipulationVerification(data: StipulationVerificationRequest): Promise<ApiResponse<QCReview>> {
  try {
    const response = await apiClient.put(`${API_ENDPOINTS.QC.VERIFICATIONS}/stipulation`, data);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Updates the verification status of a checklist item in a QC review
 * 
 * @param data - Checklist item verification request data
 * @returns Promise resolving to updated QC review data
 */
export async function updateChecklistItemVerification(data: ChecklistItemVerificationRequest): Promise<ApiResponse<QCReview>> {
  try {
    const response = await apiClient.put(`${API_ENDPOINTS.QC.VERIFICATIONS}/checklist-item`, data);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Fetches counts of QC reviews grouped by status
 * 
 * @returns Promise resolving to QC counts by status
 */
export async function getQCCountsByStatus(): Promise<ApiResponse<QCCountsByStatus>> {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.QC.BASE}/counts-by-status`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Fetches QC reviews assigned to the current user
 * 
 * @param options - Pagination, filtering, and sorting options
 * @returns Promise resolving to paginated QC review list response
 */
export async function getMyAssignedQCReviews({
  page = 1,
  page_size = 10,
  filters,
  sort
}: {
  page?: number;
  page_size?: number;
  filters?: QCReviewFilters;
  sort?: QCReviewSort;
} = {}): Promise<ApiResponse<QCReviewListResponse>> {
  try {
    // Construct query parameters
    const params: Record<string, any> = { page, page_size };
    
    // Add filters if provided
    if (filters) {
      if (filters.status) params.status = filters.status;
      if (filters.priority) params.priority = filters.priority;
      if (filters.application_id) params.application_id = filters.application_id;
      if (filters.borrower_name) params.borrower_name = filters.borrower_name;
      if (filters.school_id) params.school_id = filters.school_id;
      if (filters.date_range) {
        if (filters.date_range.start) params.date_start = filters.date_range.start;
        if (filters.date_range.end) params.date_end = filters.date_range.end;
      }
    }
    
    // Add sort if provided
    if (sort) {
      params.sort_by = sort.field;
      params.sort_direction = sort.direction;
    }
    
    const config: AxiosRequestConfig = { params };
    const response = await apiClient.get(`${API_ENDPOINTS.QC.BASE}/my-assigned`, config);
    
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Adds a note to a QC review
 * 
 * @param id - QC review ID
 * @param note - Note text
 * @returns Promise resolving to updated QC review data
 */
export async function addQCReviewNote(id: UUID, note: string): Promise<ApiResponse<QCReview>> {
  try {
    const response = await apiClient.post(`${API_ENDPOINTS.QC.BASE}/${id}/notes`, { note });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}