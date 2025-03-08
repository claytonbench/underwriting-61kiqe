import { makeStyles } from '@mui/styles'; // v5.14.0
import { Theme } from '@mui/material'; // v5.14.0
import { mediaQueries } from '../../responsive/breakpoints';
import { lightTheme } from '../../config/theme';

/**
 * Custom hook that returns style classes for form elements
 * Provides consistent styling for specialized form inputs like address fields,
 * contact fields, currency fields, date fields, phone fields, and SSN fields
 * throughout the loan management system.
 * 
 * @returns CSS class names for form elements
 */
const useStyles = makeStyles((theme: Theme = lightTheme) => ({
  // Base styling for form control elements
  formControl: {
    marginBottom: '16px',
    width: '100%',
  },
  
  // Styling for form labels
  formLabel: {
    fontWeight: 500,
    marginBottom: '8px',
    color: theme.palette.text.primary,
  },
  
  // Styling for helper text and error messages
  formHelperText: {
    marginTop: '4px',
    fontSize: '12px',
  },
  
  // Styling for input fields with focus effects
  inputField: {
    width: '100%',
    backgroundColor: theme.palette.background.paper,
    borderRadius: '4px',
    transition: 'all 0.2s ease-in-out',
    '&:focus-within': {
      boxShadow: '0 0 0 2px rgba(25, 118, 210, 0.2)',
    },
  },
  
  // Specialized styling for currency input fields
  currencyInput: {
    fontFamily: "'Roboto Mono', monospace",
    textAlign: 'right',
  },
  
  // Specialized styling for date input fields
  dateInput: {
    fontFamily: "'Roboto Mono', monospace",
  },
  
  // Specialized styling for phone input fields
  phoneInput: {
    fontFamily: "'Roboto Mono', monospace",
  },
  
  // Specialized styling for SSN input fields
  ssnInput: {
    fontFamily: "'Roboto Mono', monospace",
    letterSpacing: '0.5px',
  },
  
  // Container styling for address field groups
  addressFields: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  
  // Container styling for contact field groups with responsive behavior
  contactFields: {
    display: 'flex',
    flexDirection: 'row',
    gap: '16px',
    [mediaQueries.mobile]: {
      flexDirection: 'column',
    },
  },
  
  // Styling for input adornments (icons)
  inputAdornment: {
    color: theme.palette.text.secondary,
  },
  
  // Styling for error messages
  errorText: {
    color: theme.palette.error.main,
  },
  
  // Styling for disabled form elements
  disabled: {
    opacity: 0.7,
    cursor: 'not-allowed',
  },
}));

export default useStyles;