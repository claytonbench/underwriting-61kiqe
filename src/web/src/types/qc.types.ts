import { 
  UUID, 
  ISO8601Date, 
  PaginatedResponse, 
  SortDirection, 
  ActionStatus 
} from './common.types';
import { 
  ApplicationStatus, 
  LoanApplication 
} from './application.types';
import { 
  Document, 
  DocumentType 
} from './document.types';

/**
 * Enum representing possible QC review status values
 */
export enum QCStatus {
  PENDING = 'pending',
  IN_REVIEW = 'in_review',
  APPROVED = 'approved',
  RETURNED = 'returned'
}

/**
 * Enum representing verification status values for documents, stipulations, and checklist items
 */
export enum QCVerificationStatus {
  UNVERIFIED = 'unverified',
  VERIFIED = 'verified',
  REJECTED = 'rejected',
  WAIVED = 'waived'
}

/**
 * Enum representing reasons for returning a QC review
 */
export enum QCReturnReason {
  INCOMPLETE_DOCUMENTATION = 'incomplete_documentation',
  INCORRECT_INFORMATION = 'incorrect_information',
  MISSING_SIGNATURES = 'missing_signatures',
  STIPULATION_NOT_MET = 'stipulation_not_met',
  COMPLIANCE_ISSUE = 'compliance_issue',
  OTHER = 'other'
}

/**
 * Enum representing categories for QC checklist items
 */
export enum QCChecklistCategory {
  DOCUMENT_COMPLETENESS = 'document_completeness',
  LOAN_INFORMATION = 'loan_information',
  BORROWER_INFORMATION = 'borrower_information',
  SCHOOL_INFORMATION = 'school_information',
  STIPULATIONS = 'stipulations',
  COMPLIANCE = 'compliance'
}

/**
 * Enum representing priority levels for QC reviews
 */
export enum QCPriority {
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low'
}

/**
 * Enum representing assignment types for QC reviews
 */
export enum QCAssignmentType {
  AUTOMATIC = 'automatic',
  MANUAL = 'manual'
}

/**
 * Interface representing a QC review for a loan application
 */
export interface QCReview {
  id: UUID;
  application_id: UUID;
  application: LoanApplication;
  status: QCStatus;
  priority: QCPriority;
  assigned_to: UUID | null;
  assigned_to_name: string | null;
  assignment_type: QCAssignmentType;
  assigned_at: ISO8601Date | null;
  completed_at: ISO8601Date | null;
  return_reason: QCReturnReason | null;
  notes: string | null;
  document_verifications: DocumentVerification[];
  stipulation_verifications: QCStipulationVerification[];
  checklist_items: QCChecklistItem[];
  completion_percentage: number;
  created_at: ISO8601Date;
  updated_at: ISO8601Date;
}

/**
 * Interface representing document verification in the QC process
 */
export interface DocumentVerification {
  id: UUID;
  qc_review_id: UUID;
  document_id: UUID;
  document: Document;
  status: QCVerificationStatus;
  verified_by: UUID | null;
  verified_by_name: string | null;
  verified_at: ISO8601Date | null;
  comments: string | null;
  created_at: ISO8601Date;
  updated_at: ISO8601Date;
}

/**
 * Interface representing stipulation verification in the QC process
 */
export interface QCStipulationVerification {
  id: UUID;
  qc_review_id: UUID;
  stipulation_id: UUID;
  stipulation_description: string;
  status: QCVerificationStatus;
  verified_by: UUID | null;
  verified_by_name: string | null;
  verified_at: ISO8601Date | null;
  comments: string | null;
  created_at: ISO8601Date;
  updated_at: ISO8601Date;
}

/**
 * Interface representing a checklist item in the QC process
 */
export interface QCChecklistItem {
  id: UUID;
  qc_review_id: UUID;
  category: QCChecklistCategory;
  item_text: string;
  status: QCVerificationStatus;
  verified_by: UUID | null;
  verified_by_name: string | null;
  verified_at: ISO8601Date | null;
  comments: string | null;
  created_at: ISO8601Date;
  updated_at: ISO8601Date;
}

/**
 * Interface representing a simplified QC review for list views
 */
export interface QCReviewListItem {
  id: UUID;
  application_id: UUID;
  borrower_name: string;
  school_name: string;
  status: QCStatus;
  priority: QCPriority;
  assigned_to_name: string | null;
  assigned_at: ISO8601Date | null;
  completion_percentage: number;
  created_at: ISO8601Date;
}

/**
 * Interface representing filter options for QC review lists
 */
export interface QCReviewFilters {
  status: QCStatus | null;
  priority: QCPriority | null;
  assigned_to: UUID | null;
  application_id: UUID | null;
  borrower_name: string | null;
  school_id: UUID | null;
  date_range: { start: ISO8601Date | null; end: ISO8601Date | null };
}

/**
 * Enum representing sort field options for QC review lists
 */
export enum QCReviewSortField {
  BORROWER_NAME = 'borrower_name',
  SCHOOL_NAME = 'school_name',
  STATUS = 'status',
  PRIORITY = 'priority',
  ASSIGNED_TO = 'assigned_to',
  ASSIGNED_AT = 'assigned_at',
  COMPLETION_PERCENTAGE = 'completion_percentage',
  CREATED_AT = 'created_at'
}

/**
 * Interface representing sort options for QC review lists
 */
export interface QCReviewSort {
  field: QCReviewSortField;
  direction: SortDirection;
}

/**
 * Interface representing a paginated response of QC review list items
 */
export interface QCReviewListResponse extends PaginatedResponse<QCReviewListItem> {}

/**
 * Interface representing a request to update document verification status
 */
export interface DocumentVerificationRequest {
  document_verification_id: UUID;
  status: QCVerificationStatus;
  comments: string | null;
}

/**
 * Interface representing a request to update stipulation verification status
 */
export interface StipulationVerificationRequest {
  stipulation_verification_id: UUID;
  status: QCVerificationStatus;
  comments: string | null;
}

/**
 * Interface representing a request to update checklist item verification status
 */
export interface ChecklistItemVerificationRequest {
  checklist_item_id: UUID;
  status: QCVerificationStatus;
  comments: string | null;
}

/**
 * Interface representing a request to make a QC review decision (approve or return)
 */
export interface QCReviewDecisionRequest {
  qc_review_id: UUID;
  status: QCStatus;
  return_reason: QCReturnReason | null;
  notes: string | null;
}

/**
 * Interface representing a request to assign a QC review to a reviewer
 */
export interface QCReviewAssignmentRequest {
  qc_review_id: UUID;
  assigned_to: UUID;
  assignment_type: QCAssignmentType;
}

/**
 * Interface representing counts of QC reviews by status
 */
export interface QCCountsByStatus {
  pending: number;
  in_review: number;
  approved: number;
  returned: number;
  total: number;
}

/**
 * Interface representing the QC state in Redux store
 */
export interface QCState {
  qcReviews: QCReviewListItem[];
  selectedQCReview: QCReview | null;
  loading: boolean;
  error: string | null;
  totalQCReviews: number;
  filters: QCReviewFilters;
  sort: QCReviewSort | null;
  page: number;
  pageSize: number;
  countsByStatus: QCCountsByStatus | null;
}