import { makeStyles } from '@mui/styles';
import { Theme } from '@mui/material';
import { mediaQueries } from '../../responsive/breakpoints';

/**
 * Custom hook that provides consistent styling for the SchoolManagement components.
 * Includes styles for SchoolForm, ProgramForm, and SchoolAdminForm components with
 * responsive design adjustments for different screen sizes.
 */
const useStyles = makeStyles((theme: Theme) => ({
  // Base container for all forms
  formContainer: {
    width: '100%',
    maxWidth: '800px',
    margin: '0 auto',
    padding: theme.spacing(3),
    [mediaQueries.mobile]: {
      padding: theme.spacing(2),
    },
  },

  // Section styling with appropriate spacing
  formSection: {
    marginBottom: theme.spacing(3),
    '& > *': {
      marginBottom: theme.spacing(2),
    },
  },

  // Section title styling
  sectionTitle: {
    marginBottom: theme.spacing(2),
    fontWeight: 500,
    color: theme.palette.text.primary,
  },

  // Divider between sections
  divider: {
    margin: theme.spacing(3, 0),
  },

  // Form actions area - contains buttons
  formActions: {
    display: 'flex',
    justifyContent: 'flex-end',
    gap: theme.spacing(2),
    marginTop: theme.spacing(3),
    [mediaQueries.mobile]: {
      flexDirection: 'column',
      '& > button': {
        width: '100%',
      },
    },
  },

  // Full width form field
  fullWidthField: {
    width: '100%',
    marginBottom: theme.spacing(2),
  },

  // Field grid for multiple fields in a row
  fieldGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: theme.spacing(2),
    marginBottom: theme.spacing(2),
    [mediaQueries.mobile]: {
      gridTemplateColumns: '1fr',
    },
  },

  // Switch field styling
  switchField: {
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1),
    display: 'flex',
    alignItems: 'center',
  },

  // Program history table styling
  programHistoryTable: {
    marginTop: theme.spacing(3),
    width: '100%',
    '& th': {
      fontWeight: 600,
    },
    [mediaQueries.mobile]: {
      '& .MuiTableCell-root': {
        padding: theme.spacing(1),
      },
    },
  },

  // School administrators table styling
  adminTable: {
    marginTop: theme.spacing(2),
    width: '100%',
    [mediaQueries.mobile]: {
      '& .MuiTableCell-root': {
        padding: theme.spacing(1),
      },
    },
  },

  // Responsive container with media queries
  responsiveContainer: {
    width: '100%',
    [mediaQueries.mobile]: {
      padding: theme.spacing(1),
    },
    [mediaQueries.tablet]: {
      padding: theme.spacing(2),
    },
  },

  // Form card styling
  formCard: {
    marginBottom: theme.spacing(3),
    padding: theme.spacing(2),
    [mediaQueries.mobile]: {
      padding: theme.spacing(1.5),
    },
  },

  // Form header styling
  formHeader: {
    marginBottom: theme.spacing(3),
    padding: theme.spacing(2, 0),
    borderBottom: `1px solid ${theme.palette.divider}`,
  },

  // Add button styling
  addButton: {
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(3),
  },

  // Error message styling
  errorMessage: {
    color: theme.palette.error.main,
    marginTop: theme.spacing(1),
    fontSize: '0.875rem',
  },

  // Form helper text styling
  helperText: {
    marginTop: theme.spacing(0.5),
    fontSize: '0.75rem',
    color: theme.palette.text.secondary,
  },
}));

export default useStyles;