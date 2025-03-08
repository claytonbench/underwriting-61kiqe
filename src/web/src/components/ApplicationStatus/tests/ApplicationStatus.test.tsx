import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe'; // v7.0.0
import ApplicationStatus from '../ApplicationStatus';
import { 
  ApplicationDetail, 
  ApplicationRequiredAction, 
  ApplicationStatus as ApplicationStatusEnum 
} from '../../../types/application.types';

// Add Jest-axe matcher
expect.extend(toHaveNoViolations);

/**
 * Creates a mock ApplicationDetail object for testing
 */
const createMockApplicationDetail = (overrides?: Partial<ApplicationDetail>): ApplicationDetail => {
  const mockData = {
    application: {
      id: 'mock-app-id',
      status: ApplicationStatusEnum.APPROVED,
      submission_date: '2023-01-15T00:00:00Z',
      last_updated: '2023-01-20T00:00:00Z',
    },
    loan_details: {
      requested_amount: 10000,
      approved_amount: 10000,
      start_date: '2023-06-01T00:00:00Z',
      completion_date: '2023-09-01T00:00:00Z',
    },
    school: {
      name: 'ABC School',
    },
    program: {
      name: 'Web Development Bootcamp',
    },
    status_history: [
      {
        id: 'history-1',
        previous_status: ApplicationStatusEnum.DRAFT,
        new_status: ApplicationStatusEnum.SUBMITTED,
        changed_at: '2023-01-15T00:00:00Z',
        changed_by: 'user-1',
        comments: null,
      },
      {
        id: 'history-2',
        previous_status: ApplicationStatusEnum.SUBMITTED,
        new_status: ApplicationStatusEnum.IN_REVIEW,
        changed_at: '2023-01-16T00:00:00Z',
        changed_by: 'user-2',
        comments: null,
      },
      {
        id: 'history-3',
        previous_status: ApplicationStatusEnum.IN_REVIEW,
        new_status: ApplicationStatusEnum.APPROVED,
        changed_at: '2023-01-20T00:00:00Z',
        changed_by: 'user-3',
        comments: null,
      },
    ],
  };
  
  return { ...mockData, ...overrides } as ApplicationDetail;
};

/**
 * Creates an array of mock ApplicationRequiredAction objects for testing
 */
const createMockRequiredActions = (count: number): ApplicationRequiredAction[] => {
  return Array.from({ length: count }, (_, index) => ({
    id: `action-${index + 1}`,
    application_id: 'mock-app-id',
    action_type: index % 2 === 0 ? 'SIGN_DOCUMENT' : 'UPLOAD_DOCUMENT',
    description: index % 2 === 0 ? 'Sign Loan Agreement' : 'Upload Proof of Income',
    due_date: index % 2 === 0 ? '2023-02-20T00:00:00Z' : null,
    status: 'pending',
    related_entity_id: index % 2 === 0 ? 'doc-1' : null,
    related_entity_type: index % 2 === 0 ? 'document' : null,
  }));
};

/**
 * Helper function to render the ApplicationStatus component with mock props
 */
const renderApplicationStatus = (props = {}) => {
  const defaultProps = {
    applicationDetail: createMockApplicationDetail(),
    requiredActions: createMockRequiredActions(2),
    onAction: jest.fn(),
  };
  
  return render(
    <ApplicationStatus 
      {...defaultProps} 
      {...props} 
    />
  );
};

describe('ApplicationStatus component', () => {
  test('renders application details correctly', () => {
    renderApplicationStatus();
    
    // Check if application status section is present
    expect(screen.getByLabelText('Application status and details')).toBeInTheDocument();
    
    // Check if school and program information is displayed
    expect(screen.getByText('School')).toBeInTheDocument();
    expect(screen.getByText('ABC School')).toBeInTheDocument();
    expect(screen.getByText('Program')).toBeInTheDocument();
    expect(screen.getByText('Web Development Bootcamp')).toBeInTheDocument();
    
    // Check if financial details are displayed
    expect(screen.getByText('Requested Amount')).toBeInTheDocument();
    expect(screen.getByText('$10,000.00')).toBeInTheDocument();
    expect(screen.getByText('Approved Amount')).toBeInTheDocument();
    
    // Check if dates are displayed
    expect(screen.getByText('Submission Date')).toBeInTheDocument();
    expect(screen.getByText('01/15/2023')).toBeInTheDocument();
    expect(screen.getByText('Last Updated')).toBeInTheDocument();
    expect(screen.getByText('01/20/2023')).toBeInTheDocument();
  });

  test('displays correct status badge', () => {
    renderApplicationStatus({
      applicationDetail: createMockApplicationDetail({
        application: {
          id: 'mock-app-id',
          status: ApplicationStatusEnum.IN_REVIEW,
          submission_date: '2023-01-15T00:00:00Z',
          last_updated: '2023-01-16T00:00:00Z',
        },
      }),
    });
    
    // StatusBadge components use an aria-label with the format "Status: {status}"
    const statusBadge = screen.getByLabelText('Status: In Review');
    expect(statusBadge).toBeInTheDocument();
  });

  test('renders StatusTimeline component', () => {
    renderApplicationStatus();
    
    // Check if the Application Timeline section is rendered
    expect(screen.getByText('Application Timeline')).toBeInTheDocument();
    
    // Check if the timeline is accessible
    expect(screen.getByLabelText('Application status timeline')).toBeInTheDocument();
  });

  test('renders RequiredActions component', () => {
    renderApplicationStatus();
    
    // Check if the Required Actions section is rendered
    expect(screen.getByText('Required Actions')).toBeInTheDocument();
    
    // Check if actions are displayed
    expect(screen.getByText('Sign Loan Agreement')).toBeInTheDocument();
    expect(screen.getByText('Upload Proof of Income')).toBeInTheDocument();
    
    // Check if due date is displayed
    expect(screen.getByText('Due by 02/20/2023')).toBeInTheDocument();
    
    // Check if action buttons are displayed
    expect(screen.getByRole('button', { name: /Sign Now Sign Loan Agreement/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Upload Upload Proof of Income/i })).toBeInTheDocument();
  });

  test('handles action button clicks', () => {
    const mockOnAction = jest.fn();
    renderApplicationStatus({ onAction: mockOnAction });
    
    // Find and click the action button
    const signButton = screen.getByRole('button', { name: /Sign Now Sign Loan Agreement/i });
    fireEvent.click(signButton);
    
    // Verify that the onAction callback was called with the correct parameters
    expect(mockOnAction).toHaveBeenCalledWith('SIGN_DOCUMENT', {
      id: 'action-1',
      entityId: 'doc-1',
      entityType: 'document',
    });
  });

  test('has no accessibility violations', async () => {
    const { container } = renderApplicationStatus();
    
    // Run axe accessibility tests
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});