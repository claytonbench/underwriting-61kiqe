/**
 * Authentication-related TypeScript type definitions for the loan management system.
 * 
 * This file contains type definitions for user authentication, authorization,
 * session management, and MFA-related data structures used throughout the frontend.
 * It supports integration with Auth0 and implements the authentication framework
 * as described in the technical specifications.
 */

import { UUID, ISO8601Date, EmailAddress } from './common.types';

/**
 * Enum defining possible user types in the system
 */
export enum UserType {
  BORROWER = 'borrower',
  CO_BORROWER = 'co_borrower',
  SCHOOL_ADMIN = 'school_admin',
  UNDERWRITER = 'underwriter',
  QC = 'qc',
  SYSTEM_ADMIN = 'system_admin'
}

/**
 * Interface for authentication tokens returned from the API
 */
export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  idToken: string;
  expiresAt: number; // Unix timestamp in milliseconds
}

/**
 * Interface for authenticated user data
 */
export interface AuthUser {
  id: UUID;
  email: EmailAddress;
  firstName: string;
  lastName: string;
  userType: UserType;
  permissions: string[];
  roles: string[];
  schoolId: UUID | null; // Only relevant for school administrators
  mfaEnabled: boolean;
  lastLogin: ISO8601Date | null;
}

/**
 * Interface for login form data
 */
export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe: boolean;
}

/**
 * Interface for MFA challenge data
 */
export interface MFAChallenge {
  challengeId: string;
  method: string;
  destination: string; // Partially masked email or phone
}

/**
 * Interface for MFA verification response
 */
export interface MFAResponse {
  challengeId: string;
  code: string;
}

/**
 * Interface for login response data
 */
export interface LoginResponse {
  tokens: AuthTokens;
  user: AuthUser;
  mfaRequired: boolean;
  mfaChallenge: MFAChallenge | null;
}

/**
 * Interface for password reset request
 */
export interface PasswordResetRequest {
  email: string;
}

/**
 * Interface for password reset confirmation
 */
export interface PasswordResetConfirmation {
  token: string;
  password: string;
  confirmPassword: string;
}

/**
 * Interface for authentication state in the application
 */
export interface AuthState {
  isAuthenticated: boolean;
  user: AuthUser | null;
  tokens: AuthTokens | null;
  loading: boolean;
  error: string | null;
  mfaRequired: boolean;
  mfaChallenge: MFAChallenge | null;
}

/**
 * Interface for MFA setup data
 */
export interface MFASetupData {
  qrCodeUrl: string;
  secret: string;
  recoveryCode: string;
}

/**
 * Enum defining supported MFA methods
 */
export enum MFAMethod {
  APP = 'app',
  SMS = 'sms',
  EMAIL = 'email'
}

/**
 * Helper function to check if a user has a specific permission
 * 
 * @param user The authenticated user
 * @param permission The permission to check
 * @returns Boolean indicating if the user has the specified permission
 */
export function hasPermission(user: AuthUser | null, permission: string): boolean {
  if (!user) return false;
  return user.permissions.includes(permission);
}

/**
 * Helper function to check if a user has a specific role
 * 
 * @param user The authenticated user
 * @param role The role to check
 * @returns Boolean indicating if the user has the specified role
 */
export function hasRole(user: AuthUser | null, role: string): boolean {
  if (!user) return false;
  return user.roles.includes(role);
}