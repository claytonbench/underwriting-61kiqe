import React, { useState } from 'react';
import { TextField, InputAdornment, TextFieldProps } from '@mui/material'; // v5.14.0
import AttachMoneyIcon from '@mui/icons-material/AttachMoney'; // v5.14.0
import useStyles from './styles';
import { formatCurrency, parseCurrency } from '../../utils/formatting';

/**
 * Props for the CurrencyField component
 */
interface CurrencyFieldProps {
  /** The current numeric value of the field */
  value: number | null;
  /** Callback function when value changes */
  onChange: (value: number | null) => void;
  /** Label text for the field */
  label: string;
  /** Whether the field has an error */
  error?: boolean;
  /** Helper or error text to display below the field */
  helperText?: string;
  /** Whether the field is disabled */
  disabled?: boolean;
  /** Whether the field is required */
  required?: boolean;
  /** Whether the field should take up the full width of its container */
  fullWidth?: boolean;
  /** Placeholder text when field is empty */
  placeholder?: string;
  /** Props applied to the input element */
  inputProps?: object;
}

/**
 * A specialized form input component for currency values that handles formatting
 * and parsing of monetary inputs. It displays values with proper currency formatting
 * (e.g., $1,234.56) while allowing users to input numbers in a natural way.
 */
const CurrencyField = ({
  value,
  onChange,
  label,
  error,
  helperText,
  ...props
}: CurrencyFieldProps & Omit<TextFieldProps, 'value' | 'onChange'>): JSX.Element => {
  const classes = useStyles();
  
  // Format the initial display value, removing the $ since we have the icon
  const initialDisplayValue = value !== null && value !== undefined
    ? formatCurrency(value).replace(/^\$/, '')
    : '';
  
  const [displayValue, setDisplayValue] = useState<string>(initialDisplayValue);

  /**
   * Handles input changes and converts to numeric value
   */
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const input = event.target.value;
    
    // Remove all non-numeric characters except for the decimal point
    const cleanedInput = input.replace(/[^\d.]/g, '');
    
    // Ensure only one decimal point
    const parts = cleanedInput.split('.');
    const sanitizedInput = parts[0] + (parts.length > 1 ? '.' + parts.slice(1).join('') : '');
    
    setDisplayValue(sanitizedInput);
    
    // Convert to number and call onChange
    const numValue = parseCurrency(sanitizedInput);
    onChange(numValue);
  };

  /**
   * Formats the value when the field loses focus
   */
  const handleBlur = () => {
    if (value === null || value === undefined) {
      setDisplayValue('');
    } else {
      // Format and remove the $ since we show it as an icon
      const formatted = formatCurrency(value).replace(/^\$/, '');
      setDisplayValue(formatted);
    }
  };

  /**
   * Selects all text when the field gains focus
   */
  const handleFocus = (event: React.FocusEvent<HTMLInputElement>) => {
    // Show raw number when the field gains focus for easier editing
    if (value !== null && value !== undefined) {
      setDisplayValue(value.toString());
    } else {
      setDisplayValue('');
    }
    
    // Select all text for easy replacement
    event.target.select();
  };

  return (
    <TextField
      {...props}
      label={label}
      value={displayValue}
      onChange={handleChange}
      onBlur={handleBlur}
      onFocus={handleFocus}
      error={error}
      helperText={helperText}
      InputProps={{
        startAdornment: (
          <InputAdornment position="start">
            <AttachMoneyIcon className={classes.inputAdornment} />
          </InputAdornment>
        ),
        className: classes.currencyInput,
        ...props.InputProps
      }}
      inputProps={{
        inputMode: 'decimal',
        'aria-label': `${label} (currency)`,
        ...props.inputProps
      }}
    />
  );
};

export default CurrencyField;