import React, { useState, useEffect, useCallback } from 'react'; // react v18.2.0
import {
  Grid,
  Typography,
  TextField,
  Button,
  Divider,
  Paper,
  Box,
  Alert,
  Tabs,
  Tab,
} from '@mui/material'; // @mui/material v5.14.0
import { useSnackbar } from 'notistack'; // notistack v3.0.1

import Page from '../../components/common/Page';
import useAuth from '../../hooks/useAuth';
import useForm from '../../hooks/useForm';
import {
  getCurrentUser,
  updateUser,
  changePassword,
} from '../../api/users';
import { PhoneField, AddressFields } from '../../components/FormElements';
import {
  isRequired,
  isEmail,
  isPassword,
  isPhoneNumber,
} from '../../utils/validation';
import LoadingOverlay from '../../components/common/Loading/LoadingOverlay';
import { UserWithProfile, PasswordChangeRequest } from '../../types/user.types';

/**
 * Interface defining props for the TabPanel component
 */
interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

/**
 * Helper component to render tab content
 * @param props - Props containing children, value, and index
 * @returns JSX.Element | null - Rendered tab panel or null if not active
 */
function TabPanel(props: TabPanelProps): JSX.Element | null {
  const { children, value, index, ...other } = props;

  // Return null if value doesn't match index
  if (value !== index) {
    return null;
  }

  // Render div with role='tabpanel' and appropriate ARIA attributes
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          <Typography>{children}</Typography>
        </Box>
      )}
    </div>
  );
}

/**
 * Main component for the profile settings page
 * @returns JSX.Element - Rendered profile settings page
 */
const ProfileSettings: React.FC = () => {
  // Initialize state for user profile data
  const [user, setUser] = useState<UserWithProfile | null>(null);

  // Initialize state for active tab
  const [activeTab, setActiveTab] = useState(0);

  // Initialize state for loading indicators
  const [loading, setLoading] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);

  // Get current user authentication state using useAuth hook
  const { state } = useAuth();

  // Initialize notification snackbar
  const { enqueueSnackbar } = useSnackbar();

  // Initialize form for personal information using useForm hook
  const {
    values: profileValues,
    errors: profileErrors,
    touched: profileTouched,
    handleChange: handleProfileChange,
    handleBlur: handleProfileBlur,
    handleSubmit: handleProfileSubmit,
    isSubmitting: isProfileSubmitting,
  } = useForm(
    {
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
    },
    {
      firstName: { validate: isRequired, errorMessage: 'First name is required' },
      lastName: { validate: isRequired, errorMessage: 'Last name is required' },
      email: { validate: isEmail, errorMessage: 'Valid email is required' },
      phone: { validate: isPhoneNumber, errorMessage: 'Valid phone number is required' },
    },
    async (values) => {
      setLoading(true);
      try {
        if (!state.user) return;
        const response = await updateUser(state.user.id, {
          firstName: values.firstName,
          lastName: values.lastName,
          phone: values.phone,
        });
        if (response.success && response.data) {
          setUser(response.data);
          enqueueSnackbar('Profile updated successfully', { variant: 'success' });
        } else {
          enqueueSnackbar(response.message || 'Failed to update profile', { variant: 'error' });
        }
      } finally {
        setLoading(false);
      }
    }
  );

  // Initialize form for password change using useForm hook
  const {
    values: passwordValues,
    errors: passwordErrors,
    touched: passwordTouched,
    handleChange: handlePasswordChange,
    handleBlur: handlePasswordBlur,
    handleSubmit: handlePasswordSubmit,
    isSubmitting: isPasswordSubmitting,
  } = useForm(
    {
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    },
    {
      currentPassword: { validate: isRequired, errorMessage: 'Current password is required' },
      newPassword: { validate: isPassword, errorMessage: 'Password must be at least 12 characters and include uppercase, lowercase, number, and special character' },
      confirmPassword: {
        validate: (value, allValues) => value === allValues.newPassword,
        errorMessage: 'Passwords must match',
      },
    },
    async (values) => {
      setPasswordLoading(true);
      try {
        const response = await changePassword(
          values.currentPassword,
          values.newPassword
        );
        if (response.success) {
          enqueueSnackbar('Password changed successfully', { variant: 'success' });
        } else {
          enqueueSnackbar(response.message || 'Failed to change password', { variant: 'error' });
        }
      } finally {
        setPasswordLoading(false);
      }
    }
  );

  // Fetch current user profile data on component mount
  useEffect(() => {
    const fetchUser = async () => {
      setLoading(true);
      try {
        const response = await getCurrentUser();
        if (response.success && response.data) {
          setUser(response.data);
          profileValues.firstName = response.data.firstName;
          profileValues.lastName = response.data.lastName;
          profileValues.email = response.data.email;
          profileValues.phone = response.data.phone;
        } else {
          enqueueSnackbar(response.message || 'Failed to load profile', { variant: 'error' });
        }
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [enqueueSnackbar, profileValues.email, profileValues.firstName, profileValues.lastName, profileValues.phone]);

  // Handle tab change function
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Handle personal information form submission
  const handleProfileFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await handleProfileSubmit(e);
  };

  // Handle password change form submission
  const handlePasswordFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await handlePasswordSubmit(e);
  };

  // Render page with tabs for Personal Information and Security
  return (
    <Page title="Profile Settings">
      <LoadingOverlay isLoading={loading || passwordLoading} />
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={activeTab} onChange={handleTabChange} aria-label="profile settings tabs">
          <Tab label="Personal Information" id="simple-tab-0" aria-controls="simple-tabpanel-0" />
          <Tab label="Security" id="simple-tab-1" aria-controls="simple-tabpanel-1" />
        </Tabs>
      </Box>

      {/* Render personal information form with fields for name, email, phone */}
      <TabPanel value={activeTab} index={0}>
        <form onSubmit={handleProfileFormSubmit}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="First Name"
                name="firstName"
                value={profileValues.firstName || ''}
                onChange={handleProfileChange}
                onBlur={handleProfileBlur}
                error={profileTouched.firstName && !!profileErrors.firstName}
                helperText={profileTouched.firstName && profileErrors.firstName}
                inputProps={{
                  'aria-label': 'First Name',
                  'data-testid': 'firstName-input'
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Last Name"
                name="lastName"
                value={profileValues.lastName || ''}
                onChange={handleProfileChange}
                onBlur={handleProfileBlur}
                error={profileTouched.lastName && !!profileErrors.lastName}
                helperText={profileTouched.lastName && profileErrors.lastName}
                inputProps={{
                  'aria-label': 'Last Name',
                  'data-testid': 'lastName-input'
                }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Email"
                name="email"
                value={profileValues.email || ''}
                onChange={handleProfileChange}
                onBlur={handleProfileBlur}
                error={profileTouched.email && !!profileErrors.email}
                helperText={profileTouched.email && profileErrors.email}
                inputProps={{
                  'aria-label': 'Email',
                  'data-testid': 'email-input'
                }}
              />
            </Grid>
            <Grid item xs={12}>
              <PhoneField
                name="phone"
                value={profileValues.phone || ''}
                onChange={handleProfileChange}
                onBlur={handleProfileBlur}
                error={profileTouched.phone && !!profileErrors.phone}
                helperText={profileTouched.phone && profileErrors.phone}
              />
            </Grid>
          </Grid>
          {/* Render address fields for borrower profiles */}
          {user?.userType === 'borrower' && user.profile && (
            <AddressFields
              values={profileValues}
              errors={profileErrors}
              touched={profileTouched}
              handleChange={handleProfileChange}
              handleBlur={handleProfileBlur}
              prefix=""
            />
          )}
          <Button type="submit" variant="contained" disabled={isProfileSubmitting}>
            Update Profile
          </Button>
        </form>
      </TabPanel>

      {/* Render password change form with current password, new password, and confirm password fields */}
      <TabPanel value={activeTab} index={1}>
        <form onSubmit={handlePasswordFormSubmit}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Current Password"
                type="password"
                name="currentPassword"
                value={passwordValues.currentPassword || ''}
                onChange={handlePasswordChange}
                onBlur={handlePasswordBlur}
                error={passwordTouched.currentPassword && !!passwordErrors.currentPassword}
                helperText={passwordTouched.currentPassword && passwordErrors.currentPassword}
                inputProps={{
                  'aria-label': 'Current Password',
                  'data-testid': 'currentPassword-input'
                }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="New Password"
                type="password"
                name="newPassword"
                value={passwordValues.newPassword || ''}
                onChange={handlePasswordChange}
                onBlur={handlePasswordBlur}
                error={passwordTouched.newPassword && !!passwordErrors.newPassword}
                helperText={passwordTouched.newPassword && passwordErrors.newPassword}
                inputProps={{
                  'aria-label': 'New Password',
                  'data-testid': 'newPassword-input'
                }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Confirm New Password"
                type="password"
                name="confirmPassword"
                value={passwordValues.confirmPassword || ''}
                onChange={handlePasswordChange}
                onBlur={handlePasswordBlur}
                error={passwordTouched.confirmPassword && !!passwordErrors.confirmPassword}
                helperText={passwordTouched.confirmPassword && passwordErrors.confirmPassword}
                inputProps={{
                  'aria-label': 'Confirm New Password',
                  'data-testid': 'confirmPassword-input'
                }}
              />
            </Grid>
          </Grid>
          <Button type="submit" variant="contained" disabled={isPasswordSubmitting}>
            Change Password
          </Button>
        </form>
      </TabPanel>
    </Page>
  );
};

export default ProfileSettings;