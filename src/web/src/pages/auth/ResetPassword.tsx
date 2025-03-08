import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import {
  TextField,
  Button,
  Box,
  Typography,
  Alert,
  LinearProgress,
  InputAdornment,
  IconButton,
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';

import AuthLayout from '../../layouts/AuthLayout';
import useForm from '../../hooks/useForm';
import { isRequired, isPassword, getPasswordStrength } from '../../utils/validation';
import { confirmPasswordReset } from '../../api/auth';
import { PasswordResetConfirmation } from '../../types/auth.types';
import { LOGIN_PATH } from '../../config/routes';

// Interface for form values
interface FormValues {
  password: string;
  confirmPassword: string;
}

const ResetPassword: React.FC = () => {
  const navigate = useNavigate();
  const { token } = useParams<{ token: string }>();
  
  // State for password visibility
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  // State for password strength indicator
  const [passwordStrength, setPasswordStrength] = useState(0);
  
  // State for submission status
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  
  // Form validation schema
  const validationSchema = {
    password: {
      validate: isPassword,
      errorMessage: 'Password must be at least 8 characters with uppercase, lowercase, number, and special character',
    },
    confirmPassword: {
      validate: (value: string, allValues?: Record<string, any>) => 
        isRequired(value) && value === allValues?.password,
      errorMessage: 'Passwords must match',
    },
  };
  
  // Initialize form with useForm hook
  const formState = useForm<FormValues>(
    { password: '', confirmPassword: '' },
    validationSchema,
    () => {} // Empty function as we'll handle submission ourselves
  );
  
  // Update password strength when password changes
  useEffect(() => {
    if (formState.values.password) {
      setPasswordStrength(getPasswordStrength(formState.values.password));
    } else {
      setPasswordStrength(0);
    }
  }, [formState.values.password]);
  
  // Form submission handler
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!token) {
      setError('Reset token is missing. Please use the link from your email.');
      return;
    }
    
    // Validate all fields before submission
    const isValid = formState.validateAllFields();
    if (!isValid) {
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const resetData: PasswordResetConfirmation = {
        token,
        password: formState.values.password,
        confirmPassword: formState.values.confirmPassword,
      };
      
      const response = await confirmPasswordReset(resetData);
      
      if (response.success) {
        setSuccess(true);
        // Redirect to login page after 3 seconds
        setTimeout(() => {
          navigate(LOGIN_PATH);
        }, 3000);
      } else {
        setError(response.message || 'Failed to reset password. Please try again.');
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again later.');
      console.error('Password reset error:', err);
    } finally {
      setLoading(false);
    }
  };
  
  // Toggle password visibility
  const handleTogglePasswordVisibility = () => {
    setShowPassword((prevShowPassword) => !prevShowPassword);
  };
  
  // Toggle confirm password visibility
  const handleToggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword((prevShowConfirmPassword) => !prevShowConfirmPassword);
  };
  
  // Get password strength color
  const getPasswordStrengthColor = () => {
    if (passwordStrength < 34) return 'error';
    if (passwordStrength < 67) return 'warning';
    return 'success';
  };
  
  return (
    <AuthLayout title="Reset Your Password" subtitle="Enter a new password to continue">
      {!token ? (
        <Alert severity="error" sx={{ mb: 3 }}>
          Reset token is missing. Please use the link from your email.
        </Alert>
      ) : success ? (
        <Alert severity="success" sx={{ mb: 3 }}>
          Your password has been reset successfully! You will be redirected to the login page.
        </Alert>
      ) : (
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}
          
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="New Password"
            type={showPassword ? 'text' : 'password'}
            id="password"
            autoComplete="new-password"
            value={formState.values.password}
            onChange={formState.handleChange}
            onBlur={formState.handleBlur}
            error={!!formState.errors.password}
            helperText={formState.errors.password}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={handleTogglePasswordVisibility}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
          
          {formState.values.password && (
            <Box sx={{ mb: 2, mt: 1 }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                Password Strength: {passwordStrength < 34 ? 'Weak' : passwordStrength < 67 ? 'Medium' : 'Strong'}
              </Typography>
              <LinearProgress
                variant="determinate"
                value={passwordStrength}
                color={getPasswordStrengthColor()}
                sx={{ height: 8, borderRadius: 1 }}
              />
            </Box>
          )}
          
          <TextField
            margin="normal"
            required
            fullWidth
            name="confirmPassword"
            label="Confirm New Password"
            type={showConfirmPassword ? 'text' : 'password'}
            id="confirmPassword"
            autoComplete="new-password"
            value={formState.values.confirmPassword}
            onChange={formState.handleChange}
            onBlur={formState.handleBlur}
            error={!!formState.errors.confirmPassword}
            helperText={formState.errors.confirmPassword}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle confirm password visibility"
                    onClick={handleToggleConfirmPasswordVisibility}
                    edge="end"
                  >
                    {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
          
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={loading}
          >
            {loading ? 'Resetting Password...' : 'Reset Password'}
          </Button>
          
          <Box sx={{ textAlign: 'center' }}>
            <Link to={LOGIN_PATH}>
              Back to Login
            </Link>
          </Box>
        </Box>
      )}
    </AuthLayout>
  );
};

export default ResetPassword;