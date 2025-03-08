import React from 'react';
import { TextField, InputAdornment, InputProps as MuiInputProps } from '@mui/material'; // v5.14.0
import { Badge } from '@mui/icons-material'; // v5.14.0
import useStyles from './styles';
import { isSSN } from '../../utils/validation';
import { formatSSN, parseSSN } from '../../utils/formatting';
import { SSN } from '../../types/common.types';
import { VALIDATION } from '../../config/constants';

/**
 * Props interface for the SSNField component
 */
interface SSNFieldProps {
  name: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur?: (e: React.FocusEvent<HTMLInputElement>) => void;
  error?: boolean;
  helperText?: string;
  required?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  label?: string;
  placeholder?: string;
  showMask?: boolean;
  InputProps?: Partial<MuiInputProps>;
}

/**
 * A specialized form input component for Social Security Numbers
 * Handles formatting, validation, and security masking automatically
 * 
 * @param props Component props
 * @returns The rendered SSN field component
 */
const SSNField: React.FC<SSNFieldProps> = ({
  name,
  value,
  onChange,
  onBlur,
  error = false,
  helperText = '',
  required = false,
  disabled = false,
  fullWidth = true,
  label = 'Social Security Number',
  placeholder = 'XXX-XX-XXXX',
  showMask = false,
  InputProps,
  ...rest
}) => {
  const classes = useStyles();
  const [isFocused, setIsFocused] = React.useState(false);
  
  /**
   * Handles input changes, automatically formatting as SSN
   */
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Remove non-digits from input
    const rawValue = e.target.value.replace(/\D/g, '');
    
    // Format as SSN with hyphens
    const formatted = formatSSN(rawValue);
    
    // Create a new event with the formatted value
    const newEvent = {
      ...e,
      target: {
        ...e.target,
        value: formatted
      }
    };
    onChange(newEvent);
  };
  
  /**
   * Sets focus state to true when field gains focus
   */
  const handleFocus = () => {
    setIsFocused(true);
  };
  
  /**
   * Sets focus state to false and calls onBlur prop if provided
   */
  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    setIsFocused(false);
    if (onBlur) {
      onBlur(e);
    }
  };
  
  // Only mask the SSN when showMask is true, field is not focused, and we have a valid SSN
  let displayValue = value;
  if (showMask && !isFocused && value) {
    const ssnDigits = parseSSN(value);
    if (ssnDigits && ssnDigits.length === 9) {
      // Show only last 4 digits for security
      displayValue = `XXX-XX-${ssnDigits.slice(5, 9)}`;
    }
  }
  
  return (
    <TextField
      name={name}
      value={displayValue}
      onChange={handleChange}
      onFocus={handleFocus}
      onBlur={handleBlur}
      error={error}
      helperText={helperText}
      required={required}
      disabled={disabled}
      fullWidth={fullWidth}
      label={label}
      placeholder={placeholder}
      className={classes.formControl}
      InputProps={{
        classes: {
          root: classes.ssnInput,
        },
        startAdornment: (
          <InputAdornment position="start" className={classes.inputAdornment}>
            <Badge />
          </InputAdornment>
        ),
        ...InputProps,
      }}
      inputProps={{
        'aria-label': 'Social Security Number',
        'aria-required': required,
        'aria-invalid': error,
        'aria-describedby': error ? `${name}-helper-text` : undefined,
        maxLength: 11, // XXX-XX-XXXX is 11 characters
        pattern: VALIDATION.SSN.PATTERN.source, // Use regex pattern for HTML5 validation
        inputMode: 'numeric', // Show numeric keyboard on mobile devices
        autoComplete: 'off', // Disable autocomplete for security
      }}
      {...rest}
    />
  );
};

export default SSNField;