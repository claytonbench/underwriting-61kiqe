import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux'; // react-redux v8.1.1
import { Link } from 'react-router-dom'; // react-router-dom v6.14.0
import { Grid, Typography, Button, Box, Divider } from '@mui/material'; // @mui/material v5.14.0
import { Add as AddIcon } from '@mui/icons-material'; // @mui/icons-material v5.14.0
import { makeStyles } from '@mui/styles'; // @mui/styles v5.14.0

// Internal imports
import DashboardLayout from '../../layouts/DashboardLayout';
import { Card, StatusBadge, LoadingSpinner } from '../../components/common';
import ApplicationStatus from '../../components/ApplicationStatus';
import { RootState } from '../../store/rootReducer';
import { fetchBorrowerApplications } from '../../store/actions/applicationActions';
import { fetchPendingSignatureRequests } from '../../store/thunks/documentThunks';
import { useAuth } from '../../hooks/useAuth';
import {
  ApplicationListItem,
  SignatureRequest,
  INotificationDisplay
} from '../../types';

/**
 * Define component styles using makeStyles
 */
const useStyles = makeStyles((theme) => ({
  dashboardContainer: {
    padding: theme.spacing(3),
  },
  applicationsSection: {
    marginTop: theme.spacing(3),
  },
  documentsSection: {
    marginTop: theme.spacing(3),
  },
  notificationsSection: {
    marginTop: theme.spacing(3),
  },
  applicationCard: {
    marginBottom: theme.spacing(2),
  },
  documentCard: {
    marginBottom: theme.spacing(2),
  },
  notificationItem: {
    marginBottom: theme.spacing(1),
  },
}));

/**
 * Component to display a summary of a loan application
 * @param {object} { application: ApplicationListItem }
 * @returns {JSX.Element} Rendered application card
 */
const ApplicationCard: React.FC<{ application: ApplicationListItem }> = ({ application }) => {
  const classes = useStyles();

  return (
    <Card className={classes.applicationCard}>
      <Typography variant="h6">Application ID: {application.id}</Typography>
      <Typography>School: {application.school_name}</Typography>
      <Typography>Program: {application.program_name}</Typography>
      <Typography>Amount: {application.requested_amount}</Typography>
      <StatusBadge status={application.status} />
      <Button component={Link} to={`/applications/${application.id}`}>
        View
      </Button>
    </Card>
  );
};

/**
 * Component to display a document requiring signature
 * @param {object} { signatureRequest: SignatureRequest }
 * @returns {JSX.Element} Rendered document card
 */
const DocumentCard: React.FC<{ signatureRequest: SignatureRequest }> = ({ signatureRequest }) => {
  const classes = useStyles();

  return (
    <Card className={classes.documentCard}>
      <Typography variant="h6">Document: {signatureRequest.document_id}</Typography>
      <Typography>Application ID: {signatureRequest.document_id}</Typography>
      <Typography>Due Date: {signatureRequest.requested_at}</Typography>
      <StatusBadge status={signatureRequest.status} />
      <Button onClick={() => handleSignDocument(signatureRequest.id)}>
        Sign Now
      </Button>
    </Card>
  );
};

/**
 * Component to display a notification item
 * @param {object} { notification: INotificationDisplay }
 * @returns {JSX.Element} Rendered notification item
 */
const NotificationItem: React.FC<{ notification: INotificationDisplay }> = ({ notification }) => {
  const classes = useStyles();

  return (
    <Card className={classes.notificationItem}>
      <Typography variant="h6">{notification.title}</Typography>
      <Typography>{notification.message}</Typography>
      <Typography>Timestamp: {notification.timestamp}</Typography>
      {notification.actionUrl && (
        <Button component={Link} to={notification.actionUrl}>
          {notification.actionLabel}
        </Button>
      )}
    </Card>
  );
};

/**
 * Handler for document signing button click
 * @param {string} signatureRequestId
 * @returns {void} No return value
 */
const handleSignDocument = (signatureRequestId: string) => {
  // Navigate to document signing page with signature request ID
  console.log(`Signing document with ID: ${signatureRequestId}`);
};

/**
 * Handler for application view button click
 * @param {string} applicationId
 * @returns {void} No return value
 */
const handleViewApplication = (applicationId: string) => {
  // Navigate to application detail page with application ID
  console.log(`Viewing application with ID: ${applicationId}`);
};

/**
 * Main component for the borrower dashboard page
 * @returns {JSX.Element} Rendered borrower dashboard
 */
export const BorrowerDashboard: React.FC = () => {
  // Get authentication state using useAuth hook
  const { state } = useAuth();

  // Define component styles using makeStyles
  const classes = useStyles();

  // Get application state from Redux store using useSelector
  const applications = useSelector((state: RootState) => state.application.applications);

  // Get document state from Redux store using useSelector
  const pendingSignatures = useSelector((state: RootState) => state.document.pendingSignatures);

  // Get notification state from Redux store using useSelector
  const notifications = useSelector((state: RootState) => state.notification.notifications);

  // Initialize Redux dispatch function
  const dispatch = useDispatch();

  // Set up state for loading status
  const [loading, setLoading] = useState(false);

  // Set up effect to fetch borrower's applications on component mount
  useEffect(() => {
    setLoading(true);
    dispatch(fetchBorrowerApplications({ page: 1, pageSize: 10 }))
      .then(() => setLoading(false))
      .catch(() => setLoading(false));
  }, [dispatch]);

  // Set up effect to fetch pending signature requests on component mount
  useEffect(() => {
    dispatch(fetchPendingSignatureRequests());
  }, [dispatch]);

  return (
    <DashboardLayout>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography variant="h4">Welcome, {state.user?.firstName}</Typography>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card title="My Applications">
            {loading ? (
              <LoadingSpinner />
            ) : (
              applications.map((application) => (
                <ApplicationCard key={application.id} application={application} />
              ))
            )}
            <Button
              component={Link}
              to="/applications/new"
              startIcon={<AddIcon />}
            >
              New Application
            </Button>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card title="Documents Requiring Signature">
            {pendingSignatures.map((signatureRequest) => (
              <DocumentCard key={signatureRequest.id} signatureRequest={signatureRequest} />
            ))}
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card title="Recent Notifications">
            {notifications.map((notification) => (
              <NotificationItem key={notification.id} notification={notification} />
            ))}
          </Card>
        </Grid>
      </Grid>
    </DashboardLayout>
  );
};