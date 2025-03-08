/**
 * Redux action creators for user management operations in the loan management system.
 * 
 * These action creators define the available actions for user management including 
 * fetching, creating, updating, and deleting users as well as managing roles and permissions.
 * They support the comprehensive user management system with role-based access control.
 */

import { createAction } from '@reduxjs/toolkit'; // v1.9.5
import { UserWithProfile, Role, Permission, UserFilters } from '../../types/user.types';

// User list actions
export const getUsersRequest = createAction('users/getUsersRequest');
export const getUsersSuccess = createAction<{ users: UserWithProfile[]; total: number }>('users/getUsersSuccess');
export const getUsersFailure = createAction<string>('users/getUsersFailure');

// Single user actions
export const getUserRequest = createAction('users/getUserRequest');
export const getUserSuccess = createAction<UserWithProfile>('users/getUserSuccess');
export const getUserFailure = createAction<string>('users/getUserFailure');

// User creation actions
export const createUserRequest = createAction('users/createUserRequest');
export const createUserSuccess = createAction<UserWithProfile>('users/createUserSuccess');
export const createUserFailure = createAction<string>('users/createUserFailure');

// User update actions
export const updateUserRequest = createAction('users/updateUserRequest');
export const updateUserSuccess = createAction<UserWithProfile>('users/updateUserSuccess');
export const updateUserFailure = createAction<string>('users/updateUserFailure');

// User deletion actions
export const deleteUserRequest = createAction('users/deleteUserRequest');
export const deleteUserSuccess = createAction<string>('users/deleteUserSuccess');
export const deleteUserFailure = createAction<string>('users/deleteUserFailure');

// Role management actions
export const getRolesRequest = createAction('users/getRolesRequest');
export const getRolesSuccess = createAction<Role[]>('users/getRolesSuccess');
export const getRolesFailure = createAction<string>('users/getRolesFailure');

// Permission management actions
export const getPermissionsRequest = createAction('users/getPermissionsRequest');
export const getPermissionsSuccess = createAction<Permission[]>('users/getPermissionsSuccess');
export const getPermissionsFailure = createAction<string>('users/getPermissionsFailure');

// Password reset actions
export const resetPasswordRequest = createAction('users/resetPasswordRequest');
export const resetPasswordSuccess = createAction('users/resetPasswordSuccess');
export const resetPasswordFailure = createAction<string>('users/resetPasswordFailure');

// User activation actions
export const activateUserRequest = createAction('users/activateUserRequest');
export const activateUserSuccess = createAction<UserWithProfile>('users/activateUserSuccess');
export const activateUserFailure = createAction<string>('users/activateUserFailure');

// User deactivation actions
export const deactivateUserRequest = createAction('users/deactivateUserRequest');
export const deactivateUserSuccess = createAction<UserWithProfile>('users/deactivateUserSuccess');
export const deactivateUserFailure = createAction<string>('users/deactivateUserFailure');

// User unlocking actions
export const unlockUserRequest = createAction('users/unlockUserRequest');
export const unlockUserSuccess = createAction<UserWithProfile>('users/unlockUserSuccess');
export const unlockUserFailure = createAction<string>('users/unlockUserFailure');

// User roles update actions
export const updateUserRolesRequest = createAction('users/updateUserRolesRequest');
export const updateUserRolesSuccess = createAction<UserWithProfile>('users/updateUserRolesSuccess');
export const updateUserRolesFailure = createAction<string>('users/updateUserRolesFailure');

// User filtering actions
export const setUserFilters = createAction<UserFilters>('users/setUserFilters');

// Clear selected user action
export const clearSelectedUser = createAction('users/clearSelectedUser');