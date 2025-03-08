import React, { useState, useEffect, useCallback } from 'react';
import {
  Grid,
  Typography,
  Button,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  FormHelperText,
  Tabs,
  Tab,
  Box,
  Divider,
  IconButton,
  Tooltip,
} from '@mui/material'; // @mui/material ^5.14.0
import { DatePicker, LocalizationProvider, AdapterDateFns } from '@mui/x-date-pickers'; // @mui/x-date-pickers ^6.0.0
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
} from 'recharts'; // recharts ^2.5.0
import DownloadIcon from '@mui/icons-material/Download'; // @mui/icons-material ^5.14.0
import RefreshIcon from '@mui/icons-material/Refresh'; // @mui/icons-material ^5.14.0
import SaveIcon from '@mui/icons-material/Save'; // @mui/icons-material ^5.14.0
import BarChartIcon from '@mui/icons-material/BarChart'; // @mui/icons-material ^5.14.0
import { useParams, useNavigate } from 'react-router-dom'; // react-router-dom ^6.0.0

import {
  Page,
  Breadcrumbs,
  Card,
  DataTable,
  LoadingOverlay,
} from '../../components/common';
import {
  getApplicationVolumeReport,
  getSavedReport,
  exportReport,
  REPORT_TYPES,
} from '../../api/reports';
import { ApplicationStatus, DateRange, UUID } from '../../types';
import { useAuth } from '../../hooks';

/**
 * Interface for application volume report parameters
 */
interface ApplicationVolumeReportParams {
  date_range: DateRange;
  school_id: UUID | null;
  program_id: UUID | null;
  application_type: string | null;
  group_by: string;
  time_interval: string;
  include_processing_time: boolean;
}

/**
 * Interface for application volume report results
 */
interface ApplicationVolumeReportData {
  volume_metrics: {
    total_applications: number;
    previous_period: number;
    growth_percentage: number;
    average_volume: number;
  };
  status_distribution: {
    by_status: Record<ApplicationStatus, number>;
    by_group: Record<string, number>;
    percentages: Record<ApplicationStatus, number>;
  };
  time_trend: {
    intervals: string[];
    values: number[];
    by_status: Record<ApplicationStatus, number[]>;
  };
  processing_time?: {
    average_time_to_decision: number;
    median_time_to_decision: number;
    time_in_status: Record<ApplicationStatus, number>;
  };
  conversion_rates: {
    submission_rate: number;
    approval_rate: number;
    funding_rate: number;
    completion_rate: number;
  };
  school_program_breakdown?: {
    schools: object[];
  };
  metadata: {
    generated_at: string;
    parameters: ApplicationVolumeReportParams;
  };
}

/**
 * Formats a date string into a human-readable format
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
 */
const formatNumber = (value: number, decimals: number = 0): string => {
  return value.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};

/**
 * Formats a decimal value as a percentage
 */
const formatPercentage = (value: number, decimals: number = 2): string => {
  return (value * 100).toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }) + '%';
};

/**
 * Returns a color code for a given application status
 */
const getStatusColor = (status: ApplicationStatus): string => {
  switch (status) {
    case ApplicationStatus.APPROVED:
      return '#4CAF50'; // Green
    case ApplicationStatus.DENIED:
      return '#F44336'; // Red
    case ApplicationStatus.SUBMITTED:
      return '#2196F3'; // Blue
    case ApplicationStatus.IN_REVIEW:
      return '#FFC107'; // Amber
    default:
      return '#9E9E9E'; // Grey
  }
};

/**
 * Groups application statuses into logical categories
 */
const getStatusGroup = (status: ApplicationStatus): string => {
  if ([ApplicationStatus.DRAFT, ApplicationStatus.SUBMITTED].includes(status)) {
    return 'New';
  }
  if ([ApplicationStatus.IN_REVIEW, ApplicationStatus.REVISION_REQUESTED].includes(status)) {
    return 'In Progress';
  }
  if ([
    ApplicationStatus.APPROVED,
    ApplicationStatus.COMMITMENT_SENT,
    ApplicationStatus.COMMITMENT_ACCEPTED,
    ApplicationStatus.COUNTER_OFFER_MADE,
  ].includes(status)) {
    return 'Approved';
  }
  if ([ApplicationStatus.DENIED, ApplicationStatus.COMMITMENT_DECLINED].includes(status)) {
    return 'Declined';
  }
  if ([
    ApplicationStatus.ABANDONED,
    ApplicationStatus.INCOMPLETE,
    ApplicationStatus.DOCUMENTS_EXPIRED,
  ].includes(status)) {
    return 'Abandoned';
  }
  return 'Other';
};

/**
 * React component for the Application Volume Report page
 */
const ApplicationVolumeReport: React.FC = () => {
  // Define state variables
  const [reportParams, setReportParams] = useState<ApplicationVolumeReportParams>({
    date_range: { start: null, end: null },
    school_id: null,
    program_id: null,
    application_type: null,
    group_by: 'status',
    time_interval: 'day',
    include_processing_time: true,
  });
  const [reportData, setReportData] = useState<ApplicationVolumeReportData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<number>(0);

  // Get authentication context
  const { state: authState } = useAuth();
  const user = authState.user;

  // Get report ID from URL params
  const { id: reportId } = useParams<{ id: string }>();

  // Get navigate function
  const navigate = useNavigate();

  // Load saved report data if report ID is provided
  useEffect(() => {
    const loadSavedReport = async () => {
      if (reportId) {
        setLoading(true);
        try {
          const response = await getSavedReport(reportId as UUID);
          if (response.success && response.data) {
            setReportData(response.data.result_data as ApplicationVolumeReportData);
            setReportParams(response.data.parameters as ApplicationVolumeReportParams);
          } else {
            console.error('Failed to load saved report:', response.message);
            // Redirect to reports dashboard on failure
            navigate('/reports');
          }
        } catch (error) {
          console.error('Error loading saved report:', error);
        } finally {
          setLoading(false);
        }
      }
    };

    loadSavedReport();
  }, [reportId, navigate]);

  // Handler for form field changes
  const handleInputChange = (field: string, value: any) => {
    setReportParams((prevParams) => ({
      ...prevParams,
      [field]: value,
    }));
  };

  // Handler for generating the report
  const handleGenerateReport = async () => {
    setLoading(true);
    try {
      const response = await getApplicationVolumeReport(reportParams);
      if (response.success && response.data) {
        setReportData(response.data as ApplicationVolumeReportData);
      } else {
        console.error('Failed to generate report:', response.message);
      }
    } catch (error) {
      console.error('Error generating report:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handler for exporting the report
  const handleExportReport = async (format: string) => {
    if (!reportData) return;

    setLoading(true);
    try {
      // Assuming reportId is available or can be constructed
      const response = await exportReport(reportId as UUID, { format });
      if (response.success && response.data) {
        // Trigger download
        window.location.href = response.data.download_url;
      } else {
        console.error('Failed to export report:', response.message);
      }
    } catch (error) {
      console.error('Error exporting report:', error);
    } finally {
      setLoading(false);
    }
  };

  // Breadcrumbs navigation items
  const breadcrumbs = [
    { path: '/reports', label: 'Reports' },
    { path: '/reports/application-volume', label: 'Application Volume Report' },
  ];

  return (
    <Page title="Application Volume Report">
      <Breadcrumbs breadcrumbs={breadcrumbs} />

      <Card title="Report Parameters">
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Start Date"
                value={reportParams.date_range.start}
                onChange={(date) => handleInputChange('date_range', { ...reportParams.date_range, start: date })}
                renderInput={(params) => <TextField {...params} fullWidth size="small" />}
              />
            </LocalizationProvider>
          </Grid>
          <Grid item xs={12} md={4}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="End Date"
                value={reportParams.date_range.end}
                onChange={(date) => handleInputChange('date_range', { ...reportParams.date_range, end: date })}
                renderInput={(params) => <TextField {...params} fullWidth size="small" />}
              />
            </LocalizationProvider>
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth variant="outlined" size="small">
              <InputLabel id="group-by-label">Group By</InputLabel>
              <Select
                labelId="group-by-label"
                value={reportParams.group_by}
                onChange={(e) => handleInputChange('group_by', e.target.value)}
                label="Group By"
              >
                <MenuItem value="status">Status</MenuItem>
                <MenuItem value="school">School</MenuItem>
                <MenuItem value="program">Program</MenuItem>
              </Select>
            </FormControl>
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
            <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)} aria-label="Report tabs">
              <Tab label="Summary" />
              <Tab label="Status Distribution" />
              <Tab label="Time Trend" />
            </Tabs>
          </Box>

          {activeTab === 0 && (
            <Box p={3}>
              <Typography variant="h6">Application Volume Summary</Typography>
              <Typography>Total Applications: {formatNumber(reportData.volume_metrics.total_applications)}</Typography>
              <Typography>Previous Period: {formatNumber(reportData.volume_metrics.previous_period)}</Typography>
              <Typography>Growth: {formatPercentage(reportData.volume_metrics.growth_percentage)}</Typography>
              <Typography>Average Volume: {formatNumber(reportData.volume_metrics.average_volume)}</Typography>
            </Box>
          )}

          {activeTab === 1 && (
            <Box p={3}>
              <Typography variant="h6">Status Distribution</Typography>
              <ResponsiveContainer width="100%" height={400}>
                <PieChart>
                  <Pie
                    data={Object.entries(reportData.status_distribution.by_status).map(([status, value]) => ({
                      name: status,
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
                    {Object.keys(reportData.status_distribution.by_status).map((status, index) => (
                      <Cell key={`cell-${index}`} fill={getStatusColor(status as ApplicationStatus)} />
                    ))}
                  </Pie>
                  <ChartTooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          )}

          {activeTab === 2 && (
            <Box p={3}>
              <Typography variant="h6">Time Trend</Typography>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={reportData.time_trend.intervals.map((interval, index) => ({
                  name: interval,
                  value: reportData.time_trend.values[index],
                }))}>
                  <XAxis dataKey="name" />
                  <YAxis />
                  <ChartTooltip />
                  <Legend />
                  <Line type="monotone" dataKey="value" stroke="#8884d8" activeDot={{ r: 8 }} />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          )}

          <Box mt={2} display="flex" justifyContent="flex-end">
            <Button
              variant="contained"
              color="primary"
              startIcon={<DownloadIcon />}
              onClick={() => handleExportReport('csv')}
            >
              Export CSV
            </Button>
            <Button
              variant="contained"
              color="primary"
              startIcon={<DownloadIcon />}
              onClick={() => handleExportReport('excel')}
              sx={{ ml: 1 }}
            >
              Export Excel
            </Button>
            <Button
              variant="contained"
              color="primary"
              startIcon={<DownloadIcon />}
              onClick={() => handleExportReport('pdf')}
              sx={{ ml: 1 }}
            >
              Export PDF
            </Button>
          </Box>
        </Card>
      )}

      <LoadingOverlay isLoading={loading} message="Generating Report..." />
    </Page>
  );
};

export default ApplicationVolumeReport;