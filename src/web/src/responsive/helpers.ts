/**
 * Responsive Design Helpers
 * 
 * This file provides responsive design utility functions and React hooks for the loan management system
 * frontend application. It implements helper functions to detect device types, handle responsive values,
 * and React hooks for responsive design that can be used across components.
 *
 * Implements the responsive design approach with breakpoints for desktop (1200px and above),
 * tablet (768px to 1199px), and mobile (below 768px) as specified in the technical requirements.
 */

import * as React from 'react'; // React v18.2.0
import { useMediaQuery } from '@mui/material'; // Material-UI v5.14.0
import { deviceBreakpoints, mediaQueries, isMobile, isTablet, isDesktop } from './breakpoints';

/**
 * Interface for the responsive state object returned by useResponsive hook
 */
export interface ResponsiveState {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  deviceType: 'mobile' | 'tablet' | 'desktop';
}

/**
 * Generic interface for responsive values object used with getResponsiveValue
 */
export interface ResponsiveValues<T> {
  mobile?: T;
  tablet?: T;
  desktop?: T;
  default?: T;
}

/**
 * Determines the current device type based on viewport width
 * @param width - Optional width parameter, defaults to window.innerWidth
 * @returns 'mobile', 'tablet', or 'desktop' based on the current viewport width
 */
export function getDeviceType(width?: number): 'mobile' | 'tablet' | 'desktop' {
  const viewportWidth = width !== undefined ? width : 
    (typeof window !== 'undefined' ? window.innerWidth : 0);
    
  if (viewportWidth < deviceBreakpoints.tablet) {
    return 'mobile';
  } else if (viewportWidth < deviceBreakpoints.desktop) {
    return 'tablet';
  } else {
    return 'desktop';
  }
}

/**
 * Returns a value based on the current device type
 * @param values - Object containing values for different device types
 * @param width - Optional width parameter to determine the device type
 * @returns The appropriate value for the current device type
 */
export function getResponsiveValue<T>(values: ResponsiveValues<T>, width?: number): T | undefined {
  const deviceType = getDeviceType(width);
  
  // Return the value for the current device type if it exists
  if (deviceType === 'mobile' && values.mobile !== undefined) {
    return values.mobile;
  } else if (deviceType === 'tablet' && values.tablet !== undefined) {
    return values.tablet;
  } else if (deviceType === 'desktop' && values.desktop !== undefined) {
    return values.desktop;
  }
  
  // Fallback to default value or undefined
  return values.default;
}

/**
 * React hook that provides responsive design state for components
 * @returns An object with isMobile, isTablet, isDesktop, and deviceType properties
 */
export function useResponsive(): ResponsiveState {
  const [state, setState] = React.useState<ResponsiveState>(() => ({
    isMobile: isMobile(),
    isTablet: isTablet(),
    isDesktop: isDesktop(),
    deviceType: getDeviceType(),
  }));

  React.useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const handleResize = () => {
      setState({
        isMobile: isMobile(),
        isTablet: isTablet(),
        isDesktop: isDesktop(),
        deviceType: getDeviceType(),
      });
    };

    // Add event listener
    window.addEventListener('resize', handleResize);
    
    // Remove event listener on cleanup
    return () => window.removeEventListener('resize', handleResize);
  }, []); // Empty dependency array ensures this only runs once on mount

  return state;
}

/**
 * React hook to detect if the device is in landscape orientation
 * @returns True if the device is in landscape orientation
 */
export function useIsLandscape(): boolean {
  const [isLandscape, setIsLandscape] = React.useState<boolean>(() => {
    if (typeof window === 'undefined') return false;
    return window.innerWidth > window.innerHeight;
  });

  React.useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const handleResize = () => {
      setIsLandscape(window.innerWidth > window.innerHeight);
    };

    const handleOrientationChange = () => {
      handleResize();
    };

    // Initial check
    handleResize();

    // Add event listeners
    window.addEventListener('resize', handleResize);
    window.addEventListener('orientationchange', handleOrientationChange);
    
    // Remove event listeners on cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('orientationchange', handleOrientationChange);
    };
  }, []); // Empty dependency array ensures this only runs once on mount

  return isLandscape;
}

/**
 * React hook to detect if the current viewport is mobile size using Material-UI's useMediaQuery
 * @returns True if the current viewport is mobile size
 */
export function useIsMobile(): boolean {
  return useMediaQuery(mediaQueries.mobile);
}

/**
 * React hook to detect if the current viewport is tablet size using Material-UI's useMediaQuery
 * @returns True if the current viewport is tablet size
 */
export function useIsTablet(): boolean {
  return useMediaQuery(mediaQueries.tablet);
}

/**
 * React hook to detect if the current viewport is desktop size using Material-UI's useMediaQuery
 * @returns True if the current viewport is desktop size
 */
export function useIsDesktop(): boolean {
  return useMediaQuery(mediaQueries.desktop);
}