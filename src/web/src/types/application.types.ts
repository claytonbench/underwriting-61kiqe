import { 
  UUID, 
  ISO8601Date, 
  Currency, 
  Address, 
  PaginatedResponse, 
  SortDirection 
} from './common.types';
import { UserType } from './auth.types';
import { School, Program, ProgramVersion } from './school.types';
import { BorrowerProfile, EmploymentInfo } from './user.types';

/**
 * Enum representing all possible application status values throughout the loan lifecycle
 */
export enum ApplicationStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  IN_REVIEW = 'in_review',
  APPROVED = 'approved',
  DENIED = 'denied',
  REVISION_REQUESTED = 'revision_requested',
  COMMITMENT_SENT = 'commitment_sent',
  COMMITMENT_ACCEPTED = 'commitment_accepted',
  COMMITMENT_DECLINED = 'commitment_declined',
  COUNTER_OFFER_MADE = 'counter_offer_made',
  DOCUMENTS_SENT = 'documents_sent',
  PARTIALLY_EXECUTED = 'partially_executed',
  FULLY_EXECUTED = 'fully_executed',
  QC_REVIEW = 'qc_review',
  QC_APPROVED = 'qc_approved',
  QC_REJECTED = 'qc_rejected',
  READY_TO_FUND = 'ready_to_fund',
  FUNDED = 'funded',
  ABANDONED = 'abandoned',
  DOCUMENTS_EXPIRED = 'documents_expired',
  INCOMPLETE = 'incomplete'
}

/**
 * Enum representing housing status options for borrowers
 */
export enum HousingStatus {
  OWN = 'own',
  RENT = 'rent',
  LIVE_WITH_FAMILY = 'live_with_family',
  CAMPUS_HOUSING = 'campus_housing',
  OTHER = 'other'
}

/**
 * Enum representing employment type options for borrowers
 */
export enum EmploymentType {
  FULL_TIME = 'full_time',
  PART_TIME = 'part_time',
  SELF_EMPLOYED = 'self_employed',
  UNEMPLOYED = 'unemployed',
  RETIRED = 'retired',
  STUDENT = 'student',
  OTHER = 'other'
}

/**
 * Enum representing citizenship status options for borrowers
 */
export enum CitizenshipStatus {
  US_CITIZEN = 'us_citizen',
  PERMANENT_RESIDENT = 'permanent_resident',
  ELIGIBLE_NON_CITIZEN = 'eligible_non_citizen',
  NON_ELIGIBLE = 'non_eligible'
}

/**
 * Enum representing relationship types between borrower and co-borrower
 */
export enum RelationshipType {
  SPOUSE = 'spouse',
  PARENT = 'parent',
  SIBLING = 'sibling',
  OTHER_RELATIVE = 'other_relative',
  FRIEND = 'friend',
  OTHER = 'other'
}

/**
 * Core interface representing a loan application
 */
export interface LoanApplication {
  id: UUID;
  borrower_id: UUID;
  co_borrower_id: UUID | null;
  school_id: UUID;
  program_id: UUID;
  program_version_id: UUID;
  status: ApplicationStatus;
  submission_date: ISO8601Date | null;
  last_updated: ISO8601Date;
  created_by: UUID;
  created_at: ISO8601Date;
}

/**
 * Interface representing financial details of a loan application
 */
export interface LoanDetails {
  application_id: UUID;
  tuition_amount: Currency;
  deposit_amount: Currency;
  other_funding: Currency;
  requested_amount: Currency;
  approved_amount: Currency | null;
  start_date: ISO8601Date;
  completion_date: ISO8601Date;
}

/**
 * Interface representing a document attached to a loan application
 */
export interface ApplicationDocument {
  id: UUID;
  application_id: UUID;
  document_type: string;
  file_name: string;
  file_path: string;
  uploaded_at: ISO8601Date;
  uploaded_by: UUID;
  status: string;
  download_url: string | null;
}

/**
 * Interface representing a status change in the application history
 */
export interface ApplicationStatusHistory {
  id: UUID;
  application_id: UUID;
  previous_status: ApplicationStatus;
  new_status: ApplicationStatus;
  changed_at: ISO8601Date;
  changed_by: UUID;
  comments: string | null;
}

/**
 * Interface representing a complete loan application with all related information
 */
export interface ApplicationDetail {
  application: LoanApplication;
  loan_details: LoanDetails;
  borrower: BorrowerProfile;
  co_borrower: BorrowerProfile | null;
  school: School;
  program: Program;
  program_version: ProgramVersion;
  documents: ApplicationDocument[];
  status_history: ApplicationStatusHistory[];
}

/**
 * Interface representing a simplified loan application for list views
 */
export interface ApplicationListItem {
  id: UUID;
  borrower_name: string;
  school_name: string;
  program_name: string;
  requested_amount: Currency;
  status: ApplicationStatus;
  submission_date: ISO8601Date | null;
  last_updated: ISO8601Date;
  has_co_borrower: boolean;
}

/**
 * Interface representing the complete form data for a loan application
 */
export interface ApplicationFormData {
  borrower_info: BorrowerFormData;
  employment_info: EmploymentFormData;
  has_co_borrower: boolean;
  co_borrower_info: CoBorrowerFormData | null;
  loan_details: LoanDetailsFormData;
}

/**
 * Interface representing borrower personal information form data
 */
export interface BorrowerFormData {
  first_name: string;
  middle_name: string | null;
  last_name: string;
  ssn: string;
  dob: string;
  email: string;
  phone: string;
  citizenship_status: CitizenshipStatus;
  address_line1: string;
  address_line2: string | null;
  city: string;
  state: string;
  zip_code: string;
  housing_status: HousingStatus;
  housing_payment: number;
}

/**
 * Interface representing employment and income form data
 */
export interface EmploymentFormData {
  employment_type: EmploymentType;
  employer_name: string;
  occupation: string;
  employer_phone: string;
  years_employed: number;
  months_employed: number;
  annual_income: number;
  other_income: number;
  other_income_source: string | null;
}

/**
 * Interface representing co-borrower information form data
 */
export interface CoBorrowerFormData {
  relationship: RelationshipType;
  first_name: string;
  middle_name: string | null;
  last_name: string;
  ssn: string;
  dob: string;
  email: string;
  phone: string;
  citizenship_status: CitizenshipStatus;
  same_address: boolean;
  address_line1: string | null;
  address_line2: string | null;
  city: string | null;
  state: string | null;
  zip_code: string | null;
  employment_type: EmploymentType;
  employer_name: string;
  occupation: string;
  employer_phone: string;
  years_employed: number;
  months_employed: number;
  annual_income: number;
}

/**
 * Interface representing loan details form data
 */
export interface LoanDetailsFormData {
  school_id: UUID;
  program_id: UUID;
  start_date: string;
  completion_date: string;
  tuition_amount: number;
  deposit_amount: number;
  other_funding: number;
  requested_amount: number;
}

/**
 * Interface representing a request to create a new application
 */
export interface ApplicationCreateRequest {
  form_data: ApplicationFormData;
  created_by: UUID;
}

/**
 * Interface representing a request to update an existing application
 */
export interface ApplicationUpdateRequest {
  application_id: UUID;
  form_data: Partial<ApplicationFormData>;
}

/**
 * Interface representing a request to submit an application for review
 */
export interface ApplicationSubmitRequest {
  application_id: UUID;
}

/**
 * Interface representing filter options for application lists
 */
export interface ApplicationFilters {
  status: ApplicationStatus | null;
  school_id: UUID | null;
  program_id: UUID | null;
  borrower_name: string | null;
  date_range: { start: string | null; end: string | null };
  has_co_borrower: boolean | null;
}

/**
 * Enum representing sort field options for application lists
 */
export enum ApplicationSortField {
  BORROWER_NAME = 'borrower_name',
  SCHOOL_NAME = 'school_name',
  PROGRAM_NAME = 'program_name',
  REQUESTED_AMOUNT = 'requested_amount',
  STATUS = 'status',
  SUBMISSION_DATE = 'submission_date',
  LAST_UPDATED = 'last_updated'
}

/**
 * Interface representing sort options for application lists
 */
export interface ApplicationSort {
  field: ApplicationSortField;
  direction: SortDirection;
}

/**
 * Interface representing a paginated response of application list items
 */
export interface ApplicationListResponse extends PaginatedResponse<ApplicationListItem> {}

/**
 * Interface representing a request to upload a document for an application
 */
export interface ApplicationDocumentUploadRequest {
  application_id: UUID;
  document_type: string;
  file: File;
}

/**
 * Interface representing a request to update an application's status
 */
export interface ApplicationStatusUpdateRequest {
  application_id: UUID;
  status: ApplicationStatus;
  comments: string | null;
}

/**
 * Interface representing counts of applications by status
 */
export interface ApplicationCountsByStatus {
  draft: number;
  submitted: number;
  in_review: number;
  approved: number;
  denied: number;
  funded: number;
  total: number;
}

/**
 * Interface representing a required action for an application
 */
export interface ApplicationRequiredAction {
  id: UUID;
  application_id: UUID;
  action_type: string;
  description: string;
  due_date: ISO8601Date | null;
  status: string;
  related_entity_id: UUID | null;
  related_entity_type: string | null;
}

/**
 * Interface representing a timeline event in an application's history
 */
export interface ApplicationTimelineEvent {
  id: UUID;
  application_id: UUID;
  event_type: string;
  event_date: ISO8601Date;
  description: string;
  user_id: UUID | null;
  user_name: string | null;
  related_entity_id: UUID | null;
  related_entity_type: string | null;
}

/**
 * Interface representing the application state in Redux store
 */
export interface ApplicationState {
  applications: ApplicationListItem[];
  selectedApplication: ApplicationDetail | null;
  loading: boolean;
  error: string | null;
  totalApplications: number;
  filters: ApplicationFilters;
  sort: ApplicationSort | null;
  page: number;
  pageSize: number;
  countsByStatus: ApplicationCountsByStatus | null;
  currentFormData: ApplicationFormData | null;
  formStep: number;
  requiredActions: ApplicationRequiredAction[];
  timelineEvents: ApplicationTimelineEvent[];
}