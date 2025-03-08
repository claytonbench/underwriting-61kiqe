import React from 'react';
import { Box, Typography, Button, IconButton, Tooltip } from '@mui/material';
import { Description, Assignment, AttachMoney, Info, Delete, DoneAll } from '@mui/icons-material';
import useStyles from './styles';
import { INotificationDisplay, NotificationCategory, NotificationPriority } from '../../types/notification.types';
import { formatDateTimeForDisplay } from '../../utils/date';

/**
 * Returns the appropriate icon component based on notification category
 */
const getCategoryIcon = (category: NotificationCategory): React.ReactElement => {
  switch (category) {
    case NotificationCategory.DOCUMENT:
      return <Description />;
    case NotificationCategory.APPLICATION:
      return <Assignment />;
    case NotificationCategory.FUNDING:
      return <AttachMoney />;
    case NotificationCategory.SYSTEM:
    default:
      return <Info />;
  }
};

/**
 * Props interface for the NotificationItem component
 */
interface NotificationItemProps {
  notification: INotificationDisplay;
  onMarkAsRead: (id: string) => void;
  onDelete: (id: string) => void;
  onClick: (notification: INotificationDisplay) => void;
}

/**
 * Component that renders an individual notification item
 */
const NotificationItem: React.FC<NotificationItemProps> = ({
  notification,
  onMarkAsRead,
  onDelete,
  onClick
}) => {
  const classes = useStyles();
  const categoryIcon = getCategoryIcon(notification.category);
  const formattedTime = formatDateTimeForDisplay(notification.timestamp);

  // Handler to mark notification as read
  const handleMarkAsRead = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!notification.read) {
      onMarkAsRead(notification.id);
    }
  };

  // Handler to delete notification
  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete(notification.id);
  };

  // Handler for notification click
  const handleClick = () => {
    onClick(notification);
  };

  // Handler for action button click
  const handleActionClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (notification.actionUrl) {
      window.open(notification.actionUrl, '_blank');
    }
  };

  // Determine priority class based on notification priority
  const getPriorityClass = () => {
    switch (notification.priority) {
      case NotificationPriority.URGENT:
        return classes.notificationUrgent;
      case NotificationPriority.HIGH:
        return classes.notificationHigh;
      case NotificationPriority.MEDIUM:
        return classes.notificationMedium;
      case NotificationPriority.LOW:
      default:
        return classes.notificationLow;
    }
  };

  return (
    <Box 
      className={`${classes.notificationItem} ${!notification.read ? classes.notificationUnread : ''} ${getPriorityClass()}`}
      onClick={handleClick}
    >
      <Box className={classes.notificationHeader}>
        <Box className={classes.notificationIcon}>
          {categoryIcon}
        </Box>
        <Typography className={classes.notificationTitle} variant="subtitle1">
          {notification.title}
        </Typography>
      </Box>
      
      <Typography className={classes.notificationMessage} variant="body2">
        {notification.message}
      </Typography>
      
      {notification.actionUrl && notification.actionLabel && (
        <Button 
          variant="outlined" 
          size="small"
          className={classes.actionButton}
          onClick={handleActionClick}
        >
          {notification.actionLabel}
        </Button>
      )}
      
      <Box className={classes.notificationFooter}>
        <Typography className={classes.notificationTime} variant="caption">
          {formattedTime}
        </Typography>
        
        <Box className={classes.notificationActions}>
          {!notification.read && (
            <Tooltip title="Mark as read">
              <IconButton size="small" onClick={handleMarkAsRead} aria-label="Mark as read">
                <DoneAll fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
          
          <Tooltip title="Delete">
            <IconButton size="small" onClick={handleDelete} aria-label="Delete notification">
              <Delete fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
    </Box>
  );
};

export default NotificationItem;