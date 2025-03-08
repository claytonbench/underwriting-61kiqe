import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { Page } from '../../components/common';
import useAuth from '../../hooks/useAuth';

/**
 * Error page component that displays a 404 Not Found error message
 * when a user attempts to access a resource that doesn't exist.
 * Provides a user-friendly explanation and navigation options
 * to return to an accessible area of the application.
 */
const Error404: React.FC = () => {
  const navigate = useNavigate();
  const { state } = useAuth();

  // Navigate back to the previous page
  const handleGoBack = () => {
    navigate(-1);
  };

  // Navigate to the appropriate home page based on user role
  const handleGoHome = () => {
    if (state.isAuthenticated && state.user) {
      // Determine the appropriate dashboard based on user type
      switch (state.user.userType) {
        case 'school_admin':
          navigate('/school/dashboard');
          break;
        case 'underwriter':
          navigate('/underwriter/dashboard');
          break;
        case 'qc':
          navigate('/qc/dashboard');
          break;
        case 'system_admin':
          navigate('/admin/dashboard');
          break;
        case 'borrower':
        case 'co_borrower':
        default:
          navigate('/dashboard');
          break;
      }
    } else {
      // Not authenticated, go to login page
      navigate('/login');
    }
  };

  return (
    <Page title="Page Not Found">
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        textAlign="center"
        py={8}
        px={2}
      >
        <Typography variant="h1" color="error" sx={{ fontSize: { xs: '4rem', sm: '6rem' }, fontWeight: 'bold' }} gutterBottom>
          404
        </Typography>
        <Typography variant="h4" color="textPrimary" gutterBottom>
          Oops! Page Not Found
        </Typography>
        <Typography variant="body1" color="textSecondary" paragraph>
          We couldn't find the page you're looking for. The page may have been moved, 
          deleted, or the URL might have been mistyped.
        </Typography>
        <Typography variant="body2" color="textSecondary" paragraph>
          Please check the URL or use one of the options below to navigate to an accessible area of the application.
        </Typography>
        <Box mt={4} display="flex" gap={2} flexWrap="wrap" justifyContent="center">
          <Button 
            variant="outlined" 
            color="primary" 
            onClick={handleGoBack}
            aria-label="Go back to previous page"
          >
            Go Back
          </Button>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleGoHome}
            aria-label={state.isAuthenticated ? "Go to dashboard" : "Go to login page"}
          >
            {state.isAuthenticated ? 'Go to Dashboard' : 'Go to Login'}
          </Button>
        </Box>
        <Box mt={6} maxWidth="600px">
          <Typography variant="body2" color="textSecondary">
            If you believe this is an error and you should have access to this page, 
            please contact our support team for assistance.
          </Typography>
        </Box>
      </Box>
    </Page>
  );
};

export default Error404;