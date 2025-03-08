import { makeStyles } from '@mui/styles';
import { Theme } from '@mui/material';
import { mediaQueries } from '../../responsive/breakpoints';

// Constants for responsive sizing
const AUTH_CARD_MAX_WIDTH = 450;
const AUTH_CARD_TABLET_WIDTH = '80%';
const AUTH_CARD_MOBILE_WIDTH = '100%';

/**
 * Custom hook that generates CSS classes for the AuthLayout component
 * Provides responsive styling for authentication pages (login, registration, password reset)
 */
const useStyles = makeStyles((theme: Theme) => ({
  // Main container with full height and centered content
  root: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
    width: '100%',
    backgroundColor: theme.palette.background.default,
  },
  
  // Paper background component
  paper: {
    width: '100%',
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: theme.palette.background.default,
  },
  
  // Content container with responsive padding
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: theme.spacing(4),
    width: '100%',
    [mediaQueries.mobile]: {
      padding: theme.spacing(2),
    },
  },
  
  // Application logo styling
  logo: {
    width: '180px',
    height: 'auto',
    marginBottom: theme.spacing(4),
    [mediaQueries.mobile]: {
      width: '140px',
      marginBottom: theme.spacing(3),
    },
  },
  
  // Authentication card with responsive width and shadow
  card: {
    width: '100%',
    maxWidth: AUTH_CARD_MAX_WIDTH,
    marginBottom: theme.spacing(4),
    boxShadow: theme.shadows[2],
    borderRadius: theme.shape.borderRadius,
    overflow: 'hidden',
    [mediaQueries.tablet]: {
      width: AUTH_CARD_TABLET_WIDTH,
    },
    [mediaQueries.mobile]: {
      width: AUTH_CARD_MOBILE_WIDTH,
      boxShadow: 'none',
    },
  },
  
  // Card content with appropriate padding
  cardContent: {
    padding: theme.spacing(4),
    [mediaQueries.mobile]: {
      padding: theme.spacing(2),
    },
  },
  
  // Title styling with typography and spacing
  title: {
    marginBottom: theme.spacing(2),
    textAlign: 'center',
    color: theme.palette.text.primary,
    fontWeight: 500,
    fontSize: '1.5rem',
  },
  
  // Subtitle styling with typography and spacing
  subtitle: {
    marginBottom: theme.spacing(4),
    textAlign: 'center',
    color: theme.palette.text.secondary,
    fontSize: '1rem',
    [mediaQueries.mobile]: {
      marginBottom: theme.spacing(3),
    },
  },
}));

export default useStyles;