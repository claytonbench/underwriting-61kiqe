/**
 * Redux Toolkit slice for authentication state management in the loan management system.
 * This file defines the authentication state structure, reducers for synchronous state updates,
 * and handles async thunk action results for login, logout, token refresh, and other
 * authentication operations.
 * 
 * @version 1.0.0
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit'; // v1.9.5

// Import auth state type definition
import { 
  AuthState, 
  AuthTokens, 
  AuthUser,
  MFAChallenge
} from '../../types/auth.types';

// Import authentication-related async thunks
import { 
  loginUser,
  logoutUser,
  refreshUserToken,
  verifyMFAChallenge,
  fetchCurrentUser,
  requestUserPasswordReset,
  confirmUserPasswordReset,
  initializeAuth
} from '../thunks/authThunks';

// Initial authentication state
const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  tokens: null,
  loading: false,
  error: null,
  mfaRequired: false,
  mfaChallenge: null
};

// Create the auth slice with reducers and extra reducers for async actions
export const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    // Clear any authentication error messages
    clearAuthError: (state) => {
      state.error = null;
    },
    
    // Reset the authentication state to initial values
    resetAuthState: (state) => {
      state.isAuthenticated = false;
      state.user = null;
      state.tokens = null;
      state.loading = false;
      state.error = null;
      state.mfaRequired = false;
      state.mfaChallenge = null;
    },
    
    // Set the MFA required flag and challenge data
    setMFARequired: (state, action: PayloadAction<{ required: boolean; challenge: MFAChallenge | null }>) => {
      state.mfaRequired = action.payload.required;
      state.mfaChallenge = action.payload.challenge;
    }
  },
  extraReducers: (builder) => {
    // Handle loginUser async thunk results
    builder
      .addCase(loginUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.loading = false;
        state.tokens = action.payload.tokens;
        
        // Only set user data and authentication flag if MFA is not required
        if (!action.payload.mfaRequired) {
          state.user = action.payload.user;
          state.isAuthenticated = true;
        }
        
        state.mfaRequired = action.payload.mfaRequired;
        state.mfaChallenge = action.payload.mfaChallenge;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Login failed';
      })
    
    // Handle logoutUser async thunk results
    builder
      .addCase(logoutUser.pending, (state) => {
        state.loading = true;
      })
      .addCase(logoutUser.fulfilled, (state) => {
        // Reset state to initial values on successful logout
        return initialState;
      })
      .addCase(logoutUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Logout failed';
      })
    
    // Handle refreshUserToken async thunk results
    builder
      .addCase(refreshUserToken.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(refreshUserToken.fulfilled, (state, action) => {
        state.loading = false;
        state.tokens = action.payload;
      })
      .addCase(refreshUserToken.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Token refresh failed';
        
        // Reset authentication state on token refresh failure
        state.isAuthenticated = false;
        state.user = null;
        state.tokens = null;
      })
    
    // Handle verifyMFAChallenge async thunk results
    builder
      .addCase(verifyMFAChallenge.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(verifyMFAChallenge.fulfilled, (state, action) => {
        state.loading = false;
        state.tokens = action.payload.tokens;
        state.user = action.payload.user;
        state.isAuthenticated = true;
        state.mfaRequired = false;
        state.mfaChallenge = null;
      })
      .addCase(verifyMFAChallenge.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'MFA verification failed';
      })
    
    // Handle fetchCurrentUser async thunk results
    builder
      .addCase(fetchCurrentUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
        state.isAuthenticated = true;
      })
      .addCase(fetchCurrentUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch user data';
        
        // Reset authentication state on failure to fetch user data
        state.isAuthenticated = false;
        state.user = null;
        state.tokens = null;
      })
    
    // Handle initializeAuth async thunk results
    builder
      .addCase(initializeAuth.pending, (state) => {
        state.loading = true;
      })
      .addCase(initializeAuth.fulfilled, (state, action) => {
        state.loading = false;
        state.tokens = action.payload.tokens;
        state.user = action.payload.user;
        state.isAuthenticated = Boolean(action.payload.user);
      })
      .addCase(initializeAuth.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to initialize authentication';
      })
    
    // Handle requestUserPasswordReset async thunk results
    builder
      .addCase(requestUserPasswordReset.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(requestUserPasswordReset.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(requestUserPasswordReset.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Password reset request failed';
      })
    
    // Handle confirmUserPasswordReset async thunk results
    builder
      .addCase(confirmUserPasswordReset.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(confirmUserPasswordReset.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(confirmUserPasswordReset.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Password reset confirmation failed';
      });
  }
});

// Export action creators
export const { clearAuthError, resetAuthState, setMFARequired } = authSlice.actions;

// Export the reducer
export default authSlice.reducer;