/**
 * Application Constants
 * 
 * This file defines application-wide constants for the loan management system frontend,
 * including API endpoints, storage keys, application statuses, and configuration values.
 * Centralizing constants ensures consistency across the application and simplifies updates.
 * 
 * @version 1.0.0
 */

/**
 * API endpoint paths for all backend services
 */
export const API_ENDPOINTS = {
  BASE_URL: '/api/v1',
  
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REFRESH_TOKEN: '/auth/refresh',
    RESET_PASSWORD: '/auth/reset-password',
    FORGOT_PASSWORD: '/auth/forgot-password',
    VERIFY_EMAIL: '/auth/verify-email',
    REGISTER: '/auth/register',
    ME: '/auth/me',
  },
  
  USERS: {
    BASE: '/users',
    PROFILE: '/users/profile',
    BY_ID: (id: string) => `/users/${id}`,
    ROLES: '/users/roles',
    UPDATE_PASSWORD: '/users/password',
  },
  
  SCHOOLS: {
    BASE: '/schools',
    BY_ID: (id: string) => `/schools/${id}`,
    PROGRAMS: '/schools/programs',
    PROGRAM_BY_ID: (id: string) => `/schools/programs/${id}`,
    CONTACTS: '/schools/contacts',
    DOCUMENTS: '/schools/documents',
  },
  
  APPLICATIONS: {
    BASE: '/applications',
    BY_ID: (id: string) => `/applications/${id}`,
    STATUS_HISTORY: (id: string) => `/applications/${id}/history`,
    DOCUMENTS: (id: string) => `/applications/${id}/documents`,
    BORROWER: (id: string) => `/applications/${id}/borrower`,
    CO_BORROWER: (id: string) => `/applications/${id}/co-borrower`,
    SUBMIT: (id: string) => `/applications/${id}/submit`,
  },
  
  DOCUMENTS: {
    BASE: '/documents',
    BY_ID: (id: string) => `/documents/${id}`,
    GENERATE: '/documents/generate',
    TEMPLATES: '/documents/templates',
    SIGNATURE_REQUEST: '/documents/signature-request',
    SIGNATURE_STATUS: (id: string) => `/documents/signature-status/${id}`,
    UPLOAD: '/documents/upload',
    DOWNLOAD: (id: string) => `/documents/${id}/download`,
  },
  
  UNDERWRITING: {
    BASE: '/underwriting',
    QUEUE: '/underwriting/queue',
    DECISIONS: '/underwriting/decisions',
    REVIEW: (id: string) => `/underwriting/applications/${id}`,
    DECISION: (id: string) => `/underwriting/applications/${id}/decision`,
    STIPULATIONS: '/underwriting/stipulations',
    NOTES: '/underwriting/notes',
  },
  
  QC: {
    BASE: '/qc',
    QUEUE: '/qc/queue',
    REVIEW: (id: string) => `/qc/applications/${id}`,
    APPROVE: (id: string) => `/qc/applications/${id}/approve`,
    REJECT: (id: string) => `/qc/applications/${id}/reject`,
    VERIFICATIONS: '/qc/verifications',
  },
  
  FUNDING: {
    BASE: '/funding',
    QUEUE: '/funding/queue',
    REQUEST: (id: string) => `/funding/applications/${id}/request`,
    APPROVE: (id: string) => `/funding/applications/${id}/approve`,
    DISBURSEMENT: '/funding/disbursement',
    ENROLLMENT_VERIFICATION: '/funding/enrollment-verification',
    NOTES: '/funding/notes',
  },
  
  NOTIFICATIONS: {
    BASE: '/notifications',
    BY_ID: (id: string) => `/notifications/${id}`,
    MARK_READ: (id: string) => `/notifications/${id}/read`,
    MARK_ALL_READ: '/notifications/read-all',
  },
  
  REPORTS: {
    BASE: '/reports',
    APPLICATION_VOLUME: '/reports/application-volume',
    APPROVAL_RATES: '/reports/approval-rates',
    FUNDING_VOLUME: '/reports/funding-volume',
    PROCESSING_TIMES: '/reports/processing-times',
    DOCUMENT_COMPLETION: '/reports/document-completion',
    EXPORT: '/reports/export',
  },
};

/**
 * Local storage key names for persistent data
 */
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'lms_auth_token',
  REFRESH_TOKEN: 'lms_refresh_token',
  USER_DATA: 'lms_user_data',
  THEME_PREFERENCE: 'lms_theme',
  LANGUAGE_PREFERENCE: 'lms_language',
  LAST_ACTIVE: 'lms_last_active',
  SAVED_FILTERS: 'lms_saved_filters',
  FORM_DRAFT: 'lms_form_draft',
};

/**
 * Application status constants matching backend status values
 * These represent the entire loan application lifecycle as defined in the
 * application status flow diagram.
 */
export const APPLICATION_STATUS = {
  DRAFT: 'Draft',
  SUBMITTED: 'Submitted',
  INCOMPLETE: 'Incomplete',
  IN_REVIEW: 'InReview',
  APPROVED: 'Approved',
  DENIED: 'Denied',
  REVISION_REQUESTED: 'RevisionRequested',
  COMMITMENT_SENT: 'CommitmentSent',
  COMMITMENT_ACCEPTED: 'CommitmentAccepted',
  COMMITMENT_DECLINED: 'CommitmentDeclined',
  COUNTER_OFFER_MADE: 'CounterOfferMade',
  DOCUMENTS_SENT: 'DocumentsSent',
  PARTIALLY_EXECUTED: 'PartiallyExecuted',
  FULLY_EXECUTED: 'FullyExecuted',
  DOCUMENTS_EXPIRED: 'DocumentsExpired',
  QC_REVIEW: 'QCReview',
  QC_APPROVED: 'QCApproved',
  QC_REJECTED: 'QCRejected',
  READY_TO_FUND: 'ReadyToFund',
  FUNDED: 'Funded',
  ABANDONED: 'Abandoned',
};

/**
 * Document type constants for document management
 */
export const DOCUMENT_TYPES = {
  LOAN_AGREEMENT: 'LoanAgreement',
  COMMITMENT_LETTER: 'CommitmentLetter',
  DISCLOSURE_FORM: 'DisclosureForm',
  TRUTH_IN_LENDING: 'TruthInLending',
  PROMISSORY_NOTE: 'PromissoryNote',
  DRIVERS_LICENSE: 'DriversLicense',
  PROOF_OF_INCOME: 'ProofOfIncome',
  ENROLLMENT_AGREEMENT: 'EnrollmentAgreement',
  PAY_STUB: 'PayStub',
  W2_FORM: 'W2Form',
  TAX_RETURN: 'TaxReturn',
  BANK_STATEMENT: 'BankStatement',
  EMPLOYMENT_VERIFICATION: 'EmploymentVerification',
  IDENTITY_VERIFICATION: 'IdentityVerification',
  DISBURSEMENT_AUTHORIZATION: 'DisbursementAuthorization',
  AUTO_PAY_AUTHORIZATION: 'AutoPayAuthorization',
};

/**
 * Pagination configuration constants
 */
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_PAGE_SIZE: 10,
  PAGE_SIZE_OPTIONS: [5, 10, 25, 50, 100],
  MAX_PAGES_DISPLAYED: 5,
};

/**
 * Date format strings for consistent date formatting
 */
export const DATE_FORMATS = {
  DISPLAY: 'MM/DD/YYYY',
  DISPLAY_WITH_TIME: 'MM/DD/YYYY h:mm A',
  FORM: 'YYYY-MM-DD',
  API: 'YYYY-MM-DD',
  TIMESTAMP: 'YYYY-MM-DDTHH:mm:ss.SSSZ',
  MONTH_YEAR: 'MMMM YYYY',
  SHORT_DATE: 'MM/DD/YY',
};

/**
 * Currency formatting configuration
 */
export const CURRENCY_FORMAT = {
  LOCALE: 'en-US',
  OPTIONS: {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  },
};

/**
 * Validation patterns and rules for form validation
 */
export const VALIDATION = {
  PASSWORD: {
    MIN_LENGTH: 12,
    PATTERN: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]).{12,}$/,
    ERROR_MESSAGE: 'Password must be at least 12 characters and include uppercase, lowercase, number, and special character',
  },
  SSN: {
    PATTERN: /^\d{3}-\d{2}-\d{4}$/,
    INPUT_MASK: '999-99-9999',
    DISPLAY_MASK: 'XXX-XX-{last4}',
    ERROR_MESSAGE: 'SSN must be in format XXX-XX-XXXX',
  },
  PHONE: {
    PATTERN: /^\(\d{3}\) \d{3}-\d{4}$/,
    INPUT_MASK: '(999) 999-9999',
    ERROR_MESSAGE: 'Phone number must be in format (XXX) XXX-XXXX',
  },
  EMAIL: {
    PATTERN: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
    ERROR_MESSAGE: 'Please enter a valid email address',
  },
  ZIP_CODE: {
    PATTERN: /^\d{5}(-\d{4})?$/,
    INPUT_MASK: '99999-9999',
    ERROR_MESSAGE: 'ZIP code must be in format XXXXX or XXXXX-XXXX',
  },
  POSITIVE_NUMBER: {
    PATTERN: /^[1-9]\d*(\.\d+)?$/,
    ERROR_MESSAGE: 'Please enter a positive number',
  },
  INCOME: {
    MIN: 0,
    ERROR_MESSAGE: 'Income must be a positive number',
  },
};

/**
 * File upload constraints and configuration
 */
export const FILE_UPLOAD = {
  MAX_SIZE: 10 * 1024 * 1024, // 10MB in bytes
  ALLOWED_TYPES: [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/tiff',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  ],
  ALLOWED_EXTENSIONS: ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.doc', '.docx'],
  ERROR_MESSAGES: {
    SIZE: 'File size exceeds the maximum allowed size of 10MB',
    TYPE: 'File type not supported. Please upload a PDF, image, or Word document',
  },
};

/**
 * Theme mode constants
 */
export const THEME = {
  LIGHT: 'light',
  DARK: 'dark',
  SYSTEM: 'system',
};

/**
 * Standard error messages for consistent error handling
 */
export const ERROR_MESSAGES = {
  GENERIC: 'An unexpected error occurred. Please try again later.',
  NETWORK: 'Unable to connect to the server. Please check your internet connection and try again.',
  UNAUTHORIZED: 'Your session has expired. Please log in again.',
  FORBIDDEN: 'You do not have permission to perform this action.',
  NOT_FOUND: 'The requested resource was not found.',
  SERVER: 'The server encountered an error. Please try again later.',
  VALIDATION: 'Please correct the errors in the form before submitting.',
  TIMEOUT: 'The request timed out. Please try again.',
  REQUIRED_FIELD: 'This field is required.',
};

/**
 * Session timeout configuration (in milliseconds)
 */
export const SESSION = {
  TIMEOUT_DURATION: 30 * 60 * 1000, // 30 minutes
  WARNING_BEFORE: 5 * 60 * 1000, // Show warning 5 minutes before timeout
  PING_INTERVAL: 5 * 60 * 1000, // Check session every 5 minutes
};

/**
 * User roles that match backend role definitions
 */
export const USER_ROLES = {
  SYSTEM_ADMIN: 'SystemAdministrator',
  UNDERWRITER: 'Underwriter',
  QC: 'QualityControl',
  SCHOOL_ADMIN: 'SchoolAdministrator',
  BORROWER: 'Borrower',
  CO_BORROWER: 'CoBorrower',
};