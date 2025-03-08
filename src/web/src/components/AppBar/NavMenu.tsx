import React, { useState, useEffect } from 'react';
import { Box, Button, Drawer, List, ListItem, ListItemText, useTheme, useMediaQuery } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import useStyles from './styles';
import { useAuth } from '../../hooks/useAuth';
import { routes } from '../../config/routes';
import { UserType } from '../../types/auth.types';

/**
 * Interface for navigation menu items
 */
interface NavigationItem {
  label: string;
  path: string;
  roles: UserType[];
}

/**
 * Props for the NavMenu component
 */
interface NavMenuProps {
  mobileMenuOpen?: boolean;
  onMobileMenuClose?: () => void;
}

/**
 * Navigation menu component that displays different navigation links based on user role.
 * Supports both desktop and mobile views with a responsive design.
 */
const NavMenu: React.FC<NavMenuProps> = ({ mobileMenuOpen = false, onMobileMenuClose }) => {
  const { state } = useAuth();
  const classes = useStyles();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [drawerOpen, setDrawerOpen] = useState<boolean>(mobileMenuOpen);

  // Update drawer state when mobileMenuOpen prop changes
  useEffect(() => {
    setDrawerOpen(mobileMenuOpen);
  }, [mobileMenuOpen]);

  // Handle drawer toggle for mobile
  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  // Handle drawer close for mobile
  const handleDrawerClose = () => {
    setDrawerOpen(false);
    if (onMobileMenuClose) {
      onMobileMenuClose();
    }
  };

  // Check if a route is currently active
  const isActiveRoute = (path: string): boolean => {
    // Handle dashboard paths which could be different based on user role
    if (path === '/dashboard' && (
        location.pathname === '/borrower' || 
        location.pathname === '/school-admin' || 
        location.pathname === '/underwriter'
      )) {
      return true;
    }
    return location.pathname === path || location.pathname.startsWith(`${path}/`);
  };

  // Get navigation items based on user role
  const getNavigationItems = (): NavigationItem[] => {
    const baseItems: NavigationItem[] = [
      { label: 'Dashboard', path: '/dashboard', roles: [UserType.SYSTEM_ADMIN, UserType.BORROWER, UserType.CO_BORROWER, UserType.SCHOOL_ADMIN, UserType.UNDERWRITER, UserType.QC] },
      { label: 'Applications', path: '/applications', roles: [UserType.SYSTEM_ADMIN, UserType.SCHOOL_ADMIN, UserType.UNDERWRITER, UserType.QC] },
      { label: 'Documents', path: '/documents', roles: [UserType.SYSTEM_ADMIN, UserType.SCHOOL_ADMIN, UserType.BORROWER, UserType.CO_BORROWER] },
    ];

    // Add role-specific navigation items
    if (state.user?.userType === UserType.SYSTEM_ADMIN) {
      baseItems.push(
        { label: 'Schools', path: '/schools', roles: [UserType.SYSTEM_ADMIN] },
        { label: 'Users', path: '/users', roles: [UserType.SYSTEM_ADMIN] },
        { label: 'Reports', path: '/reports', roles: [UserType.SYSTEM_ADMIN] },
      );
    } else if (state.user?.userType === UserType.SCHOOL_ADMIN) {
      baseItems.push(
        { label: 'Programs', path: '/programs', roles: [UserType.SCHOOL_ADMIN] },
        { label: 'Reports', path: '/reports', roles: [UserType.SCHOOL_ADMIN] },
      );
    } else if (state.user?.userType === UserType.UNDERWRITER) {
      baseItems.push(
        { label: 'Underwriting', path: '/underwriting/queue', roles: [UserType.UNDERWRITER] },
        { label: 'Reports', path: '/reports', roles: [UserType.UNDERWRITER] },
      );
    } else if (state.user?.userType === UserType.QC) {
      baseItems.push(
        { label: 'Quality Control', path: '/qc', roles: [UserType.QC] },
        { label: 'Funding', path: '/funding', roles: [UserType.QC] },
        { label: 'Reports', path: '/reports', roles: [UserType.QC] },
      );
    } else if (state.user?.userType === UserType.BORROWER || state.user?.userType === UserType.CO_BORROWER) {
      // Redirect borrowers to their specific dashboard
      baseItems[0].path = '/borrower';
    }

    // Only return navigation items that the user has permission to access
    return baseItems.filter(item => {
      if (!state.user) return false;
      return item.roles.includes(state.user.userType);
    });
  };

  const navigationItems = getNavigationItems();

  // Desktop navigation menu
  const desktopNav = (
    <Box className={classes.navSection}>
      {navigationItems.map((item) => (
        <Button
          component={Link}
          to={item.path}
          key={item.path}
          className={`${classes.navItem} ${isActiveRoute(item.path) ? classes.activeNavItem : ''}`}
          color="inherit"
        >
          {item.label}
        </Button>
      ))}
    </Box>
  );

  // Mobile navigation drawer
  const mobileNav = (
    <Drawer
      anchor="left"
      open={drawerOpen}
      onClose={handleDrawerClose}
      className={classes.mobileDrawer}
      classes={{ paper: classes.mobileDrawer }}
    >
      <Box className={classes.drawerHeader}>
        <Box>Navigation</Box>
        <Button onClick={handleDrawerClose}>X</Button>
      </Box>
      <List>
        {navigationItems.map((item) => (
          <ListItem
            button
            component={Link}
            to={item.path}
            key={item.path}
            onClick={handleDrawerClose}
            className={`${classes.drawerItem} ${isActiveRoute(item.path) ? classes.activeDrawerItem : ''}`}
          >
            <ListItemText primary={item.label} />
          </ListItem>
        ))}
      </List>
    </Drawer>
  );

  return (
    <>
      {!isMobile && desktopNav}
      {isMobile && mobileNav}
    </>
  );
};

export default NavMenu;