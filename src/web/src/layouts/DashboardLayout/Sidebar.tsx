import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  IconButton,
  Tooltip,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  Dashboard as DashboardIcon,
  Description as DescriptionIcon,
  School as SchoolIcon,
  People as PeopleIcon,
  Assignment as AssignmentIcon,
  FactCheck as FactCheckIcon,
  AttachMoney as AttachMoneyIcon,
  BarChart as BarChartIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import { Link, useLocation } from 'react-router-dom';

import useStyles from './styles';
import { useAuth } from '../../hooks/useAuth';
import { routes } from '../../config/routes';
import { UserType } from '../../types/auth.types';

// Constants for drawer widths
const DRAWER_WIDTH = 240;
const CLOSED_DRAWER_WIDTH = 64;

/**
 * Props for the Sidebar component
 */
interface SidebarProps {
  open: boolean;
  onClose: () => void;
  onOpen: () => void;
}

/**
 * Interface for navigation menu items
 */
interface NavigationItem {
  label: string;
  path: string;
  icon: React.ReactNode;
  roles: UserType[];
}

/**
 * Sidebar navigation component that displays navigation links based on user role
 */
const Sidebar: React.FC<SidebarProps> = ({ open, onClose, onOpen }) => {
  const { state } = useAuth();
  const classes = useStyles();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const { user } = state;
  
  /**
   * Checks if a given route is currently active
   */
  const isActiveRoute = (path: string): boolean => {
    // Handle exact matches
    if (location.pathname === path) return true;
    
    // Handle special cases like dashboard paths
    if (path === '/dashboard' && location.pathname === '/') return true;
    
    // Handle sub-paths (e.g., /applications/123 should match /applications)
    if (path !== '/' && location.pathname.startsWith(path)) return true;
    
    return false;
  };
  
  /**
   * Returns navigation items based on user role
   */
  const getNavigationItems = (): NavigationItem[] => {
    // Base navigation items available to all authenticated users
    const baseNavItems: NavigationItem[] = [
      {
        label: 'Dashboard',
        path: '/dashboard',
        icon: <DashboardIcon />,
        roles: [UserType.SYSTEM_ADMIN, UserType.SCHOOL_ADMIN, UserType.UNDERWRITER, UserType.QC, UserType.BORROWER, UserType.CO_BORROWER]
      }
    ];
    
    // Role-specific navigation items
    const roleSpecificItems: NavigationItem[] = [];
    
    // Only add navigation items if user is authenticated
    if (user) {
      // Common items for most roles
      if (user.userType !== UserType.BORROWER && user.userType !== UserType.CO_BORROWER) {
        roleSpecificItems.push({
          label: 'Applications',
          path: '/applications',
          icon: <DescriptionIcon />,
          roles: [UserType.SYSTEM_ADMIN, UserType.SCHOOL_ADMIN, UserType.UNDERWRITER, UserType.QC]
        });
      }
      
      // System Admin specific items
      if (user.userType === UserType.SYSTEM_ADMIN) {
        roleSpecificItems.push(
          {
            label: 'Schools',
            path: '/schools',
            icon: <SchoolIcon />,
            roles: [UserType.SYSTEM_ADMIN]
          },
          {
            label: 'Users',
            path: '/users',
            icon: <PeopleIcon />,
            roles: [UserType.SYSTEM_ADMIN]
          }
        );
      }
      
      // School Admin specific items
      if (user.userType === UserType.SCHOOL_ADMIN) {
        roleSpecificItems.push({
          label: 'Programs',
          path: '/programs',
          icon: <SchoolIcon />,
          roles: [UserType.SYSTEM_ADMIN, UserType.SCHOOL_ADMIN]
        });
      }
      
      // Underwriter specific items
      if (user.userType === UserType.UNDERWRITER || user.userType === UserType.SYSTEM_ADMIN) {
        roleSpecificItems.push({
          label: 'Underwriting',
          path: '/underwriting/queue',
          icon: <AssignmentIcon />,
          roles: [UserType.UNDERWRITER, UserType.SYSTEM_ADMIN]
        });
      }
      
      // QC specific items
      if (user.userType === UserType.QC || user.userType === UserType.SYSTEM_ADMIN) {
        roleSpecificItems.push({
          label: 'Quality Control',
          path: '/qc',
          icon: <FactCheckIcon />,
          roles: [UserType.QC, UserType.SYSTEM_ADMIN]
        });
      }
      
      // Funding navigation for QC and System Admin
      if (user.userType === UserType.QC || user.userType === UserType.SYSTEM_ADMIN) {
        roleSpecificItems.push({
          label: 'Funding',
          path: '/funding',
          icon: <AttachMoneyIcon />,
          roles: [UserType.QC, UserType.SYSTEM_ADMIN]
        });
      }
      
      // Borrower specific items
      if (user.userType === UserType.BORROWER || user.userType === UserType.CO_BORROWER) {
        roleSpecificItems.push(
          {
            label: 'My Applications',
            path: '/applications',
            icon: <DescriptionIcon />,
            roles: [UserType.BORROWER, UserType.CO_BORROWER]
          },
          {
            label: 'Documents',
            path: '/documents',
            icon: <DescriptionIcon />,
            roles: [UserType.BORROWER, UserType.CO_BORROWER]
          }
        );
      }
      
      // Reports for multiple roles
      if (user.userType !== UserType.BORROWER && user.userType !== UserType.CO_BORROWER) {
        roleSpecificItems.push({
          label: 'Reports',
          path: '/reports',
          icon: <BarChartIcon />,
          roles: [UserType.SYSTEM_ADMIN, UserType.SCHOOL_ADMIN, UserType.UNDERWRITER, UserType.QC]
        });
      }
      
      // Settings for all users
      roleSpecificItems.push({
        label: 'Settings',
        path: '/settings/profile',
        icon: <SettingsIcon />,
        roles: [UserType.SYSTEM_ADMIN, UserType.SCHOOL_ADMIN, UserType.UNDERWRITER, UserType.QC, UserType.BORROWER, UserType.CO_BORROWER]
      });
    }
    
    return [...baseNavItems, ...roleSpecificItems];
  };
  
  // Get navigation items filtered by user role
  const navigationItems = getNavigationItems().filter(item => 
    !user || item.roles.includes(user.userType)
  );
  
  return (
    <Drawer
      variant={isMobile ? "temporary" : "permanent"}
      open={isMobile ? open : true}
      onClose={onClose}
      sx={{
        width: open ? DRAWER_WIDTH : CLOSED_DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: open ? DRAWER_WIDTH : CLOSED_DRAWER_WIDTH,
          overflowX: 'hidden',
          transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
        },
      }}
    >
      <div className={classes.toolbar} style={{ 
        display: 'flex',
        alignItems: 'center',
        justifyContent: open ? 'flex-end' : 'center',
        padding: theme.spacing(0, 1),
      }}>
        <IconButton onClick={open ? onClose : onOpen}>
          {theme.direction === 'rtl' ? 
            (open ? <ChevronRightIcon /> : <ChevronLeftIcon />) : 
            (open ? <ChevronLeftIcon /> : <ChevronRightIcon />)
          }
        </IconButton>
      </div>
      <Divider />
      <List>
        {navigationItems.map((item) => (
          <ListItem
            button
            component={Link}
            to={item.path}
            key={item.path}
            selected={isActiveRoute(item.path)}
            sx={{
              minHeight: 48,
              justifyContent: open ? 'initial' : 'center',
              px: 2.5,
            }}
          >
            <Tooltip title={open ? '' : item.label} placement="right">
              <ListItemIcon
                sx={{
                  minWidth: 0,
                  mr: open ? 3 : 'auto',
                  justifyContent: 'center',
                }}
              >
                {item.icon}
              </ListItemIcon>
            </Tooltip>
            {open && <ListItemText primary={item.label} />}
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
};

export default Sidebar;