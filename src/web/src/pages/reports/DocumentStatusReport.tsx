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
  Tooltip
} from '@mui/material'; // Material UI v5.14.0
import {
  DatePicker,
  LocalizationProvider,
  AdapterDateFns,
} from '@mui/x-date-pickers'; // MUI X Date Pickers v6.0.0
import {
  BarChart,
  PieChart,
  ResponsiveContainer,
  Bar,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip as ChartTooltip,
  Legend,
} from 'recharts'; // Recharts v2.5.0
import DownloadIcon from '@mui/icons-material/Download'; // Material UI Icons v5.14.0
import RefreshIcon from '@mui/icons-material/Refresh'; // Material UI Icons v5.14.0
import SaveIcon from '@mui/icons-material/Save'; // Material UI Icons v5.14.0
import DescriptionIcon from '@mui/icons-material/Description'; // Material UI Icons v5.14.0
import { useParams, useNavigate } from 'react-router-dom'; // React Router v6.0.0

import {
  Page,
  Breadcrumbs,
  Card,
  DataTable,
  LoadingOverlay,
} from '../../components/common';
import {
  getDocumentStatusReport,
  getSavedReport,
  exportReport,
  REPORT_TYPES,
} from '../../api/reports';
import {
  DocumentType,
  DocumentStatus,
  DateRange,
  UUID,
} from '../../types';
import { useAuth } from '../../hooks';

/**
 * Interface for document status report parameters
 */
interface DocumentStatusReportParams {
  date_range: DateRange;
  document_type: DocumentType | null;
  document_status: DocumentStatus | null;
  school_id: UUID | null;
  application_id: UUID | null;
  group_by: string;
  include_signature_metrics: boolean;
  include_expiration_analysis: boolean;
}

/**
 * Interface for document status report results
 */
interface DocumentStatusReportData {
  status_metrics: {
    total_documents: number;
    completed_documents: number;
    pending_documents: number;
    expired_documents: number;
    completion_rate: number;
  };
  status_distribution: {
    by_status: Record<DocumentStatus, number>;
    percentages: Record<DocumentStatus, number>;
  };
  type_distribution: {
    by_type: Record<DocumentType, number>;
    by_type_and_status: Record<DocumentType, Record<DocumentStatus, number>>;
  };
  signature_metrics?: {
    average_time_to_signature: number;
    signature_completion_rate: number;
    average_reminders_sent: number;
    by_signer_type: Record<string, object>;
  };
  expiration_analysis?: {
    at_risk_documents: number;
    expiring_soon: number;
    expired_documents: number;
    expiration_rate: number;
  };
  school_breakdown?: {
    schools: object[];
  };
  metadata: {
    generated_at: string;
    parameters: DocumentStatusReportParams;
  };
}

/**
 * Formats a date string into a human-readable format
 * @param dateString 
 * @returns 
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
 * @returns 
 */
const formatNumber = (value: number, decimals: number = 0): string => {
  return value.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};

/**
 * Formats a decimal value as a percentage
 * @param value 
 * @param decimals 
 * @returns 
 */
const formatPercentage = (value: number, decimals: number = 2): string => {
  const percentage = value * 100;
  return `${percentage.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })}%`;
};

/**
 * Returns a color code for a given document status
 * @param status 
 * @returns 
 */
const getDocumentStatusColor = (status: DocumentStatus): string => {
  switch (status) {
    case DocumentStatus.COMPLETED:
      return '#4CAF50'; // Green
    case DocumentStatus.PENDING_SIGNATURE:
      return '#FFC107'; // Amber
    case DocumentStatus.EXPIRED:
      return '#F44336'; // Red
    case DocumentStatus.REJECTED:
      return '#9E9E9E'; // Grey
    default:
      return '#90CAF9'; // Light Blue
  }
};

/**
 * Returns a human-readable label for a document type
 * @param type 
 * @returns 
 */
const getDocumentTypeLabel = (type: DocumentType): string => {
  switch (type) {
    case DocumentType.COMMITMENT_LETTER:
      return 'Commitment Letter';
    case DocumentType.LOAN_AGREEMENT:
      return 'Loan Agreement';
    case DocumentType.DISCLOSURE_FORM:
      return 'Disclosure Form';
    case DocumentType.PROMISSORY_NOTE:
      return 'Promissory Note';
    case DocumentType.TRUTH_IN_LENDING:
      return 'Truth in Lending';
    case DocumentType.ENROLLMENT_AGREEMENT:
      return 'Enrollment Agreement';
    case DocumentType.IDENTIFICATION:
      return 'Identification';
    case DocumentType.INCOME_VERIFICATION:
      return 'Income Verification';
    default:
      return 'Other Document';
  }
};

/**
 * React component for the Document Status Report page
 */
const DocumentStatusReport: React.FC = () => {
  // State variables
  const [reportParams, setReportParams] = useState<DocumentStatusReportParams>({
    date_range: { start: null, end: null },
    document_type: null,
    document_status: null,
    school_id: null,
    application_id: null,
    group_by: 'status',
    include_signature_metrics: true,
    include_expiration_analysis: true,
  });
  const [reportData, setReportData] = useState<DocumentStatusReportData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<number>(0);

  // Authentication context
  const { state } = useAuth();

  // URL parameters and navigation
  const { id: reportId } = useParams<{ id: string }>();
  const navigate = useNavigate();

  /**
   * Loads saved report data if a report ID is provided
   */
  useEffect(() => {
    const loadSavedReport = async () => {
      if (reportId) {
        setLoading(true);
        try {
          const response = await getSavedReport(reportId as UUID);
          if (response.success && response.data) {
            setReportData(response.data as DocumentStatusReportData);
            setReportParams(response.data.parameters);
          } else {
            console.error('Failed to load saved report:', response.message);
            // Redirect to report dashboard on failure
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

  /**
   * Handles form field changes
   */
  const handleInputChange = (field: keyof DocumentStatusReportParams, value: any) => {
    setReportParams((prevParams) => ({
      ...prevParams,
      [field]: value,
    }));
  };

  /**
   * Handles report generation
   */
  const handleGenerateReport = async () => {
    setLoading(true);
    try {
      const response = await getDocumentStatusReport(reportParams);
      if (response.success && response.data) {
        setReportData(response.data as DocumentStatusReportData);
      } else {
        console.error('Failed to generate report:', response.message);
      }
    } catch (error) {
      console.error('Error generating report:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handles report export in different formats
   */
  const handleExportReport = async (format: string) => {
    if (!reportData?.metadata?.parameters) return;

    setLoading(true);
    try {
      // TODO: Implement exportReport API call
      // const response = await exportReport(reportId, { format });
      // if (response.success && response.data) {
      //   // Trigger download
      //   window.location.href = response.data.download_url;
      // } else {
      //   console.error('Failed to export report:', response.message);
      // }
      console.log(`Exporting report in ${format} format`);
    } catch (error) {
      console.error('Error exporting report:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Page
      title="Document Status Report"
      description="Generate, view, and export reports on document status metrics."
    >
      <Breadcrumbs>Document Status Report</Breadcrumbs>

      <Card title="Report Parameters">
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Date Range Start"
                value={reportParams.date_range.start}
                onChange={(date) => handleInputChange('date_range', { ...reportParams.date_range, start: date })}
                renderInput={(params) => <TextField {...params} fullWidth size="small" />}
              />
            </LocalizationProvider>
          </Grid>
          <Grid item xs={12} md={4}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Date Range End"
                value={reportParams.date_range.end}
                onChange={(date) => handleInputChange('date_range', { ...reportParams.date_range, end: date })}
                renderInput={(params) => <TextField {...params} fullWidth size="small" />}
              />
            </LocalizationProvider>
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth size="small" variant="outlined">
              <InputLabel id="document-type-label">Document Type</InputLabel>
              <Select
                labelId="document-type-label"
                value={reportParams.document_type || ''}
                onChange={(e) => handleInputChange('document_type', e.target.value as DocumentType)}
                label="Document Type"
              >
                <MenuItem value=""><em>All</em></MenuItem>
                <MenuItem value={DocumentType.LOAN_AGREEMENT}>Loan Agreement</MenuItem>
                <MenuItem value={DocumentType.COMMITMENT_LETTER}>Commitment Letter</MenuItem>
                {/* Add other document types here */}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth size="small" variant="outlined">
              <InputLabel id="document-status-label">Document Status</InputLabel>
              <Select
                labelId="document-status-label"
                value={reportParams.document_status || ''}
                onChange={(e) => handleInputChange('document_status', e.target.value as DocumentStatus)}
                label="Document Status"
              >
                <MenuItem value=""><em>All</em></MenuItem>
                <MenuItem value={DocumentStatus.COMPLETED}>Completed</MenuItem>
                <MenuItem value={DocumentStatus.PENDING_SIGNATURE}>Pending Signature</MenuItem>
                {/* Add other document statuses here */}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleGenerateReport}
              startIcon={<DescriptionIcon />}
            >
              Generate Report
            </Button>
          </Grid>
        </Grid>
      </Card>

      {reportData && (
        <Card title="Report Results">
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
            <Tab label="Summary" />
            <Tab label="Status Distribution" />
            <Tab label="Type Breakdown" />
            {reportData.signature_metrics && <Tab label="Signature Metrics" />}
            {reportData.expiration_analysis && <Tab label="Expiration Analysis" />}
          </Tabs>

          <Box sx={{ mt: 2 }}>
            {activeTab === 0 && (
              <>
                <Typography variant="h6">Document Status Summary</Typography>
                <Divider sx={{ my: 1 }} />
                <Grid container spacing={2}>
                  <Grid item xs={6} md={3}>
                    <Typography variant="subtitle2">Total Documents:</Typography>
                    <Typography variant="body1">{formatNumber(reportData.status_metrics.total_documents)}</Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="subtitle2">Completed Documents:</Typography>
                    <Typography variant="body1">{formatNumber(reportData.status_metrics.completed_documents)}</Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="subtitle2">Pending Documents:</Typography>
                    <Typography variant="body1">{formatNumber(reportData.status_metrics.pending_documents)}</Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="subtitle2">Expired Documents:</Typography>
                    <Typography variant="body1">{formatNumber(reportData.status_metrics.expired_documents)}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2">Completion Rate:</Typography>
                    <Typography variant="body1">{formatPercentage(reportData.status_metrics.completion_rate)}</Typography>
                  </Grid>
                </Grid>
              </>
            )}

            {activeTab === 1 && (
              <>
                <Typography variant="h6">Status Distribution</Typography>
                <Divider sx={{ my: 1 }} />
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={Object.entries(reportData.status_distribution.by_status).map(([status, count]) => ({
                        name: status,
                        value: count,
                      }))}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      label
                    >
                      {Object.keys(reportData.status_distribution.by_status).map((status, index) => (
                        <Cell key={`cell-${index}`} fill={getDocumentStatusColor(status as DocumentStatus)} />
                      ))}
                    </Pie>
                    <ChartTooltip formatter={(value) => formatNumber(value)} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </>
            )}

            {activeTab === 2 && (
              <>
                <Typography variant="h6">Document Type Breakdown</Typography>
                <Divider sx={{ my: 1 }} />
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={Object.entries(reportData.type_distribution.by_type).map(([type, count]) => ({
                    name: getDocumentTypeLabel(type as DocumentType),
                    value: count,
                  }))}>
                    <XAxis dataKey="name" />
                    <YAxis />
                    <ChartTooltip formatter={(value) => formatNumber(value)} />
                    <Legend />
                    <Bar dataKey="value" fill="#82ca9d" />
                  </BarChart>
                </ResponsiveContainer>
              </>
            )}

            {activeTab === 3 && reportData.signature_metrics && (
              <>
                <Typography variant="h6">Signature Completion Metrics</Typography>
                <Divider sx={{ my: 1 }} />
                <Grid container spacing={2}>
                  <Grid item xs={6} md={4}>
                    <Typography variant="subtitle2">Average Time to Signature:</Typography>
                    <Typography variant="body1">{formatNumber(reportData.signature_metrics.average_time_to_signature)} days</Typography>
                  </Grid>
                  <Grid item xs={6} md={4}>
                    <Typography variant="subtitle2">Signature Completion Rate:</Typography>
                    <Typography variant="body1">{formatPercentage(reportData.signature_metrics.signature_completion_rate)}</Typography>
                  </Grid>
                  <Grid item xs={6} md={4}>
                    <Typography variant="subtitle2">Average Reminders Sent:</Typography>
                    <Typography variant="body1">{formatNumber(reportData.signature_metrics.average_reminders_sent)}</Typography>
                  </Grid>
                </Grid>
              </>
            )}

            {activeTab === 4 && reportData.expiration_analysis && (
              <>
                <Typography variant="h6">Expiration Risk Analysis</Typography>
                <Divider sx={{ my: 1 }} />
                <Grid container spacing={2}>
                  <Grid item xs={6} md={3}>
                    <Typography variant="subtitle2">At-Risk Documents:</Typography>
                    <Typography variant="body1">{formatNumber(reportData.expiration_analysis.at_risk_documents)}</Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="subtitle2">Expiring Soon:</Typography>
                    <Typography variant="body1">{formatNumber(reportData.expiration_analysis.expiring_soon)}</Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="subtitle2">Expired Documents:</Typography>
                    <Typography variant="body1">{formatNumber(reportData.expiration_analysis.expired_documents)}</Typography>
                  </Grid>
                  <Grid item xs={6} md={3}>
                    <Typography variant="subtitle2">Expiration Rate:</Typography>
                    <Typography variant="body1">{formatPercentage(reportData.expiration_analysis.expiration_rate)}</Typography>
                  </Grid>
                </Grid>
              </>
            )}
          </Box>

          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
            <Tooltip title="Refresh Report">
              <IconButton onClick={handleGenerateReport} aria-label="Refresh Report">
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Export to CSV">
              <IconButton onClick={() => handleExportReport('csv')} aria-label="Export to CSV">
                <DownloadIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Export to Excel">
              <IconButton onClick={() => handleExportReport('excel')} aria-label="Export to Excel">
                <DownloadIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Export to PDF">
              <IconButton onClick={() => handleExportReport('pdf')} aria-label="Export to PDF">
                <DownloadIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Card>
      )}

      <LoadingOverlay isLoading={loading} message="Generating Report..." />
    </Page>
  );
};

export default DocumentStatusReport;