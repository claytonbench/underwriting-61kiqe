import { makeStyles } from '@mui/styles'; // v5.14.0
import { Theme } from '@mui/material'; // v5.14.0
import { mediaQueries } from '../../responsive/breakpoints';

/**
 * Custom hook that creates and returns styles for the Stepper component
 * Implements the design system principles and accessibility requirements
 */
const useStyles = makeStyles((theme: Theme) => ({
  // Base styles for the stepper component
  root: {
    width: '100%',
    marginBottom: theme.spacing(4),
  },
  
  // Container for each step
  stepContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  
  // Base styles for step icons
  stepIcon: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '32px',
    height: '32px',
    borderRadius: '50%',
  },
  
  // Styles for the active step icon - uses primary color for emphasis
  activeStepIcon: {
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.primary.contrastText,
  },
  
  // Styles for completed step icons - uses success color for positive feedback
  completedStepIcon: {
    backgroundColor: theme.palette.success.main,
    color: theme.palette.success.contrastText,
  },
  
  // Styles for pending step icons - uses muted colors for inactive state
  pendingStepIcon: {
    backgroundColor: theme.palette.grey[300],
    color: theme.palette.text.secondary,
  },
  
  // Base styles for step connectors between step icons
  connector: {
    height: '2px',
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1),
  },
  
  // Styles for active step connectors
  activeConnector: {
    backgroundColor: theme.palette.primary.main,
  },
  
  // Styles for completed step connectors
  completedConnector: {
    backgroundColor: theme.palette.success.main,
  },
  
  // Styles for pending step connectors
  pendingConnector: {
    backgroundColor: theme.palette.grey[300],
  },
  
  // Base styles for step labels
  stepLabel: {
    marginTop: theme.spacing(1),
    textAlign: 'center',
    fontWeight: 500,
  },
  
  // Styles for active step labels
  activeStepLabel: {
    color: theme.palette.primary.main,
  },
  
  // Styles for completed step labels
  completedStepLabel: {
    color: theme.palette.success.main,
  },
  
  // Styles for pending step labels
  pendingStepLabel: {
    color: theme.palette.text.secondary,
  },
  
  // Styles for step descriptions
  stepDescription: {
    fontSize: '0.875rem',
    color: theme.palette.text.secondary,
    textAlign: 'center',
    marginTop: theme.spacing(0.5),
  },
  
  // Styles for vertical orientation
  verticalStepper: {
    alignItems: 'flex-start',
  },
  
  // Responsive adjustments for mobile devices
  mobileAdjustment: {
    fontSize: '0.75rem',
    marginTop: theme.spacing(0.5),
    marginBottom: theme.spacing(0.5),
    [mediaQueries.mobile]: {
      // Additional mobile-specific adjustments
      fontSize: '0.7rem',
    }
  },
  
  // Responsive styles for all elements can be applied conditionally
  [mediaQueries.mobile]: {
    stepIcon: {
      width: '24px',
      height: '24px',
    },
    stepLabel: {
      fontSize: '0.75rem',
    },
    connector: {
      height: '1px',
      marginTop: theme.spacing(0.5),
      marginBottom: theme.spacing(0.5),
    },
    stepDescription: {
      fontSize: '0.75rem',
    }
  }
}));

export default useStyles;