/**
 * Notification type definitions for the loan management system
 * Defines TypeScript interfaces, types, and enums for the notification system,
 * including data structures for notifications, templates, and user preferences.
 */

import { UUID, ISO8601Date, ApiResponse, PaginatedResponse } from './common.types';

/**
 * Categories of notifications for filtering and display
 */
export enum NotificationCategory {
  APPLICATION = 'application',
  DOCUMENT = 'document',
  FUNDING = 'funding',
  SYSTEM = 'system'
}

/**
 * Priority levels for notifications to control display styling and sorting
 */
export enum NotificationPriority {
  URGENT = 'urgent',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low'
}

/**
 * Interface for notification objects returned from the API
 */
export interface INotification {
  id: UUID;
  userId: UUID;
  title: string;
  message: string;
  category: NotificationCategory;
  priority: NotificationPriority;
  read: boolean;
  createdAt: ISO8601Date;
  readAt: ISO8601Date | null;
  entityType: string | null;
  entityId: UUID | null;
  actionUrl: string | null;
  actionLabel: string | null;
}

/**
 * Interface for notification objects displayed in the UI
 */
export interface INotificationDisplay {
  id: UUID;
  title: string;
  message: string;
  timestamp: ISO8601Date;
  read: boolean;
  category: NotificationCategory;
  priority: NotificationPriority;
  actionUrl: string | null;
  actionLabel: string | null;
}

/**
 * Interface for notification state in Redux store and context
 */
export interface INotificationState {
  notifications: INotificationDisplay[];
  unreadCount: number;
  loading: boolean;
  error: string | null;
  drawerOpen: boolean;
}

/**
 * Interface for notification templates used to generate notifications
 */
export interface INotificationTemplate {
  id: UUID;
  name: string;
  description: string;
  subject: string;
  bodyTemplate: string;
  category: NotificationCategory;
  priority: NotificationPriority;
  isActive: boolean;
  createdAt: ISO8601Date;
  updatedAt: ISO8601Date;
}

/**
 * Interface for user notification preferences
 */
export interface INotificationPreference {
  id: UUID;
  userId: UUID;
  category: NotificationCategory;
  emailEnabled: boolean;
  inAppEnabled: boolean;
  updatedAt: ISO8601Date;
}

/**
 * Interface for notification list response from API
 */
export interface INotificationResponse {
  notifications: INotificationDisplay[];
  unreadCount: number;
}

/**
 * Type alias for paginated notification response using PaginatedResponse generic
 */
export type PaginatedNotificationResponse = PaginatedResponse<INotificationDisplay>;

/**
 * Interface for marking notifications as read request
 */
export interface IMarkAsReadRequest {
  notificationIds: UUID[];
}

/**
 * Interface for notification filtering options
 */
export interface INotificationFilter {
  category: NotificationCategory | null;
  priority: NotificationPriority | null;
  read: boolean | null;
  startDate: ISO8601Date | null;
  endDate: ISO8601Date | null;
}