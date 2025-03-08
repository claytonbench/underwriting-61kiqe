import React from 'react';
import { Grid, TextField, MenuItem, FormHelperText } from '@mui/material';
import useStyles from './styles';
import { isRequired, isZipCode, isValidState } from '../../utils/validation';
import { Address } from '../../types/common.types';

// Define US states for the dropdown
const US_STATES = [
  { value: 'AL', label: 'Alabama' },
  { value: 'AK', label: 'Alaska' },
  { value: 'AZ', label: 'Arizona' },
  { value: 'AR', label: 'Arkansas' },
  { value: 'CA', label: 'California' },
  { value: 'CO', label: 'Colorado' },
  { value: 'CT', label: 'Connecticut' },
  { value: 'DE', label: 'Delaware' },
  { value: 'FL', label: 'Florida' },
  { value: 'GA', label: 'Georgia' },
  { value: 'HI', label: 'Hawaii' },
  { value: 'ID', label: 'Idaho' },
  { value: 'IL', label: 'Illinois' },
  { value: 'IN', label: 'Indiana' },
  { value: 'IA', label: 'Iowa' },
  { value: 'KS', label: 'Kansas' },
  { value: 'KY', label: 'Kentucky' },
  { value: 'LA', label: 'Louisiana' },
  { value: 'ME', label: 'Maine' },
  { value: 'MD', label: 'Maryland' },
  { value: 'MA', label: 'Massachusetts' },
  { value: 'MI', label: 'Michigan' },
  { value: 'MN', label: 'Minnesota' },
  { value: 'MS', label: 'Mississippi' },
  { value: 'MO', label: 'Missouri' },
  { value: 'MT', label: 'Montana' },
  { value: 'NE', label: 'Nebraska' },
  { value: 'NV', label: 'Nevada' },
  { value: 'NH', label: 'New Hampshire' },
  { value: 'NJ', label: 'New Jersey' },
  { value: 'NM', label: 'New Mexico' },
  { value: 'NY', label: 'New York' },
  { value: 'NC', label: 'North Carolina' },
  { value: 'ND', label: 'North Dakota' },
  { value: 'OH', label: 'Ohio' },
  { value: 'OK', label: 'Oklahoma' },
  { value: 'OR', label: 'Oregon' },
  { value: 'PA', label: 'Pennsylvania' },
  { value: 'RI', label: 'Rhode Island' },
  { value: 'SC', label: 'South Carolina' },
  { value: 'SD', label: 'South Dakota' },
  { value: 'TN', label: 'Tennessee' },
  { value: 'TX', label: 'Texas' },
  { value: 'UT', label: 'Utah' },
  { value: 'VT', label: 'Vermont' },
  { value: 'VA', label: 'Virginia' },
  { value: 'WA', label: 'Washington' },
  { value: 'WV', label: 'West Virginia' },
  { value: 'WI', label: 'Wisconsin' },
  { value: 'WY', label: 'Wyoming' },
  { value: 'DC', label: 'District of Columbia' },
  { value: 'AS', label: 'American Samoa' },
  { value: 'GU', label: 'Guam' },
  { value: 'MP', label: 'Northern Mariana Islands' },
  { value: 'PR', label: 'Puerto Rico' },
  { value: 'VI', label: 'U.S. Virgin Islands' },
];

interface AddressFieldsProps {
  values: Record<string, any>;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleBlur: (e: React.FocusEvent<HTMLInputElement>) => void;
  prefix: string;
  required?: boolean;
  disabled?: boolean;
}

/**
 * AddressFields component
 * 
 * A reusable form component that renders address input fields including
 * street address, city, state, and ZIP code. It integrates with form state
 * management and provides validation feedback for address fields.
 * 
 * @param values - Object containing form values
 * @param errors - Object containing error messages for form fields
 * @param touched - Object indicating which fields have been touched/visited
 * @param handleChange - Function to handle input changes
 * @param handleBlur - Function to handle input blur events
 * @param prefix - String prefix for field names (e.g., "borrower_" or "co_borrower_")
 * @param required - Whether the address fields are required
 * @param disabled - Whether the address fields should be disabled
 */
const AddressFields: React.FC<AddressFieldsProps> = ({
  values,
  errors,
  touched,
  handleChange,
  handleBlur,
  prefix,
  required = false,
  disabled = false,
}) => {
  const classes = useStyles();
  
  // Field names with prefix
  const addressLine1Field = `${prefix}address_line1`;
  const addressLine2Field = `${prefix}address_line2`;
  const cityField = `${prefix}city`;
  const stateField = `${prefix}state`;
  const zipCodeField = `${prefix}zip_code`;
  
  return (
    <Grid container spacing={2} className={classes.addressFields}>
      {/* Address Line 1 */}
      <Grid item xs={12}>
        <TextField
          id={addressLine1Field}
          name={addressLine1Field}
          label="Street Address"
          value={values[addressLine1Field] || ''}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched[addressLine1Field] && Boolean(errors[addressLine1Field])}
          helperText={
            touched[addressLine1Field] && errors[addressLine1Field] ? (
              errors[addressLine1Field]
            ) : null
          }
          fullWidth
          required={required}
          disabled={disabled}
          inputProps={{
            'aria-label': 'Street Address',
            'data-testid': addressLine1Field
          }}
        />
      </Grid>
      
      {/* Address Line 2 */}
      <Grid item xs={12}>
        <TextField
          id={addressLine2Field}
          name={addressLine2Field}
          label="Apartment, suite, etc. (optional)"
          value={values[addressLine2Field] || ''}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched[addressLine2Field] && Boolean(errors[addressLine2Field])}
          helperText={
            touched[addressLine2Field] && errors[addressLine2Field] ? (
              errors[addressLine2Field]
            ) : null
          }
          fullWidth
          disabled={disabled}
          inputProps={{
            'aria-label': 'Apartment, suite, etc.',
            'data-testid': addressLine2Field
          }}
        />
      </Grid>
      
      {/* City */}
      <Grid item xs={12} sm={5}>
        <TextField
          id={cityField}
          name={cityField}
          label="City"
          value={values[cityField] || ''}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched[cityField] && Boolean(errors[cityField])}
          helperText={
            touched[cityField] && errors[cityField] ? (
              errors[cityField]
            ) : null
          }
          fullWidth
          required={required}
          disabled={disabled}
          inputProps={{
            'aria-label': 'City',
            'data-testid': cityField
          }}
        />
      </Grid>
      
      {/* State */}
      <Grid item xs={6} sm={3}>
        <TextField
          id={stateField}
          name={stateField}
          label="State"
          select
          value={values[stateField] || ''}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched[stateField] && Boolean(errors[stateField])}
          helperText={
            touched[stateField] && errors[stateField] ? (
              errors[stateField]
            ) : null
          }
          fullWidth
          required={required}
          disabled={disabled}
          SelectProps={{
            MenuProps: {
              'aria-label': 'State Selection Menu',
              PaperProps: {
                style: {
                  maxHeight: 300
                }
              }
            }
          }}
          inputProps={{
            'aria-label': 'State',
            'data-testid': stateField
          }}
        >
          <MenuItem value="">
            <em>Select State</em>
          </MenuItem>
          {US_STATES.map((state) => (
            <MenuItem key={state.value} value={state.value}>
              {state.label}
            </MenuItem>
          ))}
        </TextField>
      </Grid>
      
      {/* ZIP Code */}
      <Grid item xs={6} sm={4}>
        <TextField
          id={zipCodeField}
          name={zipCodeField}
          label="ZIP Code"
          value={values[zipCodeField] || ''}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched[zipCodeField] && Boolean(errors[zipCodeField])}
          helperText={
            touched[zipCodeField] && errors[zipCodeField] ? (
              errors[zipCodeField]
            ) : null
          }
          fullWidth
          required={required}
          disabled={disabled}
          inputProps={{
            'aria-label': 'ZIP Code',
            'data-testid': zipCodeField,
            maxLength: 10
          }}
        />
      </Grid>
    </Grid>
  );
};

export default AddressFields;