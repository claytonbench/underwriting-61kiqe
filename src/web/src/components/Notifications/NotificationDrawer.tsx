import React, { useState, useEffect } from 'react';
import { 
  Drawer, 
  Box, 
  Typography, 
  IconButton, 
  Button, 
  Divider, 
  Tabs, 
  Tab, 
  CircularProgress 
} from '@mui/material';
import { Close, Refresh, DoneAll } from '@mui/icons-material';

import useStyles from './styles';
import NotificationItem from './NotificationItem';
import { useNotifications } from '../../hooks/useNotifications';
import { NotificationCategory, INotificationDisplay } from '../../types/notification.types';

/**
 * Interface for the notification filter state
 */
interface NotificationFilterState {
  category: NotificationCategory | 'ALL' | null;
}

/**
 * Component that renders a sliding drawer with user notifications
 */
const NotificationDrawer: React.FC = () => {
  // Get notification context
  const { 
    state: { notifications, loading, error, drawerOpen },
    fetchNotifications,
    markAsRead,
    markAllAsRead: markAllAsReadInContext,
    deleteNotification,
    closeDrawer
  } = useNotifications();

  // Get styles
  const classes = useStyles();
  
  // Local state for category filtering
  const [selectedCategory, setSelectedCategory] = useState<NotificationFilterState['category']>('ALL');

  // Fetch notifications when component mounts
  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  /**
   * Handles change of notification category filter
   */
  const handleCategoryChange = (event: React.SyntheticEvent, newCategory: NotificationCategory | 'ALL') => {
    setSelectedCategory(newCategory);
    fetchNotifications();
  };

  /**
   * Refreshes the notifications list
   */
  const handleRefresh = () => {
    fetchNotifications();
  };

  /**
   * Marks all notifications as read
   */
  const handleMarkAllAsRead = () => {
    markAllAsReadInContext();
  };

  /**
   * Marks a single notification as read
   */
  const handleMarkAsRead = (id: string) => {
    markAsRead([id]);
  };

  /**
   * Deletes a notification
   */
  const handleDelete = (id: string) => {
    deleteNotification(id);
  };

  /**
   * Handles click on a notification item
   */
  const handleNotificationClick = (notification: INotificationDisplay) => {
    // Mark as read if not already read
    if (!notification.read) {
      markAsRead([notification.id]);
    }

    // If the notification has an action URL, trigger the appropriate action
    if (notification.actionUrl) {
      window.open(notification.actionUrl, '_blank');
    }

    // Close the drawer
    closeDrawer();
  };

  /**
   * Renders an empty state message when there are no notifications
   */
  const renderEmptyState = () => {
    return (
      <Box className={classes.emptyState}>
        <DoneAll className={classes.emptyStateIcon} />
        <Typography variant="body1">
          You don't have any notifications at the moment.
        </Typography>
      </Box>
    );
  };

  return (
    <Drawer
      anchor="right"
      open={drawerOpen}
      onClose={closeDrawer}
      classes={{ paper: classes.drawer }}
    >
      {/* Drawer Header */}
      <Box className={classes.drawerHeader}>
        <Typography variant="h6" className={classes.drawerTitle}>
          Notifications
        </Typography>
        <IconButton size="small" onClick={handleRefresh} aria-label="Refresh notifications">
          <Refresh fontSize="small" />
        </IconButton>
        <IconButton size="small" onClick={handleMarkAllAsRead} aria-label="Mark all as read">
          <DoneAll fontSize="small" />
        </IconButton>
        <IconButton size="small" onClick={closeDrawer} aria-label="Close notification drawer">
          <Close fontSize="small" />
        </IconButton>
      </Box>

      {/* Category Filter Tabs */}
      <Tabs
        value={selectedCategory}
        onChange={handleCategoryChange}
        indicatorColor="primary"
        textColor="primary"
        variant="fullWidth"
        className={classes.tabs}
      >
        <Tab label="All" value="ALL" />
        <Tab label="Application" value={NotificationCategory.APPLICATION} />
        <Tab label="Document" value={NotificationCategory.DOCUMENT} />
        <Tab label="Funding" value={NotificationCategory.FUNDING} />
        <Tab label="System" value={NotificationCategory.SYSTEM} />
      </Tabs>

      {/* Notification Content */}
      <Box className={classes.drawerContent}>
        {loading ? (
          <Box className={classes.loadingContainer}>
            <CircularProgress size={40} />
          </Box>
        ) : error ? (
          <Box className={classes.errorContainer}>
            <Typography color="error">
              {error}
            </Typography>
            <Button 
              variant="outlined" 
              color="primary" 
              onClick={handleRefresh}
              size="small"
              sx={{ mt: 2 }}
            >
              Try Again
            </Button>
          </Box>
        ) : notifications.length === 0 ? (
          renderEmptyState()
        ) : (
          notifications.map(notification => (
            <NotificationItem
              key={notification.id}
              notification={notification}
              onMarkAsRead={handleMarkAsRead}
              onDelete={handleDelete}
              onClick={handleNotificationClick}
            />
          ))
        )}
      </Box>

      {/* Drawer Footer */}
      <Box className={classes.drawerFooter}>
        <Button 
          variant="outlined" 
          size="small" 
          onClick={closeDrawer}
        >
          Close
        </Button>
      </Box>
    </Drawer>
  );
};

export default NotificationDrawer;