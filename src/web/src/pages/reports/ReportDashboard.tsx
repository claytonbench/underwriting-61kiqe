import React, { useState, useEffect, useCallback } from 'react'; // react v18.0+
import { useNavigate } from 'react-router-dom'; // react-router-dom v6.0+
import { Grid, Typography, Button, Box, Divider, Tabs, Tab, IconButton, Tooltip } from '@mui/material'; // mui/material v5.14.0+
import { BarChartIcon, AssessmentIcon, DescriptionIcon, AccountBalanceIcon, AddIcon, RefreshIcon } from '@mui/icons-material'; // mui/icons-material v5.14.0+

import { Page, Card, DataTable, LoadingOverlay } from '../../components/common';
import { getSavedReports, getReportConfigurations } from '../../api/reports';
import { useAuth } from '../../hooks';

/**
 * Interface for report data (replace with actual type)
 */
interface ReportData {
  id: string;
  name: string;
  type: string;
  generatedDate: string;
  status: string;
  action: string;
}

/**
 * Interface for report configuration (replace with actual type)
 */
interface ReportConfiguration {
  id: string;
  name: string;
  description: string;
  reportType: string;
}

/**
 * React functional component that renders the main reporting dashboard with report cards, recent reports, and metrics
 * @returns The rendered component
 */
const ReportDashboard: React.FC = () => {
  // Define state variables for saved reports, report configurations, loading state, and active tab
  const [savedReports, setSavedReports] = useState<ReportData[]>([]);
  const [reportConfigurations, setReportConfigurations] = useState<ReportConfiguration[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<number>(0);

  // Use useAuth hook to get current user information and permissions
  const { state } = useAuth();

  // Use useNavigate hook for programmatic navigation
  const navigate = useNavigate();

  /**
   * Formats a date string into a human-readable format
   * @param dateString 
   * @returns Formatted date string
   */
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  /**
   * Handles changing the active tab
   * @param event 
   * @param newValue 
   */
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  /**
   * Navigates to the selected report type page
   * @param reportType 
   */
  const handleReportTypeClick = (reportType: string) => {
    navigate(`/reports/${reportType}`);
  };

  /**
   * Navigates to the detailed view of a saved report
   * @param reportId 
   * @param reportType 
   */
  const handleViewReport = (reportId: string, reportType: string) => {
    navigate(`/reports/${reportType}/${reportId}`);
  };

  /**
   * Implement useEffect to load saved reports and report configurations on component mount
   */
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        // Fetch saved reports
        const savedReportsResponse = await getSavedReports();
        if (savedReportsResponse.success && savedReportsResponse.data) {
          // Map the API response to the ReportData interface
          const mappedSavedReports: ReportData[] = savedReportsResponse.data.results.map(report => ({
            id: report.id,
            name: report.configuration_name,
            type: report.report_type,
            generatedDate: formatDate(report.generated_at),
            status: 'Completed', // Replace with actual status if available
            action: 'View',
          }));
          setSavedReports(mappedSavedReports);
        } else {
          console.error('Failed to load saved reports:', savedReportsResponse.message);
        }

        // Fetch report configurations
        const reportConfigurationsResponse = await getReportConfigurations();
        if (reportConfigurationsResponse.success && reportConfigurationsResponse.data) {
          // Map the API response to the ReportConfiguration interface
          const mappedReportConfigurations: ReportConfiguration[] = reportConfigurationsResponse.data.results.map(config => ({
            id: config.id,
            name: config.name,
            description: config.description,
            reportType: config.report_type,
          }));
          setReportConfigurations(mappedReportConfigurations);
        } else {
          console.error('Failed to load report configurations:', reportConfigurationsResponse.message);
        }
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Define columns for the recent reports table
  const recentReportsColumns = [
    { field: 'name', headerName: 'Report Name', width: 200 },
    { field: 'type', headerName: 'Report Type', width: 150 },
    { field: 'generatedDate', headerName: 'Generated Date', width: 150 },
    { field: 'status', headerName: 'Status', width: 120 },
    {
      field: 'action',
      headerName: 'Action',
      width: 100,
      render: (value: string, row: ReportData) => (
        <Button size="small" onClick={() => handleViewReport(row.id, row.type)}>
          {value}
        </Button>
      ),
    },
  ];

  // Define report type cards
  const reportTypeCards = [
    {
      title: 'Application Volume',
      description: 'Track the number of loan applications over time.',
      icon: <BarChartIcon />,
      reportType: 'application-volume',
    },
    {
      title: 'Underwriting Report',
      description: 'Analyze underwriting decisions and processing times.',
      icon: <AssessmentIcon />,
      reportType: 'underwriting',
    },
    {
      title: 'Document Status',
      description: 'Monitor the status of required documents for loan applications.',
      icon: <DescriptionIcon />,
      reportType: 'document-status',
    },
    {
      title: 'Funding Report',
      description: 'Track loan disbursement and funding metrics.',
      icon: <AccountBalanceIcon />,
      reportType: 'funding',
    },
  ];

  return (
    <Page title="Reports">
      <LoadingOverlay isLoading={loading} message="Loading reports..." />
      <Grid container spacing={3}>
        {/* Report Type Cards */}
        {reportTypeCards.map((card) => (
          <Grid item xs={12} sm={6} md={4} key={card.title}>
            <Card title={card.title} subheader={card.description}>
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 150 }}>
                {card.icon}
                <Button onClick={() => handleReportTypeClick(card.reportType)}>Generate Report</Button>
              </Box>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Divider sx={{ my: 3 }} />

      {/* Tabs */}
      <Tabs value={activeTab} onChange={handleTabChange} aria-label="report tabs">
        <Tab label="Overview" />
        <Tab label="Recent Reports" />
        <Tab label="Scheduled Reports" />
      </Tabs>

      {/* Tab Panels */}
      {activeTab === 0 && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6">Key Metrics</Typography>
          {/* Add key metrics and visualizations here */}
          <Typography variant="body2">No metrics available yet.</Typography>
        </Box>
      )}

      {activeTab === 1 && (
        <Box sx={{ mt: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Recent Reports</Typography>
            <Tooltip title="Refresh Reports">
              <IconButton onClick={() => { /* Implement refresh logic */ }}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Box>
          <DataTable
            data={savedReports}
            columns={recentReportsColumns}
            loading={loading}
            emptyStateMessage="No recent reports available."
          />
        </Box>
      )}

      {activeTab === 2 && (
        <Box sx={{ mt: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Scheduled Reports</Typography>
            <Button variant="contained" startIcon={<AddIcon />} onClick={() => { /* Implement create schedule logic */ }}>
              Create Schedule
            </Button>
          </Box>
          {/* Add scheduled reports table here */}
          <Typography variant="body2">No scheduled reports available.</Typography>
        </Box>
      )}
    </Page>
  );
};

export default ReportDashboard;