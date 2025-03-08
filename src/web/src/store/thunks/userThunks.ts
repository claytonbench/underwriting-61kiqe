# src/web/src/store/thunks/userThunks.ts
```typescript
import { createAsyncThunk } from '@reduxjs/toolkit'; // @reduxjs/toolkit ^1.9.5
import { RootState, AppDispatch } from '../index';
import { 
  UserWithProfile, 
  UserCreateRequest, 
  UserUpdateRequest, 
  UserFilters, 
  Role, 
  Permission 
} from '../../types/user.types';
import { 
  getUsers, 
  getUser, 
  getUsersBySchool, 
  createUser, 
  updateUser, 
  deleteUser, 
  resetUserPassword, 
  getRoles, 
  getPermissions, 
  assignRolesToUser, 
  removeRoleFromUser 
} from '../../api/users';

/**
 * Async thunk to fetch a paginated list of users with optional filtering
 */
export const fetchUsers = createAsyncThunk<
  { users: UserWithProfile[]; totalCount: number },
  { page?: number; pageSize?: number; filters?: UserFilters },
  { state: RootState; dispatch: AppDispatch }
>(
  'users/fetchUsers',
  async ({ page = 1, pageSize = 10, filters }, { rejectWithValue }) => {
    try {
      const response = await getUsers({ page, page_size: pageSize, filters });
      if (!response.success) {
        return rejectWithValue(response.message || 'Failed to fetch users');
      }
      return { users: response.data.results, totalCount: response.data.total };
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

/**
 * Async thunk to fetch users associated with a specific school
 */
export const fetchUsersBySchool = createAsyncThunk<
  { users: UserWithProfile[]; totalCount: number },
  { schoolId: string; page?: number; pageSize?: number; filters?: UserFilters },
  { state: RootState; dispatch: AppDispatch }
>(
  'users/fetchUsersBySchool',
  async ({ schoolId, page = 1, pageSize = 10, filters }, { rejectWithValue }) => {
    try {
      const response = await getUsersBySchool(schoolId, { page, page_size: pageSize, filters });
      if (!response.success) {
        return rejectWithValue(response.message || 'Failed to fetch users by school');
      }
      return { users: response.data.results, totalCount: response.data.total };
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

/**
 * Async thunk to fetch a single user by ID
 */
export const fetchUser = createAsyncThunk<
  UserWithProfile,
  string,
  { state: RootState; dispatch: AppDispatch }
>(
  'users/fetchUser',
  async (userId, { rejectWithValue }) => {
    try {
      const response = await getUser(userId);
      if (!response.success) {
        return rejectWithValue(response.message || 'Failed to fetch user');
      }
      return response.data;
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

/**
 * Async thunk to create a new user
 */
export const createNewUser = createAsyncThunk<
  UserWithProfile,
  UserCreateRequest,
  { state: RootState; dispatch: AppDispatch }
>(
  'users/createNewUser',
  async (userData, { rejectWithValue }) => {
    try {
      const response = await createUser(userData);
      if (!response.success) {
        return rejectWithValue(response.message || 'Failed to create user');
      }
      return response.data;
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

/**
 * Async thunk to update an existing user
 */
export const updateExistingUser = createAsyncThunk<
  UserWithProfile,
  { userId: string; userData: UserUpdateRequest },
  { state: RootState; dispatch: AppDispatch }
>(
  'users/updateExistingUser',
  async ({ userId, userData }, { rejectWithValue }) => {
    try {
      const response = await updateUser(userId, userData);
      if (!response.success) {
        return rejectWithValue(response.message || 'Failed to update user');
      }
      return response.data;
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

/**
 * Async thunk to delete a user
 */
export const deleteExistingUser = createAsyncThunk<
  string,
  string,
  { state: RootState; dispatch: AppDispatch }
>(
  'users/deleteExistingUser',
  async (userId, { rejectWithValue }) => {
    try {
      const response = await deleteUser(userId);
      if (!response.success) {
        return rejectWithValue(response.message || 'Failed to delete user');
      }
      return userId;
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

/**
 * Async thunk to reset a user's password (admin function)
 */
export const resetPassword = createAsyncThunk<
  void,
  string,
  { state: RootState; dispatch: AppDispatch }
>(
  'users/resetPassword',
  async (userId, { rejectWithValue }) => {
    try {
      const response = await resetUserPassword(userId);
      if (!response.success) {
        return rejectWithValue(response.message || 'Failed to reset password');
      }
      return;
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

/**
 * Async thunk to activate a deactivated user
 */
export const activateExistingUser = createAsyncThunk<
  UserWithProfile,
  string,
  { state: RootState; dispatch: AppDispatch }
>(
  'users/activateExistingUser',
  async (userId, { rejectWithValue }) => {
    try {
      const response = await updateUser(userId, { isActive: true } as UserUpdateRequest);
      if (!response.success) {
        return rejectWithValue(response.message || 'Failed to activate user');
      }
      return response.data;
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

/**
 * Async thunk to deactivate an active user
 */
export const deactivateExistingUser = createAsyncThunk<
  UserWithProfile,
  string,
  { state: RootState; dispatch: AppDispatch }
>(
  'users/deactivateExistingUser',
  async (userId, { rejectWithValue }) => {
    try {
      const response = await updateUser(userId, { isActive: false } as UserUpdateRequest);
      if (!response.success) {
        return rejectWithValue(response.message || 'Failed to deactivate user');
      }
      return response.data;
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

/**
 * Async thunk to unlock a locked user account
 */
export const unlockExistingUser = createAsyncThunk<
  UserWithProfile,
  string,
  { state: RootState; dispatch: AppDispatch }
>(
  'users/unlockExistingUser',
  async (userId, { rejectWithValue }) => {
    try {
      const response = await updateUser(userId, { /* Add unlock data if needed */ } as UserUpdateRequest);
      if (!response.success) {
        return rejectWithValue(response.message || 'Failed to unlock user');
      }
      return response.data;
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

/**
 * Async thunk to fetch all available roles
 */
export const fetchRoles = createAsyncThunk<
  Role[],
  void,
  { state: RootState; dispatch: AppDispatch }
>(
  'users/fetchRoles',
  async (_, { rejectWithValue }) => {
    try {
      const response = await getRoles();
      if (!response.success) {
        return rejectWithValue(response.message || 'Failed to fetch roles');
      }
      return response.data;
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

/**
 * Async thunk to fetch all available permissions
 */
export const fetchPermissions = createAsyncThunk<
  Permission[],
  void,
  { state: RootState; dispatch: AppDispatch }
>(
  'users/fetchPermissions',
  async (_, { rejectWithValue }) => {
    try {
      const response = await getPermissions();
      if (!response.success) {
        return rejectWithValue(response.message || 'Failed to fetch permissions');
      }
      return response.data;
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

/**
 * Async thunk to update a user's role assignments
 */
export const updateUserRoleAssignments = createAsyncThunk<
  UserWithProfile,
  { userId: string; roleIds: string[] },
  { state: RootState; dispatch: AppDispatch }
>(
  'users/updateUserRoleAssignments',
  async ({ userId, roleIds }, { rejectWithValue }) => {
    try {
      const response = await assignRolesToUser(userId, roleIds);
      if (!response.success) {
        return rejectWithValue(response.message || 'Failed to update user roles');
      }
      return response.data;
    } catch (error) {
      return rejectWithValue((error as Error).message);
    }
  }
);

/**
 * Async thunk to update user list filters
 */
export const setFilters = createAsyncThunk<
  UserFilters,
  UserFilters,
  { state: RootState; dispatch: AppDispatch }
>(
  'users/setFilters',
  async (filters) => {
    return filters;
  }
);

/**
 * Async thunk to clear the selected user
 */
export const clearUser = createAsyncThunk<
  void,
  void,
  { state: RootState; dispatch: AppDispatch }
>(
  'users/clearUser',
  async () => {
    return;
  }
);