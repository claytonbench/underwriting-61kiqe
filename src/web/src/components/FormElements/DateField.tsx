import React from 'react';
import { TextField, InputAdornment, InputProps } from '@mui/material';
import { CalendarToday } from '@mui/icons-material';

import useStyles from './styles';
import { isValidDate, formatDateForDisplay, parseDateFromDisplay } from '../../utils/date';
import { ISO8601Date } from '../../types/common.types';
import { DATE_FORMATS } from '../../config/constants';

interface DateFieldProps {
  name: string;
  value: string | ISO8601Date | null;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur?: (e: React.FocusEvent<HTMLInputElement>) => void;
  error?: boolean;
  helperText?: string;
  required?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  label?: string;
  placeholder?: string;
  minDate?: Date | string | null;
  maxDate?: Date | string | null;
  InputProps?: Partial<InputProps>;
}

const DateField = ({
  name,
  value,
  onChange,
  onBlur,
  error = false,
  helperText = '',
  required = false,
  disabled = false,
  fullWidth = true,
  label,
  placeholder = DATE_FORMATS.DISPLAY,
  minDate = null,
  maxDate = null,
  InputProps = {},
  ...rest
}: DateFieldProps): JSX.Element => {
  const styles = useStyles();
  
  // Format the input value for display
  const displayValue = value ? formatDateForDisplay(value) : '';
  
  // Handle input formatting as user types
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let inputValue = e.target.value;
    
    // Remove any non-digit and non-slash characters
    inputValue = inputValue.replace(/[^\d/]/g, '');
    
    // Format input as MM/DD/YYYY
    const digits = inputValue.replace(/\//g, '');
    
    if (digits.length > 0) {
      // Format the digits with slashes
      if (digits.length <= 2) {
        // Just the month part
        inputValue = digits;
      } else if (digits.length <= 4) {
        // Month and part/all of day
        inputValue = `${digits.slice(0, 2)}/${digits.slice(2)}`;
      } else {
        // Month, day, and part/all of year
        inputValue = `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4, 8)}`;
      }
    }
    
    // Ensure value doesn't exceed MM/DD/YYYY format (10 chars)
    inputValue = inputValue.slice(0, 10);
    
    // Create a modified event with the formatted value
    const modifiedEvent = {
      ...e,
      target: {
        ...e.target,
        name,
        value: inputValue
      }
    } as React.ChangeEvent<HTMLInputElement>;
    
    onChange(modifiedEvent);
  };
  
  // Check if the entered date is within the min/max range
  const isDateOutOfRange = React.useMemo(() => {
    if (!displayValue || !isValidDate(displayValue)) {
      return false; // Empty or invalid dates handled by separate validation
    }
    
    const dateValue = parseDateFromDisplay(displayValue);
    if (!dateValue) return false;
    
    // Check min date constraint
    if (minDate) {
      const minDateObj = typeof minDate === 'string' 
        ? parseDateFromDisplay(formatDateForDisplay(minDate))
        : minDate;
      
      if (minDateObj && dateValue < minDateObj) {
        return true; // Out of range
      }
    }
    
    // Check max date constraint
    if (maxDate) {
      const maxDateObj = typeof maxDate === 'string' 
        ? parseDateFromDisplay(formatDateForDisplay(maxDate))
        : maxDate;
      
      if (maxDateObj && dateValue > maxDateObj) {
        return true; // Out of range
      }
    }
    
    return false; // Within range
  }, [displayValue, minDate, maxDate]);
  
  // Get appropriate validation message
  const getValidationMessage = (): string => {
    if (isDateOutOfRange) {
      if (minDate && maxDate) {
        return `Date must be between ${formatDateForDisplay(minDate)} and ${formatDateForDisplay(maxDate)}`;
      } else if (minDate) {
        return `Date must be on or after ${formatDateForDisplay(minDate)}`;
      } else if (maxDate) {
        return `Date must be on or before ${formatDateForDisplay(maxDate)}`;
      }
    }
    return helperText;
  };
  
  // Determine if we should show an error
  const showError = error || isDateOutOfRange;
  
  // Get the appropriate helper text
  const dateHelperText = isDateOutOfRange ? getValidationMessage() : helperText;
  
  return (
    <TextField
      type="text"
      name={name}
      value={displayValue}
      onChange={handleChange}
      onBlur={onBlur}
      error={showError}
      helperText={dateHelperText}
      required={required}
      disabled={disabled}
      fullWidth={fullWidth}
      label={label}
      placeholder={placeholder}
      className={styles.dateInput}
      InputProps={{
        ...InputProps,
        endAdornment: (
          <InputAdornment position="end" className={styles.inputAdornment}>
            <CalendarToday />
          </InputAdornment>
        ),
      }}
      inputProps={{
        'aria-label': label || 'Date',
        'aria-invalid': showError,
        'aria-describedby': dateHelperText ? `${name}-helper-text` : undefined,
        maxLength: 10,
        inputMode: 'numeric'
      }}
      {...rest}
    />
  );
};

export default DateField;