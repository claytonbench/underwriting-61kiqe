/**
 * Redux Toolkit thunk actions for authentication-related operations in the loan management system.
 * Implements async operations for user login, logout, token refreshing, MFA verification,
 * user data fetching, and password management.
 * 
 * @version 1.0.0
 */

import { createAsyncThunk, AsyncThunk } from '@reduxjs/toolkit'; // v1.9.5

// API client functions for authentication
import {
  login,
  logout,
  refreshToken,
  verifyMFA,
  getCurrentUser,
  requestPasswordReset,
  confirmPasswordReset
} from '../../api/auth';

// Type definitions for authentication data
import {
  LoginCredentials,
  MFAResponse,
  PasswordResetRequest,
  PasswordResetConfirmation,
  AuthUser,
  AuthTokens,
  MFAChallenge
} from '../../types/auth.types';

// Storage utilities for persistent auth data
import {
  setAuthTokens,
  getAuthTokens,
  removeAuthTokens,
  setUserData,
  getUserData,
  removeUserData
} from '../../utils/storage';

/**
 * Thunk action to authenticate a user with email and password credentials
 * 
 * @param credentials - Login form data including email, password, and remember me preference
 * @returns Auth tokens, user data, MFA status, and challenge (if required)
 */
export const loginUser = createAsyncThunk(
  'auth/login',
  async (credentials: LoginCredentials, { rejectWithValue }) => {
    try {
      const response = await login(credentials);
      
      if (!response.success) {
        return rejectWithValue(response.message || 'Login failed');
      }
      
      const { tokens, user, mfaRequired, mfaChallenge } = response.data;
      
      // Store tokens regardless of MFA status
      if (tokens) {
        setAuthTokens(tokens);
      }
      
      // Only store user data if MFA is not required (auth is complete)
      if (!mfaRequired && user) {
        setUserData(user);
      }
      
      return { tokens, user, mfaRequired, mfaChallenge };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Authentication failed';
      return rejectWithValue(errorMessage);
    }
  }
);

/**
 * Thunk action to log out the current user and clear auth state
 * 
 * @returns Promise resolving when logout is complete
 */
export const logoutUser = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      // Call the logout API to invalidate tokens on the server
      const response = await logout();
      
      // Remove stored auth data from localStorage regardless of API response
      // This ensures the user is logged out client-side even if server request fails
      removeAuthTokens();
      removeUserData();
      
      if (!response.success) {
        // Log the error but don't reject - user should still be logged out locally
        console.warn('Server logout may have failed:', response.message);
      }
      
      return;
    } catch (error) {
      // Still clear local auth data even if API call fails
      removeAuthTokens();
      removeUserData();
      
      const errorMessage = error instanceof Error ? error.message : 'Logout failed';
      console.warn('Logout error:', errorMessage);
      return rejectWithValue(errorMessage);
    }
  }
);

/**
 * Thunk action to refresh the authentication tokens
 * 
 * @returns New authentication tokens
 */
export const refreshUserToken = createAsyncThunk(
  'auth/refreshToken',
  async (_, { rejectWithValue }) => {
    try {
      const currentTokens = getAuthTokens();
      
      if (!currentTokens?.refreshToken) {
        throw new Error('No refresh token available');
      }
      
      const response = await refreshToken(currentTokens.refreshToken);
      
      if (!response.success || !response.data) {
        return rejectWithValue(response.message || 'Token refresh failed');
      }
      
      // Store the new tokens
      setAuthTokens(response.data);
      
      return response.data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Token refresh failed';
      return rejectWithValue(errorMessage);
    }
  }
);

/**
 * Thunk action to verify a multi-factor authentication challenge
 * 
 * @param mfaResponse - The MFA challenge response containing challengeId and verification code
 * @returns Authentication tokens and user data after successful verification
 */
export const verifyMFAChallenge = createAsyncThunk(
  'auth/verifyMFA',
  async (mfaResponse: MFAResponse, { rejectWithValue }) => {
    try {
      const response = await verifyMFA(mfaResponse);
      
      if (!response.success || !response.data) {
        return rejectWithValue(response.message || 'MFA verification failed');
      }
      
      const { tokens, user } = response.data;
      
      // Store authentication data now that MFA is verified
      setAuthTokens(tokens);
      setUserData(user);
      
      return { tokens, user };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'MFA verification failed';
      return rejectWithValue(errorMessage);
    }
  }
);

/**
 * Thunk action to fetch the current authenticated user's data
 * 
 * @returns Current user data
 */
export const fetchCurrentUser = createAsyncThunk(
  'auth/fetchCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const response = await getCurrentUser();
      
      if (!response.success || !response.data) {
        return rejectWithValue(response.message || 'Failed to fetch user data');
      }
      
      // Update stored user data
      setUserData(response.data);
      
      return response.data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch user data';
      return rejectWithValue(errorMessage);
    }
  }
);

/**
 * Thunk action to request a password reset for a user
 * 
 * @param request - Password reset request containing email address
 * @returns Promise resolving when request is processed
 */
export const requestUserPasswordReset = createAsyncThunk(
  'auth/requestPasswordReset',
  async (request: PasswordResetRequest, { rejectWithValue }) => {
    try {
      const response = await requestPasswordReset(request);
      
      if (!response.success) {
        return rejectWithValue(response.message || 'Password reset request failed');
      }
      
      return;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Password reset request failed';
      return rejectWithValue(errorMessage);
    }
  }
);

/**
 * Thunk action to confirm a password reset with token and new password
 * 
 * @param confirmation - Password reset confirmation data
 * @returns Promise resolving when confirmation is complete
 */
export const confirmUserPasswordReset = createAsyncThunk(
  'auth/confirmPasswordReset',
  async (confirmation: PasswordResetConfirmation, { rejectWithValue }) => {
    try {
      const response = await confirmPasswordReset(confirmation);
      
      if (!response.success) {
        return rejectWithValue(response.message || 'Password reset confirmation failed');
      }
      
      return;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Password reset confirmation failed';
      return rejectWithValue(errorMessage);
    }
  }
);

/**
 * Thunk action to initialize authentication state from localStorage
 * Attempts to hydrate the auth state from stored tokens and user data
 * 
 * @returns Stored authentication tokens and user data
 */
export const initializeAuth = createAsyncThunk(
  'auth/initialize',
  async (_, { dispatch, rejectWithValue }) => {
    try {
      // Retrieve stored auth data
      const tokens = getAuthTokens();
      const user = getUserData();
      
      // If we have tokens but they're expired, try to refresh
      if (tokens && tokens.expiresAt && tokens.expiresAt < Date.now()) {
        try {
          // Attempt to refresh the token
          await dispatch(refreshUserToken()).unwrap();
          // Get the fresh tokens after refresh
          const refreshedTokens = getAuthTokens();
          return { tokens: refreshedTokens, user };
        } catch (refreshError) {
          // If refresh fails, clear auth data and return null
          removeAuthTokens();
          removeUserData();
          return { tokens: null, user: null };
        }
      }
      
      return { tokens, user };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to initialize authentication';
      return rejectWithValue(errorMessage);
    }
  }
);