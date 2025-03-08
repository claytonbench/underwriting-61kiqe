import { createAsyncThunk } from '@reduxjs/toolkit'; // v1.9.5
import { INotificationFilter } from '../../types/notification.types';
import { UUID } from '../../types/common.types';
import { notificationSlice } from '../slices/notificationSlice';
import { 
  getNotifications, 
  markAsRead, 
  markAllAsRead, 
  deleteNotification 
} from '../../api/notifications';
import { AppDispatch } from '../store';
import { RootState } from '../rootReducer';

/**
 * Thunk action creator that fetches notifications for the current user
 */
export const fetchNotifications = createAsyncThunk(
  'notifications/fetchNotifications',
  async (filters: INotificationFilter | undefined, { rejectWithValue }) => {
    try {
      const response = await getNotifications(filters);
      
      if (!response.success) {
        return rejectWithValue(response.message || 'Failed to fetch notifications');
      }
      
      return response.data;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to fetch notifications');
    }
  }
);

/**
 * Thunk action creator that marks specified notifications as read
 */
export const markNotificationsAsReadThunk = createAsyncThunk(
  'notifications/markAsRead',
  async (notificationIds: UUID[], { dispatch, rejectWithValue }) => {
    try {
      const response = await markAsRead(notificationIds);
      
      if (!response.success) {
        return rejectWithValue(response.message || 'Failed to mark notifications as read');
      }
      
      // Update local state to reflect changes
      dispatch(notificationSlice.actions.markAsRead(notificationIds));
      
      return response.data;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to mark notifications as read');
    }
  }
);

/**
 * Thunk action creator that marks all notifications as read
 */
export const markAllNotificationsAsReadThunk = createAsyncThunk(
  'notifications/markAllAsRead',
  async (_, { dispatch, rejectWithValue }) => {
    try {
      const response = await markAllAsRead();
      
      if (!response.success) {
        return rejectWithValue(response.message || 'Failed to mark all notifications as read');
      }
      
      // Update local state to reflect changes
      dispatch(notificationSlice.actions.markAllAsRead());
      
      return response.data;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to mark all notifications as read');
    }
  }
);

/**
 * Thunk action creator that deletes a specific notification
 */
export const deleteNotificationThunk = createAsyncThunk(
  'notifications/deleteNotification',
  async (notificationId: UUID, { dispatch, rejectWithValue }) => {
    try {
      const response = await deleteNotification(notificationId);
      
      if (!response.success) {
        return rejectWithValue(response.message || 'Failed to delete notification');
      }
      
      // Update local state to reflect changes
      dispatch(notificationSlice.actions.removeNotification(notificationId));
      
      return response.data;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to delete notification');
    }
  }
);

/**
 * Thunk action creator that fetches only the unread notification count
 */
export const fetchUnreadNotificationCount = createAsyncThunk(
  'notifications/fetchUnreadCount',
  async (_, { rejectWithValue }) => {
    try {
      // Using minimal parameters to just get the count
      const response = await getNotifications({
        category: null,
        priority: null,
        read: null,
        startDate: null,
        endDate: null
      });
      
      if (!response.success) {
        return rejectWithValue(response.message || 'Failed to fetch unread notification count');
      }
      
      return response.data.unreadCount;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to fetch unread notification count');
    }
  }
);

/**
 * Thunk action creator that refreshes notifications based on current filters
 */
export const refreshNotifications = () => (dispatch: AppDispatch, getState: () => RootState) => {
  const state = getState();
  
  // Get current filter settings from state if they exist
  // In a real implementation, these filters would likely be stored in a specific
  // location in the state or managed by the component using the notifications
  const filters = {
    category: state.notifications?.filters?.category || null,
    priority: state.notifications?.filters?.priority || null,
    read: state.notifications?.filters?.read || null,
    startDate: state.notifications?.filters?.startDate || null,
    endDate: state.notifications?.filters?.endDate || null
  };
  
  return dispatch(fetchNotifications(filters));
};