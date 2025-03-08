import React, { useState } from 'react';
import { 
  IconButton, 
  Avatar, 
  Menu, 
  MenuItem, 
  ListItemIcon, 
  ListItemText, 
  Divider, 
  Typography 
} from '@mui/material';
import { 
  AccountCircle as AccountCircleIcon, 
  Settings as SettingsIcon, 
  ExitToApp as ExitToAppIcon 
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import useStyles from './styles';
import useAuth from '../../hooks/useAuth';
import { UserType } from '../../types/auth.types';

const UserMenu: React.FC = () => {
  // Get authentication state and logout function
  const { state, logout } = useAuth();
  
  // Get component styles
  const classes = useStyles();
  
  // Get navigation function
  const navigate = useNavigate();
  
  // State for menu anchor element
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  
  /**
   * Opens the user menu dropdown
   */
  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };
  
  /**
   * Closes the user menu dropdown
   */
  const handleMenuClose = () => {
    setAnchorEl(null);
  };
  
  /**
   * Navigates to the user profile page
   */
  const handleProfileClick = () => {
    handleMenuClose();
    navigate('/profile');
  };
  
  /**
   * Navigates to the settings page based on user role
   */
  const handleSettingsClick = () => {
    handleMenuClose();
    
    // Different settings routes based on user role
    if (state.user?.userType === UserType.SYSTEM_ADMIN) {
      navigate('/admin/settings');
    } else if (state.user?.userType === UserType.SCHOOL_ADMIN) {
      navigate('/school/settings');
    } else if (state.user?.userType === UserType.UNDERWRITER || 
              state.user?.userType === UserType.QC) {
      navigate('/staff/settings');
    } else {
      // Default for borrowers and co-borrowers
      navigate('/settings');
    }
  };
  
  /**
   * Logs the user out of the application
   */
  const handleLogout = () => {
    handleMenuClose();
    logout();
    navigate('/login');
  };
  
  /**
   * Generates user initials from first and last name
   */
  const getUserInitials = (firstName: string, lastName: string): string => {
    const firstInitial = firstName ? firstName.charAt(0) : '';
    const lastInitial = lastName ? lastName.charAt(0) : '';
    return `${firstInitial}${lastInitial}`;
  };
  
  // Extract user information from auth state
  const { user } = state;
  const userInitials = user ? getUserInitials(user.firstName, user.lastName) : '';
  
  return (
    <>
      <IconButton
        aria-label="user account"
        aria-controls="user-menu"
        aria-haspopup="true"
        onClick={handleMenuOpen}
        color="inherit"
      >
        <Avatar className={classes.avatar}>
          {userInitials}
        </Avatar>
      </IconButton>
      <Menu
        id="user-menu"
        anchorEl={anchorEl}
        keepMounted
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        {user && (
          <div>
            <MenuItem disabled>
              <Typography variant="body1">
                {`${user.firstName} ${user.lastName}`}
              </Typography>
            </MenuItem>
            <Typography
              variant="caption"
              color="textSecondary"
              style={{ padding: '0 16px' }}
            >
              {user.email}
            </Typography>
            <Divider style={{ margin: '8px 0' }} />
          </div>
        )}
        <MenuItem onClick={handleProfileClick}>
          <ListItemIcon>
            <AccountCircleIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Profile" />
        </MenuItem>
        <MenuItem onClick={handleSettingsClick}>
          <ListItemIcon>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Settings" />
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleLogout}>
          <ListItemIcon>
            <ExitToAppIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Logout" />
        </MenuItem>
      </Menu>
    </>
  );
};

export default UserMenu;