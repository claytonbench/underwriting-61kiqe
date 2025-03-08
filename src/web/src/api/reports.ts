/**
 * Reports API module for the loan management system.
 * Provides functions for interacting with the report-related API endpoints.
 *
 * @version 1.0.0
 */

import axios, { AxiosRequestConfig } from 'axios'; // ^1.4.0
import { apiClient, handleApiError, API_BASE_URL } from '../config/api';
import { API_ENDPOINTS } from '../config/constants';
import { ApiResponse, PaginatedResponse, UUID, DateRange, SortParams } from '../types/common.types';

/**
 * Enum representing report types available in the system
 */
export enum ReportType {
  APPLICATION_VOLUME = 'application_volume',
  APPROVAL_RATES = 'approval_rates',
  DOCUMENT_STATUS = 'document_status',
  FUNDING_METRICS = 'funding_metrics',
  UNDERWRITING_METRICS = 'underwriting_metrics',
  PROCESSING_TIMES = 'processing_times',
  SCHOOL_PERFORMANCE = 'school_performance',
  USER_ACTIVITY = 'user_activity'
}

/**
 * Enum representing report export formats
 */
export enum ReportExportFormat {
  CSV = 'csv',
  EXCEL = 'excel',
  PDF = 'pdf',
  JSON = 'json'
}

/**
 * Enum representing report frequency for scheduled reports
 */
export enum ReportScheduleFrequency {
  DAILY = 'daily',
  WEEKLY = 'weekly',
  MONTHLY = 'monthly',
  QUARTERLY = 'quarterly'
}

/**
 * Interface representing a report configuration
 */
export interface ReportConfiguration {
  id: UUID;
  name: string;
  description: string;
  report_type: ReportType;
  parameters: Record<string, any>;
  created_by: UUID;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  is_system: boolean;
}

/**
 * Interface representing a saved/generated report
 */
export interface SavedReport {
  id: UUID;
  configuration_id: UUID;
  configuration_name: string;
  report_type: ReportType;
  parameters: Record<string, any>;
  result_data: Record<string, any>;
  generated_at: string;
  generated_by: UUID;
  file_size: number;
  expiration_date: string | null;
  download_url: string | null;
}

/**
 * Interface representing a report schedule
 */
export interface ReportSchedule {
  id: UUID;
  configuration_id: UUID;
  configuration_name: string;
  report_type: ReportType;
  frequency: ReportScheduleFrequency;
  day_of_week: number | null;
  day_of_month: number | null;
  time_of_day: string;
  recipients: string[];
  parameters: Record<string, any>;
  export_format: ReportExportFormat;
  is_active: boolean;
  last_executed_at: string | null;
  next_execution_at: string;
  created_by: UUID;
  created_at: string;
  updated_at: string;
}

/**
 * Interface representing a report permission
 */
export interface ReportPermission {
  id: UUID;
  configuration_id: UUID;
  user_id: UUID;
  user_name: string;
  user_email: string;
  can_view: boolean;
  can_edit: boolean;
  can_delete: boolean;
  can_share: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Interface for creating a new report configuration
 */
export interface ReportConfigurationCreateRequest {
  name: string;
  description: string;
  report_type: ReportType;
  parameters: Record<string, any>;
  is_active: boolean;
}

/**
 * Interface for updating an existing report configuration
 */
export interface ReportConfigurationUpdateRequest {
  name?: string;
  description?: string;
  parameters?: Record<string, any>;
  is_active?: boolean;
}

/**
 * Interface for generating a report
 */
export interface ReportGenerateRequest {
  configuration_id?: UUID;
  report_type: ReportType;
  parameters: Record<string, any>;
  async?: boolean;
}

/**
 * Interface for exporting a report
 */
export interface ReportExportRequest {
  format: ReportExportFormat;
  include_filters?: boolean;
}

/**
 * Interface for export response with download URL
 */
export interface ReportExportResponse {
  download_url: string;
  file_name: string;
  file_size: number;
  expiration_time: string;
}

/**
 * Interface for creating a report schedule
 */
export interface ReportScheduleCreateRequest {
  configuration_id: UUID;
  frequency: ReportScheduleFrequency;
  day_of_week?: number;
  day_of_month?: number;
  time_of_day: string;
  recipients: string[];
  parameters?: Record<string, any>;
  export_format: ReportExportFormat;
  is_active: boolean;
}

/**
 * Interface for updating a report schedule
 */
export interface ReportScheduleUpdateRequest {
  frequency?: ReportScheduleFrequency;
  day_of_week?: number;
  day_of_month?: number;
  time_of_day?: string;
  recipients?: string[];
  parameters?: Record<string, any>;
  export_format?: ReportExportFormat;
  is_active?: boolean;
}

/**
 * Interface for setting report permissions
 */
export interface ReportPermissionRequest {
  user_id: UUID;
  can_view: boolean;
  can_edit: boolean;
  can_delete: boolean;
  can_share: boolean;
}

/**
 * Parameters for application volume reports
 */
export interface ApplicationVolumeReportParams {
  date_range: DateRange;
  school_id?: UUID;
  program_id?: UUID;
  group_by?: 'day' | 'week' | 'month';
  include_trend?: boolean;
  statuses?: string[];
}

/**
 * Parameters for document status reports
 */
export interface DocumentStatusReportParams {
  date_range: DateRange;
  school_id?: UUID;
  document_types?: string[];
  group_by?: 'document_type' | 'status' | 'school';
}

/**
 * Parameters for funding metrics reports
 */
export interface FundingMetricsReportParams {
  date_range: DateRange;
  school_id?: UUID;
  program_id?: UUID;
  group_by?: 'day' | 'week' | 'month' | 'school' | 'program';
  include_trends?: boolean;
}

/**
 * Parameters for underwriting metrics reports
 */
export interface UnderwritingMetricsReportParams {
  date_range: DateRange;
  school_id?: UUID;
  underwriter_id?: UUID;
  include_decision_reasons?: boolean;
  include_processing_times?: boolean;
}

/**
 * Fetches a list of report configurations with optional filtering
 *
 * @param params - Query parameters for filtering, pagination
 * @returns Promise resolving to paginated report configurations
 */
export const getReportConfigurations = async (
  params: {
    page?: number;
    page_size?: number;
    report_type?: string;
    is_active?: boolean;
  } = {}
): Promise<ApiResponse<PaginatedResponse<ReportConfiguration>>> => {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.REPORTS.BASE}/configurations`, {
      params
    });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches a single report configuration by ID
 *
 * @param id - Configuration ID
 * @returns Promise resolving to report configuration
 */
export const getReportConfiguration = async (
  id: UUID
): Promise<ApiResponse<ReportConfiguration>> => {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.REPORTS.BASE}/configurations/${id}`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Creates a new report configuration
 *
 * @param data - Report configuration data
 * @returns Promise resolving to created report configuration
 */
export const createReportConfiguration = async (
  data: ReportConfigurationCreateRequest
): Promise<ApiResponse<ReportConfiguration>> => {
  try {
    const response = await apiClient.post(`${API_ENDPOINTS.REPORTS.BASE}/configurations`, data);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Updates an existing report configuration
 *
 * @param id - Configuration ID
 * @param data - Updated configuration data
 * @returns Promise resolving to updated report configuration
 */
export const updateReportConfiguration = async (
  id: UUID,
  data: ReportConfigurationUpdateRequest
): Promise<ApiResponse<ReportConfiguration>> => {
  try {
    const response = await apiClient.put(`${API_ENDPOINTS.REPORTS.BASE}/configurations/${id}`, data);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Deletes a report configuration (soft delete)
 *
 * @param id - Configuration ID
 * @returns Promise resolving when configuration is deleted
 */
export const deleteReportConfiguration = async (
  id: UUID
): Promise<ApiResponse<void>> => {
  try {
    const response = await apiClient.delete(`${API_ENDPOINTS.REPORTS.BASE}/configurations/${id}`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Generates a report based on a configuration
 *
 * @param data - Report generation parameters
 * @returns Promise resolving to saved report or task ID for async generation
 */
export const generateReport = async (
  data: ReportGenerateRequest
): Promise<ApiResponse<SavedReport | { task_id: string }>> => {
  try {
    const response = await apiClient.post(`${API_ENDPOINTS.REPORTS.BASE}/generate`, data);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches a list of saved reports with optional filtering
 *
 * @param params - Query parameters for filtering, pagination
 * @returns Promise resolving to paginated saved reports
 */
export const getSavedReports = async (
  params: {
    page?: number;
    page_size?: number;
    report_type?: string;
    date_range?: DateRange;
    configuration_id?: UUID;
  } = {}
): Promise<ApiResponse<PaginatedResponse<SavedReport>>> => {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.REPORTS.BASE}/saved`, {
      params
    });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches a single saved report by ID
 *
 * @param id - Saved report ID
 * @returns Promise resolving to saved report
 */
export const getSavedReport = async (
  id: UUID
): Promise<ApiResponse<SavedReport>> => {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.REPORTS.BASE}/saved/${id}`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Exports a saved report in the specified format
 *
 * @param reportId - Saved report ID
 * @param data - Export format and options
 * @returns Promise resolving to export details including download URL
 */
export const exportReport = async (
  reportId: UUID,
  data: ReportExportRequest
): Promise<ApiResponse<ReportExportResponse>> => {
  try {
    const response = await apiClient.post(
      `${API_ENDPOINTS.REPORTS.BASE}/saved/${reportId}/export`,
      data
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches a list of report schedules with optional filtering
 *
 * @param params - Query parameters for filtering, pagination
 * @returns Promise resolving to paginated report schedules
 */
export const getReportSchedules = async (
  params: {
    page?: number;
    page_size?: number;
    configuration_id?: UUID;
    is_active?: boolean;
  } = {}
): Promise<ApiResponse<PaginatedResponse<ReportSchedule>>> => {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.REPORTS.BASE}/schedules`, {
      params
    });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches a single report schedule by ID
 *
 * @param id - Schedule ID
 * @returns Promise resolving to report schedule
 */
export const getReportSchedule = async (
  id: UUID
): Promise<ApiResponse<ReportSchedule>> => {
  try {
    const response = await apiClient.get(`${API_ENDPOINTS.REPORTS.BASE}/schedules/${id}`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Creates a new report schedule
 *
 * @param data - Report schedule data
 * @returns Promise resolving to created report schedule
 */
export const createReportSchedule = async (
  data: ReportScheduleCreateRequest
): Promise<ApiResponse<ReportSchedule>> => {
  try {
    const response = await apiClient.post(`${API_ENDPOINTS.REPORTS.BASE}/schedules`, data);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Updates an existing report schedule
 *
 * @param id - Schedule ID
 * @param data - Updated schedule data
 * @returns Promise resolving to updated report schedule
 */
export const updateReportSchedule = async (
  id: UUID,
  data: ReportScheduleUpdateRequest
): Promise<ApiResponse<ReportSchedule>> => {
  try {
    const response = await apiClient.put(`${API_ENDPOINTS.REPORTS.BASE}/schedules/${id}`, data);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Deletes a report schedule (soft delete)
 *
 * @param id - Schedule ID
 * @returns Promise resolving when schedule is deleted
 */
export const deleteReportSchedule = async (
  id: UUID
): Promise<ApiResponse<void>> => {
  try {
    const response = await apiClient.delete(`${API_ENDPOINTS.REPORTS.BASE}/schedules/${id}`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Manually executes a report schedule
 *
 * @param id - Schedule ID
 * @returns Promise resolving to generated report
 */
export const executeReportSchedule = async (
  id: UUID
): Promise<ApiResponse<SavedReport>> => {
  try {
    const response = await apiClient.post(`${API_ENDPOINTS.REPORTS.BASE}/schedules/${id}/execute`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetches permissions for a report configuration
 *
 * @param configurationId - Configuration ID
 * @returns Promise resolving to array of report permissions
 */
export const getReportPermissions = async (
  configurationId: UUID
): Promise<ApiResponse<ReportPermission[]>> => {
  try {
    const response = await apiClient.get(
      `${API_ENDPOINTS.REPORTS.BASE}/configurations/${configurationId}/permissions`
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Sets permissions for a user on a report configuration
 *
 * @param configurationId - Configuration ID
 * @param data - Permission data
 * @returns Promise resolving to created or updated permission
 */
export const setReportPermission = async (
  configurationId: UUID,
  data: ReportPermissionRequest
): Promise<ApiResponse<ReportPermission>> => {
  try {
    const response = await apiClient.post(
      `${API_ENDPOINTS.REPORTS.BASE}/configurations/${configurationId}/permissions`,
      data
    );
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Convenience function to generate an application volume report
 *
 * @param params - Report parameters
 * @param async - Whether to generate report asynchronously
 * @returns Promise resolving to saved report or task ID
 */
export const getApplicationVolumeReport = async (
  params: ApplicationVolumeReportParams,
  async = false
): Promise<ApiResponse<SavedReport | { task_id: string }>> => {
  const request: ReportGenerateRequest = {
    report_type: ReportType.APPLICATION_VOLUME,
    parameters: params,
    async
  };
  return generateReport(request);
};

/**
 * Convenience function to generate a document status report
 *
 * @param params - Report parameters
 * @param async - Whether to generate report asynchronously
 * @returns Promise resolving to saved report or task ID
 */
export const getDocumentStatusReport = async (
  params: DocumentStatusReportParams,
  async = false
): Promise<ApiResponse<SavedReport | { task_id: string }>> => {
  const request: ReportGenerateRequest = {
    report_type: ReportType.DOCUMENT_STATUS,
    parameters: params,
    async
  };
  return generateReport(request);
};

/**
 * Convenience function to generate a funding metrics report
 *
 * @param params - Report parameters
 * @param async - Whether to generate report asynchronously
 * @returns Promise resolving to saved report or task ID
 */
export const getFundingMetricsReport = async (
  params: FundingMetricsReportParams,
  async = false
): Promise<ApiResponse<SavedReport | { task_id: string }>> => {
  const request: ReportGenerateRequest = {
    report_type: ReportType.FUNDING_METRICS,
    parameters: params,
    async
  };
  return generateReport(request);
};

/**
 * Convenience function to generate an underwriting metrics report
 *
 * @param params - Report parameters
 * @param async - Whether to generate report asynchronously
 * @returns Promise resolving to saved report or task ID
 */
export const getUnderwritingMetricsReport = async (
  params: UnderwritingMetricsReportParams,
  async = false
): Promise<ApiResponse<SavedReport | { task_id: string }>> => {
  const request: ReportGenerateRequest = {
    report_type: ReportType.UNDERWRITING_METRICS,
    parameters: params,
    async
  };
  return generateReport(request);
};