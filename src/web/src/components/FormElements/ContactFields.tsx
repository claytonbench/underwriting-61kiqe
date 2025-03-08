import React from 'react';
import { TextField, Grid, InputAdornment } from '@mui/material'; // v5.14.0
import { Email } from '@mui/icons-material'; // v5.14.0
import useStyles from './styles';
import PhoneField from './PhoneField';
import { isEmail } from '../../utils/validation';
import { EmailAddress, PhoneNumber } from '../../types/common.types';

/**
 * Props interface for the ContactFields component
 */
interface ContactFieldsProps {
  email: EmailAddress;
  phone: PhoneNumber;
  onChange: (field: string, value: string) => void;
  onBlur: (field: string) => void;
  errors: Record<string, string>;
  disabled?: boolean;
  required?: boolean;
  spacing?: number;
}

/**
 * A component that renders email and phone input fields for contact information
 * Provides consistent styling, validation, and formatting for contact fields
 * throughout the loan management system.
 */
const ContactFields = ({
  email,
  phone,
  onChange,
  onBlur,
  errors,
  disabled = false,
  required = false,
  spacing = 2,
}: ContactFieldsProps): JSX.Element => {
  const classes = useStyles();

  /**
   * Handles changes to the email input field
   * @param e - The change event from the email input
   */
  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    onChange('email', newValue);
  };

  /**
   * Handles changes to the phone input field
   * @param e - The change event from the phone input
   */
  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange('phone', e.target.value);
  };

  return (
    <Grid container spacing={spacing} className={classes.contactFields}>
      <Grid item xs={12} sm={6}>
        <TextField
          label="Email Address"
          value={email}
          onChange={handleEmailChange}
          onBlur={() => onBlur('email')}
          fullWidth
          required={required}
          disabled={disabled}
          error={!!errors.email}
          helperText={errors.email || ''}
          className={classes.inputField}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start" className={classes.inputAdornment}>
                <Email />
              </InputAdornment>
            ),
          }}
          inputProps={{
            'aria-label': 'Email Address',
            'aria-required': required,
            'aria-invalid': !!errors.email,
            'data-testid': 'email-input',
            type: 'email',
            autoComplete: 'email',
          }}
        />
      </Grid>
      <Grid item xs={12} sm={6}>
        <PhoneField
          name="phone"
          value={phone}
          onChange={handlePhoneChange}
          onBlur={() => onBlur('phone')}
          error={!!errors.phone}
          helperText={errors.phone || ''}
          required={required}
          disabled={disabled}
          label="Phone Number"
          fullWidth
          placeholder="(XXX) XXX-XXXX"
        />
      </Grid>
    </Grid>
  );
};

export default ContactFields;