/**
 * Common TypeScript types, interfaces, and utility types used throughout the loan management system frontend.
 * Provides foundational type definitions to ensure type safety and consistency across the application.
 */

// Basic type aliases
export type UUID = string;
export type ISO8601Date = string;
export type Currency = number;
export type PhoneNumber = string;
export type EmailAddress = string;
export type SSN = string;

// Common interfaces
export interface Address {
  address_line1: string;
  address_line2: string | null;
  city: string;
  state: string;
  zip_code: string;
}

// Generic interface for paginated API responses
export interface PaginatedResponse<T> {
  results: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Generic interface for API responses
export interface ApiResponse<T> {
  success: boolean;
  message: string | null;
  data: T | null;
  errors: Record<string, string[]> | null;
}

// Enum for sort direction options in list views
export enum SortDirection {
  ASC = 'asc',
  DESC = 'desc'
}

// Enum for action status values used across the application
export enum ActionStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

// Interface for pagination parameters in API requests
export interface PaginationParams {
  page: number;
  page_size: number;
}

// Interface for sorting parameters in API requests
export interface SortParams {
  sort_by: string;
  sort_direction: SortDirection;
}

// Interface for date range filters used in various list views
export interface DateRange {
  start: ISO8601Date | null;
  end: ISO8601Date | null;
}

// Interface for select/dropdown options used in form components
export interface SelectOption {
  value: string | number;
  label: string;
  disabled: boolean;
}

// Interface for error responses from the API
export interface ErrorResponse {
  status: number;
  message: string;
  errors: Record<string, string[]> | null;
}

// Interface for file upload responses
export interface FileUploadResponse {
  file_id: UUID;
  file_name: string;
  file_path: string;
  file_size: number;
  file_type: string;
  upload_date: ISO8601Date;
}

// Interface for field validation errors
export interface ValidationError {
  field: string;
  message: string;
}

// Utility types
export type Nullable<T> = T | null;
export type Optional<T> = T | undefined;
export type Required<T> = { [P in keyof T]-?: T[P] };
export type Partial<T> = { [P in keyof T]?: T[P] };
export type Pick<T, K extends keyof T> = { [P in K]: T[P] };
export type Omit<T, K extends keyof any> = Pick<T, Exclude<keyof T, K>>;