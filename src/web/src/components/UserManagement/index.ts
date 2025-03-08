// Import the UserForm component for re-export
import UserForm from './UserForm'; // ./UserForm

// Import the PermissionSelection component for re-export
import PermissionSelection from './PermissionSelection'; // ./PermissionSelection

/**
 * Exports the UserForm component for creating and editing users.
 * @component
 */
export { UserForm };

/**
 * Exports the PermissionSelection component for selecting user permissions.
 * @component
 */
export { PermissionSelection };

/**
 * Default export of all UserManagement components for convenient importing.
 */
export default {
  UserForm,
  PermissionSelection,
};