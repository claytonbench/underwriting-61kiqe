import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux'; // react-redux v8.0.5
import { useNavigate } from 'react-router-dom'; // react-router-dom v6.4.3
import {
  Card,
  CardContent,
  CardHeader,
  Grid,
  Typography,
  Button,
  Box,
  Divider,
  Chip
} from '@mui/material'; // @mui/material v5.14.5
import {
  AssignmentOutlined,
  AccessTimeOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  TrendingUpOutlined,
  VisibilityOutlined,
  EditOutlined
} from '@mui/icons-material'; // @mui/icons-material v5.14.5

import Page from '../../components/common/Page';
import DataTable from '../../components/common/DataTable';
import {
  fetchUnderwritingQueue,
  fetchAssignedApplications,
  fetchMetrics
} from '../../store/thunks/underwritingThunks';
import {
  setFilters,
  setSort,
  setPage,
  setPageSize
} from '../../store/slices/underwritingSlice';
import { RootState } from '../../store';
import {
  UnderwritingQueueItem,
  UnderwritingQueueSortField,
  UnderwritingQueueFilters,
  UnderwritingQueueSort,
  SortDirection,
  UnderwritingMetrics,
  UnderwritingQueuePriority,
  UnderwritingQueueStatus
} from '../../types/underwriting.types';
import { formatCurrency, formatDate } from '../../utils/formatting';
import useStyles from './styles';

/**
 * Custom styles hook for the UnderwriterDashboard component
 * @returns Object containing styled components and CSS classes
 */
const useStyles = () => {
  return {
    metricCard: {
      padding: '16px',
      boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.1)',
    },
    metricValue: {
      fontSize: '2rem',
      fontWeight: 500,
      marginBottom: '4px',
    },
    statusChip: {
      marginRight: '4px',
      marginBottom: '4px',
    },
    priorityChip: {
      marginRight: '4px',
      marginBottom: '4px',
    },
  };
};

/**
 * Returns the appropriate color for priority indicators
 * @param priority - UnderwritingQueuePriority
 * @returns Color code for the priority level
 */
const getPriorityColor = (priority: UnderwritingQueuePriority): string => {
  switch (priority) {
    case UnderwritingQueuePriority.HIGH:
      return 'error';
    case UnderwritingQueuePriority.MEDIUM:
      return 'warning';
    case UnderwritingQueuePriority.LOW:
      return 'info';
    default:
      return 'default';
  }
};

/**
 * Returns the appropriate color for status indicators
 * @param status - UnderwritingQueueStatus
 * @returns Color code for the status
 */
const getStatusColor = (status: UnderwritingQueueStatus): string => {
  switch (status) {
    case UnderwritingQueueStatus.PENDING:
      return 'warning';
    case UnderwritingQueueStatus.ASSIGNED:
      return 'info';
    case UnderwritingQueueStatus.IN_PROGRESS:
      return 'primary';
    case UnderwritingQueueStatus.COMPLETED:
      return 'success';
    case UnderwritingQueueStatus.RETURNED:
      return 'error';
    default:
      return 'default';
  }
};

/**
 * Handles navigation to application review page
 * @param application - UnderwritingQueueItem
 */
const handleViewApplication = (application: UnderwritingQueueItem, navigate: any): void => {
  navigate(`/underwriting/applications/${application.application_id}`);
};

/**
 * Handles changes to queue filters
 * @param filters - UnderwritingQueueFilters
 */
const handleFilterChange = (filters: UnderwritingQueueFilters, dispatch: any): void => {
  dispatch(setFilters(filters));
  dispatch(fetchUnderwritingQueue());
};

/**
 * Handles changes to queue sorting
 * @param field - string
 * @param direction - SortDirection
 */
const handleSortChange = (field: string, direction: SortDirection, dispatch: any): void => {
  const sort: UnderwritingQueueSort = {
    field: field as UnderwritingQueueSortField,
    direction: direction
  };
  dispatch(setSort(sort));
  dispatch(fetchUnderwritingQueue());
};

/**
 * Handles pagination page changes
 * @param page - number
 */
const handlePageChange = (page: number, dispatch: any): void => {
  dispatch(setPage(page));
  dispatch(fetchUnderwritingQueue());
};

/**
 * Handles changes to number of items per page
 * @param pageSize - number
 */
const handlePageSizeChange = (pageSize: number, dispatch: any): void => {
  dispatch(setPageSize(pageSize));
  dispatch(fetchUnderwritingQueue());
};

/**
 * Handles switching to view assigned applications
 */
const handleViewAssigned = (setViewAssigned: any, dispatch: any): void => {
  setViewAssigned(true);
  dispatch(fetchAssignedApplications());
};

/**
 * Handles switching to view all applications in queue
 */
const handleViewAll = (setViewAssigned: any, dispatch: any): void => {
  setViewAssigned(false);
  dispatch(fetchUnderwritingQueue());
};

/**
 * Renders the metrics cards section of the dashboard
 * @returns Rendered metrics cards grid
 */
const renderMetricsCards = (metrics: any) => {
  const classes = useStyles();

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} sm={6} md={4} lg={3}>
        <Card className={classes.metricCard}>
          <CardHeader title="Assigned Applications" avatar={<AssignmentOutlined />} />
          <CardContent>
            <Typography variant="h5" className={classes.metricValue}>
              {metrics?.assigned_to_me || 0}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={4} lg={3}>
        <Card className={classes.metricCard}>
          <CardHeader title="Pending Review" avatar={<AccessTimeOutlined />} />
          <CardContent>
            <Typography variant="h5" className={classes.metricValue}>
              {metrics?.pending_review || 0}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={4} lg={3}>
        <Card className={classes.metricCard}>
          <CardHeader title="Completed Today" avatar={<CheckCircleOutlined />} />
          <CardContent>
            <Typography variant="h5" className={classes.metricValue}>
              {metrics?.completed_today || 0}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={4} lg={3}>
        <Card className={classes.metricCard}>
          <CardHeader title="Average Decision Time" avatar={<TrendingUpOutlined />} />
          <CardContent>
            <Typography variant="h5" className={classes.metricValue}>
              {metrics?.average_decision_time ? `${metrics.average_decision_time.toFixed(1)} days` : 'N/A'}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

/**
 * Renders the applications data table
 * @returns Rendered applications table
 */
const renderApplicationsTable = (queueItems: any, loading: any, handleViewApplication: any) => {
  const classes = useStyles();

  const columns = [
    { field: 'application_id', headerName: 'Application ID', width: 150 },
    { field: 'borrower_name', headerName: 'Borrower Name', width: 200 },
    { field: 'school_name', headerName: 'School', width: 150 },
    { field: 'program_name', headerName: 'Program', width: 150 },
    { field: 'requested_amount', headerName: 'Amount', width: 120, align: 'right', render: (value: any) => formatCurrency(value) },
    { field: 'submission_date', headerName: 'Submission Date', width: 150, render: (value: any) => formatDate(value) },
    {
      field: 'priority',
      headerName: 'Priority',
      width: 120,
      render: (value: any) => (
        <Chip label={value} color={getPriorityColor(value)} className={classes.priorityChip} />
      ),
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      render: (value: any) => (
        <Chip label={value} color={getStatusColor(value)} className={classes.statusChip} />
      ),
    },
  ];

  const actions = [
    {
      icon: <VisibilityOutlined />,
      label: 'View',
      onClick: (row: any) => handleViewApplication(row),
    },
  ];

  return (
    <DataTable
      data={queueItems}
      columns={columns}
      loading={loading}
      actions={actions}
    />
  );
};

/**
 * Main component for the underwriter dashboard page
 * @returns Rendered underwriter dashboard page
 */
const UnderwriterDashboard: React.FC = () => {
  const [viewAssigned, setViewAssigned] = useState(false);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { queueItems, loading, metrics } = useSelector((state: RootState) => state.underwriting);

  useEffect(() => {
    dispatch(fetchUnderwritingQueue());
    dispatch(fetchMetrics());
  }, [dispatch]);

  return (
    <Page title="Underwriter Dashboard">
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Applications Queue</Typography>
        <Box>
          <Button
            variant={viewAssigned ? 'outlined' : 'contained'}
            color="primary"
            onClick={() => handleViewAll(setViewAssigned, dispatch)}
            style={{ marginRight: '10px' }}
          >
            All Applications
          </Button>
          <Button
            variant={viewAssigned ? 'contained' : 'outlined'}
            color="primary"
            onClick={() => handleViewAssigned(setViewAssigned, dispatch)}
          >
            My Assigned
          </Button>
        </Box>
      </Box>
      <Divider style={{ marginBottom: '20px' }} />

      {renderMetricsCards(metrics)}

      <Box mt={3}>
        {renderApplicationsTable(queueItems, loading, (row: any) => handleViewApplication(row, navigate))}
      </Box>
    </Page>
  );
};

export default UnderwriterDashboard;