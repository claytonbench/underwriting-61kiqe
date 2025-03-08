import React, { useState, useEffect, useCallback } from 'react'; // react ^18.2.0
import { Grid, Typography, Paper, Tabs, Tab, Box, CircularProgress, Alert } from '@mui/material'; // @mui/material ^5.14.0
import useStyles from './styles';
import CreditInfo from './CreditInfo';
import DocumentSection from './DocumentSection';
import UnderwritingDecisionDisplay from './UnderwritingDecision';
import {
  ApplicationDetail,
  CreditInformation,
  UnderwritingDecisionData
} from '../../types/application.types';
import {
  getApplication,
} from '../../api/applications';
import {
  getCreditInformation,
  getUnderwritingDecision,
} from '../../api/underwriting';
import { formatCurrency, formatDateForDisplay } from '../../utils/formatting';

/**
 * Interface defining the props for the TabPanel component
 */
interface TabPanelProps {
  children?: React.ReactNode;
  value: number;
  index: number;
}

/**
 * Component that renders the content for a tab panel
 * @param props - The props for the component
 * @returns A JSX element that renders the tab panel
 */
function TabPanel(props: TabPanelProps): JSX.Element {
  // Destructure children, value, index, and other props from props
  const { children, value, index, ...other } = props;

  // Render a div that is hidden when the tab is not active
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {/* When the tab is active (value === index), render the children inside the div */}
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

/**
 * Helper function to generate accessibility props for tabs
 * @param index - The index of the tab
 * @returns An object with id and aria-controls properties
 */
function a11yProps(index: number): object {
  // Return an object with id and aria-controls properties based on the index
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`,
  };
}

/**
 * Interface defining the props for the ApplicationReview component
 */
interface ApplicationReviewProps {
  /**
   * The ID of the application to review
   */
  applicationId: string;
  /**
   * Whether the review interface should be in read-only mode
   */
  readOnly?: boolean;
}

/**
 * Main component for reviewing loan applications
 * @param props - The props for the component
 * @returns A JSX element that renders the application review interface
 */
const ApplicationReview: React.FC<ApplicationReviewProps> = (props) => {
  // Destructure applicationId and readOnly from props
  const { applicationId, readOnly } = props;

  // Initialize state for application data, loading state, error state, credit information, underwriting decision, and active tab
  const [application, setApplication] = useState<ApplicationDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [borrowerCredit, setBorrowerCredit] = useState<CreditInformation | null>(null);
  const [coBorrowerCredit, setCoBorrowerCredit] = useState<CreditInformation | null>(null);
  const [decision, setDecision] = useState<UnderwritingDecisionData | null>(null);
  const [activeTab, setActiveTab] = useState<number>(0);

  // Get CSS classes using useStyles hook
  const classes = useStyles();

  /**
   * Function to retrieve application details
   */
  const fetchApplicationData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getApplication(applicationId);
      if (response.success && response.data) {
        setApplication(response.data);
      } else {
        setError(response.message || 'Failed to fetch application details');
      }
    } catch (err) {
      setError('An unexpected error occurred while fetching application details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [applicationId]);

  /**
   * Function to retrieve credit data for borrower and co-borrower
   */
  const fetchCreditInformation = useCallback(async () => {
    if (!application) return;

    try {
      const borrowerCreditResponse = await getCreditInformation(application.application.id, false);
      if (borrowerCreditResponse.success && borrowerCreditResponse.data) {
        setBorrowerCredit(borrowerCreditResponse.data);
      } else {
        console.warn('Failed to fetch borrower credit information:', borrowerCreditResponse.message);
      }

      if (application.application.co_borrower_id) {
        const coBorrowerCreditResponse = await getCreditInformation(application.application.id, true);
        if (coBorrowerCreditResponse.success && coBorrowerCreditResponse.data) {
          setCoBorrowerCredit(coBorrowerCreditResponse.data);
        } else {
          console.warn('Failed to fetch co-borrower credit information:', coBorrowerCreditResponse.message);
        }
      }
    } catch (err) {
      console.error('An unexpected error occurred while fetching credit information', err);
    }
  }, [application]);

  /**
   * Function to retrieve decision data
   */
  const fetchUnderwritingDecision = useCallback(async () => {
    if (!application) return;

    try {
      const decisionResponse = await getUnderwritingDecision(application.application.id);
      if (decisionResponse.success && decisionResponse.data) {
        setDecision(decisionResponse.data);
      } else {
        console.warn('Failed to fetch underwriting decision:', decisionResponse.message);
      }
    } catch (err) {
      console.error('An unexpected error occurred while fetching underwriting decision', err);
    }
  }, [application]);

  /**
   * Function to open credit report in new tab
   */
  const handleViewCreditReport = useCallback((creditInfo: CreditInformation) => {
    window.open(creditInfo.file_path, '_blank');
  }, []);

  /**
   * Function to switch between tabs
   */
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Fetch application data, credit information, and underwriting decision when component mounts or applicationId changes
  useEffect(() => {
    fetchApplicationData();
  }, [fetchApplicationData]);

  useEffect(() => {
    fetchCreditInformation();
  }, [fetchCreditInformation, application]);

  useEffect(() => {
    fetchUnderwritingDecision();
  }, [fetchUnderwritingDecision, application]);

  // Render loading indicator while data is being fetched
  if (loading) {
    return (
      <div className={classes.loadingContainer}>
        <CircularProgress />
        <Typography variant="body2" style={{ marginTop: 16 }}>
          Loading application details...
        </Typography>
      </div>
    );
  }

  // Render error message if data fetching fails
  if (error) {
    return (
      <Alert severity="error" className={classes.errorContainer}>
        {error}
      </Alert>
    );
  }

  // Render application review interface with tabs for different sections
  return (
    <Paper className={classes.root}>
      <Tabs
        value={activeTab}
        onChange={handleTabChange}
        aria-label="application review tabs"
        className={classes.tabs}
      >
        <Tab label="Borrower Info" {...a11yProps(0)} />
        {application?.application.co_borrower_id && <Tab label="Co-Borrower Info" {...a11yProps(1)} />}
        <Tab label="Loan Details" {...a11yProps(2)} />
        <Tab label="Credit Info" {...a11yProps(3)} />
        <Tab label="Documents" {...a11yProps(4)} />
        <Tab label="Underwriting Decision" {...a11yProps(5)} />
      </Tabs>

      {/* Render borrower information section with personal and financial details */}
      <TabPanel value={activeTab} index={0} className={classes.tabPanel}>
        <Typography variant="h6" className={classes.sectionHeader}>
          Borrower Information
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1">Personal Details</Typography>
            <div className={classes.infoGrid}>
              <div>
                <Typography variant="body2" className={classes.infoLabel}>
                  Name:
                </Typography>
                <Typography variant="body1" className={classes.infoValue}>
                  {application?.borrower.firstName} {application?.borrower.lastName}
                </Typography>
              </div>
              <div>
                <Typography variant="body2" className={classes.infoLabel}>
                  Email:
                </Typography>
                <Typography variant="body1" className={classes.infoValue}>
                  {application?.borrower.userId}
                </Typography>
              </div>
              <div>
                <Typography variant="body2" className={classes.infoLabel}>
                  Phone:
                </Typography>
                <Typography variant="body1" className={classes.infoValue}>
                  {application?.borrower.phone}
                </Typography>
              </div>
            </div>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1">Financial Details</Typography>
            <div className={classes.infoGrid}>
              <div>
                <Typography variant="body2" className={classes.infoLabel}>
                  Housing Status:
                </Typography>
                <Typography variant="body1" className={classes.infoValue}>
                  {application?.borrower.housingStatus}
                </Typography>
              </div>
              <div>
                <Typography variant="body2" className={classes.infoLabel}>
                  Housing Payment:
                </Typography>
                <Typography variant="body1" className={classes.infoValue}>
                  {formatCurrency(application?.borrower.housingPayment)}
                </Typography>
              </div>
            </div>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Render co-borrower information section if applicable */}
      {application?.application.co_borrower_id && (
        <TabPanel value={activeTab} index={1} className={classes.tabPanel}>
          <Typography variant="h6" className={classes.sectionHeader}>
            Co-Borrower Information
          </Typography>
          {application.co_borrower ? (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1">Personal Details</Typography>
                <div className={classes.infoGrid}>
                  <div>
                    <Typography variant="body2" className={classes.infoLabel}>
                      Name:
                    </Typography>
                    <Typography variant="body1" className={classes.infoValue}>
                      {application.co_borrower.firstName} {application.co_borrower.lastName}
                    </Typography>
                  </div>
                  <div>
                    <Typography variant="body2" className={classes.infoLabel}>
                      Email:
                    </Typography>
                    <Typography variant="body1" className={classes.infoValue}>
                      {application.co_borrower.userId}
                    </Typography>
                  </div>
                  <div>
                    <Typography variant="body2" className={classes.infoLabel}>
                      Phone:
                    </Typography>
                    <Typography variant="body1" className={classes.infoValue}>
                      {application.co_borrower.phone}
                    </Typography>
                  </div>
                </div>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1">Financial Details</Typography>
                <div className={classes.infoGrid}>
                  <div>
                    <Typography variant="body2" className={classes.infoLabel}>
                      Housing Status:
                    </Typography>
                    <Typography variant="body1" className={classes.infoValue}>
                      {application.co_borrower.housingStatus}
                    </Typography>
                  </div>
                  <div>
                    <Typography variant="body2" className={classes.infoLabel}>
                      Housing Payment:
                    </Typography>
                    <Typography variant="body1" className={classes.infoValue}>
                      {formatCurrency(application.co_borrower.housingPayment)}
                    </Typography>
                  </div>
                </div>
              </Grid>
            </Grid>
          ) : (
            <Typography variant="body1">
              Co-borrower information not available.
            </Typography>
          )}
        </TabPanel>
      )}

      {/* Render loan details section with program and financial information */}
      <TabPanel value={activeTab} index={2} className={classes.tabPanel}>
        <Typography variant="h6" className={classes.sectionHeader}>
          Loan Details
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1">Program Information</Typography>
            <div className={classes.infoGrid}>
              <div>
                <Typography variant="body2" className={classes.infoLabel}>
                  School:
                </Typography>
                <Typography variant="body1" className={classes.infoValue}>
                  {application?.school.name}
                </Typography>
              </div>
              <div>
                <Typography variant="body2" className={classes.infoLabel}>
                  Program:
                </Typography>
                <Typography variant="body1" className={classes.infoValue}>
                  {application?.program.name}
                </Typography>
              </div>
              <div>
                <Typography variant="body2" className={classes.infoLabel}>
                  Tuition:
                </Typography>
                <Typography variant="body1" className={classes.infoValue}>
                  {formatCurrency(application?.loan_details.tuition_amount)}
                </Typography>
              </div>
            </div>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1">Financial Information</Typography>
            <div className={classes.infoGrid}>
              <div>
                <Typography variant="body2" className={classes.infoLabel}>
                  Requested Amount:
                </Typography>
                <Typography variant="body1" className={classes.infoValue}>
                  {formatCurrency(application?.loan_details.requested_amount)}
                </Typography>
              </div>
              <div>
                <Typography variant="body2" className={classes.infoLabel}>
                  Start Date:
                </Typography>
                <Typography variant="body1" className={classes.infoValue}>
                  {formatDateForDisplay(application?.loan_details.start_date)}
                </Typography>
              </div>
              <div>
                <Typography variant="body2" className={classes.infoLabel}>
                  End Date:
                </Typography>
                <Typography variant="body1" className={classes.infoValue}>
                  {formatDateForDisplay(application?.loan_details.completion_date)}
                </Typography>
              </div>
            </div>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Render credit information section using CreditInfo component */}
      <TabPanel value={activeTab} index={3} className={classes.tabPanel}>
        <Typography variant="h6" className={classes.sectionHeader}>
          Credit Information
        </Typography>
        <CreditInfo
          borrowerCredit={borrowerCredit}
          coBorrowerCredit={coBorrowerCredit}
          onViewCreditReport={handleViewCreditReport}
        />
      </TabPanel>

      {/* Render documents section using DocumentSection component */}
      <TabPanel value={activeTab} index={4} className={classes.tabPanel}>
        <DocumentSection application={application.application} />
      </TabPanel>

      {/* Render underwriting decision section using UnderwritingDecisionDisplay component */}
      <TabPanel value={activeTab} index={5} className={classes.tabPanel}>
        <UnderwritingDecisionDisplay decision={decision} />
      </TabPanel>
    </Paper>
  );
};

export default ApplicationReview;