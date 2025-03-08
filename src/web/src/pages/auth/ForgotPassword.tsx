import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  TextField,
  Button,
  Box,
  Typography,
  Link,
  Alert,
  CircularProgress
} from '@mui/material';

import AuthLayout from '../../layouts/AuthLayout';
import useForm from '../../hooks/useForm';
import { isEmail, isRequired } from '../../utils/validation';
import { requestPasswordReset } from '../../api/auth';
import { PasswordResetRequest } from '../../types/auth.types';
import { ROUTES } from '../../config/routes';

/**
 * Forgot Password page component that allows users to request a password reset
 * by providing their email address.
 */
const ForgotPassword: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Validation schema for the form
  const validationSchema = {
    email: {
      validate: (value: string) => isRequired(value) && isEmail(value),
      errorMessage: 'Please enter a valid email address'
    }
  };

  // Initialize form state with useForm hook
  const formState = useForm<PasswordResetRequest>(
    { email: '' },
    validationSchema,
    handleSubmit
  );

  /**
   * Handles form submission to request password reset
   * @param values Form values containing the email address
   */
  async function handleSubmit(values: PasswordResetRequest): Promise<void> {
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await requestPasswordReset(values);

      if (response.success) {
        setSuccess(true);
      } else {
        setError(response.message || 'Failed to request password reset. Please try again.');
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again later.');
    } finally {
      setLoading(false);
    }
  }

  /**
   * Navigates back to the login page
   */
  const handleBackToLogin = () => {
    navigate(ROUTES.LOGIN_PATH);
  };

  return (
    <AuthLayout
      title="Forgot Password"
      subtitle="Enter your email address and we'll send you instructions to reset your password."
    >
      <Box component="form" onSubmit={formState.handleSubmit} noValidate>
        {/* Error alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Success message */}
        {success && (
          <Alert severity="success" sx={{ mb: 3 }}>
            Password reset instructions have been sent to your email address.
            Please check your inbox and follow the instructions to reset your password.
          </Alert>
        )}

        {!success && (
          <>
            {/* Email field */}
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              autoComplete="email"
              autoFocus
              value={formState.values.email}
              onChange={formState.handleChange}
              onBlur={formState.handleBlur}
              error={!!formState.errors.email && formState.touched.email}
              helperText={
                formState.touched.email && formState.errors.email
                  ? formState.errors.email
                  : ''
              }
              disabled={loading}
            />

            {/* Submit button */}
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading || !formState.isValid}
            >
              {loading ? <CircularProgress size={24} /> : 'Reset Password'}
            </Button>
          </>
        )}

        {/* Back to login link */}
        <Box textAlign="center" mt={2}>
          <Typography variant="body2">
            <Link
              component="button"
              type="button"
              variant="body2"
              onClick={handleBackToLogin}
            >
              Back to Login
            </Link>
          </Typography>
        </Box>
      </Box>
    </AuthLayout>
  );
};

export default ForgotPassword;