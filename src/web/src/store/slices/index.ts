import { applicationSlice, actions as applicationActions } from './applicationSlice'; // Import application slice and its actions
import { authSlice, actions as authActions } from './authSlice'; // Import authentication slice and its actions
import { documentSlice, actions as documentActions } from './documentSlice'; // Import document slice and its actions
import { schoolSlice, actions as schoolActions } from './schoolSlice'; // Import school slice and its actions
import { userSlice, actions as userActions } from './userSlice'; // Import user slice and its actions
import { underwritingSlice, actions as underwritingActions } from './underwritingSlice'; // Import underwriting slice and its actions
import { notificationSlice, actions as notificationActions } from './notificationSlice'; // Import notification slice and its actions
import { fundingSlice, actions as fundingActions } from './fundingSlice'; // Import funding slice and its actions
import { qcSlice, actions as qcActions } from './qcSlice'; // Import quality control slice and its actions

/**
 * Exports all Redux Toolkit slices for the loan management system.
 * This file serves as a single entry point for importing slices throughout the application,
 * simplifying imports and maintaining a clean architecture.
 */
export {
  applicationSlice,
  authSlice,
  documentSlice,
  schoolSlice,
  userSlice,
  underwritingSlice,
  notificationSlice,
  fundingSlice,
  qcSlice,
  applicationActions,
  authActions,
  documentActions,
  schoolActions,
  userActions,
  underwritingActions,
  notificationActions,
  fundingActions,
  qcActions
};