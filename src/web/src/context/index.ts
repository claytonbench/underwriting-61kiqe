/**
 * Barrel file that exports all React context providers and hooks from the context directory.
 * Provides a centralized import point for authentication and notification contexts throughout the application.
 */

// Export authentication context, provider, and hook
export { AuthContext, AuthProvider, useAuthContext } from './AuthContext';

// Export notification context, provider, and hook
export { NotificationContext, NotificationProvider, useNotifications } from './NotificationContext';