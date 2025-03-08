/**
 * Redux reducer for authentication state management in the loan management system.
 * 
 * This file imports the auth slice reducer from Redux Toolkit implementation and 
 * re-exports it as the default export. This approach maintains compatibility with the 
 * traditional Redux reducer pattern while leveraging Redux Toolkit's slice architecture
 * for managing authentication state.
 * 
 * The authentication reducer handles state for user login, session management,
 * token handling, MFA verification, and other authentication-related operations.
 * 
 * @version 1.0.0
 */

// Import type definition for Redux reducers
import { Reducer } from 'redux'; // v4.2.1

// Import the authentication state interface
import { AuthState } from '../../types/auth.types';

// Import the auth slice reducer from Redux Toolkit implementation
import { reducer } from '../slices/authSlice';

// Export the auth slice reducer as the default export to maintain compatibility with traditional Redux reducer pattern
export default reducer as Reducer<AuthState>;