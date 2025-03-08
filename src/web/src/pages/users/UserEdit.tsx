import React, { useEffect } from 'react'; // react ^18.2.0
import { useParams, useNavigate } from 'react-router-dom'; // react-router-dom ^6.14.1
import { useSelector, useDispatch } from 'react-redux'; // react-redux ^8.1.1
import { Grid, Typography, Box, Alert, Button } from '@mui/material'; // @mui/material ^5.14.0
import Page from '../../components/common/Page';
import Breadcrumbs from '../../components/common/Breadcrumbs';
import UserForm from '../../components/UserManagement/UserForm';
import LoadingOverlay from '../../components/common/Loading';
import {
  selectSelectedUser,
  selectUserLoading,
  selectUserError,
} from '../../store/slices/userSlice';
import {
  fetchUser,
  updateExistingUser,
  clearUser,
} from '../../store/thunks/userThunks';
import { usePermissions } from '../../hooks/usePermissions';

/**
 * Component for editing an existing user
 * Fetches user data, displays a form, and handles updates
 */
const UserEdit: React.FC = () => {
  // Get userId from URL parameters
  const { id: userId } = useParams<{ id: string }>();

  // Get dispatch function
  const dispatch = useDispatch();

  // Get navigation function
  const navigate = useNavigate();

  // Get selected user, loading state, and error from Redux store
  const selectedUser = useSelector(selectSelectedUser);
  const loading = useSelector(selectUserLoading);
  const error = useSelector(selectUserError);

  // Check user permissions
  const { checkPermission } = usePermissions();
  const canEditUsers = checkPermission('users:edit');

  // Fetch user data when component mounts or userId changes
  useEffect(() => {
    if (userId) {
      dispatch(fetchUser(userId));
    }
  }, [dispatch, userId]);

  // Clear user data when component unmounts
  useEffect(() => {
    return () => {
      dispatch(clearUser());
    };
  }, [dispatch]);

  /**
   * Handles form submission
   * @param formData Form data to update user
   */
  const handleFormSubmit = (formData: Record<string, any>) => {
    if (userId) {
      dispatch(updateExistingUser({ userId, userData: formData }))
        .unwrap()
        .then(() => {
          // Navigate to user list page on success
          navigate('/users');
        });
    }
  };

  /**
   * Handles form cancel
   */
  const handleFormCancel = () => {
    // Navigate back to user list page
    navigate('/users');
  };

  // If user doesn't have permission, redirect to 403 page
  if (!canEditUsers) {
    return (
      <Page title="Access Denied">
        <Alert severity="error">You do not have permission to edit users.</Alert>
        <Button onClick={() => navigate('/dashboard')}>Go to Dashboard</Button>
      </Page>
    );
  }

  // If userId is valid but user data couldn't be found
  if (userId && !selectedUser && !loading && !error) {
    return (
      <Page title="User Not Found">
        <Alert severity="warning">User with ID {userId} not found.</Alert>
        <Button onClick={() => navigate('/users')}>Go to User List</Button>
      </Page>
    );
  }

  return (
    <Page title="Edit User" className="user-edit-page">
      <Breadcrumbs
        breadcrumbs={[
          { path: '/users', label: 'Users' },
          { path: '', label: 'Edit User' },
        ]}
      />

      {/* Show loading overlay when loading is true */}
      {loading && <LoadingOverlay isLoading={true} message="Loading user data..." />}

      {/* Display error message if there's an error */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* UserForm component for editing user details */}
      {selectedUser && (
        <UserForm
          user={selectedUser}
          onSuccess={handleFormSubmit}
          onCancel={handleFormCancel}
        />
      )}
    </Page>
  );
};

export default UserEdit;