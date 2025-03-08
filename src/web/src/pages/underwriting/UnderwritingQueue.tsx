# src/web/src/pages/underwriting/UnderwritingQueue.tsx
```typescript
import React, { useState, useEffect, useMemo, useCallback } from 'react'; // react v18.2.0
import { useDispatch, useSelector } from 'react-redux'; // react-redux v8.1.1
import { useNavigate } from 'react-router-dom'; // react-router-dom v6.14.2
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  IconButton,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  TextField,
  Divider,
  Tooltip
} from '@mui/material'; // @mui/material v5.14.0
import {
  VisibilityIcon,
  EditIcon,
  AssignmentIcon,
  AssignmentIndIcon,
  FilterListIcon,
  SortIcon,
  RefreshIcon,
  PriorityHighIcon
} from '@mui/icons-material'; // @mui/icons-material v5.14.0
import { format } from 'date-fns'; // date-fns v2.30.0

import Page from '../../components/common/Page';
import DataTable from '../../components/common/DataTable';
import StatusBadge from '../../components/common/StatusBadge';
import {
  fetchUnderwritingQueue,
  fetchAssignedApplications,
  assignApplicationToUnderwriter,
  startReviewingApplication,
  fetchMetrics
} from '../../store/thunks/underwritingThunks';
import { setFilters, setSort, setPage, setPageSize } from '../../store/slices/underwritingSlice';
import { RootState } from '../../store';
import {
  UnderwritingQueueItem,
  UnderwritingQueueFilters,
  UnderwritingQueueSort,
  UnderwritingQueueSortField,
  SortDirection,
  UnderwritingQueueStatus,
  UnderwritingQueuePriority
} from '../../types/underwriting.types';
import { ROUTES } from '../../config/routes';

/**
 * Formats a number as a currency string
 * @param value - Number to format
 * @returns Formatted currency string
 */
const formatCurrency = (value: number | undefined): string => {
  if (!value) return '-';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value);
};

/**
 * Formats a date string into a readable format
 * @param dateString - Date string to format
 * @returns Formatted date string
 */
const formatDate = (dateString: string | undefined): string => {
  if (!dateString) return '-';
  return format(new Date(dateString), 'MM/dd/yyyy');
};

/**
 * Handles the action to view an application's details
 * @param application - The application to view
 */
const handleViewApplication = (application: UnderwritingQueueItem, navigate: any) => {
  navigate(ROUTES.UNDERWRITING.REVIEW(application.application_id));
};

/**
 * Handles the action to assign an application to the current underwriter
 * @param application - The application to assign
 */
const handleAssignToMe = (application: UnderwritingQueueItem, dispatch: any, auth: any) => {
  const underwriterId = auth.user?.id;
  if (underwriterId) {
    dispatch(assignApplicationToUnderwriter({ queue_id: application.queue_id, underwriter_id: underwriterId }));
  }
};

/**
 * Handles the action to start reviewing an application
 * @param application - The application to start reviewing
 */
const handleStartReview = (application: UnderwritingQueueItem, dispatch: any, navigate: any) => {
  dispatch(startReviewingApplication(application.queue_id));
  navigate(ROUTES.UNDERWRITING.REVIEW(application.application_id));
};

/**
 * Handles changes to the filter criteria
 * @param newFilters - The new filter values
 */
const handleFilterChange = (newFilters: Partial<UnderwritingQueueFilters>, dispatch: any) => {
  dispatch(setFilters(newFilters));
};

/**
 * Handles changes to the sort criteria
 * @param field - The field to sort by
 * @param direction - The sort direction
 */
const handleSortChange = (field: UnderwritingQueueSortField, direction: SortDirection, dispatch: any) => {
  dispatch(setSort({ field, direction }));
};

/**
 * Handles page navigation in the data table
 * @param page - The new page number
 */
const handlePageChange = (page: number, dispatch: any) => {
  dispatch(setPage(page));
};

/**
 * Handles changes to the number of items per page
 * @param pageSize - The new page size
 */
const handlePageSizeChange = (pageSize: number, dispatch: any) => {
  dispatch(setPageSize(pageSize));
};

/**
 * Handles manual refresh of the queue data
 */
const handleRefresh = (fetchUnderwritingQueue: any, fetchAssignedApplications: any, dispatch: any, viewMode: string, filters: any, sort: any, page: any, pageSize: any, fetchMetrics: any) => {
  if (viewMode === 'all') {
    dispatch(fetchUnderwritingQueue({ filters, sort, page, pageSize }));
  } else {
    dispatch(fetchAssignedApplications({ page, pageSize }));
  }
  dispatch(fetchMetrics());
};

/**
 * Renders the metrics cards at the top of the page
 */
const renderMetricsCards = (metrics: any) => {
  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Typography variant="h6">Assigned Applications</Typography>
            <Typography variant="h5">{metrics?.assigned_to_me || 0}</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Typography variant="h6">Pending Review</Typography>
            <Typography variant="h5">{metrics?.pending_review || 0}</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Typography variant="h6">Completed Today</Typography>
            <Typography variant="h5">{metrics?.completed_today || 0}</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Typography variant="h6">Approval Rate</Typography>
            <Typography variant="h5">{metrics?.approval_rate || 0}%</Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

/**
 * Renders the filter controls for the queue
 */
const renderFilters = () => {
  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6} md={3}>
        <FormControl fullWidth>
          <InputLabel id="status-filter-label">Status</InputLabel>
          <Select labelId="status-filter-label" id="status-filter" value="">
            <MenuItem value="">All</MenuItem>
            {Object.values(UnderwritingQueueStatus).map((status) => (
              <MenuItem key={status} value={status}>{status}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <FormControl fullWidth>
          <InputLabel id="priority-filter-label">Priority</InputLabel>
          <Select labelId="priority-filter-label" id="priority-filter" value="">
            <MenuItem value="">All</MenuItem>
            {Object.values(UnderwritingQueuePriority).map((priority) => (
              <MenuItem key={priority} value={priority}>{priority}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <TextField label="Borrower Name" fullWidth />
      </Grid>
    </Grid>
  );
};

/**
 * Defines the columns configuration for the data table
 */
const getTableColumns = (): any => {
  return [
    { field: 'application_id', headerName: 'Application ID', width: 150 },
    { field: 'borrower_name', headerName: 'Borrower Name', width: 200 },
    { field: 'school_name', headerName: 'School Name', width: 200 },
    { field: 'program_name', headerName: 'Program Name', width: 200 },
    {
      field: 'requested_amount',
      headerName: 'Requested Amount',
      width: 150,
      align: 'right',
      render: (value: number) => formatCurrency(value)
    },
    {
      field: 'submission_date',
      headerName: 'Submission Date',
      width: 150,
      render: (value: string) => formatDate(value)
    },
    {
      field: 'priority',
      headerName: 'Priority',
      width: 120,
      render: (value: string) => (
        <StatusBadge status={value} />
      )
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 150,
      render: (value: string) => (
        <StatusBadge status={value} />
      )
    },
    {
      field: 'due_date',
      headerName: 'Due Date',
      width: 150,
      render: (value: string, row: UnderwritingQueueItem) => {
        const formattedDate = formatDate(value);
        return row.is_overdue ? (
          <><PriorityHighIcon style={{ color: 'red', marginRight: 4 }} />{formattedDate}</>
        ) : formattedDate;
      }
    },
    { field: 'assigned_to_name', headerName: 'Assigned To', width: 150 }
  ];
};

/**
 * Defines the row actions for the data table
 */
const getTableActions = (auth: any, navigate: any, dispatch: any): any => {
  return [
    {
      icon: <VisibilityIcon />,
      label: 'View',
      onClick: (row: UnderwritingQueueItem) => handleViewApplication(row, navigate)
    },
    {
      icon: <AssignmentIndIcon />,
      label: 'Assign to Me',
      isVisible: (row: UnderwritingQueueItem) => !row.assigned_to,
      onClick: (row: UnderwritingQueueItem) => handleAssignToMe(row, dispatch, auth)
    },
    {
      icon: <EditIcon />,
      label: 'Start Review',
      isVisible: (row: UnderwritingQueueItem) => row.assigned_to === auth.user?.id,
      onClick: (row: UnderwritingQueueItem) => handleStartReview(row, dispatch, navigate)
    }
  ];
};

/**
 * Main component for the underwriting queue page
 */
const UnderwritingQueue: React.FC = () => {
  // Local state for view mode (all applications or assigned to me)
  const [viewMode, setViewMode] = useState('all');

  // Redux hooks
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const queue = useSelector((state: RootState) => state.underwriting.queueItems);
  const loading = useSelector((state: RootState) => state.underwriting.loading);
  const totalItems = useSelector((state: RootState) => state.underwriting.totalItems);
  const filters = useSelector((state: RootState) => state.underwriting.filters);
  const sort = useSelector((state: RootState) => state.underwriting.sort);
  const page = useSelector((state: RootState) => state.underwriting.page);
  const pageSize = useSelector((state: RootState) => state.underwriting.pageSize);
  const metrics = useSelector((state: RootState) => state.underwriting.metrics);
  const auth = useSelector((state: RootState) => state.auth);

  // Fetch queue data and metrics on component mount and when dependencies change
  useEffect(() => {
    if (viewMode === 'all') {
      dispatch(fetchUnderwritingQueue({ filters, sort, page, pageSize }));
    } else {
      dispatch(fetchAssignedApplications({ page, pageSize }));
    }
    dispatch(fetchMetrics());
  }, [dispatch, viewMode, filters, sort, page, pageSize]);

  // Define table columns and actions using memoized functions
  const columns = useMemo(() => getTableColumns(), []);
  const actions = useMemo(() => getTableActions(auth, navigate, dispatch), [auth, navigate, dispatch]);

  return (
    <Page title="Underwriting Queue">
      {renderMetricsCards(metrics)}

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          All Applications
        </Typography>
        <Box>
          <Button variant={viewMode === 'all' ? 'contained' : 'outlined'} onClick={() => setViewMode('all')}>All Applications</Button>
          <Button variant={viewMode === 'assigned' ? 'contained' : 'outlined'} onClick={() => setViewMode('assigned')}>Assigned to Me</Button>
        </Box>
      </Box>

      {renderFilters()}

      <DataTable
        data={queue}
        columns={columns}
        loading={loading}
        totalItems={totalItems}
        page={page}
        pageSize={pageSize}
        onPageChange={(newPage) => handlePageChange(newPage, dispatch)}
        onPageSizeChange={(newPageSize) => handlePageSizeChange(newPageSize, dispatch)}
        sorting
        sortField={sort?.field}
        sortDirection={sort?.direction}
        onSortChange={(field, direction) => handleSortChange(field, direction, dispatch)}
        actions={actions}
      />
    </Page>
  );
};

export default UnderwritingQueue;