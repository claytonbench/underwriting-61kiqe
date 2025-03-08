import React from 'react';
import {
  Grid,
  Typography,
  TextField,
  MenuItem,
  FormControl,
  FormHelperText,
  InputLabel,
  Select
} from '@mui/material'; // v5.14.0
import useStyles from './styles';
import { CurrencyField, PhoneField } from '../FormElements';
import { EmploymentType } from '../../types/application.types';

/**
 * Props interface for the EmploymentInfoStep component
 */
interface EmploymentInfoStepProps {
  values: Record<string, any>;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  handleChange: (e: React.ChangeEvent<any>) => void;
  handleBlur: (e: React.FocusEvent<any>) => void;
  setFieldValue: (field: string, value: any, shouldValidate?: boolean) => void;
}

/**
 * Component for collecting employment and income information in the loan application
 * 
 * This component renders the employment information step in the multi-step loan
 * application process, collecting employment details, income information, and other
 * financial data from the borrower.
 */
const EmploymentInfoStep: React.FC<EmploymentInfoStepProps> = ({
  values,
  errors,
  touched,
  handleChange,
  handleBlur,
  setFieldValue
}) => {
  const classes = useStyles();

  return (
    <>
      {/* Employment Information Section */}
      <Typography variant="h6" className={classes.formTitle}>
        Employment Information
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <FormControl 
            fullWidth 
            error={!!errors.employment_info?.employment_type && touched.employment_info?.employment_type}
          >
            <InputLabel>Employment Type</InputLabel>
            <Select
              name="employment_info.employment_type"
              value={values.employment_info?.employment_type || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              label="Employment Type"
              required
            >
              <MenuItem value={EmploymentType.FULL_TIME}>Full Time</MenuItem>
              <MenuItem value={EmploymentType.PART_TIME}>Part Time</MenuItem>
              <MenuItem value={EmploymentType.SELF_EMPLOYED}>Self Employed</MenuItem>
              <MenuItem value={EmploymentType.UNEMPLOYED}>Unemployed</MenuItem>
              <MenuItem value={EmploymentType.RETIRED}>Retired</MenuItem>
              <MenuItem value={EmploymentType.STUDENT}>Student</MenuItem>
              <MenuItem value={EmploymentType.OTHER}>Other</MenuItem>
            </Select>
            <FormHelperText>{errors.employment_info?.employment_type}</FormHelperText>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Employer Name"
            name="employment_info.employer_name"
            value={values.employment_info?.employer_name || ''}
            onChange={handleChange}
            onBlur={handleBlur}
            error={!!errors.employment_info?.employer_name && touched.employment_info?.employer_name}
            helperText={errors.employment_info?.employer_name}
            required
            disabled={values.employment_info?.employment_type === EmploymentType.UNEMPLOYED || 
                     values.employment_info?.employment_type === EmploymentType.RETIRED || 
                     values.employment_info?.employment_type === EmploymentType.STUDENT}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Occupation"
            name="employment_info.occupation"
            value={values.employment_info?.occupation || ''}
            onChange={handleChange}
            onBlur={handleBlur}
            error={!!errors.employment_info?.occupation && touched.employment_info?.occupation}
            helperText={errors.employment_info?.occupation}
            required
            disabled={values.employment_info?.employment_type === EmploymentType.UNEMPLOYED || 
                     values.employment_info?.employment_type === EmploymentType.RETIRED || 
                     values.employment_info?.employment_type === EmploymentType.STUDENT}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <PhoneField
            fullWidth
            label="Employer Phone"
            name="employment_info.employer_phone"
            value={values.employment_info?.employer_phone || ''}
            onChange={handleChange}
            onBlur={handleBlur}
            error={!!errors.employment_info?.employer_phone && touched.employment_info?.employer_phone}
            helperText={errors.employment_info?.employer_phone}
            required
            disabled={values.employment_info?.employment_type === EmploymentType.UNEMPLOYED || 
                     values.employment_info?.employment_type === EmploymentType.RETIRED || 
                     values.employment_info?.employment_type === EmploymentType.STUDENT}
          />
        </Grid>
        
        <Grid item xs={6} md={3}>
          <TextField
            fullWidth
            label="Years Employed"
            name="employment_info.years_employed"
            type="number"
            value={values.employment_info?.years_employed || 0}
            onChange={handleChange}
            onBlur={handleBlur}
            error={!!errors.employment_info?.years_employed && touched.employment_info?.years_employed}
            helperText={errors.employment_info?.years_employed}
            inputProps={{ min: 0, max: 99 }}
            disabled={values.employment_info?.employment_type === EmploymentType.UNEMPLOYED || 
                     values.employment_info?.employment_type === EmploymentType.RETIRED || 
                     values.employment_info?.employment_type === EmploymentType.STUDENT}
          />
        </Grid>
        
        <Grid item xs={6} md={3}>
          <TextField
            fullWidth
            label="Months Employed"
            name="employment_info.months_employed"
            type="number"
            value={values.employment_info?.months_employed || 0}
            onChange={handleChange}
            onBlur={handleBlur}
            error={!!errors.employment_info?.months_employed && touched.employment_info?.months_employed}
            helperText={errors.employment_info?.months_employed}
            inputProps={{ min: 0, max: 11 }}
            disabled={values.employment_info?.employment_type === EmploymentType.UNEMPLOYED || 
                     values.employment_info?.employment_type === EmploymentType.RETIRED || 
                     values.employment_info?.employment_type === EmploymentType.STUDENT}
          />
        </Grid>
      </Grid>
      
      {/* Income Information Section */}
      <Typography variant="h6" className={classes.formTitle} sx={{ mt: 4 }}>
        Income Information
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <CurrencyField
            fullWidth
            label="Annual Income"
            value={values.employment_info?.annual_income || null}
            onChange={(value) => setFieldValue('employment_info.annual_income', value)}
            error={!!errors.employment_info?.annual_income && touched.employment_info?.annual_income}
            helperText={errors.employment_info?.annual_income}
            required
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <CurrencyField
            fullWidth
            label="Other Income (Optional)"
            value={values.employment_info?.other_income || null}
            onChange={(value) => setFieldValue('employment_info.other_income', value)}
            error={!!errors.employment_info?.other_income && touched.employment_info?.other_income}
            helperText={errors.employment_info?.other_income}
          />
        </Grid>
        
        <Grid 
          item 
          xs={12} 
          md={6} 
          sx={{ display: values.employment_info?.other_income > 0 ? 'block' : 'none' }}
        >
          <TextField
            fullWidth
            label="Other Income Source"
            name="employment_info.other_income_source"
            value={values.employment_info?.other_income_source || ''}
            onChange={handleChange}
            onBlur={handleBlur}
            error={!!errors.employment_info?.other_income_source && touched.employment_info?.other_income_source}
            helperText={errors.employment_info?.other_income_source}
            required={values.employment_info?.other_income > 0}
          />
        </Grid>
      </Grid>
    </>
  );
};

export default EmploymentInfoStep;