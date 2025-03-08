import { makeStyles } from '@mui/styles';
import { Theme } from '@mui/material';
import { mediaQueries } from '../../responsive/breakpoints';

const useStyles = makeStyles((theme: Theme) => ({
  // Root container with appropriate margin and padding
  root: {
    margin: theme.spacing(2, 0),
    width: '100%',
  },
  
  // Status badge with proper positioning and emphasis
  statusBadge: {
    marginBottom: theme.spacing(2),
    display: 'inline-flex',
  },
  
  // Application details section with container styling
  detailsContainer: {
    marginBottom: theme.spacing(3),
  },
  
  // Details grid layout with responsive adjustments
  detailsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: theme.spacing(3),
    marginTop: theme.spacing(2),
    [mediaQueries.mobile]: {
      gridTemplateColumns: '1fr',
      gap: theme.spacing(2),
    },
  },
  
  // Individual detail item styling
  detailItem: {
    marginBottom: theme.spacing(2),
  },
  
  // Styling for detail item labels
  detailLabel: {
    fontWeight: 500,
    color: theme.palette.text.secondary,
    marginBottom: theme.spacing(0.5),
  },
  
  // Styling for detail item values
  detailValue: {
    fontWeight: 400,
  },
  
  // Timeline section styling
  timelineSection: {
    marginTop: theme.spacing(3),
    marginBottom: theme.spacing(3),
  },
  
  // Timeline dot styling
  timelineDot: {
    boxShadow: 'none',
  },
  
  // Timeline content styling
  timelineContent: {
    padding: theme.spacing(1, 2),
  },
  
  // Timeline date styling
  timelineDate: {
    minWidth: '100px',
    textAlign: 'right',
    color: theme.palette.text.secondary,
    fontSize: '0.875rem',
  },
  
  // Required actions section styling
  actionsSection: {
    marginTop: theme.spacing(3),
  },
  
  // Actions list styling
  actionsList: {
    padding: 0,
  },
  
  // Individual action item styling
  actionItem: {
    padding: theme.spacing(2),
    borderBottom: `1px solid ${theme.palette.divider}`,
    '&:last-child': {
      borderBottom: 'none',
    },
  },
  
  // Action button styling with responsive adjustments
  actionButton: {
    marginLeft: theme.spacing(2),
    [mediaQueries.mobile]: {
      marginTop: theme.spacing(1),
      marginLeft: 0,
    },
  },
  
  // Action description styling
  actionDescription: {
    fontWeight: 500,
  },
  
  // Action due date styling
  actionDueDate: {
    color: theme.palette.text.secondary,
    fontSize: '0.875rem',
  },
  
  // Styling for when there are no actions
  noActions: {
    padding: theme.spacing(2),
    textAlign: 'center',
    color: theme.palette.text.secondary,
  },
}));

export default useStyles;