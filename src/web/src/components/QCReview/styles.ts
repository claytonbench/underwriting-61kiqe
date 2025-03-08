import { makeStyles } from '@mui/styles';
import { Theme } from '@mui/material';
import { mediaQueries } from '../../responsive/breakpoints';
import { QCVerificationStatus } from '../../types/qc.types';

/**
 * Custom hook that generates styles for the QC review components
 * Provides styling for document verification, stipulation verification,
 * and checklist item components with status-specific variations
 */
const useStyles = makeStyles((theme: Theme) => ({
  // Main container
  root: {
    padding: theme.spacing(3),
    width: '100%',
    [mediaQueries.mobile]: {
      padding: theme.spacing(2),
    },
  },

  // Tabs section
  tabsContainer: {
    marginBottom: theme.spacing(3),
    [mediaQueries.mobile]: {
      marginBottom: theme.spacing(2),
    },
  },
  tabPanel: {
    padding: theme.spacing(2, 0),
  },

  // Card styles for verification items
  documentCard: {
    marginBottom: theme.spacing(2),
    border: `1px solid ${theme.palette.divider}`,
  },
  stipulationCard: {
    marginBottom: theme.spacing(2),
    border: `1px solid ${theme.palette.divider}`,
  },
  checklistCard: {
    marginBottom: theme.spacing(2),
    border: `1px solid ${theme.palette.divider}`,
  },

  // Status-specific card styles
  verifiedCard: {
    borderLeft: `4px solid ${theme.palette.success.main}`,
  },
  rejectedCard: {
    borderLeft: `4px solid ${theme.palette.error.main}`,
  },
  waivedCard: {
    borderLeft: `4px solid ${theme.palette.warning.main}`,
  },
  unverifiedCard: {
    borderLeft: `4px solid ${theme.palette.grey[400]}`,
  },

  // Card content and actions
  cardContent: {
    padding: theme.spacing(2),
    [mediaQueries.tablet]: {
      padding: theme.spacing(1.75),
    },
    [mediaQueries.mobile]: {
      padding: theme.spacing(1.5),
    },
  },
  cardActions: {
    padding: theme.spacing(1, 2, 2),
    justifyContent: 'flex-end',
    [mediaQueries.tablet]: {
      padding: theme.spacing(1, 1.75, 1.75),
    },
    [mediaQueries.mobile]: {
      padding: theme.spacing(1, 1.5, 1.5),
    },
  },

  // Status icons
  statusIcon: {
    marginRight: theme.spacing(1),
  },
  verifiedIcon: {
    color: theme.palette.success.main,
  },
  rejectedIcon: {
    color: theme.palette.error.main,
  },
  waivedIcon: {
    color: theme.palette.warning.main,
  },
  unverifiedIcon: {
    color: theme.palette.grey[400],
  },

  // Title styles
  documentTitle: {
    fontWeight: 500,
    marginBottom: theme.spacing(1),
  },
  stipulationTitle: {
    fontWeight: 500,
    marginBottom: theme.spacing(1),
  },
  checklistTitle: {
    fontWeight: 500,
    marginBottom: theme.spacing(1),
  },

  // Form elements
  commentsField: {
    marginTop: theme.spacing(2),
    width: '100%',
  },
  actionButton: {
    marginLeft: theme.spacing(1),
    [mediaQueries.tablet]: {
      marginLeft: theme.spacing(0.75),
    },
    [mediaQueries.mobile]: {
      marginLeft: theme.spacing(0.5),
    },
  },
  documentActions: {
    display: 'flex',
    justifyContent: 'flex-end',
    marginTop: theme.spacing(1),
    [mediaQueries.mobile]: {
      flexWrap: 'wrap',
    },
  },

  // Decision section
  decisionSection: {
    marginTop: theme.spacing(4),
    padding: theme.spacing(3),
    border: `1px solid ${theme.palette.divider}`,
    borderRadius: theme.shape.borderRadius,
    [mediaQueries.tablet]: {
      padding: theme.spacing(2.5),
      marginTop: theme.spacing(3.5),
    },
    [mediaQueries.mobile]: {
      padding: theme.spacing(2),
      marginTop: theme.spacing(3),
    },
  },
  decisionTitle: {
    fontWeight: 500,
    marginBottom: theme.spacing(2),
  },
  decisionOptions: {
    marginBottom: theme.spacing(2),
  },
  returnReasonField: {
    marginTop: theme.spacing(2),
    width: '100%',
  },
  notesField: {
    marginTop: theme.spacing(2),
    width: '100%',
  },
  submitButton: {
    marginTop: theme.spacing(3),
    [mediaQueries.tablet]: {
      marginTop: theme.spacing(2.5),
    },
    [mediaQueries.mobile]: {
      marginTop: theme.spacing(2),
      width: '100%',
    },
  },

  // Status chips
  statusChip: {
    marginLeft: theme.spacing(1),
    [mediaQueries.tablet]: {
      marginLeft: theme.spacing(0.75),
    },
    [mediaQueries.mobile]: {
      marginLeft: theme.spacing(0.5),
    },
  },
  verifiedChip: {
    backgroundColor: theme.palette.success.light,
    color: theme.palette.success.contrastText,
  },
  rejectedChip: {
    backgroundColor: theme.palette.error.light,
    color: theme.palette.error.contrastText,
  },
  waivedChip: {
    backgroundColor: theme.palette.warning.light,
    color: theme.palette.warning.contrastText,
  },
  unverifiedChip: {
    backgroundColor: theme.palette.grey[300],
    color: theme.palette.text.primary,
  },
}));

export default useStyles;