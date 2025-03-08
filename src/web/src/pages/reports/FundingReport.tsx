# src/web/src/pages/reports/FundingReport.tsx
```typescript
import React, { useState, useEffect, useCallback } from 'react'; // react v18.2.0
import {
  Grid,
  Typography,
  Button,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
  Box,
  Divider,
  IconButton,
  Tooltip,
} from '@mui/material'; // @mui/material v5.14.0
import { DatePicker, LocalizationProvider, AdapterDateFns } from '@mui/x-date-pickers'; // @mui/x-date-pickers v6.0.0
import {
  BarChart,
  LineChart,
  PieChart,
  ResponsiveContainer,
  Bar,
  Line,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip as ChartTooltip,
  Legend,
} from 'recharts'; // recharts v2.5.0
import DownloadIcon from '@mui/icons-material/Download'; // @mui/icons-material v5.14.0
import RefreshIcon from '@mui/icons-material/Refresh'; // @mui/icons-material v5.14.0
import SaveIcon from '@mui/icons-material/Save'; // @mui/icons-material v5.14.0
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn'; // @mui/icons-material v5.14.0
import { useParams, useNavigate } from 'react-router-dom'; // react-router-dom v6.0.0

import {
  Page,
  Breadcrumbs,
  Card,
  DataTable,
  LoadingOverlay,
} from '../../components/common';
import {
  getFundingMetricsReport,
  getSavedReport,
  exportReport,
  REPORT_TYPES,
} from '../../api/reports';
import {
  FundingRequestStatus,
  DisbursementStatus,
  DisbursementMethod,
} from '../../types/funding.types';
import { DateRange, UUID } from '../../types/common.types';
import { useAuth } from '../../hooks';

/**
 * Interface for funding metrics report parameters
 */
interface FundingMetricsReportParams {
  date_range: DateRange;
  school_id: UUID | null;
  program_id: UUID | null;
  funding_status: FundingRequestStatus | null;
  disbursement_status: DisbursementStatus | null;
  disbursement_method: DisbursementMethod | null;
  group_by: string;
  time_interval: string;
  include_timeline_metrics: boolean;
}

/**
 * Interface for funding metrics report results
 */
interface FundingMetricsReportData {
  volume_metrics: {
    total_funding_requests: number;
    total_disbursements: number;
    total_amount_requested: number;
    total_amount_disbursed: number;
    previous_period_amount: number;
    growth_percentage: number;
  };
  status_distribution: {
    by_funding_status: Record<FundingRequestStatus, number>;
    by_disbursement_status: Record<DisbursementStatus, number>;
    by_disbursement_method: Record<DisbursementMethod, number>;
    percentages: Record<string, number>;
  };
  time_trend: {
    intervals: string[];
    funding_values: number[];
    disbursement_values: number[];
    amount_values: number[];
    by_funding_status: Record<FundingRequestStatus, number[]>;
    by_disbursement_status: Record<DisbursementStatus, number[]>;
  };
  timeline_metrics?: {
    average_time_to_funding: number;
    median_time_to_funding: number;
    time_in_status: Record<FundingRequestStatus, number>;
    disbursement_processing_time: number;
  };
  school_program_breakdown?: {
    schools: object[];
  };
  metadata: {
    generated_at: string;
    parameters: FundingMetricsReportParams;
  };
}

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
 * Formats a number with thousands separators and optional decimal places
 * @param value
 * @param decimals
 * @returns Formatted number string
 */
const formatNumber = (value: number, decimals: number = 0): string => {
  return value.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};

/**
 * Formats a number as currency with dollar sign and two decimal places
 * @param value
 * @returns Formatted currency string
 */
const formatCurrency = (value: number): string => {
  return value.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
  });
};

/**
 * Formats a decimal value as a percentage
 * @param value
 * @param decimals
 * @returns Formatted percentage string
 */
const formatPercentage = (value: number, decimals: number = 2): string => {
  const percentage = value * 100;
  return `${percentage.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })}%`;
};

/**
 * Returns a color code for a given funding request status
 * @param status
 * @returns Color hex code
 */
const getFundingStatusColor = (status: FundingRequestStatus): string => {
  switch (status) {
    case FundingRequestStatus.APPROVED:
      return '#4CAF50'; // Green
    case FundingRequestStatus.DISBURSED:
      return '#2196F3'; // Blue
    case FundingRequestStatus.REJECTED:
      return '#F44336'; // Red
    case FundingRequestStatus.PENDING:
    default:
      return '#FFC107'; // Amber
  }
};

/**
 * Returns a color code for a given disbursement status
 * @param status
 * @returns Color hex code
 */
const getDisbursementStatusColor = (status: DisbursementStatus): string => {
  switch (status) {
    case DisbursementStatus.COMPLETED:
      return '#4CAF50'; // Green
    case DisbursementStatus.FAILED:
      return '#F44336'; // Red
    case DisbursementStatus.PROCESSING:
    default:
      return '#FFC107'; // Amber
  }
};

/**
 * React component for the Funding Report page
 * @returns The rendered component
 */
const FundingReport: React.FC = () => {
  // State variables
  const [reportParams, setReportParams] = useState<FundingMetricsReportParams>({
    date_range: { start: null, end: null },
    school_id: null,
    program_id: null,
    funding_status: null,
    disbursement_status: null,
    disbursement_method: null,
    group_by: 'status',
    time_interval: 'day',
    include_timeline_metrics: true,
  });
  const [reportData, setReportData] = useState<FundingMetricsReportData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<number>(0);

  // Authentication and navigation hooks
  const { state: authState } = useAuth();
  const { id: reportId } = useParams<{ id: string }>();
  const navigate = useNavigate();

  // Load saved report data if reportId is provided
  useEffect(() => {
    const loadSavedReport = async () => {
      if (reportId) {
        setLoading(true);
        try {
          const response = await getSavedReport(reportId as UUID);
          if (response.success && response.data) {
            setReportData(response.data.result_data as FundingMetricsReportData);
            setReportParams(response.data.parameters as FundingMetricsReportParams);
          } else {
            console.error('Failed to load saved report:', response.message);
            navigate('/reports');
          }
        } catch (error) {
          console.error('Error loading saved report:', error);
          navigate('/reports');
        } finally {
          setLoading(false);
        }
      }
    };

    loadSavedReport();
  }, [reportId, navigate]);

  // Handler functions for form field changes
  const handleDateRangeChange = (value: DateRange) => {
    setReportParams({ ...reportParams, date_range: value });
  };

  const handleSchoolChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setReportParams({ ...reportParams, school_id: event.target.value as UUID });
  };

  const handleProgramChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setReportParams({ ...reportParams, program_id: event.target.value as UUID });
  };

  // Handler function for generating the report
  const handleGenerateReport = async () => {
    setLoading(true);
    try {
      const response = await getFundingMetricsReport(reportParams);
      if (response.success && response.data) {
        setReportData(response.data as FundingMetricsReportData);
      } else {
        console.error('Failed to generate report:', response.message);
      }
    } catch (error) {
      console.error('Error generating report:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handler functions for exporting the report
  const handleExportCSV = async () => {
    if (reportData) {
      try {
        const response = await exportReport(reportId as UUID, { format: 'csv' });
        if (response.success && response.data) {
          window.location.href = response.data.download_url;
        } else {
          console.error('Failed to export report to CSV:', response.message);
        }
      } catch (error) {
        console.error('Error exporting report to CSV:', error);
      }
    }
  };

  // Handler for tab changes
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <Page title="Funding Report" description="Generate and view reports on loan funding metrics">
      <Breadcrumbs />
      <LoadingOverlay isLoading={loading} message="Generating Report..." />

      <Card title="Report Parameters">
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Date Range Start"
                value={reportParams.date_range.start}
                onChange={(date) => handleDateRangeChange({ ...reportParams.date_range, start: date })}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </LocalizationProvider>
          </Grid>
          <Grid item xs={12} md={6}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Date Range End"
                value={reportParams.date_range.end}
                onChange={(date) => handleDateRangeChange({ ...reportParams.date_range, end: date })}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </LocalizationProvider>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              select
              label="School"
              value={reportParams.school_id || ''}
              onChange={handleSchoolChange}
              fullWidth
            >
              <MenuItem value="">All Schools</MenuItem>
              {/* Add school options here */}
            </TextField>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              select
              label="Program"
              value={reportParams.program_id || ''}
              onChange={handleProgramChange}
              fullWidth
            >
              <MenuItem value="">All Programs</MenuItem>
              {/* Add program options here */}
            </TextField>
          </Grid>
        </Grid>
        <Box mt={2}>
          <Button variant="contained" color="primary" onClick={handleGenerateReport}>
            Generate Report
          </Button>
        </Box>
      </Card>

      {reportData && (
        <Card title="Report Results">
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={activeTab} onChange={handleTabChange} aria-label="Report tabs">
              <Tab label="Summary" />
              <Tab label="Status Distribution" />
              <Tab label="Time Trend" />
              {reportData.school_program_breakdown && <Tab label="School/Program Breakdown" />}
            </Tabs>
          </Box>

          {activeTab === 0 && (
            <Box mt={2}>
              <Typography variant="h6">Funding Volume Summary</Typography>
              <Divider />
              <Grid container spacing={2} mt={2}>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle1">Total Funding Requests: {formatNumber(reportData.volume_metrics.total_funding_requests)}</Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle1">Total Disbursements: {formatNumber(reportData.volume_metrics.total_disbursements)}</Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle1">Total Amount Requested: {formatCurrency(reportData.volume_metrics.total_amount_requested)}</Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle1">Total Amount Disbursed: {formatCurrency(reportData.volume_metrics.total_amount_disbursed)}</Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle1">Previous Period Amount: {formatCurrency(reportData.volume_metrics.previous_period_amount)}</Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle1">Growth Percentage: {formatPercentage(reportData.volume_metrics.growth_percentage)}</Typography>
                </Grid>
              </Grid>
            </Box>
          )}

          {activeTab === 1 && (
            <Box mt={2}>
              <Typography variant="h6">Funding Status Distribution</Typography>
              <Divider />
              <ResponsiveContainer width="100%" height={400}>
                <PieChart>
                  <Pie
                    data={Object.entries(reportData.status_distribution.by_funding_status).map(([key, value]) => ({
                      name: key,
                      value,
                    }))}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={150}
                    fill="#8884d8"
                    label
                  >
                    {Object.keys(reportData.status_distribution.by_funding_status).map((key, index) => (
                      <Cell key={`cell-${index}`} fill={getFundingStatusColor(key as FundingRequestStatus)} />
                    ))}
                  </Pie>
                  <ChartTooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          )}

          {activeTab === 2 && (
            <Box mt={2}>
              <Typography variant="h6">Disbursement Trend</Typography>
              <Divider />
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={reportData.time_trend.intervals.map((interval, index) => ({
                  interval,
                  funding: reportData.time_trend.funding_values[index],
                  disbursement: reportData.time_trend.disbursement_values[index],
                  amount: reportData.time_trend.amount_values[index],
                }))}>
                  <XAxis dataKey="interval" />
                  <YAxis />
                  <ChartTooltip />
                  <Legend />
                  <Line type="monotone" dataKey="funding" stroke="#8884d8" name="Funding Requests" />
                  <Line type="monotone" dataKey="disbursement" stroke="#82ca9d" name="Disbursements" />
                  <Line type="monotone" dataKey="amount" stroke="#ffc658" name="Disbursed Amount" />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          )}

          {activeTab === 3 && reportData.school_program_breakdown && (
            <Box mt={2}>
              <Typography variant="h6">School/Program Breakdown</Typography>
              <Divider />
              {/* Render school/program breakdown data here */}
            </Box>
          )}

          <Box mt={2} display="flex" justifyContent="flex-end">
            <Button variant="contained" color="primary" startIcon={<DownloadIcon />} onClick={handleExportCSV}>
              Export CSV
            </Button>
          </Box>
        </Card>
      )}
    </Page>
  );
};

export default FundingReport;