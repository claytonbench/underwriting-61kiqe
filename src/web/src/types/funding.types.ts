import { 
  UUID, 
  ISO8601Date, 
  Currency, 
  PaginatedResponse, 
  SortDirection 
} from './common.types';
import { ApplicationStatus } from './application.types';

/**
 * Enum representing all possible funding request status values
 */
export enum FundingRequestStatus {
  PENDING = 'pending',
  ENROLLMENT_VERIFIED = 'enrollment_verified',
  PENDING_STIPULATIONS = 'pending_stipulations',
  STIPULATIONS_COMPLETE = 'stipulations_complete',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  SCHEDULED_FOR_DISBURSEMENT = 'scheduled_for_disbursement',
  DISBURSED = 'disbursed',
  CANCELLED = 'cancelled'
}

/**
 * Enum representing disbursement method options
 */
export enum DisbursementMethod {
  ACH = 'ach',
  WIRE = 'wire',
  CHECK = 'check',
  INTERNAL_TRANSFER = 'internal_transfer'
}

/**
 * Enum representing disbursement status values
 */
export enum DisbursementStatus {
  SCHEDULED = 'scheduled',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

/**
 * Enum representing enrollment verification type options
 */
export enum EnrollmentVerificationType {
  ENROLLMENT_AGREEMENT = 'enrollment_agreement',
  SCHOOL_CONFIRMATION = 'school_confirmation',
  ATTENDANCE_VERIFICATION = 'attendance_verification'
}

/**
 * Enum representing verification status values for stipulations
 */
export enum VerificationStatus {
  PENDING = 'pending',
  VERIFIED = 'verified',
  REJECTED = 'rejected',
  WAIVED = 'waived'
}

/**
 * Enum representing funding note type options
 */
export enum FundingNoteType {
  GENERAL = 'general',
  APPROVAL = 'approval',
  REJECTION = 'rejection',
  STIPULATION = 'stipulation',
  DISBURSEMENT = 'disbursement',
  CANCELLATION = 'cancellation'
}

/**
 * Enum representing funding approval level options
 */
export enum FundingApprovalLevel {
  LEVEL_1 = 'level_1',
  LEVEL_2 = 'level_2'
}

/**
 * Enum representing sort field options for funding request lists
 */
export enum FundingSortField {
  APPLICATION_ID = 'application_id',
  BORROWER_NAME = 'borrower_name',
  SCHOOL_NAME = 'school_name',
  REQUESTED_AMOUNT = 'requested_amount',
  STATUS = 'status',
  REQUESTED_DATE = 'requested_date'
}

/**
 * Enum representing sort field options for disbursement lists
 */
export enum DisbursementSortField {
  FUNDING_REQUEST_ID = 'funding_request_id',
  AMOUNT = 'amount',
  DISBURSEMENT_DATE = 'disbursement_date',
  STATUS = 'status',
  DISBURSEMENT_METHOD = 'disbursement_method'
}

/**
 * Interface representing a funding request for a loan application
 */
export interface FundingRequest {
  id: UUID;
  application_id: UUID;
  status: FundingRequestStatus;
  requested_amount: Currency;
  approved_amount: Currency | null;
  requested_at: ISO8601Date;
  requested_by: UUID;
  approved_at: ISO8601Date | null;
  approved_by: UUID | null;
  approval_level: FundingApprovalLevel | null;
  created_at: ISO8601Date;
  updated_at: ISO8601Date;
}

/**
 * Interface representing a complete funding request with all related information
 */
export interface FundingRequestDetail {
  funding_request: FundingRequest;
  application_status: ApplicationStatus;
  borrower_name: string;
  school_name: string;
  program_name: string;
  enrollment_verification: EnrollmentVerification | null;
  stipulation_verifications: StipulationVerification[];
  disbursements: Disbursement[];
  notes: FundingNote[];
}

/**
 * Interface representing a simplified funding request for list views
 */
export interface FundingRequestListItem {
  id: UUID;
  application_id: UUID;
  borrower_name: string;
  school_name: string;
  requested_amount: Currency;
  approved_amount: Currency | null;
  status: FundingRequestStatus;
  requested_at: ISO8601Date;
  approved_at: ISO8601Date | null;
}

/**
 * Interface representing a disbursement of funds for a funding request
 */
export interface Disbursement {
  id: UUID;
  funding_request_id: UUID;
  amount: Currency;
  disbursement_date: ISO8601Date;
  disbursement_method: DisbursementMethod;
  reference_number: string | null;
  status: DisbursementStatus;
  processed_by: UUID | null;
  processed_at: ISO8601Date | null;
  created_at: ISO8601Date;
  updated_at: ISO8601Date;
}

/**
 * Interface representing a simplified disbursement for list views
 */
export interface DisbursementListItem {
  id: UUID;
  funding_request_id: UUID;
  application_id: UUID;
  borrower_name: string;
  school_name: string;
  amount: Currency;
  disbursement_date: ISO8601Date;
  disbursement_method: DisbursementMethod;
  status: DisbursementStatus;
}

/**
 * Interface representing enrollment verification for a funding request
 */
export interface EnrollmentVerification {
  id: UUID;
  funding_request_id: UUID;
  verification_type: EnrollmentVerificationType;
  verified_by: UUID;
  verified_at: ISO8601Date;
  start_date: ISO8601Date;
  comments: string | null;
  document_id: UUID | null;
  created_at: ISO8601Date;
  updated_at: ISO8601Date;
}

/**
 * Interface representing stipulation verification for a funding request
 */
export interface StipulationVerification {
  id: UUID;
  funding_request_id: UUID;
  stipulation_id: UUID;
  stipulation_description: string;
  status: VerificationStatus;
  verified_by: UUID | null;
  verified_at: ISO8601Date | null;
  comments: string | null;
  created_at: ISO8601Date;
  updated_at: ISO8601Date;
}

/**
 * Interface representing a note related to a funding request
 */
export interface FundingNote {
  id: UUID;
  funding_request_id: UUID;
  note_type: FundingNoteType;
  note_text: string;
  created_at: ISO8601Date;
  created_by: UUID;
  created_by_name: string;
}

/**
 * Interface representing filter options for funding request lists
 */
export interface FundingFilters {
  status: FundingRequestStatus | null;
  application_id: UUID | null;
  borrower_name: string | null;
  school_name: string | null;
  date_range: { start: string | null; end: string | null };
  amount_range: { min: number | null; max: number | null };
}

/**
 * Interface representing filter options for disbursement lists
 */
export interface DisbursementFilters {
  status: DisbursementStatus | null;
  funding_request_id: UUID | null;
  application_id: UUID | null;
  borrower_name: string | null;
  school_name: string | null;
  disbursement_method: DisbursementMethod | null;
  date_range: { start: string | null; end: string | null };
  amount_range: { min: number | null; max: number | null };
}

/**
 * Interface representing sort options for funding request lists
 */
export interface FundingSort {
  field: FundingSortField;
  direction: SortDirection;
}

/**
 * Interface representing sort options for disbursement lists
 */
export interface DisbursementSort {
  field: DisbursementSortField;
  direction: SortDirection;
}

/**
 * Interface representing a request to verify enrollment for a funding request
 */
export interface EnrollmentVerificationRequest {
  funding_request_id: UUID;
  verification_type: EnrollmentVerificationType;
  start_date: string;
  comments: string | null;
  document_id: UUID | null;
}

/**
 * Interface representing a request to verify a stipulation for a funding request
 */
export interface StipulationVerificationRequest {
  funding_request_id: UUID;
  stipulation_id: UUID;
  status: VerificationStatus;
  comments: string | null;
}

/**
 * Interface representing a request to approve a funding request
 */
export interface FundingApprovalRequest {
  funding_request_id: UUID;
  approved_amount: number;
  comments: string | null;
}

/**
 * Interface representing a request to create a disbursement for a funding request
 */
export interface DisbursementCreateRequest {
  funding_request_id: UUID;
  amount: number;
  disbursement_date: string;
  disbursement_method: DisbursementMethod;
  comments: string | null;
}

/**
 * Interface representing a request to create a note for a funding request
 */
export interface FundingNoteCreateRequest {
  funding_request_id: UUID;
  note_type: FundingNoteType;
  note_text: string;
}

/**
 * Interface representing a summary of funding requests by status
 */
export interface FundingStatusSummary {
  pending: number;
  enrollment_verified: number;
  pending_stipulations: number;
  stipulations_complete: number;
  approved: number;
  scheduled_for_disbursement: number;
  disbursed: number;
  rejected: number;
  cancelled: number;
  total: number;
}

/**
 * Interface representing the funding state in Redux store
 */
export interface FundingState {
  fundingRequests: FundingRequestListItem[];
  selectedFundingRequest: FundingRequestDetail | null;
  disbursements: DisbursementListItem[];
  selectedDisbursement: Disbursement | null;
  loading: boolean;
  error: string | null;
  totalFundingRequests: number;
  totalDisbursements: number;
  fundingFilters: FundingFilters;
  disbursementFilters: DisbursementFilters;
  fundingSort: FundingSort | null;
  disbursementSort: DisbursementSort | null;
  fundingPage: number;
  disbursementPage: number;
  pageSize: number;
  statusSummary: FundingStatusSummary | null;
}