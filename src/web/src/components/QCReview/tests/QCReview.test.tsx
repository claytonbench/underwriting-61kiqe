import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react'; // React Testing Library for rendering and interacting with components // version: ^14.0.0
import userEvent from '@testing-library/user-event'; // Simulates user interactions more realistically than fireEvent // version: ^14.4.3
import { Provider } from 'react-redux'; // Redux Provider for testing components with Redux state // version: ^8.1.1
import { configureStore } from '@reduxjs/toolkit'; // Create a Redux store for testing // version: ^1.9.5
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'; // Testing framework and assertions // version: ^0.34.1

import QCReviewComponent from '../QCReview'; // The component being tested
import { QCReview, QCVerificationStatus, QCStatus, QCReturnReason } from '../../../types/qc.types'; // Type definitions for QC review data
import { selectSelectedQCReview, selectLoading, selectError } from '../../../store/slices/qcSlice'; // Redux selectors for QC state
import { verifyDocumentThunk, rejectDocumentThunk, verifyStipulationThunk, rejectStipulationThunk, waiveStipulationThunk, verifyChecklistItemThunk, rejectChecklistItemThunk, submitQCDecisionThunk } from '../../../store/thunks/qcThunks'; // Redux thunks for QC operations

/**
 * Helper function to set up the test environment with a mock Redux store
 */
const setup = (initialState = {}) => {
  // Create a mock Redux store with the provided initial state
  const store = configureStore({
    reducer: {
      qc: (state = initialState) => state,
    },
  });

  // Set up userEvent for simulating user interactions
  const user = userEvent.setup();

  // Create a render function that wraps the component in a Redux Provider
  const renderWithProvider = (ui: React.ReactElement) => {
    return render(<Provider store={store}>{ui}</Provider>);
  };

  // Return the store, user, and render function
  return { store, user, render: renderWithProvider };
};

/**
 * Helper function to create a mock QC review object for testing
 */
const createMockQCReview = (overrides: Partial<QCReview> = {}): QCReview => {
  // Create a default mock QC review with all required properties
  const defaultQCReview: QCReview = {
    id: 'qc-review-1',
    application_id: 'app-1',
    application: {
      id: 'app-1',
      borrower_id: 'borrower-1',
      co_borrower_id: null,
      school_id: 'school-1',
      program_id: 'program-1',
      program_version_id: 'version-1',
      status: 'submitted',
      submission_date: '2024-01-01',
      last_updated: '2024-01-01',
      created_by: 'user-1',
      created_at: '2024-01-01',
    },
    status: QCStatus.PENDING,
    priority: 'medium',
    assigned_to: null,
    assigned_to_name: null,
    assignment_type: 'automatic',
    assigned_at: null,
    completed_at: null,
    return_reason: null,
    notes: null,
    document_verifications: [],
    stipulation_verifications: [],
    checklist_items: [],
    completion_percentage: 0,
    created_at: '2024-01-01',
    updated_at: '2024-01-01',
  };

  // Merge any provided overrides into the default mock
  return { ...defaultQCReview, ...overrides };
};

describe('QCReview Component', () => {
  it('renders loading state correctly', () => {
    // Set up test with loading state set to true
    const { render } = setup({ loading: true });

    // Render the QCReview component with required props
    render(<QCReviewComponent qcReviewId="qc-review-1" applicationId="app-1" />);

    // Verify that a loading indicator is displayed
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('renders error state correctly', () => {
    // Set up test with an error message in state
    const { render } = setup({ error: 'An error occurred' });

    // Render the QCReview component with required props
    render(<QCReviewComponent qcReviewId="qc-review-1" applicationId="app-1" />);

    // Verify that the error message is displayed
    expect(screen.getByText('An error occurred')).toBeInTheDocument();
  });

  it('renders empty state correctly', () => {
    // Set up test with selectedQCReview set to null
    const { render } = setup({ selectedQCReview: null });

    // Render the QCReview component with required props
    render(<QCReviewComponent qcReviewId="qc-review-1" applicationId="app-1" />);

    // Verify that an empty state message is displayed
    expect(screen.getByText('No QC review data available.')).toBeInTheDocument();
  });

  it('renders QC review data correctly', () => {
    // Create a mock QC review with documents, stipulations, and checklist items
    const mockQCReview = createMockQCReview({
      document_verifications: [{ id: 'doc-1', qc_review_id: 'qc-review-1', document_id: 'doc', document: { id: 'doc', document_type: 'Loan Agreement', file_name: 'loan.pdf', file_path: '/path', version: '1', status: 'generated', generated_at: '2024-01-01', generated_by: 'user-1', application_id: 'app-1', download_url: '/download' }, status: QCVerificationStatus.UNVERIFIED, verified_by: null, verified_by_name: null, verified_at: null, comments: null, created_at: '2024-01-01', updated_at: '2024-01-01' }],
      stipulation_verifications: [{ id: 'stip-1', qc_review_id: 'qc-review-1', stipulation_id: 'stip', stipulation_description: 'Proof of Income', status: QCVerificationStatus.UNVERIFIED, verified_by: null, verified_by_name: null, verified_at: null, comments: null, created_at: '2024-01-01', updated_at: '2024-01-01' }],
      checklist_items: [{ id: 'check-1', qc_review_id: 'qc-review-1', category: 'document_completeness', item_text: 'All documents present', status: QCVerificationStatus.UNVERIFIED, verified_by: null, verified_by_name: null, verified_at: null, comments: null, created_at: '2024-01-01', updated_at: '2024-01-01' }],
    });

    // Set up test with the mock QC review in state
    const { render } = setup({ selectedQCReview: mockQCReview });

    // Render the QCReview component with required props
    render(<QCReviewComponent qcReviewId="qc-review-1" applicationId="app-1" />);

    // Verify that the QC review data is displayed correctly
    expect(screen.getByText('Quality Control Review')).toBeInTheDocument();

    // Verify that tabs for Documents, Stipulations, and Checklist are present
    expect(screen.getByText('Documents')).toBeInTheDocument();
    expect(screen.getByText('Stipulations')).toBeInTheDocument();
    expect(screen.getByText('Checklist')).toBeInTheDocument();

    // Verify that the QC Decision section is displayed
    expect(screen.getByText('QC Decision')).toBeInTheDocument();
  });

  it('handles tab changes correctly', async () => {
    // Create a mock QC review with documents, stipulations, and checklist items
    const mockQCReview = createMockQCReview({
      document_verifications: [{ id: 'doc-1', qc_review_id: 'qc-review-1', document_id: 'doc', document: { id: 'doc', document_type: 'Loan Agreement', file_name: 'loan.pdf', file_path: '/path', version: '1', status: 'generated', generated_at: '2024-01-01', generated_by: 'user-1', application_id: 'app-1', download_url: '/download' }, status: QCVerificationStatus.UNVERIFIED, verified_by: null, verified_by_name: null, verified_at: null, comments: null, created_at: '2024-01-01', updated_at: '2024-01-01' }],
      stipulation_verifications: [{ id: 'stip-1', qc_review_id: 'qc-review-1', stipulation_id: 'stip', stipulation_description: 'Proof of Income', status: QCVerificationStatus.UNVERIFIED, verified_by: null, verified_by_name: null, verified_at: null, comments: null, created_at: '2024-01-01', updated_at: '2024-01-01' }],
      checklist_items: [{ id: 'check-1', qc_review_id: 'qc-review-1', category: 'document_completeness', item_text: 'All documents present', status: QCVerificationStatus.UNVERIFIED, verified_by: null, verified_by_name: null, verified_at: null, comments: null, created_at: '2024-01-01', updated_at: '2024-01-01' }],
    });

    // Set up test with the mock QC review in state
    const { render, user } = setup({ selectedQCReview: mockQCReview });

    // Render the QCReview component with required props
    render(<QCReviewComponent qcReviewId="qc-review-1" applicationId="app-1" />);

    // Click on the Stipulations tab
    await user.click(screen.getByText('Stipulations'));

    // Verify that the Stipulations content is displayed
    expect(screen.getByText('Proof of Income')).toBeInTheDocument();

    // Click on the Checklist tab
    await user.click(screen.getByText('Checklist'));

    // Verify that the Checklist content is displayed
    expect(screen.getByText('All documents present')).toBeInTheDocument();

    // Click on the Documents tab
    await user.click(screen.getByText('Documents'));

    // Verify that the Documents content is displayed
    expect(screen.getByText('Loan Agreement')).toBeInTheDocument();
  });

  it('handles document verification correctly', async () => {
    // Create a mock QC review with documents
    const mockQCReview = createMockQCReview({
      document_verifications: [{ id: 'doc-1', qc_review_id: 'qc-review-1', document_id: 'doc', document: { id: 'doc', document_type: 'Loan Agreement', file_name: 'loan.pdf', file_path: '/path', version: '1', status: 'generated', generated_at: '2024-01-01', generated_by: 'user-1', application_id: 'app-1', download_url: '/download' }, status: QCVerificationStatus.UNVERIFIED, verified_by: null, verified_by_name: null, verified_at: null, comments: null, created_at: '2024-01-01', updated_at: '2024-01-01' }],
    });

    // Set up test with the mock QC review in state
    const { render, store, user } = setup({ selectedQCReview: mockQCReview });

    // Mock the verifyDocumentThunk function
    const mockVerifyDocumentThunk = vi.fn();
    (store.dispatch as vi.Mock).mockImplementation(mockVerifyDocumentThunk);

    // Render the QCReview component with required props
    render(<QCReviewComponent qcReviewId="qc-review-1" applicationId="app-1" />);

    // Click the verify button on a document
    await user.click(screen.getByRole('button', { name: 'Verify' }));

    // Verify that verifyDocumentThunk was called with the correct parameters
    expect(mockVerifyDocumentThunk).toHaveBeenCalledWith(expect.objectContaining({
      type: verifyDocumentThunk.typePrefix,
      payload: {
        document_verification_id: 'doc-1',
        comments: ''
      }
    }));
  });

  it('handles document rejection correctly', async () => {
    // Create a mock QC review with documents
    const mockQCReview = createMockQCReview({
      document_verifications: [{ id: 'doc-1', qc_review_id: 'qc-review-1', document_id: 'doc', document: { id: 'doc', document_type: 'Loan Agreement', file_name: 'loan.pdf', file_path: '/path', version: '1', status: 'generated', generated_at: '2024-01-01', generated_by: 'user-1', application_id: 'app-1', download_url: '/download' }, status: QCVerificationStatus.UNVERIFIED, verified_by: null, verified_by_name: null, verified_at: null, comments: null, created_at: '2024-01-01', updated_at: '2024-01-01' }],
    });

    // Set up test with the mock QC review in state
    const { render, store, user } = setup({ selectedQCReview: mockQCReview });

    // Mock the rejectDocumentThunk function
    const mockRejectDocumentThunk = vi.fn();
    (store.dispatch as vi.Mock).mockImplementation(mockRejectDocumentThunk);

    // Render the QCReview component with required props
    render(<QCReviewComponent qcReviewId="qc-review-1" applicationId="app-1" />);

    // Click the reject button on a document
    await user.click(screen.getByRole('button', { name: 'Reject' }));

    // Verify that rejectDocumentThunk was called with the correct parameters
    expect(mockRejectDocumentThunk).toHaveBeenCalledWith(expect.objectContaining({
      type: rejectDocumentThunk.typePrefix,
      payload: {
        document_verification_id: 'doc-1',
        comments: ''
      }
    }));
  });

  it('handles stipulation verification correctly', async () => {
    // Create a mock QC review with stipulations
    const mockQCReview = createMockQCReview({
      stipulation_verifications: [{ id: 'stip-1', qc_review_id: 'qc-review-1', stipulation_id: 'stip', stipulation_description: 'Proof of Income', status: QCVerificationStatus.UNVERIFIED, verified_by: null, verified_by_name: null, verified_at: null, comments: null, created_at: '2024-01-01', updated_at: '2024-01-01' }],
    });

    // Set up test with the mock QC review in state
    const { render, store, user } = setup({ selectedQCReview: mockQCReview });

    // Mock the verifyStipulationThunk function
    const mockVerifyStipulationThunk = vi.fn();
    (store.dispatch as vi.Mock).mockImplementation(mockVerifyStipulationThunk);

    // Render the QCReview component with required props
    render(<QCReviewComponent qcReviewId="qc-review-1" applicationId="app-1" />);

    // Click on the Stipulations tab
    await user.click(screen.getByText('Stipulations'));

    // Click the verify button on a stipulation
    await user.click(screen.getByRole('button', { name: 'Verify' }));

    // Verify that verifyStipulationThunk was called with the correct parameters
    expect(mockVerifyStipulationThunk).toHaveBeenCalledWith(expect.objectContaining({
      type: verifyStipulationThunk.typePrefix,
      payload: {
        stipulation_verification_id: 'stip-1',
        comments: ''
      }
    }));
  });

  it('handles stipulation rejection correctly', async () => {
    // Create a mock QC review with stipulations
    const mockQCReview = createMockQCReview({
      stipulation_verifications: [{ id: 'stip-1', qc_review_id: 'qc-review-1', stipulation_id: 'stip', stipulation_description: 'Proof of Income', status: QCVerificationStatus.UNVERIFIED, verified_by: null, verified_by_name: null, verified_at: null, comments: null, created_at: '2024-01-01', updated_at: '2024-01-01' }],
    });

    // Set up test with the mock QC review in state
    const { render, store, user } = setup({ selectedQCReview: mockQCReview });

    // Mock the rejectStipulationThunk function
    const mockRejectStipulationThunk = vi.fn();
    (store.dispatch as vi.Mock).mockImplementation(mockRejectStipulationThunk);

    // Render the QCReview component with required props
    render(<QCReviewComponent qcReviewId="qc-review-1" applicationId="app-1" />);

    // Click on the Stipulations tab
    await user.click(screen.getByText('Stipulations'));

    // Click the reject button on a stipulation
    await user.click(screen.getByRole('button', { name: 'Reject' }));

    // Verify that rejectStipulationThunk was called with the correct parameters
    expect(mockRejectStipulationThunk).toHaveBeenCalledWith(expect.objectContaining({
      type: rejectStipulationThunk.typePrefix,
      payload: {
        stipulation_verification_id: 'stip-1',
        comments: ''
      }
    }));
  });

  it('handles stipulation waiving correctly', async () => {
    // Create a mock QC review with stipulations
    const mockQCReview = createMockQCReview({
      stipulation_verifications: [{ id: 'stip-1', qc_review_id: 'qc-review-1', stipulation_id: 'stip', stipulation_description: 'Proof of Income', status: QCVerificationStatus.UNVERIFIED, verified_by: null, verified_by_name: null, verified_at: null, comments: null, created_at: '2024-01-01', updated_at: '2024-01-01' }],
    });

    // Set up test with the mock QC review in state
    const { render, store, user } = setup({ selectedQCReview: mockQCReview });

    // Mock the waiveStipulationThunk function
    const mockWaiveStipulationThunk = vi.fn();
    (store.dispatch as vi.Mock).mockImplementation(mockWaiveStipulationThunk);

    // Render the QCReview component with required props
    render(<QCReviewComponent qcReviewId="qc-review-1" applicationId="app-1" />);

    // Click on the Stipulations tab
    await user.click(screen.getByText('Stipulations'));

    // Click the waive button on a stipulation
    await user.click(screen.getByRole('button', { name: 'Waive' }));

    // Verify that waiveStipulationThunk was called with the correct parameters
    expect(mockWaiveStipulationThunk).toHaveBeenCalledWith(expect.objectContaining({
      type: waiveStipulationThunk.typePrefix,
      payload: {
        stipulation_verification_id: 'stip-1',
        comments: ''
      }
    }));
  });

  it('handles checklist item verification correctly', async () => {
    // Create a mock QC review with checklist items
    const mockQCReview = createMockQCReview({
      checklist_items: [{ id: 'check-1', qc_review_id: 'qc-review-1', category: 'document_completeness', item_text: 'All documents present', status: QCVerificationStatus.UNVERIFIED, verified_by: null, verified_by_name: null, verified_at: null, comments: null, created_at: '2024-01-01', updated_at: '2024-01-01' }],
    });

    // Set up test with the mock QC review in state
    const { render, store, user } = setup({ selectedQCReview: mockQCReview });

    // Mock the verifyChecklistItemThunk function
    const mockVerifyChecklistItemThunk = vi.fn();
    (store.dispatch as vi.Mock).mockImplementation(mockVerifyChecklistItemThunk);

    // Render the QCReview component with required props
    render(<QCReviewComponent qcReviewId="qc-review-1" applicationId="app-1" />);

    // Click on the Checklist tab
    await user.click(screen.getByText('Checklist'));

    // Click the verify button on a checklist item
    await user.click(screen.getByRole('button', { name: 'Verify' }));

    // Verify that verifyChecklistItemThunk was called with the correct parameters
    expect(mockVerifyChecklistItemThunk).toHaveBeenCalledWith(expect.objectContaining({
      type: verifyChecklistItemThunk.typePrefix,
      payload: {
        checklist_item_id: 'check-1',
        comments: ''
      }
    }));
  });

  it('handles checklist item rejection correctly', async () => {
    // Create a mock QC review with checklist items
    const mockQCReview = createMockQCReview({
      checklist_items: [{ id: 'check-1', qc_review_id: 'qc-review-1', category: 'document_completeness', item_text: 'All documents present', status: QCVerificationStatus.UNVERIFIED, verified_by: null, verified_by_name: null, verified_at: null, comments: null, created_at: '2024-01-01', updated_at: '2024-01-01' }],
    });

    // Set up test with the mock QC review in state
    const { render, store, user } = setup({ selectedQCReview: mockQCReview });

    // Mock the rejectCheckListItemThunk function
    const mockRejectChecklistItemThunk = vi.fn();
    (store.dispatch as vi.Mock).mockImplementation(mockRejectChecklistItemThunk);

    // Render the QCReview component with required props
    render(<QCReviewComponent qcReviewId="qc-review-1" applicationId="app-1" />);

    // Click on the Checklist tab
    await user.click(screen.getByText('Checklist'));

    // Click the reject button on a checklist item
    await user.click(screen.getByRole('button', { name: 'Reject' }));

    // Verify that rejectChecklistItemThunk was called with the correct parameters
    expect(mockRejectChecklistItemThunk).toHaveBeenCalledWith(expect.objectContaining({
      type: rejectChecklistItemThunk.typePrefix,
      payload: {
        checklist_item_id: 'check-1',
        comments: ''
      }
    }));
  });

  it('handles QC decision submission correctly', async () => {
    // Create a mock QC review
    const mockQCReview = createMockQCReview();

    // Set up test with the mock QC review in state
    const { render, store, user } = setup({ selectedQCReview: mockQCReview });

    // Mock the submitQCDecisionThunk function
    const mockSubmitQCDecisionThunk = vi.fn();
    (store.dispatch as vi.Mock).mockImplementation(mockSubmitQCDecisionThunk);

    // Render the QCReview component with required props
    render(<QCReviewComponent qcReviewId="qc-review-1" applicationId="app-1" />);

    // Select the Approve radio button
    await user.click(screen.getByLabelText('Approve application'));

    // Click the Submit button
    await user.click(screen.getByRole('button', { name: 'Submit QC decision' }));

    // Verify that submitQCDecisionThunk was called with the correct parameters (status: APPROVED)
    expect(mockSubmitQCDecisionThunk).toHaveBeenCalledWith(expect.objectContaining({
      type: submitQCDecisionThunk.typePrefix,
      payload: {
        qc_review_id: 'qc-review-1',
        status: QCStatus.APPROVED,
        return_reason: null,
        notes: ''
      }
    }));
  });

  it('handles QC return decision correctly', async () => {
    // Create a mock QC review
    const mockQCReview = createMockQCReview();

    // Set up test with the mock QC review in state
    const { render, store, user } = setup({ selectedQCReview: mockQCReview });

    // Mock the submitQCDecisionThunk function
    const mockSubmitQCDecisionThunk = vi.fn();
    (store.dispatch as vi.Mock).mockImplementation(mockSubmitQCDecisionThunk);

    // Render the QCReview component with required props
    render(<QCReviewComponent qcReviewId="qc-review-1" applicationId="app-1" />);

    // Select the Return radio button
    await user.click(screen.getByLabelText('Return application'));

    // Select a return reason
    await user.selectOptions(screen.getByLabelText('Return reason'), 'incomplete_documentation');

    // Enter notes for the return
    await user.type(screen.getByLabelText('Additional notes'), 'Missing some documents');

    // Click the Submit button
    await user.click(screen.getByRole('button', { name: 'Submit QC decision' }));

    // Verify that submitQCDecisionThunk was called with the correct parameters (status: RETURNED, reason, notes)
    expect(mockSubmitQCDecisionThunk).toHaveBeenCalledWith(expect.objectContaining({
      type: submitQCDecisionThunk.typePrefix,
      payload: {
        qc_review_id: 'qc-review-1',
        status: QCStatus.RETURNED,
        return_reason: QCReturnReason.INCOMPLETE_DOCUMENTATION,
        notes: 'Missing some documents'
      }
    }));
  });

  it('disables submit button when form is invalid', async () => {
    // Create a mock QC review
    const mockQCReview = createMockQCReview();

    // Set up test with the mock QC review in state
    const { render, user } = setup({ selectedQCReview: mockQCReview });

    // Render the QCReview component with required props
    render(<QCReviewComponent qcReviewId="qc-review-1" applicationId="app-1" />);

    // Select the Return radio button
    await user.click(screen.getByLabelText('Return application'));

    // Verify that the Submit button is disabled (because no return reason is selected)
    expect(screen.getByRole('button', { name: 'Submit QC decision' })).toBeDisabled();

    // Select a return reason
    await user.selectOptions(screen.getByLabelText('Return reason'), 'incomplete_documentation');

    // Verify that the Submit button is now enabled
    expect(screen.getByRole('button', { name: 'Submit QC decision' })).toBeEnabled();
  });

  it('renders in read-only mode correctly', () => {
    // Create a mock QC review with documents, stipulations, and checklist items
    const mockQCReview = createMockQCReview({
      document_verifications: [{ id: 'doc-1', qc_review_id: 'qc-review-1', document_id: { id: 'doc', document_type: 'Loan Agreement', file_name: 'loan.pdf', file_path: '/path', version: '1', status: 'generated', generated_at: '2024-01-01', generated_by: 'user-1', application_id: 'app-1' } as any, status: QCVerificationStatus.UNVERIFIED, verified_by: null, verified_by_name: null, verified_at: null, comments: null, created_at: '2024-01-01', updated_at: '2024-01-01' }],
      stipulation_verifications: [{ id: 'stip-1', qc_review_id: 'qc-review-1', stipulation_id: 'stip', stipulation_description: 'Proof of Income', status: QCVerificationStatus.UNVERIFIED, verified_by: null, verified_by_name: null, verified_at: null, comments: null, created_at: '2024-01-01', updated_at: '2024-01-01' }],
      checklist_items: [{ id: 'check-1', qc_review_id: 'qc-review-1', category: 'document_completeness', item_text: 'All documents present', status: QCVerificationStatus.UNVERIFIED, verified_by: null, verified_by_name: null, verified_at: null, comments: null, created_at: '2024-01-01', updated_at: '2024-01-01' }],
    });

    // Set up test with the mock QC review in state
    const { render } = setup({ selectedQCReview: mockQCReview });

    // Render the QCReview component with isReadOnly prop set to true
    render(<QCReviewComponent qcReviewId="qc-review-1" applicationId="app-1" isReadOnly={true} />);

    // Verify that verification buttons are not displayed
    expect(screen.queryByRole('button', { name: 'Verify' })).toBeNull();
    expect(screen.queryByRole('button', { name: 'Reject' })).toBeNull();
    expect(screen.queryByRole('button', { name: 'Waive' })).toBeNull();

    // Verify that the QC Decision section is not displayed
    expect(screen.queryByText('QC Decision')).toBeNull();
  });
});