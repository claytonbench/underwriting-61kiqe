import { configureStore, EnhancedStore } from '@reduxjs/toolkit'; // @reduxjs/toolkit ^1.9.5
import { ThunkAction } from 'redux-thunk'; // redux-thunk ^2.4.2
import { Action } from 'redux'; // redux ^4.2.1
import rootReducer, { RootState } from './rootReducer';

/**
 * Configures the Redux store with middleware and enhancers.
 * This setup uses Redux Toolkit's `configureStore` for simplified store configuration.
 *
 * The store includes:
 * - The combined `rootReducer` to manage the entire application state.
 * - Redux Thunk middleware for handling asynchronous actions.
 * - DevTools integration for debugging (enabled by default in development).
 *
 * @returns An enhanced Redux store with the specified configuration.
 */
const store: EnhancedStore = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      thunk: true, // Enable Redux Thunk middleware
      serializableCheck: { // Validates that state and actions are serializable
        ignoredActions: ['auth/setCredentials', 'document/setSignatureData'],
        ignoredPaths: ['auth.credentials', 'document.signatureData']
      }
    }),
  devTools: {
    name: 'Loan Management System', // Customize the name in Redux DevTools
    trace: true, // Enable tracing of actions through the reducers
    traceLimit: 25 // Limit the number of trace entries to avoid performance issues
  }
});

/**
 * Type definition for the dispatch function of the Redux store.
 * This type is derived directly from the store instance to ensure type safety.
 */
export type AppDispatch = typeof store.dispatch;

/**
 * Type definition for thunk actions that can be dispatched in the application.
 * Includes the return type, root state, extra argument (if any), and action type.
 */
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>;

/**
 * Export the configured Redux store for use in the application.
 */
export default store;