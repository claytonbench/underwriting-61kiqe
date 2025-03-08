/**
 * API client module for authentication-related operations in the loan management system.
 * Provides functions for user login, logout, token refresh, MFA verification, and user profile retrieval.
 * Acts as the interface between the frontend application and the authentication backend services.
 * 
 * @version 1.0.0
 */

import { apiClient, handleApiError } from '../config/api';
import { API_ENDPOINTS } from '../config/constants';
import { 
  LoginCredentials, 
  LoginResponse, 
  AuthTokens, 
  AuthUser, 
  MFAResponse,
  MFASetupData,
  PasswordResetRequest,
  PasswordResetConfirmation
} from '../types/auth.types';
import { ApiResponse } from '../types/common.types';

/**
 * Authenticates a user with email and password credentials
 * 
 * @param credentials - The user's login credentials
 * @returns Promise resolving to login response with tokens and user data
 */
export async function login(credentials: LoginCredentials): Promise<ApiResponse<LoginResponse>> {
  try {
    const response = await apiClient.post(API_ENDPOINTS.AUTH.LOGIN, credentials);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Logs out the current user and invalidates their tokens
 * 
 * @returns Promise resolving to success response
 */
export async function logout(): Promise<ApiResponse<void>> {
  try {
    const response = await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Refreshes the authentication tokens using a refresh token
 * 
 * @param refreshToken - The current refresh token
 * @returns Promise resolving to new authentication tokens
 */
export async function refreshToken(refreshToken: string): Promise<ApiResponse<AuthTokens>> {
  try {
    const response = await apiClient.post(API_ENDPOINTS.AUTH.REFRESH_TOKEN, { refresh_token: refreshToken });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Verifies a multi-factor authentication challenge
 * 
 * @param mfaResponse - The MFA challenge response containing challengeId and verification code
 * @returns Promise resolving to login response with tokens and user data
 */
export async function verifyMFA(mfaResponse: MFAResponse): Promise<ApiResponse<LoginResponse>> {
  try {
    const response = await apiClient.post(`${API_ENDPOINTS.AUTH.LOGIN}/mfa-verify`, mfaResponse);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Initiates MFA setup for a user
 * 
 * @param method - The MFA method to setup (app, sms, email)
 * @returns Promise resolving to MFA setup data including QR code and recovery codes
 */
export async function setupMFA(method: string): Promise<ApiResponse<MFASetupData>> {
  try {
    const response = await apiClient.post(`${API_ENDPOINTS.AUTH.ME}/mfa/setup`, { method });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Verifies and completes MFA setup with verification code
 * 
 * @param code - The verification code from the MFA device or app
 * @param secret - The secret key from MFA setup
 * @returns Promise resolving to success status
 */
export async function verifyMFASetup(code: string, secret: string): Promise<ApiResponse<boolean>> {
  try {
    const response = await apiClient.post(`${API_ENDPOINTS.AUTH.ME}/mfa/verify`, { code, secret });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Disables MFA for the current user
 * 
 * @returns Promise resolving to success status
 */
export async function disableMFA(): Promise<ApiResponse<boolean>> {
  try {
    const response = await apiClient.post(`${API_ENDPOINTS.AUTH.ME}/mfa/disable`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Retrieves the current authenticated user's profile
 * 
 * @returns Promise resolving to current user data
 */
export async function getCurrentUser(): Promise<ApiResponse<AuthUser>> {
  try {
    const response = await apiClient.get(API_ENDPOINTS.AUTH.ME);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Requests a password reset for a user by email
 * 
 * @param request - Password reset request containing email
 * @returns Promise resolving to success response
 */
export async function requestPasswordReset(request: PasswordResetRequest): Promise<ApiResponse<void>> {
  try {
    const response = await apiClient.post(API_ENDPOINTS.AUTH.FORGOT_PASSWORD, request);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Confirms a password reset with token and new password
 * 
 * @param confirmation - Password reset confirmation with token and new password
 * @returns Promise resolving to success response
 */
export async function confirmPasswordReset(confirmation: PasswordResetConfirmation): Promise<ApiResponse<void>> {
  try {
    const response = await apiClient.post(API_ENDPOINTS.AUTH.RESET_PASSWORD, confirmation);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Changes the password for the current authenticated user
 * 
 * @param currentPassword - The user's current password
 * @param newPassword - The new password to set
 * @returns Promise resolving to success response
 */
export async function changePassword(currentPassword: string, newPassword: string): Promise<ApiResponse<void>> {
  try {
    const response = await apiClient.post(API_ENDPOINTS.USERS.UPDATE_PASSWORD, {
      current_password: currentPassword,
      new_password: newPassword
    });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}