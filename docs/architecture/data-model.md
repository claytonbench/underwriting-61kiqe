# Data Model Architecture

## Introduction

This document describes the data model architecture for the loan management system, including entity relationships, database schema, and data flow between components. The system uses PostgreSQL as the primary relational database with AWS S3 for document storage.

## Core Entities

### User Management

The user management component includes models for managing users, roles, and permissions across different user types (borrowers, co-borrowers, school administrators, internal staff).

#### User

Core user model that extends CoreModel and links to Auth0User for authentication.

**Key Fields:**
- `auth0_user`: Reference to Auth0 authentication profile
- `first_name`: User's first name
- `last_name`: User's last name
- `email`: User's email address (unique)
- `phone`: User's phone number
- `user_type`: Enumeration (Borrower, CoBorrower, SchoolAdmin, Underwriter, QC, SystemAdmin)
- `is_active`: Boolean indicating if the account is active

**Relationships:**
- One-to-one with Auth0User
- One-to-one with profile models based on user_type (BorrowerProfile, SchoolAdminProfile, InternalUserProfile)

**Key Methods:**
- `get_full_name()`: Returns the user's full name
- `get_profile()`: Returns the appropriate profile based on user_type
- `has_role(role_name)`: Checks if user has a specific role

#### BorrowerProfile

Profile model for borrowers with personal and financial information.

**Key Fields:**
- `user`: Foreign key to User
- `ssn`: Encrypted Social Security Number
- `dob`: Date of birth
- `citizenship_status`: Enumeration (USCitizen, PermanentResident, EligibleNonCitizen, Other)
- `address_line1`: Street address
- `address_line2`: Optional additional address information
- `city`: City
- `state`: State
- `zip_code`: ZIP code
- `housing_status`: Enumeration (Own, Rent, LiveWithParents, Other)
- `housing_payment`: Monthly housing payment amount

**Relationships:**
- One-to-one with User
- One-to-many with EmploymentInfo

**Key Methods:**
- `get_full_address()`: Returns the complete formatted address
- `get_age()`: Calculates age based on date of birth
- `is_eligible_by_age()`: Checks if borrower meets minimum age requirement
- `is_eligible_by_citizenship()`: Checks if borrower has eligible citizenship status

#### EmploymentInfo

Model for storing borrower employment and income information.

**Key Fields:**
- `profile`: Foreign key to BorrowerProfile
- `employment_type`: Enumeration (FullTime, PartTime, SelfEmployed, Unemployed, Retired, Student)
- `employer_name`: Name of employer
- `occupation`: Job title/occupation
- `employer_phone`: Employer contact phone
- `years_employed`: Years at current employer
- `months_employed`: Months at current employer
- `annual_income`: Annual gross income
- `other_income`: Additional income amount
- `other_income_source`: Source of additional income

**Relationships:**
- Many-to-one with BorrowerProfile

**Key Methods:**
- `get_total_income()`: Returns combined income from all sources
- `get_monthly_income()`: Calculates monthly income
- `get_total_employment_duration()`: Returns total employment duration in months
- `meets_minimum_employment()`: Checks if meets minimum employment duration
- `meets_minimum_income()`: Checks if meets minimum income requirements

#### SchoolAdminProfile

Profile model for school administrators.

**Key Fields:**
- `user`: Foreign key to User
- `school`: Foreign key to School
- `title`: Job title
- `department`: Department within school
- `is_primary_contact`: Boolean indicating if primary contact
- `can_sign_documents`: Boolean indicating if authorized to sign documents

**Relationships:**
- One-to-one with User
- Many-to-one with School

**Key Methods:**
- `get_managed_programs()`: Returns programs managed by this administrator

#### InternalUserProfile

Profile model for internal staff (underwriters, QC, system admins).

**Key Fields:**
- `user`: Foreign key to User
- `employee_id`: Internal employee identifier
- `department`: Department (Underwriting, QC, IT, etc.)
- `title`: Job title
- `supervisor`: Foreign key to another InternalUserProfile

**Relationships:**
- One-to-one with User
- Many-to-one with InternalUserProfile (supervisor)

**Key Methods:**
- `get_subordinates()`: Returns all users reporting to this user

#### UserPermission

Model for storing custom permissions for users beyond their role-based permissions.

**Key Fields:**
- `user`: Foreign key to User
- `permission_name`: Name of the permission
- `resource_type`: Type of resource the permission applies to
- `resource_id`: Identifier of the resource
- `is_granted`: Boolean indicating if permission is granted or denied

**Relationships:**
- Many-to-one with User

### School and Program Management

Models for managing schools, programs, and related entities that form the foundation for loan applications.

#### School

Model representing an educational institution that offers programs eligible for financing.

**Key Fields:**
- `name`: School name
- `legal_name`: Legal business name
- `tax_id`: Encrypted tax identification number
- `address_line1`: Street address
- `address_line2`: Optional additional address information
- `city`: City
- `state`: State
- `zip_code`: ZIP code
- `phone`: Contact phone number
- `website`: School website URL
- `status`: Enumeration (Active, Inactive, Pending, Suspended)

**Relationships:**
- One-to-many with Program
- One-to-many with SchoolContact
- One-to-many with SchoolAdminProfile

**Key Methods:**
- `get_active_programs()`: Returns active programs offered by the school
- `get_administrators()`: Returns users with admin access to this school
- `get_primary_contact()`: Returns the primary contact for the school
- `get_full_address()`: Returns the complete formatted address
- `get_applications()`: Returns applications associated with this school

#### Program

Model representing an educational program offered by a school.

**Key Fields:**
- `school`: Foreign key to School
- `name`: Program name
- `description`: Detailed program description
- `duration_hours`: Program length in hours
- `duration_weeks`: Program length in weeks
- `status`: Enumeration (Active, Inactive)

**Relationships:**
- Many-to-one with School
- One-to-many with ProgramVersion

**Key Methods:**
- `get_current_version()`: Returns the current active version
- `get_all_versions()`: Returns all versions of this program
- `get_current_tuition()`: Returns the current tuition amount
- `create_new_version()`: Creates a new version of this program

#### ProgramVersion

Model representing a specific version of a program with its tuition amount and effective date.

**Key Fields:**
- `program`: Foreign key to Program
- `version_number`: Sequential version number
- `effective_date`: Date when this version becomes effective
- `tuition_amount`: Cost of the program
- `is_current`: Boolean indicating if this is the current version

**Relationships:**
- Many-to-one with Program

#### SchoolDocument

Model representing a document associated with a school.

**Key Fields:**
- `school`: Foreign key to School
- `document_type`: Enumeration (Agreement, License, Insurance, Other)
- `file_name`: Original filename
- `file_path`: Path to file in storage
- `uploaded_at`: Timestamp of upload
- `uploaded_by`: Foreign key to User
- `status`: Enumeration (Pending, Verified, Rejected)

**Relationships:**
- Many-to-one with School
- Many-to-one with User (uploaded_by)

**Key Methods:**
- `get_download_url()`: Generates a secure URL for downloading the document

#### SchoolContact

Model representing a contact person for a school who is not necessarily a user.

**Key Fields:**
- `school`: Foreign key to School
- `first_name`: Contact's first name
- `last_name`: Contact's last name
- `title`: Job title
- `email`: Email address
- `phone`: Phone number
- `is_primary`: Boolean indicating if primary contact
- `can_sign_documents`: Boolean indicating if authorized to sign documents

**Relationships:**
- Many-to-one with School

**Key Methods:**
- `get_full_name()`: Returns the contact's full name

### Loan Application

Models for managing loan applications and related data, forming the core of the system's functionality.

#### LoanApplication

Core model representing a loan application in the system.

**Key Fields:**
- `borrower`: Foreign key to User (primary borrower)
- `co_borrower`: Foreign key to User (optional co-borrower)
- `school`: Foreign key to School
- `program`: Foreign key to Program
- `program_version`: Foreign key to ProgramVersion
- `application_type`: Enumeration (New, Refinance)
- `status`: Enumeration (Draft, Submitted, InReview, Approved, Denied, etc.)
- `relationship_type`: Enumeration for co-borrower relationship (Spouse, Parent, Other)
- `submission_date`: Date application was submitted

**Relationships:**
- Many-to-one with User (borrower)
- Many-to-one with User (co_borrower)
- Many-to-one with School
- Many-to-one with Program
- Many-to-one with ProgramVersion
- One-to-one with LoanDetails
- One-to-many with ApplicationDocument
- One-to-many with ApplicationStatusHistory
- One-to-one with UnderwritingDecision
- One-to-one with FundingRequest

**Key Methods:**
- `submit()`: Submits the application for review
- `is_editable()`: Checks if application can be edited
- `get_loan_details()`: Returns associated loan details
- `get_documents()`: Returns documents associated with application
- `get_status_history()`: Returns history of status changes
- `get_underwriting_decision()`: Returns underwriting decision
- `get_funding_request()`: Returns associated funding request

#### LoanDetails

Model storing financial details for a loan application.

**Key Fields:**
- `application`: Foreign key to LoanApplication
- `tuition_amount`: Full tuition amount
- `deposit_amount`: Amount of deposit paid
- `other_funding`: Amount from other funding sources
- `requested_amount`: Requested loan amount
- `approved_amount`: Approved loan amount (after underwriting)
- `start_date`: Program start date
- `completion_date`: Expected program completion date

**Relationships:**
- One-to-one with LoanApplication

**Key Methods:**
- `get_net_tuition()`: Calculates tuition minus deposit and other funding
- `get_program_duration_weeks()`: Calculates program duration from dates

#### ApplicationDocument

Model representing a document uploaded for a loan application.

**Key Fields:**
- `application`: Foreign key to LoanApplication
- `document_type`: Enumeration (IDDocument, ProofOfIncome, EnrollmentAgreement, etc.)
- `file_name`: Original filename
- `file_path`: Path to file in storage
- `uploaded_at`: Timestamp of upload
- `uploaded_by`: Foreign key to User
- `status`: Enumeration (Pending, Verified, Rejected)

**Relationships:**
- Many-to-one with LoanApplication
- Many-to-one with User (uploaded_by)

**Key Methods:**
- `get_download_url()`: Generates a secure URL for downloading the document
- `is_verified()`: Checks if document has been verified
- `verify()`: Marks document as verified

#### ApplicationStatusHistory

Model tracking status changes for loan applications.

**Key Fields:**
- `application`: Foreign key to LoanApplication
- `previous_status`: Previous application status
- `new_status`: New application status
- `changed_at`: Timestamp of status change
- `changed_by`: Foreign key to User who changed the status
- `comments`: Optional comments about the status change

**Relationships:**
- Many-to-one with LoanApplication
- Many-to-one with User (changed_by)

#### ApplicationNote

Model for storing notes related to loan applications.

**Key Fields:**
- `application`: Foreign key to LoanApplication
- `note_text`: Text content of the note
- `created_at`: Timestamp of creation
- `created_by`: Foreign key to User
- `is_internal`: Boolean indicating if note is internal only

**Relationships:**
- Many-to-one with LoanApplication
- Many-to-one with User (created_by)

### Underwriting

Models for managing the underwriting process, including application review, credit information, and decision-making.

#### UnderwritingQueue

Model representing an application in the underwriting queue.

**Key Fields:**
- `application`: Foreign key to LoanApplication
- `assigned_to`: Foreign key to User (underwriter)
- `assignment_date`: Date assigned to underwriter
- `priority`: Integer priority level
- `status`: Enumeration (Queued, InProgress, Completed, Returned)
- `due_date`: Date by which review should be completed

**Relationships:**
- One-to-one with LoanApplication
- Many-to-one with User (assigned_to)

**Key Methods:**
- `assign(underwriter)`: Assigns the application to an underwriter
- `start_review()`: Marks the application as in progress
- `complete()`: Marks the review as completed
- `return_to_queue()`: Returns the application to the queue
- `is_overdue()`: Checks if review is past due date

#### CreditInformation

Model for storing credit report information for borrowers and co-borrowers.

**Key Fields:**
- `application`: Foreign key to LoanApplication
- `borrower`: Foreign key to User
- `is_co_borrower`: Boolean indicating if for co-borrower
- `credit_score`: Credit score value
- `report_date`: Date of credit report
- `report_reference`: Reference ID for credit report
- `file_path`: Path to credit report file in storage
- `uploaded_by`: Foreign key to User
- `uploaded_at`: Timestamp of upload
- `monthly_debt`: Monthly debt obligations
- `debt_to_income_ratio`: Calculated DTI ratio

**Relationships:**
- Many-to-one with LoanApplication
- Many-to-one with User (borrower)
- Many-to-one with User (uploaded_by)

**Key Methods:**
- `get_credit_tier()`: Returns credit tier based on score
- `calculate_dti()`: Calculates debt-to-income ratio
- `get_download_url()`: Generates a secure URL for downloading the report

#### UnderwritingDecision

Model for recording underwriting decisions for loan applications.

**Key Fields:**
- `application`: Foreign key to LoanApplication
- `decision`: Enumeration (Approved, Denied, RevisionRequested)
- `decision_date`: Date decision was made
- `underwriter`: Foreign key to User
- `comments`: Decision comments
- `approved_amount`: Approved loan amount (if approved)
- `interest_rate`: Interest rate (if approved)
- `term_months`: Loan term in months (if approved)

**Relationships:**
- One-to-one with LoanApplication
- Many-to-one with User (underwriter)
- One-to-many with DecisionReason
- One-to-many with Stipulation

**Key Methods:**
- `update_application_status()`: Updates application status based on decision
- `get_reasons()`: Returns reasons for decision
- `get_stipulations()`: Returns stipulations for approval
- `is_approved()`: Checks if decision is approval
- `is_denied()`: Checks if decision is denial
- `is_revision_requested()`: Checks if revision was requested

#### DecisionReason

Model for storing reasons for underwriting decisions.

**Key Fields:**
- `decision`: Foreign key to UnderwritingDecision
- `reason_code`: Code representing reason
- `description`: Detailed description of reason
- `is_primary`: Boolean indicating if primary reason

**Relationships:**
- Many-to-one with UnderwritingDecision

#### Stipulation

Model for tracking required conditions for loan approval.

**Key Fields:**
- `application`: Foreign key to LoanApplication
- `stipulation_type`: Enumeration (DocumentRequired, IncomeVerification, etc.)
- `description`: Detailed description of stipulation
- `required_by_date`: Date by which stipulation must be satisfied
- `status`: Enumeration (Pending, Satisfied, Waived, Rejected)
- `created_at`: Creation timestamp
- `created_by`: Foreign key to User who created stipulation
- `satisfied_at`: Timestamp when satisfied
- `satisfied_by`: Foreign key to User who marked as satisfied

**Relationships:**
- Many-to-one with LoanApplication
- Many-to-one with User (created_by)
- Many-to-one with User (satisfied_by)
- One-to-many with StipulationVerification

**Key Methods:**
- `satisfy()`: Marks stipulation as satisfied
- `is_satisfied()`: Checks if stipulation is satisfied
- `is_pending()`: Checks if stipulation is pending
- `is_waived()`: Checks if stipulation is waived
- `is_overdue()`: Checks if stipulation is overdue

#### UnderwritingNote

Model for storing notes related to the underwriting process.

**Key Fields:**
- `application`: Foreign key to LoanApplication
- `note_text`: Text content of the note
- `created_at`: Timestamp of creation
- `created_by`: Foreign key to User
- `is_internal`: Boolean indicating if note is internal only

**Relationships:**
- Many-to-one with LoanApplication
- Many-to-one with User (created_by)

### Document Management

Models for managing document templates, generation, and e-signatures.

#### DocumentTemplate

Model for storing document templates used to generate loan documents.

**Key Fields:**
- `name`: Template name
- `description`: Template description
- `document_type`: Enumeration (LoanAgreement, CommitmentLetter, Disclosure, etc.)
- `file_path`: Path to template file in storage
- `version`: Version identifier
- `is_active`: Boolean indicating if template is active
- `created_at`: Creation timestamp
- `created_by`: Foreign key to User who created template

**Relationships:**
- Many-to-one with User (created_by)
- One-to-many with Document

**Key Methods:**
- `get_content()`: Returns template content

#### DocumentPackage

Model for grouping related documents that should be processed together.

**Key Fields:**
- `application`: Foreign key to LoanApplication
- `package_type`: Enumeration (ApprovalPackage, ClosingPackage, etc.)
- `status`: Enumeration (Preparing, Sent, PartiallyExecuted, FullyExecuted, Expired)
- `created_at`: Creation timestamp
- `expiration_date`: Date when package expires

**Relationships:**
- Many-to-one with LoanApplication
- One-to-many with Document

**Key Methods:**
- `get_documents()`: Returns documents in the package
- `is_complete()`: Checks if all documents are executed
- `is_expired()`: Checks if package is expired
- `update_status()`: Updates package status based on document statuses

#### Document

Model representing an individual document in the system.

**Key Fields:**
- `package`: Foreign key to DocumentPackage
- `document_type`: Enumeration (LoanAgreement, CommitmentLetter, Disclosure, etc.)
- `file_name`: Document filename
- `file_path`: Path to document file in storage
- `version`: Version identifier
- `status`: Enumeration (Draft, Sent, Signed, Rejected, Expired)
- `generated_at`: Timestamp of generation
- `generated_by`: Foreign key to User who generated document

**Relationships:**
- Many-to-one with DocumentPackage
- Many-to-one with User (generated_by)
- One-to-many with SignatureRequest
- One-to-many with DocumentField

**Key Methods:**
- `get_content()`: Returns document content
- `get_download_url()`: Generates a secure URL for downloading the document
- `get_signature_requests()`: Returns signature requests for this document
- `get_fields()`: Returns fields in the document
- `update_status()`: Updates document status
- `is_signed()`: Checks if document is fully signed
- `is_expired()`: Checks if document is expired

#### SignatureRequest

Model tracking signature requests for documents.

**Key Fields:**
- `document`: Foreign key to Document
- `signer`: Foreign key to User
- `signer_type`: Enumeration (Borrower, CoBorrower, SchoolAdmin, Internal)
- `status`: Enumeration (Pending, Completed, Declined, Expired)
- `requested_at`: Timestamp of request
- `completed_at`: Timestamp of completion
- `reminder_count`: Number of reminders sent
- `last_reminder_at`: Timestamp of last reminder
- `external_reference`: Reference ID in e-signature system

**Relationships:**
- Many-to-one with Document
- Many-to-one with User (signer)

**Key Methods:**
- `update_status()`: Updates request status
- `send_reminder()`: Sends signature reminder
- `can_send_reminder()`: Checks if reminder can be sent
- `get_signing_url()`: Generates URL for signing

#### DocumentField

Model representing a field in a document (signature, date, text, etc.).

**Key Fields:**
- `document`: Foreign key to Document
- `field_name`: Name of the field
- `field_type`: Enumeration (Signature, Date, Text, Checkbox, etc.)
- `field_value`: Value of the field (if applicable)
- `x_position`: X position on page
- `y_position`: Y position on page
- `page_number`: Page number

**Relationships:**
- Many-to-one with Document

**Key Methods:**
- `to_docusign_tab()`: Converts to DocuSign tab format

### Funding Process

Models for managing the funding process from QC approval to disbursement.

#### FundingRequest

Model representing a funding request for a loan application.

**Key Fields:**
- `application`: Foreign key to LoanApplication
- `status`: Enumeration (Pending, EnrollmentVerified, StipulationsVerified, Approved, Rejected, Disbursed)
- `requested_amount`: Requested funding amount
- `approved_amount`: Approved funding amount
- `requested_at`: Timestamp of request
- `requested_by`: Foreign key to User who requested funding
- `approved_at`: Timestamp of approval
- `approved_by`: Foreign key to User who approved funding
- `approval_level`: Enumeration (Level1, Level2, Level3) based on amount

**Relationships:**
- One-to-one with LoanApplication
- Many-to-one with User (requested_by)
- Many-to-one with User (approved_by)
- One-to-many with Disbursement
- One-to-one with EnrollmentVerification
- One-to-many with FundingNote
- One-to-many with StipulationVerification

**Key Methods:**
- `update_status()`: Updates request status
- `verify_enrollment()`: Marks enrollment as verified
- `check_stipulations()`: Checks if all stipulations are verified
- `approve()`: Approves funding request
- `reject()`: Rejects funding request
- `schedule_disbursement()`: Schedules disbursement
- `process_disbursement()`: Processes disbursement
- `cancel()`: Cancels funding request
- `get_enrollment_verification()`: Returns enrollment verification
- `get_disbursements()`: Returns disbursements
- `get_notes()`: Returns funding notes
- `get_required_approval_level()`: Determines required approval level
- `is_eligible_for_funding()`: Checks if eligible for funding

#### Disbursement

Model representing a disbursement of funds for a funding request.

**Key Fields:**
- `funding_request`: Foreign key to FundingRequest
- `amount`: Disbursement amount
- `disbursement_date`: Scheduled disbursement date
- `disbursement_method`: Enumeration (ACH, Wire, Check)
- `reference_number`: Reference number for transaction
- `status`: Enumeration (Scheduled, Processing, Completed, Failed, Cancelled)
- `processed_by`: Foreign key to User who processed disbursement
- `processed_at`: Timestamp of processing

**Relationships:**
- Many-to-one with FundingRequest
- Many-to-one with User (processed_by)

**Key Methods:**
- `process()`: Processes the disbursement
- `cancel()`: Cancels the disbursement
- `is_scheduled()`: Checks if disbursement is scheduled
- `is_completed()`: Checks if disbursement is completed
- `is_cancelled()`: Checks if disbursement is cancelled

#### EnrollmentVerification

Model for tracking enrollment verification for funding requests.

**Key Fields:**
- `funding_request`: Foreign key to FundingRequest
- `verification_type`: Enumeration (DocumentVerification, SystemVerification)
- `verified_by`: Foreign key to User who verified enrollment
- `verified_at`: Timestamp of verification
- `start_date`: Verified start date
- `comments`: Verification comments
- `document_id`: Reference to enrollment verification document

**Relationships:**
- One-to-one with FundingRequest
- Many-to-one with User (verified_by)

#### StipulationVerification

Model for tracking stipulation verification for funding requests.

**Key Fields:**
- `funding_request`: Foreign key to FundingRequest
- `stipulation`: Foreign key to Stipulation
- `status`: Enumeration (Pending, Verified, Rejected, Waived)
- `verified_by`: Foreign key to User who verified stipulation
- `verified_at`: Timestamp of verification
- `comments`: Verification comments

**Relationships:**
- Many-to-one with FundingRequest
- Many-to-one with Stipulation
- Many-to-one with User (verified_by)

**Key Methods:**
- `verify()`: Marks stipulation as verified
- `reject()`: Marks stipulation as rejected
- `waive()`: Waives the stipulation
- `is_verified()`: Checks if stipulation is verified
- `is_rejected()`: Checks if stipulation is rejected
- `is_waived()`: Checks if stipulation is waived
- `is_pending()`: Checks if stipulation is pending

#### FundingNote

Model for storing notes related to funding requests.

**Key Fields:**
- `funding_request`: Foreign key to FundingRequest
- `note_type`: Enumeration (General, QCReview, Disbursement)
- `note_text`: Text content of the note
- `created_at`: Timestamp of creation
- `created_by`: Foreign key to User who created the note

**Relationships:**
- Many-to-one with FundingRequest
- Many-to-one with User (created_by)

### Workflow Management

Models for managing workflow state transitions and tasks across the system.

#### WorkflowTransitionHistory

Model for tracking history of workflow state transitions.

**Key Fields:**
- `workflow_type`: Enumeration (ApplicationWorkflow, UnderwritingWorkflow, etc.)
- `from_state`: Previous state
- `to_state`: New state
- `transition_date`: Timestamp of transition
- `transitioned_by`: Foreign key to User who initiated transition
- `reason`: Reason for transition
- `transition_event`: Event that triggered transition
- `content_type`: Type of related object
- `object_id`: ID of related object

**Relationships:**
- Many-to-one with User (transitioned_by)
- Generic foreign key to any model (content_object)

#### AutomaticTransitionSchedule

Model for scheduling automatic state transitions.

**Key Fields:**
- `workflow_type`: Enumeration (ApplicationWorkflow, UnderwritingWorkflow, etc.)
- `from_state`: Current state
- `to_state`: Target state
- `scheduled_date`: Date/time for transition
- `is_executed`: Boolean indicating if executed
- `executed_at`: Timestamp of execution
- `reason`: Reason for transition
- `content_type`: Type of related object
- `object_id`: ID of related object

**Relationships:**
- Generic foreign key to any model (content_object)

**Key Methods:**
- `execute()`: Executes the scheduled transition

#### WorkflowTask

Model representing a task in a workflow process.

**Key Fields:**
- `task_type`: Enumeration (Review, Verification, Approval, etc.)
- `description`: Task description
- `status`: Enumeration (Pending, InProgress, Completed, Cancelled)
- `created_at`: Creation timestamp
- `due_date`: Task due date
- `completed_at`: Completion timestamp
- `assigned_to`: Foreign key to User assigned to task
- `completed_by`: Foreign key to User who completed task
- `notes`: Task notes
- `content_type`: Type of related object
- `object_id`: ID of related object

**Relationships:**
- Many-to-one with User (assigned_to)
- Many-to-one with User (completed_by)
- Generic foreign key to any model (content_object)

**Key Methods:**
- `complete()`: Marks task as completed
- `cancel()`: Cancels the task
- `reassign(user)`: Reassigns task to another user
- `is_overdue()`: Checks if task is overdue

#### WorkflowEntity

Abstract model providing workflow state functionality for models.

**Key Fields:**
- `current_state`: Current workflow state
- `state_changed_at`: Timestamp of last state change
- `state_changed_by`: Foreign key to User who changed state
- `is_terminal`: Boolean indicating if in terminal state
- `sla_due_at`: SLA due date/time

**Relationships:**
- Many-to-one with User (state_changed_by)

**Key Methods:**
- `get_workflow_type()`: Returns workflow type
- `get_transition_history()`: Returns transition history
- `get_pending_tasks()`: Returns pending tasks
- `calculate_sla_due_date()`: Calculates SLA due date based on state
- `update_sla_due_date()`: Updates SLA due date
- `is_sla_breached()`: Checks if SLA is breached

## Database Design

### Schema Organization

The database schema is organized into logical modules corresponding to the major functional areas of the system: user management, school management, loan applications, underwriting, document management, funding, and workflow management. Each module has its own set of tables with appropriate relationships between them.

This modular approach allows for:
- Clear separation of concerns
- Easier maintenance and updates
- Logical grouping of related entities
- Better query performance through focused indexes
- Simplified data access patterns

### Indexing Strategy

Indexes are created on frequently queried columns, foreign keys, and columns used in filtering operations. Composite indexes are used for queries that filter on multiple columns. Unique indexes are applied to fields requiring uniqueness constraints.

Key indexing patterns include:
- Primary keys: All tables have UUID primary keys
- Foreign keys: All foreign key columns are indexed
- Lookup fields: Fields commonly used in WHERE clauses (status, type fields)
- Search fields: Fields used for searching (names, IDs, dates)
- Sorting fields: Fields commonly used for sorting (creation dates, status)
- Unique constraints: Fields requiring uniqueness (email addresses, external references)

### Data Integrity

Data integrity is maintained through:
- Foreign key constraints to enforce relationships between tables
- Check constraints for field validation
- Unique constraints for preventing duplicates
- Not-null constraints for required fields
- Default values for consistency
- Validation at both the database and application levels
- Transaction management for operations that affect multiple tables

### Performance Considerations

The schema is designed with performance in mind:
- Appropriate data types for each field to minimize storage requirements
- Normalization to reduce redundancy while maintaining query efficiency
- Strategic denormalization where necessary for reporting and analytics
- Partitioning of large tables (application_status_history, notifications)
- Indexing strategy optimized for common query patterns
- Query optimization through execution plan analysis
- Regular database maintenance (VACUUM, ANALYZE)

## Data Storage

### Relational Data

PostgreSQL is used as the primary database for storing all structured data, including user information, application data, and workflow state.

PostgreSQL was chosen for its:
- Robust transaction support ensuring data consistency
- Advanced data types (UUID, JSON, Array, etc.)
- Strong support for complex relationships
- Excellent performance with properly designed queries
- Rich ecosystem of tools and extensions
- Enterprise-grade reliability and security features
- Support for advanced features like partitioning and replication

### Document Storage

AWS S3 is used for storing documents and files, with metadata about the documents stored in the PostgreSQL database.

This hybrid approach provides:
- Scalable, secure storage for loan documents
- Versioning capabilities for document history
- Efficient storage and retrieval of large files
- Cost-effective long-term storage
- Separate backup and retention policies
- Ability to generate pre-signed URLs for secure access

Document references in the database include:
- Metadata (filename, type, creation date)
- S3 bucket and key information
- Status and relationship to entities
- Security and access control information

### Caching

Redis is used for caching frequently accessed data such as:
- Reference data (schools, programs, document templates)
- User sessions and authentication information
- Application status and summary information
- Frequently accessed configuration settings

Redis provides:
- In-memory performance for frequently accessed data
- Support for complex data structures (lists, sets, sorted sets)
- Atomic operations for counters and rate limiting
- Pub/sub capabilities for real-time notifications
- Persistence options for durability
- Cluster support for scalability

## Data Flow

### Application Submission

When a loan application is submitted:
1. The frontend collects and validates application data
2. Data is sent to the application service via API
3. The service performs comprehensive validation
4. A database transaction begins
5. Core application data is stored in the LoanApplication table
6. Related data is stored in associated tables (LoanDetails, etc.)
7. Uploaded documents are stored in S3 with references in ApplicationDocument
8. Application status is set to "Submitted"
9. Status history is recorded in ApplicationStatusHistory
10. The transaction is committed
11. The application is placed in the underwriting queue
12. Notifications are sent to appropriate parties

### Underwriting Process

During the underwriting process:
1. Underwriters retrieve applications from the queue
2. Credit information is uploaded and associated with the application
3. Application and supporting documents are reviewed
4. Underwriting notes are recorded during review
5. The underwriter makes a decision (approve, deny, request revision)
6. Decision details are recorded in UnderwritingDecision
7. Decision reasons are recorded in DecisionReason
8. For approvals, stipulations are created in Stipulation
9. Application status is updated to reflect the decision
10. Notifications are sent to appropriate parties
11. For approvals, the document generation process is triggered

### Document Generation

When documents need to be generated:
1. The document service identifies required documents based on application state
2. Document templates are retrieved from DocumentTemplate
3. Templates are populated with application data
4. Generated documents are stored in S3
5. Document metadata is stored in Document
6. Documents are grouped into a DocumentPackage
7. Signature fields are defined in DocumentField
8. The package status is updated to "Prepared"
9. The application status is updated to reflect document status
10. Notifications and signature requests are sent

### Signature Collection

During the e-signature process:
1. Signature requests are created in SignatureRequest
2. E-signature requests are sent via DocuSign
3. Signers receive email notifications with signing links
4. Signers complete signing in DocuSign
5. DocuSign sends webhooks with signature updates
6. SignatureRequest records are updated with signature status
7. When all signatures are collected, Document status is updated
8. When all documents in a package are signed, DocumentPackage status is updated
9. The application moves to the next stage in the workflow
10. Notifications are sent to appropriate parties

### Funding Process

During the funding process:
1. Quality Control review is completed on signed documents
2. A FundingRequest is created for the application
3. Enrollment verification is performed and recorded in EnrollmentVerification
4. Stipulations are verified and recorded in StipulationVerification
5. When all requirements are met, the request is sent for approval
6. Approvers review and approve the funding request
7. Disbursement is scheduled in Disbursement
8. The disbursement is processed on the scheduled date
9. The application status is updated to "Funded"
10. Notifications are sent to appropriate parties

## Security Considerations

### Data Encryption

Sensitive personal information such as SSNs and tax IDs are encrypted at the column level using the EncryptedField type. Encryption is implemented using:
- AES-256 encryption for sensitive fields
- AWS KMS for key management
- Envelope encryption with data encryption keys
- Different encryption contexts for different data types
- Automatic encryption/decryption through model layer

All data is encrypted at rest in the database and in S3 using:
- Database-level encryption for PostgreSQL
- S3 server-side encryption for document storage
- Encrypted backups and snapshots

### Access Control

Access to data is controlled through:
- Role-based permissions defining what actions users can perform
- Row-level security ensuring users can only access authorized data
- Object-level permissions for specific resources
- Field-level access control for sensitive data
- API authorization checks at multiple levels

The system implements:
- Explicit permission checks before data access
- Data filtering based on user context
- Attribute-based access control for complex scenarios
- Logging of access attempts for security auditing

### Audit Logging

All significant data changes are logged in audit tables, including:
- Who made the change (user ID)
- When it was made (timestamp)
- What was changed (before/after values)
- Why it was changed (context/reason)
- How it was changed (source/endpoint)

This provides:
- Comprehensive audit trail for compliance
- Ability to reconstruct history of changes
- Support for forensic analysis if needed
- Accountability for all system actions

### Compliance

The data model is designed to support compliance with regulations such as:
- GLBA (Gramm-Leach-Bliley Act): Protection of personal financial information
- FCRA (Fair Credit Reporting Act): Proper handling of credit information
- ECOA (Equal Credit Opportunity Act): Fair and consistent underwriting
- E-SIGN Act: Legal validity of electronic signatures

Compliance features include:
- Data retention policies with appropriate timeframes
- Data minimization to collect only necessary information
- Documentation of data usage and purpose
- Support for data subject access requests
- Secure data disposal processes