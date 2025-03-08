/**
 * API client module for notification-related operations in the loan management system.
 * Provides functions for interacting with the notification endpoints.
 * 
 * @version 1.0.0
 */

import { apiClient, handleApiError } from '../config/api'; // axios v1.4.0
import { API_ENDPOINTS } from '../config/constants';
import { 
  INotification, 
  INotificationDisplay, 
  INotificationResponse, 
  IMarkAsReadRequest, 
  INotificationFilter, 
  INotificationTemplate, 
  INotificationPreference,
  PaginatedNotificationResponse
} from '../types/notification.types';
import { ApiResponse, UUID } from '../types/common.types';

/**
 * Retrieves notifications for the current user with optional filtering
 * 
 * @param filters - Optional filters to apply to the notification request
 * @param page - Page number for pagination
 * @param limit - Number of results per page
 * @returns Promise resolving to notification response with notifications and unread count
 */
export async function getNotifications(
  filters?: INotificationFilter,
  page?: number,
  limit?: number
): Promise<ApiResponse<INotificationResponse>> {
  try {
    // Construct query parameters
    const params: Record<string, any> = {};
    
    if (filters) {
      if (filters.category) params.category = filters.category;
      if (filters.priority) params.priority = filters.priority;
      if (filters.read !== null && filters.read !== undefined) params.read = filters.read;
      if (filters.startDate) params.start_date = filters.startDate;
      if (filters.endDate) params.end_date = filters.endDate;
    }
    
    if (page) params.page = page;
    if (limit) params.limit = limit;

    const response = await apiClient.get<ApiResponse<INotificationResponse>>(
      API_ENDPOINTS.NOTIFICATIONS.BASE,
      { params }
    );

    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Retrieves paginated notifications for the current user with optional filtering
 * 
 * @param filters - Optional filters to apply to the notification request
 * @param page - Page number for pagination (required)
 * @param limit - Number of results per page (required)
 * @returns Promise resolving to paginated notification response
 */
export async function getPaginatedNotifications(
  filters?: INotificationFilter,
  page: number = 1,
  limit: number = 10
): Promise<ApiResponse<PaginatedNotificationResponse>> {
  try {
    // Construct query parameters
    const params: Record<string, any> = {
      page,
      limit
    };
    
    if (filters) {
      if (filters.category) params.category = filters.category;
      if (filters.priority) params.priority = filters.priority;
      if (filters.read !== null && filters.read !== undefined) params.read = filters.read;
      if (filters.startDate) params.start_date = filters.startDate;
      if (filters.endDate) params.end_date = filters.endDate;
    }

    const response = await apiClient.get<ApiResponse<PaginatedNotificationResponse>>(
      `${API_ENDPOINTS.NOTIFICATIONS.BASE}/paginated`,
      { params }
    );

    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Retrieves a specific notification by ID
 * 
 * @param id - Notification ID
 * @returns Promise resolving to notification display object
 */
export async function getNotificationById(id: UUID): Promise<ApiResponse<INotificationDisplay>> {
  try {
    const response = await apiClient.get<ApiResponse<INotificationDisplay>>(
      API_ENDPOINTS.NOTIFICATIONS.BY_ID(id)
    );

    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Marks specified notifications as read
 * 
 * @param notificationIds - Array of notification IDs to mark as read
 * @returns Promise resolving to success response
 */
export async function markAsRead(notificationIds: UUID[]): Promise<ApiResponse<void>> {
  try {
    const payload: IMarkAsReadRequest = {
      notificationIds
    };

    const response = await apiClient.post<ApiResponse<void>>(
      `${API_ENDPOINTS.NOTIFICATIONS.BASE}/mark-read`,
      payload
    );

    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Marks all notifications for the current user as read
 * 
 * @returns Promise resolving to success response
 */
export async function markAllAsRead(): Promise<ApiResponse<void>> {
  try {
    const response = await apiClient.post<ApiResponse<void>>(
      API_ENDPOINTS.NOTIFICATIONS.MARK_ALL_READ
    );

    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Deletes a specific notification by ID
 * 
 * @param id - Notification ID
 * @returns Promise resolving to success response
 */
export async function deleteNotification(id: UUID): Promise<ApiResponse<void>> {
  try {
    const response = await apiClient.delete<ApiResponse<void>>(
      API_ENDPOINTS.NOTIFICATIONS.BY_ID(id)
    );

    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Retrieves notification preferences for the current user
 * 
 * @returns Promise resolving to notification preferences
 */
export async function getNotificationPreferences(): Promise<ApiResponse<INotificationPreference[]>> {
  try {
    const response = await apiClient.get<ApiResponse<INotificationPreference[]>>(
      `${API_ENDPOINTS.NOTIFICATIONS.BASE}/preferences`
    );

    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Updates a specific notification preference
 * 
 * @param preferenceId - Preference ID
 * @param updates - Object containing preference fields to update
 * @returns Promise resolving to updated notification preference
 */
export async function updateNotificationPreference(
  preferenceId: UUID,
  updates: Partial<INotificationPreference>
): Promise<ApiResponse<INotificationPreference>> {
  try {
    const response = await apiClient.patch<ApiResponse<INotificationPreference>>(
      `${API_ENDPOINTS.NOTIFICATIONS.BASE}/preferences/${preferenceId}`,
      updates
    );

    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Retrieves notification templates with optional filtering
 * 
 * @param filters - Optional filter criteria for templates
 * @returns Promise resolving to notification templates
 */
export async function getNotificationTemplates(
  filters?: object
): Promise<ApiResponse<INotificationTemplate[]>> {
  try {
    const response = await apiClient.get<ApiResponse<INotificationTemplate[]>>(
      `${API_ENDPOINTS.NOTIFICATIONS.BASE}/templates`,
      filters ? { params: filters } : undefined
    );

    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Retrieves a specific notification template by ID
 * 
 * @param id - Template ID
 * @returns Promise resolving to notification template
 */
export async function getNotificationTemplateById(id: UUID): Promise<ApiResponse<INotificationTemplate>> {
  try {
    const response = await apiClient.get<ApiResponse<INotificationTemplate>>(
      `${API_ENDPOINTS.NOTIFICATIONS.BASE}/templates/${id}`
    );

    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Creates a new notification template
 * 
 * @param templateData - Template data excluding auto-generated fields
 * @returns Promise resolving to created notification template
 */
export async function createNotificationTemplate(
  templateData: Omit<INotificationTemplate, 'id' | 'createdAt' | 'updatedAt'>
): Promise<ApiResponse<INotificationTemplate>> {
  try {
    const response = await apiClient.post<ApiResponse<INotificationTemplate>>(
      `${API_ENDPOINTS.NOTIFICATIONS.BASE}/templates`,
      templateData
    );

    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Updates a specific notification template
 * 
 * @param id - Template ID
 * @param updates - Object containing template fields to update
 * @returns Promise resolving to updated notification template
 */
export async function updateNotificationTemplate(
  id: UUID,
  updates: Partial<INotificationTemplate>
): Promise<ApiResponse<INotificationTemplate>> {
  try {
    const response = await apiClient.patch<ApiResponse<INotificationTemplate>>(
      `${API_ENDPOINTS.NOTIFICATIONS.BASE}/templates/${id}`,
      updates
    );

    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Deletes a specific notification template by ID
 * 
 * @param id - Template ID
 * @returns Promise resolving to success response
 */
export async function deleteNotificationTemplate(id: UUID): Promise<ApiResponse<void>> {
  try {
    const response = await apiClient.delete<ApiResponse<void>>(
      `${API_ENDPOINTS.NOTIFICATIONS.BASE}/templates/${id}`
    );

    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Generates a preview of a notification template with sample data
 * 
 * @param id - Template ID
 * @param sampleData - Optional sample data to use for template variables
 * @returns Promise resolving to preview with subject and body
 */
export async function previewNotificationTemplate(
  id: UUID,
  sampleData?: object
): Promise<ApiResponse<{subject: string, body: string}>> {
  try {
    const response = await apiClient.post<ApiResponse<{subject: string, body: string}>>(
      `${API_ENDPOINTS.NOTIFICATIONS.BASE}/templates/${id}/preview`,
      sampleData || {}
    );

    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}