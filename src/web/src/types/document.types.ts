/**
 * TypeScript interfaces and types for document management in the loan management system.
 * 
 * Defines data structures for documents, document packages, signature requests, and 
 * related types needed for document generation, storage, and e-signature workflows.
 */

import { 
  UUID, 
  ISO8601Date, 
  PaginatedResponse, 
  SortDirection 
} from './common.types';
import { ApplicationStatus } from './application.types';
import { UserType } from './auth.types';

/**
 * Types of documents supported in the system
 */
export enum DocumentType {
  COMMITMENT_LETTER = 'commitment_letter',
  LOAN_AGREEMENT = 'loan_agreement',
  DISCLOSURE_FORM = 'disclosure_form',
  PROMISSORY_NOTE = 'promissory_note',
  TRUTH_IN_LENDING = 'truth_in_lending',
  ENROLLMENT_AGREEMENT = 'enrollment_agreement',
  IDENTIFICATION = 'identification',
  INCOME_VERIFICATION = 'income_verification',
  OTHER = 'other'
}

/**
 * Possible statuses for documents in the system
 */
export enum DocumentStatus {
  DRAFT = 'draft',
  GENERATED = 'generated',
  PENDING_SIGNATURE = 'pending_signature',
  PARTIALLY_SIGNED = 'partially_signed',
  COMPLETED = 'completed',
  EXPIRED = 'expired',
  REJECTED = 'rejected',
  ERROR = 'error'
}

/**
 * Types of document packages that can be created
 */
export enum DocumentPackageType {
  APPROVAL = 'approval',
  LOAN_DOCUMENTS = 'loan_documents',
  SUPPORTING_DOCUMENTS = 'supporting_documents',
  FUNDING = 'funding'
}

/**
 * Possible statuses for document packages
 */
export enum DocumentPackageStatus {
  DRAFT = 'draft',
  PENDING_SIGNATURE = 'pending_signature',
  PARTIALLY_SIGNED = 'partially_signed',
  COMPLETED = 'completed',
  EXPIRED = 'expired',
  REJECTED = 'rejected'
}

/**
 * Possible statuses for signature requests
 */
export enum SignatureRequestStatus {
  PENDING = 'pending',
  COMPLETED = 'completed',
  DECLINED = 'declined',
  EXPIRED = 'expired'
}

/**
 * Types of entities that can sign documents
 */
export enum SignerType {
  BORROWER = 'borrower',
  CO_BORROWER = 'co_borrower',
  SCHOOL = 'school',
  LENDER = 'lender'
}

/**
 * Interface representing a document in the system
 */
export interface Document {
  id: UUID;
  package_id: UUID | null;
  document_type: DocumentType;
  file_name: string;
  file_path: string;
  version: string;
  status: DocumentStatus;
  generated_at: ISO8601Date;
  generated_by: UUID;
  application_id: UUID | null;
  download_url: string | null;
  signature_requests: SignatureRequest[];
}

/**
 * Interface representing a package of related documents
 */
export interface DocumentPackage {
  id: UUID;
  application_id: UUID;
  package_type: DocumentPackageType;
  status: DocumentPackageStatus;
  created_at: ISO8601Date;
  expiration_date: ISO8601Date | null;
  documents: Document[];
}

/**
 * Interface representing a field within a document
 */
export interface DocumentField {
  id: UUID;
  document_id: UUID;
  field_name: string;
  field_type: string;
  field_value: string;
  x_position: number;
  y_position: number;
  page_number: number;
}

/**
 * Interface representing a request for document signature
 */
export interface SignatureRequest {
  id: UUID;
  document_id: UUID;
  signer_id: UUID;
  signer_type: SignerType;
  signer_name: string;
  signer_email: string;
  status: SignatureRequestStatus;
  requested_at: ISO8601Date;
  completed_at: ISO8601Date | null;
  reminder_count: number;
  last_reminder_at: ISO8601Date | null;
  external_reference: string | null;
  decline_reason: string | null;
}

/**
 * Interface representing a simplified document for list views
 */
export interface DocumentListItem {
  id: UUID;
  document_type: DocumentType;
  file_name: string;
  status: DocumentStatus;
  generated_at: ISO8601Date;
  application_id: UUID | null;
  borrower_name: string | null;
  school_name: string | null;
  package_id: UUID | null;
}

/**
 * Interface representing a simplified document package for list views
 */
export interface DocumentPackageListItem {
  id: UUID;
  application_id: UUID;
  borrower_name: string;
  school_name: string;
  package_type: DocumentPackageType;
  status: DocumentPackageStatus;
  created_at: ISO8601Date;
  expiration_date: ISO8601Date | null;
  document_count: number;
}

/**
 * Interface representing filter options for document lists
 */
export interface DocumentFilters {
  document_type: DocumentType | null;
  status: DocumentStatus | null;
  application_id: UUID | null;
  package_id: UUID | null;
  date_range: { start: ISO8601Date | null; end: ISO8601Date | null };
  search: string | null;
}

/**
 * Interface representing filter options for document package lists
 */
export interface DocumentPackageFilters {
  package_type: DocumentPackageType | null;
  status: DocumentPackageStatus | null;
  application_id: UUID | null;
  date_range: { start: ISO8601Date | null; end: ISO8601Date | null };
  search: string | null;
}

/**
 * Enum representing sort field options for document lists
 */
export enum DocumentSortField {
  DOCUMENT_TYPE = 'document_type',
  FILE_NAME = 'file_name',
  STATUS = 'status',
  GENERATED_AT = 'generated_at',
  BORROWER_NAME = 'borrower_name',
  SCHOOL_NAME = 'school_name'
}

/**
 * Enum representing sort field options for document package lists
 */
export enum DocumentPackageSortField {
  PACKAGE_TYPE = 'package_type',
  STATUS = 'status',
  CREATED_AT = 'created_at',
  EXPIRATION_DATE = 'expiration_date',
  BORROWER_NAME = 'borrower_name',
  SCHOOL_NAME = 'school_name',
  DOCUMENT_COUNT = 'document_count'
}

/**
 * Interface representing sort options for document lists
 */
export interface DocumentSort {
  field: DocumentSortField;
  direction: SortDirection;
}

/**
 * Interface representing sort options for document package lists
 */
export interface DocumentPackageSort {
  field: DocumentPackageSortField;
  direction: SortDirection;
}

/**
 * Interface representing a request to upload a document
 */
export interface DocumentUploadRequest {
  application_id: UUID;
  document_type: DocumentType;
  file: File;
}

/**
 * Interface representing a response to a document upload
 */
export interface DocumentUploadResponse {
  id: UUID;
  file_name: string;
  file_path: string;
  document_type: DocumentType;
  application_id: UUID;
  uploaded_at: ISO8601Date;
}

/**
 * Interface representing a request to create a signature request
 */
export interface SignatureRequestCreateRequest {
  document_id: UUID;
  signer_id: UUID;
  signer_type: SignerType;
}

/**
 * Interface representing a response to creating a signature request
 */
export interface SignatureRequestCreateResponse {
  id: UUID;
  document_id: UUID;
  signer_id: UUID;
  signer_type: SignerType;
  status: SignatureRequestStatus;
  requested_at: ISO8601Date;
  external_reference: string | null;
}

/**
 * Interface representing a document signing session
 */
export interface DocumentSigningSession {
  signature_request_id: UUID;
  document: Document;
  signer: {
    id: UUID;
    name: string;
    email: string;
    type: SignerType;
  };
  document_url: string;
  signature_fields: {
    id: string;
    page: number;
    x: number;
    y: number;
    width: number;
    height: number;
  }[];
  session_expiration: ISO8601Date;
}

/**
 * Interface representing the result of a document signing process
 */
export interface DocumentSigningResult {
  signature_request_id: UUID;
  document_id: UUID;
  status: SignatureRequestStatus;
  completed_at: ISO8601Date | null;
  decline_reason: string | null;
  next_steps: string | null;
}

/**
 * Interface representing the document state in Redux store
 */
export interface DocumentState {
  documents: DocumentListItem[];
  documentPackages: DocumentPackageListItem[];
  selectedDocument: Document | null;
  selectedDocumentPackage: DocumentPackage | null;
  pendingSignatures: SignatureRequest[];
  loading: boolean;
  error: string | null;
  totalDocuments: number;
  totalDocumentPackages: number;
  documentFilters: DocumentFilters;
  documentPackageFilters: DocumentPackageFilters;
  documentSort: DocumentSort | null;
  documentPackageSort: DocumentPackageSort | null;
  documentPage: number;
  documentPageSize: number;
  documentPackagePage: number;
  documentPackagePageSize: number;
}