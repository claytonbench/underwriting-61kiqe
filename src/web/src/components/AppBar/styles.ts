import { makeStyles } from '@mui/styles'; // @mui/styles v5.14.0
import { Theme } from '@mui/material'; // @mui/material v5.14.0
import { mediaQueries } from '../../responsive/breakpoints';

// Define the constant for AppBar height
export const appBarHeight = '64px';

// Create styles for the AppBar component using Material-UI's makeStyles
const useStyles = makeStyles((theme: Theme) => ({
  // Styles for the AppBar root element
  root: {
    backgroundColor: theme.palette.background.paper,
    boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.1)',
    zIndex: theme.zIndex.appBar
  },
  
  // Styles for the toolbar within the AppBar
  toolbar: {
    display: 'flex',
    justifyContent: 'space-between',
    height: appBarHeight,
    padding: '0 16px',
    [mediaQueries.mobile]: {
      padding: '0 8px'
    }
  },
  
  // Styles for the logo container
  logoContainer: {
    display: 'flex',
    alignItems: 'center',
    textDecoration: 'none'
  },
  
  // Styles for the application logo
  logo: {
    height: '40px',
    marginRight: '16px',
    [mediaQueries.mobile]: {
      height: '32px',
      marginRight: '8px'
    }
  },
  
  // Styles for the application title
  title: {
    color: theme.palette.text.primary,
    fontWeight: 500,
    fontSize: '1.25rem',
    [mediaQueries.mobile]: {
      fontSize: '1rem',
      display: 'none'
    }
  },
  
  // Styles for the navigation section
  navSection: {
    display: 'flex',
    alignItems: 'center',
    [mediaQueries.mobile]: {
      display: 'none'
    }
  },
  
  // Styles for navigation items
  navItem: {
    margin: '0 8px',
    color: theme.palette.text.primary,
    textDecoration: 'none',
    fontWeight: 400,
    fontSize: '1rem',
    padding: '6px 12px',
    borderRadius: '4px',
    transition: 'background-color 0.2s ease-in-out',
    '&:hover': {
      backgroundColor: 'rgba(0, 0, 0, 0.04)'
    }
  },
  
  // Styles for active navigation items
  activeNavItem: {
    color: theme.palette.primary.main,
    fontWeight: 500,
    backgroundColor: 'rgba(25, 118, 210, 0.08)'
  },
  
  // Styles for the user section (notification bell and user menu)
  userSection: {
    display: 'flex',
    alignItems: 'center'
  },
  
  // Styles for the mobile menu button
  mobileMenuButton: {
    display: 'none',
    [mediaQueries.mobile]: {
      display: 'flex',
      marginRight: '8px'
    }
  },
  
  // Styles for the user avatar
  avatar: {
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.primary.contrastText,
    width: '32px',
    height: '32px',
    fontSize: '1rem'
  },
  
  // Styles for the notification badge
  notificationBadge: {
    marginRight: '16px',
    [mediaQueries.mobile]: {
      marginRight: '8px'
    }
  },
  
  // Styles for the mobile navigation drawer
  mobileDrawer: {
    width: '250px'
  },
  
  // Styles for the mobile drawer header
  drawerHeader: {
    display: 'flex',
    alignItems: 'center',
    padding: '16px',
    justifyContent: 'space-between',
    borderBottom: '1px solid rgba(0, 0, 0, 0.12)'
  },
  
  // Styles for mobile drawer items
  drawerItem: {
    padding: '12px 16px'
  },
  
  // Styles for active mobile drawer items
  activeDrawerItem: {
    backgroundColor: 'rgba(25, 118, 210, 0.08)',
    color: theme.palette.primary.main,
    fontWeight: 500
  }
}));

export default useStyles;