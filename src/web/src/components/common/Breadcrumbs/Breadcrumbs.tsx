import React, { useMemo } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Breadcrumbs as MuiBreadcrumbs, Typography } from '@mui/material'; // v5.14.0
import { Home as HomeIcon, NavigateNext as NavigateNextIcon } from '@mui/icons-material'; // v5.14.0
import useStyles from './styles';
import { routes } from '../../../config/routes';

/**
 * Interface for breadcrumb item structure
 */
interface BreadcrumbItem {
  path: string;
  label: string;
}

/**
 * Props interface for the Breadcrumbs component
 */
interface BreadcrumbsProps {
  breadcrumbs?: BreadcrumbItem[];
  className?: string;
}

/**
 * Generates breadcrumb items based on the current path
 * 
 * @param pathname Current URL path
 * @returns Array of breadcrumb items with path and label
 */
const generateBreadcrumbs = (pathname: string): BreadcrumbItem[] => {
  // Split the path into segments, removing empty strings
  const segments = pathname.split('/').filter(Boolean);
  const breadcrumbs: BreadcrumbItem[] = [];
  
  let currentPath = '';
  
  // Build breadcrumbs for each path segment
  for (let i = 0; i < segments.length; i++) {
    const segment = segments[i];
    currentPath += `/${segment}`;
    
    // Find matching route configuration
    const matchingRoute = routes.find(route => {
      // Handle exact matches
      if (route.path === currentPath) {
        return true;
      }
      
      // Handle dynamic routes with parameters (e.g., /users/:id)
      const routeSegments = route.path.split('/').filter(Boolean);
      const pathSegments = currentPath.split('/').filter(Boolean);
      
      if (routeSegments.length !== pathSegments.length) {
        return false;
      }
      
      return routeSegments.every((routeSegment, index) => {
        return routeSegment.startsWith(':') || routeSegment === pathSegments[index];
      });
    });
    
    if (matchingRoute) {
      breadcrumbs.push({
        path: currentPath,
        label: matchingRoute.title
      });
    } else {
      // Fallback for segments without matching routes
      // Format the segment: convert dashes to spaces and capitalize
      const formattedLabel = segment
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
      
      breadcrumbs.push({
        path: currentPath,
        label: formattedLabel
      });
    }
  }
  
  return breadcrumbs;
};

/**
 * A component that displays breadcrumb navigation based on the current route
 * 
 * @param props Component props
 * @returns Rendered breadcrumbs component
 */
const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ breadcrumbs, className }) => {
  const classes = useStyles();
  const location = useLocation();
  const navigate = useNavigate();
  
  // Use custom breadcrumbs if provided, otherwise generate from current path
  const breadcrumbItems = useMemo(() => (
    breadcrumbs || generateBreadcrumbs(location.pathname)
  ), [breadcrumbs, location.pathname]);
  
  /**
   * Handles click on the home icon
   * Navigates to the appropriate dashboard based on user role
   * 
   * @param event Mouse event
   */
  const handleHomeClick = (event: React.MouseEvent) => {
    event.preventDefault();
    
    // In a real implementation, this would get the user's role from auth context/store
    // And navigate to the appropriate dashboard
    
    // Example of role-based navigation (using auth context in real app):
    // const { user } = useAuth();
    // 
    // if (user) {
    //   switch(user.userType) {
    //     case UserType.BORROWER:
    //     case UserType.CO_BORROWER:
    //       navigate('/borrower');
    //       break;
    //     case UserType.SCHOOL_ADMIN:
    //       navigate('/school-admin');
    //       break;
    //     case UserType.UNDERWRITER:
    //       navigate('/underwriter');
    //       break;
    //     case UserType.QC:
    //       navigate('/qc');
    //       break;
    //     case UserType.SYSTEM_ADMIN:
    //     default:
    //       navigate('/dashboard');
    //   }
    // } else {
    //   navigate('/dashboard');
    // }
    
    // For now, navigate to the generic dashboard
    navigate('/dashboard');
  };
  
  return (
    <MuiBreadcrumbs
      className={`${classes.root} ${className || ''}`}
      separator={
        <NavigateNextIcon className={classes.icon} fontSize="small" aria-hidden="true" />
      }
      aria-label="Breadcrumb navigation"
    >
      {/* Home icon as first breadcrumb */}
      <Link
        to="/dashboard"
        onClick={handleHomeClick}
        className={classes.link}
        aria-label="Home"
      >
        <HomeIcon className={`${classes.icon} ${classes.homeIcon}`} fontSize="small" />
        <span className={classes.srOnly}>Home</span>
      </Link>
      
      {/* Map breadcrumb items to UI elements */}
      {breadcrumbItems.map((item, index) => {
        const isLast = index === breadcrumbItems.length - 1;
        
        return isLast ? (
          // Current page (not clickable)
          <Typography
            key={item.path}
            className={classes.currentPage}
            aria-current="page"
          >
            {item.label}
          </Typography>
        ) : (
          // Clickable breadcrumb
          <Link
            key={item.path}
            className={classes.link}
            to={item.path}
          >
            {item.label}
          </Link>
        );
      })}
    </MuiBreadcrumbs>
  );
};

export default Breadcrumbs;