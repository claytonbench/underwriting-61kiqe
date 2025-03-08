/**
 * Barrel file that exports all custom React hooks used throughout the loan management system
 * This simplifies imports by allowing consumers to import multiple hooks from a single location.
 * 
 * @example
 * // Instead of multiple imports
 * import { useAuth } from './hooks/useAuth';
 * import { useForm } from './hooks/useForm';
 * 
 * // Use a single import
 * import { useAuth, useForm } from './hooks';
 */

// Export authentication hook
export { useAuth } from './useAuth';

// Export form management hook
export { default as useForm } from './useForm';

// Export notifications hook
export { useNotifications } from './useNotifications';

// Export permissions hook
export { usePermissions } from './usePermissions';