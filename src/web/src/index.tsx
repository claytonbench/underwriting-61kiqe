import React, { StrictMode } from 'react'; // react v18.2.0
import { createRoot } from 'react-dom/client'; // react-dom/client v18.2.0
import reportWebVitals from 'web-vitals'; // web-vitals v2.1.4
import App from './App';
import './assets/css/global.css';

/**
 * This is the entry point for the React application.
 * It renders the root App component into the DOM, sets up global styles,
 * and configures performance monitoring.
 */
// 1. Import required modules and components
// React, ReactDOM, App component, global CSS

// 2. Import global CSS styles
// This import applies global styles defined in global.css to the entire application

// 3. Get root DOM element
// Find the DOM element with the ID 'root' where the React app will be rendered
const rootElement = document.getElementById('root');

// Check if rootElement exists before proceeding
if (!rootElement) {
  throw new Error('Failed to find the root element in the DOM.');
}

// 4. Create React root using createRoot
// Use React 18's createRoot API to create a root for rendering the App component
const root = createRoot(rootElement);

// 5. Render App component wrapped in StrictMode
// Render the App component inside React's StrictMode for additional development checks
root.render(
  <StrictMode>
    <App />
  </StrictMode>
);

/**
 * Configures performance monitoring using web-vitals library.
 * Measures and reports web vitals metrics for performance analysis.
 *
 * @param metric - A function that reports web vitals metrics.
 */
const sendToAnalytics = (metric: any) => {
  // In a real-world scenario, this function would send the metric
  // to a dedicated analytics service for tracking and analysis.
  // For example, you might use Google Analytics, New Relic, or a custom endpoint.
  console.log('Web Vitals Metric:', metric);
};

/**
 * Measures and reports web vitals metrics for performance analysis.
 * This function is called after the initial render to start measuring web vitals.
 *
 * The following metrics are collected:
 * - CLS (Cumulative Layout Shift): Measures visual stability.
 * - FID (First Input Delay): Measures responsiveness.
 * - FCP (First Contentful Paint): Measures perceived load speed.
 * - LCP (Largest Contentful Paint): Measures load speed.
 * - TTFB (Time to First Byte): Measures server response time.
 *
 * The metrics are reported to an analytics service using the sendToAnalytics function.
 */
reportWebVitals(sendToAnalytics);