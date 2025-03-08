/**
 * Barrel file that exports all TypeScript types, interfaces, and enums
 * from the various type definition files in the loan management system frontend.
 * This file serves as a central export point to simplify imports throughout the application.
 */

// Import and re-export all application-related types
export * from './application.types';

// Import and re-export all authentication-related types
export * from './auth.types';

// Import and re-export all common utility types
export * from './common.types';

// Import and re-export all document-related types
export * from './document.types';

// Import and re-export all funding-related types
export * from './funding.types';

// Import and re-export all notification-related types
export * from './notification.types';

// Import and re-export all quality control-related types
export * from './qc.types';

// Import and re-export all school-related types
export * from './school.types';

// Import and re-export all underwriting-related types
export * from './underwriting.types';

// Import and re-export all user-related types
export * from './user.types';