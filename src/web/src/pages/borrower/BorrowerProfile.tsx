import React, { useState, useEffect } from 'react'; // React library for building user interfaces v18.2.0
import {
  Grid,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Divider,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Alert,
  Snackbar,
  CircularProgress,
} from '@mui/material'; // Material-UI components for UI design v5.14.0
import DashboardLayout from '../../layouts/DashboardLayout'; // Layout component for authenticated user pages
import Page from '../../components/common/Page'; // Page container component for consistent layout
import useForm from '../../hooks/useForm'; // Custom hook for form state management and validation
import useAuth from '../../hooks/useAuth'; // Hook to access authentication context and user information
import { getCurrentUser, updateUser } from '../../api/users'; // API functions for fetching and updating user data
import {
  AddressFields,
  ContactFields,
  DateField,
  SSNField,
} from '../../components/FormElements'; // Form input components for profile information
import {
  UserWithProfile,
  BorrowerProfile as BorrowerProfileType,
  EmploymentInfo,
} from '../../types/user.types'; // Type definitions for user and profile data

/**
 * @interface ProfileFormValues
 * @description Interface for the profile form values
 */
interface ProfileFormValues {
  firstName: string; // Borrower's first name
  lastName: string; // Borrower's last name
  email: string; // Borrower's email address
  phone: string; // Borrower's phone number
  ssn: string; // Borrower's social security number (masked)
  dob: string; // Borrower's date of birth
  citizenshipStatus: string; // Borrower's citizenship status
  addressLine1: string; // First line of borrower's address
  addressLine2: string; // Second line of borrower's address (optional)
  city: string; // City of borrower's address
  state: string; // State of borrower's address
  zipCode: string; // ZIP code of borrower's address
  housingStatus: string; // Borrower's housing status (own/rent)
  housingPayment: number; // Borrower's monthly housing payment
  employmentType: string; // Borrower's employment type
  employerName: string; // Name of borrower's employer
  occupation: string; // Borrower's job title/occupation
  employerPhone: string; // Phone number of borrower's employer
  yearsEmployed: number; // Years at current employer
  monthsEmployed: number; // Additional months at current employer
  annualIncome: number; // Borrower's annual income
  otherIncome: number; // Borrower's income from other sources
  otherIncomeSource: string; // Source of borrower's other income
}

/**
 * @function BorrowerProfile
 * @description Component for displaying and editing borrower profile information
 * @returns {JSX.Element} Rendered borrower profile page
 */
const BorrowerProfile: React.FC = () => {
  // Initialize state for user profile data
  const [user, setUser] = useState<UserWithProfile | null>(null);

  // Initialize state for loading status
  const [loading, setLoading] = useState<boolean>(true);

  // Initialize state for submitting status
  const [submitting, setSubmitting] = useState<boolean>(false);

  // Initialize state for success/error notifications
  const [success, setSuccess] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Get authentication context using useAuth hook
  const { state } = useAuth();

  // Set up useEffect to fetch user profile data on component mount
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        const response = await getCurrentUser();
        if (response.success && response.data) {
          setUser(response.data);
        } else {
          setError(response.message || 'Failed to load profile');
        }
      } catch (e: any) {
        setError(e.message || 'Failed to load profile');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  // Set up form validation schema for profile fields
  const validationSchema = {
    firstName: {
      validate: (value: string) => value && value.length > 0,
      errorMessage: 'Required field',
    },
    lastName: {
      validate: (value: string) => value && value.length > 0,
      errorMessage: 'Required field',
    },
    email: {
      validate: (value: string) => value && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
      errorMessage: 'Valid email format required',
    },
    phone: {
      validate: (value: string) => value && /^\(\d{3}\) \d{3}-\d{4}$/.test(value),
      errorMessage: 'Valid phone number format required',
    },
    addressLine1: {
      validate: (value: string) => value && value.length > 0,
      errorMessage: 'Required field',
    },
    city: {
      validate: (value: string) => value && value.length > 0,
      errorMessage: 'Required field',
    },
    state: {
      validate: (value: string) => value && value.length > 0,
      errorMessage: 'Required field',
    },
    zipCode: {
      validate: (value: string) => value && /^\d{5}(-\d{4})?$/.test(value),
      errorMessage: 'Valid ZIP code format required',
    },
    housingStatus: {
      validate: (value: string) => value && value.length > 0,
      errorMessage: 'Required field',
    },
    employmentType: {
      validate: (value: string) => value && value.length > 0,
      errorMessage: 'Required field',
    },
    employerName: {
      validate: (value: string, allValues: ProfileFormValues) => {
        return allValues.employmentType !== 'unemployed' ? value && value.length > 0 : true;
      },
      errorMessage: 'Required field if employed',
    },
    occupation: {
      validate: (value: string, allValues: ProfileFormValues) => {
        return allValues.employmentType !== 'unemployed' ? value && value.length > 0 : true;
      },
      errorMessage: 'Required field if employed',
    },
    annualIncome: {
      validate: (value: number) => value > 0,
      errorMessage: 'Must be a positive number',
    },
  };

  // Initialize form state using useForm hook with profile data
  const { values, errors, touched, handleChange, handleBlur, handleSubmit: submitForm, resetForm, isSubmitting } = useForm<ProfileFormValues>(
    {
      firstName: user?.firstName || '',
      lastName: user?.lastName || '',
      email: user?.email || '',
      phone: user?.phone || '',
      ssn: user?.profile?.ssn || '',
      dob: user?.profile?.dob || '',
      citizenshipStatus: user?.profile?.citizenshipStatus || '',
      addressLine1: user?.profile?.address?.address_line1 || '',
      addressLine2: user?.profile?.address?.address_line2 || '',
      city: user?.profile?.address?.city || '',
      state: user?.profile?.address?.state || '',
      zipCode: user?.profile?.address?.zip_code || '',
      housingStatus: user?.profile?.housingStatus || '',
      housingPayment: user?.profile?.housingPayment || 0,
      employmentType: user?.profile?.employmentInfo?.employmentType || '',
      employerName: user?.profile?.employmentInfo?.employerName || '',
      occupation: user?.profile?.employmentInfo?.occupation || '',
      employerPhone: user?.profile?.employmentInfo?.employerPhone || '',
      yearsEmployed: user?.profile?.employmentInfo?.yearsEmployed || 0,
      monthsEmployed: user?.profile?.employmentInfo?.monthsEmployed || 0,
      annualIncome: user?.profile?.employmentInfo?.annualIncome || 0,
      otherIncome: user?.profile?.employmentInfo?.otherIncome || 0,
      otherIncomeSource: user?.profile?.employmentInfo?.otherIncomeSource || '',
    },
    validationSchema,
    async (formValues: ProfileFormValues) => {
      // Implement handleSubmit function to update profile information
      setSubmitting(true);
      try {
        if (!user) {
          throw new Error('User not loaded');
        }

        const profileData = {
          firstName: formValues.firstName,
          lastName: formValues.lastName,
          phone: formValues.phone,
        };

        const response = await updateUser(user.id, profileData);

        if (response.success) {
          setSuccess(true);
          setUser({
            ...user,
            firstName: formValues.firstName,
            lastName: formValues.lastName,
            phone: formValues.phone,
          });
        } else {
          setError(response.message || 'Failed to update profile');
        }
      } catch (e: any) {
        setError(e.message || 'Failed to update profile');
      } finally {
        setSubmitting(false);
      }
    }
  );

  // Implement handleCancel function to reset form
  const handleCancel = () => {
    resetForm();
  };

  // Render page with profile form sections
  return (
    <DashboardLayout>
      <Page title="Borrower Profile">
        {loading ? (
          <CircularProgress />
        ) : (
          <form onSubmit={submitForm}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Personal Information
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="First Name"
                      name="firstName"
                      value={values.firstName}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      error={touched.firstName && !!errors.firstName}
                      helperText={touched.firstName && errors.firstName}
                      fullWidth
                      required
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Last Name"
                      name="lastName"
                      value={values.lastName}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      error={touched.lastName && !!errors.lastName}
                      helperText={touched.lastName && errors.lastName}
                      fullWidth
                      required
                    />
                  </Grid>
                </Grid>
                <ContactFields
                  email={values.email}
                  phone={values.phone}
                  onChange={(field, value) => {
                    handleChange({ target: { name: field, value } } as any);
                  }}
                  onBlur={(field) => handleBlur({ target: { name: field } } as any)}
                  errors={{ email: errors.email, phone: errors.phone }}
                />
                <SSNField
                  name="ssn"
                  label="Social Security Number"
                  value={values.ssn}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={touched.ssn && !!errors.ssn}
                  helperText={touched.ssn && errors.ssn}
                  fullWidth
                  showMask
                />
                <DateField
                  name="dob"
                  label="Date of Birth"
                  value={values.dob}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={touched.dob && !!errors.dob}
                  helperText={touched.dob && errors.dob}
                  fullWidth
                />
                <FormControl fullWidth>
                  <InputLabel id="citizenshipStatus-label">Citizenship Status</InputLabel>
                  <Select
                    labelId="citizenshipStatus-label"
                    id="citizenshipStatus"
                    name="citizenshipStatus"
                    value={values.citizenshipStatus}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    error={touched.citizenshipStatus && !!errors.citizenshipStatus}
                  >
                    <MenuItem value="us_citizen">US Citizen</MenuItem>
                    <MenuItem value="permanent_resident">Permanent Resident</MenuItem>
                    <MenuItem value="eligible_non_citizen">Eligible Non-Citizen</MenuItem>
                  </Select>
                  {touched.citizenshipStatus && errors.citizenshipStatus && (
                    <FormHelperText error>{errors.citizenshipStatus}</FormHelperText>
                  )}
                </FormControl>
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Address Information
                </Typography>
                <AddressFields
                  values={values}
                  errors={errors}
                  touched={touched}
                  handleChange={handleChange}
                  handleBlur={handleBlur}
                  prefix=""
                  required
                />
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Employment Information
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Employment Type"
                      name="employmentType"
                      value={values.employmentType}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      error={touched.employmentType && !!errors.employmentType}
                      helperText={touched.employmentType && errors.employmentType}
                      fullWidth
                      required
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Employer Name"
                      name="employerName"
                      value={values.employerName}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      error={touched.employerName && !!errors.employerName}
                      helperText={touched.employerName && errors.employerName}
                      fullWidth
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Occupation"
                      name="occupation"
                      value={values.occupation}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      error={touched.occupation && !!errors.occupation}
                      helperText={touched.occupation && errors.occupation}
                      fullWidth
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Employer Phone"
                      name="employerPhone"
                      value={values.employerPhone}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      error={touched.employerPhone && !!errors.employerPhone}
                      helperText={touched.employerPhone && errors.employerPhone}
                      fullWidth
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Years Employed"
                      name="yearsEmployed"
                      value={values.yearsEmployed}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      error={touched.yearsEmployed && !!errors.yearsEmployed}
                      helperText={touched.yearsEmployed && errors.yearsEmployed}
                      fullWidth
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Months Employed"
                      name="monthsEmployed"
                      value={values.monthsEmployed}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      error={touched.monthsEmployed && !!errors.monthsEmployed}
                      helperText={touched.monthsEmployed && errors.monthsEmployed}
                      fullWidth
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Annual Income"
                      name="annualIncome"
                      value={values.annualIncome}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      error={touched.annualIncome && !!errors.annualIncome}
                      helperText={touched.annualIncome && errors.annualIncome}
                      fullWidth
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Other Income"
                      name="otherIncome"
                      value={values.otherIncome}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      error={touched.otherIncome && !!errors.otherIncome}
                      helperText={touched.otherIncome && errors.otherIncome}
                      fullWidth
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      label="Other Income Source"
                      name="otherIncomeSource"
                      value={values.otherIncomeSource}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      error={touched.otherIncomeSource && !!errors.otherIncomeSource}
                      helperText={touched.otherIncomeSource && errors.otherIncomeSource}
                      fullWidth
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            <Divider />
            <Box mt={3} display="flex" justifyContent="flex-end">
              <Button onClick={handleCancel} disabled={isSubmitting}>
                Cancel
              </Button>
              <Button
                variant="contained"
                color="primary"
                type="submit"
                disabled={isSubmitting}
              >
                {submitting ? <CircularProgress size={24} /> : 'Update Profile'}
              </Button>
            </Box>
          </form>
        )}

        {/* Render success/error notifications */}
        <Snackbar
          open={success}
          autoHideDuration={6000}
          onClose={() => setSuccess(false)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
        >
          <Alert onClose={() => setSuccess(false)} severity="success">
            Profile updated successfully!
          </Alert>
        </Snackbar>
        <Snackbar
          open={!!error}
          autoHideDuration={6000}
          onClose={() => setError(null)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
        >
          <Alert onClose={() => setError(null)} severity="error">
            {error}
          </Alert>
        </Snackbar>
      </Page>
    </DashboardLayout>
  );
};

export default BorrowerProfile;