import { AuthContext, useAuthContext } from '../context/AuthContext';
import { AuthState, LoginCredentials, MFAResponse, AuthUser, AuthTokens } from '../types/auth.types';

/**
 * Interface defining the return type of the useAuth hook
 */
interface UseAuthReturn {
  /** Current authentication state */
  state: AuthState;
  
  /**
   * Authenticates a user with the provided credentials
   * @param credentials - User login credentials
   */
  login: (credentials: LoginCredentials) => Promise<void>;
  
  /**
   * Logs out the current user
   */
  logout: () => Promise<void>;
  
  /**
   * Verifies a multi-factor authentication response
   * @param mfaResponse - MFA challenge response
   */
  verifyMFA: (mfaResponse: MFAResponse) => Promise<void>;
  
  /**
   * Refreshes the authentication tokens
   */
  refreshTokens: () => Promise<void>;
}

/**
 * Custom hook that provides access to authentication state and methods
 * throughout the application. Simplifies access to authentication context.
 * 
 * This hook wraps the AuthContext to provide:
 * - Current authentication state (user, tokens, loading, error, etc.)
 * - Login functionality
 * - Logout functionality
 * - MFA verification
 * - Token refresh
 * 
 * @returns Object containing authentication state and methods
 * @example
 * const { state, login, logout } = useAuth();
 * 
 * // Check if user is authenticated
 * if (state.isAuthenticated) {
 *   // User is logged in
 * }
 * 
 * // Login user
 * await login({ email: 'user@example.com', password: 'password', rememberMe: true });
 * 
 * // Logout user
 * await logout();
 */
export function useAuth(): UseAuthReturn {
  const authContext = useAuthContext();
  
  return authContext;
}

export default useAuth;