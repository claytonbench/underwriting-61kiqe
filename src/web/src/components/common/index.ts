/**
 * Common UI Components
 * 
 * This barrel file exports all common UI components from their respective directories,
 * providing a centralized import point for reusable components throughout the application.
 * 
 * Implements the component organization pattern with barrel exports as specified
 * in the technical requirements to ensure consistent usage across the loan management system.
 */

// Breadcrumbs
import Breadcrumbs from './Breadcrumbs';

// Card
import Card from './Card';

// Confirmation
import { ConfirmationDialog } from './Confirmation';

// Loading components
import { LoadingSpinner, LoadingOverlay } from './Loading';

// StatusBadge
import StatusBadge, { StatusBadgeProps } from './StatusBadge';

// Stepper
import Stepper from './Stepper';

// DataTable and related components
import DataTable, {
  TableActions,
  TableFilters,
  TablePagination,
  DataTableProps,
  TableColumn,
  TableAction,
  TableActionsProps,
  TableFiltersProps,
  FilterConfig,
  TablePaginationProps
} from './DataTable';

// FileUpload
import FileUpload from './FileUpload';

// Page components
import Page, { PageHeader } from './Page';

// Export everything
export {
  // Navigation
  Breadcrumbs,
  
  // Layout
  Card,
  Page,
  PageHeader,
  
  // Feedback
  ConfirmationDialog,
  LoadingSpinner,
  LoadingOverlay,
  StatusBadge,
  StatusBadgeProps,
  
  // Workflow
  Stepper,
  
  // Data Display
  DataTable,
  TableActions,
  TableFilters,
  TablePagination,
  DataTableProps,
  TableColumn,
  TableAction,
  TableActionsProps,
  TableFiltersProps,
  FilterConfig,
  TablePaginationProps,
  
  // Input
  FileUpload
};