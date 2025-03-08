// This file configures the testing environment for Jest in our React application
import '@testing-library/jest-dom'; // v5.16.5
import { configureAxe, toHaveNoViolations } from 'jest-axe'; // v7.0.0
import { setupServer } from 'msw/node'; // v1.2.2
import { DefaultBodyType, MockedRequest, RestHandler } from 'msw';

// Extend Jest matchers with accessibility testing
expect.extend(toHaveNoViolations);

// Set up the axe configuration for accessibility testing
configureAxe({
  rules: {
    // Add specific rule configurations as needed
    'color-contrast': { enabled: true },
    'aria-required-attr': { enabled: true },
    'aria-roles': { enabled: true }
  }
});

// Mock window.matchMedia
window.matchMedia = jest.fn().mockImplementation(query => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: jest.fn(), // deprecated but still needed for some tests
  removeListener: jest.fn(), // deprecated but still needed for some tests
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  dispatchEvent: jest.fn(),
}));

// Mock window.scrollTo
window.scrollTo = jest.fn();

// Mock ResizeObserver
class ResizeObserverMock {
  observe = jest.fn();
  unobserve = jest.fn();
  disconnect = jest.fn();
}

// Register the ResizeObserver mock
Object.defineProperty(window, 'ResizeObserver', {
  writable: true,
  configurable: true,
  value: ResizeObserverMock
});

// Mock IntersectionObserver
class IntersectionObserverMock {
  constructor(callback: IntersectionObserverCallback) {
    this.callback = callback;
  }
  callback: IntersectionObserverCallback;
  root = null;
  rootMargin = '';
  thresholds = [];
  observe = jest.fn();
  unobserve = jest.fn();
  disconnect = jest.fn();
  takeRecords = jest.fn().mockReturnValue([]);
}

// Register the IntersectionObserver mock
Object.defineProperty(window, 'IntersectionObserver', {
  writable: true,
  configurable: true,
  value: IntersectionObserverMock
});

// Extend Jest timeout for longer running tests
jest.setTimeout(10000);

/**
 * Sets up the Mock Service Worker server for API mocking in tests
 * This helps simulate API calls without making actual network requests
 */
export const setupMswServer = () => {
  // Create MSW server instance
  const server = setupServer();

  // Setup lifecycle hooks
  beforeAll(() => {
    // Start the server before all tests
    server.listen({
      onUnhandledRequest: 'warn', // Warn if there's an unhandled request
    });
  });

  afterEach(() => {
    // Reset handlers after each test
    server.resetHandlers();
  });

  afterAll(() => {
    // Close server after all tests are done
    server.close();
  });

  // Return server instance so it can be used to add handlers in tests
  return server;
};

/**
 * Utility function to wait for a specific condition to be true
 * Useful for async operations in tests
 */
export const waitFor = (conditionFn: () => boolean, timeout = 1000, interval = 50): Promise<void> => {
  const startTime = Date.now();
  return new Promise((resolve, reject) => {
    const check = () => {
      if (conditionFn()) {
        resolve();
        return;
      }
      if (Date.now() - startTime > timeout) {
        reject(new Error(`Timed out waiting for condition after ${timeout}ms`));
        return;
      }
      setTimeout(check, interval);
    };
    check();
  });
};

// Add any additional testing utilities or configurations below