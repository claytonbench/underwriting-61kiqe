import React, { useState, useEffect, useCallback } from 'react'; // React v18.2.0
import { useParams } from 'react-router-dom'; // react-router-dom v6.0.0
import {
  Grid,
  Typography,
  Button,
  Box,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
} from '@mui/material'; // @mui/material v5.14.0
import { DatePicker } from '@mui/x-date-pickers'; // @mui/x-date-pickers v6.0.0
import {
  BarChart,
  PieChart,
  LineChart,
  Bar,
  Pie,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  Cell,
  ResponsiveContainer,
} from 'recharts'; // recharts v2.5.0
import DownloadIcon from '@mui/icons-material/Download'; // @mui/icons-material v5.14.0
import RefreshIcon from '@mui/icons-material/Refresh'; // @mui/icons-material v5.14.0

import {
  Page,
  Card,
  DataTable,
  LoadingOverlay,
  getUnderwritingMetricsReport,
  exportReport,
  getSavedReport,
  useAuth,
} from '../../components/common';
import {
  UnderwritingDecision,
  DecisionReasonCode,
} from '../../types';
import { DateRange } from '../../types/common.types';

/**
 * React functional component that renders the underwriting metrics report page
 * @returns The rendered component
 */
const UnderwritingReport: React.FC = () => {
  // Define state variables for report data, loading state, date range, and filter options
  const [reportData, setReportData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [dateRange, setDateRange] = useState<DateRange>({ start: null, end: null });
  const [filters, setFilters] = useState<{ schoolId: string | null; underwriterId: string | null }>({
    schoolId: null,
    underwriterId: null,
  });

  // Use useParams hook to get report ID from URL if viewing a saved report
  const { id: reportId } = useParams<{ id: string }>();

  // Use useAuth hook to get current user information and permissions
  const { state } = useAuth();

  /**
   * Loads saved report data if report ID is provided
   */
  useEffect(() => {
    const loadSavedReport = async () => {
      if (reportId) {
        setLoading(true);
        try {
          const response = await getSavedReport(reportId);
          if (response.success && response.data) {
            setReportData(response.data.result_data);
            setDateRange(response.data.parameters.dateRange);
            setFilters({
              schoolId: response.data.parameters.schoolId || null,
              underwriterId: response.data.parameters.underwriterId || null,
            });
          } else {
            console.error('Failed to load saved report:', response.message);
          }
        } catch (error) {
          console.error('Error loading saved report:', error);
        } finally {
          setLoading(false);
        }
      }
    };

    loadSavedReport();
  }, [reportId]);

  /**
   * Generates a new underwriting metrics report based on current filters
   */
  const handleGenerateReport = useCallback(async () => {
    setLoading(true);
    try {
      // Construct report parameters from state (date range, filters)
      const reportParams = {
        date_range: dateRange,
        school_id: filters.schoolId,
        underwriter_id: filters.underwriterId,
      };

      // Call getUnderwritingMetricsReport API function with parameters
      const response = await getUnderwritingMetricsReport(reportParams);

      // Process the API response and update report data state
      if (response.success && response.data) {
        setReportData(response.data);
      } else {
        console.error('Failed to generate report:', response.message);
      }
    } catch (error) {
      console.error('Error generating report:', error);
    } finally {
      setLoading(false);
    }
  }, [dateRange, filters]);

  /**
   * Exports the current report in the specified format
   * @param format
   */
  const handleExportReport = useCallback(async (format: string) => {
    if (!reportData) return;

    setLoading(true);
    try {
      // Call exportReport API function with report ID and format
      // const response = await exportReport(reportId, { format });
      // TODO: Implement exportReport API and replace with actual report ID
      // For now, simulate export with a dummy download URL
      const downloadUrl = 'https://example.com/report.pdf';

      // Trigger file download using the URL
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `underwriting_report.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error exporting report:', error);
    } finally {
      setLoading(false);
    }
  }, [reportData]);

  /**
   * Updates the date range filter state
   * @param newDateRange
   */
  const handleDateRangeChange = (newDateRange: DateRange) => {
    setDateRange(newDateRange);
  };

  /**
   * Updates the filter options state
   * @param event
   */
  const handleFilterChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setFilters(prevFilters => ({
      ...prevFilters,
      [name]: value,
    }));
  };

  /**
   * Renders the approval rate trend chart
   */
  const renderApprovalRateChart = () => {
    if (!reportData || !reportData.approvalTrends) return null;

    // Process report data to extract approval rate trends over time
    const chartData = reportData.approvalTrends.map((item: any) => ({
      date: item.date,
      approvalRate: item.approvalRate * 100,
    }));

    return (
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis tickFormatter={(value) => `${value}%`} />
          <RechartsTooltip labelFormatter={(value) => `Date: ${value}`} formatter={(value) => [`${value}%`, 'Approval Rate']} />
          <Legend />
          <Line type="monotone" dataKey="approvalRate" stroke="#8884d8" activeDot={{ r: 8 }} />
        </LineChart>
      </ResponsiveContainer>
    );
  };

  /**
   * Renders the decision reasons distribution chart
   */
  const renderDecisionReasonsChart = () => {
    if (!reportData || !reportData.decisionReasons) return null;

    // Process report data to extract decision reason distribution
    const chartData = reportData.decisionReasons.map((item: any) => ({
      reason: item.reason,
      count: item.count,
    }));

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#808080'];

    return (
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            dataKey="count"
            nameKey="reason"
            cx="50%"
            cy="50%"
            outerRadius={80}
            fill="#8884d8"
            label
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <RechartsTooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    );
  };

  /**
   * Renders the decision time chart
   */
  const renderDecisionTimeChart = () => {
    if (!reportData || !reportData.decisionTimes) return null;

    // Process report data to extract decision time metrics
    const chartData = reportData.decisionTimes.map((item: any) => ({
      date: item.date,
      decisionTime: item.decisionTime,
    }));

    return (
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <RechartsTooltip labelFormatter={(value) => `Date: ${value}`} formatter={(value) => [`${value}`, 'Decision Time']} />
          <Legend />
          <Bar dataKey="decisionTime" fill="#82ca9d" />
        </BarChart>
      </ResponsiveContainer>
    );
  };

  /**
   * Renders the key metrics summary section
   */
  const renderMetricsSummary = () => {
    if (!reportData) return null;

    // Extract key metrics from report data (approval rate, average decision time, etc.)
    const { approvalRate, averageDecisionTime, totalApplications } = reportData;

    return (
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card title="Total Applications" subheader="Total number of applications">
            <Typography variant="h5">{totalApplications}</Typography>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card title="Approval Rate" subheader="Percentage of applications approved">
            <Typography variant="h5">{approvalRate}</Typography>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card title="Average Decision Time" subheader="Average time to make a decision">
            <Typography variant="h5">{averageDecisionTime}</Typography>
          </Card>
        </Grid>
      </Grid>
    );
  };

  /**
   * Renders the detailed data table with all report data
   */
  const renderDataTable = () => {
    if (!reportData || !reportData.applications) return null;

    // Define table columns based on report data structure
    const columns = [
      { field: 'id', headerName: 'Application ID', width: 150 },
      { field: 'borrowerName', headerName: 'Borrower Name', width: 200 },
      { field: 'schoolName', headerName: 'School Name', width: 200 },
      { field: 'programName', headerName: 'Program Name', width: 200 },
      { field: 'requestedAmount', headerName: 'Requested Amount', width: 150 },
      { field: 'status', headerName: 'Status', width: 150 },
      { field: 'decision', headerName: 'Decision', width: 150 },
    ];

    // Process report data for table display
    const tableData = reportData.applications.map((item: any) => ({
      id: item.id,
      borrowerName: item.borrowerName,
      schoolName: item.schoolName,
      programName: item.programName,
      requestedAmount: item.requestedAmount,
      status: item.status,
      decision: item.decision,
    }));

    return (
      <DataTable
        data={tableData}
        columns={columns}
        loading={loading}
        emptyStateMessage="No data available"
      />
    );
  };

  // Render the page layout with header and action buttons
  return (
    <Page
      title="Underwriting Report"
      description="Generate and view underwriting metrics reports"
      actions={
        <>
          <Tooltip title="Generate Report">
            <IconButton onClick={handleGenerateReport} aria-label="Generate Report">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button variant="contained" startIcon={<DownloadIcon />} onClick={() => handleExportReport('pdf')}>
            Export to PDF
          </Button>
        </>
      }
    >
      <LoadingOverlay isLoading={loading} message="Generating Report..." />

      {/* Report filters section with date range picker and other filters */}
      <Card title="Report Filters">
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <DatePicker
              label="Date Range"
              value={dateRange}
              onChange={handleDateRangeChange}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth variant="outlined">
              <InputLabel id="school-filter-label">School</InputLabel>
              <Select
                labelId="school-filter-label"
                id="school-filter"
                name="schoolId"
                value={filters.schoolId || ''}
                onChange={handleFilterChange}
                label="School"
              >
                <MenuItem value="">
                  <em>All</em>
                </MenuItem>
                {/* TODO: Fetch school options from API */}
                <MenuItem value="school1">ABC School</MenuItem>
                <MenuItem value="school2">XYZ Academy</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth variant="outlined">
              <InputLabel id="underwriter-filter-label">Underwriter</InputLabel>
              <Select
                labelId="underwriter-filter-label"
                id="underwriter-filter"
                name="underwriterId"
                value={filters.underwriterId || ''}
                onChange={handleFilterChange}
                label="Underwriter"
              >
                <MenuItem value="">
                  <em>All</em>
                </MenuItem>
                {/* TODO: Fetch underwriter options from API */}
                <MenuItem value="underwriter1">Robert Taylor</MenuItem>
                <MenuItem value="underwriter2">Jane Doe</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Card>

      {/* Report metrics summary section with key performance indicators */}
      {renderMetricsSummary()}

      {/* Approval rate chart section showing approval trends over time */}
      <Card title="Approval Rate Trend">
        {renderApprovalRateChart()}
      </Card>

      {/* Decision reasons chart section showing distribution of denial reasons */}
      <Card title="Decision Reasons Distribution">
        {renderDecisionReasonsChart()}
      </Card>

      {/* Decision time chart section showing average time to decision */}
      <Card title="Decision Time">
        {renderDecisionTimeChart()}
      </Card>

      {/* Detailed data table section with all report data */}
      <Card title="Application Details">
        {renderDataTable()}
      </Card>
    </Page>
  );
};

export default UnderwritingReport;