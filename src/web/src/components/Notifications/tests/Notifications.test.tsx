import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';

import NotificationItem from '../NotificationItem';
import NotificationDrawer from '../NotificationDrawer';
import { NotificationContext } from '../../../context/NotificationContext';
import { NotificationCategory, NotificationPriority, INotificationDisplay } from '../../../types/notification.types';

// Helper function to render components with required providers
const renderWithProviders = (
  ui: React.ReactElement,
  options = {}
) => {
  // Create a mock Redux store
  const mockStore = configureStore({
    reducer: {
      notifications: (state = {}) => state
    },
    preloadedState: {}
  });

  // Create mock notification context values
  const mockNotificationContext = {
    state: {
      notifications: [],
      unreadCount: 0,
      loading: false,
      error: null,
      drawerOpen: true
    },
    fetchNotifications: jest.fn(),
    markAsRead: jest.fn(),
    markAllAsRead: jest.fn(),
    deleteNotification: jest.fn(),
    toggleDrawer: jest.fn(),
    closeDrawer: jest.fn()
  };

  return render(
    <Provider store={mockStore}>
      <NotificationContext.Provider value={mockNotificationContext}>
        {ui}
      </NotificationContext.Provider>
    </Provider>,
    options
  );
};

// Helper function to create mock notification objects
const createMockNotification = (overrides?: Partial<INotificationDisplay>): INotificationDisplay => {
  return {
    id: 'test-notification-id',
    title: 'Test Notification',
    message: 'This is a test notification message',
    timestamp: '2023-05-01T12:00:00Z',
    read: false,
    category: NotificationCategory.SYSTEM,
    priority: NotificationPriority.MEDIUM,
    actionUrl: null,
    actionLabel: null,
    ...overrides
  };
};

describe('NotificationItem', () => {
  test('renders notification item correctly', () => {
    const mockNotification = createMockNotification();
    const onMarkAsRead = jest.fn();
    const onDelete = jest.fn();
    const onClick = jest.fn();

    render(
      <NotificationItem
        notification={mockNotification}
        onMarkAsRead={onMarkAsRead}
        onDelete={onDelete}
        onClick={onClick}
      />
    );

    expect(screen.getByText('Test Notification')).toBeInTheDocument();
    expect(screen.getByText('This is a test notification message')).toBeInTheDocument();
    expect(screen.getByText('5/1/2023 12:00 PM')).toBeInTheDocument();
  });

  test('applies correct styling based on read status', () => {
    const unreadNotification = createMockNotification({ read: false });
    const readNotification = createMockNotification({ read: true });
    
    const { rerender } = render(
      <NotificationItem
        notification={unreadNotification}
        onMarkAsRead={jest.fn()}
        onDelete={jest.fn()}
        onClick={jest.fn()}
      />
    );

    // Using data-testid would be better, but testing class names based on provided code
    const notificationElement = screen.getByText('Test Notification').closest('div');
    expect(notificationElement?.className).toContain('notificationUnread');

    rerender(
      <NotificationItem
        notification={readNotification}
        onMarkAsRead={jest.fn()}
        onDelete={jest.fn()}
        onClick={jest.fn()}
      />
    );

    expect(notificationElement?.className).not.toContain('notificationUnread');
  });

  test('applies correct styling based on priority', () => {
    const priorities = [
      { priority: NotificationPriority.URGENT, className: 'notificationUrgent' },
      { priority: NotificationPriority.HIGH, className: 'notificationHigh' },
      { priority: NotificationPriority.MEDIUM, className: 'notificationMedium' },
      { priority: NotificationPriority.LOW, className: 'notificationLow' }
    ];

    priorities.forEach(({ priority, className }) => {
      const notification = createMockNotification({ priority });
      const { unmount } = render(
        <NotificationItem
          notification={notification}
          onMarkAsRead={jest.fn()}
          onDelete={jest.fn()}
          onClick={jest.fn()}
        />
      );

      const notificationElement = screen.getByText('Test Notification').closest('div');
      expect(notificationElement?.className).toContain(className);
      
      unmount();
    });
  });

  test('calls onMarkAsRead when mark as read button is clicked', () => {
    const mockNotification = createMockNotification();
    const onMarkAsRead = jest.fn();
    
    render(
      <NotificationItem
        notification={mockNotification}
        onMarkAsRead={onMarkAsRead}
        onDelete={jest.fn()}
        onClick={jest.fn()}
      />
    );

    const markAsReadButton = screen.getByLabelText('Mark as read');
    fireEvent.click(markAsReadButton);
    
    expect(onMarkAsRead).toHaveBeenCalledWith(mockNotification.id);
  });

  test('calls onDelete when delete button is clicked', () => {
    const mockNotification = createMockNotification();
    const onDelete = jest.fn();
    
    render(
      <NotificationItem
        notification={mockNotification}
        onMarkAsRead={jest.fn()}
        onDelete={onDelete}
        onClick={jest.fn()}
      />
    );

    const deleteButton = screen.getByLabelText('Delete notification');
    fireEvent.click(deleteButton);
    
    expect(onDelete).toHaveBeenCalledWith(mockNotification.id);
  });

  test('calls onClick when notification is clicked', () => {
    const mockNotification = createMockNotification();
    const onClick = jest.fn();
    
    render(
      <NotificationItem
        notification={mockNotification}
        onMarkAsRead={jest.fn()}
        onDelete={jest.fn()}
        onClick={onClick}
      />
    );

    const notificationElement = screen.getByText('Test Notification').closest('div');
    fireEvent.click(notificationElement!);
    
    expect(onClick).toHaveBeenCalledWith(mockNotification);
  });

  test('renders action button when actionUrl and actionLabel are provided', () => {
    const mockNotification = createMockNotification({
      actionUrl: 'https://example.com',
      actionLabel: 'View Details'
    });
    
    render(
      <NotificationItem
        notification={mockNotification}
        onMarkAsRead={jest.fn()}
        onDelete={jest.fn()}
        onClick={jest.fn()}
      />
    );

    expect(screen.getByText('View Details')).toBeInTheDocument();
  });

  test('renders the correct icon based on category', () => {
    const categories = [
      NotificationCategory.DOCUMENT,
      NotificationCategory.APPLICATION,
      NotificationCategory.FUNDING,
      NotificationCategory.SYSTEM
    ];

    categories.forEach(category => {
      const notification = createMockNotification({ category });
      const { unmount } = render(
        <NotificationItem
          notification={notification}
          onMarkAsRead={jest.fn()}
          onDelete={jest.fn()}
          onClick={jest.fn()}
        />
      );
      
      // We can't easily test for specific icons, but we can verify the component renders
      const notificationIcon = screen.getByText('Test Notification')
        .parentElement?.querySelector('svg');
        
      expect(notificationIcon).toBeInTheDocument();
      
      unmount();
    });
  });
});

describe('NotificationDrawer', () => {
  test('renders notification drawer correctly', () => {
    const mockNotifications = [
      createMockNotification({ id: '1', title: 'Notification 1' }),
      createMockNotification({ id: '2', title: 'Notification 2' })
    ];
    
    const mockContext = {
      state: {
        notifications: mockNotifications,
        unreadCount: 1,
        loading: false,
        error: null,
        drawerOpen: true
      },
      fetchNotifications: jest.fn(),
      markAsRead: jest.fn(),
      markAllAsRead: jest.fn(),
      deleteNotification: jest.fn(),
      toggleDrawer: jest.fn(),
      closeDrawer: jest.fn()
    };

    render(
      <Provider store={configureStore({ reducer: {} })}>
        <NotificationContext.Provider value={mockContext}>
          <NotificationDrawer />
        </NotificationContext.Provider>
      </Provider>
    );

    expect(screen.getByText('Notifications')).toBeInTheDocument();
    expect(screen.getByText('All')).toBeInTheDocument();
    expect(screen.getByText('Application')).toBeInTheDocument();
    expect(screen.getByText('Document')).toBeInTheDocument();
    expect(screen.getByText('Funding')).toBeInTheDocument();
    expect(screen.getByText('System')).toBeInTheDocument();
    expect(screen.getByText('Notification 1')).toBeInTheDocument();
    expect(screen.getByText('Notification 2')).toBeInTheDocument();
  });

  test('displays loading state correctly', () => {
    const mockContext = {
      state: {
        notifications: [],
        unreadCount: 0,
        loading: true,
        error: null,
        drawerOpen: true
      },
      fetchNotifications: jest.fn(),
      markAsRead: jest.fn(),
      markAllAsRead: jest.fn(),
      deleteNotification: jest.fn(),
      toggleDrawer: jest.fn(),
      closeDrawer: jest.fn()
    };

    render(
      <Provider store={configureStore({ reducer: {} })}>
        <NotificationContext.Provider value={mockContext}>
          <NotificationDrawer />
        </NotificationContext.Provider>
      </Provider>
    );

    // Check for CircularProgress component - we'll look for its role
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('displays error state correctly', () => {
    const mockContext = {
      state: {
        notifications: [],
        unreadCount: 0,
        loading: false,
        error: 'Failed to load notifications',
        drawerOpen: true
      },
      fetchNotifications: jest.fn(),
      markAsRead: jest.fn(),
      markAllAsRead: jest.fn(),
      deleteNotification: jest.fn(),
      toggleDrawer: jest.fn(),
      closeDrawer: jest.fn()
    };

    render(
      <Provider store={configureStore({ reducer: {} })}>
        <NotificationContext.Provider value={mockContext}>
          <NotificationDrawer />
        </NotificationContext.Provider>
      </Provider>
    );

    expect(screen.getByText('Failed to load notifications')).toBeInTheDocument();
    expect(screen.getByText('Try Again')).toBeInTheDocument();
  });

  test('displays empty state correctly', () => {
    const mockContext = {
      state: {
        notifications: [],
        unreadCount: 0,
        loading: false,
        error: null,
        drawerOpen: true
      },
      fetchNotifications: jest.fn(),
      markAsRead: jest.fn(),
      markAllAsRead: jest.fn(),
      deleteNotification: jest.fn(),
      toggleDrawer: jest.fn(),
      closeDrawer: jest.fn()
    };

    render(
      <Provider store={configureStore({ reducer: {} })}>
        <NotificationContext.Provider value={mockContext}>
          <NotificationDrawer />
        </NotificationContext.Provider>
      </Provider>
    );

    expect(screen.getByText("You don't have any notifications at the moment.")).toBeInTheDocument();
  });

  test('calls fetchNotifications on mount', () => {
    const fetchNotifications = jest.fn();
    const mockContext = {
      state: {
        notifications: [],
        unreadCount: 0,
        loading: false,
        error: null,
        drawerOpen: true
      },
      fetchNotifications,
      markAsRead: jest.fn(),
      markAllAsRead: jest.fn(),
      deleteNotification: jest.fn(),
      toggleDrawer: jest.fn(),
      closeDrawer: jest.fn()
    };

    render(
      <Provider store={configureStore({ reducer: {} })}>
        <NotificationContext.Provider value={mockContext}>
          <NotificationDrawer />
        </NotificationContext.Provider>
      </Provider>
    );

    expect(fetchNotifications).toHaveBeenCalledTimes(1);
  });

  test('calls fetchNotifications when refresh button is clicked', () => {
    const fetchNotifications = jest.fn();
    const mockContext = {
      state: {
        notifications: [],
        unreadCount: 0,
        loading: false,
        error: null,
        drawerOpen: true
      },
      fetchNotifications,
      markAsRead: jest.fn(),
      markAllAsRead: jest.fn(),
      deleteNotification: jest.fn(),
      toggleDrawer: jest.fn(),
      closeDrawer: jest.fn()
    };

    render(
      <Provider store={configureStore({ reducer: {} })}>
        <NotificationContext.Provider value={mockContext}>
          <NotificationDrawer />
        </NotificationContext.Provider>
      </Provider>
    );

    // Reset the mock to clear the first call on mount
    fetchNotifications.mockClear();
    
    const refreshButton = screen.getByLabelText('Refresh notifications');
    fireEvent.click(refreshButton);
    
    expect(fetchNotifications).toHaveBeenCalledTimes(1);
  });

  test('calls markAllAsRead when mark all as read button is clicked', () => {
    const markAllAsRead = jest.fn();
    const mockContext = {
      state: {
        notifications: [],
        unreadCount: 0,
        loading: false,
        error: null,
        drawerOpen: true
      },
      fetchNotifications: jest.fn(),
      markAsRead: jest.fn(),
      markAllAsRead,
      deleteNotification: jest.fn(),
      toggleDrawer: jest.fn(),
      closeDrawer: jest.fn()
    };

    render(
      <Provider store={configureStore({ reducer: {} })}>
        <NotificationContext.Provider value={mockContext}>
          <NotificationDrawer />
        </NotificationContext.Provider>
      </Provider>
    );

    const markAllReadButton = screen.getByLabelText('Mark all as read');
    fireEvent.click(markAllReadButton);
    
    expect(markAllAsRead).toHaveBeenCalledTimes(1);
  });

  test('filters notifications when category tab is clicked', async () => {
    const fetchNotifications = jest.fn();
    const mockContext = {
      state: {
        notifications: [
          createMockNotification({ id: '1', category: NotificationCategory.APPLICATION }),
          createMockNotification({ id: '2', category: NotificationCategory.DOCUMENT })
        ],
        unreadCount: 2,
        loading: false,
        error: null,
        drawerOpen: true
      },
      fetchNotifications,
      markAsRead: jest.fn(),
      markAllAsRead: jest.fn(),
      deleteNotification: jest.fn(),
      toggleDrawer: jest.fn(),
      closeDrawer: jest.fn()
    };

    render(
      <Provider store={configureStore({ reducer: {} })}>
        <NotificationContext.Provider value={mockContext}>
          <NotificationDrawer />
        </NotificationContext.Provider>
      </Provider>
    );

    // Reset mock to clear the call made on mount
    fetchNotifications.mockClear();
    
    const applicationTab = screen.getByText('Application');
    fireEvent.click(applicationTab);
    
    expect(fetchNotifications).toHaveBeenCalledTimes(1);
  });

  test('calls markAsRead when a notification is marked as read', () => {
    const markAsRead = jest.fn();
    const mockNotifications = [
      createMockNotification({ id: '1', title: 'Test Notification' })
    ];
    
    const mockContext = {
      state: {
        notifications: mockNotifications,
        unreadCount: 1,
        loading: false,
        error: null,
        drawerOpen: true
      },
      fetchNotifications: jest.fn(),
      markAsRead,
      markAllAsRead: jest.fn(),
      deleteNotification: jest.fn(),
      toggleDrawer: jest.fn(),
      closeDrawer: jest.fn()
    };

    render(
      <Provider store={configureStore({ reducer: {} })}>
        <NotificationContext.Provider value={mockContext}>
          <NotificationDrawer />
        </NotificationContext.Provider>
      </Provider>
    );

    const markAsReadButton = screen.getByLabelText('Mark as read');
    fireEvent.click(markAsReadButton);
    
    expect(markAsRead).toHaveBeenCalledWith(['1']);
  });

  test('calls deleteNotification when a notification is deleted', () => {
    const deleteNotification = jest.fn();
    const mockNotifications = [
      createMockNotification({ id: '1', title: 'Test Notification' })
    ];
    
    const mockContext = {
      state: {
        notifications: mockNotifications,
        unreadCount: 1,
        loading: false,
        error: null,
        drawerOpen: true
      },
      fetchNotifications: jest.fn(),
      markAsRead: jest.fn(),
      markAllAsRead: jest.fn(),
      deleteNotification,
      toggleDrawer: jest.fn(),
      closeDrawer: jest.fn()
    };

    render(
      <Provider store={configureStore({ reducer: {} })}>
        <NotificationContext.Provider value={mockContext}>
          <NotificationDrawer />
        </NotificationContext.Provider>
      </Provider>
    );

    const deleteButton = screen.getByLabelText('Delete notification');
    fireEvent.click(deleteButton);
    
    expect(deleteNotification).toHaveBeenCalledWith('1');
  });

  test('handles notification click correctly', () => {
    const markAsRead = jest.fn();
    const closeDrawer = jest.fn();
    const mockNotifications = [
      createMockNotification({ 
        id: '1', 
        title: 'Test Notification',
        read: false,
        actionUrl: 'https://example.com'
      })
    ];
    
    const mockContext = {
      state: {
        notifications: mockNotifications,
        unreadCount: 1,
        loading: false,
        error: null,
        drawerOpen: true
      },
      fetchNotifications: jest.fn(),
      markAsRead,
      markAllAsRead: jest.fn(),
      deleteNotification: jest.fn(),
      toggleDrawer: jest.fn(),
      closeDrawer
    };

    // Mock window.open
    const originalOpen = window.open;
    window.open = jest.fn();

    render(
      <Provider store={configureStore({ reducer: {} })}>
        <NotificationContext.Provider value={mockContext}>
          <NotificationDrawer />
        </NotificationContext.Provider>
      </Provider>
    );

    const notificationItem = screen.getByText('Test Notification').closest('div');
    fireEvent.click(notificationItem!);
    
    expect(markAsRead).toHaveBeenCalledWith(['1']);
    expect(closeDrawer).toHaveBeenCalled();
    
    // Restore original window.open
    window.open = originalOpen;
  });
});