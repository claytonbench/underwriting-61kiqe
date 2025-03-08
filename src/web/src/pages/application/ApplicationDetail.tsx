import React, { useEffect, useCallback } from 'react'; // React v18.0+
import { useParams, useNavigate } from 'react-router-dom'; // react-router-dom v6.x
import { useDispatch, useSelector } from 'react-redux'; // react-redux v8.x
import { Box, Button, Typography, Divider, Grid, Paper } from '@mui/material'; // Material-UI v5.14+
import { ArrowBack as ArrowBackIcon } from '@mui/icons-material'; // Material-UI v5.14+

// Internal imports
import Page from '../../components/common/Page';
import Breadcrumbs from '../../components/common/Breadcrumbs';
import LoadingOverlay from '../../components/common/Loading';
import ApplicationStatus from '../../components/ApplicationStatus';
import {
  fetchApplicationById,
  fetchApplicationRequiredActions,
  fetchApplicationTimeline,
  fetchApplicationDocuments,
} from '../../store/thunks/applicationThunks';
import {
  selectSelectedApplication,
  selectLoading,
  selectError,
  selectRequiredActions,
  selectTimelineEvents,
} from '../../store/slices/applicationSlice';
import { useAuth } from '../../hooks/useAuth';

/**
 * Main component for displaying detailed information about a loan application
 */
const ApplicationDetail: React.FC = () => {
  // Extract application ID from URL parameters
  const { id } = useParams<{ id: string }>();

  // Initialize navigation
  const navigate = useNavigate();

  // Get dispatch function from Redux
  const dispatch = useDispatch();

  // Get current user and role information
  const { state: authState } = useAuth();
  const user = authState.user;

  // Select application data, loading state, and error state from Redux store
  const application = useSelector(selectSelectedApplication);
  const loading = useSelector(selectLoading);
  const error = useSelector(selectError);
  const requiredActions = useSelector(selectRequiredActions);
  const timelineEvents = useSelector(selectTimelineEvents);

  /**
   * Handles navigation back to the applications list
   */
  const handleBack = useCallback(() => {
    let backUrl = '/applications';
    if (user) {
      if (user.userType === 'borrower' || user.userType === 'co_borrower') {
        backUrl = '/borrower';
      } else if (user.userType === 'school_admin') {
        backUrl = '/school-admin';
      } else if (user.userType === 'underwriter') {
        backUrl = '/underwriting/queue';
      } else if (user.userType === 'qc') {
        backUrl = '/qc';
      }
    }
    navigate(backUrl);
  }, [navigate, user]);

  /**
   * Handles actions triggered from the application status component
   * @param actionType Type of action being performed
   * @param data Additional data for the action
   */
  const handleAction = useCallback((actionType: string, data?: any) => {
    switch (actionType) {
      case 'sign_document':
        navigate(`/documents/${data.entityId}/sign`);
        break;
      case 'upload_document':
        // Navigate to document upload page
        break;
      case 'view_document':
        // Navigate to document view page
        break;
      default:
        // Handle other action types as needed
        break;
    }
  }, [navigate]);

  /**
   * Fetches application data when the component mounts or the ID changes
   */
  useEffect(() => {
    if (id) {
      dispatch(fetchApplicationById(id));
      dispatch(fetchApplicationRequiredActions(id));
      dispatch(fetchApplicationTimeline(id));
      dispatch(fetchApplicationDocuments(id));
    }
  }, [dispatch, id]);

  /**
   * Generates breadcrumb items for the current application
   * @param application Application detail
   * @returns Array of breadcrumb items with path and label
   */
  const getBreadcrumbs = useCallback((application: ApplicationDetail | null) => {
    const breadcrumbs = [{ path: '/applications', label: 'Applications' }];
    if (application) {
      breadcrumbs.push({ path: `/applications/${application.application.id}`, label: 'Application Details' });
    }
    return breadcrumbs;
  }, []);

  return (
    <Page
      title="Application Details"
      actions={
        <Button variant="outlined" startIcon={<ArrowBackIcon />} onClick={handleBack}>
          Back to Applications
        </Button>
      }
    >
      <LoadingOverlay isLoading={loading} message="Loading application details..." />
      {error && (
        <Box color="error.main" textAlign="center">
          <Typography variant="h6">Error: {error}</Typography>
        </Box>
      )}
      {application && (
        <>
          <Breadcrumbs breadcrumbs={getBreadcrumbs(application)} />
          <ApplicationStatus
            applicationDetail={application}
            requiredActions={requiredActions}
            onAction={handleAction}
          />
        </>
      )}
    </Page>
  );
};

export default ApplicationDetail;