/**
 * Notification context provider for the loan management system.
 * Provides a centralized way to access notification state and methods throughout the application,
 * enabling components to display notifications, mark them as read, and manage the notification drawer.
 * 
 * @version 1.0.0
 */

import React, { createContext, useContext } from 'react'; // ^18.2.0
import { useDispatch, useSelector } from 'react-redux'; // ^8.1.1

import { INotificationState, INotificationDisplay } from '../types/notification.types';
import { UUID } from '../types/common.types';

import { 
  fetchNotifications,
  markNotificationsAsReadThunk,
  markAllNotificationsAsReadThunk,
  deleteNotificationThunk
} from '../store/thunks/notificationThunks';

import { 
  actions,
  selectNotifications,
  selectUnreadCount,
  selectNotificationLoading,
  selectNotificationError,
  selectDrawerOpen
} from '../store/slices/notificationSlice';

/**
 * Interface defining the shape of the notification context
 */
interface NotificationContextType {
  state: INotificationState;
  fetchNotifications: () => Promise<void>;
  markAsRead: (ids: UUID[]) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  deleteNotification: (id: UUID) => Promise<void>;
  toggleDrawer: () => void;
  closeDrawer: () => void;
}

/**
 * Default context value with empty state and no-op functions
 */
const defaultContextValue: NotificationContextType = {
  state: {
    notifications: [],
    unreadCount: 0,
    loading: false,
    error: null,
    drawerOpen: false
  },
  fetchNotifications: async () => {},
  markAsRead: async () => {},
  markAllAsRead: async () => {},
  deleteNotification: async () => {},
  toggleDrawer: () => {},
  closeDrawer: () => {}
};

/**
 * React context for notification state and methods
 */
export const NotificationContext = createContext<NotificationContextType>(defaultContextValue);

/**
 * Provider component that makes notification context available to child components
 */
export const NotificationProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const dispatch = useDispatch();
  
  // Select notification state from Redux store
  const notifications = useSelector(selectNotifications);
  const unreadCount = useSelector(selectUnreadCount);
  const loading = useSelector(selectNotificationLoading);
  const error = useSelector(selectNotificationError);
  const drawerOpen = useSelector(selectDrawerOpen);
  
  // Build state object from Redux selectors
  const state: INotificationState = {
    notifications,
    unreadCount,
    loading,
    error,
    drawerOpen
  };
  
  // Define methods that wrap Redux actions/thunks
  const handleFetchNotifications = async (): Promise<void> => {
    await dispatch(fetchNotifications(undefined) as any);
  };
  
  const handleMarkAsRead = async (ids: UUID[]): Promise<void> => {
    await dispatch(markNotificationsAsReadThunk(ids) as any);
  };
  
  const handleMarkAllAsRead = async (): Promise<void> => {
    await dispatch(markAllNotificationsAsReadThunk() as any);
  };
  
  const handleDeleteNotification = async (id: UUID): Promise<void> => {
    await dispatch(deleteNotificationThunk(id) as any);
  };
  
  const handleToggleDrawer = (): void => {
    dispatch(actions.toggleDrawer());
  };
  
  const handleCloseDrawer = (): void => {
    dispatch(actions.closeDrawer());
  };
  
  // Create the context value object
  const contextValue: NotificationContextType = {
    state,
    fetchNotifications: handleFetchNotifications,
    markAsRead: handleMarkAsRead,
    markAllAsRead: handleMarkAllAsRead,
    deleteNotification: handleDeleteNotification,
    toggleDrawer: handleToggleDrawer,
    closeDrawer: handleCloseDrawer
  };
  
  return (
    <NotificationContext.Provider value={contextValue}>
      {children}
    </NotificationContext.Provider>
  );
};

/**
 * Custom hook that provides access to notification context
 * @returns Notification context with state and methods
 */
export const useNotifications = (): NotificationContextType => {
  const context = useContext(NotificationContext);
  
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  
  return context;
};