// Centralizes and re-exports all Redux action creators from the various domain-specific action files
// in the loan management system. This file serves as a single entry point for importing actions
// throughout the application, simplifying imports and promoting code organization.

// Import all application-related action creators
import * as applicationActions from './applicationActions';

// Import all authentication-related action creators
import * as authActions from './authActions';

// Import all document-related action creators
import * as documentActions from './documentActions';

// Import all funding-related action creators
import * as fundingActions from './fundingActions';

// Import all notification-related action creators
import * as notificationActions from './notificationActions';

// Import all quality control-related action creators
import * as qcActions from './qcActions';

// Import all school-related action creators
import * as schoolActions from './schoolActions';

// Import all underwriting-related action creators
import * as underwritingActions from './underwritingActions';

// Import all user management-related action creators
import * as userActions from './userActions';

// Re-export all application action creators
export * as applicationActions from './applicationActions';

// Re-export all authentication action creators
export * as authActions from './authActions';

// Re-export all document action creators
export * as documentActions from './documentActions';

// Re-export all funding action creators
export * as fundingActions from './fundingActions';

// Re-export all notification action creators
export * as notificationActions from './notificationActions';

// Re-export all quality control action creators
export * as qcActions from './qcActions';

// Re-export all school action creators
export * as schoolActions from './schoolActions';

// Re-export all underwriting action creators
export * as underwritingActions from './underwritingActions';

// Re-export all user management action creators
export * as userActions from './userActions';