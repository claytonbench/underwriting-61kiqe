import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom'; // ^6.10.0
import {
  TextField,
  Button,
  Box,
  Typography,
  Alert,
  Divider,
  InputAdornment,
  IconButton,
  Paper,
} from '@mui/material'; // ^5.14.0
import { Visibility, VisibilityOff } from '@mui/icons-material'; // ^5.14.0

import AuthLayout from '../../layouts/AuthLayout';
import useAuth from '../../hooks/useAuth';
import useForm from '../../hooks/useForm';
import { isEmail, isRequired, isPassword } from '../../utils/validation';
import { LoginCredentials, MFAResponse, UserType } from '../../types/auth.types';
import LoadingOverlay from '../../components/common/Loading/LoadingOverlay';
import { ROUTES } from '../../config/routes';

/**
 * Interface for login form values
 */
interface FormValues {
  email: string;
  password: string;
  rememberMe: boolean;
}

/**
 * Login page component that provides user authentication functionality for the loan management system.
 * Handles credential validation, form submission, multi-factor authentication challenges, and 
 * redirects authenticated users to appropriate dashboards based on their roles.
 */
const Login: React.FC = () => {
  const navigate = useNavigate();
  const { state, login, verifyMFA } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [mfaCode, setMfaCode] = useState('');

  // Define validation schema for login form
  const validationSchema = {
    email: {
      validate: isEmail,
      errorMessage: 'Please enter a valid email address'
    },
    password: {
      validate: isRequired,
      errorMessage: 'Password is required'
    }
  };

  // Initialize form with useForm hook
  const formState = useForm<FormValues>(
    { email: '', password: '', rememberMe: false },
    validationSchema,
    handleSubmit
  );

  /**
   * Effect to redirect authenticated users to appropriate dashboard
   */
  useEffect(() => {
    if (state.isAuthenticated && state.user) {
      switch (state.user.userType) {
        case UserType.SYSTEM_ADMIN:
          navigate(ROUTES.DASHBOARD_PATH);
          break;
        case UserType.SCHOOL_ADMIN:
          navigate('/school-admin');
          break;
        case UserType.UNDERWRITER:
          navigate('/underwriter');
          break;
        case UserType.QC:
          navigate('/qc');
          break;
        case UserType.BORROWER:
        case UserType.CO_BORROWER:
          navigate('/borrower');
          break;
        default:
          navigate(ROUTES.DASHBOARD_PATH);
      }
    }
  }, [state.isAuthenticated, state.user, navigate]);

  /**
   * Handle login form submission
   * @param e - The form event
   */
  async function handleSubmit(values: FormValues) {
    const credentials: LoginCredentials = {
      email: values.email,
      password: values.password,
      rememberMe: values.rememberMe
    };

    await login(credentials);
  }

  /**
   * Handle MFA verification form submission
   * @param e - The form event
   */
  async function handleMFASubmit(e: React.FormEvent) {
    e.preventDefault();
    
    if (!state.mfaChallenge) return;
    
    const mfaResponse: MFAResponse = {
      challengeId: state.mfaChallenge.challengeId,
      code: mfaCode
    };
    
    await verifyMFA(mfaResponse);
  }

  /**
   * Toggle password visibility
   */
  const handleTogglePasswordVisibility = () => {
    setShowPassword((prev) => !prev);
  };

  /**
   * Handle MFA code change
   */
  const handleMFACodeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setMfaCode(e.target.value);
  };

  return (
    <AuthLayout title="Sign In" subtitle="Enter your credentials to access your account">
      {/* Show loading overlay during authentication */}
      {state.loading && <LoadingOverlay isLoading={true} message="Authenticating..." />}
      
      {/* Show MFA verification form if MFA is required */}
      {state.mfaRequired && state.mfaChallenge ? (
        <Box component="form" onSubmit={handleMFASubmit} noValidate>
          <Typography variant="body1" sx={{ mb: 2 }}>
            Please enter the verification code sent to {state.mfaChallenge.destination}
          </Typography>
          
          <TextField
            margin="normal"
            required
            fullWidth
            id="mfa-code"
            label="Verification Code"
            name="mfaCode"
            autoComplete="one-time-code"
            autoFocus
            value={mfaCode}
            onChange={handleMFACodeChange}
            inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
          />
          
          {state.error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {state.error}
            </Alert>
          )}
          
          <Button
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            sx={{ mt: 3, mb: 2 }}
            disabled={!mfaCode}
          >
            Verify
          </Button>
        </Box>
      ) : (
        /* Show login form if MFA is not required */
        <Box component="form" onSubmit={formState.handleSubmit} noValidate>
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
            helperText={formState.touched.email ? formState.errors.email : ''}
          />
          
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type={showPassword ? 'text' : 'password'}
            id="password"
            autoComplete="current-password"
            value={formState.values.password}
            onChange={formState.handleChange}
            onBlur={formState.handleBlur}
            error={!!formState.errors.password && formState.touched.password}
            helperText={formState.touched.password ? formState.errors.password : ''}
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
          
          {state.error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {state.error}
            </Alert>
          )}
          
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
            <Link to="/forgot-password" style={{ textDecoration: 'none' }}>
              <Typography variant="body2" color="primary">
                Forgot password?
              </Typography>
            </Link>
          </Box>
          
          <Button
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            size="large"
            sx={{ mt: 3, mb: 2 }}
            disabled={formState.isSubmitting}
          >
            Sign In
          </Button>
          
          <Divider sx={{ my: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Or
            </Typography>
          </Divider>
          
          <Box sx={{ textAlign: 'center', mt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Having trouble signing in? Contact your administrator.
            </Typography>
          </Box>
        </Box>
      )}
    </AuthLayout>
  );
};

export default Login;