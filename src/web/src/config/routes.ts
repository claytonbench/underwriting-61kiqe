import React from 'react';
import { UserType } from '../types/auth.types';

/**
 * Enum defining possible layout types for routes
 */
export enum LayoutType {
  AUTH = 'auth',
  DASHBOARD = 'dashboard'
}

/**
 * Interface defining the structure of route configuration objects
 */
export interface RouteConfig {
  path: string;
  component: React.LazyExoticComponent<React.ComponentType<any>>;
  layout: LayoutType;
  exact: boolean;
  roles: UserType[] | null; // null means accessible to all
  title: string;
}

// Path constants
export const LOGIN_PATH = '/login';
export const DASHBOARD_PATH = '/dashboard';
export const ERROR_PATHS = {
  FORBIDDEN: '/403',
  NOT_FOUND: '/404',
  SERVER_ERROR: '/500'
};

// Auth pages
const Login = React.lazy(() => import('../pages/auth/Login'));
const ForgotPassword = React.lazy(() => import('../pages/auth/ForgotPassword'));
const ResetPassword = React.lazy(() => import('../pages/auth/ResetPassword'));

// Dashboard pages
const AdminDashboard = React.lazy(() => import('../pages/dashboard/AdminDashboard'));
const BorrowerDashboard = React.lazy(() => import('../pages/borrower/BorrowerDashboard'));
const SchoolAdminDashboard = React.lazy(() => import('../pages/school/SchoolAdminDashboard'));
const UnderwriterDashboard = React.lazy(() => import('../pages/underwriting/UnderwriterDashboard'));

// Application pages
const ApplicationList = React.lazy(() => import('../pages/application/ApplicationList'));
const ApplicationDetail = React.lazy(() => import('../pages/application/ApplicationDetail'));
const ApplicationNew = React.lazy(() => import('../pages/application/ApplicationNew'));

// Document pages
const DocumentList = React.lazy(() => import('../pages/documents/DocumentList'));
const DocumentDetail = React.lazy(() => import('../pages/documents/DocumentDetail'));
const DocumentSign = React.lazy(() => import('../pages/documents/DocumentSign'));

// School pages
const SchoolList = React.lazy(() => import('../pages/school/SchoolList'));
const SchoolDetail = React.lazy(() => import('../pages/school/SchoolDetail'));
const SchoolNew = React.lazy(() => import('../pages/school/SchoolNew'));
const SchoolEdit = React.lazy(() => import('../pages/school/SchoolEdit'));

// Program pages
const ProgramList = React.lazy(() => import('../pages/school/ProgramList'));
const ProgramDetail = React.lazy(() => import('../pages/school/ProgramDetail'));
const ProgramNew = React.lazy(() => import('../pages/school/ProgramNew'));
const ProgramEdit = React.lazy(() => import('../pages/school/ProgramEdit'));

// User pages
const UserList = React.lazy(() => import('../pages/users/UserList'));
const UserDetail = React.lazy(() => import('../pages/users/UserDetail'));
const UserNew = React.lazy(() => import('../pages/users/UserNew'));
const UserEdit = React.lazy(() => import('../pages/users/UserEdit'));

// Underwriting pages
const UnderwritingQueue = React.lazy(() => import('../pages/underwriting/UnderwritingQueue'));
const ApplicationReview = React.lazy(() => import('../pages/underwriting/ApplicationReview'));

// QC pages
const QCList = React.lazy(() => import('../pages/qc/QCList'));
const QCDetail = React.lazy(() => import('../pages/qc/QCDetail'));

// Funding pages
const FundingList = React.lazy(() => import('../pages/funding/FundingList'));
const FundingDetail = React.lazy(() => import('../pages/funding/FundingDetail'));

// Report pages
const ReportDashboard = React.lazy(() => import('../pages/reports/ReportDashboard'));
const ApplicationVolumeReport = React.lazy(() => import('../pages/reports/ApplicationVolumeReport'));
const UnderwritingReport = React.lazy(() => import('../pages/reports/UnderwritingReport'));
const DocumentStatusReport = React.lazy(() => import('../pages/reports/DocumentStatusReport'));
const FundingReport = React.lazy(() => import('../pages/reports/FundingReport'));

// Settings pages
const ProfileSettings = React.lazy(() => import('../pages/settings/ProfileSettings'));
const SystemSettings = React.lazy(() => import('../pages/settings/SystemSettings'));
const EmailTemplates = React.lazy(() => import('../pages/settings/EmailTemplates'));
const EditEmailTemplate = React.lazy(() => import('../pages/settings/EditEmailTemplate'));

// Error pages
const Error403 = React.lazy(() => import('../pages/errors/Error403'));
const Error404 = React.lazy(() => import('../pages/errors/Error404'));
const Error500 = React.lazy(() => import('../pages/errors/Error500'));

/**
 * Array of route configurations for the application.
 * Each route defines its path, component, layout, access control, and metadata.
 */
export const routes: RouteConfig[] = [
  // Auth routes (accessible to everyone)
  {
    path: '/login',
    component: Login,
    layout: LayoutType.AUTH,
    exact: true,
    roles: null,
    title: 'Login'
  },
  {
    path: '/forgot-password',
    component: ForgotPassword,
    layout: LayoutType.AUTH,
    exact: true,
    roles: null,
    title: 'Forgot Password'
  },
  {
    path: '/reset-password',
    component: ResetPassword,
    layout: LayoutType.AUTH,
    exact: true,
    roles: null,
    title: 'Reset Password'
  },
  
  // Dashboard routes (role-specific)
  {
    path: '/dashboard',
    component: AdminDashboard,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN],
    title: 'Dashboard'
  },
  {
    path: '/borrower',
    component: BorrowerDashboard,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.BORROWER, UserType.CO_BORROWER],
    title: 'Borrower Dashboard'
  },
  {
    path: '/school-admin',
    component: SchoolAdminDashboard,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SCHOOL_ADMIN],
    title: 'School Admin Dashboard'
  },
  {
    path: '/underwriter',
    component: UnderwriterDashboard,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.UNDERWRITER],
    title: 'Underwriter Dashboard'
  },
  
  // Application routes
  {
    path: '/applications',
    component: ApplicationList,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN, UserType.SCHOOL_ADMIN, UserType.UNDERWRITER, UserType.QC],
    title: 'Applications'
  },
  {
    path: '/applications/:id',
    component: ApplicationDetail,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN, UserType.SCHOOL_ADMIN, UserType.UNDERWRITER, UserType.QC, UserType.BORROWER, UserType.CO_BORROWER],
    title: 'Application Details'
  },
  {
    path: '/applications/new',
    component: ApplicationNew,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN, UserType.SCHOOL_ADMIN, UserType.BORROWER],
    title: 'New Application'
  },
  
  // Document routes
  {
    path: '/documents',
    component: DocumentList,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN, UserType.SCHOOL_ADMIN, UserType.BORROWER, UserType.CO_BORROWER],
    title: 'Documents'
  },
  {
    path: '/documents/:id',
    component: DocumentDetail,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN, UserType.SCHOOL_ADMIN, UserType.BORROWER, UserType.CO_BORROWER, UserType.UNDERWRITER, UserType.QC],
    title: 'Document Details'
  },
  {
    path: '/documents/:id/sign',
    component: DocumentSign,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN, UserType.SCHOOL_ADMIN, UserType.BORROWER, UserType.CO_BORROWER],
    title: 'Sign Document'
  },
  
  // School routes
  {
    path: '/schools',
    component: SchoolList,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN],
    title: 'Schools'
  },
  {
    path: '/schools/:id',
    component: SchoolDetail,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN, UserType.SCHOOL_ADMIN],
    title: 'School Details'
  },
  {
    path: '/schools/new',
    component: SchoolNew,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN],
    title: 'New School'
  },
  {
    path: '/schools/:id/edit',
    component: SchoolEdit,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN],
    title: 'Edit School'
  },
  
  // Program routes
  {
    path: '/programs',
    component: ProgramList,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN, UserType.SCHOOL_ADMIN],
    title: 'Programs'
  },
  {
    path: '/programs/:id',
    component: ProgramDetail,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN, UserType.SCHOOL_ADMIN],
    title: 'Program Details'
  },
  {
    path: '/programs/new',
    component: ProgramNew,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN, UserType.SCHOOL_ADMIN],
    title: 'New Program'
  },
  {
    path: '/programs/:id/edit',
    component: ProgramEdit,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN, UserType.SCHOOL_ADMIN],
    title: 'Edit Program'
  },
  
  // User routes
  {
    path: '/users',
    component: UserList,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN],
    title: 'Users'
  },
  {
    path: '/users/:id',
    component: UserDetail,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN],
    title: 'User Details'
  },
  {
    path: '/users/new',
    component: UserNew,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN],
    title: 'New User'
  },
  {
    path: '/users/:id/edit',
    component: UserEdit,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN],
    title: 'Edit User'
  },
  
  // Underwriting routes
  {
    path: '/underwriting/queue',
    component: UnderwritingQueue,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.UNDERWRITER, UserType.SYSTEM_ADMIN],
    title: 'Underwriting Queue'
  },
  {
    path: '/underwriting/review/:id',
    component: ApplicationReview,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.UNDERWRITER, UserType.SYSTEM_ADMIN],
    title: 'Application Review'
  },
  
  // QC routes
  {
    path: '/qc',
    component: QCList,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.QC, UserType.SYSTEM_ADMIN],
    title: 'Quality Control'
  },
  {
    path: '/qc/:id',
    component: QCDetail,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.QC, UserType.SYSTEM_ADMIN],
    title: 'QC Review'
  },
  
  // Funding routes
  {
    path: '/funding',
    component: FundingList,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN, UserType.QC],
    title: 'Funding'
  },
  {
    path: '/funding/:id',
    component: FundingDetail,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN, UserType.QC],
    title: 'Funding Details'
  },
  
  // Report routes
  {
    path: '/reports',
    component: ReportDashboard,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN, UserType.SCHOOL_ADMIN, UserType.UNDERWRITER, UserType.QC],
    title: 'Reports'
  },
  {
    path: '/reports/application-volume',
    component: ApplicationVolumeReport,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN, UserType.SCHOOL_ADMIN],
    title: 'Application Volume Report'
  },
  {
    path: '/reports/underwriting',
    component: UnderwritingReport,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN, UserType.UNDERWRITER],
    title: 'Underwriting Report'
  },
  {
    path: '/reports/document-status',
    component: DocumentStatusReport,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN, UserType.SCHOOL_ADMIN],
    title: 'Document Status Report'
  },
  {
    path: '/reports/funding',
    component: FundingReport,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN, UserType.QC],
    title: 'Funding Report'
  },
  
  // Settings routes
  {
    path: '/settings/profile',
    component: ProfileSettings,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN, UserType.SCHOOL_ADMIN, UserType.UNDERWRITER, UserType.QC, UserType.BORROWER, UserType.CO_BORROWER],
    title: 'Profile Settings'
  },
  {
    path: '/settings/system',
    component: SystemSettings,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN],
    title: 'System Settings'
  },
  {
    path: '/settings/email-templates',
    component: EmailTemplates,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN],
    title: 'Email Templates'
  },
  {
    path: '/settings/email-templates/:id',
    component: EditEmailTemplate,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: [UserType.SYSTEM_ADMIN],
    title: 'Edit Email Template'
  },
  
  // Error routes (accessible to everyone)
  {
    path: '/403',
    component: Error403,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: null,
    title: 'Access Denied'
  },
  {
    path: '/404',
    component: Error404,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: null,
    title: 'Page Not Found'
  },
  {
    path: '/500',
    component: Error500,
    layout: LayoutType.DASHBOARD,
    exact: true,
    roles: null,
    title: 'Server Error'
  },
  
  // Catch-all route (must be the last one)
  {
    path: '*',
    component: Error404,
    layout: LayoutType.DASHBOARD,
    exact: false,
    roles: null,
    title: 'Page Not Found'
  }
];