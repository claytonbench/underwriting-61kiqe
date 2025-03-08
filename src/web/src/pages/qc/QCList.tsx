import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux'; // react-redux v8.1.1
import { useNavigate } from 'react-router-dom'; // react-router-dom v6.14.1
import { 
  Box, 
  Typography, 
  Tabs, 
  Tab, 
  Button, 
  Chip, 
  Alert, 
  Card, 
  CardContent,
  Grid
} from '@mui/material'; // @mui/material v5.14.0
import { 
  VisibilityIcon, 
  AssignmentIcon, 
  CheckCircleIcon, 
  ErrorIcon 
} from '@mui/icons-material'; // @mui/icons-material v5.14.0

import Page from '../../components/common/Page';
import DataTable from '../../components/common/DataTable';
import { 
  QCReviewListItem, 
  QCStatus, 
  QCPriority, 
  QCReviewFilters, 
  QCReviewSort, 
  QCReviewSortField 
} from '../../types/qc.types';
import { 
  SortDirection, 
  TableColumn, 
  FilterConfig, 
  FilterOption 
} from '../../types/common.types';
import { 
  selectQCReviews, 
  selectLoading, 
  selectError, 
  selectTotalQCReviews, 
  selectFilters, 
  selectSort, 
  selectPage, 
  selectPageSize,
  selectCountsByStatus 
} from '../../store/slices/qcSlice';
import { actions } from '../../store/slices/qcSlice';
import { 
  fetchQCReviewsThunk,
  fetchQCCountsByStatusThunk 
} from '../../store/thunks/qcThunks';
import { formatDate } from '../../utils/formatting';

/**
 * Main component for the QC list page that displays a list of loan applications pending QC review
 * @returns Rendered QC list page
 */
const QCList: React.FC = () => {
  // Initialize Redux dispatch and navigate functions
  const dispatch = useDispatch();
  const navigate = useNavigate();

  // Set up selectors for QC reviews, loading state, error state, total count, filters, sort, page, page size, and status counts
  const qcReviews = useSelector(selectQCReviews);
  const loading = useSelector(selectLoading);
  const error = useSelector(selectError);
  const totalQCReviews = useSelector(selectTotalQCReviews);
  const filters = useSelector(selectFilters);
  const sort = useSelector(selectSort);
  const page = useSelector(selectPage);
  const pageSize = useSelector(selectPageSize);
  const countsByStatus = useSelector(selectCountsByStatus);

  // Set up state for active tab (All, Pending, In Review, etc.)
  const [activeTab, setActiveTab] = useState<QCStatus | 'all'>('all');

  // Create useEffect to fetch QC reviews and status counts when component mounts or dependencies change
  useEffect(() => {
    // Fetch QC reviews based on current page, page size, filters, and sort
    dispatch(fetchQCReviewsThunk({ 
      page, 
      pageSize, 
      filters: filters as QCReviewFilters, 
      sort: sort as QCReviewSort 
    }));

    // Fetch QC review counts by status
    dispatch(fetchQCCountsByStatusThunk());
  }, [dispatch, page, pageSize, filters, sort]);

  // Define table columns configuration with field mappings, headers, and custom renderers
  const columns: TableColumn<QCReviewListItem>[] = useMemo(() => [
    { 
      field: 'application_id', 
      headerName: 'Application ID', 
      width: 150,
      render: (value) => <Typography variant="body2">{value}</Typography>
    },
    { 
      field: 'borrower_name', 
      headerName: 'Borrower Name', 
      width: 200,
      sortable: true,
      render: (value) => <Typography variant="body2">{value}</Typography>
    },
    { 
      field: 'school_name', 
      headerName: 'School Name', 
      width: 200,
      sortable: true,
      render: (value) => <Typography variant="body2">{value}</Typography>
    },
    { 
      field: 'status', 
      headerName: 'Status', 
      width: 150,
      sortable: true,
      render: (value) => (
        <Chip 
          label={value} 
          color={
            value === QCStatus.APPROVED ? 'success' :
            value === QCStatus.RETURNED ? 'error' :
            value === QCStatus.IN_REVIEW ? 'warning' : 'primary'
          } 
          size="small" 
        />
      )
    },
    { 
      field: 'priority', 
      headerName: 'Priority', 
      width: 120,
      sortable: true,
      render: (value) => <Typography variant="body2">{value}</Typography>
    },
    { 
      field: 'assigned_to_name', 
      headerName: 'Assigned To', 
      width: 180,
      sortable: true,
      render: (value) => <Typography variant="body2">{value || 'Unassigned'}</Typography>
    },
    { 
      field: 'assigned_at', 
      headerName: 'Assigned At', 
      width: 150,
      sortable: true,
      render: (value) => <Typography variant="body2">{value ? formatDate(value) : 'N/A'}</Typography>
    },
    { 
      field: 'completion_percentage', 
      headerName: 'Completion', 
      width: 120,
      sortable: true,
      render: (value) => <Typography variant="body2">{value}%</Typography>
    },
    { 
      field: 'created_at', 
      headerName: 'Created At', 
      width: 150,
      sortable: true,
      render: (value) => <Typography variant="body2">{formatDate(value)}</Typography>
    }
  ], []);

  // Create filter configuration for status, priority, borrower name, and school filters
  const filterConfig: FilterConfig[] = useMemo(() => [
    { 
      field: 'borrower_name', 
      label: 'Borrower Name', 
      type: 'text', 
      width: 200 
    },
    { 
      field: 'school_name', 
      label: 'School Name', 
      type: 'text', 
      width: 200 
    }
  ], []);

  // Define handler functions for filter changes, sort changes, page changes, and page size changes
  const handleFilterChange = useCallback((newFilters: FilterOption[]) => {
    const qcFilters: QCReviewFilters = {};
    newFilters.forEach(filter => {
      qcFilters[filter.field] = filter.value;
    });
    dispatch(actions.setFilters(qcFilters));
  }, [dispatch]);

  const handleSortChange = useCallback((field: string, direction: SortDirection) => {
    dispatch(actions.setSort({ field: field as QCReviewSortField, direction }));
  }, [dispatch]);

  const handlePageChange = useCallback((newPage: number) => {
    dispatch(actions.setPage(newPage));
  }, [dispatch]);

  const handlePageSizeChange = useCallback((newPageSize: number) => {
    dispatch(actions.setPageSize(newPageSize));
  }, [dispatch]);

  // Define handler function for tab changes to update status filter
  const handleTabChange = useCallback((event: React.SyntheticEvent, newValue: QCStatus | 'all') => {
    setActiveTab(newValue);
    if (newValue === 'all') {
      dispatch(actions.setFilters({}));
    } else {
      dispatch(actions.setFilters({ status: newValue }));
    }
  }, [dispatch]);

  // Define handler function for view action to navigate to QC review detail page
  const handleViewAction = useCallback((review: QCReviewListItem) => {
    navigate(`/qc/${review.application_id}`);
  }, [navigate]);

  // Define handler function for start review action to begin QC review process
  const handleStartReviewAction = useCallback((review: QCReviewListItem) => {
    dispatch(fetchQCReviewsThunk(review.id));
  }, [dispatch]);

  // Define actions for the table
  const actionsList = useMemo(() => [
    { 
      icon: <VisibilityIcon />, 
      label: 'View', 
      onClick: handleViewAction 
    },
    { 
      icon: <AssignmentIcon />, 
      label: 'Start Review', 
      onClick: handleStartReviewAction,
      isVisible: (review: QCReviewListItem) => review.status === QCStatus.PENDING 
    }
  ], [handleViewAction, handleStartReviewAction]);

  // Render the Page component with appropriate title and actions
  return (
    <Page
      title="Quality Control Reviews"
    >
      {/* Render status summary cards showing counts by status */}
      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Total</Typography>
              <Typography variant="h4">{countsByStatus?.total || 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Pending</Typography>
              <Typography variant="h4">{countsByStatus?.pending || 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">In Review</Typography>
              <Typography variant="h4">{countsByStatus?.in_review || 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Approved</Typography>
              <Typography variant="h4">{countsByStatus?.approved || 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Render tabs for filtering by status (All, Pending, In Review, etc.) */}
      <Tabs
        value={activeTab}
        onChange={handleTabChange}
        aria-label="QC Status"
        sx={{ mb: 2 }}
      >
        <Tab label="All" value="all" />
        <Tab label="Pending" value={QCStatus.PENDING} />
        <Tab label="In Review" value={QCStatus.IN_REVIEW} />
        <Tab label="Approved" value={QCStatus.APPROVED} />
      </Tabs>

      {/* Render DataTable component with QC reviews data, columns, and handlers */}
      <DataTable
        data={qcReviews}
        columns={columns}
        loading={loading}
        emptyStateMessage="No QC reviews found"
        actions={actionsList}
        pagination
        page={page}
        pageSize={pageSize}
        totalItems={totalQCReviews}
        onPageChange={handlePageChange}
        onPageSizeChange={handlePageSizeChange}
        sorting
        sortField={sort?.field}
        sortDirection={sort?.direction}
        onSortChange={handleSortChange}
        filtering
        filterConfig={filterConfig}
        filterOptions={filters ? Object.entries(filters).map(([field, value]) => ({ field, value })) : []}
        onFilterChange={handleFilterChange}
      />

      {/* Handle loading and error states appropriately */}
      {loading && (
        <Box textAlign="center" mt={2}>
          <Typography variant="body2">Loading QC reviews...</Typography>
        </Box>
      )}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Page>
  );
};

export default QCList;