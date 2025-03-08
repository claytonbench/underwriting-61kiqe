import React, { useState, useEffect, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux'; // ^8.1.1
import { useNavigate, useParams } from 'react-router-dom'; // ^6.14.2
import {
  Button,
  Typography,
  Box,
  Chip,
  IconButton,
  TextField,
  MenuItem
} from '@mui/material'; // ^5.14.0
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon
} from '@mui/icons-material'; // ^5.14.0

import Page from '../../components/common/Page/Page';
import DataTable from '../../components/common/DataTable/DataTable';
import {
  Program,
  ProgramStatus,
  ProgramFilters
} from '../../types/school.types';
import { SortDirection } from '../../types/common.types';
import {
  fetchPrograms,
  fetchProgramsBySchool,
  selectPrograms,
  selectTotalPrograms,
  selectSchoolLoading,
  selectSchoolError,
  selectProgramFilters,
  setProgramFilters,
  deleteExistingProgram
} from '../../store/slices/schoolSlice';

/**
 * Main component that displays a list of educational programs with filtering, sorting, and pagination.
 * Provides program management interface for school administrators and system administrators.
 */
const ProgramList: React.FC = () => {
  // Get URL parameters to check for schoolId
  const { schoolId } = useParams<{ schoolId?: string }>();

  // Initialize navigation
  const navigate = useNavigate();

  // Set up Redux state
  const dispatch = useDispatch();
  const programs = useSelector(selectPrograms);
  const totalPrograms = useSelector(selectTotalPrograms);
  const loading = useSelector(selectSchoolLoading);
  const error = useSelector(selectSchoolError);
  const filters = useSelector(selectProgramFilters);

  // Local state for pagination and sorting
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [sortField, setSortField] = useState<string>('name');
  const [sortDirection, setSortDirection] = useState<SortDirection>(SortDirection.ASC);

  /**
   * Fetch program data based on current filters, pagination, and sorting
   */
  const fetchProgramData = useCallback(() => {
    const fetchAction = schoolId
      ? fetchProgramsBySchool({
          schoolId,
          page,
          pageSize,
          filters: {
            ...filters,
            school_id: schoolId
          }
        })
      : fetchPrograms({
          page,
          pageSize,
          filters
        });
    
    dispatch(fetchAction);
  }, [dispatch, schoolId, page, pageSize, filters]);

  // Fetch data when component mounts or dependencies change
  useEffect(() => {
    fetchProgramData();
  }, [fetchProgramData]);

  /**
   * Handles page change events from the DataTable pagination
   */
  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    // Data refetch will be triggered by the useEffect dependency on page
  };

  /**
   * Handles page size change events from the DataTable pagination
   */
  const handlePageSizeChange = (newPageSize: number) => {
    setPageSize(newPageSize);
    setPage(1); // Reset to page 1
    // Data refetch will be triggered by the useEffect dependency on pageSize
  };

  /**
   * Handles sort change events from the DataTable
   */
  const handleSortChange = (field: string, direction: SortDirection) => {
    setSortField(field);
    setSortDirection(direction);
    // In a real implementation, we would pass sortField and sortDirection to the API
    // Data refetch would be triggered by the useEffect dependency on these values
  };

  /**
   * Handles filter change events
   */
  const handleFilterChange = (newFilters: ProgramFilters) => {
    dispatch(setProgramFilters(newFilters));
    setPage(1); // Reset to page 1
    // Data refetch will be triggered by the useEffect dependency on filters
  };

  /**
   * Handles click on the Add Program button
   */
  const handleAddProgram = () => {
    if (schoolId) {
      navigate(`/schools/${schoolId}/programs/new`);
    } else {
      navigate('/programs/new');
    }
  };

  /**
   * Handles click on the View action for a program
   */
  const handleViewProgram = (program: Program) => {
    if (schoolId) {
      navigate(`/schools/${schoolId}/programs/${program.id}`);
    } else {
      navigate(`/programs/${program.id}`);
    }
  };

  /**
   * Handles click on the Edit action for a program
   */
  const handleEditProgram = (program: Program) => {
    if (schoolId) {
      navigate(`/schools/${schoolId}/programs/${program.id}/edit`);
    } else {
      navigate(`/programs/${program.id}/edit`);
    }
  };

  /**
   * Handles click on the Delete action for a program
   */
  const handleDeleteProgram = (program: Program) => {
    if (window.confirm(`Are you sure you want to delete the program "${program.name}"?`)) {
      dispatch(deleteExistingProgram(program.id))
        .unwrap()
        .then(() => {
          // Show success notification
          alert('Program deleted successfully');
          // Refetch data to update the list
          fetchProgramData();
        })
        .catch((err) => {
          // Show error notification
          alert(`Failed to delete program: ${err.message || 'Unknown error'}`);
        });
    }
  };

  /**
   * Renders a status chip with appropriate color based on program status
   */
  const renderStatusChip = (status: ProgramStatus) => {
    const color = status === ProgramStatus.ACTIVE ? 'success' : 'default';
    return (
      <Chip 
        label={status === ProgramStatus.ACTIVE ? 'Active' : 'Inactive'} 
        color={color} 
        size="small" 
      />
    );
  };

  // Define columns for the DataTable
  const columns = [
    {
      field: 'name',
      headerName: 'Program Name',
      sortable: true,
      width: '30%'
    },
    {
      field: 'duration_weeks',
      headerName: 'Duration (Weeks)',
      sortable: true,
      width: '15%',
      align: 'right' as const
    },
    {
      field: 'current_tuition',
      headerName: 'Tuition',
      sortable: true,
      width: '15%',
      align: 'right' as const,
      render: (value: number) => `$${value.toLocaleString()}`
    },
    {
      field: 'status',
      headerName: 'Status',
      sortable: true,
      width: '15%',
      render: (value: ProgramStatus) => renderStatusChip(value)
    }
  ];

  // Define row actions for the DataTable
  const actions = [
    {
      icon: <ViewIcon />,
      label: 'View Program',
      onClick: handleViewProgram,
      color: 'info' as const
    },
    {
      icon: <EditIcon />,
      label: 'Edit Program',
      onClick: handleEditProgram,
      color: 'primary' as const
    },
    {
      icon: <DeleteIcon />,
      label: 'Delete Program',
      onClick: handleDeleteProgram,
      color: 'error' as const
    }
  ];

  // Define page title and description based on context
  const pageTitle = schoolId ? 'School Programs' : 'Programs';
  const pageDescription = schoolId 
    ? 'Manage educational programs for this school' 
    : 'Manage all educational programs across schools';

  return (
    <Page
      title={pageTitle}
      description={pageDescription}
      actions={
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleAddProgram}
          aria-label="Add new program"
        >
          Add Program
        </Button>
      }
    >
      {/* Filter controls */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <TextField
          label="Program Name"
          variant="outlined"
          size="small"
          value={filters.name || ''}
          onChange={(e) => handleFilterChange({ ...filters, name: e.target.value || null })}
          sx={{ minWidth: 200 }}
          placeholder="Search by name"
          aria-label="Filter by program name"
        />
        <TextField
          select
          label="Status"
          variant="outlined"
          size="small"
          value={filters.status || ''}
          onChange={(e) => handleFilterChange({ 
            ...filters, 
            status: e.target.value ? e.target.value as ProgramStatus : null 
          })}
          sx={{ minWidth: 150 }}
          aria-label="Filter by status"
        >
          <MenuItem value="">All</MenuItem>
          <MenuItem value={ProgramStatus.ACTIVE}>Active</MenuItem>
          <MenuItem value={ProgramStatus.INACTIVE}>Inactive</MenuItem>
        </TextField>
      </Box>

      {/* Display error message if any */}
      {error && (
        <Box sx={{ mb: 2 }}>
          <Typography color="error">{error}</Typography>
        </Box>
      )}

      {/* Programs table */}
      <DataTable
        data={programs}
        columns={columns}
        loading={loading}
        emptyStateMessage="No programs found. Add a program to get started."
        
        pagination
        page={page}
        pageSize={pageSize}
        totalItems={totalPrograms}
        onPageChange={handlePageChange}
        onPageSizeChange={handlePageSizeChange}
        pageSizeOptions={[10, 25, 50, 100]}
        
        sorting
        sortField={sortField}
        sortDirection={sortDirection}
        onSortChange={handleSortChange}
        
        actions={actions}
        mobileFields={['name', 'status', 'current_tuition']}
      />
    </Page>
  );
};

export default ProgramList;