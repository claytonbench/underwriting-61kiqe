import React, { useEffect } from 'react';
import { useDispatch } from 'react-redux'; // v8.1.1
import { IconButton, Badge, Tooltip } from '@mui/material'; // v5.14.0
import { Notifications as NotificationsIcon } from '@mui/icons-material'; // v5.14.0

// Import custom hooks and styles
import useStyles from './styles';
import useNotifications from '../../hooks/useNotifications';
import { fetchUnreadNotificationCount } from '../../store/thunks/notificationThunks';

/**
 * Component that renders a notification bell icon in the application header with an 
 * unread count badge. When clicked, it toggles the notification drawer.
 *
 * @returns {JSX.Element} The rendered notification bell component
 */
const NotificationBell: React.FC = () => {
  // Access notification context to get state and methods
  const { state, toggleDrawer } = useNotifications();
  const { unreadCount } = state;
  
  // Get styles for the component
  const classes = useStyles();
  
  // Get dispatch function for fetching data
  const dispatch = useDispatch();
  
  // Fetch unread notification count on component mount
  useEffect(() => {
    dispatch(fetchUnreadNotificationCount() as any);
  }, [dispatch]);
  
  // Set up interval to periodically refresh unread count
  useEffect(() => {
    const intervalId = setInterval(() => {
      dispatch(fetchUnreadNotificationCount() as any);
    }, 60000); // Refresh every minute
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, [dispatch]);
  
  /**
   * Handles click on the notification bell icon
   */
  const handleClick = () => {
    toggleDrawer();
  };
  
  return (
    <Tooltip title={unreadCount > 0 ? `${unreadCount} unread notifications` : "No unread notifications"}>
      <IconButton
        color="inherit"
        aria-label="notifications"
        onClick={handleClick}
        className={classes.notificationBadge}
      >
        <Badge 
          badgeContent={unreadCount} 
          color="error"
          max={99}
          invisible={unreadCount === 0}
        >
          <NotificationsIcon />
        </Badge>
      </IconButton>
    </Tooltip>
  );
};

export default NotificationBell;