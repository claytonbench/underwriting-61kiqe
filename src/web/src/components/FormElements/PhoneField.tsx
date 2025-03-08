import React from 'react';
import { TextField, InputAdornment } from '@mui/material';
import { Phone } from '@mui/icons-material';
import useStyles from './styles';
import { isPhoneNumber } from '../../utils/validation';
import { formatPhoneNumber, parsePhoneNumber } from '../../utils/formatting';
import { PhoneNumber } from '../../types/common.types';
import { VALIDATION } from '../../config/constants';

/**
 * Props interface for the PhoneField component
 */
interface PhoneFieldProps {
  name: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur: (e: React.FocusEvent<HTMLInputElement>) => void;
  error?: boolean;
  helperText?: string;
  required?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  label?: string;
  placeholder?: string;
  InputProps?: Partial<React.ComponentProps<typeof TextField>['InputProps']>;
}

/**
 * A specialized input field component for phone numbers with automatic formatting
 * Formats input as a US phone number pattern (XXX) XXX-XXXX while providing proper validation
 * feedback and accessibility attributes.
 */
const PhoneField = ({
  name,
  value,
  onChange,
  onBlur,
  error = false,
  helperText = '',
  required = false,
  disabled = false,
  fullWidth = true,
  label = 'Phone Number',
  placeholder = '(XXX) XXX-XXXX',
  InputProps,
  ...otherProps
}: PhoneFieldProps) => {
  const classes = useStyles();

  /**
   * Handles input changes and formats the phone number as the user types
   */
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Extract only digits from the input
    const digits = e.target.value.replace(/\D/g, '');
    
    // Format according to number of digits entered
    let formattedValue = '';
    if (digits.length > 0) {
      if (digits.length <= 3) {
        formattedValue = `(${digits}`;
      } else if (digits.length <= 6) {
        formattedValue = `(${digits.slice(0, 3)}) ${digits.slice(3)}`;
      } else {
        formattedValue = `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6, 10)}`;
      }
    }
    
    // Create a new synthetic event with the formatted value
    const newEvent = {
      ...e,
      target: {
        ...e.target,
        value: formattedValue
      }
    } as React.ChangeEvent<HTMLInputElement>;
    
    onChange(newEvent);
  };

  return (
    <TextField
      name={name}
      value={value}
      onChange={handleChange}
      onBlur={onBlur}
      error={error}
      helperText={helperText}
      required={required}
      disabled={disabled}
      fullWidth={fullWidth}
      label={label}
      placeholder={placeholder}
      InputProps={{
        ...InputProps,
        startAdornment: (
          <InputAdornment position="start" className={classes.inputAdornment}>
            <Phone />
          </InputAdornment>
        ),
      }}
      inputProps={{
        className: classes.phoneInput,
        'aria-label': label,
        'aria-required': required,
        'aria-invalid': error,
        inputMode: 'tel',
        pattern: VALIDATION.PHONE.PATTERN.toString().slice(1, -1),
      }}
      {...otherProps}
    />
  );
};

export default PhoneField;