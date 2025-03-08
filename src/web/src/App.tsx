import React, { Suspense, lazy, useEffect } from 'react'; // react v18.0+
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'; // react-router-dom v6.14.1
import { Provider } from 'react-redux'; // react-redux v8.1.1
import { CssBaseline, CircularProgress } from '@mui/material'; // @mui/material v5.14.0
import { ThemeProvider } from '@mui/material/styles'; // @mui/material v5.14.0

import { routes, LayoutType } from './config/routes';
import { AuthProvider, useAuthContext } from './context/AuthContext';
import { NotificationProvider } from './context/NotificationContext';
import { AuthLayout, DashboardLayout } from './layouts';
import store from './store';

/**
 * Main application component that sets up providers and routing
 */
const App: React.FC = () => {
  return (
    <Provider store={store}>
      <ThemeProvider>
        <CssBaseline />
        <AuthProvider>
          <NotificationProvider>
            <BrowserRouter>
              <AppRoutes />
            </BrowserRouter>
          </NotificationProvider>
        </AuthProvider>
      </ThemeProvider>
    </Provider>
  );
};

/**
 * Component that handles the application routing based on authentication state and user roles
 */
const AppRoutes: React.FC = () => {
  const { state } = useAuthContext();
  const location = useLocation();

  return (
    <Suspense fallback={<CircularProgress />}>
      <Routes>
        {routes.map((route) => (
          <Route
            key={route.path}
            path={route.path}
            element={
              <ProtectedRoute
                component={route.component}
                layout={route.layout}
                roles={route.roles}
                path={route.path}
                exact={route.exact}
              />
            }
          />
        ))}
      </Routes>
    </Suspense>
  );
};

/**
 * Component that handles route protection based on authentication and role
 */
interface ProtectedRouteProps {
  component: React.ComponentType<any>;
  layout: LayoutType;
  roles: any;
  path: string;
  exact: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  component: Component,
  layout: LayoutType,
  roles,
  path,
  exact,
}) => {
  const { state } = useAuthContext();
  const location = useLocation();

  // Check if user is authenticated
  if (!state.isAuthenticated) {
    // Redirect to login page with return URL
    return <Navigate to={`/login?returnUrl=${path}`} replace />;
  }

  // Check if user has required role
  if (roles && !roles.includes(state.user?.userType)) {
    // Redirect to 403 page if user doesn't have required role
    return <Navigate to="/403" replace />;
  }

  let LayoutComponent;
  switch (LayoutType) {
    case LayoutType.AUTH:
      LayoutComponent = AuthLayout;
      break;
    case LayoutType.DASHBOARD:
      LayoutComponent = DashboardLayout;
      break;
    default:
      LayoutComponent = DashboardLayout;
      break;
  }

  // Render the component inside the specified layout
  return (
    <LayoutComponent>
      <Component />
    </LayoutComponent>
  );
};

export default App;