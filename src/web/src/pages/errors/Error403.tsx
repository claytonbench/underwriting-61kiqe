import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { Page } from '../../components/common';
import useAuth from '../../hooks/useAuth';

/**
 * Component that renders a 403 Forbidden error page when a user attempts
 * to access a resource they don't have permission to view.
 * Provides a user-friendly explanation and navigation options to return
 * to an accessible area of the application.
 * 
 * @returns Rendered error page component
 */
const Error403: React.FC = () => {
  const navigate = useNavigate();
  const { state } = useAuth();

  // Handle navigation to the previous page
  const handleGoBack = () => {
    navigate(-1);
  };

  // Handle navigation to the appropriate homepage based on user role
  const handleGoHome = () => {
    if (state.isAuthenticated && state.user) {
      // Navigate to role-specific dashboard
      switch (state.user.userType) {
        case 'borrower':
        case 'co_borrower':
          navigate('/borrower/dashboard');
          break;
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
        default:
          navigate('/');
          break;
      }
    } else {
      // If not authenticated, go to login page
      navigate('/login');
    }
  };

  return (
    <Page title="403 - Access Forbidden">
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        py={8}
      >
        <Typography variant="h1" color="error" gutterBottom>
          403
        </Typography>
        <Typography variant="h4" gutterBottom>
          Access Forbidden
        </Typography>
        <Typography variant="body1" align="center" paragraph>
          You do not have permission to access this resource.
        </Typography>
        <Typography variant="body2" align="center" color="textSecondary" paragraph>
          If you believe this is an error, please contact your system administrator or support team.
        </Typography>
        <Box display="flex" gap={2} mt={4}>
          <Button variant="outlined" color="primary" onClick={handleGoBack}>
            Go Back
          </Button>
          <Button variant="contained" color="primary" onClick={handleGoHome}>
            Go to Home
          </Button>
        </Box>
      </Box>
    </Page>
  );
};

export default Error403;