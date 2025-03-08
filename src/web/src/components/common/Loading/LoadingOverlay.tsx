import React from 'react';
import { Portal } from '@mui/material'; // @mui/material ^5.14.0
import useStyles from './styles';
import LoadingSpinner from './LoadingSpinner';

/**
 * Props interface for the LoadingOverlay component
 */
interface LoadingOverlayProps {
  /**
   * Whether the loading overlay should be displayed
   */
  isLoading: boolean;
  /**
   * Optional text to display below the spinner to inform users about the current operation
   */
  message?: string;
  /**
   * Optional container element to scope the overlay to instead of full screen
   * Useful for loading states within specific components rather than the entire page
   */
  container?: HTMLElement | null;
  /**
   * Z-index for the overlay to control its stacking context
   * Default: 1300 (same as Material-UI modal)
   */
  zIndex?: number;
  /**
   * Color of the spinner (primary, secondary, or CSS color)
   * Default: 'primary'
   */
  color?: string;
  /**
   * Size of the spinner in pixels
   * Default: 40
   */
  size?: number;
  /**
   * Additional CSS class for styling the overlay container
   */
  className?: string;
}

/**
 * A reusable loading overlay component that displays a semi-transparent overlay with a loading spinner,
 * used to block user interaction during asynchronous operations.
 * 
 * This component renders a Portal to ensure the overlay appears above all other content regardless
 * of DOM structure. The overlay is only rendered when `isLoading` is true.
 * 
 * @example
 * ```tsx
 * <LoadingOverlay 
 *   isLoading={isSubmitting} 
 *   message="Submitting application..." 
 * />
 * ```
 */
const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  isLoading,
  message,
  container,
  zIndex = 1300,
  color = 'primary',
  size = 40,
  className,
}) => {
  const { OverlayContainer } = useStyles();

  // Don't render anything if not loading
  if (!isLoading) {
    return null;
  }

  // Use the provided container or default to document.body
  const portalContainer = container || document.body;

  return (
    <Portal container={portalContainer}>
      <OverlayContainer 
        zIndex={zIndex} 
        className={className}
        aria-live="polite"
        aria-busy={true}
        role="status"
        data-testid="loading-overlay"
      >
        <LoadingSpinner 
          color={color} 
          size={size} 
          label={message}
        />
      </OverlayContainer>
    </Portal>
  );
};

export default LoadingOverlay;