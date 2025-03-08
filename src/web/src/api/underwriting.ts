import { AxiosRequestConfig } from 'axios'; // ^1.4.0

import { apiClient, handleApiError, API_BASE_URL } from '../config/api';
import { API_ENDPOINTS } from '../config/constants';
import {
  UnderwritingQueue,
  UnderwritingQueueItem,
  UnderwritingApplicationDetail,
  UnderwritingDecisionRequest,
  UnderwritingDecisionData,
  UnderwritingQueueFilters,
  UnderwritingQueueSort,
  UnderwritingQueueResponse,
  UnderwritingQueueAssignRequest,
  UnderwritingNoteCreateRequest,
  StipulationUpdateRequest,
  UnderwritingMetrics,
  CreditInformation,
  Stipulation,
  UnderwritingNote
} from '../types/underwriting.types';
import { ApiResponse, PaginatedResponse, UUID } from '../types/common.types';

/**
 * Fetches a paginated list of applications in the underwriting queue with optional filtering and sorting
 * 
 * @param options - Pagination, filter, and sort options
 * @returns Promise resolving to paginated underwriting queue response
 */
export async function getUnderwritingQueue({
  page = 1,
  page_size = 10,
  filters = {},
  sort = {}
}: {
  page?: number;
  page_size?: number;
  filters?: UnderwritingQueueFilters;
  sort?: UnderwritingQueueSort;
}): Promise<ApiResponse<UnderwritingQueueResponse>> {
  try {
    // Construct query parameters
    const params: Record<string, any> = {
      page,
      page_size,
      ...filters,
    };

    // Add sort parameters if provided
    if (sort && sort.field) {
      params.sort_by = sort.field;
      params.sort_direction = sort.direction;
    }

    const response = await apiClient.get(`${API_ENDPOINTS.UNDERWRITING.QUEUE}`, { params });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Fetches comprehensive application data for underwriting review
 * 
 * @param applicationId - ID of the application to review
 * @returns Promise resolving to application detail for underwriting
 */
export async function getApplicationForUnderwriting(
  applicationId: UUID
): Promise<ApiResponse<UnderwritingApplicationDetail>> {
  try {
    const response = await apiClient.get(
      `${API_ENDPOINTS.UNDERWRITING.REVIEW(applicationId)}`
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Evaluates an application against underwriting criteria
 * 
 * @param applicationId - ID of the application to evaluate
 * @returns Promise resolving to evaluation results
 */
export async function evaluateApplication(
  applicationId: UUID
): Promise<ApiResponse<any>> {
  try {
    const response = await apiClient.get(
      `${API_ENDPOINTS.UNDERWRITING.REVIEW(applicationId)}/evaluate`
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Fetches the underwriting decision for an application
 * 
 * @param applicationId - ID of the application
 * @returns Promise resolving to underwriting decision data
 */
export async function getUnderwritingDecision(
  applicationId: UUID
): Promise<ApiResponse<UnderwritingDecisionData>> {
  try {
    const response = await apiClient.get(
      `${API_ENDPOINTS.UNDERWRITING.DECISION(applicationId)}`
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Creates an underwriting decision for an application
 * 
 * @param data - Underwriting decision data
 * @returns Promise resolving to created decision data
 */
export async function createUnderwritingDecision(
  data: UnderwritingDecisionRequest
): Promise<ApiResponse<UnderwritingDecisionData>> {
  try {
    const response = await apiClient.post(
      `${API_ENDPOINTS.UNDERWRITING.DECISION(data.application_id)}`,
      data
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Assigns an application in the underwriting queue to an underwriter
 * 
 * @param data - Assignment request data
 * @returns Promise resolving to updated queue item
 */
export async function assignApplication(
  data: UnderwritingQueueAssignRequest
): Promise<ApiResponse<UnderwritingQueue>> {
  try {
    const response = await apiClient.post(
      `${API_ENDPOINTS.UNDERWRITING.QUEUE}/${data.queue_id}/assign`,
      { underwriter_id: data.underwriter_id }
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Marks an application as in review by the underwriter
 * 
 * @param queueId - ID of the queue item
 * @returns Promise resolving to updated queue item
 */
export async function startApplicationReview(
  queueId: UUID
): Promise<ApiResponse<UnderwritingQueue>> {
  try {
    const response = await apiClient.post(
      `${API_ENDPOINTS.UNDERWRITING.QUEUE}/${queueId}/start-review`
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Fetches applications that are past their due date
 * 
 * @returns Promise resolving to array of overdue queue items
 */
export async function getOverdueApplications(): Promise<ApiResponse<UnderwritingQueueItem[]>> {
  try {
    const response = await apiClient.get(
      `${API_ENDPOINTS.UNDERWRITING.QUEUE}/overdue`
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Fetches credit information for a borrower or co-borrower on an application
 * 
 * @param applicationId - ID of the application
 * @param isCoApplicant - Whether to get credit info for co-borrower
 * @returns Promise resolving to credit information data
 */
export async function getCreditInformation(
  applicationId: UUID,
  isCoApplicant: boolean = false
): Promise<ApiResponse<CreditInformation>> {
  try {
    const params = { is_co_borrower: isCoApplicant };
    const response = await apiClient.get(
      `${API_ENDPOINTS.UNDERWRITING.REVIEW(applicationId)}/credit`,
      { params }
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Uploads credit information for a borrower or co-borrower
 * 
 * @param applicationId - ID of the application
 * @param data - Credit information data and file
 * @returns Promise resolving to uploaded credit information
 */
export async function uploadCreditInformation(
  applicationId: UUID,
  data: {
    credit_score: number;
    monthly_debt: number;
    report_file: File;
    is_co_borrower: boolean;
  }
): Promise<ApiResponse<CreditInformation>> {
  try {
    const formData = new FormData();
    formData.append('credit_score', data.credit_score.toString());
    formData.append('monthly_debt', data.monthly_debt.toString());
    formData.append('report_file', data.report_file);
    formData.append('is_co_borrower', data.is_co_borrower.toString());

    const config: AxiosRequestConfig = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    };

    const response = await apiClient.post(
      `${API_ENDPOINTS.UNDERWRITING.REVIEW(applicationId)}/credit`,
      formData,
      config
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Fetches stipulations for an application
 * 
 * @param applicationId - ID of the application
 * @param options - Optional filter options
 * @returns Promise resolving to array of stipulations
 */
export async function getStipulations(
  applicationId: UUID,
  options: { status?: string } = {}
): Promise<ApiResponse<Stipulation[]>> {
  try {
    const params = {
      application_id: applicationId,
      ...options,
    };

    const response = await apiClient.get(
      `${API_ENDPOINTS.UNDERWRITING.STIPULATIONS}`,
      { params }
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Updates a stipulation's status (typically to mark as satisfied)
 * 
 * @param data - Stipulation update request data
 * @returns Promise resolving to updated stipulation
 */
export async function updateStipulation(
  data: StipulationUpdateRequest
): Promise<ApiResponse<Stipulation>> {
  try {
    const response = await apiClient.put(
      `${API_ENDPOINTS.UNDERWRITING.STIPULATIONS}/${data.stipulation_id}`,
      {
        status: data.status,
        comments: data.comments,
      }
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Fetches notes for an application in the underwriting process
 * 
 * @param applicationId - ID of the application
 * @returns Promise resolving to array of underwriting notes
 */
export async function getUnderwritingNotes(
  applicationId: UUID
): Promise<ApiResponse<UnderwritingNote[]>> {
  try {
    const params = { application_id: applicationId };
    const response = await apiClient.get(
      `${API_ENDPOINTS.UNDERWRITING.NOTES}`,
      { params }
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Creates a new note for an application in the underwriting process
 * 
 * @param data - Note creation request data
 * @returns Promise resolving to created note
 */
export async function createUnderwritingNote(
  data: UnderwritingNoteCreateRequest
): Promise<ApiResponse<UnderwritingNote>> {
  try {
    const response = await apiClient.post(
      `${API_ENDPOINTS.UNDERWRITING.NOTES}`,
      data
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Fetches metrics and statistics about the underwriting process
 * 
 * @param options - Optional date range filter
 * @returns Promise resolving to underwriting metrics
 */
export async function getUnderwritingMetrics(
  options: { start_date?: string; end_date?: string } = {}
): Promise<ApiResponse<UnderwritingMetrics>> {
  try {
    const response = await apiClient.get(
      `${API_ENDPOINTS.UNDERWRITING.BASE}/statistics`,
      { params: options }
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Fetches workload statistics for an underwriter
 * 
 * @param underwriterId - ID of the underwriter
 * @returns Promise resolving to workload statistics
 */
export async function getUnderwriterWorkload(
  underwriterId: UUID
): Promise<ApiResponse<any>> {
  try {
    const response = await apiClient.get(
      `${API_ENDPOINTS.UNDERWRITING.BASE}/workload/${underwriterId}`
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}