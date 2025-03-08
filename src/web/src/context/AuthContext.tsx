import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { 
  AuthState, 
  LoginCredentials, 
  MFAResponse, 
  AuthTokens, 
  AuthUser 
} from '../types/auth.types';
import { 
  login as apiLogin, 
  logout as apiLogout, 
  refreshToken as apiRefreshToken,
  verifyMFA as apiVerifyMFA,
  getCurrentUser as apiGetCurrentUser
} from '../api/auth';
import {
  setAuthTokens,
  getAuthTokens,
  removeAuthTokens,
  setUserData,
  getUserData,
  removeUserData
} from '../utils/storage';

/**
 * Interface defining the shape of the authentication context
 */
interface AuthContextType {
  state: AuthState;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  verifyMFA: (mfaResponse: MFAResponse) => Promise<void>;
  refreshTokens: () => Promise<void>;
}

/**
 * Interface for the AuthProvider component props
 */
interface AuthProviderProps {
  children: ReactNode;
}

// Create the auth context with undefined as default value
const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Authentication Provider component that manages auth state and provides
 * authentication-related functionality throughout the application
 */
const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  // Initialize authentication state
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    tokens: null,
    loading: true,
    error: null,
    mfaRequired: false,
    mfaChallenge: null
  });

  /**
   * Initialize auth state from stored tokens and user data
   */
  const initializeAuthState = useCallback(() => {
    try {
      const tokens = getAuthTokens();
      const userData = getUserData();

      if (tokens && userData) {
        // Check if token is expired
        const currentTime = Date.now();
        if (tokens.expiresAt > currentTime) {
          // Token is still valid
          setAuthState({
            isAuthenticated: true,
            user: userData,
            tokens,
            loading: false,
            error: null,
            mfaRequired: false,
            mfaChallenge: null
          });
        } else {
          // Token is expired, try to refresh
          handleRefreshTokens().catch(() => {
            // If refresh fails, ensure we're in a logged-out state
            setAuthState({
              isAuthenticated: false,
              user: null,
              tokens: null,
              loading: false,
              error: null,
              mfaRequired: false,
              mfaChallenge: null
            });
          });
        }
      } else {
        // No tokens or user data, ensure we're in a logged-out state
        setAuthState({
          isAuthenticated: false,
          user: null,
          tokens: null,
          loading: false,
          error: null,
          mfaRequired: false,
          mfaChallenge: null
        });
      }
    } catch (error) {
      console.error('Error initializing auth state:', error);
      setAuthState({
        isAuthenticated: false,
        user: null,
        tokens: null,
        loading: false,
        error: 'Failed to initialize authentication state',
        mfaRequired: false,
        mfaChallenge: null
      });
    }
  }, []);

  /**
   * Handles user login with credentials
   * @param credentials User login credentials
   */
  const handleLogin = useCallback(async (credentials: LoginCredentials) => {
    try {
      setAuthState(prevState => ({
        ...prevState,
        loading: true,
        error: null
      }));

      const response = await apiLogin(credentials);

      if (!response.success) {
        throw new Error(response.message || 'Login failed');
      }

      const { data } = response;

      if (data.mfaRequired) {
        // MFA is required
        setAuthState(prevState => ({
          ...prevState,
          loading: false,
          mfaRequired: true,
          mfaChallenge: data.mfaChallenge
        }));
        return;
      }

      // Login successful, store tokens and user data
      const { tokens, user } = data;
      setAuthTokens(tokens);
      setUserData(user);

      setAuthState({
        isAuthenticated: true,
        user,
        tokens,
        loading: false,
        error: null,
        mfaRequired: false,
        mfaChallenge: null
      });
    } catch (error) {
      console.error('Login error:', error);
      setAuthState(prevState => ({
        ...prevState,
        loading: false,
        error: error instanceof Error ? error.message : 'An unexpected error occurred'
      }));
    }
  }, []);

  /**
   * Handles user logout
   */
  const handleLogout = useCallback(async () => {
    try {
      // Call logout API
      await apiLogout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Always clean up local state, even if API call fails
      removeAuthTokens();
      removeUserData();
      
      setAuthState({
        isAuthenticated: false,
        user: null,
        tokens: null,
        loading: false,
        error: null,
        mfaRequired: false,
        mfaChallenge: null
      });
    }
  }, []);

  /**
   * Handles MFA verification
   * @param mfaResponse MFA challenge response from user
   */
  const handleVerifyMFA = useCallback(async (mfaResponse: MFAResponse) => {
    try {
      setAuthState(prevState => ({
        ...prevState,
        loading: true,
        error: null
      }));

      const response = await apiVerifyMFA(mfaResponse);

      if (!response.success) {
        throw new Error(response.message || 'MFA verification failed');
      }

      const { data } = response;
      
      // MFA successful, store tokens and user data
      const { tokens, user } = data;
      setAuthTokens(tokens);
      setUserData(user);

      setAuthState({
        isAuthenticated: true,
        user,
        tokens,
        loading: false,
        error: null,
        mfaRequired: false,
        mfaChallenge: null
      });
    } catch (error) {
      console.error('MFA verification error:', error);
      setAuthState(prevState => ({
        ...prevState,
        loading: false,
        error: error instanceof Error ? error.message : 'An unexpected error occurred'
      }));
    }
  }, []);

  /**
   * Refreshes authentication tokens
   */
  const handleRefreshTokens = useCallback(async () => {
    try {
      const currentTokens = authState.tokens || getAuthTokens();
      
      if (!currentTokens?.refreshToken) {
        // No refresh token available, can't refresh
        handleLogout();
        return null;
      }

      const response = await apiRefreshToken(currentTokens.refreshToken);

      if (!response.success || !response.data) {
        throw new Error(response.message || 'Token refresh failed');
      }

      const newTokens = response.data;
      
      // Store new tokens
      setAuthTokens(newTokens);
      
      // Update auth state with new tokens
      setAuthState(prevState => ({
        ...prevState,
        tokens: newTokens,
        isAuthenticated: true
      }));
      
      return newTokens;
    } catch (error) {
      console.error('Token refresh error:', error);
      // If refresh fails, log the user out
      handleLogout();
      return null;
    }
  }, [authState.tokens, handleLogout]);

  // Initialize auth state from storage on component mount
  useEffect(() => {
    initializeAuthState();
  }, [initializeAuthState]);

  // Set up token refresh mechanism
  useEffect(() => {
    if (!authState.tokens) return undefined;

    // Calculate time until token expiration
    const currentTime = Date.now();
    const expiresAt = authState.tokens.expiresAt;
    
    // We want to refresh the token 5 minutes before it expires
    const timeUntilRefresh = Math.max(0, expiresAt - currentTime - (5 * 60 * 1000));
    
    // If the token is already expired or will expire in less than 5 minutes, refresh now
    if (timeUntilRefresh === 0) {
      handleRefreshTokens().catch(err => {
        console.error('Failed to refresh token during setup:', err);
      });
      return undefined;
    }

    // Set up timer to refresh the token
    const refreshTimer = setTimeout(() => {
      handleRefreshTokens().catch(err => {
        console.error('Failed to refresh token from timer:', err);
      });
    }, timeUntilRefresh);

    // Clean up timer on unmount or when tokens change
    return () => {
      clearTimeout(refreshTimer);
    };
  }, [authState.tokens, handleRefreshTokens]);

  // Context value that will be provided
  const contextValue: AuthContextType = {
    state: authState,
    login: handleLogin,
    logout: handleLogout,
    verifyMFA: handleVerifyMFA,
    refreshTokens: handleRefreshTokens
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

/**
 * Custom hook to use the authentication context
 * @returns Authentication context with state and methods
 * @throws Error if used outside of AuthProvider
 */
const useAuthContext = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
};

export { AuthProvider, useAuthContext, AuthContext };