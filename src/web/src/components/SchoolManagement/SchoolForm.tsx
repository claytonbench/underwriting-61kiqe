import React, { useState, useEffect } from 'react'; // version: ^18.2.0
import {
  Grid,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Typography,
  Divider,
  Switch,
  FormControlLabel,
} from '@mui/material'; // version: ^5.14.0
import { useDispatch, useSelector } from 'react-redux'; // version: ^8.1.1

import useStyles from './styles';
import useForm, { FormState } from '../../hooks/useForm';
import AddressFields from '../FormElements/AddressFields';
import CustomCard from '../common/Card';
import {
  School,
  SchoolStatus,
  SchoolCreateRequest,
  SchoolUpdateRequest,
} from '../../types/school.types';
import {
  isRequired,
  isEmail,
  isPhoneNumber,
  isValidState,
  isMaxLength,
} from '../../utils/validation';
import { createSchool, updateSchool } from '../../store/actions/schoolActions';

/**
 * Props interface for the SchoolForm component
 */
interface SchoolFormProps {
  /** Existing school data for editing, or null for creating a new school */
  school: School | null;
  /** Callback function to execute on successful form submission */
  onSubmitSuccess: (school: School) => void;
  /** Callback function to execute when the form is cancelled */
  onCancel: () => void;
}

/**
 * Form component for creating and editing schools
 *
 * This component provides a form interface for creating new school entities or
 * editing existing ones. It includes input fields for all school properties,
 * validation, and submission handling.
 *
 * @param {SchoolFormProps} props - The component props
 * @returns {JSX.Element} Rendered form component
 */
const SchoolForm: React.FC<SchoolFormProps> = ({ school, onSubmitSuccess, onCancel }) => {
  // Initialize styles using the useStyles hook
  const classes = useStyles();

  // Set up Redux dispatch and selector hooks
  const dispatch = useDispatch();
  const loading = useSelector((state: any) => state.school.loading);

  // Define initial form values based on provided school prop or default values
  const initialValues = {
    name: school?.name || '',
    legal_name: school?.legal_name || '',
    tax_id: school?.tax_id || '',
    address_line1: school?.address_line1 || '',
    address_line2: school?.address_line2 || '',
    city: school?.city || '',
    state: school?.state || '',
    zip_code: school?.zip_code || '',
    phone: school?.phone || '',
    website: school?.website || '',
    status: school?.status || SchoolStatus.ACTIVE,
  };

  // Define validation schema for all form fields
  const validationSchema = {
    name: {
      validate: isRequired,
      errorMessage: 'School name is required',
    },
    legal_name: {
      validate: isRequired,
      errorMessage: 'Legal name is required',
    },
    tax_id: {
      validate: isRequired,
      errorMessage: 'Tax ID is required',
    },
    address_line1: {
      validate: isRequired,
      errorMessage: 'Street address is required',
    },
    city: {
      validate: isRequired,
      errorMessage: 'City is required',
    },
    state: {
      validate: isValidState,
      errorMessage: 'Valid state is required',
    },
    zip_code: {
      validate: isZipCode,
      errorMessage: 'Valid ZIP code is required',
    },
    phone: {
      validate: isPhoneNumber,
      errorMessage: 'Valid phone number is required',
    },
    website: {
      validate: isEmail,
      errorMessage: 'Valid website URL is required',
    },
  };

  // Initialize form state using useForm hook with initial values, validation schema, and submit handler
  const {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    resetForm,
  } = useForm(initialValues, validationSchema, async (formValues) => {
    // Implement form submission handler that creates or updates a school
    try {
      if (school) {
        // Update existing school
        const updatedSchool = await dispatch(
          updateSchool(school.id, formValues as SchoolUpdateRequest)
        ).unwrap();
        onSubmitSuccess(updatedSchool);
      } else {
        // Create new school
        const newSchool = await dispatch(
          createSchool(formValues as SchoolCreateRequest)
        ).unwrap();
        onSubmitSuccess(newSchool);
      }
      resetForm();
    } catch (error) {
      // Handle errors during form submission
      console.error('Failed to submit school form:', error);
    }
  });

  return (
    <CustomCard title={school ? 'Edit School' : 'Create School'}>
      <form onSubmit={handleSubmit} className={classes.formContainer}>
        {/* Render form sections for school information, address, and status */}
        <Grid container spacing={2}>
          {/* School Information */}
          <Grid item xs={12}>
            <Typography variant="h6" className={classes.sectionTitle}>
              School Information
            </Typography>
            {/* Render TextField components for name, legal name, tax ID, phone, and website */}
            <TextField
              id="name"
              name="name"
              label="School Name"
              value={values.name}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.name && Boolean(errors.name)}
              helperText={touched.name && errors.name}
              fullWidth
              required
              inputProps={{
                'aria-label': 'School Name',
                'data-testid': 'name'
              }}
            />
            <TextField
              id="legal_name"
              name="legal_name"
              label="Legal Name"
              value={values.legal_name}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.legal_name && Boolean(errors.legal_name)}
              helperText={touched.legal_name && errors.legal_name}
              fullWidth
              required
              inputProps={{
                'aria-label': 'Legal Name',
                'data-testid': 'legal_name'
              }}
            />
            <TextField
              id="tax_id"
              name="tax_id"
              label="Tax ID"
              value={values.tax_id}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.tax_id && Boolean(errors.tax_id)}
              helperText={touched.tax_id && errors.tax_id}
              fullWidth
              required
              inputProps={{
                'aria-label': 'Tax ID',
                'data-testid': 'tax_id'
              }}
            />
          </Grid>

          {/* Address Information */}
          <Grid item xs={12}>
            <Typography variant="h6" className={classes.sectionTitle}>
              Address Information
            </Typography>
            {/* Render AddressFields component for address fields */}
            <AddressFields
              values={values}
              errors={errors}
              touched={touched}
              handleChange={handleChange}
              handleBlur={handleBlur}
              prefix=""
              required
            />
          </Grid>

          {/* Contact Information */}
          <Grid item xs={12}>
            <Typography variant="h6" className={classes.sectionTitle}>
              Contact Information
            </Typography>
            <TextField
              id="phone"
              name="phone"
              label="Phone Number"
              value={values.phone}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.phone && Boolean(errors.phone)}
              helperText={touched.phone && errors.phone}
              fullWidth
              required
              inputProps={{
                'aria-label': 'Phone Number',
                'data-testid': 'phone'
              }}
            />
            <TextField
              id="website"
              name="website"
              label="Website URL"
              value={values.website}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.website && Boolean(errors.website)}
              helperText={touched.website && errors.website}
              fullWidth
              inputProps={{
                'aria-label': 'Website URL',
                'data-testid': 'website'
              }}
            />
          </Grid>

          {/* School Status */}
          <Grid item xs={12}>
            <FormControl fullWidth required>
              <InputLabel id="status-label">Status</InputLabel>
              {/* Render FormControl with Select for school status */}
              <Select
                labelId="status-label"
                id="status"
                name="status"
                value={values.status}
                onChange={handleChange}
                onBlur={handleBlur}
                error={touched.status && Boolean(errors.status)}
                inputProps={{
                  'aria-label': 'School Status',
                  'data-testid': 'status'
                }}
              >
                <MenuItem value={SchoolStatus.ACTIVE}>Active</MenuItem>
                <MenuItem value={SchoolStatus.INACTIVE}>Inactive</MenuItem>
              </Select>
              {touched.status && errors.status && (
                <FormHelperText error>{errors.status}</FormHelperText>
              )}
            </FormControl>
          </Grid>
        </Grid>

        {/* Render form action buttons (Cancel and Submit) */}
        <div className={classes.formActions}>
          <Button onClick={onCancel} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button type="submit" variant="contained" disabled={isSubmitting}>
            {isSubmitting ? 'Submitting...' : 'Submit'}
          </Button>
        </div>
      </form>
    </CustomCard>
  );
};

export default SchoolForm;