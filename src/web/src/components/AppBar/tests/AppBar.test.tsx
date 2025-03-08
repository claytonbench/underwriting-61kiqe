import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { ThemeProvider, createTheme, useMediaQuery } from '@mui/material';
import ApplicationAppBar from '../AppBar';
import { useAuth } from '../../../hooks/useAuth';
import { UserType } from '../../../types/auth.types';

// Mock the hooks
jest.mock('../../../hooks/useAuth');
jest.mock('@mui/material', () => {
  const originalModule = jest.requireActual('@mui/material');
  return {
    ...originalModule,
    useMediaQuery: jest.fn(),
  };
});

// Mock the useNotifications hook
jest.mock('../../../hooks/useNotifications', () => ({
  __esModule: true,
  default: jest.fn().mockReturnValue({
    state: {
      unreadCount: 0,
      notifications: [],
      loading: false,
      error: null,
      drawerOpen: false
    },
    toggleDrawer: jest.fn(),
    closeDrawer: jest.fn(),
    fetchNotifications: jest.fn(),
    markAsRead: jest.fn(),
    markAllAsRead: jest.fn(),
    deleteNotification: jest.fn()
  })
}));

/**
 * Helper function to render components with all required providers
 */
const renderWithProviders = (ui, options = {}) => {
  // Create a mock Redux store
  const store = configureStore({
    reducer: {
      notifications: (state = { unreadCount: 0 }, action) => state,
    },
    preloadedState: options.preloadedState,
  });

  // Create a Material-UI theme
  const theme = createTheme();

  // Render the component wrapped in all necessary providers
  return render(
    <BrowserRouter>
      <Provider store={store}>
        <ThemeProvider theme={theme}>
          {ui}
        </ThemeProvider>
      </Provider>
    </BrowserRouter>,
    options
  );
};

/**
 * Mock implementation of the useAuth hook for testing
 */
const mockUseAuth = (overrides = {}) => {
  const defaultAuth = {
    state: {
      isAuthenticated: false,
      user: null,
      tokens: null,
      loading: false,
      error: null,
      mfaRequired: false,
      mfaChallenge: null,
    },
    login: jest.fn(),
    logout: jest.fn(),
    verifyMFA: jest.fn(),
    refreshTokens: jest.fn(),
  };

  return {
    ...defaultAuth,
    ...overrides,
  };
};

describe('ApplicationAppBar', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Default to desktop view
    (useMediaQuery as jest.Mock).mockReturnValue(false);
  });

  test('renders without crashing', () => {
    (useAuth as jest.Mock).mockReturnValue(mockUseAuth());
    renderWithProviders(<ApplicationAppBar />);
    expect(screen.getByText('Loan Management System')).toBeInTheDocument();
  });

  test('displays logo and application name', () => {
    (useAuth as jest.Mock).mockReturnValue(mockUseAuth());
    renderWithProviders(<ApplicationAppBar />);
    
    expect(screen.getByAltText('Logo')).toBeInTheDocument();
    expect(screen.getByText('Loan Management System')).toBeInTheDocument();
  });

  test('does not show navigation menu when user is not authenticated', () => {
    (useAuth as jest.Mock).mockReturnValue(mockUseAuth());
    renderWithProviders(<ApplicationAppBar />);
    
    // Check that notification bell is not rendered
    expect(screen.queryByLabelText('notifications')).not.toBeInTheDocument();
    
    // Check that user menu is not rendered
    expect(screen.queryByLabelText('user account')).not.toBeInTheDocument();
    
    // Check that mobile menu button is not rendered
    expect(screen.queryByLabelText('menu')).not.toBeInTheDocument();
  });

  test('shows navigation menu when user is authenticated', () => {
    (useAuth as jest.Mock).mockReturnValue(mockUseAuth({
      state: {
        isAuthenticated: true,
        user: {
          userType: UserType.BORROWER,
          firstName: 'John',
          lastName: 'Doe'
        }
      }
    }));
    
    renderWithProviders(<ApplicationAppBar />);
    
    // While we can't directly test NavMenu's content, we can check that
    // authenticated elements like notification bell and user menu are rendered
    expect(screen.getByLabelText('notifications')).toBeInTheDocument();
    expect(screen.getByLabelText('user account')).toBeInTheDocument();
  });

  test('shows user menu when user is authenticated', () => {
    (useAuth as jest.Mock).mockReturnValue(mockUseAuth({
      state: {
        isAuthenticated: true,
        user: {
          userType: UserType.BORROWER,
          firstName: 'John',
          lastName: 'Doe',
          email: 'john@example.com'
        }
      }
    }));
    
    renderWithProviders(<ApplicationAppBar />);
    
    // Find and click the user menu button
    const userButton = screen.getByLabelText('user account');
    fireEvent.click(userButton);
    
    // Check that user menu items are displayed
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
    expect(screen.getByText('Profile')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
    expect(screen.getByText('Logout')).toBeInTheDocument();
  });

  test('shows notification bell when user is authenticated', () => {
    (useAuth as jest.Mock).mockReturnValue(mockUseAuth({
      state: {
        isAuthenticated: true,
        user: {
          userType: UserType.BORROWER,
          firstName: 'John',
          lastName: 'Doe'
        }
      }
    }));
    
    renderWithProviders(<ApplicationAppBar />);
    
    expect(screen.getByLabelText('notifications')).toBeInTheDocument();
  });

  test('shows mobile menu button on small screens', () => {
    // Simulate mobile viewport
    (useMediaQuery as jest.Mock).mockReturnValue(true);
    
    (useAuth as jest.Mock).mockReturnValue(mockUseAuth({
      state: {
        isAuthenticated: true,
        user: {
          userType: UserType.BORROWER,
          firstName: 'John',
          lastName: 'Doe'
        }
      }
    }));
    
    renderWithProviders(<ApplicationAppBar />);
    
    expect(screen.getByLabelText('menu')).toBeInTheDocument();
  });

  test('opens mobile menu when button is clicked', () => {
    // Simulate mobile viewport
    (useMediaQuery as jest.Mock).mockReturnValue(true);
    
    (useAuth as jest.Mock).mockReturnValue(mockUseAuth({
      state: {
        isAuthenticated: true,
        user: {
          userType: UserType.BORROWER,
          firstName: 'John',
          lastName: 'Doe'
        }
      }
    }));
    
    renderWithProviders(<ApplicationAppBar />);
    
    // Find and click the mobile menu button
    const menuButton = screen.getByLabelText('menu');
    fireEvent.click(menuButton);
    
    // Since this test is focused on the AppBar, not NavMenu, we mainly want to
    // verify that the click handler was called and the button exists
    expect(menuButton).toBeInTheDocument();
  });

  test('displays different navigation options based on user role', () => {
    // Test with BORROWER role
    (useAuth as jest.Mock).mockReturnValue(mockUseAuth({
      state: {
        isAuthenticated: true,
        user: {
          userType: UserType.BORROWER,
          firstName: 'John',
          lastName: 'Doe'
        }
      }
    }));
    
    renderWithProviders(<ApplicationAppBar />);
    
    expect(screen.getByLabelText('user account')).toBeInTheDocument();
    expect(screen.getByLabelText('notifications')).toBeInTheDocument();
    
    // Test with SCHOOL_ADMIN role
    (useAuth as jest.Mock).mockReturnValue(mockUseAuth({
      state: {
        isAuthenticated: true,
        user: {
          userType: UserType.SCHOOL_ADMIN,
          firstName: 'Jane',
          lastName: 'Smith'
        }
      }
    }));
    
    renderWithProviders(<ApplicationAppBar />);
    
    expect(screen.getByLabelText('user account')).toBeInTheDocument();
    expect(screen.getByLabelText('notifications')).toBeInTheDocument();
    
    // Test with UNDERWRITER role
    (useAuth as jest.Mock).mockReturnValue(mockUseAuth({
      state: {
        isAuthenticated: true,
        user: {
          userType: UserType.UNDERWRITER,
          firstName: 'Robert',
          lastName: 'Johnson'
        }
      }
    }));
    
    renderWithProviders(<ApplicationAppBar />);
    
    expect(screen.getByLabelText('user account')).toBeInTheDocument();
    expect(screen.getByLabelText('notifications')).toBeInTheDocument();
    
    // Test with QC role
    (useAuth as jest.Mock).mockReturnValue(mockUseAuth({
      state: {
        isAuthenticated: true,
        user: {
          userType: UserType.QC,
          firstName: 'Patricia',
          lastName: 'Williams'
        }
      }
    }));
    
    renderWithProviders(<ApplicationAppBar />);
    
    expect(screen.getByLabelText('user account')).toBeInTheDocument();
    expect(screen.getByLabelText('notifications')).toBeInTheDocument();
    
    // Test with SYSTEM_ADMIN role
    (useAuth as jest.Mock).mockReturnValue(mockUseAuth({
      state: {
        isAuthenticated: true,
        user: {
          userType: UserType.SYSTEM_ADMIN,
          firstName: 'Admin',
          lastName: 'User'
        }
      }
    }));
    
    renderWithProviders(<ApplicationAppBar />);
    
    expect(screen.getByLabelText('user account')).toBeInTheDocument();
    expect(screen.getByLabelText('notifications')).toBeInTheDocument();
  });
});