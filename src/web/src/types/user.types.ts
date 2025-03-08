/**
 * User-related TypeScript type definitions for the loan management system.
 * 
 * This file contains interfaces and types for user profiles, roles, permissions,
 * and request/response structures related to user management. These types support
 * the comprehensive user management system with role-based access control as
 * described in the technical specifications.
 */

import { 
  UUID, 
  ISO8601Date, 
  EmailAddress, 
  PhoneNumber, 
  Address, 
  ApiResponse, 
  PaginatedResponse 
} from './common.types';
import { UserType } from './auth.types';

/**
 * Core user interface representing basic user information
 */
export interface User {
  id: UUID;
  firstName: string;
  lastName: string;
  email: EmailAddress;
  phone: PhoneNumber;
  userType: UserType;
  isActive: boolean;
  createdAt: ISO8601Date;
  updatedAt: ISO8601Date;
  lastLogin: ISO8601Date | null;
}

/**
 * Interface for borrower-specific profile information
 */
export interface BorrowerProfile {
  id: UUID;
  userId: UUID;
  ssn: string; // Masked in UI except for authorized users
  dob: ISO8601Date;
  citizenshipStatus: string;
  address: Address;
  housingStatus: string;
  housingPayment: number;
  
  // Computed properties
  fullAddress: string; // Formatted full address string
  age: number; // Computed from DOB
}

/**
 * Interface for borrower employment and income information
 */
export interface EmploymentInfo {
  id: UUID;
  profileId: UUID;
  employmentType: string;
  employerName: string;
  occupation: string;
  employerPhone: PhoneNumber;
  yearsEmployed: number;
  monthsEmployed: number;
  annualIncome: number;
  otherIncome: number;
  otherIncomeSource: string;
  
  // Computed properties
  totalIncome: number; // annualIncome + otherIncome
  monthlyIncome: number; // totalIncome / 12
  totalEmploymentDuration: number; // years + months/12 (in years)
}

/**
 * Interface for school administrator profile information
 */
export interface SchoolAdminProfile {
  id: UUID;
  userId: UUID;
  schoolId: UUID;
  schoolName: string; // May be populated from related data
  title: string;
  department: string;
  isPrimaryContact: boolean;
  canSignDocuments: boolean;
}

/**
 * Interface for internal staff profile information (underwriters, QC, system admins)
 */
export interface InternalUserProfile {
  id: UUID;
  userId: UUID;
  employeeId: string;
  department: string;
  title: string;
  supervisorId: UUID | null;
  supervisorName: string | null; // May be populated from related data
}

/**
 * Union type for all possible user profile types
 */
export type UserProfile = BorrowerProfile | SchoolAdminProfile | InternalUserProfile;

/**
 * Extended user interface that includes profile information, employment data, roles, and permissions
 */
export interface UserWithProfile extends User {
  profile: UserProfile | null;
  employmentInfo: EmploymentInfo | null;
  roles: Role[];
  permissions: string[];
}

/**
 * Interface for user role information
 */
export interface Role {
  id: UUID;
  name: string;
  description: string;
  permissions: Permission[];
  permissionsCount: number; // Computed field
  createdAt: ISO8601Date;
  updatedAt: ISO8601Date;
}

/**
 * Interface for permission information
 */
export interface Permission {
  id: UUID;
  name: string;
  description: string;
  resourceType: string;
}

/**
 * Interface for user creation request data
 */
export interface UserCreateRequest {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  phone: string;
  userType: UserType;
  isActive: boolean;
  profileData: Record<string, any>; // Type depends on userType
  roleIds: string[];
}

/**
 * Interface for user update request data
 */
export interface UserUpdateRequest {
  firstName: string;
  lastName: string;
  phone: string;
  isActive: boolean;
  profileData: Record<string, any>; // Type depends on userType
}

/**
 * Interface for borrower profile creation request data
 */
export interface BorrowerProfileCreateRequest {
  ssn: string;
  dob: string; // ISO8601 format
  citizenshipStatus: string;
  addressLine1: string;
  addressLine2: string | null;
  city: string;
  state: string;
  zipCode: string;
  housingStatus: string;
  housingPayment: number;
  employmentInfo: EmploymentInfoCreateRequest;
}

/**
 * Interface for employment information creation request data
 */
export interface EmploymentInfoCreateRequest {
  employmentType: string;
  employerName: string;
  occupation: string;
  employerPhone: string;
  yearsEmployed: number;
  monthsEmployed: number;
  annualIncome: number;
  otherIncome: number;
  otherIncomeSource: string;
}

/**
 * Interface for school administrator profile creation request data
 */
export interface SchoolAdminProfileCreateRequest {
  schoolId: string;
  title: string;
  department: string;
  isPrimaryContact: boolean;
  canSignDocuments: boolean;
}

/**
 * Interface for internal user profile creation request data
 */
export interface InternalUserProfileCreateRequest {
  employeeId: string;
  department: string;
  title: string;
  supervisorId: string | null;
}

/**
 * Interface for user filtering options in list views
 */
export interface UserFilters {
  search: string | null;
  userType: UserType | null;
  isActive: boolean | null;
  roleId: string | null;
  schoolId: string | null;
  createdAfter: string | null;
  createdBefore: string | null;
}

/**
 * Interface for password change request data
 */
export interface PasswordChangeRequest {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

/**
 * Type alias for API response containing user data
 */
export type UserResponse = ApiResponse<User>;

/**
 * Type alias for API response containing detailed user data
 */
export type UserDetailResponse = ApiResponse<UserWithProfile>;

/**
 * Type alias for API response containing paginated user list
 */
export type UsersListResponse = ApiResponse<PaginatedResponse<UserWithProfile>>;

/**
 * Type alias for API response containing roles data
 */
export type RolesResponse = ApiResponse<Role[]>;

/**
 * Type alias for API response containing single role data
 */
export type RoleResponse = ApiResponse<Role>;

/**
 * Type alias for API response containing permissions data
 */
export type PermissionsResponse = ApiResponse<Permission[]>;