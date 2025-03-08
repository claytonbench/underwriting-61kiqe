import { UUID, ISO8601Date, Currency, Address, PaginatedResponse } from './common.types';

/**
 * Enum representing possible school status values
 */
export enum SchoolStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  PENDING = 'pending_approval',
  REJECTED = 'rejected'
}

/**
 * Enum representing possible program status values
 */
export enum ProgramStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive'
}

/**
 * Enum representing possible school document types
 */
export enum DocumentType {
  ENROLLMENT_AGREEMENT = 'enrollment_agreement',
  ACCREDITATION = 'accreditation',
  CATALOG = 'catalog',
  OTHER = 'other'
}

/**
 * Interface representing a school entity
 */
export interface School {
  id: UUID;
  name: string;
  legal_name: string;
  tax_id: string;
  address_line1: string;
  address_line2: string | null;
  city: string;
  state: string;
  zip_code: string;
  phone: string;
  website: string;
  status: SchoolStatus;
  created_at: ISO8601Date;
  updated_at: ISO8601Date;
}

/**
 * Interface representing detailed school information including related entities
 */
export interface SchoolDetail extends School {
  programs: Program[];
  contacts: SchoolContact[];
  documents: SchoolDocument[];
  application_count: number;
}

/**
 * Interface representing an educational program offered by a school
 */
export interface Program {
  id: UUID;
  school_id: UUID;
  name: string;
  description: string;
  duration_hours: number;
  duration_weeks: number;
  status: ProgramStatus;
  current_tuition: Currency;
  created_at: ISO8601Date;
  updated_at: ISO8601Date;
}

/**
 * Interface representing detailed program information including version history
 */
export interface ProgramDetail extends Program {
  school_name: string;
  versions: ProgramVersion[];
  current_version: ProgramVersion;
  student_count: number;
}

/**
 * Interface representing a specific version of a program with its tuition amount and effective date
 */
export interface ProgramVersion {
  id: UUID;
  program_id: UUID;
  version_number: number;
  effective_date: ISO8601Date;
  tuition_amount: Currency;
  is_current: boolean;
  created_at: ISO8601Date;
}

/**
 * Interface representing a contact person for a school
 */
export interface SchoolContact {
  id: UUID;
  school_id: UUID;
  first_name: string;
  last_name: string;
  title: string;
  email: string;
  phone: string;
  is_primary: boolean;
  can_sign_documents: boolean;
  created_at: ISO8601Date;
  updated_at: ISO8601Date;
}

/**
 * Interface representing a document associated with a school
 */
export interface SchoolDocument {
  id: UUID;
  school_id: UUID;
  document_type: DocumentType;
  file_name: string;
  file_path: string;
  uploaded_at: ISO8601Date;
  uploaded_by: UUID;
  status: string;
  download_url: string | null;
}

/**
 * Interface representing data required to create a new school
 */
export interface SchoolCreateRequest {
  name: string;
  legal_name: string;
  tax_id: string;
  address_line1: string;
  address_line2: string | null;
  city: string;
  state: string;
  zip_code: string;
  phone: string;
  website: string;
  status: SchoolStatus;
}

/**
 * Interface representing data required to update an existing school
 */
export interface SchoolUpdateRequest {
  name: string;
  legal_name: string;
  tax_id: string;
  address_line1: string;
  address_line2: string | null;
  city: string;
  state: string;
  zip_code: string;
  phone: string;
  website: string;
  status: SchoolStatus;
}

/**
 * Interface representing data required to create a new program
 */
export interface ProgramCreateRequest {
  school_id: UUID;
  name: string;
  description: string;
  duration_hours: number;
  duration_weeks: number;
  status: ProgramStatus;
  tuition_amount: Currency;
  effective_date: ISO8601Date;
}

/**
 * Interface representing data required to update an existing program
 */
export interface ProgramUpdateRequest {
  name: string;
  description: string;
  duration_hours: number;
  duration_weeks: number;
  status: ProgramStatus;
}

/**
 * Interface representing data required to create a new program version
 */
export interface ProgramVersionCreateRequest {
  program_id: UUID;
  tuition_amount: Currency;
  effective_date: ISO8601Date;
}

/**
 * Interface representing data required to create a new school contact
 */
export interface SchoolContactCreateRequest {
  school_id: UUID;
  first_name: string;
  last_name: string;
  title: string;
  email: string;
  phone: string;
  is_primary: boolean;
  can_sign_documents: boolean;
}

/**
 * Interface representing data required to update an existing school contact
 */
export interface SchoolContactUpdateRequest {
  first_name: string;
  last_name: string;
  title: string;
  email: string;
  phone: string;
  is_primary: boolean;
  can_sign_documents: boolean;
}

/**
 * Interface representing data required to upload a school document
 */
export interface SchoolDocumentUploadRequest {
  school_id: UUID;
  document_type: DocumentType;
  file: File;
  status: string;
}

/**
 * Interface representing filter options for school lists
 */
export interface SchoolFilters {
  status: SchoolStatus | null;
  name: string | null;
  state: string | null;
}

/**
 * Interface representing filter options for program lists
 */
export interface ProgramFilters {
  status: ProgramStatus | null;
  name: string | null;
  school_id: UUID | null;
}

/**
 * Interface representing a paginated response of schools
 */
export interface SchoolListResponse {
  results: School[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/**
 * Interface representing a paginated response of programs
 */
export interface ProgramListResponse {
  results: Program[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/**
 * Interface representing the school state in Redux store
 */
export interface SchoolState {
  schools: School[];
  selectedSchool: SchoolDetail | null;
  programs: Program[];
  selectedProgram: ProgramDetail | null;
  loading: boolean;
  error: string | null;
  totalSchools: number;
  totalPrograms: number;
  schoolFilters: SchoolFilters;
  programFilters: ProgramFilters;
  page: number;
  pageSize: number;
}