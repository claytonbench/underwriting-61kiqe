/**
 * Responsive Design System
 * 
 * This barrel file exports all responsive design utilities from the responsive module,
 * providing a centralized entry point for breakpoints, media queries, and responsive 
 * helper functions used throughout the loan management system frontend application.
 * 
 * The responsive system implements the technical specifications for:
 * - Desktop: 1200px and above
 * - Tablet: 768px to 1199px
 * - Mobile: Below 768px
 * 
 * And provides utilities to create appropriate layouts and adaptations for each
 * device type.
 */

// Re-export all breakpoint definitions and device detection functions
export {
  breakpoints,
  deviceBreakpoints,
  mediaQueries,
  isMobile,
  isTablet,
  isDesktop,
} from './breakpoints';

// Re-export all responsive helper functions and hooks
export {
  getDeviceType,
  getResponsiveValue,
  useResponsive,
  useIsLandscape,
  useIsMobile,
  useIsTablet,
  useIsDesktop,
  // Type interfaces
  type ResponsiveState,
  type ResponsiveValues,
} from './helpers';