import { makeStyles } from '@mui/styles';
import { Theme } from '@mui/material';
import { NotificationPriority } from '../../types/notification.types';
import { mediaQueries } from '../../responsive/breakpoints';

/**
 * Creates and returns style classes for Notification components
 * Includes styles for NotificationDrawer and NotificationItem with priority-based styling
 */
const useStyles = makeStyles((theme: Theme) => ({
  drawer: {
    width: '360px',
    maxWidth: '100%',
    padding: '0',
    overflow: 'hidden',
    [mediaQueries.mobile]: {
      width: '100%',
    },
  },
  drawerHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '16px',
    borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
  },
  drawerTitle: {
    flexGrow: 1,
    fontWeight: 500,
  },
  drawerContent: {
    overflowY: 'auto',
    height: 'calc(100% - 120px)',
    padding: '0',
    [mediaQueries.mobile]: {
      height: 'calc(100% - 110px)',
    },
    [mediaQueries.tablet]: {
      height: 'calc(100% - 115px)',
    },
  },
  drawerFooter: {
    padding: '16px',
    borderTop: '1px solid rgba(0, 0, 0, 0.12)',
    display: 'flex',
    justifyContent: 'flex-end',
  },
  notificationItem: {
    padding: '16px',
    borderBottom: '1px solid rgba(0, 0, 0, 0.08)',
    transition: 'background-color 0.2s ease',
    cursor: 'pointer',
    '&:hover': {
      backgroundColor: 'rgba(0, 0, 0, 0.04)',
    },
    [mediaQueries.mobile]: {
      padding: '12px',
    },
  },
  notificationUnread: {
    backgroundColor: 'rgba(25, 118, 210, 0.08)',
  },
  notificationUrgent: {
    borderLeft: `4px solid #D32F2F`, // Error color for NotificationPriority.URGENT
  },
  notificationHigh: {
    borderLeft: `4px solid #FFA000`, // Warning color for NotificationPriority.HIGH
  },
  notificationMedium: {
    borderLeft: `4px solid #1976D2`, // Primary color for NotificationPriority.MEDIUM
  },
  notificationLow: {
    borderLeft: `4px solid #388E3C`, // Success color for NotificationPriority.LOW
  },
  notificationHeader: {
    display: 'flex',
    alignItems: 'flex-start',
    marginBottom: '8px',
  },
  notificationIcon: {
    marginRight: '12px',
    marginTop: '2px',
  },
  notificationTitle: {
    fontWeight: 500,
    flexGrow: 1,
    marginRight: '8px',
    [mediaQueries.mobile]: {
      fontSize: '0.9rem',
    },
  },
  notificationMessage: {
    marginBottom: '8px',
    color: 'rgba(0, 0, 0, 0.7)',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    display: '-webkit-box',
    '-webkit-line-clamp': 2,
    '-webkit-box-orient': 'vertical',
    [mediaQueries.mobile]: {
      fontSize: '0.85rem',
    },
  },
  notificationFooter: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  notificationTime: {
    color: 'rgba(0, 0, 0, 0.6)',
    fontSize: '0.75rem',
  },
  notificationActions: {
    display: 'flex',
    [mediaQueries.mobile]: {
      flexDirection: 'column',
    },
  },
  actionButton: {
    marginTop: '8px',
    [mediaQueries.mobile]: {
      fontSize: '0.8rem',
    },
  },
  emptyState: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '48px 24px',
    textAlign: 'center',
    color: 'rgba(0, 0, 0, 0.6)',
    [mediaQueries.mobile]: {
      padding: '32px 16px',
    },
  },
  emptyStateIcon: {
    fontSize: '48px',
    marginBottom: '16px',
    color: 'rgba(0, 0, 0, 0.3)',
    [mediaQueries.mobile]: {
      fontSize: '36px',
    },
  },
  tabs: {
    borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
  },
  loadingContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '32px',
  },
  errorContainer: {
    padding: '24px',
    textAlign: 'center',
    color: '#D32F2F',
  },
}));

export default useStyles;