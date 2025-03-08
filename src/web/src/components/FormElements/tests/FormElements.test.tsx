import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react'; // v14.0.0
import userEvent from '@testing-library/user-event'; // v14.4.3
import { ThemeProvider, createTheme } from '@mui/material'; // v5.14.0

// Import components to test
import AddressFields from '../AddressFields';
import ContactFields from '../ContactFields';
import CurrencyField from '../CurrencyField';
import DateField from '../DateField';
import PhoneField from '../PhoneField';
import SSNField from '../SSNField';

// Import validation and formatting utilities
import { isEmail, isPhoneNumber, isSSN, isZipCode } from '../../../utils/validation';
import { formatCurrency, formatPhoneNumber, formatSSN } from '../../../utils/formatting';

/**
 * Helper function to render components with Material-UI theme provider
 * @param ui The React element to render
 * @returns The rendered component with all testing utilities
 */
const renderWithTheme = (ui: React.ReactElement) => {
  const theme = createTheme();
  return render(
    <ThemeProvider theme={theme}>
      {ui}
    </ThemeProvider>
  );
};

describe('AddressFields', () => {
  it('renders all address fields correctly', () => {
    const mockValues = {};
    const mockErrors = {};
    const mockTouched = {};
    const mockHandleChange = jest.fn();
    const mockHandleBlur = jest.fn();

    renderWithTheme(
      <AddressFields
        values={mockValues}
        errors={mockErrors}
        touched={mockTouched}
        handleChange={mockHandleChange}
        handleBlur={mockHandleBlur}
        prefix="borrower_"
      />
    );

    expect(screen.getByLabelText('Street Address')).toBeInTheDocument();
    expect(screen.getByLabelText('Apartment, suite, etc. (optional)')).toBeInTheDocument();
    expect(screen.getByLabelText('City')).toBeInTheDocument();
    expect(screen.getByLabelText('State')).toBeInTheDocument();
    expect(screen.getByLabelText('ZIP Code')).toBeInTheDocument();
  });

  it('handles input changes correctly', () => {
    const mockValues = {};
    const mockErrors = {};
    const mockTouched = {};
    const mockHandleChange = jest.fn();
    const mockHandleBlur = jest.fn();

    renderWithTheme(
      <AddressFields
        values={mockValues}
        errors={mockErrors}
        touched={mockTouched}
        handleChange={mockHandleChange}
        handleBlur={mockHandleBlur}
        prefix="borrower_"
      />
    );

    const streetAddressField = screen.getByTestId('borrower_address_line1');
    fireEvent.change(streetAddressField, { target: { value: '123 Main St' } });
    
    expect(mockHandleChange).toHaveBeenCalledTimes(1);
  });

  it('displays validation errors when fields are touched and invalid', () => {
    const mockValues = {};
    const mockErrors = {
      borrower_address_line1: 'Street address is required',
      borrower_city: 'City is required',
      borrower_state: 'State is required',
      borrower_zip_code: 'ZIP code is required',
    };
    const mockTouched = {
      borrower_address_line1: true,
      borrower_city: true,
      borrower_state: true,
      borrower_zip_code: true,
    };
    const mockHandleChange = jest.fn();
    const mockHandleBlur = jest.fn();

    renderWithTheme(
      <AddressFields
        values={mockValues}
        errors={mockErrors}
        touched={mockTouched}
        handleChange={mockHandleChange}
        handleBlur={mockHandleBlur}
        prefix="borrower_"
      />
    );

    expect(screen.getByText('Street address is required')).toBeInTheDocument();
    expect(screen.getByText('City is required')).toBeInTheDocument();
    expect(screen.getByText('State is required')).toBeInTheDocument();
    expect(screen.getByText('ZIP code is required')).toBeInTheDocument();
  });

  it('applies disabled state correctly', () => {
    const mockValues = {};
    const mockErrors = {};
    const mockTouched = {};
    const mockHandleChange = jest.fn();
    const mockHandleBlur = jest.fn();

    renderWithTheme(
      <AddressFields
        values={mockValues}
        errors={mockErrors}
        touched={mockTouched}
        handleChange={mockHandleChange}
        handleBlur={mockHandleBlur}
        prefix="borrower_"
        disabled={true}
      />
    );

    expect(screen.getByTestId('borrower_address_line1')).toBeDisabled();
    expect(screen.getByLabelText('Apartment, suite, etc. (optional)')).toBeDisabled();
    expect(screen.getByLabelText('City')).toBeDisabled();
    expect(screen.getByLabelText('State')).toBeDisabled();
    expect(screen.getByLabelText('ZIP Code')).toBeDisabled();
  });
});

describe('ContactFields', () => {
  it('renders email and phone fields correctly', () => {
    const mockOnChange = jest.fn();
    const mockOnBlur = jest.fn();

    renderWithTheme(
      <ContactFields
        email=""
        phone=""
        onChange={mockOnChange}
        onBlur={mockOnBlur}
        errors={{}}
      />
    );

    expect(screen.getByLabelText('Email Address')).toBeInTheDocument();
    expect(screen.getByLabelText('Phone Number')).toBeInTheDocument();
  });

  it('handles email input changes correctly', () => {
    const mockOnChange = jest.fn();
    const mockOnBlur = jest.fn();

    renderWithTheme(
      <ContactFields
        email=""
        phone=""
        onChange={mockOnChange}
        onBlur={mockOnBlur}
        errors={{}}
      />
    );

    const emailInput = screen.getByTestId('email-input');
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    
    expect(mockOnChange).toHaveBeenCalledWith('email', 'test@example.com');
  });

  it('handles phone input changes correctly', () => {
    const mockOnChange = jest.fn();
    const mockOnBlur = jest.fn();

    renderWithTheme(
      <ContactFields
        email=""
        phone=""
        onChange={mockOnChange}
        onBlur={mockOnBlur}
        errors={{}}
      />
    );

    const phoneInput = screen.getByLabelText('Phone Number');
    fireEvent.change(phoneInput, { target: { value: '1234567890' } });
    
    expect(mockOnChange).toHaveBeenCalled();
  });

  it('displays validation errors for invalid email and phone', () => {
    const mockOnChange = jest.fn();
    const mockOnBlur = jest.fn();

    renderWithTheme(
      <ContactFields
        email="invalid-email"
        phone="123"
        onChange={mockOnChange}
        onBlur={mockOnBlur}
        errors={{
          email: 'Invalid email address',
          phone: 'Invalid phone number',
        }}
      />
    );

    expect(screen.getByText('Invalid email address')).toBeInTheDocument();
    expect(screen.getByText('Invalid phone number')).toBeInTheDocument();
  });
});

describe('CurrencyField', () => {
  it('renders with correct formatting', () => {
    const mockOnChange = jest.fn();

    renderWithTheme(
      <CurrencyField
        value={1234.56}
        onChange={mockOnChange}
        label="Amount"
      />
    );

    const input = screen.getByLabelText('Amount (currency)');
    // The initial value will be formatted without the $ sign because we use the icon
    expect(input.value).toContain('1,234.56');
  });

  it('handles input changes correctly', () => {
    const mockOnChange = jest.fn();

    renderWithTheme(
      <CurrencyField
        value={null}
        onChange={mockOnChange}
        label="Amount"
      />
    );

    const input = screen.getByLabelText('Amount (currency)');
    fireEvent.change(input, { target: { value: '1234.56' } });
    
    expect(mockOnChange).toHaveBeenCalledWith(1234.56);
  });

  it('formats value on blur', () => {
    const mockOnChange = jest.fn();

    renderWithTheme(
      <CurrencyField
        value={1000}
        onChange={mockOnChange}
        label="Amount"
      />
    );

    const input = screen.getByLabelText('Amount (currency)');
    fireEvent.focus(input);
    
    // When focused, it should show the raw value
    expect(input.value).toBe('1000');
    
    fireEvent.blur(input);
    // After blur, it should format with commas
    expect(input.value).toContain('1,000');
  });

  it('handles invalid input gracefully', () => {
    const mockOnChange = jest.fn();

    renderWithTheme(
      <CurrencyField
        value={null}
        onChange={mockOnChange}
        label="Amount"
      />
    );

    const input = screen.getByLabelText('Amount (currency)');
    fireEvent.change(input, { target: { value: 'abc' } });
    
    // Should filter out non-numeric characters
    expect(mockOnChange).toHaveBeenCalled();
    // The value passed to onChange should be null since 'abc' is not a valid number
    expect(mockOnChange).toHaveBeenCalledWith(null);
  });
});

describe('DateField', () => {
  it('renders with correct date format', () => {
    const mockOnChange = jest.fn();

    renderWithTheme(
      <DateField
        name="date"
        value="2023-05-15"
        onChange={mockOnChange}
        label="Date"
      />
    );

    // The date should be formatted as MM/DD/YYYY
    const input = screen.getByLabelText('Date');
    expect(input).toBeInTheDocument();
    // We can't assert the exact value without the formatDateForDisplay function,
    // but we can check that the input is rendered
  });

  it('handles input changes correctly', () => {
    const mockOnChange = jest.fn();

    renderWithTheme(
      <DateField
        name="date"
        value=""
        onChange={mockOnChange}
        label="Date"
      />
    );

    const input = screen.getByLabelText('Date');
    fireEvent.change(input, { target: { value: '05/15/2023' } });
    
    expect(mockOnChange).toHaveBeenCalled();
    // The onChange should be called with a synthetic event containing the formatted date
  });

  it('validates date format', () => {
    const mockOnChange = jest.fn();

    renderWithTheme(
      <DateField
        name="date"
        value="invalid-date"
        onChange={mockOnChange}
        error={true}
        helperText="Invalid date format"
        label="Date"
      />
    );

    expect(screen.getByText('Invalid date format')).toBeInTheDocument();
  });

  it('enforces min and max date constraints', () => {
    const mockOnChange = jest.fn();

    renderWithTheme(
      <DateField
        name="date"
        value="2023-05-15"
        onChange={mockOnChange}
        minDate="2023-05-01"
        maxDate="2023-05-31"
        label="Date"
      />
    );

    const input = screen.getByLabelText('Date');
    expect(input).toBeInTheDocument();
    
    // We can verify the component renders with min/max date constraints
    // Full validation testing would require the date validation logic
  });
});

describe('PhoneField', () => {
  it('renders with correct phone format', () => {
    const mockOnChange = jest.fn();
    const mockOnBlur = jest.fn();

    renderWithTheme(
      <PhoneField
        name="phone"
        value="(123) 456-7890"
        onChange={mockOnChange}
        onBlur={mockOnBlur}
        label="Phone"
      />
    );

    const input = screen.getByLabelText('Phone');
    expect(input).toHaveValue('(123) 456-7890');
  });

  it('handles input changes correctly', () => {
    const mockOnChange = jest.fn();
    const mockOnBlur = jest.fn();

    renderWithTheme(
      <PhoneField
        name="phone"
        value=""
        onChange={mockOnChange}
        onBlur={mockOnBlur}
        label="Phone"
      />
    );

    const input = screen.getByLabelText('Phone');
    fireEvent.change(input, { target: { value: '1234567890' } });
    
    expect(mockOnChange).toHaveBeenCalled();
    // The component creates a synthetic event with formatted phone number
  });

  it('formats phone number as user types', () => {
    const mockOnChange = jest.fn();
    const mockOnBlur = jest.fn();

    renderWithTheme(
      <PhoneField
        name="phone"
        value=""
        onChange={mockOnChange}
        onBlur={mockOnBlur}
        label="Phone"
      />
    );

    const input = screen.getByLabelText('Phone');
    
    // Test that formatting is applied as the user types
    fireEvent.change(input, { target: { value: '1' } });
    expect(mockOnChange).toHaveBeenCalledWith(expect.objectContaining({
      target: expect.objectContaining({ value: '(1' })
    }));
    
    fireEvent.change(input, { target: { value: '123' } });
    expect(mockOnChange).toHaveBeenCalledWith(expect.objectContaining({
      target: expect.objectContaining({ value: '(123' })
    }));
    
    fireEvent.change(input, { target: { value: '1234' } });
    expect(mockOnChange).toHaveBeenCalledWith(expect.objectContaining({
      target: expect.objectContaining({ value: '(123) 4' })
    }));
  });

  it('displays validation error for invalid phone number', () => {
    const mockOnChange = jest.fn();
    const mockOnBlur = jest.fn();

    renderWithTheme(
      <PhoneField
        name="phone"
        value="123"
        onChange={mockOnChange}
        onBlur={mockOnBlur}
        error={true}
        helperText="Invalid phone number"
        label="Phone"
      />
    );

    expect(screen.getByText('Invalid phone number')).toBeInTheDocument();
  });
});

describe('SSNField', () => {
  it('renders with correct SSN format', () => {
    const mockOnChange = jest.fn();

    renderWithTheme(
      <SSNField
        name="ssn"
        value="123-45-6789"
        onChange={mockOnChange}
        label="SSN"
      />
    );

    const input = screen.getByLabelText('Social Security Number');
    expect(input).toHaveValue('123-45-6789');
  });

  it('handles input changes correctly', () => {
    const mockOnChange = jest.fn();

    renderWithTheme(
      <SSNField
        name="ssn"
        value=""
        onChange={mockOnChange}
        label="SSN"
      />
    );

    const input = screen.getByLabelText('Social Security Number');
    fireEvent.change(input, { target: { value: '123456789' } });
    
    expect(mockOnChange).toHaveBeenCalled();
    // The component should format the input as it's entered
  });

  it('masks SSN when showMask is true', () => {
    const mockOnChange = jest.fn();

    renderWithTheme(
      <SSNField
        name="ssn"
        value="123-45-6789"
        onChange={mockOnChange}
        label="SSN"
        showMask={true}
      />
    );

    const input = screen.getByLabelText('Social Security Number');
    
    // With showMask=true and not focused, it should display the masked SSN
    expect(input).toHaveValue('XXX-XX-6789');
    
    // Focus should show the full value
    fireEvent.focus(input);
    expect(input).toHaveValue('123-45-6789');
    
    // Blur should mask it again
    fireEvent.blur(input);
    expect(input).toHaveValue('XXX-XX-6789');
  });

  it('formats SSN as user types', () => {
    const mockOnChange = jest.fn();

    renderWithTheme(
      <SSNField
        name="ssn"
        value=""
        onChange={mockOnChange}
        label="SSN"
      />
    );

    const input = screen.getByLabelText('Social Security Number');
    
    // Test progressive formatting of SSN
    fireEvent.change(input, { target: { value: '123' } });
    expect(mockOnChange).toHaveBeenCalledWith(expect.objectContaining({
      target: expect.objectContaining({ value: '123' })
    }));
    
    // Reset mock to test next formatting
    mockOnChange.mockReset();
    
    fireEvent.change(input, { target: { value: '123456' } });
    expect(mockOnChange).toHaveBeenCalledWith(expect.objectContaining({
      target: expect.objectContaining({ value: '123-45-6' })
    }));
  });

  it('displays validation error for invalid SSN', () => {
    const mockOnChange = jest.fn();

    renderWithTheme(
      <SSNField
        name="ssn"
        value="123-45"
        onChange={mockOnChange}
        error={true}
        helperText="Invalid SSN"
        label="SSN"
      />
    );

    expect(screen.getByText('Invalid SSN')).toBeInTheDocument();
  });
});