import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { Page } from '../../components/common';
import useAuth from '../../hooks/useAuth';

/**
 * Component that renders a 500 Internal Server Error page with user-friendly
 * explanation and navigation options to recover from the error.
 * 
 * @returns Rendered error page component
 */
const Error500: React.FC = () => {
  const navigate = useNavigate();
  const { state } = useAuth();
  
  // Generate a random incident ID for support reference
  const incidentId = React.useMemo(() => {
    const randomId = Math.random().toString(36).substring(2, 8).toUpperCase();
    const timestamp = Date.now().toString(36).substring(-4);
    return `INC-${randomId}-${timestamp}`;
  }, []);
  
  // Navigate to the previous page
  const handleGoBack = () => {
    navigate(-1);
  };
  
  // Navigate to the appropriate home page based on user role
  const handleGoHome = () => {
    if (state.isAuthenticated) {
      // Redirect to the appropriate dashboard based on user type
      switch (state.user?.userType) {
        case 'system_admin':
          navigate('/admin/dashboard');
          break;
        case 'underwriter':
          navigate('/underwriting/dashboard');
          break;
        case 'school_admin':
          navigate('/school/dashboard');
          break;
        case 'qc':
          navigate('/qc/dashboard');
          break;
        case 'borrower':
        case 'co_borrower':
          navigate('/borrower/dashboard');
          break;
        default:
          navigate('/');
      }
    } else {
      // Redirect to landing page if not authenticated
      navigate('/');
    }
  };
  
  return (
    <Page title="500: Internal Server Error">
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        py={6}
        textAlign="center"
      >
        <Typography variant="h1" component="h1" gutterBottom color="error">
          500
        </Typography>
        
        <Typography variant="h4" component="h2" gutterBottom>
          Internal Server Error
        </Typography>
        
        <Typography variant="body1" color="textSecondary" paragraph sx={{ maxWidth: 600, mb: 3 }}>
          We're sorry, but something went wrong on our end. Our team has been notified
          and is working to fix the issue. Please try again later or contact support
          if the problem persists.
        </Typography>
        
        <Typography variant="body2" color="textSecondary" paragraph>
          Incident ID: <strong>{incidentId}</strong>
        </Typography>
        
        <Box display="flex" justifyContent="center" mt={4} gap={2}>
          <Button variant="outlined" color="primary" onClick={handleGoBack}>
            Go Back
          </Button>
          <Button variant="contained" color="primary" onClick={handleGoHome}>
            Go to Home
          </Button>
        </Box>
        
        <Typography variant="body2" color="textSecondary" mt={4}>
          If you continue to experience issues, please contact our support team and reference
          the incident ID above.
        </Typography>
      </Box>
    </Page>
  );
};

export default Error500;