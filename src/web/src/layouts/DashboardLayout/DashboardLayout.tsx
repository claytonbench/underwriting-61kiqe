import React, { useState, useEffect } from 'react';
import { Box, CssBaseline, useTheme, useMediaQuery } from '@mui/material'; // @mui/material v5.14.0
import { Navigate, useLocation } from 'react-router-dom'; // react-router-dom v6.14.0

import useStyles from './styles';
import Sidebar from './Sidebar';
import { useAuth } from '../../hooks/useAuth';
import ApplicationAppBar from '../../components/AppBar';

/**
 * Main layout component for authenticated users that provides a consistent structure with
 * sidebar, app bar, and content area. This layout is used for all authenticated pages
 * in the loan management system.
 * 
 * @param props Component props with children
 * @returns Rendered dashboard layout with children or redirect to login
 */
const DashboardLayout: React.FC<React.PropsWithChildren<{}>> = ({ children }) => {
  // Get authentication state
  const { state } = useAuth();
  
  // Get component styles
  const classes = useStyles();
  
  // Get theme for responsive design
  const theme = useTheme();
  
  // Get current location for route change detection
  const location = useLocation();
  
  // Check if screen is mobile size
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // State for sidebar open status - initially closed on mobile, open on desktop
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(!isMobile);

  /**
   * Opens the sidebar navigation
   */
  const handleSidebarOpen = () => {
    setSidebarOpen(true);
  };

  /**
   * Closes the sidebar navigation
   */
  const handleSidebarClose = () => {
    setSidebarOpen(false);
  };

  // Effect to handle sidebar state based on screen size changes
  useEffect(() => {
    if (isMobile) {
      setSidebarOpen(false);
    } else {
      setSidebarOpen(true);
    }
  }, [isMobile]);

  // Effect to close sidebar on mobile when route changes
  useEffect(() => {
    if (isMobile) {
      setSidebarOpen(false);
    }
  }, [isMobile, location.pathname]);

  // If user is not authenticated, redirect to login page
  if (!state.isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return (
    <Box className={classes.root}>
      <CssBaseline />
      <ApplicationAppBar />
      <Sidebar 
        open={sidebarOpen} 
        onClose={handleSidebarClose} 
        onOpen={handleSidebarOpen} 
      />
      <Box
        component="main"
        className={`${classes.content} ${sidebarOpen && !isMobile ? classes.contentShift : ''} ${isMobile ? classes.mobileContent : ''}`}
      >
        <div className={classes.toolbar} />
        {children}
      </Box>
    </Box>
  );
};

export default DashboardLayout;