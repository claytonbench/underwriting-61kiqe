import { makeStyles } from '@mui/styles';
import { Theme } from '@mui/material';
import { mobile, tablet } from '../../responsive/breakpoints';

/**
 * Custom styles for the ApplicationReview component and its child components.
 * Provides styling for the comprehensive application review interface used by underwriters.
 */
const useStyles = makeStyles((theme: Theme) => ({
  // Main container
  root: {
    padding: theme.spacing(3),
    marginBottom: theme.spacing(4),
    width: '100%',
    [mobile]: {
      padding: theme.spacing(1),
      marginBottom: theme.spacing(2),
    }
  },

  // Section styling
  sectionHeader: {
    marginBottom: theme.spacing(2),
    fontWeight: 500,
    color: theme.palette.primary.main,
    paddingBottom: theme.spacing(1),
    borderBottom: `1px solid ${theme.palette.divider}`,
    fontSize: '1.125rem',
  },
  sectionContent: {
    marginBottom: theme.spacing(3),
  },

  // Tab styling
  tabs: {
    borderBottom: '1px solid',
    borderColor: theme.palette.divider,
    marginBottom: theme.spacing(2),
  },
  tabPanel: {
    padding: theme.spacing(3, 0),
    [mobile]: {
      padding: theme.spacing(2, 0),
    }
  },

  // Information grid layout
  infoGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: theme.spacing(2),
    marginBottom: theme.spacing(2),
    [mobile]: {
      gridTemplateColumns: '1fr',
      gap: theme.spacing(1),
    },
    [tablet]: {
      gridTemplateColumns: 'repeat(2, 1fr)',
    }
  },
  infoLabel: {
    fontWeight: 500,
    color: theme.palette.text.secondary,
    fontSize: '0.875rem',
  },
  infoValue: {
    color: theme.palette.text.primary,
    fontSize: '1rem',
    overflowWrap: 'break-word',
  },

  // Credit score styling
  creditScoreContainer: {
    display: 'flex',
    alignItems: 'center',
    marginBottom: theme.spacing(1),
  },
  creditScore: {
    fontWeight: 'bold',
    fontSize: '1.5rem',
    padding: theme.spacing(1, 2),
    borderRadius: '4px',
    marginRight: theme.spacing(2),
    display: 'inline-block',
  },
  creditScoreExcellent: {
    backgroundColor: '#388e3c', // Green
    color: '#ffffff',
  },
  creditScoreGood: {
    backgroundColor: '#4caf50', // Light green
    color: '#ffffff',
  },
  creditScoreFair: {
    backgroundColor: '#ffa000', // Amber
    color: '#000000',
  },
  creditScorePoor: {
    backgroundColor: '#d32f2f', // Red
    color: '#ffffff',
  },

  // Financial metrics
  financialMetric: {
    display: 'flex',
    alignItems: 'center',
    marginBottom: theme.spacing(1),
  },
  metricLabel: {
    marginRight: theme.spacing(1),
    fontWeight: 500,
  },
  metricValue: {
    fontWeight: 'bold',
  },
  metricGood: {
    color: theme.palette.success.main,
  },
  metricWarning: {
    color: theme.palette.warning.main,
  },
  metricDanger: {
    color: theme.palette.error.main,
  },

  // Document section styling
  documentTable: {
    marginTop: theme.spacing(2),
    width: '100%',
    borderCollapse: 'collapse',
    '& th': {
      textAlign: 'left',
      padding: theme.spacing(1),
      backgroundColor: theme.palette.action.hover,
    },
    '& td': {
      padding: theme.spacing(1),
      borderBottom: `1px solid ${theme.palette.divider}`,
    },
    [mobile]: {
      '& th:nth-child(3), & td:nth-child(3)': {
        display: 'none',
      }
    }
  },
  documentActions: {
    display: 'flex',
    gap: theme.spacing(1),
  },
  documentStatus: {
    padding: theme.spacing(0.5, 1),
    borderRadius: '4px',
    fontSize: '0.75rem',
    fontWeight: 'bold',
    display: 'inline-block',
  },
  statusUploaded: {
    backgroundColor: theme.palette.info.light,
    color: theme.palette.info.contrastText,
  },
  statusSigned: {
    backgroundColor: theme.palette.success.light,
    color: theme.palette.success.contrastText,
  },
  statusMissing: {
    backgroundColor: theme.palette.error.light,
    color: theme.palette.error.contrastText,
  },

  // Underwriting decision section
  decisionCard: {
    padding: theme.spacing(2),
    borderRadius: '4px',
    marginTop: theme.spacing(2),
    boxShadow: '0 1px 3px rgba(0,0,0,0.12)',
    position: 'relative',
    '&:before': {
      content: '""',
      position: 'absolute',
      left: 0,
      top: 0,
      bottom: 0,
      width: '5px',
      borderTopLeftRadius: '4px',
      borderBottomLeftRadius: '4px',
    }
  },
  decisionApproved: {
    '&:before': {
      backgroundColor: theme.palette.success.main,
    }
  },
  decisionDenied: {
    '&:before': {
      backgroundColor: theme.palette.error.main,
    }
  },
  decisionRevise: {
    '&:before': {
      backgroundColor: theme.palette.warning.main,
    }
  },
  decisionHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing(2),
  },
  decisionTitle: {
    fontWeight: 'bold',
    fontSize: '1.125rem',
  },
  decisionDate: {
    color: theme.palette.text.secondary,
    fontSize: '0.875rem',
  },
  
  // Stipulation list
  stipulationList: {
    marginTop: theme.spacing(2),
    listStyleType: 'none',
    padding: 0,
  },
  stipulationItem: {
    marginBottom: theme.spacing(1),
    padding: theme.spacing(1),
    display: 'flex',
    alignItems: 'flex-start',
    gap: theme.spacing(1),
    backgroundColor: theme.palette.background.default,
    borderRadius: '4px',
  },
  stipulationText: {
    flex: 1,
  },
  stipulationStatus: {
    fontSize: '0.75rem',
    fontWeight: 'bold',
    padding: theme.spacing(0.25, 1),
    borderRadius: '4px',
  },
  
  // Form controls for decision making
  formControl: {
    marginBottom: theme.spacing(2),
    width: '100%',
  },
  radioGroup: {
    marginBottom: theme.spacing(2),
  },
  amountField: {
    marginBottom: theme.spacing(2),
  },
  textField: {
    marginBottom: theme.spacing(2),
  },
  buttonContainer: {
    display: 'flex',
    justifyContent: 'flex-end',
    gap: theme.spacing(2),
    marginTop: theme.spacing(3),
  },
  
  // Loading and error states
  loadingContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    padding: theme.spacing(4),
    minHeight: '300px',
  },
  errorContainer: {
    padding: theme.spacing(2),
    marginTop: theme.spacing(2),
    backgroundColor: theme.palette.error.light,
    borderRadius: '4px',
    color: theme.palette.error.contrastText,
  },

  // Comments section
  commentSection: {
    marginTop: theme.spacing(3),
  },
  commentInput: {
    width: '100%',
  },
  comments: {
    marginTop: theme.spacing(2),
  },
  comment: {
    padding: theme.spacing(1, 2),
    marginBottom: theme.spacing(1),
    backgroundColor: theme.palette.background.default,
    borderRadius: '4px',
    borderLeft: `4px solid ${theme.palette.primary.main}`,
  },
  commentHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: theme.spacing(0.5),
  },
  commentAuthor: {
    fontWeight: 500,
  },
  commentDate: {
    fontSize: '0.75rem',
    color: theme.palette.text.secondary,
  },
  
  // File viewer
  fileViewer: {
    marginTop: theme.spacing(2),
    width: '100%',
    border: `1px solid ${theme.palette.divider}`,
    borderRadius: '4px',
    minHeight: '400px',
    overflow: 'hidden',
  },
}));

export default useStyles;