import React, { useState, useEffect, useCallback } from 'react'; // react v18.0+
import { useNavigate } from 'react-router-dom'; // react-router-dom
import { useDispatch, useSelector } from 'react-redux'; // react-redux
import { Button } from '@mui/material'; // @mui/material
import { Add, Edit, Delete, LockReset, Block, CheckCircle } from '@mui/icons-material'; // @mui/icons-material
import Page from '../../components/common/Page';
import DataTable from '../../components/common/DataTable';
import {
  UserWithProfile,
  UserFilters,
  Role,
} from '../../types/user.types';
import { UserType } from '../../types/auth.types';
import { SortDirection } from '../../types/common.types';
import {
  fetchUsers,
  deleteExistingUser,
  resetPassword,
  activateExistingUser,
  deactivateExistingUser,
  setFilters,
} from '../../store/thunks/userThunks';
import {
  selectUsers,
  selectUserLoading,
  selectTotalUsers,
  selectUserFilters,
} from '../../store/slices/userSlice';
import usePermissions from '../../hooks/usePermissions';
import ConfirmationDialog from '../../components/common/Confirmation/ConfirmationDialog';

/**
 * Main component that displays a list of users with filtering, sorting, and pagination
 * @returns Rendered user list page
 */
const UserList: React.FC = () => {
  // Initialize state for pagination (page, pageSize)
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);

  // Initialize state for sorting (sortField, sortDirection)
  const [sortField, setSortField] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>(SortDirection.ASC);

  // Initialize state for confirmation dialogs (deleteDialog, resetDialog, etc.)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState<boolean>(false);
  const [resetDialogOpen, setResetDialogOpen] = useState<boolean>(false);
  const [activateDialogOpen, setActivateDialogOpen] = useState<boolean>(false);
  const [deactivateDialogOpen, setDeactivateDialogOpen] = useState<boolean>(false);

  // Initialize state for the user being acted upon (selectedUser)
  const [selectedUser, setSelectedUser] = useState<UserWithProfile | null>(null);

  // Get Redux dispatch function using useDispatch
  const dispatch = useDispatch();

  // Get navigation function using useNavigate
  const navigate = useNavigate();

  // Get permission checking function using usePermissions
  const { checkPermission } = usePermissions();

  // Select users, loading state, total count, and filters from Redux store
  const users = useSelector(selectUsers);
  const loading = useSelector(selectUserLoading);
  const totalUsers = useSelector(selectTotalUsers);
  const filters = useSelector(selectUserFilters);

  /**
   * Handles page change events from the DataTable pagination
   * @param newPage
   */
  const handlePageChange = (newPage: number) => {
    // Update the page state with the new page number
    setPage(newPage);
    // Fetch users with the updated page number
    dispatch(fetchUsers({ page: newPage, pageSize, filters: filters }));
  };

  /**
   * Handles page size change events from the DataTable pagination
   * @param newPageSize
   */
  const handlePageSizeChange = (newPageSize: number) => {
    // Update the pageSize state with the new page size
    setPageSize(newPageSize);
    // Reset to page 1
    setPage(1);
    // Fetch users with the updated page size
    dispatch(fetchUsers({ page: 1, pageSize: newPageSize, filters: filters }));
  };

  /**
   * Handles sort change events from the DataTable
   * @param field
   * @param direction
   */
  const handleSortChange = (field: string, direction: SortDirection) => {
    // Update the sortField and sortDirection state
    setSortField(field);
    setSortDirection(direction);
    // Reset to page 1
    setPage(1);
    // Fetch users with the updated sort parameters
    dispatch(fetchUsers({ page: 1, pageSize, filters: filters }));
  };

  /**
   * Handles filter change events from the DataTable
   * @param filters
   */
  const handleFilterChange = (filters: any) => {
    // Convert filter options to UserFilters object
    const userFilters: UserFilters = {
      search: filters.find((f: any) => f.field === 'search')?.value || null,
      userType: filters.find((f: any) => f.field === 'userType')?.value || null,
      isActive: filters.find((f: any) => f.field === 'isActive')?.value || null,
      roleId: filters.find((f: any) => f.field === 'roleId')?.value || null,
      schoolId: filters.find((f: any) => f.field === 'schoolId')?.value || null,
      createdAfter: filters.find((f: any) => f.field === 'createdAfter')?.value || null,
      createdBefore: filters.find((f: any) => f.field === 'createdBefore')?.value || null,
    };
    // Dispatch setFilters action with the new filters
    dispatch(setFilters(userFilters));
    // Reset to page 1
    setPage(1);
    // Fetch users with the updated filters
    dispatch(fetchUsers({ page: 1, pageSize, filters: userFilters }));
  };

  /**
   * Handles edit user action
   * @param user
   */
  const handleEditUser = (user: UserWithProfile) => {
    // Navigate to the user edit page with the user ID
    navigate(`/users/${user.id}/edit`);
  };

  /**
   * Handles delete user button click
   * @param user
   */
  const handleDeleteClick = (user: UserWithProfile) => {
    // Set the selected user state
    setSelectedUser(user);
    // Open the delete confirmation dialog
    setDeleteDialogOpen(true);
  };

  /**
   * Handles delete confirmation
   */
  const handleDeleteConfirm = () => {
    if (selectedUser) {
      // Dispatch deleteExistingUser action with the selected user ID
      dispatch(deleteExistingUser(selectedUser.id));
      // Close the delete confirmation dialog
      setDeleteDialogOpen(false);
      // Clear the selected user state
      setSelectedUser(null);
    }
  };

  /**
   * Handles reset password button click
   * @param user
   */
  const handleResetPasswordClick = (user: UserWithProfile) => {
    // Set the selected user state
    setSelectedUser(user);
    // Open the reset password confirmation dialog
    setResetDialogOpen(true);
  };

  /**
   * Handles reset password confirmation
   */
  const handleResetPasswordConfirm = () => {
    if (selectedUser) {
      // Dispatch resetPassword action with the selected user ID
      dispatch(resetPassword(selectedUser.id));
      // Close the reset password confirmation dialog
      setResetDialogOpen(false);
      // Clear the selected user state
      setSelectedUser(null);
    }
  };

  /**
   * Handles activate user button click
   * @param user
   */
  const handleActivateClick = (user: UserWithProfile) => {
    // Set the selected user state
    setSelectedUser(user);
    // Open the activate confirmation dialog
    setActivateDialogOpen(true);
  };

  /**
   * Handles activate confirmation
   */
  const handleActivateConfirm = () => {
    if (selectedUser) {
      // Dispatch activateExistingUser action with the selected user ID
      dispatch(activateExistingUser(selectedUser.id));
      // Close the activate confirmation dialog
      setActivateDialogOpen(false);
      // Clear the selected user state
      setSelectedUser(null);
    }
  };

  /**
   * Handles deactivate user button click
   * @param user
   */
  const handleDeactivateClick = (user: UserWithProfile) => {
    // Set the selected user state
    setSelectedUser(user);
    // Open the deactivate confirmation dialog
    setDeactivateDialogOpen(true);
  };

  /**
   * Handles deactivate confirmation
   */
  const handleDeactivateConfirm = () => {
    if (selectedUser) {
      // Dispatch deactivateExistingUser action with the selected user ID
      dispatch(deactivateExistingUser(selectedUser.id));
      // Close the deactivate confirmation dialog
      setDeactivateDialogOpen(false);
      // Clear the selected user state
      setSelectedUser(null);
    }
  };

  /**
   * Handles create user button click
   */
  const handleCreateUser = () => {
    // Navigate to the user creation page
    navigate('/users/create');
  };

  // Define table columns configuration with field mappings and formatting
  const columns = [
    { field: 'firstName', headerName: 'First Name', width: 150, sortable: true },
    { field: 'lastName', headerName: 'Last Name', width: 150, sortable: true },
    { field: 'email', headerName: 'Email', width: 250, sortable: true },
    { field: 'userType', headerName: 'User Type', width: 150, sortable: true },
    {
      field: 'isActive',
      headerName: 'Status',
      width: 120,
      sortable: true,
      render: (value: boolean) => (value ? 'Active' : 'Inactive'),
    },
  ];

  // Define filter configuration for user type, status, etc.
  const filterConfig = [
    { field: 'search', label: 'Search', type: 'text', placeholder: 'Search by name or email' },
    {
      field: 'userType',
      label: 'User Type',
      type: 'select',
      options: [
        { value: UserType.BORROWER, label: 'Borrower' },
        { value: UserType.SCHOOL_ADMIN, label: 'School Admin' },
        { value: UserType.UNDERWRITER, label: 'Underwriter' },
        { value: UserType.QC, label: 'QC' },
        { value: UserType.SYSTEM_ADMIN, label: 'System Admin' },
      ],
    },
    {
      field: 'isActive',
      label: 'Status',
      type: 'select',
      options: [
        { value: 'true', label: 'Active' },
        { value: 'false', label: 'Inactive' },
      ],
    },
  ];

  // Define row actions (edit, delete, reset password, etc.) with permission checks
  const actions = [
    {
      icon: <Edit />,
      label: 'Edit',
      onClick: handleEditUser,
      isVisible: () => checkPermission('users:update'),
    },
    {
      icon: <Delete />,
      label: 'Delete',
      onClick: handleDeleteClick,
      isVisible: () => checkPermission('users:delete'),
    },
    {
      icon: <LockReset />,
      label: 'Reset Password',
      onClick: handleResetPasswordClick,
      isVisible: () => checkPermission('users:resetPassword'),
    },
    {
      icon: <CheckCircle />,
      label: 'Activate',
      onClick: handleActivateClick,
      isVisible: (user: UserWithProfile) => !user.isActive && checkPermission('users:activate'),
    },
    {
      icon: <Block />,
      label: 'Deactivate',
      onClick: handleDeactivateClick,
      isVisible: (user: UserWithProfile) => user.isActive && checkPermission('users:deactivate'),
    },
  ];

  // Fetch users on component mount and when dependencies change
  useEffect(() => {
    dispatch(fetchUsers({ page, pageSize, filters: filters }));
  }, [dispatch, page, pageSize, filters]);

  return (
    <Page
      title="User Management"
      description="Manage user accounts and roles within the system"
      actions={
        checkPermission('users:create') ? (
          <Button
            variant="contained"
            color="primary"
            startIcon={<Add />}
            onClick={handleCreateUser}
          >
            Create User
          </Button>
        ) : null
      }
    >
      <DataTable
        data={users}
        columns={columns}
        loading={loading}
        totalItems={totalUsers}
        page={page}
        pageSize={pageSize}
        onPageChange={handlePageChange}
        onPageSizeChange={handlePageSizeChange}
        sorting={true}
        sortField={sortField || undefined}
        sortDirection={sortDirection}
        onSortChange={handleSortChange}
        filtering={true}
        filterConfig={filterConfig}
        filterOptions={filters ? Object.entries(filters).map(([key, value]) => ({ field: key, value })) : []}
        onFilterChange={handleFilterChange}
        actions={actions}
      />

      <ConfirmationDialog
        open={deleteDialogOpen}
        title="Delete User"
        message={`Are you sure you want to delete user ${selectedUser?.firstName} ${selectedUser?.lastName}?`}
        confirmLabel="Delete"
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeleteDialogOpen(false)}
        loading={loading}
      />

      <ConfirmationDialog
        open={resetDialogOpen}
        title="Reset Password"
        message={`Are you sure you want to reset the password for user ${selectedUser?.firstName} ${selectedUser?.lastName}?`}
        confirmLabel="Reset Password"
        onConfirm={handleResetPasswordConfirm}
        onCancel={() => setResetDialogOpen(false)}
        loading={loading}
      />

      <ConfirmationDialog
        open={activateDialogOpen}
        title="Activate User"
        message={`Are you sure you want to activate user ${selectedUser?.firstName} ${selectedUser?.lastName}?`}
        confirmLabel="Activate"
        onConfirm={handleActivateConfirm}
        onCancel={() => setActivateDialogOpen(false)}
        loading={loading}
      />

      <ConfirmationDialog
        open={deactivateDialogOpen}
        title="Deactivate User"
        message={`Are you sure you want to deactivate user ${selectedUser?.firstName} ${selectedUser?.lastName}?`}
        confirmLabel="Deactivate"
        onConfirm={handleDeactivateConfirm}
        onCancel={() => setDeactivateDialogOpen(false)}
        loading={loading}
      />
    </Page>
  );
};

export default UserList;