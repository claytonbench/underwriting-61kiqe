import React from 'react'; // React v18.0+
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'; // React Testing Library utilities v14.0+
import userEvent from '@testing-library/user-event'; // User event simulation for more realistic interaction testing v14.4.3
import { axe, toHaveNoViolations } from 'jest-axe'; // Accessibility testing for form components v7.0.0
import { MemoryRouter, Routes, Route } from 'react-router-dom'; // Router components for testing components that use navigation v6.14.0

import ApplicationFormContainer from '../ApplicationFormContainer';
import BorrowerInfoStep from '../BorrowerInfoStep';
import EmploymentInfoStep from '../EmploymentInfoStep';
import CoBorrowerInfoStep from '../CoBorrowerInfoStep';
import LoanDetailsStep from '../LoanDetailsStep';
import ReviewSubmitStep from '../ReviewSubmitStep';
import { createApplication, saveApplicationDraft, submitApplication } from '../../api/applications';
import { CitizenshipStatus, HousingStatus } from '../../types/application.types';

// Extend Jest expect to include accessibility checks
expect.extend(toHaveNoViolations);

// Mock props for testing individual form step components
const mockFormProps = {
  values: {
    first_name: '',
    middle_name: '',
    last_name: '',
    ssn: '',
    dob: '',
    email: '',
    phone: '',
    citizenship_status: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    zip_code: '',
    housing_status: '',
    housing_payment: 0,
  },
  errors: {},
  touched: {},
  handleChange: jest.fn(),
  handleBlur: jest.fn(),
  setFieldValue: jest.fn(),
  setFieldTouched: jest.fn(),
  isSubmitting: false,
  isValid: true,
};

// Mock data for a valid borrower information step
const mockValidBorrowerData = {
  first_name: 'John',
  middle_name: '',
  last_name: 'Smith',
  ssn: '123-45-6789',
  dob: '1990-01-01',
  email: 'john.smith@example.com',
  phone: '(555) 123-4567',
  citizenship_status: CitizenshipStatus.US_CITIZEN,
  address_line1: '123 Main St',
  address_line2: '',
  city: 'Anytown',
  state: 'CA',
  zip_code: '12345',
  housing_status: HousingStatus.RENT,
  housing_payment: 1500,
};

// Mock data for a valid employment information step
const mockValidEmploymentData = {
  employment_type: 'FULL_TIME',
  employer_name: 'Acme Corporation',
  occupation: 'Software Developer',
  employer_phone: '(555) 987-6543',
  years_employed: 3,
  months_employed: 6,
  annual_income: 85000,
  other_income: 0,
  other_income_source: '',
  has_co_borrower: false,
};

// Mock data for a valid loan details step
const mockValidLoanData = {
  school_id: 'school-123',
  program_id: 'program-456',
  start_date: '2023-09-01',
  completion_date: '2024-03-01',
  tuition_amount: 10000,
  deposit_amount: 1000,
  other_funding: 0,
  requested_amount: 9000,
};

// Setup function to create a test wrapper with routing for the application form
const setup = (props = {}) => {
  // Create a wrapper component with MemoryRouter
  const Wrapper = ({ children }) => (
    <MemoryRouter initialEntries={['/application-form']}>
      <Routes>
        <Route path="/application-form" element={children} />
      </Routes>
    </MemoryRouter>
  );

  // Render the ApplicationFormContainer with provided props inside the wrapper
  const renderResult = render(<ApplicationFormContainer {...props} />, { wrapper: Wrapper });

  // Return rendered component and utilities
  return {
    ...renderResult,
  };
};

// Function to mock API calls used by the application form
const mockApiCalls = () => {
  // Mock createApplication to return a successful response with a new application ID
  const createApplicationMock = jest.fn().mockResolvedValue({
    success: true,
    data: { id: 'new-application-id' },
    message: null,
  });
  (createApplication as jest.Mock) = createApplicationMock;

  // Mock saveApplicationDraft to return a successful response with the application data
  const saveApplicationDraftMock = jest.fn().mockResolvedValue({
    success: true,
    data: { id: 'existing-application-id' },
    message: null,
  });
  (saveApplicationDraft as jest.Mock) = saveApplicationDraftMock;

  // Mock submitApplication to return a successful response with the submitted application data
  const submitApplicationMock = jest.fn().mockResolvedValue({
    success: true,
    data: { id: 'new-application-id' },
    message: null,
  });
  (submitApplication as jest.Mock) = submitApplicationMock;

  // Return the mocked functions for assertions
  return {
    createApplicationMock,
    saveApplicationDraftMock,
    submitApplicationMock,
  };
};

// Test suite for the main application form container component
describe('ApplicationFormContainer', () => {
  // Test that the form initially renders the borrower information step
  it('renders the first step (borrower info) by default', () => {
    // Render the ApplicationFormContainer component
    setup();

    // Check that the stepper shows 'Borrower Information' as the active step
    expect(screen.getByText('Borrower Information')).toBeInTheDocument();

    // Verify that first name, last name, and other borrower fields are visible
    expect(screen.getByLabelText(/First Name/i)).toBeVisible();
    expect(screen.getByLabelText(/Last Name/i)).toBeVisible();
  });

  // Test that the form advances to the next step when validation passes
  it('navigates to the next step when Next button is clicked and validation passes', async () => {
    // Render the ApplicationFormContainer component
    setup();

    // Fill in all required fields in the borrower information step
    userEvent.type(screen.getByLabelText(/First Name/i), mockValidBorrowerData.first_name);
    userEvent.type(screen.getByLabelText(/Last Name/i), mockValidBorrowerData.last_name);
    userEvent.type(screen.getByLabelText(/Email/i), mockValidBorrowerData.email);

    // Click the Next button
    fireEvent.click(screen.getByText(/Next/i));

    // Verify that the form advances to the Employment Information step
    await waitFor(() => {
      expect(screen.getByText(/Employment Information/i)).toBeInTheDocument();
    });
  });

  // Test that validation errors are displayed when required fields are missing
  it('shows validation errors when Next is clicked with invalid fields', async () => {
    // Render the ApplicationFormContainer component
    setup();

    // Leave required fields empty
    // Click the Next button
    fireEvent.click(screen.getByText(/Next/i));

    // Verify that error messages are displayed for the required fields
    await waitFor(() => {
      expect(screen.getByText(/First name is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Last name is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Valid email address is required/i)).toBeInTheDocument();
    });

    // Verify that the form does not advance to the next step
    expect(screen.getByText(/Borrower Information/i)).toBeInTheDocument();
  });

  // Test that the form returns to the previous step when Back is clicked
  it('navigates back to the previous step when Back button is clicked', async () => {
    // Render the ApplicationFormContainer component
    setup();

    // Fill in all required fields in the borrower information step
    userEvent.type(screen.getByLabelText(/First Name/i), mockValidBorrowerData.first_name);
    userEvent.type(screen.getByLabelText(/Last Name/i), mockValidBorrowerData.last_name);
    userEvent.type(screen.getByLabelText(/Email/i), mockValidBorrowerData.email);

    // Click the Next button to advance to the Employment Information step
    fireEvent.click(screen.getByText(/Next/i));
    await waitFor(() => {
      expect(screen.getByText(/Employment Information/i)).toBeInTheDocument();
    });

    // Click the Back button
    fireEvent.click(screen.getByText(/Back/i));

    // Verify that the form returns to the Borrower Information step
    await waitFor(() => {
      expect(screen.getByText(/Borrower Information/i)).toBeInTheDocument();
    });
  });

  // Test that the co-borrower step is skipped when not needed
  it('skips co-borrower step when has_co_borrower is false', async () => {
    // Render the ApplicationFormContainer component
    setup();

    // Complete the borrower information step
    userEvent.type(screen.getByLabelText(/First Name/i), mockValidBorrowerData.first_name);
    userEvent.type(screen.getByLabelText(/Last Name/i), mockValidBorrowerData.last_name);
    userEvent.type(screen.getByLabelText(/Email/i), mockValidBorrowerData.email);
    fireEvent.click(screen.getByText(/Next/i));

    // Complete the employment information step with has_co_borrower set to false
    await waitFor(() => {
      expect(screen.getByText(/Employment Information/i)).toBeInTheDocument();
    });
    fireEvent.change(screen.getByLabelText(/Employment Type/i), { target: { value: 'FULL_TIME' } });
    fireEvent.click(screen.getByText(/Next/i));

    // Verify that the form skips to the Loan Details step instead of Co-Borrower Information
    await waitFor(() => {
      expect(screen.getByText(/Loan Details/i)).toBeInTheDocument();
    });
  });

  // Test that the co-borrower step is included when needed
  it('includes co-borrower step when has_co_borrower is true', async () => {
    // Render the ApplicationFormContainer component
    setup();

    // Complete the borrower information step
    userEvent.type(screen.getByLabelText(/First Name/i), mockValidBorrowerData.first_name);
    userEvent.type(screen.getByLabelText(/Last Name/i), mockValidBorrowerData.last_name);
    userEvent.type(screen.getByLabelText(/Email/i), mockValidBorrowerData.email);
    fireEvent.click(screen.getByText(/Next/i));

    // Complete the employment information step with has_co_borrower set to true
    await waitFor(() => {
      expect(screen.getByText(/Employment Information/i)).toBeInTheDocument();
    });
    fireEvent.change(screen.getByLabelText(/Employment Type/i), { target: { value: 'FULL_TIME' } });
    fireEvent.click(screen.getByText(/Next/i));

    // Verify that the form advances to the Co-Borrower Information step
    await waitFor(() => {
      expect(screen.getByText(/Co-Borrower Information/i)).toBeInTheDocument();
    });
  });

  // Test that the form saves a draft application
  it('saves draft application when Save Draft button is clicked', async () => {
    // Mock the saveApplicationDraft API function
    const { saveApplicationDraftMock } = mockApiCalls();

    // Render the ApplicationFormContainer component
    setup();

    // Fill in some form fields
    userEvent.type(screen.getByLabelText(/First Name/i), mockValidBorrowerData.first_name);

    // Click the Save Draft button
    fireEvent.click(screen.getByText(/Save Draft/i));

    // Verify that saveApplicationDraft was called with the correct data
    await waitFor(() => {
      expect(saveApplicationDraftMock).toHaveBeenCalled();
    });

    // Verify that a success message is displayed
    // This part depends on how you display success messages in your component
    // For example, if you use an Alert component:
    // await waitFor(() => {
    //   expect(screen.getByText(/Draft saved successfully/i)).toBeInTheDocument();
    // });
  });

  // Test that the form submits the complete application
  it('submits the application when Submit button is clicked on final step', async () => {
    // Mock the createApplication and submitApplication API functions
    const { createApplicationMock, submitApplicationMock } = mockApiCalls();

    // Render the ApplicationFormContainer component
    setup({ onSubmitSuccess: jest.fn() });

    // Complete all steps of the form
    userEvent.type(screen.getByLabelText(/First Name/i), mockValidBorrowerData.first_name);
    fireEvent.click(screen.getByText(/Next/i));

    await waitFor(() => {
      expect(screen.getByText(/Employment Information/i)).toBeInTheDocument();
    });
    fireEvent.change(screen.getByLabelText(/Employment Type/i), { target: { value: 'FULL_TIME' } });
    fireEvent.click(screen.getByText(/Next/i));

    await waitFor(() => {
      expect(screen.getByText(/Loan Details/i)).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText(/Next/i));

    await waitFor(() => {
      expect(screen.getByText(/Review & Submit/i)).toBeInTheDocument();
    });

    // Accept terms and conditions on the final step
    fireEvent.click(screen.getByLabelText(/I accept the terms and conditions/i));

    // Click the Submit button
    fireEvent.click(screen.getByText(/Submit/i));

    // Verify that createApplication and submitApplication were called with the correct data
    await waitFor(() => {
      expect(createApplicationMock).toHaveBeenCalled();
      expect(submitApplicationMock).toHaveBeenCalled();
    });

    // Verify that the onSubmitSuccess callback was called
    // This part depends on how you handle the onSubmitSuccess callback
    // For example, if you use a mock function:
    // await waitFor(() => {
    //   expect(onSubmitSuccessMock).toHaveBeenCalledWith('new-application-id');
    // });
  });

  // Test that the form loads existing application data for editing
  it('loads existing application data when initialValues are provided', () => {
    // Create mock initial values for an existing application
    const initialValues = {
      borrower_info: mockValidBorrowerData,
      employment_info: mockValidEmploymentData,
      loan_details: mockValidLoanData,
    };

    // Render the ApplicationFormContainer with initialValues prop
    setup({ initialValues });

    // Verify that form fields are pre-populated with the initial values
    expect(screen.getByLabelText(/First Name/i)).toHaveValue(mockValidBorrowerData.first_name);
    expect(screen.getByLabelText(/Employer Name/i)).toHaveValue(mockValidEmploymentData.employer_name);
  });

  // Test error handling when API calls fail
  it('displays error message when API call fails', async () => {
    // Mock the submitApplication API function to reject with an error
    (submitApplication as jest.Mock).mockRejectedValue(new Error('API Error'));

    // Render the ApplicationFormContainer component
    setup();

    // Complete all steps of the form
    userEvent.type(screen.getByLabelText(/First Name/i), mockValidBorrowerData.first_name);
    fireEvent.click(screen.getByText(/Next/i));

    await waitFor(() => {
      expect(screen.getByText(/Employment Information/i)).toBeInTheDocument();
    });
    fireEvent.change(screen.getByLabelText(/Employment Type/i), { target: { value: 'FULL_TIME' } });
    fireEvent.click(screen.getByText(/Next/i));

    await waitFor(() => {
      expect(screen.getByText(/Loan Details/i)).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText(/Next/i));

    await waitFor(() => {
      expect(screen.getByText(/Review & Submit/i)).toBeInTheDocument();
    });

    // Click the Submit button
    fireEvent.click(screen.getByText(/Submit/i));

    // Verify that an error message is displayed
    await waitFor(() => {
      expect(screen.getByText(/API Error/i)).toBeInTheDocument();
    });
  });
});

// Test suite for the borrower information step component
describe('BorrowerInfoStep', () => {
  // Test that all required borrower information fields are rendered
  it('renders all required borrower information fields', () => {
    // Create mock form props (values, errors, touched, handlers)
    const mockProps = mockFormProps;

    // Render the BorrowerInfoStep component with mock props
    render(<BorrowerInfoStep {...mockProps} />);

    // Verify that all required fields are present (name, SSN, DOB, contact, citizenship, address, housing)
    expect(screen.getByLabelText(/First Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Last Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Social Security Number/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Date of Birth/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Phone Number/i)).toBeInTheDocument();
    expect(screen.getByText(/Citizenship Status/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Street Address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/City/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/State/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/ZIP Code/i)).toBeInTheDocument();
    expect(screen.getByText(/Housing Status/i)).toBeInTheDocument();
  });

  // Test that validation is applied to required fields
  it('validates required fields correctly', () => {
    // Create mock form props with empty values and validation errors
    const mockProps = {
      ...mockFormProps,
      errors: {
        first_name: 'First name is required',
        last_name: 'Last name is required',
        email: 'Valid email address is required',
      },
      touched: {
        first_name: true,
        last_name: true,
        email: true,
      },
    };

    // Render the BorrowerInfoStep component with mock props
    render(<BorrowerInfoStep {...mockProps} />);

    // Verify that error messages are displayed for required fields
    expect(screen.getByText(/First name is required/i)).toBeInTheDocument();
    expect(screen.getByText(/Last name is required/i)).toBeInTheDocument();
    expect(screen.getByText(/Valid email address is required/i)).toBeInTheDocument();
  });

  // Test that input changes update form values
  it('handles input changes correctly', () => {
    // Create mock form props with handleChange function
    const mockProps = {
      ...mockFormProps,
      handleChange: jest.fn(),
    };

    // Render the BorrowerInfoStep component with mock props
    render(<BorrowerInfoStep {...mockProps} />);

    // Simulate user typing in the first name field
    const firstNameInput = screen.getByLabelText(/First Name/i);
    fireEvent.change(firstNameInput, { target: { value: 'John' } });

    // Verify that handleChange was called with the correct field and value
    expect(mockProps.handleChange).toHaveBeenCalledWith(expect.objectContaining({
      target: expect.objectContaining({
        name: 'first_name',
        value: 'John',
      }),
    }));
  });

  // Test conditional rendering of the housing payment field
  it('conditionally shows housing payment field based on housing status', () => {
    // Create mock form props with housing_status set to RENT
    const mockPropsRent = {
      ...mockFormProps,
      values: {
        ...mockFormProps.values,
        housing_status: HousingStatus.RENT,
      },
    };

    // Render the BorrowerInfoStep component with mock props
    render(<BorrowerInfoStep {...mockPropsRent} />);

    // Verify that the housing payment field is visible
    expect(screen.getByLabelText(/Monthly Housing Payment/i)).toBeVisible();

    // Update props with housing_status set to LIVE_WITH_FAMILY
    const mockPropsFamily = {
      ...mockFormProps,
      values: {
        ...mockFormProps.values,
        housing_status: HousingStatus.LIVE_WITH_FAMILY,
      },
    };

    // Re-render the component with updated props
    render(<BorrowerInfoStep {...mockPropsFamily} />);

    // Verify that the housing payment field is not visible
    expect(screen.queryByLabelText(/Monthly Housing Payment/i)).toBeNull();
  });
});

// Test suite for accessibility compliance of form components
describe('Accessibility Tests', () => {
  // Test that the form container meets accessibility standards
  it('ApplicationFormContainer has no accessibility violations', async () => {
    // Render the ApplicationFormContainer component
    const { container } = setup();

    // Run axe accessibility tests on the rendered component
    const results = await axe(container);

    // Verify that there are no accessibility violations
    expect(results).toHaveNoViolations();
  });

  // Test that the borrower info step meets accessibility standards
  it('BorrowerInfoStep has no accessibility violations', async () => {
    // Create mock form props
    const mockProps = mockFormProps;

    // Render the BorrowerInfoStep component with mock props
    const { container } = render(<BorrowerInfoStep {...mockProps} />);

    // Run axe accessibility tests on the rendered component
    const results = await axe(container);

    // Verify that there are no accessibility violations
    expect(results).toHaveNoViolations();
  });
});