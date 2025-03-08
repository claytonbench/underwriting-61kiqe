/**
 * Main barrel file that exports all components from their respective directories,
 * providing a centralized import point for components throughout the application.
 * This simplifies imports by allowing consumers to import any component from a single location.
 */

// Import all common UI components
import * as CommonComponents from './common';

// Import all form element components
import * as FormElements from './FormElements';

// Import the main application bar component
import ApplicationAppBar, { NavMenu, UserMenu, NotificationBell } from './AppBar';

// Import all application form components
import * as ApplicationForm from './ApplicationForm';

// Import all application review components
import * as ApplicationReview from './ApplicationReview';

// Import all application status components
import * as ApplicationStatus from './ApplicationStatus';

// Import all document signing components
import * as DocumentSigning from './DocumentSigning';

// Import all notification components
import * as Notifications from './Notifications';

// Import all QC review components
import * as QCReview from './QCReview';

// Import all school management components
import * as SchoolManagement from './SchoolManagement';

// Import all user management components
import * as UserManagement from './UserManagement';

// Re-export all common UI components
export * from './common';

// Re-export all form element components
export * from './FormElements';

// Export the main application bar component with a renamed export
export { ApplicationAppBar as AppBar };

// Re-export the navigation menu component
export { NavMenu };

// Re-export the user menu component
export { UserMenu };

// Re-export the notification bell component
export { NotificationBell };

// Re-export all application form components
export * from './ApplicationForm';

// Re-export all application review components
export * from './ApplicationReview';

// Re-export all application status components
export * from './ApplicationStatus';

// Re-export all document signing components
export * from './DocumentSigning';

// Re-export all notification components
export * from './Notifications';

// Re-export all QC review components
export * from './QCReview';

// Re-export all school management components
export * from './SchoolManagement';

// Re-export all user management components
export * from './UserManagement';