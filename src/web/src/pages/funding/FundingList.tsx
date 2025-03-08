import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  Grid,
  Typography,
  Button,
  Card,
  CardContent,
  Box,
  Chip,
  Alert,
} from '@mui/material'; // Material-UI v5.14.0
import { Visibility as VisibilityIcon, Edit as EditIcon } from '@mui/icons-material'; // Material-UI v5.14.0

import Page from '../../components/common/Page';
import DataTable from '../../components/common/DataTable';
import StatusBadge from '../../components/common/StatusBadge';
import LoadingOverlay from '../../components/common/Loading';
import { formatCurrency } from '../../utils/formatting';
import { formatDate } from '../../utils/date';
import usePermissions from '../../hooks/usePermissions';
import {
  FundingRequestStatus,
  FundingRequestListItem,
  FundingFilters,
  FundingSort,
  FundingSortField,
  FundingStatusSummary,
} from '../../types/funding.types';
import { TableColumn, SortDirection, FilterOption } from '../../types/common.types';
import {
  fetchFundingRequests,
  fetchFundingStatusSummary,
} from '../../store/thunks/fundingThunks';
import {
  setFundingFilters,
  setFundingSort,
  setFundingPage,
  setPageSize,
} from '../../store/slices/fundingSlice';

/**
 * Main component for displaying a list of funding requests
 * @returns Rendered funding list page
 */
const FundingList: React.FC = () => {
  // Initialize Redux dispatch and navigation functions
  const dispatch = useDispatch();
  const navigate = useNavigate();

  // Select funding requests, loading state, error, filters, sort, pagination, and status summary from Redux store
  const fundingRequests = useSelector((state: any) => state.funding.fundingRequests);
  const loading = useSelector((state: any) => state.funding.loading);
  const error = useSelector((state: any) => state.funding.error);
  const filters = useSelector((state: any) => state.funding.fundingFilters);
  const sort = useSelector((state: any) => state.funding.fundingSort);
  const page = useSelector((state: any) => state.funding.fundingPage);
  const pageSize = useSelector((state: any) => state.funding.pageSize);
  const totalFundingRequests = useSelector((state: any) => state.funding.totalFundingRequests);
  const statusSummary = useSelector((state: any) => state.funding.statusSummary);

  // Check user permissions for viewing and managing funding requests
  const { checkPermission } = usePermissions();
  const canViewFunding = checkPermission('funding:view');
  const canEditFunding = checkPermission('funding:edit');

  // Define table columns for funding requests (application ID, borrower name, school name, requested amount, approved amount, status, requested date, actions)
  const columns: TableColumn<FundingRequestListItem>[] = [
    {
      field: 'application_id',
      headerName: 'Application ID',
      width: 150,
      sortable: true,
    },
    {
      field: 'borrower_name',
      headerName: 'Borrower Name',
      width: 200,
      sortable: true,
    },
    {
      field: 'school_name',
      headerName: 'School Name',
      width: 200,
      sortable: true,
    },
    {
      field: 'requested_amount',
      headerName: 'Requested Amount',
      width: 150,
      sortable: true,
      align: 'right',
      render: (value) => formatCurrency(value),
    },
    {
      field: 'approved_amount',
      headerName: 'Approved Amount',
      width: 150,
      sortable: true,
      align: 'right',
      render: (value) => formatCurrency(value),
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 150,
      sortable: true,
      render: (status: FundingRequestStatus) => renderStatusCell(status),
    },
    {
      field: 'requested_at',
      headerName: 'Requested Date',
      width: 150,
      sortable: true,
      render: (value) => formatDate(value, 'MM/DD/YYYY'),
    },
  ];

  // Define filter configuration for funding request filtering
  const filterConfig: any[] = [
    {
      field: 'status',
      label: 'Status',
      type: 'select',
      options: Object.values(FundingRequestStatus).map((status) => ({
        value: status,
        label: status.replace(/_/g, ' '),
      })),
    },
    {
      field: 'borrower_name',
      label: 'Borrower Name',
      type: 'text',
      width: 200,
    },
    {
      field: 'school_name',
      label: 'School Name',
      type: 'text',
      width: 200,
    },
  ];

  // Fetch funding requests and status summary on component mount and when filters, sort, or pagination changes
  useEffect(() => {
    if (!canViewFunding) return;

    dispatch(
      fetchFundingRequests({
        page,
        pageSize,
        filters,
        sort,
      })
    );
    dispatch(fetchFundingStatusSummary());
  }, [dispatch, page, pageSize, filters, sort, canViewFunding]);

  // Handle filter changes by dispatching setFundingFilters action
  const handleFilterChange = useCallback(
    (newFilters: FilterOption[]) => {
      const parsedFilters: FundingFilters = {};
      newFilters.forEach((filter) => {
        parsedFilters[filter.field] = filter.value;
      });
      dispatch(setFundingFilters(parsedFilters));
    },
    [dispatch]
  );

  // Handle sort changes by dispatching setFundingSort action
  const handleSortChange = useCallback(
    (field: string, direction: SortDirection) => {
      const newSort: FundingSort = {
        field: field as FundingSortField,
        direction: direction,
      };
      dispatch(setFundingSort(newSort));
    },
    [dispatch]
  );

  // Handle page changes by dispatching setFundingPage action
  const handlePageChange = useCallback(
    (newPage: number) => {
      dispatch(setFundingPage(newPage));
    },
    [dispatch]
  );

  // Handle page size changes by dispatching setPageSize action
  const handlePageSizeChange = useCallback(
    (newPageSize: number) => {
      dispatch(setPageSize(newPageSize));
    },
    [dispatch]
  );

  // Handle view details action to navigate to funding detail page
  const handleViewDetails = useCallback(
    (row: FundingRequestListItem) => {
      navigate(`/funding/${row.id}`);
    },
    [navigate]
  );

  // Render page with status summary cards and funding requests data table
  return (
    <Page title="Funding Requests" description="Manage loan funding requests">
      {statusSummary && <StatusSummaryCards statusSummary={statusSummary} />}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <DataTable
        data={fundingRequests}
        columns={columns}
        loading={loading}
        totalItems={totalFundingRequests}
        page={page}
        pageSize={pageSize}
        onPageChange={handlePageChange}
        onPageSizeChange={handlePageSizeChange}
        sorting
        sortField={sort?.field}
        sortDirection={sort?.direction}
        onSortChange={handleSortChange}
        filtering
        filterOptions={
          filters
            ? Object.entries(filters).map(([key, value]) => ({
                field: key,
                value: value,
              }))
            : []
        }
        filterConfig={filterConfig}
        onFilterChange={handleFilterChange}
        actions={
          canEditFunding
            ? [
                {
                  icon: <VisibilityIcon />,
                  label: 'View Details',
                  onClick: handleViewDetails,
                },
              ]
            : []
        }
      />

      <LoadingOverlay isLoading={loading} message="Loading funding requests..." />
    </Page>
  );
};

/**
 * Component for displaying funding status summary cards
 * @param object - { statusSummary }
 * @returns Rendered status summary cards
 */
const StatusSummaryCards: React.FC<{ statusSummary: FundingStatusSummary }> = ({
  statusSummary,
}) => {
  // Display grid of cards showing counts for each funding status
  // Include cards for pending, enrollment verified, pending stipulations, stipulations complete, approved, scheduled for disbursement, disbursed, rejected, and total
  // Format each card with appropriate status color and count
  // Make cards clickable to filter the list by status
  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6} md={4} lg={3}>
        <Card>
          <CardContent>
            <Typography variant="h6">Pending</Typography>
            <Typography variant="h5">{statusSummary.pending}</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={4} lg={3}>
        <Card>
          <CardContent>
            <Typography variant="h6">Enrollment Verified</Typography>
            <Typography variant="h5">{statusSummary.enrollment_verified}</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={4} lg={3}>
        <Card>
          <CardContent>
            <Typography variant="h6">Pending Stipulations</Typography>
            <Typography variant="h5">{statusSummary.pending_stipulations}</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={4} lg={3}>
        <Card>
          <CardContent>
            <Typography variant="h6">Stipulations Complete</Typography>
            <Typography variant="h5">{statusSummary.stipulations_complete}</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={4} lg={3}>
        <Card>
          <CardContent>
            <Typography variant="h6">Approved</Typography>
            <Typography variant="h5">{statusSummary.approved}</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={4} lg={3}>
        <Card>
          <CardContent>
            <Typography variant="h6">Scheduled for Disbursement</Typography>
            <Typography variant="h5">{statusSummary.scheduled_for_disbursement}</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={4} lg={3}>
        <Card>
          <CardContent>
            <Typography variant="h6">Disbursed</Typography>
            <Typography variant="h5">{statusSummary.disbursed}</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={4} lg={3}>
        <Card>
          <CardContent>
            <Typography variant="h6">Rejected</Typography>
            <Typography variant="h5">{statusSummary.rejected}</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={4} lg={3}>
        <Card>
          <CardContent>
            <Typography variant="h6">Cancelled</Typography>
            <Typography variant="h5">{statusSummary.cancelled}</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6} md={4} lg={3}>
        <Card>
          <CardContent>
            <Typography variant="h6">Total</Typography>
            <Typography variant="h5">{statusSummary.total}</Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

/**
 * Helper function to get the appropriate color for a funding status
 * @param FundingRequestStatus - status
 * @returns Color code for the status
 */
const getStatusColor = (status: FundingRequestStatus): string => {
  // Map each FundingRequestStatus value to an appropriate color
  // Return the color code for the given status
  switch (status) {
    case FundingRequestStatus.PENDING:
      return 'warning';
    case FundingRequestStatus.ENROLLMENT_VERIFIED:
      return 'info';
    case FundingRequestStatus.PENDING_STIPULATIONS:
      return 'warning';
    case FundingRequestStatus.STIPULATIONS_COMPLETE:
      return 'info';
    case FundingRequestStatus.APPROVED:
      return 'success';
    case FundingRequestStatus.REJECTED:
      return 'error';
    case FundingRequestStatus.SCHEDULED_FOR_DISBURSEMENT:
      return 'info';
    case FundingRequestStatus.DISBURSED:
      return 'success';
    case FundingRequestStatus.CANCELLED:
      return 'error';
    default:
      return 'default';
  }
};

/**
 * Helper function to render a status cell in the data table
 * @param FundingRequestStatus - status
 * @returns Rendered status badge
 */
const renderStatusCell = (status: FundingRequestStatus): JSX.Element => {
  // Return a StatusBadge component with the appropriate status and color
  return <StatusBadge status={status} />;
};

// Export the FundingList component
export default FundingList;