import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux'; // ^8.1.0
import { useNavigate } from 'react-router-dom'; // ^6.14.0
import {
  Button,
  Box,
  Typography,
  Chip,
  IconButton,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select
} from '@mui/material'; // ^5.14.0
import {
  Add as AddIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon,
  Delete as DeleteIcon
} from '@mui/icons-material'; // ^5.14.0

import Page from '../../components/common/Page';
import DataTable from '../../components/common/DataTable';
import { School, SchoolStatus, SchoolFilters } from '../../types/school.types';
import { SortDirection } from '../../types/common.types';
import {
  fetchSchools,
  setSchoolFilters,
  selectSchools,
  selectTotalSchools,
  selectSchoolLoading,
  selectSchoolError,
  selectSchoolFilters
} from '../../store/slices/schoolSlice';

/**
 * Returns the appropriate color for a school status chip
 */
const getStatusColor = (status: SchoolStatus): string => {
  switch (status) {
    case SchoolStatus.ACTIVE:
      return 'success';
    case SchoolStatus.INACTIVE:
      return 'error';
    case SchoolStatus.PENDING:
      return 'warning';
    case SchoolStatus.REJECTED:
      return 'default';
    default:
      return 'default';
  }
};

/**
 * SchoolList component displays a paginated, sortable list of schools with filtering capabilities.
 * It provides options to view, edit, or create schools and is accessible only to system administrators.
 */
const SchoolList: React.FC = () => {
  // State for pagination and sorting
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);
  const [sortField, setSortField] = useState<string>('name');
  const [sortDirection, setSortDirection] = useState<SortDirection>(SortDirection.ASC);

  // Redux hooks
  const dispatch = useDispatch();
  const navigate = useNavigate();
  
  // Select data from Redux store
  const schools = useSelector(selectSchools);
  const totalSchools = useSelector(selectTotalSchools);
  const loading = useSelector(selectSchoolLoading);
  const error = useSelector(selectSchoolError);
  const filters = useSelector(selectSchoolFilters);

  // Fetch schools when dependencies change
  useEffect(() => {
    dispatch(fetchSchools({ 
      page, 
      pageSize, 
      filters 
    }));
  }, [dispatch, page, pageSize, sortField, sortDirection, filters]);

  /**
   * Handles changes to the filter values
   */
  const handleFilterChange = useCallback((newFilters: SchoolFilters) => {
    dispatch(setSchoolFilters(newFilters));
    setPage(1); // Reset to page 1 when filters change
  }, [dispatch]);

  /**
   * Handles changes to the sort field and direction
   */
  const handleSortChange = useCallback((field: string, direction: SortDirection) => {
    setSortField(field);
    setSortDirection(direction);
  }, []);

  /**
   * Handles page change events from the pagination component
   */
  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage);
  }, []);

  /**
   * Handles page size change events from the pagination component
   */
  const handlePageSizeChange = useCallback((newPageSize: number) => {
    setPageSize(newPageSize);
    setPage(1); // Reset to page 1 when page size changes
  }, []);

  /**
   * Navigates to the school detail page
   */
  const handleViewSchool = useCallback((school: School) => {
    navigate(`/schools/${school.id}`);
  }, [navigate]);

  /**
   * Navigates to the school edit page
   */
  const handleEditSchool = useCallback((school: School) => {
    navigate(`/schools/${school.id}/edit`);
  }, [navigate]);

  /**
   * Navigates to the new school page
   */
  const handleAddSchool = useCallback(() => {
    navigate('/schools/new');
  }, [navigate]);

  // Define table columns
  const columns = useMemo(() => [
    {
      field: 'name',
      headerName: 'School Name',
      sortable: true,
      width: '25%'
    },
    {
      field: 'legal_name',
      headerName: 'Legal Name',
      sortable: true,
      width: '25%',
      desktopOnly: true
    },
    {
      field: 'state',
      headerName: 'State',
      sortable: true,
      width: '10%'
    },
    {
      field: 'status',
      headerName: 'Status',
      sortable: true,
      width: '15%',
      render: (value: SchoolStatus) => (
        <Chip 
          label={value.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} 
          color={getStatusColor(value) as any}
          size="small"
        />
      )
    },
    {
      field: 'created_at',
      headerName: 'Created',
      sortable: true,
      width: '15%',
      desktopOnly: true,
      render: (value: string) => {
        const date = new Date(value);
        return date.toLocaleDateString('en-US', {
          month: '2-digit',
          day: '2-digit',
          year: 'numeric'
        });
      }
    }
  ], []);

  // Define table actions
  const actions = useMemo(() => [
    {
      icon: <VisibilityIcon />,
      label: 'View School',
      onClick: handleViewSchool,
      color: 'primary'
    },
    {
      icon: <EditIcon />,
      label: 'Edit School',
      onClick: handleEditSchool,
      color: 'secondary'
    }
  ], [handleViewSchool, handleEditSchool]);

  // Define filter configuration
  const filterConfig = useMemo(() => [
    {
      field: 'status',
      label: 'Status',
      type: 'select',
      options: [
        { value: '', label: 'All' },
        { value: 'active', label: 'Active' },
        { value: 'inactive', label: 'Inactive' },
        { value: 'pending_approval', label: 'Pending' },
        { value: 'rejected', label: 'Rejected' }
      ]
    },
    {
      field: 'name',
      label: 'School Name',
      type: 'text'
    },
    {
      field: 'state',
      label: 'State',
      type: 'text'
    }
  ], []);

  return (
    <Page
      title="School Management"
      description="Manage schools and their programs in the loan management system"
      actions={
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleAddSchool}
          aria-label="Add new school"
        >
          Add School
        </Button>
      }
    >
      {error && (
        <Box mt={2} mb={2}>
          <Typography color="error">{error}</Typography>
        </Box>
      )}

      <DataTable
        data={schools}
        columns={columns}
        loading={loading}
        actions={actions}
        
        // Pagination props
        pagination={true}
        page={page}
        pageSize={pageSize}
        totalItems={totalSchools}
        onPageChange={handlePageChange}
        onPageSizeChange={handlePageSizeChange}
        pageSizeOptions={[10, 25, 50, 100]}
        
        // Sorting props
        sorting={true}
        sortField={sortField}
        sortDirection={sortDirection}
        onSortChange={handleSortChange}
        
        // Filtering props
        filtering={true}
        filterConfig={filterConfig}
        onFilterChange={handleFilterChange as any} // Type assertion needed due to different filter interfaces
        
        emptyStateMessage="No schools found. Please adjust your filters or create a new school."
      />
    </Page>
  );
};

export default SchoolList;