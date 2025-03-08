import { makeStyles } from '@mui/styles'; // v5.14.0
import { Theme } from '@mui/material'; // v5.14.0
import { mediaQueries } from '../../responsive/breakpoints';

/**
 * Styles for the Page and PageHeader components
 * Provides consistent layout styling with responsive adjustments
 */
const useStyles = makeStyles((theme: Theme) => ({
  pageContainer: {
    padding: '24px',
    width: '100%',
    maxWidth: '100%',
    boxSizing: 'border-box',
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
    minHeight: 'calc(100vh - 64px)', // Subtract header height
    [mediaQueries.tablet]: {
      padding: '16px',
    },
    [mediaQueries.mobile]: {
      padding: '12px',
    },
  },
  contentContainer: {
    backgroundColor: theme.palette.background.paper,
    borderRadius: '8px',
    boxShadow: '0px 2px 8px rgba(0, 0, 0, 0.1)',
    padding: '24px',
    flex: '1',
    [mediaQueries.tablet]: {
      padding: '16px',
    },
    [mediaQueries.mobile]: {
      padding: '12px',
      borderRadius: '4px',
    },
  },
  pageHeader: {
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '16px',
    [mediaQueries.mobile]: {
      flexDirection: 'column',
      alignItems: 'flex-start',
      gap: '12px',
    },
  },
  headerContent: {
    display: 'flex',
    flexDirection: 'column',
  },
  headerTitle: {
    color: theme.palette.text.primary,
    marginBottom: '4px',
  },
  headerDescription: {
    color: theme.palette.text.secondary,
  },
  headerActions: {
    display: 'flex',
    gap: '8px',
    [mediaQueries.mobile]: {
      width: '100%',
      justifyContent: 'flex-end',
    },
  },
}));

export default useStyles;