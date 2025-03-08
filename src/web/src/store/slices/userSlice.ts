import { createSlice, PayloadAction } from '@reduxjs/toolkit'; // @reduxjs/toolkit ^1.9.5
import { 
  UserWithProfile, 
  Role, 
  Permission, 
  UserFilters 
} from '../../types/user.types';
import { 
  fetchUsers, 
  fetchUsersBySchool, 
  fetchUser, 
  createNewUser, 
  updateExistingUser, 
  deleteExistingUser, 
  fetchRoles, 
  fetchPermissions, 
  resetPassword, 
  activateExistingUser, 
  deactivateExistingUser, 
  unlockExistingUser, 
  updateUserRoleAssignments,
  setFilters,
  clearUser
} from '../thunks/userThunks';

/**
 * Interface defining the structure of the user state
 */
export interface UserState {
  users: UserWithProfile[];
  selectedUser: UserWithProfile | null;
  roles: Role[];
  permissions: Permission[];
  loading: boolean;
  error: string | null;
  totalUsers: number;
  filters: UserFilters;
}

/**
 * Initial state for the user slice
 */
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
 * Redux Toolkit slice for user management
 */
export const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    /**
     * Sets the currently selected user
     * @param state The current state
     * @param action Payload containing the user to select
     */
    setSelectedUser: (state, action: PayloadAction<UserWithProfile>) => {
      state.selectedUser = action.payload;
    },
    
    /**
     * Clears the currently selected user
     * @param state The current state
     */
    clearSelectedUser: (state) => {
      state.selectedUser = null;
    },
    
    /**
     * Updates the user list filters
     * @param state The current state
     * @param action Payload containing the new filters
     */
    setUserFilters: (state, action: PayloadAction<UserFilters>) => {
      state.filters = action.payload;
    },
    
    /**
     * Resets the user state to initial values
     * @param state The current state
     */
    resetUserState: (state) => {
      state.users = [];
      state.selectedUser = null;
      state.roles = [];
      state.permissions = [];
      state.loading = false;
      state.error = null;
      state.totalUsers = 0;
      state.filters = {
        search: null,
        userType: null,
        isActive: null,
        roleId: null,
        schoolId: null,
        createdAfter: null,
        createdBefore: null,
      };
    }
  },
  extraReducers: (builder) => {
    builder
      // Handle fetchUsers async thunk actions
      .addCase(fetchUsers.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.users = action.payload.users;
        state.totalUsers = action.payload.totalCount;
        state.loading = false;
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch users';
      })

      // Handle fetchUsersBySchool async thunk actions
      .addCase(fetchUsersBySchool.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUsersBySchool.fulfilled, (state, action) => {
        state.users = action.payload.users;
        state.totalUsers = action.payload.totalCount;
        state.loading = false;
      })
      .addCase(fetchUsersBySchool.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch users by school';
      })

      // Handle fetchUser async thunk actions
      .addCase(fetchUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUser.fulfilled, (state, action) => {
        state.selectedUser = action.payload;
        state.loading = false;
      })
      .addCase(fetchUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch user';
      })

      // Handle createNewUser async thunk actions
      .addCase(createNewUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createNewUser.fulfilled, (state, action) => {
        state.users = [...state.users, action.payload];
        state.totalUsers = state.totalUsers + 1;
        state.loading = false;
      })
      .addCase(createNewUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to create user';
      })

      // Handle updateExistingUser async thunk actions
      .addCase(updateExistingUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateExistingUser.fulfilled, (state, action) => {
        state.users = state.users.map(user =>
          user.id === action.payload.id ? action.payload : user
        );
        if (state.selectedUser && state.selectedUser.id === action.payload.id) {
          state.selectedUser = action.payload;
        }
        state.loading = false;
      })
      .addCase(updateExistingUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to update user';
      })

      // Handle deleteExistingUser async thunk actions
      .addCase(deleteExistingUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteExistingUser.fulfilled, (state, action) => {
        const userId = action.payload;
        state.users = state.users.filter(user => user.id !== userId);
        if (state.selectedUser && state.selectedUser.id === userId) {
          state.selectedUser = null;
        }
        state.totalUsers = state.totalUsers - 1;
        state.loading = false;
      })
      .addCase(deleteExistingUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to delete user';
      })

      // Handle fetchRoles async thunk actions
      .addCase(fetchRoles.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRoles.fulfilled, (state, action) => {
        state.roles = action.payload;
        state.loading = false;
      })
      .addCase(fetchRoles.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch roles';
      })

      // Handle fetchPermissions async thunk actions
      .addCase(fetchPermissions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPermissions.fulfilled, (state, action) => {
        state.permissions = action.payload;
        state.loading = false;
      })
      .addCase(fetchPermissions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch permissions';
      })

      // Handle resetPassword async thunk actions
      .addCase(resetPassword.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(resetPassword.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(resetPassword.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to reset password';
      })

      // Handle activateExistingUser async thunk actions
      .addCase(activateExistingUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(activateExistingUser.fulfilled, (state, action) => {
        state.users = state.users.map(user =>
          user.id === action.payload.id ? action.payload : user
        );
        if (state.selectedUser && state.selectedUser.id === action.payload.id) {
          state.selectedUser = action.payload;
        }
        state.loading = false;
      })
      .addCase(activateExistingUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to activate user';
      })

      // Handle deactivateExistingUser async thunk actions
      .addCase(deactivateExistingUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deactivateExistingUser.fulfilled, (state, action) => {
        state.users = state.users.map(user =>
          user.id === action.payload.id ? action.payload : user
        );
        if (state.selectedUser && state.selectedUser.id === action.payload.id) {
          state.selectedUser = action.payload;
        }
        state.loading = false;
      })
      .addCase(deactivateExistingUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to deactivate user';
      })

      // Handle unlockExistingUser async thunk actions
      .addCase(unlockExistingUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(unlockExistingUser.fulfilled, (state, action) => {
        state.users = state.users.map(user =>
          user.id === action.payload.id ? action.payload : user
        );
        if (state.selectedUser && state.selectedUser.id === action.payload.id) {
          state.selectedUser = action.payload;
        }
        state.loading = false;
      })
      .addCase(unlockExistingUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to unlock user';
      })

      // Handle updateUserRoleAssignments async thunk actions
      .addCase(updateUserRoleAssignments.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateUserRoleAssignments.fulfilled, (state, action) => {
        state.users = state.users.map(user =>
          user.id === action.payload.id ? action.payload : user
        );
        if (state.selectedUser && state.selectedUser.id === action.payload.id) {
          state.selectedUser = action.payload;
        }
        state.loading = false;
      })
      .addCase(updateUserRoleAssignments.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to update user roles';
      })
      
      // Handle setFilters async thunk actions
      .addCase(setFilters.fulfilled, (state, action) => {
          state.filters = action.payload;
      })

      // Handle clearUser async thunk actions
      .addCase(clearUser.fulfilled, (state) => {
          state.selectedUser = null;
      });
  }
});

// Extract the action creators from the slice
export const { setSelectedUser, clearSelectedUser, setUserFilters, resetUserState } = userSlice.actions;

// Export the reducer
export default userSlice.reducer;