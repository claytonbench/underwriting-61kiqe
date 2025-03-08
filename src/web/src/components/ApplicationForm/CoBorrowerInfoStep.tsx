import React from 'react';
import {
  Grid,
  TextField,
  Typography,
  FormControl,
  FormLabel,
  RadioGroup,
  Radio,
  FormControlLabel,
  FormHelperText,
  Checkbox,
  MenuItem,
  Select,
  InputAdornment
} from '@mui/material'; // v5.14.0

import {
  AddressFields,
  SSNField,
  DateField,
  PhoneField
} from '../FormElements';
import useStyles from './styles';
import {
  CitizenshipStatus,
  RelationshipType,
  EmploymentType,
  CoBorrowerFormData
} from '../../types/application.types';
import {
  isRequired,
  isEmail,
  isDate,
  isAdult
} from '../../utils/validation';

/**
 * Props interface for the CoBorrowerInfoStep component
 */
interface CoBorrowerInfoStepProps {
  values: Record<string, any>;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleBlur: (e: React.FocusEvent<HTMLInputElement>) => void;
  setFieldValue: (field: string, value: any) => void;
  setFieldTouched: (field: string, touched: boolean) => void;
  isSubmitting: boolean;
  isValid: boolean;
}

/**
 * Component that renders the co-borrower information step of the loan application form
 * Collects relationship type, personal information, address, and employment details
 * 
 * @param props - The component props
 * @returns The rendered component or null if no co-borrower
 */
const CoBorrowerInfoStep: React.FC<CoBorrowerInfoStepProps> = ({
  values,
  errors,
  touched,
  handleChange,
  handleBlur,
  setFieldValue,
  setFieldTouched,
  isSubmitting,
  isValid
}) => {
  const classes = useStyles();

  // If has_co_borrower is false, don't render this step
  if (!values.has_co_borrower) {
    return null;
  }

  /**
   * Handles changes to the "Same Address as Borrower" checkbox
   * @param event The change event
   */
  const handleSameAddressChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const checked = event.target.checked;
    setFieldValue('co_borrower_info.same_address', checked);
    
    // If checked, clear address field errors and values
    if (checked) {
      // Clear address field errors by marking them as untouched
      setFieldTouched('co_borrower_info.address_line1', false);
      setFieldTouched('co_borrower_info.city', false);
      setFieldTouched('co_borrower_info.state', false);
      setFieldTouched('co_borrower_info.zip_code', false);
      
      // Clear address values to use borrower's address
      setFieldValue('co_borrower_info.address_line1', null);
      setFieldValue('co_borrower_info.address_line2', null);
      setFieldValue('co_borrower_info.city', null);
      setFieldValue('co_borrower_info.state', null);
      setFieldValue('co_borrower_info.zip_code', null);
    }
  };

  return (
    <Grid container spacing={3}>
      {/* Relationship Information Section */}
      <Grid item xs={12}>
        <Typography variant="h6" className={classes.sectionTitle}>
          Relationship to Borrower
        </Typography>
        <FormControl 
          component="fieldset" 
          fullWidth 
          required 
          error={touched['co_borrower_info.relationship'] && Boolean(errors['co_borrower_info.relationship'])}
        >
          <FormLabel component="legend">Relationship to Borrower</FormLabel>
          <RadioGroup
            aria-label="relationship-to-borrower"
            name="co_borrower_info.relationship"
            value={values.co_borrower_info?.relationship || ''}
            onChange={handleChange}
            onBlur={handleBlur}
            className={classes.radioGroup}
            data-testid="co-borrower-relationship"
          >
            <FormControlLabel value={RelationshipType.SPOUSE} control={<Radio />} label="Spouse" />
            <FormControlLabel value={RelationshipType.PARENT} control={<Radio />} label="Parent" />
            <FormControlLabel value={RelationshipType.SIBLING} control={<Radio />} label="Sibling" />
            <FormControlLabel value={RelationshipType.OTHER_RELATIVE} control={<Radio />} label="Other Relative" />
            <FormControlLabel value={RelationshipType.FRIEND} control={<Radio />} label="Friend" />
            <FormControlLabel value={RelationshipType.OTHER} control={<Radio />} label="Other" />
          </RadioGroup>
          {touched['co_borrower_info.relationship'] && errors['co_borrower_info.relationship'] && (
            <FormHelperText error>{errors['co_borrower_info.relationship']}</FormHelperText>
          )}
        </FormControl>
      </Grid>

      {/* Personal Information Section */}
      <Grid item xs={12}>
        <Typography variant="h6" className={classes.sectionTitle}>
          Personal Information
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={4}>
            <TextField
              label="First Name"
              name="co_borrower_info.first_name"
              value={values.co_borrower_info?.first_name || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched['co_borrower_info.first_name'] && Boolean(errors['co_borrower_info.first_name'])}
              helperText={touched['co_borrower_info.first_name'] && errors['co_borrower_info.first_name']}
              fullWidth
              required
              inputProps={{ 
                'aria-label': 'Co-borrower First Name',
                'data-testid': 'co-borrower-first-name'
              }}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              label="Middle Name"
              name="co_borrower_info.middle_name"
              value={values.co_borrower_info?.middle_name || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched['co_borrower_info.middle_name'] && Boolean(errors['co_borrower_info.middle_name'])}
              helperText={touched['co_borrower_info.middle_name'] && errors['co_borrower_info.middle_name']}
              fullWidth
              inputProps={{ 
                'aria-label': 'Co-borrower Middle Name',
                'data-testid': 'co-borrower-middle-name'
              }}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              label="Last Name"
              name="co_borrower_info.last_name"
              value={values.co_borrower_info?.last_name || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched['co_borrower_info.last_name'] && Boolean(errors['co_borrower_info.last_name'])}
              helperText={touched['co_borrower_info.last_name'] && errors['co_borrower_info.last_name']}
              fullWidth
              required
              inputProps={{ 
                'aria-label': 'Co-borrower Last Name',
                'data-testid': 'co-borrower-last-name'
              }}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <SSNField
              name="co_borrower_info.ssn"
              value={values.co_borrower_info?.ssn || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched['co_borrower_info.ssn'] && Boolean(errors['co_borrower_info.ssn'])}
              helperText={touched['co_borrower_info.ssn'] && errors['co_borrower_info.ssn']}
              required
              label="Social Security Number"
              placeholder="XXX-XX-XXXX"
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <DateField
              name="co_borrower_info.dob"
              label="Date of Birth"
              value={values.co_borrower_info?.dob || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched['co_borrower_info.dob'] && Boolean(errors['co_borrower_info.dob'])}
              helperText={touched['co_borrower_info.dob'] && errors['co_borrower_info.dob']}
              required
              maxDate={new Date()} // Cannot select future dates
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              label="Email"
              name="co_borrower_info.email"
              type="email"
              value={values.co_borrower_info?.email || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched['co_borrower_info.email'] && Boolean(errors['co_borrower_info.email'])}
              helperText={touched['co_borrower_info.email'] && errors['co_borrower_info.email']}
              fullWidth
              required
              inputProps={{ 
                'aria-label': 'Co-borrower Email',
                'data-testid': 'co-borrower-email'
              }}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <PhoneField
              name="co_borrower_info.phone"
              value={values.co_borrower_info?.phone || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched['co_borrower_info.phone'] && Boolean(errors['co_borrower_info.phone'])}
              helperText={touched['co_borrower_info.phone'] && errors['co_borrower_info.phone']}
              required
              label="Phone Number"
              placeholder="(XXX) XXX-XXXX"
            />
          </Grid>
          <Grid item xs={12}>
            <FormControl 
              component="fieldset" 
              fullWidth 
              required 
              error={touched['co_borrower_info.citizenship_status'] && Boolean(errors['co_borrower_info.citizenship_status'])}
            >
              <FormLabel component="legend">Citizenship Status</FormLabel>
              <RadioGroup
                aria-label="citizenship-status"
                name="co_borrower_info.citizenship_status"
                value={values.co_borrower_info?.citizenship_status || ''}
                onChange={handleChange}
                onBlur={handleBlur}
                className={classes.radioGroup}
                data-testid="co-borrower-citizenship-status"
              >
                <FormControlLabel value={CitizenshipStatus.US_CITIZEN} control={<Radio />} label="US Citizen" />
                <FormControlLabel value={CitizenshipStatus.PERMANENT_RESIDENT} control={<Radio />} label="Permanent Resident" />
                <FormControlLabel value={CitizenshipStatus.ELIGIBLE_NON_CITIZEN} control={<Radio />} label="Eligible Non-Citizen" />
                <FormControlLabel value={CitizenshipStatus.NON_ELIGIBLE} control={<Radio />} label="Non-Eligible" />
              </RadioGroup>
              {touched['co_borrower_info.citizenship_status'] && errors['co_borrower_info.citizenship_status'] && (
                <FormHelperText error>{errors['co_borrower_info.citizenship_status']}</FormHelperText>
              )}
            </FormControl>
          </Grid>
        </Grid>
      </Grid>

      {/* Address Information Section */}
      <Grid item xs={12}>
        <Typography variant="h6" className={classes.sectionTitle}>
          Address Information
        </Typography>
        <FormControlLabel
          control={
            <Checkbox
              checked={values.co_borrower_info?.same_address || false}
              onChange={handleSameAddressChange}
              name="co_borrower_info.same_address"
              color="primary"
              data-testid="co-borrower-same-address"
              aria-label="Same address as borrower"
            />
          }
          label="Same Address as Borrower"
        />
        
        {/* Render address fields only if same_address is false */}
        {!values.co_borrower_info?.same_address && (
          <AddressFields
            values={values}
            errors={errors}
            touched={touched}
            handleChange={handleChange}
            handleBlur={handleBlur}
            prefix="co_borrower_info."
            required
          />
        )}
      </Grid>

      {/* Employment Information Section */}
      <Grid item xs={12}>
        <Typography variant="h6" className={classes.sectionTitle}>
          Employment Information
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <FormControl 
              fullWidth 
              required
              error={touched['co_borrower_info.employment_type'] && Boolean(errors['co_borrower_info.employment_type'])}
            >
              <FormLabel>Employment Type</FormLabel>
              <Select
                name="co_borrower_info.employment_type"
                value={values.co_borrower_info?.employment_type || ''}
                onChange={handleChange}
                onBlur={handleBlur}
                inputProps={{ 
                  'aria-label': 'Co-borrower Employment Type',
                  'data-testid': 'co-borrower-employment-type'
                }}
              >
                <MenuItem value={EmploymentType.FULL_TIME}>Full Time</MenuItem>
                <MenuItem value={EmploymentType.PART_TIME}>Part Time</MenuItem>
                <MenuItem value={EmploymentType.SELF_EMPLOYED}>Self Employed</MenuItem>
                <MenuItem value={EmploymentType.UNEMPLOYED}>Unemployed</MenuItem>
                <MenuItem value={EmploymentType.RETIRED}>Retired</MenuItem>
                <MenuItem value={EmploymentType.STUDENT}>Student</MenuItem>
                <MenuItem value={EmploymentType.OTHER}>Other</MenuItem>
              </Select>
              {touched['co_borrower_info.employment_type'] && errors['co_borrower_info.employment_type'] && (
                <FormHelperText error>{errors['co_borrower_info.employment_type']}</FormHelperText>
              )}
            </FormControl>
          </Grid>
          
          {/* Only show employment fields if not unemployed or student */}
          {values.co_borrower_info?.employment_type && 
           values.co_borrower_info?.employment_type !== EmploymentType.UNEMPLOYED && 
           values.co_borrower_info?.employment_type !== EmploymentType.STUDENT && (
            <>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Employer Name"
                  name="co_borrower_info.employer_name"
                  value={values.co_borrower_info?.employer_name || ''}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={touched['co_borrower_info.employer_name'] && Boolean(errors['co_borrower_info.employer_name'])}
                  helperText={touched['co_borrower_info.employer_name'] && errors['co_borrower_info.employer_name']}
                  fullWidth
                  required
                  inputProps={{ 
                    'aria-label': 'Co-borrower Employer Name',
                    'data-testid': 'co-borrower-employer-name'
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Occupation"
                  name="co_borrower_info.occupation"
                  value={values.co_borrower_info?.occupation || ''}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={touched['co_borrower_info.occupation'] && Boolean(errors['co_borrower_info.occupation'])}
                  helperText={touched['co_borrower_info.occupation'] && errors['co_borrower_info.occupation']}
                  fullWidth
                  required
                  inputProps={{ 
                    'aria-label': 'Co-borrower Occupation',
                    'data-testid': 'co-borrower-occupation'
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <PhoneField
                  name="co_borrower_info.employer_phone"
                  label="Employer Phone"
                  value={values.co_borrower_info?.employer_phone || ''}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={touched['co_borrower_info.employer_phone'] && Boolean(errors['co_borrower_info.employer_phone'])}
                  helperText={touched['co_borrower_info.employer_phone'] && errors['co_borrower_info.employer_phone']}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={3}>
                <TextField
                  label="Years Employed"
                  name="co_borrower_info.years_employed"
                  type="number"
                  value={values.co_borrower_info?.years_employed || ''}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={touched['co_borrower_info.years_employed'] && Boolean(errors['co_borrower_info.years_employed'])}
                  helperText={touched['co_borrower_info.years_employed'] && errors['co_borrower_info.years_employed']}
                  fullWidth
                  required
                  inputProps={{ 
                    min: 0, 
                    step: 1,
                    'aria-label': 'Co-borrower Years Employed',
                    'data-testid': 'co-borrower-years-employed'
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={3}>
                <TextField
                  label="Months Employed"
                  name="co_borrower_info.months_employed"
                  type="number"
                  value={values.co_borrower_info?.months_employed || ''}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={touched['co_borrower_info.months_employed'] && Boolean(errors['co_borrower_info.months_employed'])}
                  helperText={touched['co_borrower_info.months_employed'] && errors['co_borrower_info.months_employed']}
                  fullWidth
                  required
                  inputProps={{ 
                    min: 0, 
                    max: 11, 
                    step: 1,
                    'aria-label': 'Co-borrower Months Employed',
                    'data-testid': 'co-borrower-months-employed'
                  }}
                />
              </Grid>
            </>
          )}
          
          <Grid item xs={12} sm={6}>
            <TextField
              label="Annual Income"
              name="co_borrower_info.annual_income"
              type="number"
              value={values.co_borrower_info?.annual_income || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched['co_borrower_info.annual_income'] && Boolean(errors['co_borrower_info.annual_income'])}
              helperText={touched['co_borrower_info.annual_income'] && errors['co_borrower_info.annual_income']}
              fullWidth
              required
              InputProps={{
                startAdornment: <InputAdornment position="start">$</InputAdornment>,
              }}
              inputProps={{ 
                min: 0, 
                step: 1,
                'aria-label': 'Co-borrower Annual Income',
                'data-testid': 'co-borrower-annual-income'
              }}
            />
          </Grid>
        </Grid>
      </Grid>
    </Grid>
  );
};

export default CoBorrowerInfoStep;