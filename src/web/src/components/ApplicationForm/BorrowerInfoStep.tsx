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
} from '@mui/material';
import {
  AddressFields,
  SSNField,
  DateField,
  PhoneField,
  CurrencyField,
} from '../FormElements';
import useStyles from './styles';
import {
  CitizenshipStatus,
  HousingStatus,
} from '../../types/application.types';
import {
  isRequired,
  isEmail,
  isDate,
  isAdult,
} from '../../utils/validation';

/**
 * Props interface for the BorrowerInfoStep component
 */
interface BorrowerInfoStepProps {
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
 * BorrowerInfoStep component - First step of the loan application process
 * Collects borrower personal information including contact details, identification,
 * citizenship status, address information, and housing information
 */
const BorrowerInfoStep: React.FC<BorrowerInfoStepProps> = ({
  values,
  errors,
  touched,
  handleChange,
  handleBlur,
  setFieldValue,
  setFieldTouched,
  isSubmitting,
  isValid,
}) => {
  const classes = useStyles();

  return (
    <>
      {/* Personal Information Section */}
      <div className={classes.formSection}>
        <Typography variant="h6" className={classes.sectionTitle}>
          Personal Information
        </Typography>
        <Grid container spacing={2}>
          {/* First Name */}
          <Grid item xs={12} sm={4}>
            <TextField
              id="first_name"
              name="first_name"
              label="First Name"
              value={values.first_name || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.first_name && Boolean(errors.first_name)}
              helperText={touched.first_name && errors.first_name}
              fullWidth
              required
              disabled={isSubmitting}
              inputProps={{
                'aria-label': 'First Name',
                'data-testid': 'first_name-input',
              }}
            />
          </Grid>

          {/* Middle Name */}
          <Grid item xs={12} sm={4}>
            <TextField
              id="middle_name"
              name="middle_name"
              label="Middle Name"
              value={values.middle_name || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.middle_name && Boolean(errors.middle_name)}
              helperText={touched.middle_name && errors.middle_name}
              fullWidth
              disabled={isSubmitting}
              inputProps={{
                'aria-label': 'Middle Name',
                'data-testid': 'middle_name-input',
              }}
            />
          </Grid>

          {/* Last Name */}
          <Grid item xs={12} sm={4}>
            <TextField
              id="last_name"
              name="last_name"
              label="Last Name"
              value={values.last_name || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.last_name && Boolean(errors.last_name)}
              helperText={touched.last_name && errors.last_name}
              fullWidth
              required
              disabled={isSubmitting}
              inputProps={{
                'aria-label': 'Last Name',
                'data-testid': 'last_name-input',
              }}
            />
          </Grid>

          {/* SSN */}
          <Grid item xs={12} sm={6}>
            <SSNField
              name="ssn"
              value={values.ssn || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.ssn && Boolean(errors.ssn)}
              helperText={touched.ssn && errors.ssn}
              required
              disabled={isSubmitting}
            />
          </Grid>

          {/* Date of Birth */}
          <Grid item xs={12} sm={6}>
            <DateField
              name="dob"
              value={values.dob || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.dob && Boolean(errors.dob)}
              helperText={touched.dob && errors.dob}
              label="Date of Birth"
              required
              disabled={isSubmitting}
            />
          </Grid>

          {/* Email */}
          <Grid item xs={12} sm={6}>
            <TextField
              id="email"
              name="email"
              label="Email"
              type="email"
              value={values.email || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.email && Boolean(errors.email)}
              helperText={touched.email && errors.email}
              fullWidth
              required
              disabled={isSubmitting}
              inputProps={{
                'aria-label': 'Email',
                'data-testid': 'email-input',
              }}
            />
          </Grid>

          {/* Phone */}
          <Grid item xs={12} sm={6}>
            <PhoneField
              name="phone"
              value={values.phone || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.phone && Boolean(errors.phone)}
              helperText={touched.phone && errors.phone}
              required
              disabled={isSubmitting}
            />
          </Grid>

          {/* Citizenship Status */}
          <Grid item xs={12}>
            <FormControl 
              component="fieldset" 
              error={touched.citizenship_status && Boolean(errors.citizenship_status)}
              className={classes.formControl}
            >
              <FormLabel component="legend" required>Citizenship Status</FormLabel>
              <RadioGroup
                aria-label="citizenship status"
                name="citizenship_status"
                value={values.citizenship_status || ''}
                onChange={handleChange}
                onBlur={handleBlur}
                className={classes.radioGroup}
              >
                <FormControlLabel
                  value={CitizenshipStatus.US_CITIZEN}
                  control={<Radio />}
                  label="US Citizen"
                  disabled={isSubmitting}
                />
                <FormControlLabel
                  value={CitizenshipStatus.PERMANENT_RESIDENT}
                  control={<Radio />}
                  label="Permanent Resident"
                  disabled={isSubmitting}
                />
                <FormControlLabel
                  value={CitizenshipStatus.ELIGIBLE_NON_CITIZEN}
                  control={<Radio />}
                  label="Eligible Non-Citizen"
                  disabled={isSubmitting}
                />
                <FormControlLabel
                  value={CitizenshipStatus.NON_ELIGIBLE}
                  control={<Radio />}
                  label="Non-Eligible"
                  disabled={isSubmitting}
                />
              </RadioGroup>
              {touched.citizenship_status && errors.citizenship_status && (
                <FormHelperText>{errors.citizenship_status}</FormHelperText>
              )}
            </FormControl>
          </Grid>
        </Grid>
      </div>

      {/* Address Information Section */}
      <div className={classes.formSection}>
        <Typography variant="h6" className={classes.sectionTitle}>
          Address Information
        </Typography>
        <AddressFields
          values={values}
          errors={errors}
          touched={touched}
          handleChange={handleChange}
          handleBlur={handleBlur}
          prefix=""
          required={true}
          disabled={isSubmitting}
        />
      </div>

      {/* Housing Information Section */}
      <div className={classes.formSection}>
        <Typography variant="h6" className={classes.sectionTitle}>
          Housing Information
        </Typography>
        <Grid container spacing={2}>
          {/* Housing Status */}
          <Grid item xs={12}>
            <FormControl 
              component="fieldset" 
              error={touched.housing_status && Boolean(errors.housing_status)}
              className={classes.formControl}
            >
              <FormLabel component="legend" required>Housing Status</FormLabel>
              <RadioGroup
                aria-label="housing status"
                name="housing_status"
                value={values.housing_status || ''}
                onChange={handleChange}
                onBlur={handleBlur}
                className={classes.radioGroup}
              >
                <FormControlLabel
                  value={HousingStatus.OWN}
                  control={<Radio />}
                  label="Own"
                  disabled={isSubmitting}
                />
                <FormControlLabel
                  value={HousingStatus.RENT}
                  control={<Radio />}
                  label="Rent"
                  disabled={isSubmitting}
                />
                <FormControlLabel
                  value={HousingStatus.LIVE_WITH_FAMILY}
                  control={<Radio />}
                  label="Live with Family"
                  disabled={isSubmitting}
                />
                <FormControlLabel
                  value={HousingStatus.CAMPUS_HOUSING}
                  control={<Radio />}
                  label="Campus Housing"
                  disabled={isSubmitting}
                />
                <FormControlLabel
                  value={HousingStatus.OTHER}
                  control={<Radio />}
                  label="Other"
                  disabled={isSubmitting}
                />
              </RadioGroup>
              {touched.housing_status && errors.housing_status && (
                <FormHelperText>{errors.housing_status}</FormHelperText>
              )}
            </FormControl>
          </Grid>

          {/* Housing Payment (only for Own or Rent) */}
          {(values.housing_status === HousingStatus.OWN || values.housing_status === HousingStatus.RENT) && (
            <Grid item xs={12} sm={6}>
              <CurrencyField
                label="Monthly Housing Payment"
                value={values.housing_payment || null}
                onChange={(value) => setFieldValue('housing_payment', value)}
                error={touched.housing_payment && Boolean(errors.housing_payment)}
                helperText={touched.housing_payment && errors.housing_payment}
                fullWidth
                required
                disabled={isSubmitting}
                onBlur={() => setFieldTouched('housing_payment', true)}
              />
            </Grid>
          )}
        </Grid>
      </div>
    </>
  );
};

export default BorrowerInfoStep;