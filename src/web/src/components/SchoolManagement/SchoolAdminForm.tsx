import React, { useState, useEffect } from 'react';
import { 
  Grid, 
  TextField, 
  Button, 
  FormControl, 
  FormControlLabel, 
  Switch, 
  Typography, 
  Divider 
} from '@mui/material';
import { useDispatch } from 'react-redux';

// Import custom hooks and components
import useStyles from './styles';
import useForm from '../../hooks/useForm';
import CustomCard from '../common/Card/Card';

// Import types
import { 
  SchoolContact, 
  SchoolContactCreateRequest, 
  SchoolContactUpdateRequest 
} from '../../types/school.types';

// Import validation functions
import { 
  isRequired, 
  isEmail, 
  isPhoneNumber, 
  isMaxLength 
} from '../../utils/validation';

// Import actions
import { 
  createSchoolContact, 
  updateSchoolContact 
} from '../../store/actions/schoolActions';

/**
 * Props interface for the SchoolAdminForm component
 */
interface SchoolAdminFormProps {
  contact: SchoolContact | null;
  schoolId: string;
  onSubmitSuccess: (contact: SchoolContact) => void;
  onCancel: () => void;
}

/**
 * Form component for creating and editing school administrators
 * 
 * Provides form fields for entering all school administrator information including
 * personal details and permissions. Handles validation and submission of the form
 * to either create a new school contact or update an existing one.
 */
const SchoolAdminForm: React.FC<SchoolAdminFormProps> = ({
  contact,
  schoolId,
  onSubmitSuccess,
  onCancel
}) => {
  // Initialize styles and dispatch
  const classes = useStyles();
  const dispatch = useDispatch();

  // Define initial form values based on provided contact or defaults for new contact
  const initialValues = {
    first_name: contact?.first_name || '',
    last_name: contact?.last_name || '',
    title: contact?.title || '',
    email: contact?.email || '',
    phone: contact?.phone || '',
    is_primary: contact?.is_primary || false,
    can_sign_documents: contact?.can_sign_documents || false
  };

  // Define validation schema for form fields
  const validationSchema = {
    first_name: {
      validate: isRequired,
      errorMessage: 'First name is required'
    },
    last_name: {
      validate: isRequired,
      errorMessage: 'Last name is required'
    },
    title: {
      validate: isRequired,
      errorMessage: 'Title is required'
    },
    email: {
      validate: (value: string) => isRequired(value) && isEmail(value),
      errorMessage: 'Valid email address is required'
    },
    phone: {
      validate: (value: string) => isRequired(value) && isPhoneNumber(value),
      errorMessage: 'Valid phone number is required in format (XXX) XXX-XXXX'
    }
  };

  // Initialize form state using useForm hook with initial values and validation rules
  const form = useForm(initialValues, validationSchema, handleSubmit);

  /**
   * Form submission handler that creates or updates a school contact
   * 
   * @param values - Form field values
   */
  async function handleSubmit(values: typeof initialValues) {
    try {
      if (contact) {
        // Update existing contact
        const updateData: SchoolContactUpdateRequest = {
          first_name: values.first_name,
          last_name: values.last_name,
          title: values.title,
          email: values.email,
          phone: values.phone,
          is_primary: values.is_primary,
          can_sign_documents: values.can_sign_documents
        };

        const updatedContact = await dispatch(updateSchoolContact(contact.id, updateData));
        onSubmitSuccess(updatedContact);
      } else {
        // Create new contact
        const createData: SchoolContactCreateRequest = {
          school_id: schoolId,
          first_name: values.first_name,
          last_name: values.last_name,
          title: values.title,
          email: values.email,
          phone: values.phone,
          is_primary: values.is_primary,
          can_sign_documents: values.can_sign_documents
        };

        const newContact = await dispatch(createSchoolContact(createData));
        onSubmitSuccess(newContact);
      }
    } catch (error) {
      console.error('Error submitting school admin form:', error);
      // Form errors will be handled by the useForm hook
    }
  }

  return (
    <CustomCard>
      <form onSubmit={form.handleSubmit}>
        <Typography variant="h6" className={classes.sectionTitle}>
          {contact ? 'Edit Administrator' : 'Add New Administrator'}
        </Typography>
        
        <div className={classes.formSection}>
          {/* Personal Information Section */}
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                name="first_name"
                label="First Name"
                value={form.values.first_name}
                onChange={form.handleChange}
                onBlur={form.handleBlur}
                error={!!form.touched.first_name && !!form.errors.first_name}
                helperText={
                  form.touched.first_name && form.errors.first_name
                    ? form.errors.first_name
                    : ''
                }
                fullWidth
                required
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                name="last_name"
                label="Last Name"
                value={form.values.last_name}
                onChange={form.handleChange}
                onBlur={form.handleBlur}
                error={!!form.touched.last_name && !!form.errors.last_name}
                helperText={
                  form.touched.last_name && form.errors.last_name
                    ? form.errors.last_name
                    : ''
                }
                fullWidth
                required
                margin="normal"
              />
            </Grid>
          </Grid>

          {/* Position Information */}
          <TextField
            name="title"
            label="Title"
            value={form.values.title}
            onChange={form.handleChange}
            onBlur={form.handleBlur}
            error={!!form.touched.title && !!form.errors.title}
            helperText={
              form.touched.title && form.errors.title
                ? form.errors.title
                : ''
            }
            fullWidth
            required
            margin="normal"
          />

          {/* Contact Information */}
          <TextField
            name="email"
            label="Email"
            type="email"
            value={form.values.email}
            onChange={form.handleChange}
            onBlur={form.handleBlur}
            error={!!form.touched.email && !!form.errors.email}
            helperText={
              form.touched.email && form.errors.email
                ? form.errors.email
                : ''
            }
            fullWidth
            required
            margin="normal"
          />

          <TextField
            name="phone"
            label="Phone"
            value={form.values.phone}
            onChange={form.handleChange}
            onBlur={form.handleBlur}
            error={!!form.touched.phone && !!form.errors.phone}
            helperText={
              form.touched.phone && form.errors.phone
                ? form.errors.phone
                : 'Format: (XXX) XXX-XXXX'
            }
            fullWidth
            required
            margin="normal"
          />

          {/* Admin Permissions */}
          <FormControlLabel
            control={
              <Switch
                name="is_primary"
                checked={form.values.is_primary}
                onChange={form.handleChange}
                color="primary"
              />
            }
            label="Primary Contact"
            className={classes.switchField}
          />

          <FormControlLabel
            control={
              <Switch
                name="can_sign_documents"
                checked={form.values.can_sign_documents}
                onChange={form.handleChange}
                color="primary"
              />
            }
            label="Can Sign Documents"
            className={classes.switchField}
          />
        </div>

        <Divider className={classes.divider} />

        {/* Form Actions */}
        <div className={classes.formActions}>
          <Button 
            onClick={onCancel} 
            variant="outlined"
            disabled={form.isSubmitting}
          >
            Cancel
          </Button>
          <Button 
            type="submit" 
            variant="contained" 
            color="primary"
            disabled={form.isSubmitting || !form.isValid}
          >
            {form.isSubmitting ? 'Saving...' : contact ? 'Save Changes' : 'Add Administrator'}
          </Button>
        </div>
      </form>
    </CustomCard>
  );
};

export default SchoolAdminForm;