# src/web/src/components/ApplicationReview/tests/ApplicationReview.test.tsx
```typescript
import React from 'react'; // react ^18.2.0
import { render, screen, waitFor, fireEvent } from '@testing-library/react'; // @testing-library/react ^14.0.0
import { axe, toHaveNoViolations } from 'jest-axe'; // jest-axe ^7.0.0
import ApplicationReview from '../ApplicationReview';
import { getApplication } from '../../../api/applications';
import { getCreditInformation, getUnderwritingDecision } from '../../../api/underwriting';
import { ApplicationDetail, CreditInformation, UnderwritingDecisionData, CreditScoreTier, UnderwritingDecision } from '../../../types/application.types';

// Extend Jest expect to include axe matchers
expect.extend(toHaveNoViolations);

// Define mock data for testing
const mockApplicationData: ApplicationDetail = {
  application: {
    id: 'test-app-id',
    borrower_id: 'borrower-id',
    co_borrower_id: 'co-borrower-id',
    school_id: 'school-id',
    program_id: 'program-id',
    program_version_id: 'program-version-id',
    status: 'IN_REVIEW',
    submission_date: '2023-05-01T00:00:00Z',
    last_updated: '2023-05-02T00:00:00Z',
    created_by: 'creator-id',
    created_at: '2023-05-01T00:00:00Z',
  },
  loan_details: {
    application_id: 'test-app-id',
    tuition_amount: 10000,
    deposit_amount: 1000,
    other_funding: 0,
    requested_amount: 9000,
    approved_amount: null,
    start_date: '2023-06-01T00:00:00Z',
    completion_date: '2023-12-01T00:00:00Z',
  },
  borrower: {
    user_id: 'borrower-id',
    first_name: 'John',
    last_name: 'Smith',
    email: 'john@example.com',
    phone: '555-123-4567',
    ssn: 'XXX-XX-1234',
    dob: '1990-01-01',
    citizenship_status: 'US_CITIZEN',
    address_line1: '123 Main St',
    address_line2: 'Apt 4B',
    city: 'Anytown',
    state: 'CA',
    zip_code: '12345',
    housing_status: 'RENT',
    housing_payment: 1500,
    employment_info: {
      employment_type: 'FULL_TIME',
      employer_name: 'Tech Company',
      occupation: 'Software Developer',
      employer_phone: '555-987-6543',
      years_employed: 3,
      months_employed: 6,
      annual_income: 85000,
      other_income: 0,
      other_income_source: null,
    }
  },
  co_borrower: {
    user_id: 'co-borrower-id',
    first_name: 'Jane',
    last_name: 'Smith',
    email: 'jane@example.com',
    phone: '555-765-4321',
    ssn: 'XXX-XX-5678',
    dob: '1992-02-02',
    citizenship_status: 'US_CITIZEN',
    address_line1: '123 Main St',
    address_line2: 'Apt 4B',
    city: 'Anytown',
    state: 'CA',
    zip_code: '12345',
    housing_status: 'RENT',
    housing_payment: 1500,
    employment_info: {
      employment_type: 'FULL_TIME',
      employer_name: 'Marketing Agency',
      occupation: 'Marketing Manager',
      employer_phone: '555-876-5432',
      years_employed: 2,
      months_employed: 8,
      annual_income: 75000,
      other_income: 0,
      other_income_source: null,
    }
  },
  school: {
    id: 'school-id',
    name: 'ABC School',
    address_line1: '456 Education Ave',
    city: 'Learning City',
    state: 'NY',
    zip_code: '54321',
    status: 'ACTIVE',
  },
  program: {
    id: 'program-id',
    school_id: 'school-id',
    name: 'Web Development Bootcamp',
    description: 'Intensive coding bootcamp',
    duration_weeks: 24,
    status: 'ACTIVE',
  },
  program_version: {
    id: 'program-version-id',
    program_id: 'program-id',
    version_number: 1,
    effective_date: '2023-01-01T00:00:00Z',
    tuition_amount: 10000,
    is_current: true,
  },
  documents: [
    {
      id: 'doc-id-1',
      application_id: 'test-app-id',
      document_type: 'IDENTIFICATION',
      file_name: 'drivers_license.pdf',
      file_path: '/documents/test-app-id/drivers_license.pdf',
      uploaded_at: '2023-05-01T00:00:00Z',
      uploaded_by: 'borrower-id',
      status: 'COMPLETED',
      download_url: '/api/documents/doc-id-1/download',
      signature_requests: []
    },
    {
      id: 'doc-id-2',
      application_id: 'test-app-id',
      document_type: 'INCOME_VERIFICATION',
      file_name: 'paystub.pdf',
      file_path: '/documents/test-app-id/paystub.pdf',
      uploaded_at: '2023-05-01T00:00:00Z',
      uploaded_by: 'borrower-id',
      status: 'COMPLETED',
      download_url: '/api/documents/doc-id-2/download',
      signature_requests: []
    }
  ],
  status_history: [
    {
      id: 'history-id-1',
      application_id: 'test-app-id',
      previous_status: 'DRAFT',
      new_status: 'SUBMITTED',
      changed_at: '2023-05-01T00:00:00Z',
      changed_by: 'borrower-id',
      comments: 'Application submitted by borrower',
    },
    {
      id: 'history-id-2',
      application_id: 'test-app-id',
      previous_status: 'SUBMITTED',
      new_status: 'IN_REVIEW',
      changed_at: '2023-05-02T00:00:00Z',
      changed_by: 'underwriter-id',
      comments: 'Application assigned to underwriter',
    },
  ],
};

const mockBorrowerCreditData: CreditInformation = {
  id: 'credit-id-1',
  application_id: 'test-app-id',
  borrower_id: 'borrower-id',
  is_co_borrower: false,
  credit_score: 720,
  credit_tier: CreditScoreTier.GOOD,
  report_date: '2023-05-01T00:00:00Z',
  report_reference: 'CR-12345',
  file_path: '/credit/test-app-id/borrower-credit.pdf',
  monthly_debt: 1200,
  debt_to_income_ratio: 0.32,
  uploaded_at: '2023-05-01T00:00:00Z',
  download_url: '/api/credit/credit-id-1/download',
};

const mockCoBorrowerCreditData: CreditInformation = {
  id: 'credit-id-2',
  application_id: 'test-app-id',
  borrower_id: 'co-borrower-id',
  is_co_borrower: true,
  credit_score: 680,
  credit_tier: CreditScoreTier.GOOD,
  report_date: '2023-05-01T00:00:00Z',
  report_reference: 'CR-67890',
  file_path: '/credit/test-app-id/co-borrower-credit.pdf',
  monthly_debt: 900,
  debt_to_income_ratio: 0.28,
  uploaded_at: '2023-05-01T00:00:00Z',
  download_url: '/api/credit/credit-id-2/download',
};

const mockUnderwritingDecisionData: UnderwritingDecisionData = {
  application_id: 'test-app-id',
  decision: UnderwritingDecision.APPROVE,
  decision_date: '2023-05-03T00:00:00Z',
  underwriter_id: 'underwriter-id',
  comments: 'Application meets all approval criteria',
  approved_amount: 9000,
  interest_rate: 5.25,
  term_months: 36,
  reasons: [
    {
      id: 'reason-id-1',
      decision_id: 'decision-id',
      reason_code: 'CREDIT_SCORE',
      description: 'Good credit history',
      is_primary: true,
    },
  ],
  stipulations: [
    {
      id: 'stip-id-1',
      application_id: 'test-app-id',
      stipulation_type: 'ENROLLMENT_AGREEMENT',
      category: 'EDUCATION_DOCUMENTATION',
      description: 'Signed enrollment agreement required',
      required_by_date: '2023-05-15T00:00:00Z',
      status: 'PENDING',
      created_at: '2023-05-03T00:00:00Z',
      created_by: 'underwriter-id',
      satisfied_at: null,
      satisfied_by: null,
      is_overdue: false,
    },
  ],
};

// Mock API functions
jest.mock('../../../api/applications');
jest.mock('../../../api/underwriting');

const mockGetApplication = getApplication as jest.MockedFunction<typeof getApplication>;
const mockGetCreditInformation = getCreditInformation as jest.MockedFunction<typeof getCreditInformation>;
const mockGetUnderwritingDecision = getUnderwritingDecision as jest.MockedFunction<typeof getUnderwritingDecision>;

/**
 * Sets up mocks for API functions before each test
 */
const setup = () => {
  mockGetApplication.mockResolvedValue({ success: true, message: null, data: mockApplicationData, errors: null });
  mockGetCreditInformation.mockImplementation((applicationId, borrowerId, isCoBorrower) => {
    return Promise.resolve({ success: true, message: null, data: isCoBorrower ? mockCoBorrowerCreditData : mockBorrowerCreditData, errors: null });
  });
  mockGetUnderwritingDecision.mockResolvedValue({ success: true, message: null, data: mockUnderwritingDecisionData, errors: null });
};

describe('ApplicationReview Component', () => {
  beforeEach(() => {
    setup();
  });

  it('renders loading state initially', async () => {
    render(<ApplicationReview applicationId="test-app-id" />);
    expect(screen.getByText(/Loading application details/i)).toBeInTheDocument();
    expect(screen.queryByText(/Borrower Information/i)).not.toBeInTheDocument();
  });

  it('renders application data when loaded', async () => {
    render(<ApplicationReview applicationId="test-app-id" />);
    await waitFor(() => expect(screen.getByText(/Borrower Information/i)).toBeInTheDocument());
    expect(screen.getByText(/John Smith/i)).toBeInTheDocument();
    expect(screen.getByText(/Web Development Bootcamp/i)).toBeInTheDocument();
    expect(screen.getByText(/\$9,000.00/i)).toBeInTheDocument();
  });

  it('renders error state when API call fails', async () => {
    mockGetApplication.mockRejectedValue(new Error('Failed to fetch'));
    render(<ApplicationReview applicationId="test-app-id" />);
    await waitFor(() => expect(screen.getByText(/An unexpected error occurred while fetching application details/i)).toBeInTheDocument());
    expect(screen.queryByText(/Borrower Information/i)).not.toBeInTheDocument();
  });

  it('displays co-borrower information when available', async () => {
    render(<ApplicationReview applicationId="test-app-id" />);
    await waitFor(() => expect(screen.getByText(/Co-Borrower Information/i)).toBeInTheDocument());
    expect(screen.getByText(/Jane Smith/i)).toBeInTheDocument();
  });

  it('does not display co-borrower section when no co-borrower exists', async () => {
    mockGetApplication.mockResolvedValue({
      success: true,
      message: null,
      data: { ...mockApplicationData, co_borrower: null },
      errors: null,
    });
    render(<ApplicationReview applicationId="test-app-id" />);
    await waitFor(() => expect(screen.queryByText(/Co-Borrower Information/i)).not.toBeInTheDocument());
  });

  it('displays credit information correctly', async () => {
    render(<ApplicationReview applicationId="test-app-id" />);
    await waitFor(() => expect(screen.getByText(/Borrower Information/i)).toBeInTheDocument());

    fireEvent.click(screen.getByText(/Credit Info/i));

    await waitFor(() => {
      expect(screen.getByText(/720/i)).toBeInTheDocument();
      expect(screen.getByText(/32%/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/680/i)).toBeInTheDocument();
    expect(screen.getByText(/28%/i)).toBeInTheDocument();
  });

  it('displays documents section correctly', async () => {
    render(<ApplicationReview applicationId="test-app-id" />);
    await waitFor(() => expect(screen.getByText(/Borrower Information/i)).toBeInTheDocument());

    fireEvent.click(screen.getByText(/Documents/i));

    await waitFor(() => {
      expect(screen.getByText(/drivers_license.pdf/i)).toBeInTheDocument();
      expect(screen.getByText(/paystub.pdf/i)).toBeInTheDocument();
    });
  });

  it('displays underwriting decision when available', async () => {
    render(<ApplicationReview applicationId="test-app-id" />);
    await waitFor(() => expect(screen.getByText(/Borrower Information/i)).toBeInTheDocument());

    fireEvent.click(screen.getByText(/Underwriting Decision/i));

    await waitFor(() => {
      expect(screen.getByText(/Approved/i)).toBeInTheDocument();
      expect(screen.getByText(/Application meets all approval criteria/i)).toBeInTheDocument();
      expect(screen.getByText(/Signed enrollment agreement required/i)).toBeInTheDocument();
    });
  });

  it('handles tab switching correctly', async () => {
    render(<ApplicationReview applicationId="test-app-id" />);
    await waitFor(() => expect(screen.getByText(/Borrower Information/i)).toBeInTheDocument());

    fireEvent.click(screen.getByText(/Loan Details/i));
    expect(screen.getByText(/School:/i)).toBeInTheDocument();

    fireEvent.click(screen.getByText(/Credit Info/i));
    expect(screen.getByText(/Credit Score/i)).toBeInTheDocument();

    fireEvent.click(screen.getByText(/Documents/i));
    expect(screen.getByText(/drivers_license.pdf/i)).toBeInTheDocument();
  });

  it('applies read-only mode when specified', async () => {
    render(<ApplicationReview applicationId="test-app-id" readOnly={true} />);
    await waitFor(() => expect(screen.getByText(/Borrower Information/i)).toBeInTheDocument());

    fireEvent.click(screen.getByText(/Documents/i));

    await waitFor(() => {
      const viewButtons = screen.getAllByText(/View/i);
      viewButtons.forEach(button => expect(button).toBeDisabled());
    });
  });

  it('has no accessibility violations', async () => {
    const { container } = render(<ApplicationReview applicationId="test-app-id" />);
    await waitFor(() => expect(screen.getByText(/Borrower Information/i)).toBeInTheDocument());
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});