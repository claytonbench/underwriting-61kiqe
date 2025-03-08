import { createSlice, PayloadAction, createAction, ActionReducerMapBuilder, SerializedError } from '@reduxjs/toolkit';
import { INotificationState, INotificationDisplay } from '../../types/notification.types';
import { UUID } from '../../types/common.types';

/**
 * Initial state for the notification slice
 */
const initialState: INotificationState = {
  notifications: [],
  unreadCount: 0,
  loading: false,
  error: null,
  drawerOpen: false,
};

/**
 * Notification slice for managing notification state in the Redux store
 * Handles user notifications for the loan management system
 */
export const notificationSlice = createSlice({
  name: 'notifications',
  initialState,
  reducers: {
    /**
     * Sets the notifications array in state
     */
    setNotifications: (state, action: PayloadAction<INotificationDisplay[]>) => {
      state.notifications = action.payload;
    },
    
    /**
     * Sets the unread notification count
     */
    setUnreadCount: (state, action: PayloadAction<number>) => {
      state.unreadCount = action.payload;
    },
    
    /**
     * Sets the loading state
     */
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    
    /**
     * Sets the error message
     */
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    
    /**
     * Clears the error message
     */
    clearError: (state) => {
      state.error = null;
    },
    
    /**
     * Toggles the notification drawer open/closed
     */
    toggleDrawer: (state) => {
      state.drawerOpen = !state.drawerOpen;
    },
    
    /**
     * Sets the notification drawer open state
     */
    setDrawerOpen: (state, action: PayloadAction<boolean>) => {
      state.drawerOpen = action.payload;
    },
    
    /**
     * Marks specific notifications as read
     */
    markAsRead: (state, action: PayloadAction<UUID[]>) => {
      state.notifications = state.notifications.map(notification => {
        if (action.payload.includes(notification.id) && !notification.read) {
          return { ...notification, read: true };
        }
        return notification;
      });
      
      // Recalculate unread count
      state.unreadCount = state.notifications.filter(notification => !notification.read).length;
    },
    
    /**
     * Marks all notifications as read
     */
    markAllAsRead: (state) => {
      state.notifications = state.notifications.map(notification => ({
        ...notification,
        read: true
      }));
      state.unreadCount = 0;
    },
    
    /**
     * Removes a notification from the state
     */
    removeNotification: (state, action: PayloadAction<UUID>) => {
      const notificationToRemove = state.notifications.find(n => n.id === action.payload);
      const wasUnread = notificationToRemove && !notificationToRemove.read;
      
      state.notifications = state.notifications.filter(notification => notification.id !== action.payload);
      
      // Recalculate unread count if we removed an unread notification
      if (wasUnread) {
        state.unreadCount = Math.max(0, state.unreadCount - 1);
      }
    }
  },
  
  extraReducers: (builder: ActionReducerMapBuilder<INotificationState>) => {
    /**
     * In a real implementation, this section would use imported thunk action creators.
     * For illustration purposes, we're using string literals, but in production code
     * we would import and use the actual thunk action creators.
     */
    builder
      // Fetch notifications
      .addCase('fetchNotifications/pending', (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase('fetchNotifications/fulfilled', (state, action) => {
        state.loading = false;
        state.notifications = action.payload.notifications;
        state.unreadCount = action.payload.unreadCount;
      })
      .addCase('fetchNotifications/rejected', (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch notifications';
      })
      
      // Mark notifications as read
      .addCase('markNotificationsAsReadThunk/pending', (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase('markNotificationsAsReadThunk/fulfilled', (state) => {
        state.loading = false;
      })
      .addCase('markNotificationsAsReadThunk/rejected', (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to mark notifications as read';
      })
      
      // Mark all notifications as read
      .addCase('markAllNotificationsAsReadThunk/pending', (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase('markAllNotificationsAsReadThunk/fulfilled', (state) => {
        state.loading = false;
      })
      .addCase('markAllNotificationsAsReadThunk/rejected', (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to mark all notifications as read';
      })
      
      // Delete notification
      .addCase('deleteNotificationThunk/pending', (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase('deleteNotificationThunk/fulfilled', (state) => {
        state.loading = false;
      })
      .addCase('deleteNotificationThunk/rejected', (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to delete notification';
      })
      
      // Fetch unread notification count
      .addCase('fetchUnreadNotificationCount/pending', (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase('fetchUnreadNotificationCount/fulfilled', (state, action) => {
        state.loading = false;
        state.unreadCount = action.payload;
      })
      .addCase('fetchUnreadNotificationCount/rejected', (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch unread notification count';
      });
  }
});

// Export actions for use in components and thunks
export const {
  setNotifications,
  setUnreadCount,
  setLoading,
  setError,
  clearError,
  toggleDrawer,
  setDrawerOpen,
  markAsRead,
  markAllAsRead,
  removeNotification
} = notificationSlice.actions;

// Export reducer as default
export default notificationSlice.reducer;