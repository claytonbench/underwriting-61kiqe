import { makeStyles } from '@mui/styles';
import { Theme } from '@mui/material';
import { mediaQueries } from '../../responsive/breakpoints';

/**
 * Custom hook that generates styles for the Card component
 */
const useStyles = makeStyles((theme: Theme) => ({
  /**
   * Base styles for the card component
   */
  root: {
    margin: theme.spacing(2, 0),
    height: 'auto',
    [mediaQueries.mobile]: {
      margin: theme.spacing(1, 0),
    },
  },
  /**
   * Styles for cards that should fill the available height
   */
  fullHeight: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
  },
  /**
   * Styles for the card content area
   */
  content: {
    padding: theme.spacing(3),
    flex: '1 1 auto', // Allow content to grow and fill available space
    [mediaQueries.mobile]: {
      padding: theme.spacing(2),
    },
  },
  /**
   * Styles for content areas without padding
   */
  noPadding: {
    padding: '0 !important',
  },
}));

export default useStyles;