import { makeStyles } from '@mui/styles'; // @mui/styles ^5.14.0
import { Theme, styled } from '@mui/material'; // @mui/material ^5.14.0
import { mediaQueries } from '../../../responsive/breakpoints';

/**
 * Styled component for the loading spinner container
 * Provides a flex container that centers its content both horizontally and vertically
 */
const SpinnerContainer = styled('div')(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: theme.spacing(2),
  
  // Responsive adjustments for mobile devices
  [mediaQueries.mobile]: {
    padding: theme.spacing(1),
  }
}));

/**
 * Props interface for the OverlayContainer component
 */
interface OverlayContainerProps {
  zIndex?: number;
}

/**
 * Styled component for the loading overlay container
 * Creates a semi-transparent overlay that blocks user interaction during loading
 */
const OverlayContainer = styled('div', {
  shouldForwardProp: (prop) => prop !== 'zIndex',
})<OverlayContainerProps>(({ theme, zIndex }) => ({
  position: 'absolute',
  top: 0,
  left: 0,
  width: '100%',
  height: '100%',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  backgroundColor: 'rgba(255, 255, 255, 0.7)', // Semi-transparent white backdrop for accessibility
  zIndex: zIndex || 1300, // Default to a high z-index unless specified
  
  // Ensure loading indicator is visible on mobile devices
  [mediaQueries.mobile]: {
    // Mobile-specific styling if needed
  }
}));

/**
 * Custom hook that returns styled components for loading indicators
 * These components provide consistent styling for loading states throughout the application
 */
const useStyles = () => {
  return {
    SpinnerContainer,
    OverlayContainer,
  };
};

export default useStyles;