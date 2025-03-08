/**
 * Centralizes and exports all Redux Toolkit async thunks from the various
 * domain-specific thunk files. This index file serves as a single entry point
 * for importing thunk actions throughout the application, simplifying imports
 * and providing a comprehensive view of all available async actions.
 */

import * as applicationThunks from './applicationThunks';
import * as authThunks from './authThunks';
import * as documentThunks from './documentThunks';
import * as fundingThunks from './fundingThunks';
import * as notificationThunks from './notificationThunks';
import * as qcThunks from './qcThunks';
import * as schoolThunks from './schoolThunks';
import * as underwritingThunks from './underwritingThunks';
import * as userThunks from './userThunks';

export {
  applicationThunks,
  authThunks,
  documentThunks,
  fundingThunks,
  notificationThunks,
  qcThunks,
  schoolThunks,
  underwritingThunks,
  userThunks,
};