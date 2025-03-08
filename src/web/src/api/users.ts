import { AxiosRequestConfig } from 'axios'; // axios v1.4.0
import { apiClient, handleApiError, API_BASE_URL } from '../config/api';
import { API_ENDPOINTS } from '../config/constants';
import {
  User,
  UserWithProfile,
  Role,
  Permission,
  UserCreateRequest,
  UserUpdateRequest,
  BorrowerProfileCreateRequest,
  SchoolAdminProfileCreateRequest,
  InternalUserProfileCreateRequest,
  UserFilters,
  PasswordChangeRequest,
  UserResponse,
  UserDetailResponse,
  UsersListResponse,
  RolesResponse,
  RoleResponse,
  PermissionsResponse
} from '../types/user.types';
import { ApiResponse, PaginatedResponse, UUID } from '../types/common.types';
import { UserType } from '../types/auth.types';

/**
 * Fetches a paginated list of users with optional filtering
 * 
 * @param page - Page number to fetch (optional, defaults to 1)
 * @param page_size - Number of items per page (optional, defaults to 10)
 * @param filters - Optional filter criteria for users
 * @returns Promise resolving to paginated user list response
 */
export async function getUsers({
  page = 1,
  page_size = 10,
  filters
}: {
  page?: number;
  page_size?: number;
  filters?: UserFilters;
} = {}): Promise<UsersListResponse> {
  try {
    // Construct query parameters
    const params: Record<string, any> = {
      page,
      page_size
    };

    // Add filters to query parameters if provided
    if (filters) {
      if (filters.search) params.search = filters.search;
      if (filters.userType) params.user_type = filters.userType;
      if (filters.isActive !== null && filters.isActive !== undefined) params.is_active = filters.isActive;
      if (filters.roleId) params.role_id = filters.roleId;
      if (filters.schoolId) params.school_id = filters.schoolId;
      if (filters.createdAfter) params.created_after = filters.createdAfter;
      if (filters.createdBefore) params.created_before = filters.createdBefore;
    }

    const config: AxiosRequestConfig = { params };
    const response = await apiClient.get<UsersListResponse>(API_ENDPOINTS.USERS.BASE, config);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Fetches a single user by ID with profile information
 * 
 * @param id - User ID
 * @returns Promise resolving to user detail response
 */
export async function getUser(id: UUID): Promise<UserDetailResponse> {
  try {
    const response = await apiClient.get<UserDetailResponse>(API_ENDPOINTS.USERS.BY_ID(id));
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Fetches the currently authenticated user's profile
 * 
 * @returns Promise resolving to current user detail response
 */
export async function getCurrentUser(): Promise<UserDetailResponse> {
  try {
    const response = await apiClient.get<UserDetailResponse>(`${API_ENDPOINTS.USERS.BASE}/me`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Creates a new user with specified type and profile data
 * 
 * @param data - User creation request data
 * @returns Promise resolving to created user data
 */
export async function createUser(data: UserCreateRequest): Promise<UserResponse> {
  try {
    const response = await apiClient.post<UserResponse>(API_ENDPOINTS.USERS.BASE, data);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Updates an existing user's information
 * 
 * @param id - User ID
 * @param data - User update request data
 * @returns Promise resolving to updated user data
 */
export async function updateUser(id: UUID, data: UserUpdateRequest): Promise<UserResponse> {
  try {
    const response = await apiClient.put<UserResponse>(API_ENDPOINTS.USERS.BY_ID(id), data);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Deletes a user (soft delete by setting isActive to false)
 * 
 * @param id - User ID
 * @returns Promise resolving when user is deleted
 */
export async function deleteUser(id: UUID): Promise<ApiResponse<void>> {
  try {
    const response = await apiClient.delete<ApiResponse<void>>(API_ENDPOINTS.USERS.BY_ID(id));
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Changes the password for the current user
 * 
 * @param data - Password change request data
 * @returns Promise resolving when password is changed
 */
export async function changePassword(data: PasswordChangeRequest): Promise<ApiResponse<void>> {
  try {
    const response = await apiClient.post<ApiResponse<void>>(API_ENDPOINTS.USERS.UPDATE_PASSWORD, data);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Initiates a password reset for a user (admin function)
 * 
 * @param id - User ID
 * @returns Promise resolving when password reset is initiated
 */
export async function resetUserPassword(id: UUID): Promise<ApiResponse<void>> {
  try {
    const response = await apiClient.post<ApiResponse<void>>(`${API_ENDPOINTS.USERS.BY_ID(id)}/reset-password`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Fetches users associated with a specific school
 * 
 * @param schoolId - School ID
 * @param page - Page number to fetch (optional, defaults to 1)
 * @param page_size - Number of items per page (optional, defaults to 10)
 * @param filters - Optional filter criteria for users
 * @returns Promise resolving to paginated user list response
 */
export async function getUsersBySchool(
  schoolId: UUID,
  {
    page = 1,
    page_size = 10,
    filters
  }: {
    page?: number;
    page_size?: number;
    filters?: UserFilters;
  } = {}
): Promise<UsersListResponse> {
  try {
    // Construct query parameters
    const params: Record<string, any> = {
      page,
      page_size
    };

    // Add filters to query parameters if provided
    if (filters) {
      if (filters.search) params.search = filters.search;
      if (filters.userType) params.user_type = filters.userType;
      if (filters.isActive !== null && filters.isActive !== undefined) params.is_active = filters.isActive;
      if (filters.roleId) params.role_id = filters.roleId;
      if (filters.createdAfter) params.created_after = filters.createdAfter;
      if (filters.createdBefore) params.created_before = filters.createdBefore;
    }

    const config: AxiosRequestConfig = { params };
    const response = await apiClient.get<UsersListResponse>(`/schools/${schoolId}/users`, config);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Fetches all available roles in the system
 * 
 * @returns Promise resolving to roles list response
 */
export async function getRoles(): Promise<RolesResponse> {
  try {
    const response = await apiClient.get<RolesResponse>('/roles');
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Fetches a single role by ID with associated permissions
 * 
 * @param id - Role ID
 * @returns Promise resolving to role detail response
 */
export async function getRole(id: UUID): Promise<RoleResponse> {
  try {
    const response = await apiClient.get<RoleResponse>(`/roles/${id}`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Creates a new role with specified permissions
 * 
 * @param name - Role name
 * @param description - Role description
 * @param permissionIds - Array of permission IDs to associate with the role
 * @returns Promise resolving to created role data
 */
export async function createRole({
  name,
  description,
  permissionIds
}: {
  name: string;
  description: string;
  permissionIds: UUID[];
}): Promise<RoleResponse> {
  try {
    const response = await apiClient.post<RoleResponse>('/roles', {
      name,
      description,
      permission_ids: permissionIds
    });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Updates an existing role's information and permissions
 * 
 * @param id - Role ID
 * @param name - Role name (optional)
 * @param description - Role description (optional)
 * @param permissionIds - Array of permission IDs to associate with the role (optional)
 * @returns Promise resolving to updated role data
 */
export async function updateRole(
  id: UUID,
  {
    name,
    description,
    permissionIds
  }: {
    name?: string;
    description?: string;
    permissionIds?: UUID[];
  }
): Promise<RoleResponse> {
  try {
    const data: Record<string, any> = {};
    if (name !== undefined) data.name = name;
    if (description !== undefined) data.description = description;
    if (permissionIds !== undefined) data.permission_ids = permissionIds;

    const response = await apiClient.put<RoleResponse>(`/roles/${id}`, data);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Deletes a role from the system
 * 
 * @param id - Role ID
 * @returns Promise resolving when role is deleted
 */
export async function deleteRole(id: UUID): Promise<ApiResponse<void>> {
  try {
    const response = await apiClient.delete<ApiResponse<void>>(`/roles/${id}`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Fetches all available permissions in the system
 * 
 * @returns Promise resolving to permissions list response
 */
export async function getPermissions(): Promise<PermissionsResponse> {
  try {
    const response = await apiClient.get<PermissionsResponse>('/permissions');
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Assigns roles to a user
 * 
 * @param userId - User ID
 * @param roleIds - Array of role IDs to assign
 * @returns Promise resolving to updated user detail response
 */
export async function assignRolesToUser(userId: UUID, roleIds: UUID[]): Promise<UserDetailResponse> {
  try {
    const response = await apiClient.post<UserDetailResponse>(`${API_ENDPOINTS.USERS.BY_ID(userId)}/roles`, {
      role_ids: roleIds
    });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Removes a role from a user
 * 
 * @param userId - User ID
 * @param roleId - Role ID to remove
 * @returns Promise resolving to updated user detail response
 */
export async function removeRoleFromUser(userId: UUID, roleId: UUID): Promise<UserDetailResponse> {
  try {
    const response = await apiClient.delete<UserDetailResponse>(`${API_ENDPOINTS.USERS.BY_ID(userId)}/roles/${roleId}`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
}