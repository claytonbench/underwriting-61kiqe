import { makeStyles } from '@mui/styles'; // v5.14.0
import { Theme } from '@mui/material'; // v5.14.0
import { palette } from '../../../config/theme';

/**
 * Custom hook that generates CSS classes for the StatusBadge component based on the theme
 */
const useStyles = makeStyles((theme: Theme) => ({
  // Base style for all badges
  root: {
    display: 'inline-flex',
    borderRadius: '16px',
    padding: '4px 12px',
    fontSize: '0.75rem',
    fontWeight: 500,
    textTransform: 'capitalize',
    whiteSpace: 'nowrap',
  },
  // Success variant (green)
  success: {
    backgroundColor: 'rgba(56, 142, 60, 0.1)',
    color: '#388E3C',
    border: '1px solid rgba(56, 142, 60, 0.2)',
  },
  // Error variant (red)
  error: {
    backgroundColor: 'rgba(211, 47, 47, 0.1)',
    color: '#D32F2F',
    border: '1px solid rgba(211, 47, 47, 0.2)',
  },
  // Warning variant (amber)
  warning: {
    backgroundColor: 'rgba(255, 160, 0, 0.1)',
    color: '#FFA000',
    border: '1px solid rgba(255, 160, 0, 0.2)',
  },
  // Info variant (light blue)
  info: {
    backgroundColor: 'rgba(2, 136, 209, 0.1)',
    color: '#0288D1',
    border: '1px solid rgba(2, 136, 209, 0.2)',
  },
  // Default variant (gray)
  default: {
    backgroundColor: 'rgba(117, 117, 117, 0.1)',
    color: '#757575',
    border: '1px solid rgba(117, 117, 117, 0.2)',
  },
}));

export default useStyles;