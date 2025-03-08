# src/web/src/pages/users/UserDetail.tsx
```tsx
import React, { useState, useEffect, useCallback } from 'react'; // react ^18.2.0
import { useDispatch, useSelector } from 'react-redux'; // react-redux ^8.1.1
import { useParams, useNavigate } from 'react-router-dom'; // react-router-dom ^6.14.1
import {
  Typography,
  Button,
  Grid,
  Divider,
  Box,
  Card,
  CardContent,
  CardHeader,
  Chip,
  IconButton,
  Tooltip,
  Tab,
  Tabs,
} from '@mui/material'; // @mui/material ^5.14.0
import {
  Edit,
  Delete,
  LockReset,
  PersonAdd,
  ArrowBack,
  CheckCircle,
  Cancel,
  Lock,
  LockOpen,
} from '@mui/icons-material'; // @mui/icons-material ^5.14.0
import Page from '../../components/common/Page';
import UserForm from '../../components/UserManagement/UserForm';
import LoadingOverlay from '../../components/common/Loading/LoadingOverlay';
import ConfirmationDialog from '../../components/common/Confirmation/ConfirmationDialog';
import { UserWithProfile, UserType } from '../../types/user.types';
import {
  selectSelectedUser,
  selectUserLoading,
  selectUserError,
} from '../../store/slices/userSlice';
import {
  fetchUser,
  updateExistingUser,
  deleteExistingUser,
  resetPassword,
  activateExistingUser,
  deactivateExistingUser,
  clearUser,
} from '../../store/thunks/userThunks';

/**
 * Component that displays and manages user details
 */
const UserDetail: React.FC = () => {
  // Extract userId from URL parameters using useParams
  const { userId } = useParams<{ userId: string }>();

  // Initialize Redux dispatch and navigation functions
  const dispatch = useDispatch();
  const navigate = useNavigate();

  // Select user data, loading state, and error state from Redux store
  const user = useSelector(selectSelectedUser);
  const isLoading = useSelector(selectUserLoading);
  const error = useSelector(selectUserError);

  // Initialize state for edit mode, confirmation dialogs, and loading states
  const [editMode, setEditMode] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [resetPasswordDialogOpen, setResetPasswordDialogOpen] = useState(false);
  const [activateDialogOpen, setActivateDialogOpen] = useState(false);
  const [deactivateDialogOpen, setDeactivateDialogOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isResettingPassword, setIsResettingPassword] = useState(false);
  const [isActivating, setIsActivating] = useState(false);
  const [isDeactivating, setIsDeactivating] = useState(false);
  const [activeTab, setActiveTab] = useState(0);

  // Fetch user data when component mounts or userId changes
  useEffect(() => {
    if (userId) {
      dispatch(fetchUser(userId));
    }

    return () => {
      dispatch(clearUser());
    };
  }, [dispatch, userId]);

  // Handle user edit form submission
  const handleFormSubmit = useCallback(() => {
    setEditMode(false);
  }, []);

  // Handle user deletion with confirmation
  const handleDeleteClick = useCallback(() => {
    setDeleteDialogOpen(true);
  }, []);

  const handleDeleteConfirm = useCallback(async () => {
    if (userId) {
      setIsDeleting(true);
      await dispatch(deleteExistingUser(userId));
      setIsDeleting(false);
      setDeleteDialogOpen(false);
      navigate('/users');
    }
  }, [dispatch, navigate, userId]);

  const handleDeleteCancel = useCallback(() => {
    setDeleteDialogOpen(false);
  }, []);

  // Handle password reset with confirmation
  const handleResetPasswordClick = useCallback(() => {
    setResetPasswordDialogOpen(true);
  }, []);

  const handleResetPasswordConfirm = useCallback(async () => {
    if (userId) {
      setIsResettingPassword(true);
      await dispatch(resetPassword(userId));
      setIsResettingPassword(false);
      setResetPasswordDialogOpen(false);
    }
  }, [dispatch, userId]);

  const handleResetPasswordCancel = useCallback(() => {
    setResetPasswordDialogOpen(false);
  }, []);

  // Handle user activation/deactivation
  const handleActivateClick = useCallback(() => {
    setActivateDialogOpen(true);
  }, []);

  const handleActivateConfirm = useCallback(async () => {
    if (userId) {
      setIsActivating(true);
      await dispatch(activateExistingUser(userId));
      setIsActivating(false);
      setActivateDialogOpen(false);
    }
  }, [dispatch, userId]);

  const handleActivateCancel = useCallback(() => {
    setActivateDialogOpen(false);
  }, []);

  const handleDeactivateClick = useCallback(() => {
    setDeactivateDialogOpen(true);
  }, []);

  const handleDeactivateConfirm = useCallback(async () => {
    if (userId) {
      setIsDeactivating(true);
      await dispatch(deactivateExistingUser(userId));
      setIsDeactivating(false);
      setDeactivateDialogOpen(false);
    }
  }, [dispatch, userId]);

  const handleDeactivateCancel = useCallback(() => {
    setDeactivateDialogOpen(false);
  }, []);

  // Handle navigation back to user list
  const handleBackClick = useCallback(() => {
    navigate('/users');
  }, [navigate]);

  // Toggle edit mode on/off
  const handleEditClick = useCallback(() => {
    setEditMode(true);
  }, []);

  // Cancel edit mode and return to view mode
  const handleCancelEdit = useCallback(() => {
    setEditMode(false);
  }, []);

  // Handles tab selection change
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Render page with user information or edit form based on edit mode
  return (
    <Page
      title="User Details"
      actions={
        <>
          <Tooltip title="Back to User List">
            <IconButton onClick={handleBackClick} aria-label="Back to User List">
              <ArrowBack />
            </IconButton>
          </Tooltip>
          {!editMode && user && (
            <>
              <Tooltip title="Edit User">
                <IconButton onClick={handleEditClick} aria-label="Edit User">
                  <Edit />
                </IconButton>
              </Tooltip>
              <Tooltip title="Delete User">
                <IconButton onClick={handleDeleteClick} aria-label="Delete User">
                  <Delete />
                </IconButton>
              </Tooltip>
              <Tooltip title="Reset Password">
                <IconButton onClick={handleResetPasswordClick} aria-label="Reset Password">
                  <LockReset />
                </IconButton>
              </Tooltip>
              {user.isActive ? (
                <Tooltip title="Deactivate User">
                  <IconButton onClick={handleDeactivateClick} aria-label="Deactivate User">
                    <Lock />
                  </IconButton>
                </Tooltip>
              ) : (
                <Tooltip title="Activate User">
                  <IconButton onClick={handleActivateClick} aria-label="Activate User">
                    <LockOpen />
                  </IconButton>
                </Tooltip>
              )}
            </>
          )}
        </>
      }
    >
      {/* Render edit form when in edit mode */}
      {editMode && user ? (
        <UserForm user={user} onSuccess={handleFormSubmit} onCancel={handleCancelEdit} />
      ) : (
        /* Render user information when not in edit mode */
        user && (
          <>
            <Card>
              <CardHeader
                title={`${user.firstName} ${user.lastName}`}
                subheader={user.email}
              />
              <CardContent>
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={12} md={6}>
                    <Typography variant="body1">
                      User Type: {user.userType}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Chip
                      icon={user.isActive ? <CheckCircle /> : <Cancel />}
                      label={user.isActive ? 'Active' : 'Inactive'}
                      color={user.isActive ? 'success' : 'error'}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs value={activeTab} onChange={handleTabChange} aria-label="user details tabs">
                <Tab label="Profile" />
                <Tab label="Roles & Permissions" />
              </Tabs>
            </Box>
            {activeTab === 0 && (
              <Card>
                <CardContent>
                  <Typography variant="h6">Profile Information</Typography>
                  <Divider />
                  {/* Display profile information based on user type */}
                  {user.userType === UserType.BORROWER && (
                    <Typography variant="body2">Borrower Profile Details...</Typography>
                  )}
                  {user.userType === UserType.SCHOOL_ADMIN && (
                    <Typography variant="body2">School Admin Profile Details...</Typography>
                  )}
                  {user.userType === UserType.UNDERWRITER && (
                    <Typography variant="body2">Underwriter Profile Details...</Typography>
                  )}
                </CardContent>
              </Card>
            )}
            {activeTab === 1 && (
              <Card>
                <CardContent>
                  <Typography variant="h6">Roles & Permissions</Typography>
                  <Divider />
                  {/* Display roles and permissions information */}
                  <Typography variant="body2">Roles and Permissions Details...</Typography>
                </CardContent>
              </Card>
            )}
          </>
        )
      )}

      {/* Render confirmation dialogs for destructive actions */}
      <ConfirmationDialog
        open={deleteDialogOpen}
        title="Delete User"
        message="Are you sure you want to delete this user? This action cannot be undone."
        confirmLabel="Delete"
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
        loading={isDeleting}
      />
      <ConfirmationDialog
        open={resetPasswordDialogOpen}
        title="Reset Password"
        message="Are you sure you want to reset this user's password? A new password will be generated and sent to the user."
        confirmLabel="Reset Password"
        onConfirm={handleResetPasswordConfirm}
        onCancel={handleResetPasswordCancel}
        loading={isResettingPassword}
      />
      <ConfirmationDialog
        open={activateDialogOpen}
        title="Activate User"
        message="Are you sure you want to activate this user?"
        confirmLabel="Activate"
        onConfirm={handleActivateConfirm}
        onCancel={handleActivateCancel}
        loading={isActivating}
      />
      <ConfirmationDialog
        open={deactivateDialogOpen}
        title="Deactivate User"
        message="Are you sure you want to deactivate this user?"
        confirmLabel="Deactivate"
        onConfirm={handleDeactivateConfirm}
        onCancel={handleDeactivateCancel}
        loading={isDeactivating}
      />
    </Page>
  );
};

export default UserDetail;