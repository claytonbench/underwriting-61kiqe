import { useCallback } from 'react';
import { useAuth } from './useAuth';
import { hasPermission, hasRole } from '../types/auth.types';

/**
 * Interface defining the return type of the usePermissions hook
 */
interface UsePermissionsReturn {
  /**
   * Checks if the current user has a specific permission
   * @param permission - The permission to check
   * @returns True if the user has the permission, false otherwise
   */
  checkPermission: (permission: string) => boolean;
  
  /**
   * Checks if the current user has a specific role
   * @param role - The role to check
   * @returns True if the user has the role, false otherwise
   */
  checkRole: (role: string) => boolean;
  
  /**
   * Checks if the current user has any of the specified permissions
   * @param permissions - Array of permissions to check
   * @returns True if the user has any of the permissions, false otherwise
   */
  checkAnyPermission: (permissions: string[]) => boolean;
  
  /**
   * Checks if the current user has all of the specified permissions
   * @param permissions - Array of permissions to check
   * @returns True if the user has all of the permissions, false otherwise
   */
  checkAllPermissions: (permissions: string[]) => boolean;
}

/**
 * Custom hook that provides permission checking functionality throughout the application.
 * Simplifies access control by providing utility functions to check if the current user
 * has specific permissions or roles.
 * 
 * This hook serves as a client-side enforcement point for authorization rules and
 * implements the role-based access control as defined in the security architecture.
 * 
 * @returns Object containing permission checking functions
 * @example
 * const { checkPermission, checkRole } = usePermissions();
 * 
 * // Check if user can view applications
 * const canViewApplications = checkPermission('application:view');
 * 
 * // Check if user is an underwriter
 * const isUnderwriter = checkRole('underwriter');
 */
export function usePermissions(): UsePermissionsReturn {
  // Get authentication state using useAuth hook
  const { state } = useAuth();
  
  /**
   * Checks if the current user has a specific permission
   */
  const checkPermission = useCallback((permission: string): boolean => {
    return hasPermission(state.user, permission);
  }, [state.user]);
  
  /**
   * Checks if the current user has a specific role
   */
  const checkRole = useCallback((role: string): boolean => {
    return hasRole(state.user, role);
  }, [state.user]);
  
  /**
   * Checks if the current user has any of the specified permissions
   */
  const checkAnyPermission = useCallback((permissions: string[]): boolean => {
    if (!state.user) return false;
    return permissions.some(permission => hasPermission(state.user, permission));
  }, [state.user]);
  
  /**
   * Checks if the current user has all of the specified permissions
   */
  const checkAllPermissions = useCallback((permissions: string[]): boolean => {
    if (!state.user) return false;
    return permissions.every(permission => hasPermission(state.user, permission));
  }, [state.user]);
  
  return {
    checkPermission,
    checkRole,
    checkAnyPermission,
    checkAllPermissions
  };
}

export default usePermissions;