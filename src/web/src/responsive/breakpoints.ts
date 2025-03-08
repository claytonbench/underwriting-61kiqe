/**
 * Responsive design breakpoints and media queries for the loan management system.
 * Defines consistent breakpoints for desktop, tablet, and mobile views as specified
 * in the technical requirements.
 */

// Material-UI standard breakpoints for reference
export const breakpoints = {
  xs: 0,
  sm: 600,
  md: 960,
  lg: 1280,
  xl: 1920,
};

// Device breakpoints as specified in technical requirements
// Mobile: below 768px, Tablet: 768px-1199px, Desktop: 1200px and above
export const deviceBreakpoints = {
  mobile: 768, // Upper boundary for mobile devices
  tablet: 768, // Lower boundary for tablet devices
  desktop: 1200, // Lower boundary for desktop devices
};

// CSS media queries for use in styled components or other CSS-in-JS solutions
export const mediaQueries = {
  mobile: `@media (max-width: ${deviceBreakpoints.tablet - 0.02}px)`,
  tablet: `@media (min-width: ${deviceBreakpoints.tablet}px) and (max-width: ${deviceBreakpoints.desktop - 0.02}px)`,
  desktop: `@media (min-width: ${deviceBreakpoints.desktop}px)`,
  mobileLandscape: `@media (max-width: ${deviceBreakpoints.tablet - 0.02}px) and (orientation: landscape)`,
};

/**
 * Determines if the current viewport width is in the mobile range
 * @param width - Optional width parameter, defaults to window.innerWidth
 * @returns True if the width is less than the mobile breakpoint
 */
export function isMobile(width?: number): boolean {
  const viewportWidth = width !== undefined ? width : 
    (typeof window !== 'undefined' ? window.innerWidth : 0);
  return viewportWidth < deviceBreakpoints.tablet;
}

/**
 * Determines if the current viewport width is in the tablet range
 * @param width - Optional width parameter, defaults to window.innerWidth
 * @returns True if the width is between tablet and desktop breakpoints
 */
export function isTablet(width?: number): boolean {
  const viewportWidth = width !== undefined ? width : 
    (typeof window !== 'undefined' ? window.innerWidth : 0);
  return viewportWidth >= deviceBreakpoints.tablet && viewportWidth < deviceBreakpoints.desktop;
}

/**
 * Determines if the current viewport width is in the desktop range
 * @param width - Optional width parameter, defaults to window.innerWidth
 * @returns True if the width is greater than or equal to the desktop breakpoint
 */
export function isDesktop(width?: number): boolean {
  const viewportWidth = width !== undefined ? width : 
    (typeof window !== 'undefined' ? window.innerWidth : 0);
  return viewportWidth >= deviceBreakpoints.desktop;
}