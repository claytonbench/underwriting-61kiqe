import { makeStyles } from '@mui/styles';
import { Theme } from '@mui/material';
import { mediaQueries } from '../../responsive/breakpoints';

/**
 * Styles for the UserManagement components including UserForm and PermissionSelection
 * Components are designed to be responsive and follow accessibility guidelines
 * with proper spacing, contrast, and layout considerations.
 */
const useStyles = makeStyles((theme: Theme) => ({
  // Main form container with responsive width constraints
  formContainer: {
    width: '100%',
    maxWidth: 800,
    margin: '0 auto',
    padding: theme.spacing(3),
    [mediaQueries.mobile]: {
      padding: theme.spacing(2),
    },
  },

  // Form sections with consistent bottom margins
  formSection: {
    marginBottom: theme.spacing(4),
    [mediaQueries.mobile]: {
      marginBottom: theme.spacing(3),
    },
  },

  // Section titles with primary color for emphasis
  sectionTitle: {
    marginBottom: theme.spacing(2),
    fontWeight: 500,
    color: theme.palette.primary.main,
  },

  // Container for form action buttons with proper alignment and spacing
  formActions: {
    display: 'flex',
    justifyContent: 'flex-end',
    gap: theme.spacing(2),
    marginTop: theme.spacing(4),
    [mediaQueries.mobile]: {
      flexDirection: 'column',
      '& > button': {
        width: '100%',
      },
    },
  },

  // Tabs container with bottom border
  tabsContainer: {
    marginBottom: theme.spacing(3),
    borderBottom: `1px solid ${theme.palette.divider}`,
  },

  // Individual tab styling
  tab: {
    fontWeight: 500,
    '&.Mui-selected': {
      color: theme.palette.primary.main,
    },
  },

  // Permission selection container
  permissionContainer: {
    marginTop: theme.spacing(2),
  },

  // Permission group with padding and margin
  permissionGroup: {
    marginBottom: theme.spacing(2),
    padding: theme.spacing(1, 0),
    backgroundColor: theme.palette.background.paper,
    borderRadius: theme.shape.borderRadius,
  },

  // Permission group title
  permissionGroupTitle: {
    fontWeight: 500,
    marginBottom: theme.spacing(1),
    padding: theme.spacing(0, 2),
  },

  // Individual permission item
  permissionItem: {
    marginLeft: theme.spacing(2),
    display: 'flex',
    alignItems: 'center',
  },

  // Indented checkbox for hierarchical permissions
  indentedCheckbox: {
    marginLeft: theme.spacing(2),
  },

  // Divider with consistent vertical margins
  divider: {
    margin: theme.spacing(2, 0),
  },

  // Role selection section
  roleSelection: {
    marginBottom: theme.spacing(3),
  },

  // Alert messages
  alert: {
    marginBottom: theme.spacing(3),
  },

  // Responsive grid layout that adjusts for smaller screens
  responsiveGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: theme.spacing(2),
    [mediaQueries.mobile]: {
      gridTemplateColumns: '1fr',
    },
  },

  // User type selection with responsive layout
  userTypeSelection: {
    display: 'flex',
    flexDirection: 'column',
    gap: theme.spacing(1),
    marginBottom: theme.spacing(3),
  },

  // School selection for school admin profiles
  schoolSelection: {
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(2),
  },

  // Form field with bottom margin
  formField: {
    marginBottom: theme.spacing(2),
  },

  // Toggle button with styling consistency
  toggleButton: {
    '&.MuiToggleButton-root': {
      textTransform: 'none',
    },
    '&.Mui-selected': {
      backgroundColor: theme.palette.primary.light,
      color: theme.palette.primary.contrastText,
      '&:hover': {
        backgroundColor: theme.palette.primary.main,
      },
    },
  },

  // Password reset section
  passwordReset: {
    marginTop: theme.spacing(2),
    padding: theme.spacing(2),
    border: `1px solid ${theme.palette.divider}`,
    borderRadius: theme.shape.borderRadius,
    backgroundColor: theme.palette.background.paper,
  },

  // Helper text with proper spacing
  helperText: {
    marginTop: theme.spacing(0.5),
    color: theme.palette.text.secondary,
    fontSize: '0.75rem',
  },

  // Mobile adaptations
  [mediaQueries.mobile]: {
    formContainer: {
      padding: theme.spacing(1.5),
    },
  },

  // Tablet adaptations
  [mediaQueries.tablet]: {
    formContainer: {
      padding: theme.spacing(2),
    },
  },
}));

export default useStyles;