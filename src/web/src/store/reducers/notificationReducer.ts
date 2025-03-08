import { Reducer } from 'redux'; // redux v4.2.1

import { 
  INotificationState,
  INotificationDisplay 
} from '../../types/notification.types';
import { UUID } from '../../types/common.types';
import {
  FETCH_NOTIFICATIONS_REQUEST,
  FETCH_NOTIFICATIONS_SUCCESS,
  FETCH_NOTIFICATIONS_FAILURE,
  MARK_NOTIFICATIONS_READ_REQUEST,
  MARK_NOTIFICATIONS_READ_SUCCESS,
  MARK_NOTIFICATIONS_READ_FAILURE,
  MARK_ALL_NOTIFICATIONS_READ_REQUEST,
  MARK_ALL_NOTIFICATIONS_READ_SUCCESS,
  MARK_ALL_NOTIFICATIONS_READ_FAILURE,
  DELETE_NOTIFICATION_REQUEST,
  DELETE_NOTIFICATION_SUCCESS,
  DELETE_NOTIFICATION_FAILURE,
  FETCH_UNREAD_COUNT_REQUEST,
  FETCH_UNREAD_COUNT_SUCCESS,
  FETCH_UNREAD_COUNT_FAILURE,
  TOGGLE_NOTIFICATION_DRAWER,
  CLOSE_NOTIFICATION_DRAWER,
  NotificationAction
} from '../actions/notificationActions';

/**
 * Initial state for notification reducer
 */
const initialState: INotificationState = {
  notifications: [],
  unreadCount: 0,
  loading: false,
  error: null,
  drawerOpen: false
};

/**
 * Reducer function for handling notification-related actions
 * @param state - Current notification state
 * @param action - Action to process
 * @returns Updated notification state
 */
const notificationReducer: Reducer<INotificationState, NotificationAction> = (
  state = initialState,
  action
): INotificationState => {
  switch (action.type) {
    // Fetch notifications actions
    case FETCH_NOTIFICATIONS_REQUEST:
      return {
        ...state,
        loading: true,
        error: null
      };
    
    case FETCH_NOTIFICATIONS_SUCCESS:
      return {
        ...state,
        notifications: action.payload.notifications,
        unreadCount: action.payload.unreadCount,
        loading: false,
        error: null
      };
    
    case FETCH_NOTIFICATIONS_FAILURE:
      return {
        ...state,
        loading: false,
        error: action.payload
      };
    
    // Mark notifications as read actions
    case MARK_NOTIFICATIONS_READ_REQUEST:
      return {
        ...state,
        loading: true,
        error: null
      };
    
    case MARK_NOTIFICATIONS_READ_SUCCESS: {
      const notificationIds = action.payload as UUID[];
      const updatedNotifications = state.notifications.map(notification => 
        notificationIds.includes(notification.id) 
          ? { ...notification, read: true } 
          : notification
      );

      // Calculate new unread count by counting unread notifications
      const newUnreadCount = updatedNotifications.filter(notification => !notification.read).length;
      
      return {
        ...state,
        notifications: updatedNotifications,
        unreadCount: newUnreadCount,
        loading: false
      };
    }
    
    case MARK_NOTIFICATIONS_READ_FAILURE:
      return {
        ...state,
        loading: false,
        error: action.payload
      };
    
    // Mark all notifications as read actions
    case MARK_ALL_NOTIFICATIONS_READ_REQUEST:
      return {
        ...state,
        loading: true,
        error: null
      };
    
    case MARK_ALL_NOTIFICATIONS_READ_SUCCESS: {
      const updatedNotifications = state.notifications.map(notification => ({
        ...notification,
        read: true
      }));
      
      return {
        ...state,
        notifications: updatedNotifications,
        unreadCount: 0,
        loading: false
      };
    }
    
    case MARK_ALL_NOTIFICATIONS_READ_FAILURE:
      return {
        ...state,
        loading: false,
        error: action.payload
      };
    
    // Delete notification actions
    case DELETE_NOTIFICATION_REQUEST:
      return {
        ...state,
        loading: true,
        error: null
      };
    
    case DELETE_NOTIFICATION_SUCCESS: {
      const notificationId = action.payload as UUID;
      const updatedNotifications = state.notifications.filter(
        notification => notification.id !== notificationId
      );
      
      // Recalculate unread count after deletion
      const newUnreadCount = updatedNotifications.filter(notification => !notification.read).length;
      
      return {
        ...state,
        notifications: updatedNotifications,
        unreadCount: newUnreadCount,
        loading: false
      };
    }
    
    case DELETE_NOTIFICATION_FAILURE:
      return {
        ...state,
        loading: false,
        error: action.payload
      };
    
    // Fetch unread count actions
    case FETCH_UNREAD_COUNT_REQUEST:
      return {
        ...state,
        loading: true,
        error: null
      };
    
    case FETCH_UNREAD_COUNT_SUCCESS:
      return {
        ...state,
        unreadCount: action.payload,
        loading: false
      };
    
    case FETCH_UNREAD_COUNT_FAILURE:
      return {
        ...state,
        loading: false,
        error: action.payload
      };
    
    // Notification drawer control actions
    case TOGGLE_NOTIFICATION_DRAWER:
      return {
        ...state,
        drawerOpen: !state.drawerOpen
      };
    
    case CLOSE_NOTIFICATION_DRAWER:
      return {
        ...state,
        drawerOpen: false
      };
    
    default:
      return state;
  }
};

export default notificationReducer;