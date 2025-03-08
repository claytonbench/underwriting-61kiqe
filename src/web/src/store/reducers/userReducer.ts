/**
 * Redux reducer for managing user state in the loan management system
 * 
 * This reducer handles state management for the comprehensive user management system,
 * supporting operations for users, roles, and permissions. It enables functionalities
 * such as user creation, updating, deletion, role assignment, and permission management.
 * 
 * The reducer responds to various actions to update the application state, including:
 * - User list operations (fetch, filter)
 * - Individual user operations (create, read, update, delete)
 * - Role and permission management
 * - User account actions (activate, deactivate, unlock, reset password)
 */

import { AnyAction } from 'redux'; // v4.2.1
import {
  UserState,
  UserWithProfile,
  Role,
  Permission,
  UserFilters
} from '../../types/user.types';
import {
  getUsersRequest,
  getUsersSuccess,
  getUsersFailure,
  getUserRequest,
  getUserSuccess,
  getUserFailure,
  createUserRequest,
  createUserSuccess,
  createUserFailure,
  updateUserRequest,
  updateUserSuccess,
  updateUserFailure,
  deleteUserRequest,
  deleteUserSuccess,
  deleteUserFailure,
  getRolesRequest,
  getRolesSuccess,
  getRolesFailure,
  getPermissionsRequest,
  getPermissionsSuccess,
  getPermissionsFailure,
  resetPasswordRequest,
  resetPasswordSuccess,
  resetPasswordFailure,
  activateUserRequest,
  activateUserSuccess,
  activateUserFailure,
  deactivateUserRequest,
  deactivateUserSuccess,
  deactivateUserFailure,
  unlockUserRequest,
  unlockUserSuccess,
  unlockUserFailure,
  updateUserRolesRequest,
  updateUserRolesSuccess,
  updateUserRolesFailure,
  setUserFilters,
  clearSelectedUser
} from '../actions/userActions';

// Define the initial state
const initialState: UserState = {
  users: [],
  selectedUser: null,
  roles: [],
  permissions: [],
  loading: false,
  error: null,
  totalUsers: 0,
  filters: {
    search: null,
    userType: null,
    isActive: null,
    roleId: null,
    schoolId: null,
    createdAfter: null,
    createdBefore: null,
  }
};

/**
 * Reducer function for managing user state in the Redux store
 * 
 * Handles user-related actions including fetching, creating, updating, and deleting users,
 * as well as role and permission management for the user management interface.
 * 
 * @param state The current user state
 * @param action The dispatched action
 * @returns The updated user state
 */
const userReducer = (state: UserState = initialState, action: AnyAction): UserState => {
  // Handle user listing actions
  if (getUsersRequest.match(action)) {
    return {
      ...state,
      loading: true,
      error: null
    };
  }

  if (getUsersSuccess.match(action)) {
    return {
      ...state,
      users: action.payload.users,
      totalUsers: action.payload.total,
      loading: false,
      error: null
    };
  }

  if (getUsersFailure.match(action)) {
    return {
      ...state,
      loading: false,
      error: action.payload
    };
  }

  // Handle single user fetch actions
  if (getUserRequest.match(action)) {
    return {
      ...state,
      loading: true,
      error: null
    };
  }

  if (getUserSuccess.match(action)) {
    return {
      ...state,
      selectedUser: action.payload,
      loading: false,
      error: null
    };
  }

  if (getUserFailure.match(action)) {
    return {
      ...state,
      loading: false,
      error: action.payload
    };
  }

  // Handle user creation actions
  if (createUserRequest.match(action)) {
    return {
      ...state,
      loading: true,
      error: null
    };
  }

  if (createUserSuccess.match(action)) {
    return {
      ...state,
      users: [...state.users, action.payload],
      totalUsers: state.totalUsers + 1,
      loading: false,
      error: null
    };
  }

  if (createUserFailure.match(action)) {
    return {
      ...state,
      loading: false,
      error: action.payload
    };
  }

  // Handle user update actions
  if (updateUserRequest.match(action)) {
    return {
      ...state,
      loading: true,
      error: null
    };
  }

  if (updateUserSuccess.match(action)) {
    const updatedUsers = state.users.map(user => 
      user.id === action.payload.id ? action.payload : user
    );
    
    return {
      ...state,
      users: updatedUsers,
      selectedUser: state.selectedUser && state.selectedUser.id === action.payload.id 
        ? action.payload 
        : state.selectedUser,
      loading: false,
      error: null
    };
  }

  if (updateUserFailure.match(action)) {
    return {
      ...state,
      loading: false,
      error: action.payload
    };
  }

  // Handle user deletion actions
  if (deleteUserRequest.match(action)) {
    return {
      ...state,
      loading: true,
      error: null
    };
  }

  if (deleteUserSuccess.match(action)) {
    const userId = action.payload;
    const filteredUsers = state.users.filter(user => user.id !== userId);
    
    return {
      ...state,
      users: filteredUsers,
      selectedUser: state.selectedUser && state.selectedUser.id === userId 
        ? null 
        : state.selectedUser,
      totalUsers: state.totalUsers - 1,
      loading: false,
      error: null
    };
  }

  if (deleteUserFailure.match(action)) {
    return {
      ...state,
      loading: false,
      error: action.payload
    };
  }

  // Handle role management actions
  if (getRolesRequest.match(action)) {
    return {
      ...state,
      loading: true,
      error: null
    };
  }

  if (getRolesSuccess.match(action)) {
    return {
      ...state,
      roles: action.payload,
      loading: false,
      error: null
    };
  }

  if (getRolesFailure.match(action)) {
    return {
      ...state,
      loading: false,
      error: action.payload
    };
  }

  // Handle permission management actions
  if (getPermissionsRequest.match(action)) {
    return {
      ...state,
      loading: true,
      error: null
    };
  }

  if (getPermissionsSuccess.match(action)) {
    return {
      ...state,
      permissions: action.payload,
      loading: false,
      error: null
    };
  }

  if (getPermissionsFailure.match(action)) {
    return {
      ...state,
      loading: false,
      error: action.payload
    };
  }

  // Handle password reset actions
  if (resetPasswordRequest.match(action)) {
    return {
      ...state,
      loading: true,
      error: null
    };
  }

  if (resetPasswordSuccess.match(action)) {
    return {
      ...state,
      loading: false,
      error: null
    };
  }

  if (resetPasswordFailure.match(action)) {
    return {
      ...state,
      loading: false,
      error: action.payload
    };
  }

  // Handle user activation actions
  if (activateUserRequest.match(action)) {
    return {
      ...state,
      loading: true,
      error: null
    };
  }

  if (activateUserSuccess.match(action)) {
    const updatedUsers = state.users.map(user => 
      user.id === action.payload.id ? action.payload : user
    );
    
    return {
      ...state,
      users: updatedUsers,
      selectedUser: state.selectedUser && state.selectedUser.id === action.payload.id 
        ? action.payload 
        : state.selectedUser,
      loading: false,
      error: null
    };
  }

  if (activateUserFailure.match(action)) {
    return {
      ...state,
      loading: false,
      error: action.payload
    };
  }

  // Handle user deactivation actions
  if (deactivateUserRequest.match(action)) {
    return {
      ...state,
      loading: true,
      error: null
    };
  }

  if (deactivateUserSuccess.match(action)) {
    const updatedUsers = state.users.map(user => 
      user.id === action.payload.id ? action.payload : user
    );
    
    return {
      ...state,
      users: updatedUsers,
      selectedUser: state.selectedUser && state.selectedUser.id === action.payload.id 
        ? action.payload 
        : state.selectedUser,
      loading: false,
      error: null
    };
  }

  if (deactivateUserFailure.match(action)) {
    return {
      ...state,
      loading: false,
      error: action.payload
    };
  }

  // Handle user unlock actions
  if (unlockUserRequest.match(action)) {
    return {
      ...state,
      loading: true,
      error: null
    };
  }

  if (unlockUserSuccess.match(action)) {
    const updatedUsers = state.users.map(user => 
      user.id === action.payload.id ? action.payload : user
    );
    
    return {
      ...state,
      users: updatedUsers,
      selectedUser: state.selectedUser && state.selectedUser.id === action.payload.id 
        ? action.payload 
        : state.selectedUser,
      loading: false,
      error: null
    };
  }

  if (unlockUserFailure.match(action)) {
    return {
      ...state,
      loading: false,
      error: action.payload
    };
  }

  // Handle user roles update actions
  if (updateUserRolesRequest.match(action)) {
    return {
      ...state,
      loading: true,
      error: null
    };
  }

  if (updateUserRolesSuccess.match(action)) {
    const updatedUsers = state.users.map(user => 
      user.id === action.payload.id ? action.payload : user
    );
    
    return {
      ...state,
      users: updatedUsers,
      selectedUser: state.selectedUser && state.selectedUser.id === action.payload.id 
        ? action.payload 
        : state.selectedUser,
      loading: false,
      error: null
    };
  }

  if (updateUserRolesFailure.match(action)) {
    return {
      ...state,
      loading: false,
      error: action.payload
    };
  }

  // Handle user filtering actions
  if (setUserFilters.match(action)) {
    return {
      ...state,
      filters: action.payload
    };
  }

  // Handle clear selected user action
  if (clearSelectedUser.match(action)) {
    return {
      ...state,
      selectedUser: null
    };
  }

  // Return current state for unhandled actions
  return state;
};

export default userReducer;