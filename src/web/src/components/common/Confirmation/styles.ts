import { makeStyles } from '@mui/styles'; // v5.14.0
import { Theme } from '@mui/material'; // v5.14.0
import theme from '../../../config/theme';

/**
 * Custom hook that generates styles for the ConfirmationDialog component
 * Provides styling for dialog elements, buttons, and loading states
 * consistent with the application's design system
 */
const useStyles = makeStyles((theme: Theme) => ({
  /**
   * Styles for the dialog content area
   */
  dialogContent: {
    padding: theme.spacing(2, 3),
    minWidth: '300px',
  },
  
  /**
   * Styles for the dialog actions container
   * Maintains proper spacing between buttons and from content
   */
  dialogActions: {
    padding: theme.spacing(2, 3, 3),
    justifyContent: 'space-between',
  },
  
  /**
   * Styles for the confirm action button
   * Uses error colors to visually indicate destructive actions
   */
  confirmButton: {
    backgroundColor: theme.palette.error.main,
    color: theme.palette.error.contrastText,
    '&:hover': {
      backgroundColor: theme.palette.error.dark,
    },
    '&:focus-visible': {
      outline: '2px solid',
      outlineColor: theme.palette.error.light,
      outlineOffset: '2px',
    },
    minWidth: '100px',
  },
  
  /**
   * Styles for the cancel action button
   */
  cancelButton: {
    minWidth: '100px',
  },
  
  /**
   * Styles for the loading state container within buttons
   * Displays a loading indicator alongside button text
   */
  loadingWrapper: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
  },
}));

export default useStyles;