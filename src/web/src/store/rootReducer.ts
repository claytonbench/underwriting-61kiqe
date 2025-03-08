import { combineReducers, Reducer } from 'redux'; // redux v4.2.1
import {
  applicationReducer,
  authReducer,
  documentReducer,
  schoolReducer,
  userReducer,
  underwritingReducer,
  notificationReducer,
  fundingReducer,
  qcReducer
} from './reducers';
import { ApplicationState } from '../types/application.types';
import { AuthState } from '../types/auth.types';
import { DocumentState } from '../types/document.types';
import { SchoolState } from '../types/school.types';
import { UserState } from '../types/user.types';
import { UnderwritingState } from '../types/underwriting.types';
import { NotificationState } from '../types/notification.types';
import { FundingState } from '../types/funding.types';
import { QCState } from '../types/qc.types';

/**
 * Defines the structure of the root state for the Redux store.
 * It includes slices for authentication, application, document, school, user,
 * underwriting, notification, funding, and quality control states.
 */
export interface RootState {
  auth: AuthState;
  application: ApplicationState;
  document: DocumentState;
  school: SchoolState;
  user: UserState;
  underwriting: UnderwritingState;
  notification: NotificationState;
  funding: FundingState;
  qc: QCState;
}

/**
 * Combines all individual reducers into a single root reducer.
 * This root reducer manages the entire state tree of the application.
 * Each reducer is responsible for managing a specific slice of the state.
 *
 * @param auth - Reducer for authentication state.
 * @param application - Reducer for loan application state.
 * @param document - Reducer for document management state.
 * @param school - Reducer for school and program management state.
 * @param user - Reducer for user management state.
 * @param underwriting - Reducer for underwriting process state.
 * @param notification - Reducer for notification state.
 * @param funding - Reducer for funding process state.
 * @param qc - Reducer for quality control process state.
 *
 * @returns A combined reducer that handles all actions and updates the root state.
 */
const rootReducer: Reducer<RootState> = combineReducers<RootState>({
  auth: authReducer,
  application: applicationReducer,
  document: documentReducer,
  school: schoolReducer,
  user: userReducer,
  underwriting: underwritingReducer,
  notification: notificationReducer,
  funding: fundingReducer,
  qc: qcReducer,
});

export default rootReducer;