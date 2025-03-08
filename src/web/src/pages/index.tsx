import React, { Suspense, lazy } from 'react'; // react v18.2.0
import { Routes, Route, Navigate, useLocation } from 'react-router-dom'; // react-router-dom v6.14.1
import { CircularProgress } from '@mui/material'; // @mui/material v5.14.0
import { routes as routeConfigs, RouteConfig, LayoutType, LOGIN_PATH, DASHBOARD_PATH, ERROR_PATHS } from '../config/routes';
import { AuthLayout, DashboardLayout } from '../layouts';
import { useAuthContext } from '../context/AuthContext';
import { UserType } from '../types/auth.types';

/**
 * Main router component that handles all application routes
 * @returns Rendered router with all routes and layouts
 */
const AppRouter: React.FC = () => {
  // LD1: Get authentication state from useAuthContext hook
  const { state } = useAuthContext();
  // LD1: Get current location from useLocation hook
  const location = useLocation();

  // LD1: Render Routes component with all configured routes
  return (
    <Routes>
      {/* LD1: For each route, determine if user has access based on role */}
      {routeConfigs.map((route: RouteConfig) => (
        <Route
          key={route.path}
          path={route.path}
          element={
            // LD1: Implement route protection with redirection to login or error pages
            <ProtectedRoute route={route}>
              {/* LD1: Apply appropriate layout (AuthLayout or DashboardLayout) based on route configuration */}
              <RouteWithLayout route={route} />
            </ProtectedRoute>
          }
        />
      ))}
    </Routes>
  );
};

/**
 * Component that protects routes based on authentication state and user role
 * @param props 
 * @returns Rendered component or redirect
 */
const ProtectedRoute: React.FC<{ route: RouteConfig; children: React.ReactNode }> = ({ route, children }) => {
  // LD1: Get authentication state from useAuthContext hook
  const { state } = useAuthContext();

  // LD1: Check if user is authenticated
  if (!state.isAuthenticated) {
    // LD1: If not authenticated, redirect to login page with return URL
    return <Navigate to={`${LOGIN_PATH}?returnUrl=${location.pathname}`} replace />;
  }

  // LD1: If authenticated, check if user has required role
  if (route.roles && !route.roles.includes(state.user?.userType as UserType)) {
    // LD1: If user doesn't have required role, redirect to forbidden page
    return <Navigate to={ERROR_PATHS.FORBIDDEN} replace />;
  }

  // LD1: If user has required role, render the component
  return <>{children}</>;
};

/**
 * Component that wraps a route with the appropriate layout
 */
const RouteWithLayout: React.FC<{ route: RouteConfig }> = ({ route }) => {
  // LD1: Determine which layout to use based on layout type
  const getLayout = (layout: LayoutType) => {
    switch (layout) {
      case LayoutType.AUTH:
        return AuthLayout;
      case LayoutType.DASHBOARD:
        return DashboardLayout;
      default:
        return React.Fragment; // No layout
    }
  };

  const LayoutComponent = getLayout(route.layout);

  // LD1: Render the component wrapped in the appropriate layout
  return (
    <LayoutComponent
      title={route.title}
    >
      {/* LD1: Use Suspense with fallback for lazy-loaded components */}
      <Suspense fallback={<LoadingFallback />}>
        {React.createElement(route.component)}
      </Suspense>
    </LayoutComponent>
  );
};

/**
 * Component displayed while lazy-loaded components are loading
 * @returns Loading indicator centered on the page
 */
const LoadingFallback: React.FC = () => {
  // LD1: Render a centered CircularProgress component
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      width: '100%'
    }}>
      <CircularProgress />
    </div>
  );
};

// IE3: Export AppRouter as the default export
export default AppRouter;