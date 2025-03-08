/**
 * Redux action creators for authentication-related operations in the loan management system.
 * Re-exports async thunks and synchronous actions to provide a unified interface for authentication
 * operations throughout the application.
 *
 * @version 1.0.0
 */

// Import async thunk actions for authentication operations
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

// Import synchronous action creators from auth slice
import {
  setAuthError,
  clearAuthError,
  resetAuthState
} from '../slices/authSlice';

// Import selector functions for auth state
import {
  selectAuthState,
  selectIsAuthenticated,
  selectCurrentUser,
  selectAuthLoading,
  selectAuthError,
  selectMFARequired,
  selectMFAChallenge
} from '../slices/authSlice';

// Re-export all authentication-related actions and selectors
export {
  // Async thunk actions
  loginUser,
  logoutUser,
  refreshUserToken,
  verifyMFAChallenge,
  fetchCurrentUser,
  requestUserPasswordReset,
  confirmUserPasswordReset,
  initializeAuth,
  
  // Synchronous actions
  setAuthError,
  clearAuthError,
  resetAuthState,
  
  // Selectors
  selectAuthState,
  selectIsAuthenticated,
  selectCurrentUser,
  selectAuthLoading,
  selectAuthError,
  selectMFARequired,
  selectMFAChallenge
};