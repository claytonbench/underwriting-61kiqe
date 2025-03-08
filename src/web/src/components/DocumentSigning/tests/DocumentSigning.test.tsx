import React from 'react';
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import DocumentSigning from '../DocumentSigning';
import { getSigningSession, completeSignature, declineSignature } from '../../api/documents';

// Mock the API functions
jest.mock('../../api/documents', () => ({
  getSigningSession: jest.fn(),
  completeSignature: jest.fn(),
  declineSignature: jest.fn(),
}));

// Mock the useNavigate hook
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock data for the signing session
const mockSigningSession = {
  signature_request_id: '123',
  document: {
    id: 'doc-123',
    document_type: 'LOAN_AGREEMENT',
    file_name: 'Test Document.pdf',
    file_path: '/documents/test-document.pdf',
    status: 'PENDING_SIGNATURE',
    generated_at: '2023-06-15T10:00:00Z',
    package_id: 'pkg-123',
    version: '1.0',
    generated_by: 'user-123',
    application_id: 'app-123',
    download_url: '/download/test-document.pdf'
  },
  signer: {
    id: 'user-456',
    name: 'John Smith',
    email: 'john@example.com',
    type: 'BORROWER'
  },
  document_url: 'https://example.com/document.pdf',
  signature_fields: [
    {
      id: 'field-1',
      page: 1,
      x: 100,
      y: 200,
      width: 200,
      height: 50
    }
  ],
  session_expiration: '2023-06-16T10:00:00Z'
};

// Helper function to render the component with router context
const renderWithRouter = (signatureRequestId = '123') => {
  return render(
    <MemoryRouter initialEntries={[`/sign/${signatureRequestId}`]}>
      <Routes>
        <Route path="/sign/:signatureRequestId" element={<DocumentSigning />} />
      </Routes>
    </MemoryRouter>
  );
};

describe('DocumentSigning Component', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    
    // Default mock implementation for getSigningSession
    (getSigningSession as jest.Mock).mockResolvedValue({
      success: true,
      data: mockSigningSession,
      message: null,
      errors: null
    });
    
    // Default mock implementation for completeSignature
    (completeSignature as jest.Mock).mockResolvedValue({
      success: true,
      data: {
        signature_request_id: '123',
        document_id: 'doc-123',
        status: 'COMPLETED',
        completed_at: '2023-06-15T12:00:00Z',
        next_steps: null
      },
      message: null,
      errors: null
    });
    
    // Default mock implementation for declineSignature
    (declineSignature as jest.Mock).mockResolvedValue({
      success: true,
      data: {
        signature_request_id: '123',
        document_id: 'doc-123',
        status: 'DECLINED',
        completed_at: '2023-06-15T12:00:00Z',
        decline_reason: 'Test reason',
        next_steps: null
      },
      message: null,
      errors: null
    });
  });

  test('renders loading state initially', () => {
    renderWithRouter();
    expect(screen.getByText(/Loading document signing session/i)).toBeInTheDocument();
  });

  test('displays error message when session loading fails', async () => {
    (getSigningSession as jest.Mock).mockResolvedValue({
      success: false,
      data: null,
      message: 'Failed to load signing session',
      errors: null
    });

    renderWithRouter();
    
    await waitFor(() => {
      expect(screen.getByText(/Error Loading Document Signing Session/i)).toBeInTheDocument();
      expect(screen.getByText(/Failed to load signing session/i)).toBeInTheDocument();
    });
  });

  test('renders document preview in the first step', async () => {
    renderWithRouter();
    
    await waitFor(() => {
      expect(screen.getByText(/Please review the document before signing/i)).toBeInTheDocument();
      expect(screen.getByTestId('document-preview')).toBeInTheDocument();
      expect(screen.getByText(/Test Document\.pdf/i)).toBeInTheDocument();
      
      // Verify stepper shows correct step
      expect(screen.getByText(/Review Document/i)).toBeInTheDocument();
    });
  });

  test('navigates to signature capture on next step', async () => {
    renderWithRouter();
    
    await waitFor(() => {
      expect(screen.getByText(/Please review the document before signing/i)).toBeInTheDocument();
    });
    
    // Click the "Proceed to Sign" button
    fireEvent.click(screen.getByText(/Proceed to Sign/i));
    
    // Signature capture should be displayed
    expect(screen.getByText(/Sign your name in the box below/i)).toBeInTheDocument();
    
    // Verify stepper shows correct step
    const steps = screen.getAllByText(/Sign Document/i);
    expect(steps.length).toBeGreaterThan(0);
  });

  test('captures signature and shows confirmation step', async () => {
    renderWithRouter();
    
    // Wait for document to load
    await waitFor(() => {
      expect(screen.getByText(/Please review the document before signing/i)).toBeInTheDocument();
    });
    
    // Navigate to signature capture
    fireEvent.click(screen.getByText(/Proceed to Sign/i));
    
    // Find canvas element
    const canvas = document.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
    
    // Simulate drawing a signature
    if (canvas) {
      // Mouse down
      fireEvent.mouseDown(canvas, { clientX: 10, clientY: 10 });
      // Mouse move
      fireEvent.mouseMove(canvas, { clientX: 50, clientY: 50 });
      // Mouse up
      fireEvent.mouseUp(canvas);
    }
    
    // Submit signature
    fireEvent.click(screen.getByText(/Submit Signature/i));
    
    // Confirmation step should be displayed
    await waitFor(() => {
      expect(screen.getByText(/Confirm your signature/i)).toBeInTheDocument();
      expect(screen.getByText(/Document: Test Document\.pdf/i)).toBeInTheDocument();
      expect(screen.getByText(/Signer: John Smith/i)).toBeInTheDocument();
      expect(screen.getByText(/Your signature:/i)).toBeInTheDocument();
      
      // Verify stepper shows correct step
      const steps = screen.getAllByText(/Confirm Signature/i);
      expect(steps.length).toBeGreaterThan(0);
    });
  });

  test('submits signature successfully', async () => {
    renderWithRouter();
    
    // Wait for document to load
    await waitFor(() => {
      expect(screen.getByText(/Please review the document before signing/i)).toBeInTheDocument();
    });
    
    // Navigate to signature capture
    fireEvent.click(screen.getByText(/Proceed to Sign/i));
    
    // Find canvas element
    const canvas = document.querySelector('canvas');
    
    // Simulate drawing a signature
    if (canvas) {
      // Mouse down
      fireEvent.mouseDown(canvas, { clientX: 10, clientY: 10 });
      // Mouse move
      fireEvent.mouseMove(canvas, { clientX: 50, clientY: 50 });
      // Mouse up
      fireEvent.mouseUp(canvas);
    }
    
    // Submit signature
    fireEvent.click(screen.getByText(/Submit Signature/i));
    
    // Wait for confirmation step
    await waitFor(() => {
      expect(screen.getByText(/Confirm your signature/i)).toBeInTheDocument();
    });
    
    // Submit final signature
    fireEvent.click(screen.getByText(/Submit Signature/i));
    
    // Verify completeSignature was called with the correct parameters
    await waitFor(() => {
      expect(completeSignature).toHaveBeenCalledWith('123');
      expect(mockNavigate).toHaveBeenCalledWith('/documents', expect.any(Object));
    });
  });

  test('handles signature submission error', async () => {
    // Mock the API to return an error
    (completeSignature as jest.Mock).mockResolvedValue({
      success: false,
      data: null,
      message: 'Failed to submit signature',
      errors: null
    });
    
    renderWithRouter();
    
    // Wait for document to load
    await waitFor(() => {
      expect(screen.getByText(/Please review the document before signing/i)).toBeInTheDocument();
    });
    
    // Navigate to signature capture
    fireEvent.click(screen.getByText(/Proceed to Sign/i));
    
    // Find canvas element
    const canvas = document.querySelector('canvas');
    
    // Simulate drawing a signature
    if (canvas) {
      // Mouse down
      fireEvent.mouseDown(canvas, { clientX: 10, clientY: 10 });
      // Mouse move
      fireEvent.mouseMove(canvas, { clientX: 50, clientY: 50 });
      // Mouse up
      fireEvent.mouseUp(canvas);
    }
    
    // Submit signature
    fireEvent.click(screen.getByText(/Submit Signature/i));
    
    // Wait for confirmation step
    await waitFor(() => {
      expect(screen.getByText(/Confirm your signature/i)).toBeInTheDocument();
    });
    
    // Submit final signature
    fireEvent.click(screen.getByText(/Submit Signature/i));
    
    // Verify error message is displayed
    await waitFor(() => {
      expect(screen.getByText(/Failed to submit signature/i)).toBeInTheDocument();
    });
  });

  test('allows declining signature with reason', async () => {
    renderWithRouter();
    
    // Wait for document to load
    await waitFor(() => {
      expect(screen.getByText(/Please review the document before signing/i)).toBeInTheDocument();
    });
    
    // Click the "Decline to Sign" button
    fireEvent.click(screen.getByText(/Decline to Sign/i));
    
    // Decline dialog should be displayed
    expect(screen.getByText(/Decline to Sign/i)).toBeInTheDocument();
    expect(screen.getByText(/Please provide a reason for declining to sign this document:/i)).toBeInTheDocument();
    
    // Enter a decline reason
    fireEvent.change(screen.getByTestId('decline-reason-input'), {
      target: { value: 'I need to review this with my attorney' }
    });
    
    // Click the "Decline Signature" button
    fireEvent.click(screen.getByText(/Decline Signature/i));
    
    // Verify declineSignature was called with the correct parameters
    await waitFor(() => {
      expect(declineSignature).toHaveBeenCalledWith({
        signatureRequestId: '123',
        reason: 'I need to review this with my attorney'
      });
      expect(mockNavigate).toHaveBeenCalledWith('/documents', expect.any(Object));
    });
  });

  test('navigates back to previous steps', async () => {
    renderWithRouter();
    
    // Wait for document to load
    await waitFor(() => {
      expect(screen.getByText(/Please review the document before signing/i)).toBeInTheDocument();
    });
    
    // Navigate to signature capture
    fireEvent.click(screen.getByText(/Proceed to Sign/i));
    
    // Signature capture should be displayed
    expect(screen.getByText(/Sign your name in the box below/i)).toBeInTheDocument();
    
    // Click the "Back" button
    fireEvent.click(screen.getByText(/Back/i));
    
    // Document preview should be displayed again
    expect(screen.getByText(/Please review the document before signing/i)).toBeInTheDocument();
    
    // Verify stepper shows correct step
    expect(screen.getByText(/Review Document/i)).toBeInTheDocument();
  });

  test('handles cancel action', async () => {
    renderWithRouter();
    
    // Wait for document to load
    await waitFor(() => {
      expect(screen.getByText(/Please review the document before signing/i)).toBeInTheDocument();
    });
    
    // Click the "Cancel" button
    fireEvent.click(screen.getByText(/Cancel/i));
    
    // Verify navigation
    expect(mockNavigate).toHaveBeenCalledWith('/documents');
  });
});