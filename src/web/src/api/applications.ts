/**
 * API client for loan application operations in the loan management system.
 * Provides functions for creating, retrieving, updating, and managing loan applications
 * and their related resources.
 */
import { AxiosRequestConfig } from 'axios'; // ^1.4.0
import { apiClient, handleApiError, API_BASE_URL } from '../config/api';
import { API_ENDPOINTS } from '../config/constants';
import {
  LoanApplication,
  ApplicationDetail,
  ApplicationListItem,
  ApplicationFormData,
  ApplicationFilters,
  ApplicationSort,
  ApplicationDocument,
  ApplicationStatusHistory,
  ApplicationListResponse,
  ApplicationCreateRequest,
  ApplicationUpdateRequest,
  ApplicationSubmitRequest,
  ApplicationDocumentUploadRequest,
  ApplicationStatusUpdateRequest,
  ApplicationRequiredAction,
  ApplicationTimelineEvent,
  ApplicationCountsByStatus
} from '../types/application.types';
import {
  ApiResponse,
  PaginatedResponse,
  UUID
} from '../types/common.types';

/**
 * Fetches a paginated list of loan applications with optional filtering and sorting
 * 
 * @param options - Pagination, filter, and sorting options
 * @returns Promise resolving to paginated application list response
 */
export const getApplications = async (
  options: { 
    page?: number; 
    page_size?: number; 
    filters?: ApplicationFilters; 
    sort?: ApplicationSort 
  } = {}
): Promise<ApiResponse<ApplicationListResponse>> => {
  try {
    const { page = 1, page_size = 10, filters = {}, sort } = options;
    
    // Construct query parameters
    const params: Record<string, any> = {
      page,
      page_size
    };
    
    // Add filter parameters if provided
    if (filters.status) params.status = filters.status;
    if (filters.school_id) params.school_id = filters.school_id;
    if (filters.program_id) params.program_id = filters.program_id;
    if (filters.borrower_name) params.borrower_name = filters.borrower_name;
    if (filters.has_co_borrower !== null && filters.has_co_borrower !== undefined) {
      params.has_co_borrower = filters.has_co_borrower;
    }
    if (filters.date_range?.start) params.date_from = filters.date_range.start;
    if (filters.date_range?.end) params.date_to = filters.date_range.end;
    
    // Add sort parameters if provided
    if (sort) {
      params.sort_by = sort.field;
      params.sort_direction = sort.direction;
    }
    
    const response = await apiClient.get(API_ENDPOINTS.APPLICATIONS.BASE, { params });
    
    return {
      success: true,
      message: null,
      data: response.data,
      errors: null
    };
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches a single loan application by ID with all related details
 * 
 * @param id - Application UUID
 * @returns Promise resolving to application detail response
 */
export const getApplication = async (id: UUID): Promise<ApiResponse<ApplicationDetail>> => {
  try {
    const response = await apiClient.get(API_ENDPOINTS.APPLICATIONS.BY_ID(id));
    
    return {
      success: true,
      message: null,
      data: response.data,
      errors: null
    };
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Creates a new loan application
 * 
 * @param data - Application creation request data
 * @returns Promise resolving to created application data
 */
export const createApplication = async (
  data: ApplicationCreateRequest
): Promise<ApiResponse<LoanApplication>> => {
  try {
    const response = await apiClient.post(API_ENDPOINTS.APPLICATIONS.BASE, data);
    
    return {
      success: true,
      message: 'Application created successfully',
      data: response.data,
      errors: null
    };
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Updates an existing loan application
 * 
 * @param id - Application UUID
 * @param data - Application update request data
 * @returns Promise resolving to updated application data
 */
export const updateApplication = async (
  id: UUID,
  data: ApplicationUpdateRequest
): Promise<ApiResponse<LoanApplication>> => {
  try {
    const response = await apiClient.put(API_ENDPOINTS.APPLICATIONS.BY_ID(id), data);
    
    return {
      success: true,
      message: 'Application updated successfully',
      data: response.data,
      errors: null
    };
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Submits an application for review, changing its status from draft to submitted
 * 
 * @param id - Application UUID
 * @returns Promise resolving to submitted application data
 */
export const submitApplication = async (id: UUID): Promise<ApiResponse<LoanApplication>> => {
  try {
    const response = await apiClient.post(API_ENDPOINTS.APPLICATIONS.SUBMIT(id));
    
    return {
      success: true,
      message: 'Application submitted successfully',
      data: response.data,
      errors: null
    };
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Saves a draft of an application without submitting it for review
 * 
 * @param id - Application UUID
 * @param data - Application form data
 * @returns Promise resolving to saved draft application data
 */
export const saveApplicationDraft = async (
  id: UUID,
  data: ApplicationFormData
): Promise<ApiResponse<LoanApplication>> => {
  try {
    const response = await apiClient.put(`${API_ENDPOINTS.APPLICATIONS.BY_ID(id)}/draft`, data);
    
    return {
      success: true,
      message: 'Draft saved successfully',
      data: response.data,
      errors: null
    };
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Uploads a document for an application
 * 
 * @param data - Document upload request data
 * @returns Promise resolving to uploaded document data
 */
export const uploadApplicationDocument = async (
  data: ApplicationDocumentUploadRequest
): Promise<ApiResponse<ApplicationDocument>> => {
  try {
    const formData = new FormData();
    formData.append('file', data.file);
    formData.append('document_type', data.document_type);
    
    const config: AxiosRequestConfig = {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    };
    
    const response = await apiClient.post(
      API_ENDPOINTS.APPLICATIONS.DOCUMENTS(data.application_id),
      formData,
      config
    );
    
    return {
      success: true,
      message: 'Document uploaded successfully',
      data: response.data,
      errors: null
    };
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Deletes a document from an application
 * 
 * @param applicationId - Application UUID
 * @param documentId - Document UUID
 * @returns Promise resolving when document is deleted
 */
export const deleteApplicationDocument = async (
  applicationId: UUID,
  documentId: UUID
): Promise<ApiResponse<void>> => {
  try {
    await apiClient.delete(`${API_ENDPOINTS.APPLICATIONS.DOCUMENTS(applicationId)}/${documentId}`);
    
    return {
      success: true,
      message: 'Document deleted successfully',
      data: null,
      errors: null
    };
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches all documents for an application
 * 
 * @param id - Application UUID
 * @returns Promise resolving to array of application documents
 */
export const getApplicationDocuments = async (
  id: UUID
): Promise<ApiResponse<ApplicationDocument[]>> => {
  try {
    const response = await apiClient.get(API_ENDPOINTS.APPLICATIONS.DOCUMENTS(id));
    
    return {
      success: true,
      message: null,
      data: response.data,
      errors: null
    };
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches the status history for an application
 * 
 * @param id - Application UUID
 * @returns Promise resolving to array of status history entries
 */
export const getApplicationStatusHistory = async (
  id: UUID
): Promise<ApiResponse<ApplicationStatusHistory[]>> => {
  try {
    const response = await apiClient.get(API_ENDPOINTS.APPLICATIONS.STATUS_HISTORY(id));
    
    return {
      success: true,
      message: null,
      data: response.data,
      errors: null
    };
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Cancels an application, changing its status to abandoned
 * 
 * @param id - Application UUID
 * @returns Promise resolving when application is cancelled
 */
export const cancelApplication = async (id: UUID): Promise<ApiResponse<void>> => {
  try {
    await apiClient.post(`${API_ENDPOINTS.APPLICATIONS.BY_ID(id)}/cancel`);
    
    return {
      success: true,
      message: 'Application cancelled successfully',
      data: null,
      errors: null
    };
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches a paginated list of applications for a specific school
 * 
 * @param schoolId - School UUID
 * @param options - Pagination, filter, and sorting options
 * @returns Promise resolving to paginated application list response
 */
export const getApplicationsBySchool = async (
  schoolId: UUID,
  options: { 
    page?: number; 
    page_size?: number; 
    filters?: ApplicationFilters; 
    sort?: ApplicationSort 
  } = {}
): Promise<ApiResponse<ApplicationListResponse>> => {
  try {
    const { page = 1, page_size = 10, filters = {}, sort } = options;
    
    // Construct query parameters
    const params: Record<string, any> = {
      page,
      page_size
    };
    
    // Add filter parameters if provided
    if (filters.status) params.status = filters.status;
    if (filters.program_id) params.program_id = filters.program_id;
    if (filters.borrower_name) params.borrower_name = filters.borrower_name;
    if (filters.has_co_borrower !== null && filters.has_co_borrower !== undefined) {
      params.has_co_borrower = filters.has_co_borrower;
    }
    if (filters.date_range?.start) params.date_from = filters.date_range.start;
    if (filters.date_range?.end) params.date_to = filters.date_range.end;
    
    // Add sort parameters if provided
    if (sort) {
      params.sort_by = sort.field;
      params.sort_direction = sort.direction;
    }
    
    const response = await apiClient.get(`/schools/${schoolId}/applications`, { params });
    
    return {
      success: true,
      message: null,
      data: response.data,
      errors: null
    };
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches a paginated list of applications for the current borrower
 * 
 * @param options - Pagination, filter, and sorting options
 * @returns Promise resolving to paginated application list response
 */
export const getApplicationsByBorrower = async (
  options: { 
    page?: number; 
    page_size?: number; 
    filters?: ApplicationFilters; 
    sort?: ApplicationSort 
  } = {}
): Promise<ApiResponse<ApplicationListResponse>> => {
  try {
    const { page = 1, page_size = 10, filters = {}, sort } = options;
    
    // Construct query parameters
    const params: Record<string, any> = {
      page,
      page_size
    };
    
    // Add filter parameters if provided
    if (filters.status) params.status = filters.status;
    if (filters.school_id) params.school_id = filters.school_id;
    if (filters.program_id) params.program_id = filters.program_id;
    if (filters.date_range?.start) params.date_from = filters.date_range.start;
    if (filters.date_range?.end) params.date_to = filters.date_range.end;
    
    // Add sort parameters if provided
    if (sort) {
      params.sort_by = sort.field;
      params.sort_direction = sort.direction;
    }
    
    const response = await apiClient.get(`${API_ENDPOINTS.APPLICATIONS.BASE}/my-applications`, { params });
    
    return {
      success: true,
      message: null,
      data: response.data,
      errors: null
    };
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Updates the status of an application
 * 
 * @param data - Status update request data
 * @returns Promise resolving to updated application data
 */
export const updateApplicationStatus = async (
  data: ApplicationStatusUpdateRequest
): Promise<ApiResponse<LoanApplication>> => {
  try {
    const response = await apiClient.put(
      `${API_ENDPOINTS.APPLICATIONS.BY_ID(data.application_id)}/status`,
      {
        status: data.status,
        comments: data.comments
      }
    );
    
    return {
      success: true,
      message: 'Application status updated successfully',
      data: response.data,
      errors: null
    };
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches counts of applications grouped by status
 * 
 * @param options - Optional filter by school ID
 * @returns Promise resolving to application counts by status
 */
export const getApplicationCountsByStatus = async (
  options: { schoolId?: UUID } = {}
): Promise<ApiResponse<ApplicationCountsByStatus>> => {
  try {
    const params: Record<string, any> = {};
    
    if (options.schoolId) {
      params.school_id = options.schoolId;
    }
    
    const response = await apiClient.get(`${API_ENDPOINTS.APPLICATIONS.BASE}/counts-by-status`, { params });
    
    return {
      success: true,
      message: null,
      data: response.data,
      errors: null
    };
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches required actions for an application
 * 
 * @param id - Application UUID
 * @returns Promise resolving to array of required actions
 */
export const getApplicationRequiredActions = async (
  id: UUID
): Promise<ApiResponse<ApplicationRequiredAction[]>> => {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.APPLICATIONS.BY_ID(id)}/required-actions`);
    
    return {
      success: true,
      message: null,
      data: response.data,
      errors: null
    };
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches timeline events for an application
 * 
 * @param id - Application UUID
 * @returns Promise resolving to array of timeline events
 */
export const getApplicationTimeline = async (
  id: UUID
): Promise<ApiResponse<ApplicationTimelineEvent[]>> => {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.APPLICATIONS.BY_ID(id)}/timeline`);
    
    return {
      success: true,
      message: null,
      data: response.data,
      errors: null
    };
  } catch (error) {
    return handleApiError(error);
  }
};