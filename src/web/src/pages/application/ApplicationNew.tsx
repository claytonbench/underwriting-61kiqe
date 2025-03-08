import React, { useState, useEffect } from 'react'; // React v18.2.0
import { useNavigate } from 'react-router-dom'; // React Router v6.14.1
import { useDispatch } from 'react-redux'; // React Redux v8.1.1
import { Box, Typography, Alert } from '@mui/material'; // Material-UI v5.14.0

import Page from '../../components/common/Page';
import ApplicationFormContainer from '../../components/ApplicationForm/ApplicationFormContainer';
import useAuth from '../../hooks/useAuth';
import useNotifications from '../../hooks/useNotifications';
import DashboardLayout from '../../layouts/DashboardLayout';
import { createNewApplication } from '../../store/thunks/applicationThunks';
import LoadingOverlay from '../../components/common/Loading/LoadingOverlay';

/**
 * Page component for creating a new loan application
 *
 * @returns Rendered application form page
 */
const ApplicationNew: React.FC = () => {
  // Get authentication state using useAuth hook
  const { state: authState } = useAuth();

  // Get dispatch function using useDispatch hook
  const dispatch = useDispatch();

  // Get notification functions using useNotifications hook
  const {  } = useNotifications();

  // Get navigate function using useNavigate hook
  const navigate = useNavigate();

  // Set up state for loading, error, and success
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);

  /**
   * Handles successful form submission
   * @param applicationId The ID of the submitted application
   */
  const handleSubmitSuccess = (applicationId: string) => {
    // Set loading state to false
    setLoading(false);

    // Set success state to true
    setSuccess(true);

    // Show success notification
    

    // Navigate to application detail page or dashboard after a short delay
    setTimeout(() => {
      navigate(`/applications/${applicationId}`);
    }, 1500);
  };

  /**
   * Handles form cancellation
   */
  const handleCancel = () => {
    // Navigate back to application list or dashboard
    navigate('/applications');
  };

  // Navigate to application list or dashboard after successful submission
  useEffect(() => {
    if (success) {
      const timeoutId = setTimeout(() => {
        navigate('/applications');
      }, 3000);

      return () => clearTimeout(timeoutId);
    }
  }, [success, navigate]);

  /**
   * Renders success message after form submission
   */
  const renderSuccessMessage = () => {
    if (success) {
      return (
        <Alert severity="success">
          Application submitted successfully! Redirecting...
        </Alert>
      );
    }
    return null;
  };

  /**
   * Renders error message if operation fails
   */
  const renderErrorMessage = () => {
    if (error) {
      return (
        <Alert severity="error">
          {error}
        </Alert>
      );
    }
    return null;
  };

  // Render the page with appropriate layout and components
  return (
    <DashboardLayout>
      <Page title="New Loan Application">
        <Box>
          {renderSuccessMessage()}
          {renderErrorMessage()}
          <ApplicationFormContainer
            onSubmitSuccess={handleSubmitSuccess}
            onCancel={handleCancel}
          />
        </Box>
        {/* Display loading overlay during async operations */}
        <LoadingOverlay isLoading={loading} message="Submitting application..." />
      </Page>
    </DashboardLayout>
  );
};

export default ApplicationNew;