import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  useTheme,
  useMediaQuery
} from '@mui/material'; // @mui/material v5.14.0
import { Menu as MenuIcon } from '@mui/icons-material'; // @mui/icons-material v5.14.0
import { Link } from 'react-router-dom'; // react-router-dom v6.14.0
import useStyles from './styles';
import NavMenu from './NavMenu';
import UserMenu from './UserMenu';
import NotificationBell from './NotificationBell';
import { useAuth } from '../../hooks/useAuth';

/**
 * Main application header component that provides navigation, user menu, and notification functionality
 * Adapts to different screen sizes and displays appropriate navigation options based on user role
 */
const ApplicationAppBar: React.FC = () => {
  // Get authentication state
  const { state } = useAuth();
  
  // Get component styles
  const classes = useStyles();
  
  // Get theme for responsive design
  const theme = useTheme();
  
  // Check if screen is mobile size
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // State for mobile menu open status
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);

  /**
   * Toggles the mobile navigation menu open/closed state
   */
  const handleMobileMenuToggle = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  /**
   * Closes the mobile navigation menu
   */
  const handleMobileMenuClose = () => {
    setMobileMenuOpen(false);
  };

  return (
    <AppBar position="fixed" className={classes.root} color="default">
      <Toolbar className={classes.toolbar}>
        {/* Logo and Title */}
        <Link to={state.isAuthenticated ? '/dashboard' : '/'} className={classes.logoContainer}>
          <img src="/logo.png" alt="Logo" className={classes.logo} />
          <Typography variant="h6" className={classes.title}>
            Loan Management System
          </Typography>
        </Link>

        {/* Navigation Links - Only shown if authenticated */}
        {state.isAuthenticated && (
          <NavMenu 
            mobileMenuOpen={mobileMenuOpen} 
            onMobileMenuClose={handleMobileMenuClose} 
          />
        )}

        {/* Right side items: notifications and user menu */}
        <Box className={classes.userSection}>
          {/* Notification Bell - Only shown if authenticated */}
          {state.isAuthenticated && <NotificationBell />}
          
          {/* User Menu - Only shown if authenticated */}
          {state.isAuthenticated && <UserMenu />}
        </Box>
        
        {/* Mobile menu button - CSS will handle display based on screen size */}
        {state.isAuthenticated && (
          <IconButton
            edge="start"
            color="inherit"
            aria-label="menu"
            onClick={handleMobileMenuToggle}
            className={classes.mobileMenuButton}
          >
            <MenuIcon />
          </IconButton>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default ApplicationAppBar;