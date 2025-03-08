import {
  UUID,
  ISO8601Date,
  Currency,
  PaginatedResponse,
  SortDirection,
  ApiResponse
} from './common.types';
import { UserType } from './auth.types';
import { LoanApplication, ApplicationStatus } from './application.types';

/**
 * Enum representing priority levels for applications in the underwriting queue
 */
export enum UnderwritingQueuePriority {
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low'
}

/**
 * Enum representing status values for applications in the underwriting queue
 */
export enum UnderwritingQueueStatus {
  PENDING = 'pending',
  ASSIGNED = 'assigned',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  RETURNED = 'returned'
}

/**
 * Enum representing possible underwriting decision values
 */
export enum UnderwritingDecision {
  APPROVE = 'approve',
  DENY = 'deny',
  REVISE = 'revise'
}

/**
 * Enum representing credit score quality tiers
 */
export enum CreditScoreTier {
  EXCELLENT = 'excellent',
  GOOD = 'good',
  FAIR = 'fair',
  POOR = 'poor',
  BAD = 'bad'
}

/**
 * Enum representing types of stipulations that may be required for loan approval
 */
export enum StipulationType {
  PROOF_OF_IDENTITY = 'proof_of_identity',
  PROOF_OF_INCOME = 'proof_of_income',
  PROOF_OF_RESIDENCE = 'proof_of_residence',
  ENROLLMENT_AGREEMENT = 'enrollment_agreement',
  ADDITIONAL_DOCUMENTATION = 'additional_documentation'
}

/**
 * Enum representing possible status values for stipulations
 */
export enum StipulationStatus {
  PENDING = 'pending',
  SATISFIED = 'satisfied',
  WAIVED = 'waived'
}

/**
 * Enum representing categories for grouping related stipulation types
 */
export enum StipulationCategory {
  IDENTITY_VERIFICATION = 'identity_verification',
  INCOME_VERIFICATION = 'income_verification',
  CITIZENSHIP_RESIDENCY = 'citizenship_residency',
  EDUCATION_DOCUMENTATION = 'education_documentation',
  FINANCIAL = 'financial'
}

/**
 * Enum representing reason codes for underwriting decisions
 */
export enum DecisionReasonCode {
  CREDIT_SCORE = 'credit_score',
  DEBT_TO_INCOME = 'debt_to_income',
  EMPLOYMENT_HISTORY = 'employment_history',
  HOUSING_PAYMENT = 'housing_payment',
  INCOME_INSUFFICIENT = 'income_insufficient',
  CITIZENSHIP_STATUS = 'citizenship_status',
  PROGRAM_ELIGIBILITY = 'program_eligibility',
  DOCUMENTATION_ISSUES = 'documentation_issues',
  IDENTITY_VERIFICATION = 'identity_verification',
  OTHER = 'other'
}

/**
 * Interface representing an application in the underwriting queue
 */
export interface UnderwritingQueue {
  id: UUID;
  application_id: UUID;
  assigned_to: UUID | null;
  assignment_date: ISO8601Date | null;
  priority: UnderwritingQueuePriority;
  status: UnderwritingQueueStatus;
  due_date: ISO8601Date;
  created_at: ISO8601Date;
  is_overdue: boolean;
}

/**
 * Interface representing credit report information for borrowers and co-borrowers
 */
export interface CreditInformation {
  id: UUID;
  application_id: UUID;
  borrower_id: UUID;
  is_co_borrower: boolean;
  credit_score: number;
  credit_tier: CreditScoreTier;
  report_date: ISO8601Date;
  report_reference: string;
  file_path: string;
  monthly_debt: Currency;
  debt_to_income_ratio: number;
  uploaded_at: ISO8601Date;
  download_url: string | null;
}

/**
 * Interface representing an underwriting decision with all related data
 */
export interface UnderwritingDecisionData {
  application_id: UUID;
  decision: UnderwritingDecision;
  decision_date: ISO8601Date;
  underwriter_id: UUID;
  comments: string;
  approved_amount: Currency | null;
  interest_rate: number | null;
  term_months: number | null;
  reasons: DecisionReason[];
  stipulations: Stipulation[];
}

/**
 * Interface representing a reason for an underwriting decision
 */
export interface DecisionReason {
  id: UUID;
  decision_id: UUID;
  reason_code: DecisionReasonCode;
  description: string;
  is_primary: boolean;
}

/**
 * Interface representing a stipulation required for loan approval
 */
export interface Stipulation {
  id: UUID;
  application_id: UUID;
  stipulation_type: StipulationType;
  category: StipulationCategory;
  description: string;
  required_by_date: ISO8601Date;
  status: StipulationStatus;
  created_at: ISO8601Date;
  created_by: UUID;
  satisfied_at: ISO8601Date | null;
  satisfied_by: UUID | null;
  is_overdue: boolean;
}

/**
 * Interface representing a note related to the underwriting process
 */
export interface UnderwritingNote {
  id: UUID;
  application_id: UUID;
  note_text: string;
  created_at: ISO8601Date;
  created_by: UUID;
  created_by_name: string;
  is_internal: boolean;
}

/**
 * Interface representing an item in the underwriting queue with additional display information
 */
export interface UnderwritingQueueItem {
  queue_id: UUID;
  application_id: UUID;
  borrower_name: string;
  school_name: string;
  program_name: string;
  requested_amount: Currency;
  submission_date: ISO8601Date;
  priority: UnderwritingQueuePriority;
  status: UnderwritingQueueStatus;
  due_date: ISO8601Date;
  is_overdue: boolean;
  has_co_borrower: boolean;
  assigned_to: UUID | null;
  assigned_to_name: string | null;
}

/**
 * Interface representing a complete application with all underwriting-related information
 */
export interface UnderwritingApplicationDetail {
  application: LoanApplication;
  queue_item: UnderwritingQueue | null;
  borrower_credit: CreditInformation | null;
  co_borrower_credit: CreditInformation | null;
  decision: UnderwritingDecisionData | null;
  notes: UnderwritingNote[];
  documents: Array<{
    id: UUID;
    document_type: string;
    file_name: string;
    uploaded_at: ISO8601Date;
    download_url: string | null;
  }>;
}

/**
 * Interface representing a request to record an underwriting decision
 */
export interface UnderwritingDecisionRequest {
  application_id: UUID;
  decision: UnderwritingDecision;
  comments: string;
  approved_amount: Currency | null;
  interest_rate: number | null;
  term_months: number | null;
  reasons: Array<{
    reason_code: DecisionReasonCode;
    is_primary: boolean;
  }>;
  stipulations: Array<{
    stipulation_type: StipulationType;
    description: string;
    required_by_date: ISO8601Date;
  }>;
}

/**
 * Interface representing a request to assign an application to an underwriter
 */
export interface UnderwritingQueueAssignRequest {
  queue_id: UUID;
  underwriter_id: UUID;
}

/**
 * Interface representing a request to create a new underwriting note
 */
export interface UnderwritingNoteCreateRequest {
  application_id: UUID;
  note_text: string;
  is_internal: boolean;
}

/**
 * Interface representing a request to update a stipulation's status
 */
export interface StipulationUpdateRequest {
  stipulation_id: UUID;
  status: StipulationStatus;
  comments: string | null;
}

/**
 * Interface representing filter options for the underwriting queue
 */
export interface UnderwritingQueueFilters {
  status: UnderwritingQueueStatus | null;
  priority: UnderwritingQueuePriority | null;
  assigned_to: UUID | null;
  borrower_name: string | null;
  school_id: UUID | null;
  is_overdue: boolean | null;
  date_range: {
    start: ISO8601Date | null;
    end: ISO8601Date | null;
  };
}

/**
 * Enum representing sort field options for the underwriting queue
 */
export enum UnderwritingQueueSortField {
  BORROWER_NAME = 'borrower_name',
  SCHOOL_NAME = 'school_name',
  PROGRAM_NAME = 'program_name',
  REQUESTED_AMOUNT = 'requested_amount',
  SUBMISSION_DATE = 'submission_date',
  PRIORITY = 'priority',
  DUE_DATE = 'due_date',
  STATUS = 'status'
}

/**
 * Interface representing sort options for the underwriting queue
 */
export interface UnderwritingQueueSort {
  field: UnderwritingQueueSortField;
  direction: SortDirection;
}

/**
 * Interface representing a paginated response of underwriting queue items
 */
export interface UnderwritingQueueResponse {
  results: UnderwritingQueueItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/**
 * Interface representing metrics for the underwriting dashboard
 */
export interface UnderwritingMetrics {
  total_in_queue: number;
  assigned_to_me: number;
  pending_review: number;
  completed_today: number;
  overdue: number;
  average_decision_time: number; // in days
  approval_rate: number; // percentage
}

/**
 * Interface representing the underwriting state in Redux store
 */
export interface UnderwritingState {
  queueItems: UnderwritingQueueItem[];
  selectedApplication: UnderwritingApplicationDetail | null;
  loading: boolean;
  error: string | null;
  totalItems: number;
  filters: UnderwritingQueueFilters;
  sort: UnderwritingQueueSort | null;
  page: number;
  pageSize: number;
  metrics: UnderwritingMetrics | null;
  decisionDraft: Partial<UnderwritingDecisionRequest> | null;
}