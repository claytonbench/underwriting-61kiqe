import React from 'react';
import { CircularProgress, Typography } from '@mui/material'; // ^5.14.0
import useStyles from './styles';

/**
 * Props interface for the LoadingSpinner component
 */
interface LoadingSpinnerProps {
  /** Size of the spinner in pixels */
  size?: number;
  /** Color of the spinner (primary, secondary, or CSS color) */
  color?: 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' | 'inherit' | string;
  /** Thickness of the spinner circle */
  thickness?: number;
  /** Optional text to display below the spinner */
  label?: string;
  /** Additional CSS class for styling */
  className?: string;
}

/**
 * A reusable loading spinner component that displays a circular progress indicator 
 * with optional text label.
 * 
 * Used throughout the application to indicate loading states during asynchronous operations.
 * Provides visual feedback to users during data loading or processing.
 * 
 * @param props - Component props containing configuration options
 * @returns A loading spinner component with optional label
 */
const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 40,
  color = 'primary',
  thickness = 3.6,
  label,
  className,
}) => {
  const { SpinnerContainer } = useStyles();

  return (
    <SpinnerContainer className={className} data-testid="loading-spinner">
      <CircularProgress 
        size={size} 
        color={color as 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' | 'inherit'} 
        thickness={thickness}
        aria-label={label || "Loading"}
      />
      {label && (
        <Typography 
          variant="body2" 
          color="text.secondary" 
          align="center" 
          sx={{ mt: 1 }}
          aria-live="polite"
        >
          {label}
        </Typography>
      )}
    </SpinnerContainer>
  );
};

export default LoadingSpinner;