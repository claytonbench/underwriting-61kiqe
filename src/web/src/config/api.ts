import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';
import { API_ENDPOINTS, STORAGE_KEYS, ERROR_MESSAGES } from './constants';
import { ApiResponse } from '../types';
import { getAuthTokens } from '../utils/storage';

// API base URL
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

// Configure axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const tokens = getAuthTokens();
    if (tokens?.accessToken) {
      // Add authorization header
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${tokens.accessToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error: AxiosError) => {
    // Handle token refresh for 401 errors
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && originalRequest && !(originalRequest as any)._retry) {
      (originalRequest as any)._retry = true;
      
      try {
        const tokens = getAuthTokens();
        
        if (tokens?.refreshToken) {
          // Call token refresh endpoint
          const response = await axios.post(
            `${API_BASE_URL}${API_ENDPOINTS.AUTH.REFRESH_TOKEN}`,
            { refresh_token: tokens.refreshToken }
          );
          
          if (response.data.success && response.data.data.accessToken) {
            // Update Authorization header and retry
            originalRequest.headers = originalRequest.headers || {};
            originalRequest.headers.Authorization = `Bearer ${response.data.data.accessToken}`;
            return axios(originalRequest);
          }
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
      }
    }
    
    // For all other errors, proceed with standard error handling
    return Promise.reject(handleApiError(error));
  }
);

/**
 * Processes API errors and formats them into a standardized response
 * 
 * @param error - The AxiosError object from a failed request
 * @returns A standardized API error response
 */
export function handleApiError(error: AxiosError): ApiResponse<any> {
  let message = ERROR_MESSAGES.GENERIC;
  let errors = null;

  if (error.response) {
    // The request was made and the server responded with a status code outside of 2xx
    const responseData = error.response.data as any;
    
    if (responseData) {
      if (responseData.message) {
        message = responseData.message;
      } else if (typeof responseData === 'string') {
        message = responseData;
      }
      
      if (responseData.errors) {
        errors = responseData.errors;
      }
    }

    // Handle specific HTTP status codes
    switch (error.response.status) {
      case 401:
        message = ERROR_MESSAGES.UNAUTHORIZED;
        break;
      case 403:
        message = ERROR_MESSAGES.FORBIDDEN;
        break;
      case 404:
        message = ERROR_MESSAGES.NOT_FOUND;
        break;
      case 422:
        message = ERROR_MESSAGES.VALIDATION;
        break;
      case 500:
        message = ERROR_MESSAGES.SERVER;
        break;
      case 504:
        message = ERROR_MESSAGES.TIMEOUT;
        break;
    }
  } else if (error.request) {
    // The request was made but no response was received
    message = ERROR_MESSAGES.NETWORK;
  } else {
    // Something happened in setting up the request that triggered an error
    message = error.message || ERROR_MESSAGES.GENERIC;
  }

  return {
    success: false,
    message,
    data: null,
    errors
  };
}

export { apiClient };