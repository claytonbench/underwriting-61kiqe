/**
 * Redux action creators and types for the notification system
 * Provides action types and creator functions for managing notification-related state
 *
 * @version 1.0.0
 */

import { INotificationDisplay } from '../../types/notification.types';
import { UUID } from '../../types/common.types';

// Action type constants
export const FETCH_NOTIFICATIONS_REQUEST = 'notification/FETCH_NOTIFICATIONS_REQUEST';
export const FETCH_NOTIFICATIONS_SUCCESS = 'notification/FETCH_NOTIFICATIONS_SUCCESS';
export const FETCH_NOTIFICATIONS_FAILURE = 'notification/FETCH_NOTIFICATIONS_FAILURE';

export const MARK_NOTIFICATIONS_READ_REQUEST = 'notification/MARK_NOTIFICATIONS_READ_REQUEST';
export const MARK_NOTIFICATIONS_READ_SUCCESS = 'notification/MARK_NOTIFICATIONS_READ_SUCCESS';
export const MARK_NOTIFICATIONS_READ_FAILURE = 'notification/MARK_NOTIFICATIONS_READ_FAILURE';

export const MARK_ALL_NOTIFICATIONS_READ_REQUEST = 'notification/MARK_ALL_NOTIFICATIONS_READ_REQUEST';
export const MARK_ALL_NOTIFICATIONS_READ_SUCCESS = 'notification/MARK_ALL_NOTIFICATIONS_READ_SUCCESS';
export const MARK_ALL_NOTIFICATIONS_READ_FAILURE = 'notification/MARK_ALL_NOTIFICATIONS_READ_FAILURE';

export const DELETE_NOTIFICATION_REQUEST = 'notification/DELETE_NOTIFICATION_REQUEST';
export const DELETE_NOTIFICATION_SUCCESS = 'notification/DELETE_NOTIFICATION_SUCCESS';
export const DELETE_NOTIFICATION_FAILURE = 'notification/DELETE_NOTIFICATION_FAILURE';

export const FETCH_UNREAD_COUNT_REQUEST = 'notification/FETCH_UNREAD_COUNT_REQUEST';
export const FETCH_UNREAD_COUNT_SUCCESS = 'notification/FETCH_UNREAD_COUNT_SUCCESS';
export const FETCH_UNREAD_COUNT_FAILURE = 'notification/FETCH_UNREAD_COUNT_FAILURE';

export const TOGGLE_NOTIFICATION_DRAWER = 'notification/TOGGLE_NOTIFICATION_DRAWER';
export const CLOSE_NOTIFICATION_DRAWER = 'notification/CLOSE_NOTIFICATION_DRAWER';

// Action creator functions

/**
 * Initiates a request to fetch user notifications
 */
export const fetchNotificationsRequest = () => ({
  type: FETCH_NOTIFICATIONS_REQUEST
});

/**
 * Handles successful notification fetch
 * @param payload - Object containing notifications array and unread count
 */
export const fetchNotificationsSuccess = (
  payload: { notifications: INotificationDisplay[]; unreadCount: number }
) => ({
  type: FETCH_NOTIFICATIONS_SUCCESS,
  payload
});

/**
 * Handles failed notification fetch
 * @param error - Error message
 */
export const fetchNotificationsFailure = (error: string) => ({
  type: FETCH_NOTIFICATIONS_FAILURE,
  payload: error
});

/**
 * Initiates a request to mark specific notifications as read
 */
export const markNotificationsReadRequest = () => ({
  type: MARK_NOTIFICATIONS_READ_REQUEST
});

/**
 * Handles successful marking of notifications as read
 * @param notificationIds - Array of notification IDs that were marked as read
 */
export const markNotificationsReadSuccess = (notificationIds: UUID[]) => ({
  type: MARK_NOTIFICATIONS_READ_SUCCESS,
  payload: notificationIds
});

/**
 * Handles failed attempt to mark notifications as read
 * @param error - Error message
 */
export const markNotificationsReadFailure = (error: string) => ({
  type: MARK_NOTIFICATIONS_READ_FAILURE,
  payload: error
});

/**
 * Initiates a request to mark all notifications as read
 */
export const markAllNotificationsReadRequest = () => ({
  type: MARK_ALL_NOTIFICATIONS_READ_REQUEST
});

/**
 * Handles successful marking of all notifications as read
 */
export const markAllNotificationsReadSuccess = () => ({
  type: MARK_ALL_NOTIFICATIONS_READ_SUCCESS
});

/**
 * Handles failed attempt to mark all notifications as read
 * @param error - Error message
 */
export const markAllNotificationsReadFailure = (error: string) => ({
  type: MARK_ALL_NOTIFICATIONS_READ_FAILURE,
  payload: error
});

/**
 * Initiates a request to delete a notification
 */
export const deleteNotificationRequest = () => ({
  type: DELETE_NOTIFICATION_REQUEST
});

/**
 * Handles successful notification deletion
 * @param notificationId - ID of the deleted notification
 */
export const deleteNotificationSuccess = (notificationId: UUID) => ({
  type: DELETE_NOTIFICATION_SUCCESS,
  payload: notificationId
});

/**
 * Handles failed notification deletion
 * @param error - Error message
 */
export const deleteNotificationFailure = (error: string) => ({
  type: DELETE_NOTIFICATION_FAILURE,
  payload: error
});

/**
 * Initiates a request to fetch unread notification count
 */
export const fetchUnreadCountRequest = () => ({
  type: FETCH_UNREAD_COUNT_REQUEST
});

/**
 * Handles successful unread count fetch
 * @param count - Number of unread notifications
 */
export const fetchUnreadCountSuccess = (count: number) => ({
  type: FETCH_UNREAD_COUNT_SUCCESS,
  payload: count
});

/**
 * Handles failed unread count fetch
 * @param error - Error message
 */
export const fetchUnreadCountFailure = (error: string) => ({
  type: FETCH_UNREAD_COUNT_FAILURE,
  payload: error
});

/**
 * Toggles notification drawer open/closed state
 */
export const toggleNotificationDrawer = () => ({
  type: TOGGLE_NOTIFICATION_DRAWER
});

/**
 * Closes notification drawer
 */
export const closeNotificationDrawer = () => ({
  type: CLOSE_NOTIFICATION_DRAWER
});

// Define union type for notification actions for type safety in the reducer
export type NotificationAction = 
  | ReturnType<typeof fetchNotificationsRequest>
  | ReturnType<typeof fetchNotificationsSuccess>
  | ReturnType<typeof fetchNotificationsFailure>
  | ReturnType<typeof markNotificationsReadRequest>
  | ReturnType<typeof markNotificationsReadSuccess>
  | ReturnType<typeof markNotificationsReadFailure>
  | ReturnType<typeof markAllNotificationsReadRequest>
  | ReturnType<typeof markAllNotificationsReadSuccess>
  | ReturnType<typeof markAllNotificationsReadFailure>
  | ReturnType<typeof deleteNotificationRequest>
  | ReturnType<typeof deleteNotificationSuccess>
  | ReturnType<typeof deleteNotificationFailure>
  | ReturnType<typeof fetchUnreadCountRequest>
  | ReturnType<typeof fetchUnreadCountSuccess>
  | ReturnType<typeof fetchUnreadCountFailure>
  | ReturnType<typeof toggleNotificationDrawer>
  | ReturnType<typeof closeNotificationDrawer>;