import React from 'react'; // react ^18.2.0
import { useNavigate } from 'react-router-dom'; // react-router-dom ^6.14.0
import { Alert } from '@mui/material'; // @mui/material ^5.14.0
import Page from '../../components/common/Page';
import UserForm from '../../components/UserManagement/UserForm';
import { usePermissions } from '../../hooks/usePermissions';

/**
 * Component for creating new users in the system
 */
const UserNew: React.FC = () => {
  // Get navigation function using useNavigate
  const navigate = useNavigate();

  // Get permission checking function using usePermissions
  const { checkPermission } = usePermissions();

  // Check if user has permission to create users
  const hasCreatePermission = checkPermission('users:create');

  /**
   * Handles successful user creation
   */
  const handleSuccess = () => {
    // Navigate to the user list page
    navigate('/users');
  };

  /**
   * Handles form cancellation
   */
  const handleCancel = () => {
    // Navigate to the user list page
    navigate('/users');
  };

  return (
    <Page title="Create New User">
      {/* If user has permission, render UserForm component */}
      {hasCreatePermission ? (
        <UserForm
          user={null} // null user indicates creation mode
          onSuccess={handleSuccess}
          onCancel={handleCancel}
        />
      ) : (
        // If user doesn't have permission, render permission error alert
        <Alert severity="error">
          You do not have permission to create users.
        </Alert>
      )}
    </Page>
  );
};

export default UserNew;